"""Tests for the ATT&CK validator.

The real-ID cases below were checked against ATT&CK v20.0 (attack.mitre.org).
The synthetic catalog tests exercise each status branch without depending on MITRE data.
"""

import pytest

from app.catalogs.attack import AttackCatalog, Status, get_catalog

SYNTHETIC = {
    "source": {"version": "test"},
    "techniques": {
        "T1486": {"name": "Data Encrypted for Impact", "tactics": ["impact"], "url": None},
        "T1685": {"name": "Disable or Modify Tools", "tactics": ["defense-impairment"], "url": None},
    },
    "revoked": {
        "T1562.001": {"name": "Disable or Modify Tools", "revoked_by": "T1685"},
        "T9000": {"name": "Gone", "revoked_by": None},
    },
    "deprecated": {"T1000": {"name": "Old technique"}},
}


@pytest.fixture
def synthetic() -> AttackCatalog:
    return AttackCatalog(SYNTHETIC)


@pytest.mark.parametrize(
    "tid, status, accepted",
    [
        ("T1486", Status.VALID, True),
        (" t1486 ", Status.VALID, True),          # normalized: trimmed and upper-cased
        ("T1562.001", Status.REMAPPED, True),     # revoked with successor -> successor kept
        ("T9000", Status.REVOKED, False),
        ("T1000", Status.DEPRECATED, False),
        ("T1999", Status.UNKNOWN, False),         # well-formed but made up
        ("T1486.1", Status.MALFORMED, False),
        ("Phishing", Status.MALFORMED, False),
        ("TA0001", Status.MALFORMED, False),      # a tactic ID, not a technique ID
    ],
)
def test_status_branches(synthetic, tid, status, accepted):
    result = synthetic.validate(tid)
    assert result.status is status
    assert result.accepted is accepted


def test_remap_returns_successor(synthetic):
    result = synthetic.validate("T1562.001")
    assert result.technique.id == "T1685"
    assert "replaced by T1685" in result.note


def test_filter_valid_dedupes_and_reports(synthetic):
    kept, rejected = synthetic.filter_valid(["T1486", "T1486", "T1999", "T1562.001", "T1685"])
    assert [t.id for t in kept] == ["T1486", "T1685"]
    assert [r.input_id for r in rejected] == ["T1999"]


# --- Real catalog (generated from MITRE's official STIX data) ---

@pytest.mark.parametrize(
    "tid, name",
    [
        ("T1486", "Data Encrypted for Impact"),
        ("T1490", "Inhibit System Recovery"),
        ("T1566.001", "Spearphishing Attachment"),
        ("T1114.003", "Email Forwarding Rule"),
        ("T1195.002", "Compromise Software Supply Chain"),
        ("T1052.001", "Exfiltration over USB"),
    ],
)
def test_real_catalog_known_techniques(tid, name):
    result = get_catalog().validate(tid)
    assert result.status is Status.VALID
    assert result.technique.name == name


def test_real_catalog_rejects_invented_id():
    assert get_catalog().validate("T1999.999").status is Status.UNKNOWN


def test_real_catalog_remaps_revoked_technique():
    # In ATT&CK v20.0, T1562.001 "Disable or Modify Tools" was revoked and replaced by T1685.
    result = get_catalog().validate("T1562.001")
    assert result.status is Status.REMAPPED
    assert result.technique.id == "T1685"
