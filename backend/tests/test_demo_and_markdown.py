import pytest

from app.catalogs.attack import get_catalog
from app.catalogs.ir_lifecycle import get_ir_lifecycle
from app.catalogs.scenarios import get_scenarios
from app.llm.base import LLMNotConfiguredError
from app.llm.demo import DEMO_TABLETOP_FILE, DemoStructuredLLM, exercise_to_draft, load_demo_tabletop
from app.modules.tabletop.markdown import render_markdown
from app.modules.tabletop.schemas import TabletopDraft, TabletopRequest
from app.modules.tabletop.service import TabletopService

REQUEST = TabletopRequest(industry="healthcare", org_size="medium", scenario="ransomware", audience="executive")


def _service(llm, notice=None):
    return TabletopService(llm, get_catalog(), get_ir_lifecycle(), get_scenarios(), notice=notice)


def test_example_survives_current_validation_unchanged():
    """The committed example must still be fully valid against today's catalogs."""
    saved = load_demo_tabletop()
    rebuilt = _service(DemoStructuredLLM.default()).generate(saved.request)
    assert rebuilt.model_dump() == saved.model_dump()
    assert saved.validation.rejected == []
    assert {q.phase for q in saved.discussion_questions} == {"detect", "respond", "recover", "improve"}


def test_exercise_to_draft_keeps_only_technique_ids():
    draft = exercise_to_draft(load_demo_tabletop())
    assert draft.injects[0].technique_ids == ["T1566.001", "T1059.001"]
    assert len(draft.discussion_questions.improve) == 4


def test_demo_llm_rejects_unknown_schema():
    with pytest.raises(LLMNotConfiguredError):
        DemoStructuredLLM.default().generate(system="", prompt="", schema=TabletopRequest)


def test_demo_llm_returns_a_copy():
    llm = DemoStructuredLLM.default()
    first = llm.generate(system="", prompt="", schema=TabletopDraft)
    first.title = "changed"
    assert llm.generate(system="", prompt="", schema=TabletopDraft).title != "changed"


def test_notice_is_the_first_warning():
    exercise = _service(DemoStructuredLLM.default(), notice="Demo mode").generate(REQUEST)
    assert exercise.validation.warnings[0] == "Demo mode"


def test_markdown_example_is_in_sync_with_json():
    expected = render_markdown(load_demo_tabletop())
    assert DEMO_TABLETOP_FILE.with_suffix(".md").read_text(encoding="utf-8") == expected


def test_markdown_links_techniques_and_groups_questions():
    md = render_markdown(load_demo_tabletop())
    assert "[T1486 Data Encrypted for Impact](https://attack.mitre.org/techniques/T1486)" in md
    assert md.index("### Detect") < md.index("### Respond") < md.index("### Recover") < md.index("### Improve")
    assert "*(RC.RP)*" in md


def test_demo_mode_runs_the_api_without_a_key(monkeypatch):
    from fastapi.testclient import TestClient

    from app.api import deps
    from app.api.routes import health
    from app.core.config import Settings
    from app.main import app

    demo = Settings(llm_provider="demo", anthropic_api_key=None, _env_file=None)
    deps.get_llm.cache_clear()
    monkeypatch.setattr(deps, "get_settings", lambda: demo)
    monkeypatch.setattr(health, "get_settings", lambda: demo)
    try:
        client = TestClient(app)
        assert client.get("/api/health").json()["llm_provider"] == "demo"
        assert client.get("/api/health").json()["llm_configured"] is True
        other = {"industry": "technology", "org_size": "large", "scenario": "bec", "audience": "technical"}
        res = client.post("/api/tabletop", json=other)
    finally:
        deps.get_llm.cache_clear()
    assert res.status_code == 200
    body = res.json()
    assert body["validation"]["warnings"][0] == deps.DEMO_NOTICE
    assert body["validation"]["techniques_accepted"] == 9
    # The response reports what the content was generated for, not the ignored form inputs.
    assert body["request"] == REQUEST.model_dump(mode="json")


def test_markdown_export_endpoint():
    from fastapi.testclient import TestClient

    from app.main import app

    saved = load_demo_tabletop()
    res = TestClient(app).post("/api/tabletop/markdown", json=saved.model_dump(mode="json"))
    assert res.status_code == 200
    assert res.headers["content-type"].startswith("text/markdown")
    assert res.text == render_markdown(saved)


def test_markdown_export_rejects_invalid_body():
    from fastapi.testclient import TestClient

    from app.main import app

    assert TestClient(app).post("/api/tabletop/markdown", json={"title": "x"}).status_code == 422
