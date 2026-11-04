"""Integrity tests for the JSON framework data.

These protect the "never invent IDs" rule at the data level: if someone edits a
scenario file with a typo'd or revoked technique, CI fails before the LLM ever sees it.
"""

import typing

import pytest

from app.catalogs.attack import Status, get_catalog
from app.catalogs.ir_lifecycle import get_ir_lifecycle
from app.catalogs.scenarios import get_scenarios
from app.modules.tabletop.schemas import PhaseId, ScenarioId

SCENARIOS = get_scenarios()


def test_scenario_ids_match_schema_literal():
    assert set(SCENARIOS) == set(typing.get_args(ScenarioId))


def test_phase_ids_match_schema_literal():
    assert get_ir_lifecycle().phase_ids == typing.get_args(PhaseId)


@pytest.mark.parametrize("scenario_id", sorted(SCENARIOS))
def test_scenario_techniques_are_active_attack_ids(scenario_id):
    catalog = get_catalog()
    for tid in SCENARIOS[scenario_id].technique_ids:
        # VALID only: scenario data must use current IDs, not ones that need remapping.
        assert catalog.validate(tid).status is Status.VALID, f"{scenario_id}: {tid}"


@pytest.mark.parametrize("scenario_id", sorted(SCENARIOS))
def test_scenario_csf_focus_uses_known_categories(scenario_id):
    lifecycle = get_ir_lifecycle()
    for cat in SCENARIOS[scenario_id].csf_focus:
        assert lifecycle.is_known_csf_category(cat), f"{scenario_id}: {cat}"


def test_lifecycle_matches_800_61r3_model():
    # SP 800-61r3 Section 2.1: Detect, Respond and Recover are the incident response itself.
    ir = {p.id for p in get_ir_lifecycle().phases if p.is_incident_response}
    assert ir == {"detect", "respond", "recover"}
