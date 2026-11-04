"""Tabletop scenario templates stored as JSON in /frameworks/scenarios.

A template gives the LLM a realistic attack path and suggested ATT&CK techniques
to build on. Adding a scenario means adding a JSON file; no code changes.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from pydantic import BaseModel, Field

from app.catalogs.paths import FRAMEWORKS_DIR

DEFAULT_DIR = FRAMEWORKS_DIR / "scenarios"


class AttackStage(BaseModel):
    stage: str
    description: str
    techniques: list[str] = Field(min_length=1)


class ScenarioTemplate(BaseModel):
    id: str
    name: str
    summary: str
    attack_path: list[AttackStage] = Field(min_length=1)
    key_decisions: list[str]
    stakeholders: list[str]
    csf_focus: list[str]

    @property
    def technique_ids(self) -> list[str]:
        return [t for stage in self.attack_path for t in stage.techniques]


def load_scenarios(directory: Path = DEFAULT_DIR) -> dict[str, ScenarioTemplate]:
    scenarios: dict[str, ScenarioTemplate] = {}
    for path in sorted(directory.glob("*.json")):
        with open(path, encoding="utf-8") as f:
            scenario = ScenarioTemplate.model_validate(json.load(f))
        if scenario.id != path.stem:
            raise ValueError(f"{path.name}: id '{scenario.id}' must match the file name")
        scenarios[scenario.id] = scenario
    return scenarios


@lru_cache(maxsize=1)
def get_scenarios() -> dict[str, ScenarioTemplate]:
    return load_scenarios()
