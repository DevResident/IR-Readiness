"""Tabletop generation: ask the LLM for a draft, then verify everything it claims."""

from __future__ import annotations

from app.catalogs.attack import AttackCatalog, Status
from app.catalogs.ir_lifecycle import IRLifecycle
from app.catalogs.scenarios import ScenarioTemplate
from app.llm.base import StructuredLLM
from app.modules.tabletop.prompts import SYSTEM_PROMPT, build_prompt
from app.modules.tabletop.schemas import (
    AttackTechniqueRef,
    DiscussionQuestion,
    Inject,
    RejectedReference,
    TabletopDraft,
    TabletopExercise,
    TabletopRequest,
    ValidationReport,
)

REQUIRED_QUESTION_PHASES = ("detect", "respond", "recover", "improve")


class TabletopService:
    def __init__(
        self,
        llm: StructuredLLM,
        catalog: AttackCatalog,
        lifecycle: IRLifecycle,
        scenarios: dict[str, ScenarioTemplate],
    ):
        self._llm = llm
        self._catalog = catalog
        self._lifecycle = lifecycle
        self._scenarios = scenarios

    def generate(self, request: TabletopRequest) -> TabletopExercise:
        scenario = self._scenarios[request.scenario]
        prompt = build_prompt(request, scenario, self._catalog, self._lifecycle)
        draft = self._llm.generate(system=SYSTEM_PROMPT, prompt=prompt, schema=TabletopDraft)
        return self.validate_draft(request, draft)

    def validate_draft(self, request: TabletopRequest, draft: TabletopDraft) -> TabletopExercise:
        """Turn an untrusted draft into the public exercise. Pure function: no LLM calls."""
        rejected: list[RejectedReference] = []
        remapped: list[str] = []
        warnings: list[str] = []
        accepted = 0

        injects: list[Inject] = []
        for position, d in enumerate(sorted(draft.injects, key=lambda i: i.sequence), start=1):
            location = f"inject {position}"
            kept, dropped = self._catalog.filter_valid(d.technique_ids)
            for tid in d.technique_ids:
                result = self._catalog.validate(tid)
                if result.status is Status.REMAPPED:
                    remapped.append(f"{location}: {result.note}")
            rejected += [RejectedReference(location=location, value=r.input_id, reason=r.note or r.status.value)
                         for r in dropped]
            accepted += len(kept)
            injects.append(Inject(
                sequence=position,  # renumbered so the timeline is always 1..n
                time_offset=d.time_offset,
                title=d.title,
                description=d.description,
                phase=d.phase,
                techniques=[AttackTechniqueRef(id=t.id, name=t.name, tactics=list(t.tactics), url=t.url) for t in kept],
                expected_actions=d.expected_actions,
            ))

        questions: list[DiscussionQuestion] = []
        for i, q in enumerate(draft.discussion_questions, start=1):
            category = q.csf_category.strip().upper() if q.csf_category else None
            if category and not self._lifecycle.is_known_csf_category(category):
                rejected.append(RejectedReference(
                    location=f"question {i}", value=q.csf_category, reason="Not a recognized CSF 2.0 category"
                ))
                category = None
            questions.append(q.model_copy(update={"csf_category": category}))

        covered = {q.phase for q in questions}
        missing = [p for p in REQUIRED_QUESTION_PHASES if p not in covered]
        if missing:
            warnings.append(f"No discussion questions for phase(s): {', '.join(missing)}")
        if accepted == 0:
            warnings.append("No inject has a validated ATT&CK technique")

        return TabletopExercise(
            request=request,
            title=draft.title,
            narrative=draft.narrative,
            objectives=draft.objectives,
            roles=draft.roles,
            injects=injects,
            discussion_questions=questions,
            facilitator_guide=draft.facilitator_guide,
            validation=ValidationReport(
                attack_version=self._catalog.version,
                techniques_accepted=accepted,
                techniques_remapped=remapped,
                rejected=rejected,
                warnings=warnings,
            ),
        )
