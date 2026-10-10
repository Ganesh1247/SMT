"""Detect instruction-like learner text. Learner text is data, never instructions.

Matched sentences are removed before scoring; each match is reported as an event.
The event carries the pattern name only, never the learner's text."""
from __future__ import annotations

import re

_PATTERNS: tuple[tuple[str, str], ...] = (
    ("ignore_instructions", r"ignore\s+(?:all\s+|any\s+|the\s+)?(?:previous|prior|above|earlier)\s+(?:instructions?|prompts?|rules?)"),
    ("disregard_instructions", r"disregard\s+(?:all\s+|any\s+|the\s+)?(?:previous|prior|above|instructions?|rules?)"),
    ("role_override", r"you\s+are\s+now\b"),
    ("system_prompt_reference", r"\b(?:system|developer)\s+(?:prompt|message|instructions?)\b"),
    ("score_demand", r"\b(?:give|award|assign|set)\s+(?:me\s+|this\s+|it\s+)?(?:a\s+)?(?:full|maximum|max|perfect|top)\b"),
    ("score_value_demand", r"\b(?:score|rate|mark)\s+(?:me\s+|this\s+|it\s+)?(?:a\s+|as\s+)?3\b"),
    ("approval_demand", r"\b(?:pass|approve)\s+(?:me|this\s+candidate|this\s+answer)\b"),
    ("reveal_request", r"\breveal\s+(?:your|the)\s+(?:prompt|instructions?|rubric|answer\s+key)\b"),
    ("delimiter_spoof", r"</?\s*(?:system|instructions?|untrusted[a-z_]*)\b[^>]*>"),
    ("jailbreak_term", r"\bjailbreak\b"),
)
_COMPILED = tuple(
    (name, re.compile(rf"{rx}[^.!?\n]*[.!?\n]?", re.IGNORECASE)) for name, rx in _PATTERNS
)


def strip_instructions(text: str) -> tuple[str, list[str]]:
    """Return (clean_text, matched_pattern_names)."""
    matched: list[str] = []
    clean = text
    for name, rx in _COMPILED:
        if rx.search(clean):
            matched.append(name)
            clean = rx.sub(" ", clean)
    return " ".join(clean.split()), matched
