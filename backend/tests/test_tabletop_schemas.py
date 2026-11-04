import pytest
from pydantic import ValidationError

from app.modules.tabletop.schemas import TabletopDraft, TabletopRequest
from tests.fakes import make_draft


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
