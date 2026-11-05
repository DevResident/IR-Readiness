"""Schemas for the Tabletop Exercise Generator.

There are deliberately two output models:

* ``TabletopDraft`` is what the LLM must fill in. It contains raw technique IDs
  as plain strings, because the model's claims are untrusted.
* ``TabletopExercise`` is what the API returns. It is built by the service after
  every technique ID has been validated against the local ATT&CK catalog, so
  names and URLs come from MITRE data, never from the model.

Length and count limits keep the LLM output bounded and the UI predictable.
"""

from __future__ import annotations

from enum import Enum
from typing import Annotated, Literal

from pydantic import BaseModel, Field, StringConstraints

# Phase IDs from frameworks/nist/ir-lifecycle-800-61r3.json (SP 800-61r3, Section 2.1).
# A test keeps this Literal in sync with the JSON file.
PhaseId = Literal["prepare", "detect", "respond", "recover", "improve"]

# Scenario IDs = file names in frameworks/scenarios/. Also kept in sync by a test.
ScenarioId = Literal["ransomware", "bec", "insider_threat", "supply_chain"]

ShortText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=300)]
LongText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=3000)]


# ---------- Input ----------

class Industry(str, Enum):
    HEALTHCARE = "healthcare"
    FINANCIAL_SERVICES = "financial_services"
    MANUFACTURING = "manufacturing"
    RETAIL = "retail"
    TECHNOLOGY = "technology"
    EDUCATION = "education"
    GOVERNMENT = "government"
    ENERGY = "energy"
    PROFESSIONAL_SERVICES = "professional_services"


class OrgSize(str, Enum):
    SMALL = "small"      # fewer than 250 employees
    MEDIUM = "medium"    # 250 to 2,500 employees
    LARGE = "large"      # more than 2,500 employees


class Audience(str, Enum):
    TECHNICAL = "technical"  # IT / security staff: focus on detection, containment, forensics
    EXECUTIVE = "executive"  # leadership: focus on decisions, communication, business impact


class TabletopRequest(BaseModel):
    industry: Industry
    org_size: OrgSize
    scenario: ScenarioId
    audience: Audience
    duration_minutes: int = Field(default=90, ge=30, le=240)


# ---------- Parts shared by the draft and the final exercise ----------

class Role(BaseModel):
    title: ShortText
    responsibilities: list[str] = Field(min_length=1, max_length=6)


class DiscussionQuestion(BaseModel):
    phase: PhaseId
    question: ShortText
    csf_category: str | None = Field(
        default=None, description="Optional CSF 2.0 category ID, e.g. RS.CO. Validated by the service."
    )


class QuestionDraft(BaseModel):
    question: ShortText
    csf_category: str | None = Field(
        default=None, description="Optional CSF 2.0 category ID, e.g. RS.CO. Validated by the service."
    )


class QuestionsByPhase(BaseModel):
    """One required list per phase, so the model cannot skip a phase.

    A flat list with a phase field let a real model return only 'detect' questions.
    With required keys, structured outputs guarantee every phase is present, and the
    minimum count is validated client-side (triggering a corrective retry).
    """

    detect: list[QuestionDraft] = Field(min_length=2, max_length=6)
    respond: list[QuestionDraft] = Field(min_length=2, max_length=6)
    recover: list[QuestionDraft] = Field(min_length=2, max_length=6)
    improve: list[QuestionDraft] = Field(min_length=2, max_length=6)


class FacilitatorGuide(BaseModel):
    preparation: list[str] = Field(min_length=1, max_length=10)
    agenda: list[str] = Field(min_length=1, max_length=12)
    facilitation_tips: list[str] = Field(min_length=1, max_length=10)
    expected_gaps: list[str] = Field(
        min_length=1, max_length=10, description="Weaknesses this exercise is designed to surface."
    )


# ---------- LLM draft (untrusted) ----------

class InjectDraft(BaseModel):
    sequence: int = Field(ge=1)
    time_offset: str = Field(min_length=1, max_length=20, description="Exercise clock, e.g. 'T+0h' or 'Day 2, 09:00'.")
    title: ShortText
    description: LongText
    phase: PhaseId
    technique_ids: list[str] = Field(default_factory=list, max_length=6)
    expected_actions: list[str] = Field(min_length=1, max_length=8)


class TabletopDraft(BaseModel):
    title: ShortText
    narrative: LongText
    objectives: list[str] = Field(min_length=1, max_length=8)
    roles: list[Role] = Field(min_length=1, max_length=12)
    injects: list[InjectDraft] = Field(min_length=3, max_length=12)
    discussion_questions: QuestionsByPhase
    facilitator_guide: FacilitatorGuide


# ---------- Validated output (returned by the API) ----------

class AttackTechniqueRef(BaseModel):
    id: str
    name: str
    tactics: list[str]
    url: str | None


class Inject(BaseModel):
    sequence: int
    time_offset: str
    title: str
    description: str
    phase: PhaseId
    techniques: list[AttackTechniqueRef]
    expected_actions: list[str]


class RejectedReference(BaseModel):
    """A framework ID the LLM produced that did not survive validation."""

    location: str = Field(description="Where it appeared, e.g. 'inject 3'.")
    value: str
    reason: str


class ValidationReport(BaseModel):
    attack_version: str
    techniques_accepted: int
    techniques_remapped: list[str] = Field(description="Notes for revoked IDs replaced by their official successor.")
    rejected: list[RejectedReference]
    warnings: list[str] = Field(default_factory=list, description="Quality issues that did not block the exercise.")


class TabletopExercise(BaseModel):
    request: TabletopRequest
    title: str
    narrative: str
    objectives: list[str]
    roles: list[Role]
    injects: list[Inject]
    discussion_questions: list[DiscussionQuestion]
    facilitator_guide: FacilitatorGuide
    validation: ValidationReport
