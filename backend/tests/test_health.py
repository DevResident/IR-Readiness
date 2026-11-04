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
