"""The LLM "port": the only thing business logic knows about language models.

Services depend on ``StructuredLLM``, not on the Anthropic SDK. Tests inject a fake
implementation, so they are deterministic, fast and free.
"""

from __future__ import annotations

from typing import Protocol, TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class LLMError(Exception):
    """Base class for every failure the API layer may need to translate."""


class LLMNotConfiguredError(LLMError):
    """No API key is configured."""


class LLMUnavailableError(LLMError):
    """Network problem, rate limit or provider outage (worth retrying later)."""


class LLMRefusalError(LLMError):
    """The model declined the request."""


class LLMInvalidOutputError(LLMError):
    """The model's output could not be parsed into the expected schema."""


class StructuredLLM(Protocol):
    def generate(self, *, system: str, prompt: str, schema: type[T]) -> T:
        """Return an instance of ``schema`` or raise an ``LLMError``."""
        ...
