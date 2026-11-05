"""Render a validated TabletopExercise as Markdown, ready to share with a client.

Only the public (validated) model is rendered, so every ATT&CK name and link comes
from the MITRE catalog, never from the model's text.
"""

from __future__ import annotations

from app.modules.tabletop.schemas import TabletopExercise

PHASE_TITLES = {
    "prepare": "Prepare (Govern, Identify, Protect)",
    "detect": "Detect",
    "respond": "Respond",
    "recover": "Recover",
    "improve": "Improve (ID.IM)",
}


def _bullets(items: list[str]) -> list[str]:
    return [f"- {item}" for item in items]


def render_markdown(exercise: TabletopExercise) -> str:
    r = exercise.request
    lines: list[str] = [
        f"# {exercise.title}",
        "",
        f"**Industry:** {r.industry.value} · **Size:** {r.org_size.value} · **Scenario:** {r.scenario} · "
        f"**Audience:** {r.audience.value} · **Duration:** {r.duration_minutes} min",
        "",
        "## Narrative",
        "",
        exercise.narrative,
        "",
        "## Objectives",
        "",
        *_bullets(exercise.objectives),
        "",
        "## Roles",
        "",
    ]
    for role in exercise.roles:
        lines += [f"**{role.title}**", "", *_bullets(role.responsibilities), ""]

    lines += ["## Injects", ""]
    for inject in exercise.injects:
        lines += [
            f"### {inject.sequence}. {inject.title}",
            "",
            f"*{inject.time_offset} · Phase: {PHASE_TITLES.get(inject.phase, inject.phase)}*",
            "",
            inject.description,
            "",
        ]
        if inject.techniques:
            refs = ", ".join(f"[{t.id} {t.name}]({t.url})" if t.url else f"{t.id} {t.name}"
                             for t in inject.techniques)
            lines += [f"**ATT&CK:** {refs}", ""]
        lines += ["**Expected actions:**", "", *_bullets(inject.expected_actions), ""]

    lines += ["## Discussion questions", ""]
    for phase, title in PHASE_TITLES.items():
        questions = [q for q in exercise.discussion_questions if q.phase == phase]
        if not questions:
            continue
        lines += [f"### {title}", ""]
        for q in questions:
            suffix = f" *({q.csf_category})*" if q.csf_category else ""
            lines.append(f"1. {q.question}{suffix}")
        lines.append("")

    guide = exercise.facilitator_guide
    lines += [
        "## Facilitator guide",
        "",
        "### Preparation", "", *_bullets(guide.preparation), "",
        "### Agenda", "", *_bullets(guide.agenda), "",
        "### Facilitation tips", "", *_bullets(guide.facilitation_tips), "",
        "### Expected gaps", "", *_bullets(guide.expected_gaps), "",
    ]

    v = exercise.validation
    lines += [
        "## Validation report",
        "",
        f"- ATT&CK version: Enterprise v{v.attack_version}",
        f"- Techniques accepted: {v.techniques_accepted}",
        f"- Techniques remapped: {len(v.techniques_remapped)}",
        f"- References rejected: {len(v.rejected)}",
    ]
    lines += [f"  - {x}" for x in v.techniques_remapped]
    lines += [f"  - {x.location}: `{x.value}` ({x.reason})" for x in v.rejected]
    lines += [f"- Warning: {w}" for w in v.warnings]
    lines += ["", "*Fictional scenario for training purposes. Generated with IR Readiness Copilot.*", ""]
    return "\n".join(lines)
