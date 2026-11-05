"""Deterministic quote verification and scoring. No LLM involved."""

from __future__ import annotations

import re
import unicodedata

from app.modules.assessment.schemas import Status

_QUOTE_CHARS = str.maketrans({"‘": "'", "’": "'", "“": '"', "”": '"',
                              "–": "-", "—": "-", " ": " "})
_ELLIPSIS = re.compile(r"\s*(?:\.\.\.|…)\s*")
MIN_FRAGMENT_CHARS = 12  # a fragment shorter than this could match almost any document

CREDIT: dict[Status, float] = {"met": 1.0, "partial": 0.5, "missing": 0.0}
DOWNGRADE: dict[Status, Status] = {"met": "partial", "partial": "missing", "missing": "missing"}

SCORE_FORMULA = (
    "score = 100 × Σ(weight × credit) / Σ(weight), with weights critical=3, high=2, medium=1 "
    "and credit met=1, partial=0.5, missing=0; coverage = 100 × (met + partial) / controls"
)


def normalize(text: str) -> str:
    """Make matching robust to formatting the model cannot reproduce exactly:
    Unicode forms, curly quotes, dashes, case and whitespace (including PDF line breaks)."""
    text = unicodedata.normalize("NFKC", text).translate(_QUOTE_CHARS).lower()
    return " ".join(text.split())


def quote_in_document(quote: str, normalized_document: str) -> bool:
    """True if every '...'-separated fragment of the quote appears in the document, in order."""
    fragments = [normalize(f) for f in _ELLIPSIS.split(quote)]
    fragments = [f.strip(" \"'") for f in fragments if f.strip(" \"'")]
    if not fragments or any(len(f) < MIN_FRAGMENT_CHARS for f in fragments):
        return False
    position = 0
    for fragment in fragments:
        found = normalized_document.find(fragment, position)
        if found < 0:
            return False
        position = found + len(fragment)
    return True


def compute_score(statuses: list[tuple[Status, int]]) -> tuple[float, float]:
    """(score, coverage) from (status, weight) pairs, both 0-100 with one decimal."""
    if not statuses:
        return 0.0, 0.0
    total_weight = sum(w for _, w in statuses)
    earned = sum(CREDIT[s] * w for s, w in statuses)
    covered = sum(1 for s, _ in statuses if s != "missing")
    return round(100 * earned / total_weight, 1), round(100 * covered / len(statuses), 1)
