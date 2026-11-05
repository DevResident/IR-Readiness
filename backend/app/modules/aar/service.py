"""AAR generation: draft with the LLM, then verify quotes, CSF categories and links in code."""

from __future__ import annotations

from app.llm.base import StructuredLLM
from app.modules.aar.prompts import SYSTEM_PROMPT, build_prompt
from app.modules.aar.schemas import (
    AARDraft,
    AARRequest,
    AARValidation,
    AfterActionReport,
    Observation,
    Recommendation,
)
from app.modules.assessment.evidence import normalize, quote_in_document

PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}
TIMEFRAME_ORDER = {"30 days": 0, "90 days": 1, "180 days": 2}


class AARService:
    def __init__(
        self,
        llm: StructuredLLM,
        csf_categories: dict[str, str],
        *,
        notice: str | None = None,
        fixed_request: AARRequest | None = None,
    ):
        self._llm = llm
        self._csf = csf_categories
        self._notice = notice  # e.g. the demo-mode disclaimer, shown first in warnings
        # Demo mode: always use the example notes, so quotes are verified against the notes they came from
        self._fixed_request = fixed_request

    def generate(self, request: AARRequest) -> AfterActionReport:
        request = self._fixed_request or request
        prompt = build_prompt(request, self._csf)
        draft = self._llm.generate(system=SYSTEM_PROMPT, prompt=prompt, schema=AARDraft)
        report = self.build_report(request, draft)
        if self._notice:
            report.validation.warnings.insert(0, self._notice)
        return report

    def _category(self, raw: str | None, where: str, rejected: list[str]) -> tuple[str | None, str | None]:
        if not raw:
            return None, None
        cid = raw.strip().upper()
        if cid in self._csf:
            return cid, self._csf[cid]
        rejected.append(f"{where}: {raw}")
        return None, None

    def build_report(self, request: AARRequest, draft: AARDraft) -> AfterActionReport:
        """Pure function: no LLM calls."""
        notes = normalize(request.notes)
        rejected: list[str] = []
        unverified: list[str] = []
        warnings: list[str] = []

        observations: list[Observation] = []
        seen: set[str] = set()
        for i, o in enumerate(draft.observations, start=1):
            oid = o.id.strip().upper() or f"O{i}"
            if oid in seen:
                oid = f"O{i}"
            seen.add(oid)
            cid, ctitle = self._category(o.csf_category, f"observation {oid}", rejected)
            verified = bool(o.evidence_quote) and quote_in_document(o.evidence_quote, notes)
            if not verified:
                unverified.append(oid)
            observations.append(Observation(
                id=oid, kind=o.kind, title=o.title, detail=o.detail, phase=o.phase,
                csf_category=cid, csf_title=ctitle,
                evidence_quote=o.evidence_quote or None, evidence_verified=verified,
            ))
        ids = {o.id for o in observations}

        dropped: list[str] = []
        recs: list[Recommendation] = []
        for r in draft.recommendations:
            links = []
            for ref in r.addresses:
                ref_id = ref.strip().upper()
                if ref_id in ids and ref_id not in links:
                    links.append(ref_id)
                elif ref_id not in ids:
                    dropped.append(f"{r.title}: {ref}")
            cid, ctitle = self._category(r.csf_category, f"recommendation '{r.title}'", rejected)
            recs.append(Recommendation(
                rank=0, title=r.title, action=r.action, priority=r.priority, timeframe=r.timeframe,
                suggested_owner=r.suggested_owner, addresses=links, csf_category=cid, csf_title=ctitle,
            ))
        recs.sort(key=lambda r: (PRIORITY_ORDER[r.priority], TIMEFRAME_ORDER[r.timeframe]))
        for rank, r in enumerate(recs, start=1):
            r.rank = rank

        if unverified:
            warnings.append(f"{len(unverified)} observation(s) cite text that was not found in the notes; "
                            "review them before sharing the report.")
        orphan = [r.title for r in recs if not r.addresses]
        if orphan:
            warnings.append(f"{len(orphan)} recommendation(s) are not linked to any observation.")
        if not any(o.kind == "improvement" for o in observations):
            warnings.append("No areas for improvement were identified.")

        return AfterActionReport(
            title=draft.title,
            event_type=request.event_type,
            event_date=request.event_date,
            executive_summary=draft.executive_summary,
            scope=draft.scope,
            strengths=[o for o in observations if o.kind == "strength"],
            areas_for_improvement=[o for o in observations if o.kind == "improvement"],
            gaps=draft.gaps,
            recommendations=recs,
            validation=AARValidation(unverified_observations=unverified, rejected_csf_categories=rejected,
                                     dropped_links=dropped, warnings=warnings),
        )
