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
        self.beta = SimpleNamespace(messages=SimpleNamespace(parse=lambda **kw: self._parse("beta", **kw)))
        self.messages = SimpleNamespace(parse=lambda **kw: self._parse("ga", **kw))

    def _parse(self, endpoint, **kwargs):
        self.calls.append({"endpoint": endpoint, **kwargs})
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
    assert call["endpoint"] == "beta"
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


def test_haiku_does_not_send_fallbacks():
    client = FakeClient([response(parsed=Out(answer="ok"))])
    ClaudeStructuredLLM(client, model="claude-haiku-5-5").generate(system="s", prompt="p", schema=Out)
    call = client.calls[0]
    assert call["endpoint"] == "ga" and "fallbacks" not in call and "betas" not in call


def test_gateway_base_url_disables_fallbacks():
    from pydantic import SecretStr

    from app.core.config import Settings

    settings = Settings(anthropic_api_key=SecretStr("k"), anthropic_model="claude-opus-5-5",
                        anthropic_base_url="https://gateway.example/anthropic", _env_file=None)
    llm = ClaudeStructuredLLM.from_settings(settings)
    assert llm._use_fallbacks is False
    assert str(llm._client.base_url).startswith("https://gateway.example/anthropic")


def test_empty_base_url_uses_official_api():
    from pydantic import SecretStr

    from app.core.config import Settings

    settings = Settings(anthropic_api_key=SecretStr("k"), anthropic_base_url="", _env_file=None)
    llm = ClaudeStructuredLLM.from_settings(settings)
    assert "api.anthropic.com" in str(llm._client.base_url)
    assert llm._use_fallbacks is True


def _status_error(cls, status):
    import httpx2

    req = httpx2.Request("POST", "https://gateway.example/v1/messages")
    resp = httpx2.Response(status, request=req, json={"error": {"message": "model not found"}})
    return cls("model not found", response=resp, body=None)


def test_status_errors_are_logged_with_status_and_message(caplog):
    import anthropic

    from app.llm.base import LLMUnavailableError

    client = FakeClient([_status_error(anthropic.NotFoundError, 404)])
    with caplog.at_level("ERROR"), pytest.raises(LLMUnavailableError):
        llm(client).generate(system="s", prompt="p", schema=Out)
    assert "status=404" in caplog.text and "model not found" in caplog.text


def test_connection_errors_are_logged(caplog):
    import anthropic
    import httpx2

    from app.llm.base import LLMUnavailableError

    exc = anthropic.APIConnectionError(request=httpx2.Request("POST", "https://gateway.example"))
    client = FakeClient([exc])
    with caplog.at_level("ERROR"), pytest.raises(LLMUnavailableError):
        llm(client).generate(system="s", prompt="p", schema=Out)
    assert "LLM connection failed" in caplog.text


def test_payment_required_is_a_configuration_error(caplog):
    import anthropic

    from app.llm.base import LLMNotConfiguredError

    client = FakeClient([_status_error(anthropic.APIStatusError, 402)])
    with caplog.at_level("ERROR"), pytest.raises(LLMNotConfiguredError):
        llm(client).generate(system="s", prompt="p", schema=Out)
    assert "status=402" in caplog.text
