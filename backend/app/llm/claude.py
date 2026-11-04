"""Claude implementation of the StructuredLLM port.

Defensive layers, from the API outward:
1. Structured outputs (``output_format=<Pydantic model>``): the API constrains the
   response to the JSON schema, and the SDK validates it client-side, including
   constraints the API itself does not enforce (string lengths, list sizes).
2. Stop reasons are checked before reading content (refusal, max_tokens).
3. If validation still fails, we retry once and tell the model what was wrong.
4. Only typed ``LLMError`` subclasses leave this module.

Nothing from the prompt or the response is logged; only sizes and request IDs.
"""

from __future__ import annotations

import logging
from typing import Any

import anthropic
from pydantic import ValidationError

from app.llm.base import (
    LLMInvalidOutputError,
    LLMNotConfiguredError,
    LLMRefusalError,
    LLMUnavailableError,
    T,
)

logger = logging.getLogger(__name__)

# Server-side fallback: if a safety classifier declines the request (security
# content like ransomware can trip the "cyber" classifier), the API re-runs it on
# Anthropic's recommended fallback model inside the same call.
FALLBACK_BETA = "server-side-fallback-2026-07-01"
USER_AGENT = "ir-readiness-copilot/0.1.0"
# Models that support server-side fallbacks (Haiku does not).
FALLBACK_MODELS = {"claude-fable-5-1", "claude-opus-5-5", "claude-opus-5", "claude-sonnet-5-5"}


class ClaudeStructuredLLM:
    def __init__(
        self,
        client: Any,
        model: str,
        effort: str = "medium",
        max_tokens: int = 16000,
        max_attempts: int = 2,
        use_fallbacks: bool | None = None,
    ):
        self._client = client
        self._model = model
        # Fallbacks are a beta feature of api.anthropic.com; gateways may not support them.
        self._use_fallbacks = model in FALLBACK_MODELS if use_fallbacks is None else use_fallbacks
        self._target = str(getattr(client, "base_url", "unknown"))
        self._effort = effort
        self._max_tokens = max_tokens
        self._max_attempts = max_attempts

    @classmethod
    def from_settings(cls, settings) -> "ClaudeStructuredLLM":
        if settings.anthropic_api_key is None:
            raise LLMNotConfiguredError("ANTHROPIC_API_KEY is not set")
        client = anthropic.Anthropic(
            api_key=settings.anthropic_api_key.get_secret_value(),
            base_url=settings.anthropic_base_url or None,  # empty or None -> official Anthropic API
            # Identify the app honestly to the provider, plus any gateway-specific headers.
            default_headers={"User-Agent": USER_AGENT, **settings.anthropic_extra_headers},
            timeout=300.0,
        )
        use_fallbacks = False if settings.anthropic_base_url else None
        return cls(client, model=settings.anthropic_model, effort=settings.anthropic_effort,
                   use_fallbacks=use_fallbacks)

    def _call(self, system: str, messages: list[dict], schema: type[T]):
        common = dict(
            model=self._model,
            max_tokens=self._max_tokens,
            system=system,
            messages=messages,
            output_format=schema,
            output_config={"effort": self._effort},
        )
        if self._use_fallbacks:
            return self._client.beta.messages.parse(**common, betas=[FALLBACK_BETA], fallbacks="default")
        return self._client.messages.parse(**common)

    def generate(self, *, system: str, prompt: str, schema: type[T]) -> T:
        messages: list[dict] = [{"role": "user", "content": prompt}]
        last_error = "unknown error"

        for attempt in range(1, self._max_attempts + 1):
            try:
                response = self._call(system, messages, schema)
            except ValidationError as exc:
                # The SDK received JSON that violates client-side constraints.
                last_error = _summarize_validation_error(exc)
                logger.warning("LLM output failed validation (attempt %d): %s", attempt, last_error)
                messages = _with_correction(prompt, last_error)
                continue
            except anthropic.APIConnectionError as exc:
                logger.error("LLM connection failed target=%s error=%s: %s",
                             self._target, type(exc).__name__, exc.__cause__ or exc)
                raise LLMUnavailableError("The language model is temporarily unavailable") from exc
            except anthropic.AuthenticationError as exc:
                logger.error("LLM authentication failed target=%s status=401: %s", self._target, exc.message)
                raise LLMNotConfiguredError("The API key was rejected") from exc
            except anthropic.APIStatusError as exc:
                # The provider's error message is safe to log: it describes our request, not user data.
                logger.error("LLM request failed target=%s model=%s status=%s request_id=%s: %s",
                             self._target, self._model, exc.status_code, exc.request_id, exc.message)
                if exc.status_code == 402:
                    # Payment required: the account behind the API key has no credit (common on gateways).
                    raise LLMNotConfiguredError("The AI provider account has no available credit") from exc
                if isinstance(exc, anthropic.BadRequestError):
                    raise LLMUnavailableError("The language model rejected the request configuration") from exc
                raise LLMUnavailableError("The language model is temporarily unavailable") from exc

            logger.info(
                "LLM call ok request_id=%s stop_reason=%s input_tokens=%s output_tokens=%s",
                getattr(response, "_request_id", None),
                response.stop_reason,
                response.usage.input_tokens,
                response.usage.output_tokens,
            )

            if response.stop_reason == "refusal":
                raise LLMRefusalError("The model declined to generate this content")
            if response.stop_reason == "max_tokens":
                last_error = "the response was cut off because it was too long; be more concise"
                messages = _with_correction(prompt, last_error)
                continue
            if response.parsed_output is None:
                last_error = "no JSON output was returned"
                messages = _with_correction(prompt, last_error)
                continue
            return response.parsed_output

        raise LLMInvalidOutputError(f"Model output was invalid after {self._max_attempts} attempts: {last_error}")


def _summarize_validation_error(exc: ValidationError, limit: int = 8) -> str:
    parts = [f"{'.'.join(str(p) for p in e['loc'])}: {e['msg']}" for e in exc.errors()[:limit]]
    return "; ".join(parts)


def _with_correction(prompt: str, error: str) -> list[dict]:
    # A fresh single-turn request (no assistant prefill): the original task plus what to fix.
    return [{
        "role": "user",
        "content": f"{prompt}\n\nA previous attempt was rejected for this reason: {error}. "
                   "Produce a complete, corrected response.",
    }]
