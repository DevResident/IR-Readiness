"""Tests for the Claude adapter, using a fake SDK client (no network, no API key)."""

from types import SimpleNamespace

import pytest
from pydantic import BaseModel, Field, ValidationError

from app.llm.base import LLMInvalidOutputError, LLMRefusalError
from app.llm.claude import FALLBACK_BETA, ClaudeStructuredLLM


class Out(BaseModel):
    answer: str = Field(max_length=5)


def response(stop_reason="end_turn", parsed=None):
    return SimpleNamespace(
        stop_reason=stop_reason, parsed_output=parsed, _request_id="req_test",
        usage=SimpleNamespace(input_tokens=10, output_tokens=20),
    )


def validation_error() -> ValidationError:
    try:
        Out(answer="too long")
    except ValidationError as exc:
        return exc


class FakeClient:
    def __init__(self, outcomes):
        self.outcomes = list(outcomes)
        self.calls = []
        self.beta = SimpleNamespace(messages=SimpleNamespace(parse=self._parse))

    def _parse(self, **kwargs):
        self.calls.append(kwargs)
        outcome = self.outcomes.pop(0)
        if isinstance(outcome, Exception):
            raise outcome
        return outcome


def llm(client):
    return ClaudeStructuredLLM(client, model="claude-opus-5-5", effort="medium")


def test_success_sends_expected_request():
    client = FakeClient([response(parsed=Out(answer="ok"))])
    assert llm(client).generate(system="sys", prompt="hi", schema=Out).answer == "ok"
    call = client.calls[0]
    assert call["model"] == "claude-opus-5-5"
    assert call["output_format"] is Out
    assert call["output_config"] == {"effort": "medium"}
    assert call["betas"] == [FALLBACK_BETA] and call["fallbacks"] == "default"


def test_validation_error_is_retried_with_feedback():
    client = FakeClient([validation_error(), response(parsed=Out(answer="ok"))])
    assert llm(client).generate(system="s", prompt="task", schema=Out).answer == "ok"
    retry_prompt = client.calls[1]["messages"][0]["content"]
    assert retry_prompt.startswith("task") and "answer" in retry_prompt


def test_gives_up_after_max_attempts():
    client = FakeClient([validation_error(), validation_error()])
    with pytest.raises(LLMInvalidOutputError):
        llm(client).generate(system="s", prompt="p", schema=Out)


def test_truncated_output_is_retried():
    client = FakeClient([response(stop_reason="max_tokens"), response(parsed=Out(answer="ok"))])
    assert llm(client).generate(system="s", prompt="p", schema=Out).answer == "ok"


def test_refusal_is_not_retried():
    client = FakeClient([response(stop_reason="refusal")])
    with pytest.raises(LLMRefusalError):
        llm(client).generate(system="s", prompt="p", schema=Out)
    assert len(client.calls) == 1
