import pytest
from pydantic import ValidationError

from app.modules.tabletop.schemas import TabletopDraft, TabletopRequest


def make_draft(**overrides) -> dict:
    inject = {
        "sequence": 1,
        "time_offset": "T+0h",
        "title": "Help desk ticket",
        "description": "Several users report they cannot open files on the shared drive.",
        "phase": "detect",
        "technique_ids": ["T1486"],
        "expected_actions": ["Triage the ticket", "Escalate to the security team"],
    }
    draft = {
        "title": "Operation Cold Storage",
        "narrative": "A regional hospital discovers encrypted file shares on a Monday morning.",
        "objectives": ["Test escalation paths"],
        "roles": [{"title": "Incident response lead", "responsibilities": ["Coordinate the response"]}],
        "injects": [inject, {**inject, "sequence": 2}, {**inject, "sequence": 3}],
        "discussion_questions": [
            {"phase": "detect", "question": "Who decides this is an incident?", "csf_category": "RS.MA"},
            {"phase": "respond", "question": "What do we isolate first?"},
            {"phase": "improve", "question": "What would we change in the plan?"},
        ],
        "facilitator_guide": {
            "preparation": ["Confirm participants"],
            "agenda": ["Introduction", "Injects", "Hot wash"],
            "facilitation_tips": ["Keep the clock moving"],
            "expected_gaps": ["No out-of-band communication channel"],
        },
    }
    draft.update(overrides)
    return draft


def test_valid_draft_parses():
    draft = TabletopDraft.model_validate(make_draft())
    assert len(draft.injects) == 3


def test_unknown_phase_is_rejected():
    bad = make_draft()
    bad["injects"][0]["phase"] = "containment"  # a Rev. 2 phase name, not a valid phase ID
    with pytest.raises(ValidationError):
        TabletopDraft.model_validate(bad)


def test_too_few_injects_is_rejected():
    bad = make_draft()
    bad["injects"] = bad["injects"][:2]
    with pytest.raises(ValidationError):
        TabletopDraft.model_validate(bad)


def test_overlong_text_is_rejected():
    with pytest.raises(ValidationError):
        TabletopDraft.model_validate(make_draft(title="x" * 301))


def test_request_rejects_unknown_scenario():
    with pytest.raises(ValidationError):
        TabletopRequest(industry="healthcare", org_size="medium", scenario="ddos", audience="executive")
