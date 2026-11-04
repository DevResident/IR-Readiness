"""Prompt construction for the Tabletop Exercise Generator.

The request contains only enum values (no free text from the user), so there is
no user-controlled text that could carry a prompt injection into this prompt.
"""

from __future__ import annotations

from app.catalogs.attack import AttackCatalog
from app.catalogs.ir_lifecycle import IRLifecycle
from app.catalogs.scenarios import ScenarioTemplate
from app.modules.tabletop.schemas import Audience, OrgSize, TabletopRequest

SYSTEM_PROMPT = """\
You are an experienced incident response consultant who designs tabletop exercises \
for client organizations. A tabletop exercise is a discussion-based simulation: \
participants talk through how they would respond to a realistic incident, so the \
organization can find gaps in its incident response plan before a real incident.

Write for a professional consulting deliverable: concrete, realistic, and specific \
to the client's industry and size. Use fictional names for the organization, people \
and vendors. Do not include real malware code, exploit instructions or other \
operational attack details; describe attacker activity only at the level a defender \
needs to discuss detection and response.

Framework rules:
- Every inject must have a phase from the list you are given. Phases follow NIST SP \
800-61 Rev. 3, which models incident response with the CSF 2.0 Functions.
- technique_ids must be MITRE ATT&CK Enterprise technique IDs (format T1234 or \
T1234.001). Prefer the suggested techniques. Never invent an ID: if you are not sure \
an ID exists, leave it out. Every ID is checked against ATT&CK and unknown IDs are removed.
- csf_category, when used, must be one of the CSF 2.0 categories you are given, or null.
"""

AUDIENCE_GUIDANCE = {
    Audience.TECHNICAL: (
        "The audience is technical: IT operations and security staff. Focus injects and "
        "questions on detection sources, triage, scoping, containment options, evidence "
        "preservation, eradication and restoring systems."
    ),
    Audience.EXECUTIVE: (
        "The audience is executive leadership. Focus injects and questions on business "
        "impact, decision authority, legal and regulatory obligations, communication with "
        "employees, customers, regulators and the media, third parties such as insurers "
        "and law enforcement, and recovery priorities. Avoid deep technical detail."
    ),
}

ORG_SIZE_LABEL = {
    OrgSize.SMALL: "small (fewer than 250 employees, likely no dedicated security team)",
    OrgSize.MEDIUM: "medium (250 to 2,500 employees, a small security team)",
    OrgSize.LARGE: "large (more than 2,500 employees, a dedicated security operations team)",
}


def build_prompt(
    request: TabletopRequest,
    scenario: ScenarioTemplate,
    catalog: AttackCatalog,
    lifecycle: IRLifecycle,
) -> str:
    stages = []
    for stage in scenario.attack_path:
        techniques = ", ".join(
            f"{tid} {tech.name}" for tid in stage.techniques if (tech := catalog.get(tid)) is not None
        )
        stages.append(f"- {stage.stage}: {stage.description} Suggested techniques: {techniques}")

    phases = "\n".join(
        f"- {p.id}: {p.name} (CSF 2.0: {', '.join(p.csf_functions)}). {p.description}"
        for p in lifecycle.phases
    )
    categories = "\n".join(f"- {cid}: {name}" for cid, name in lifecycle.csf_categories.items())
    num_injects = max(4, min(10, request.duration_minutes // 12))

    return f"""\
Design a tabletop exercise with these parameters.

Client industry: {request.industry.value.replace("_", " ")}
Client size: {ORG_SIZE_LABEL[request.org_size]}
Exercise length: {request.duration_minutes} minutes
{AUDIENCE_GUIDANCE[request.audience]}

Scenario: {scenario.name}
{scenario.summary}

Typical attack path:
{chr(10).join(stages)}

Decisions this scenario should force:
{chr(10).join(f"- {d}" for d in scenario.key_decisions)}

Stakeholders to consider for roles: {", ".join(scenario.stakeholders)}

Phases (use these exact IDs):
{phases}

CSF 2.0 categories you may reference:
{categories}

Requirements:
- About {num_injects} injects in chronological order, with sequence numbers starting at 1, \
escalating in pressure. Most injects belong to detect, respond and recover.
- Discussion questions for each of detect, respond, recover and improve; 3 to 5 per phase.
- A facilitator guide with preparation steps, a timed agenda that fits {request.duration_minutes} \
minutes, facilitation tips, and the gaps this exercise is expected to surface.
"""
