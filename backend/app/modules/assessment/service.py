"""IR plan assessment: ask the LLM for findings, then verify and score them in code."""

from __future__ import annotations

from app.catalogs.checklists import Checklist
from app.catalogs.csf import CsfCatalog
from app.llm.base import StructuredLLM
from app.modules.assessment.evidence import (
    DOWNGRADE,
    SCORE_FORMULA,
    compute_score,
    normalize,
    quote_in_document,
)
from app.modules.assessment.ingest import ExtractedDocument
from app.modules.assessment.prompts import SYSTEM_PROMPT, build_prompt
from app.modules.assessment.schemas import (
    AssessmentDraft,
    AssessmentReport,
    AssessmentValidation,
    ControlResult,
    CsfReference,
    DocumentInfo,
    Evidence,
    ScoreBreakdown,
)

PRIORITY_ORDER = {"critical": 0, "high": 1, "medium": 2}
TOP_GAPS = 5


class AssessmentService:
    def __init__(
        self,
        llm: StructuredLLM,
        checklist: Checklist,
        csf: CsfCatalog,
        notice: str | None = None,
        fixed_document: ExtractedDocument | None = None,
    ):
        self._llm = llm
        self._checklist = checklist
        self._csf = csf
        self._notice = notice  # e.g. the demo-mode disclaimer, shown first in warnings
        # Demo mode replays the assessment of one example plan. Its quotes must be verified
        # against that plan, not against whatever the user uploaded.
        self._fixed_document = fixed_document

    def assess(self, document: ExtractedDocument) -> AssessmentReport:
        document = self._fixed_document or document
        prompt = build_prompt(document.text, self._checklist, self._csf)
        draft = self._llm.generate(system=SYSTEM_PROMPT, prompt=prompt, schema=AssessmentDraft)
        return self.build_report(document, draft)

    def build_report(self, document: ExtractedDocument, draft: AssessmentDraft) -> AssessmentReport:
        """Turn untrusted findings into the public report. Pure function: no LLM calls."""
        known = {c.id for c in self._checklist.controls}
        findings = {}
        unknown: list[str] = []
        for f in draft.findings:
            cid = f.control_id.strip().upper()
            if cid not in known:
                unknown.append(f.control_id)
            elif cid not in findings:  # keep the first finding if the model repeats a control
                findings[cid] = f

        normalized_doc = normalize(document.text)
        results: list[ControlResult] = []
        unverified: list[str] = []
        not_assessed: list[str] = []
        for control in self._checklist.controls:
            csf_refs = [CsfReference(id=s, text=self._csf.subcategory_text(s) or "") for s in control.csf_subcategories]
            base = dict(control_id=control.id, title=control.title, topic=control.topic, phase=control.phase,
                        priority=control.priority, csf=csf_refs, sp800_61r3=control.sp800_61r3)
            f = findings.get(control.id)
            if f is None:
                not_assessed.append(control.id)
                results.append(ControlResult(
                    **base, status="missing", model_status="missing", evidence=None,
                    rationale="Not assessed by the model; scored as missing.",
                    recommendation="Review this control manually.",
                ))
                continue

            status = f.status
            evidence = None
            if f.status != "missing":
                quote = f.evidence_quote or ""
                verified = bool(quote) and quote_in_document(quote, normalized_doc)
                evidence = Evidence(quote=quote, verified=verified) if quote else None
                if not verified:
                    status = DOWNGRADE[f.status]
                    unverified.append(control.id)
            results.append(ControlResult(
                **base, status=status, model_status=f.status, evidence=evidence,
                rationale=f.rationale, recommendation=f.recommendation,
            ))

        weights = {c.id: self._checklist.weight(c) for c in self._checklist.controls}
        score, coverage = compute_score([(r.status, weights[r.control_id]) for r in results])
        gaps = sorted((r for r in results if r.status != "met"),
                      key=lambda r: (PRIORITY_ORDER[r.priority], r.status != "missing"))

        warnings: list[str] = [self._notice] if self._notice else []
        if document.truncated:
            warnings.append(f"The document was truncated to {len(document.text):,} characters; "
                            "content after that point was not assessed.")
        if unverified:
            warnings.append(f"{len(unverified)} control(s) were downgraded because their quote "
                            "was not found in the document.")

        return AssessmentReport(
            checklist=f"{self._checklist.title} v{self._checklist.version}",
            document=DocumentInfo(kind=document.kind, pages=document.pages,
                                  characters=len(document.text), truncated=document.truncated),
            summary=draft.summary,
            score=ScoreBreakdown(
                score=score, coverage=coverage,
                met=sum(r.status == "met" for r in results),
                partial=sum(r.status == "partial" for r in results),
                missing=sum(r.status == "missing" for r in results),
                formula=SCORE_FORMULA,
            ),
            results=results,
            top_gaps=[r.control_id for r in gaps[:TOP_GAPS]],
            validation=AssessmentValidation(
                unverified_quotes=unverified, unknown_controls=unknown,
                not_assessed=not_assessed, warnings=warnings,
            ),
        )
