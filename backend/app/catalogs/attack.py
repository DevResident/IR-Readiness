"""Validation of MITRE ATT&CK technique IDs against the local, MITRE-generated subset.

Design rule: the LLM is allowed to *suggest* technique IDs, but only this module
decides whether an ID is real. Names, tactics and URLs always come from the
catalog, never from the model's text.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from enum import Enum
from functools import lru_cache
from pathlib import Path

from app.catalogs.paths import FRAMEWORKS_DIR

DEFAULT_CATALOG = FRAMEWORKS_DIR / "attack" / "enterprise-attack-v20.0-subset.json"

# T + 4 digits, optionally a sub-technique suffix of 3 digits (e.g. T1566 or T1566.001).
TECHNIQUE_ID_RE = re.compile(r"^T\d{4}(?:\.\d{3})?$")


class Status(str, Enum):
    VALID = "valid"            # active technique; safe to show
    REMAPPED = "remapped"      # revoked by MITRE, replaced with its official successor
    REVOKED = "revoked"        # revoked with no successor; discard
    DEPRECATED = "deprecated"  # no longer maintained by MITRE; discard
    UNKNOWN = "unknown"        # well-formed but not in ATT&CK (likely hallucinated); discard
    MALFORMED = "malformed"    # not even shaped like a technique ID; discard


@dataclass(frozen=True)
class Technique:
    id: str
    name: str
    tactics: tuple[str, ...]
    url: str | None


@dataclass(frozen=True)
class ValidationResult:
    input_id: str
    status: Status
    technique: Technique | None = None  # set only when the ID can be kept
    note: str | None = None

    @property
    def accepted(self) -> bool:
        return self.technique is not None


class AttackCatalog:
    def __init__(self, data: dict):
        self.source: dict = data["source"]
        self._techniques: dict[str, dict] = data["techniques"]
        self._revoked: dict[str, dict] = data.get("revoked", {})
        self._deprecated: dict[str, dict] = data.get("deprecated", {})

    @classmethod
    def from_file(cls, path: Path = DEFAULT_CATALOG) -> "AttackCatalog":
        with open(path, encoding="utf-8") as f:
            return cls(json.load(f))

    @property
    def version(self) -> str:
        return self.source["version"]

    def __len__(self) -> int:
        return len(self._techniques)

    def get(self, technique_id: str) -> Technique | None:
        raw = self._techniques.get(technique_id)
        if raw is None:
            return None
        return Technique(technique_id, raw["name"], tuple(raw["tactics"]), raw.get("url"))

    def validate(self, technique_id: str) -> ValidationResult:
        tid = technique_id.strip().upper()

        if not TECHNIQUE_ID_RE.match(tid):
            return ValidationResult(technique_id, Status.MALFORMED, note="Not an ATT&CK technique ID format")

        if (tech := self.get(tid)) is not None:
            return ValidationResult(technique_id, Status.VALID, tech)

        if tid in self._revoked:
            successor_id = self._revoked[tid].get("revoked_by")
            successor = self.get(successor_id) if successor_id else None
            if successor is not None:
                return ValidationResult(
                    technique_id,
                    Status.REMAPPED,
                    successor,
                    note=f"{tid} was revoked by MITRE and replaced by {successor.id}",
                )
            return ValidationResult(technique_id, Status.REVOKED, note=f"{tid} was revoked by MITRE")

        if tid in self._deprecated:
            return ValidationResult(technique_id, Status.DEPRECATED, note=f"{tid} is deprecated in ATT&CK")

        return ValidationResult(
            technique_id, Status.UNKNOWN, note=f"{tid} does not exist in ATT&CK v{self.version}"
        )

    def filter_valid(self, technique_ids: list[str]) -> tuple[list[Technique], list[ValidationResult]]:
        """Split IDs into kept techniques (deduplicated, in order) and rejected results."""
        kept: list[Technique] = []
        rejected: list[ValidationResult] = []
        seen: set[str] = set()
        for tid in technique_ids:
            result = self.validate(tid)
            if result.accepted:
                if result.technique.id not in seen:
                    seen.add(result.technique.id)
                    kept.append(result.technique)
            else:
                rejected.append(result)
        return kept, rejected


@lru_cache(maxsize=1)
def get_catalog() -> AttackCatalog:
    """Load the catalog once per process (it is read-only)."""
    return AttackCatalog.from_file()
