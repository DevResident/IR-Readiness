import pytest

from app.catalogs.attack import get_catalog
from app.catalogs.ir_lifecycle import get_ir_lifecycle
from app.catalogs.scenarios import get_scenarios
from app.llm.base import LLMRefusalError
from app.modules.tabletop.schemas import TabletopRequest
from tests.fakes import FakeLLM, make_draft

REQUEST = TabletopRequest(industry="healthcare", org_size="medium", scenario="ransomware", audience="executive")


def service(llm):
    from app.modules.tabletop.service import TabletopService
    return TabletopService(llm, get_catalog(), get_ir_lifecycle(), get_scenarios())


def draft_with_injects(technique_lists):
    base = make_draft()["injects"][0]
    return make_draft(injects=[{**base, "sequence": i + 1, "technique_ids": ids} for i, ids in enumerate(technique_lists)])


def test_valid_techniques_get_names_from_catalog_not_from_llm():
    exercise = service(FakeLLM(draft_with_injects([["T1486"], ["T1490"], ["T1566.001"]]))).generate(REQUEST)
    first = exercise.injects[0].techniques[0]
    assert (first.id, first.name) == ("T1486", "Data Encrypted for Impact")
    assert first.url == "https://attack.mitre.org/techniques/T1486"
    assert exercise.validation.techniques_accepted == 3
    assert exercise.validation.rejected == []


def test_draft_missing_a_question_phase_is_invalid():
    from pydantic import ValidationError

    from app.modules.tabletop.schemas import TabletopDraft

    draft = make_draft()
    del draft["discussion_questions"]["recover"]
    with pytest.raises(ValidationError):
        TabletopDraft.model_validate(draft)


def test_invented_techniques_are_dropped_and_reported():
    exercise = service(FakeLLM(draft_with_injects([["T1486", "T1999"], ["T9999.999"], ["phishing"]]))).generate(REQUEST)
    assert [t.id for t in exercise.injects[0].techniques] == ["T1486"]
    assert exercise.injects[1].techniques == []
    assert {(r.location, r.value) for r in exercise.validation.rejected} == {
        ("inject 1", "T1999"), ("inject 2", "T9999.999"), ("inject 3", "phishing"),
    }


def test_revoked_technique_is_remapped_and_noted():
    exercise = service(FakeLLM(draft_with_injects([["T1562.001"], [], []]))).generate(REQUEST)
    assert exercise.injects[0].techniques[0].id == "T1685"
    assert exercise.validation.techniques_remapped == ["inject 1: T1562.001 was revoked by MITRE and replaced by T1685"]


def test_injects_are_sorted_and_renumbered():
    base = make_draft()["injects"][0]
    draft = make_draft(injects=[{**base, "sequence": 7, "title": "Late"}, {**base, "sequence": 2, "title": "Early"},
                                {**base, "sequence": 5, "title": "Middle"}])
    exercise = service(FakeLLM(draft)).generate(REQUEST)
    assert [(i.sequence, i.title) for i in exercise.injects] == [(1, "Early"), (2, "Middle"), (3, "Late")]


def test_unknown_csf_category_is_removed():
    questions = make_draft()["discussion_questions"]
    questions["detect"][0]["csf_category"] = "RS.XX"
    questions["detect"][1]["csf_category"] = "rs.co"  # normalized to upper case
    exercise = service(FakeLLM(make_draft(discussion_questions=questions))).generate(REQUEST)
    assert exercise.discussion_questions[0].csf_category is None
    assert exercise.discussion_questions[1].csf_category == "RS.CO"
    assert exercise.validation.rejected[0].value == "RS.XX"


def test_questions_are_flattened_in_phase_order():
    exercise = service(FakeLLM(make_draft())).generate(REQUEST)
    assert [q.phase for q in exercise.discussion_questions] == [
        "detect", "detect", "respond", "respond", "recover", "recover", "improve", "improve",
    ]


def test_missing_inject_phase_is_a_warning():
    exercise = service(FakeLLM(make_draft())).generate(REQUEST)  # all fake injects are "detect"
    assert exercise.validation.warnings == ["No injects for phase(s): respond, recover"]


def test_prompt_contains_scenario_context_and_audience():
    llm = FakeLLM(make_draft())
    service(llm).generate(REQUEST)
    prompt = llm.calls[0]["prompt"]
    assert "Ransomware with data extortion" in prompt
    assert "T1486 Data Encrypted for Impact" in prompt  # suggested technique, named from the catalog
    assert "executive leadership" in prompt
    assert "RS.MA: Incident Management" in prompt


def test_llm_errors_propagate():
    with pytest.raises(LLMRefusalError):
        service(FakeLLM(error=LLMRefusalError("no"))).generate(REQUEST)
