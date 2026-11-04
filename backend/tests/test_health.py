from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_reports_attack_catalog():
    body = client.get("/api/health").json()
    assert body["status"] == "ok"
    assert body["attack_version"] == "20.0"
    assert body["attack_techniques"] > 500


def test_validate_endpoint_flags_invented_id():
    body = client.get("/api/attack/techniques/T1999").json()
    assert body == {
        "input": "T1999",
        "status": "unknown",
        "accepted": False,
        "technique": None,
        "note": "T1999 does not exist in ATT&CK v20.0",
    }


def test_tabletop_options_lists_scenarios_and_phases():
    body = client.get("/api/tabletop/options").json()
    assert {s["id"] for s in body["scenarios"]} == {"ransomware", "bec", "insider_threat", "supply_chain"}
    assert [p["id"] for p in body["phases"]] == ["prepare", "detect", "respond", "recover", "improve"]


def test_generate_tabletop_with_fake_llm():
    from app.api.deps import get_tabletop_service
    from app.catalogs.attack import get_catalog
    from app.catalogs.ir_lifecycle import get_ir_lifecycle
    from app.catalogs.scenarios import get_scenarios
    from app.modules.tabletop.service import TabletopService
    from tests.fakes import FakeLLM, make_draft

    fake = TabletopService(FakeLLM(make_draft()), get_catalog(), get_ir_lifecycle(), get_scenarios())
    app.dependency_overrides[get_tabletop_service] = lambda: fake
    try:
        res = client.post("/api/tabletop", json={
            "industry": "healthcare", "org_size": "medium", "scenario": "ransomware", "audience": "technical",
        })
    finally:
        app.dependency_overrides.clear()
    assert res.status_code == 200
    body = res.json()
    assert body["injects"][0]["techniques"][0]["name"] == "Data Encrypted for Impact"
    assert body["validation"]["attack_version"] == "20.0"


def test_generate_tabletop_without_api_key_returns_503(monkeypatch):
    from app.api import deps
    from app.core.config import Settings

    deps.get_llm.cache_clear()
    monkeypatch.setattr(deps, "get_settings", lambda: Settings(anthropic_api_key=None, _env_file=None))
    res = client.post("/api/tabletop", json={
        "industry": "retail", "org_size": "small", "scenario": "bec", "audience": "executive",
    })
    deps.get_llm.cache_clear()
    assert res.status_code == 503


def test_generate_tabletop_rejects_bad_input():
    res = client.post("/api/tabletop", json={"industry": "retail", "org_size": "small", "scenario": "ddos", "audience": "executive"})
    assert res.status_code == 422
