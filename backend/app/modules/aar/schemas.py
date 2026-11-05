"""Schemas for the After-Action Report (AAR) generator.

Input is free text (exercise or incident notes), so it is untrusted. The LLM fills an
``AARDraft``; the service verifies every quoted note excerpt, validates CSF categories
and links between recommendations and observations, then builds the public ``AfterActionReport``.
"""

from __future__ import annotations

from datetime import date
from typing import Annotated, Literal

from pydantic import BaseModel, Field, StringConstraints

PhaseId = Literal["prepare", "detect", "respond", "recover", "improve"]
Priority = Literal["high", "medium", "low"]
ObservationKind = Literal["strength", "improvement"]
Timeframe = Literal["30 days", "90 days", "180 days"]

ShortText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=400)]
LongText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=2500)]
MAX_NOTES_CHARS = 30_000


# ---------- Input ----------

class AARRequest(BaseModel):
    notes: Annotated[str, StringConstraints(strip_whitespace=True, min_length=50, max_length=MAX_NOTES_CHARS)] = Field(
        description="Raw notes from the exercise or incident: what happened, decisions, issues raised."
    )
    exercise_title: Annotated[str, StringConstraints(strip_whitespace=True, max_length=200)] | None = None
    event_type: Literal["tabletop", "incident"] = "tabletop"
    event_date: date | None = None


# ---------- LLM draft (untrusted) ----------

class ObservationDraft(BaseModel):
    id: str = Field(description="Short ID such as O1, O2.")
    kind: ObservationKind
    title: ShortText
    detail: LongText
    phase: PhaseId
    csf_category: str | None = Field(default=None, description="CSF 2.0 category ID from the allowed list, or null.")
    evidence_quote: Annotated[str, StringConstraints(strip_whitespace=True, max_length=400)] | None = Field(
        default=None, description="Exact excerpt copied from the notes that supports this observation."
    )


class RecommendationDraft(BaseModel):
    title: ShortText
    action: LongText
    priority: Priority
    timeframe: Timeframe
    suggested_owner: ShortText = Field(description="A role, not a person's name, e.g. 'Incident Response Lead'.")
    addresses: list[str] = Field(min_length=1, max_length=6, description="Observation IDs this recommendation fixes.")
    csf_category: str | None = None


class AARDraft(BaseModel):
    title: ShortText
    executive_summary: LongText
    scope: LongText
    observations: list[ObservationDraft] = Field(min_length=2, max_length=20)
    gaps: list[ShortText] = Field(min_length=1, max_length=12, description="Plan, process or capability gaps found.")
    recommendations: list[RecommendationDraft] = Field(min_length=1, max_length=15)


# ---------- Validated output ----------

class Observation(BaseModel):
    id: str
    kind: ObservationKind
    title: str
    detail: str
    phase: PhaseId
    csf_category: str | None
    csf_title: str | None
    evidence_quote: str | None
    evidence_verified: bool


class Recommendation(BaseModel):
    rank: int
    title: str
    action: str
    priority: Priority
    timeframe: Timeframe
    suggested_owner: str
    addresses: list[str]
    csf_category: str | None
    csf_title: str | None


class AARValidation(BaseModel):
    unverified_observations: list[str] = Field(description="Observation IDs whose quote was not found in the notes.")
    rejected_csf_categories: list[str]
    dropped_links: list[str] = Field(description="Recommendation links to observation IDs that do not exist.")
    warnings: list[str] = Field(default_factory=list)


class AfterActionReport(BaseModel):
    title: str
    event_type: Literal["tabletop", "incident"]
    event_date: date | None
    executive_summary: str
    scope: str
    strengths: list[Observation]
    areas_for_improvement: list[Observation]
    gaps: list[str]
    recommendations: list[Recommendation] = Field(description="Sorted by priority, then timeframe.")
    validation: AARValidation
