"""Integrity tests for the Module 1 checklist and the CSF 2.0 subset it cites."""

from app.catalogs.checklists import get_checklist
from app.catalogs.csf import SUBCATEGORY_RE, get_csf
from app.catalogs.ir_lifecycle import get_ir_lifecycle


def test_csf_subcategory_ids_are_well_formed_and_belong_to_a_known_category():
    csf = get_csf()
    for sid, text in csf.subcategories.items():
        assert SUBCATEGORY_RE.match(sid), sid
        assert csf.category_of(sid) in csf.categories, sid
        assert text.strip() and not text.endswith("."), sid  # verbatim CSF text has no trailing period


def test_every_checklist_reference_exists_in_the_csf_subset():
    csf = get_csf()
    for control in get_checklist().controls:
        for sid in control.csf_subcategories:
            assert csf.subcategory_text(sid) is not None, f"{control.id} cites unknown {sid}"


def test_csf_category_titles_match_the_phase_model():
    csf = get_csf()
    lifecycle = get_ir_lifecycle()
    for cid, category in csf.categories.items():
        if cid in lifecycle.csf_categories:
            assert lifecycle.csf_categories[cid] == category.title, cid


def test_checklist_covers_every_required_topic():
    topics = {c.topic for c in get_checklist().controls}
    required = {"roles", "escalation", "severity", "communication", "contacts", "evidence",
                "containment", "eradication", "recovery", "lessons_learned", "continuity"}
    assert required <= topics, required - topics


def test_checklist_covers_every_ir_phase():
    phases = {c.phase for c in get_checklist().controls}
    assert phases == set(get_ir_lifecycle().phase_ids)


def test_checklist_cites_only_verified_800_61r3_tables():
    allowed = {
        "SP 800-61r3 Section 3.1, Table 2 (Preparation and Lessons Learned)",
        "SP 800-61r3 Section 3.2, Table 3 (Incident Response)",
    }
    assert {c.sp800_61r3 for c in get_checklist().controls} <= allowed


def test_priority_weights_cover_all_priorities():
    checklist = get_checklist()
    assert all(checklist.weight(c) > 0 for c in checklist.controls)
