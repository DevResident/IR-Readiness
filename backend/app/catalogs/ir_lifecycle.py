"""Incident response life cycle phases from NIST SP 800-61 Rev. 3 (Section 2.1, Fig. 2 and Table 1)."""

from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from app.catalogs.paths import FRAMEWORKS_DIR

DEFAULT_PATH = FRAMEWORKS_DIR / "nist" / "ir-lifecycle-800-61r3.json"


@dataclass(frozen=True)
class Phase:
    id: str
    name: str
    csf_functions: tuple[str, ...]
    is_incident_response: bool
    rev2_equivalent: str
    description: str


class IRLifecycle:
    def __init__(self, data: dict):
        self.source: dict = data["source"]
        self.phases: tuple[Phase, ...] = tuple(
            Phase(**{**p, "csf_functions": tuple(p["csf_functions"])}) for p in data["phases"]
        )
        self.csf_categories: dict[str, str] = data["csf_categories"]

    @classmethod
    def from_file(cls, path: Path = DEFAULT_PATH) -> "IRLifecycle":
        with open(path, encoding="utf-8") as f:
            return cls(json.load(f))

    @property
    def phase_ids(self) -> tuple[str, ...]:
        return tuple(p.id for p in self.phases)

    def is_known_csf_category(self, category_id: str) -> bool:
        return category_id in self.csf_categories


@lru_cache(maxsize=1)
def get_ir_lifecycle() -> IRLifecycle:
    return IRLifecycle.from_file()
