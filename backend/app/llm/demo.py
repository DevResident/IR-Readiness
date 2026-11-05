"""Demo mode: a StructuredLLM that replays a pre-generated example instead of calling a model.

It lets anyone run the app (and the frontend) without an API key. The replayed draft
still goes through the real validation in ``TabletopService.validate_draft``, so demo
mode exercises the same ATT&CK and CSF checks as a live run.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import TypeVar

from pydantic import BaseModel

from app.catalogs.paths import EXAMPLES_DIR
from app.llm.base import LLMNotConfiguredError
from app.modules.aar.schemas import AARDraft, AARRequest, AfterActionReport
from app.modules.assessment.ingest import ExtractedDocument, extract_document
from app.modules.assessment.schemas import AssessmentDraft, AssessmentReport
from app.modules.tabletop.schemas import TabletopDraft, TabletopExercise

T = TypeVar("T", bound=BaseModel)

DEMO_TABLETOP_FILE = EXAMPLES_DIR / "tabletop-ransomware-healthcare-executive.json"
DEMO_PLAN_FILE = EXAMPLES_DIR / "ir-plan-fictional-meridian-logistics.md"
DEMO_ASSESSMENT_FILE = EXAMPLES_DIR / "ir-plan-fictional-meridian-logistics.assessment.json"
DEMO_AAR_NOTES_FILE = EXAMPLES_DIR / "aar-notes-ransomware-tabletop.md"
DEMO_AAR_FILE = EXAMPLES_DIR / "aar-ransomware-tabletop.json"


def exercise_to_draft(exercise: TabletopExercise) -> TabletopDraft:
    """Rebuild the untrusted draft shape from a saved public exercise.

    Only technique IDs are kept (names and URLs are re-derived from the catalog on
    validation), and the flat question list is grouped back by phase.
    """
    by_phase: dict[str, list[dict]] = {"detect": [], "respond": [], "recover": [], "improve": []}
    for q in exercise.discussion_questions:
        if q.phase in by_phase:
            by_phase[q.phase].append({"question": q.question, "csf_category": q.csf_category})
    return TabletopDraft.model_validate({
        "title": exercise.title,
        "narrative": exercise.narrative,
        "objectives": exercise.objectives,
        "roles": [r.model_dump() for r in exercise.roles],
        "injects": [
            {
                "sequence": i.sequence,
                "time_offset": i.time_offset,
                "title": i.title,
                "description": i.description,
                "phase": i.phase,
                "technique_ids": [t.id for t in i.techniques],
                "expected_actions": i.expected_actions,
            }
            for i in exercise.injects
        ],
        "discussion_questions": by_phase,
        "facilitator_guide": exercise.facilitator_guide.model_dump(),
    })


def load_demo_tabletop(path: Path = DEMO_TABLETOP_FILE) -> TabletopExercise:
    return TabletopExercise.model_validate(json.loads(path.read_text(encoding="utf-8")))


def load_demo_assessment(path: Path = DEMO_ASSESSMENT_FILE) -> AssessmentReport:
    return AssessmentReport.model_validate(json.loads(path.read_text(encoding="utf-8")))


def load_demo_plan(path: Path = DEMO_PLAN_FILE) -> ExtractedDocument:
    return extract_document(path.name, path.read_bytes())


def report_to_draft(report: AssessmentReport) -> AssessmentDraft:
    """Rebuild the model's draft from a saved report: the model's own status, not the verified one."""
    return AssessmentDraft.model_validate({
        "findings": [
            {
                "control_id": r.control_id,
                "status": r.model_status,
                "evidence_quote": r.evidence.quote if r.evidence else None,
                "rationale": r.rationale,
                "recommendation": r.recommendation,
            }
            for r in report.results
        ],
        "summary": report.summary,
    })


def load_demo_aar(path: Path = DEMO_AAR_FILE) -> AfterActionReport:
    return AfterActionReport.model_validate(json.loads(path.read_text(encoding="utf-8")))


def load_demo_aar_request(path: Path = DEMO_AAR_NOTES_FILE) -> AARRequest:
    report = load_demo_aar()
    return AARRequest(notes=path.read_text(encoding="utf-8"), event_type=report.event_type,
                      event_date=report.event_date)


def aar_to_draft(report: AfterActionReport) -> AARDraft:
    """Rebuild the model's draft from a saved report, in the model's own observation order."""
    observations = sorted(report.strengths + report.areas_for_improvement, key=lambda o: int(o.id[1:]))
    return AARDraft.model_validate({
        "title": report.title,
        "executive_summary": report.executive_summary,
        "scope": report.scope,
        "observations": [
            {"id": o.id, "kind": o.kind, "title": o.title, "detail": o.detail, "phase": o.phase,
             "csf_category": o.csf_category, "evidence_quote": o.evidence_quote}
            for o in observations
        ],
        "gaps": report.gaps,
        "recommendations": [
            {"title": r.title, "action": r.action, "priority": r.priority, "timeframe": r.timeframe,
             "suggested_owner": r.suggested_owner, "addresses": r.addresses, "csf_category": r.csf_category}
            for r in report.recommendations
        ],
    })


class DemoStructuredLLM:
    """Returns a fixed response per schema. Unknown schemas fail like an unconfigured model."""

    def __init__(self, responses: dict[type[BaseModel], BaseModel]):
        self._responses = responses

    @classmethod
    def default(cls) -> DemoStructuredLLM:
        return cls({
            TabletopDraft: exercise_to_draft(load_demo_tabletop()),
            AssessmentDraft: report_to_draft(load_demo_assessment()),
            AARDraft: aar_to_draft(load_demo_aar()),
        })

    def generate(self, *, system: str, prompt: str, schema: type[T]) -> T:
        response = self._responses.get(schema)
        if response is None:
            raise LLMNotConfiguredError(f"Demo mode has no example for {schema.__name__}")
        return response.model_copy(deep=True)
