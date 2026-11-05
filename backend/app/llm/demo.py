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
from app.modules.tabletop.schemas import TabletopDraft, TabletopExercise

T = TypeVar("T", bound=BaseModel)

DEMO_TABLETOP_FILE = EXAMPLES_DIR / "tabletop-ransomware-healthcare-executive.json"


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


class DemoStructuredLLM:
    """Returns a fixed response per schema. Unknown schemas fail like an unconfigured model."""

    def __init__(self, responses: dict[type[BaseModel], BaseModel]):
        self._responses = responses

    @classmethod
    def default(cls) -> DemoStructuredLLM:
        return cls({TabletopDraft: exercise_to_draft(load_demo_tabletop())})

    def generate(self, *, system: str, prompt: str, schema: type[T]) -> T:
        response = self._responses.get(schema)
        if response is None:
            raise LLMNotConfiguredError(f"Demo mode has no example for {schema.__name__}")
        return response.model_copy(deep=True)
