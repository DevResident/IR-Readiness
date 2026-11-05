"""Map typed LLM errors to HTTP responses with generic, client-safe messages."""

from collections.abc import Iterator
from contextlib import contextmanager

from fastapi import HTTPException

from app.llm.base import (
    LLMInvalidOutputError,
    LLMNotConfiguredError,
    LLMRefusalError,
    LLMUnavailableError,
)


@contextmanager
def llm_errors_as_http(what: str) -> Iterator[None]:
    """``what`` names the artifact in messages, e.g. "exercise" or "assessment"."""
    try:
        yield
    except LLMNotConfiguredError as exc:
        raise HTTPException(status_code=503, detail="The AI model is not configured on the server") from exc
    except LLMUnavailableError as exc:
        raise HTTPException(status_code=503, detail="The AI model is temporarily unavailable, try again") from exc
    except LLMRefusalError as exc:
        raise HTTPException(status_code=422, detail=f"The AI model declined to generate this {what}") from exc
    except LLMInvalidOutputError as exc:
        raise HTTPException(status_code=502, detail=f"The AI model returned an invalid {what}, try again") from exc
