"""Schemas for the IR Plan Readiness Assessment.

As in the tabletop module, the LLM fills an untrusted draft (``AssessmentDraft``) and
the service builds the public ``AssessmentReport`` after deterministic checks: every
control ID must exist, every quote must be found in the document, and the score is
computed in code, never by the model.
"""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, Field, StringConstraints

from app.modules.assessment.ingest import DocumentKind

Status = Literal["met", "partial", "missing"]
Priority = Literal["critical", "high", "medium"]

Quote = Annotated[str, StringConstraints(strip_whitespace=True, max_length=600)]
ShortText = Annotated[str, StringConstraints(strip_whitespace=True, max_length=600)]


# ---------- LLM draft (untrusted) ----------

class ControlFindingDraft(BaseModel):
    control_id: str = Field(description="Checklist control ID, e.g. IRP-05.")
    status: Status
    evidence_quote: Quote | None = Field(
        default=None,
        description="Exact text copied from the document that supports the status. Required for met or partial. "
        "Use '...' only to join two exact fragments from the same passage.",
    )
    rationale: ShortText = Field(description="Why this status: which look_for elements are present or absent.")
    recommendation: ShortText = Field(
        description="Concrete improvement to the plan. Empty string if the control is fully met."
    )


class AssessmentDraft(BaseModel):
    findings: list[ControlFindingDraft] = Field(min_length=1, max_length=40)
    summary: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=1500)] = Field(
        description="Three to five sentences for an executive: overall readiness and the most important gaps."
    )


# ---------- Validated output (returned by the API) ----------

class CsfReference(BaseModel):
    id: str
    text: str


class Evidence(BaseModel):
    quote: str
    verified: bool = Field(description="True if the quote was found in the document text.")


class ControlResult(BaseModel):
    control_id: str
    title: str
    topic: str
    phase: str
    priority: Priority
    csf: list[CsfReference]
    sp800_61r3: str
    status: Status
    model_status: Status = Field(description="Status the model proposed, before evidence verification.")
    evidence: Evidence | None
    rationale: str
    recommendation: str


class ScoreBreakdown(BaseModel):
    score: float = Field(description="0-100, weighted by priority: 100 × Σ(weight × credit) / Σ(weight).")
    coverage: float = Field(description="0-100, share of controls that are met or partial.")
    met: int
    partial: int
    missing: int
    formula: str


class DocumentInfo(BaseModel):
    kind: DocumentKind
    pages: int | None
    characters: int
    truncated: bool


class AssessmentValidation(BaseModel):
    unverified_quotes: list[str] = Field(description="Controls downgraded because their quote was not in the document.")
    unknown_controls: list[str] = Field(description="Control IDs the model returned that are not in the checklist.")
    not_assessed: list[str] = Field(description="Controls the model skipped; they are scored as missing.")
    warnings: list[str] = Field(default_factory=list)


class AssessmentReport(BaseModel):
    checklist: str
    document: DocumentInfo
    summary: str
    score: ScoreBreakdown
    results: list[ControlResult] = Field(description="All controls, in checklist order.")
    top_gaps: list[str] = Field(description="Control IDs to fix first: missing or partial, by priority.")
    validation: AssessmentValidation
