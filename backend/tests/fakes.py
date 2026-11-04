"""Test doubles."""

from app.llm.base import LLMError


class FakeLLM:
    """Returns a canned draft (or raises) and records what it was asked."""

    def __init__(self, draft: dict | None = None, error: LLMError | None = None):
        self.draft = draft
        self.error = error
        self.calls: list[dict] = []

    def generate(self, *, system, prompt, schema):
        self.calls.append({"system": system, "prompt": prompt, "schema": schema})
        if self.error:
            raise self.error
        return schema.model_validate(self.draft)


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
            {"phase": "recover", "question": "How do we know backups are clean?", "csf_category": "RC.RP"},
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
