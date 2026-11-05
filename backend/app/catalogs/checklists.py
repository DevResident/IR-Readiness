"""IR plan readiness checklist (Module 1), loaded from frameworks/checklists/."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field, model_validator

from app.catalogs.paths import FRAMEWORKS_DIR

CHECKLIST_FILE = FRAMEWORKS_DIR / "checklists" / "ir-plan-readiness.json"

Priority = Literal["critical", "high", "medium"]


class ChecklistControl(BaseModel):
    id: str = Field(pattern=r"^IRP-\d{2}$")
    topic: str
    title: str
    look_for: list[str] = Field(min_length=1)
    csf_subcategories: list[str] = Field(min_length=1)
    sp800_61r3: str
    phase: Literal["prepare", "detect", "respond", "recover", "improve"]
    priority: Priority


class Checklist(BaseModel):
    id: str
    version: str
    title: str
    description: str
    sources: list[dict]
    notes: str
    priority_weights: dict[Priority, int]
    controls: list[ChecklistControl] = Field(min_length=1)

    @model_validator(mode="after")
    def _unique_ids(self) -> Checklist:
        ids = [c.id for c in self.controls]
        if len(ids) != len(set(ids)):
            raise ValueError("Duplicate control IDs in checklist")
        return self

    def weight(self, control: ChecklistControl) -> int:
        return self.priority_weights[control.priority]


def load_checklist(path: Path = CHECKLIST_FILE) -> Checklist:
    return Checklist.model_validate(json.loads(path.read_text(encoding="utf-8")))


@lru_cache(maxsize=1)
def get_checklist() -> Checklist:
    return load_checklist()
