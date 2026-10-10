"""Deterministic, offline provider. Keyword and length rules; clearly labelled as a stub."""
from __future__ import annotations

import re

from ..domain.rubric import CRITERIA

_CUES = {
    "explain": ("loop", "iterate", "return", "function", "dictionary", "list", "set", "sort", "compare", "first", "then", "count", "store", "join", "group"),
    "justify_approach": ("because", "so that", "instead", "trade", "alternative", "simpler", "faster", "readable", "since", "rather"),
    "complexity": ("o(n", "o(1", "o(log", "linear", "quadratic", "constant", "logarithmic", "time", "space", "memory"),
    "edge_cases": ("empty", "none", "null", "zero", "negative", "duplicate", "single", "large", "invalid", "missing", "boundary", "tie"),
    "adapt": ("instead", "change", "modify", "would", "replace", "additionally", "also", "adapt", "stream", "one pass", "generator", "constraint"),
}
_SENT = re.compile(r"[^.!?\n]+[.!?]?")


class StubProvider:
    model_ref = "stub-deterministic-v1"
    label = "offline-stub"

    def evaluate(self, answers: dict[str, str], solution_code: str, rubric_version: str) -> list[dict]:
        out = []
        for c in CRITERIA:
            text = answers.get(c, "")
            if not text:
                continue
            words = len(text.split())
            low = text.lower()
            hits = [cue for cue in _CUES[c] if cue in low]
            h = len(hits)
            if words < 3:
                score = 0
            else:
                score = 1 + (1 if h >= 1 else 0) + (1 if h >= 3 and words >= 20 else 0)
            confidence = 0.4 if words < 8 else min(0.85, 0.55 + 0.1 * min(h, 3) + (0.1 if words >= 20 else 0.0))
            quotes = [s.strip() for s in _SENT.findall(text) if any(k in s.lower() for k in hits)][:2]
            out.append({
                "criterion": c,
                "score": score,
                "rationale": f"Offline rule-based stub: {h} cue(s) matched in {words} words. Not a human or model judgement.",
                "confidence": round(confidence, 2),
                "evidence_quotes": [q[:160] for q in quotes],
            })
        return out

    def feedback(self, kind: str, payload: dict) -> dict:
        if kind == "failing_tests":
            failed = payload.get("failed", [])
            if not failed:
                return {"text": "All visible checks passed. Review edge cases once more.", "confidence": 0.9}
            parts = [f"{f['id']}: {f['message_safe'] or 'output differed from the expectation'}" for f in failed]
            return {
                "text": f"{len(failed)} check(s) did not pass ({payload.get('passed_count', 0)} passed). "
                        + "; ".join(parts) + ". Re-trace your code on a small input.",
                "confidence": 0.7,
            }
        text = payload.get("explanation", "")
        words = len(text.split())
        if words < 8:
            return {"text": "Your explanation is brief. Say what the code did, why it was wrong, and how your change fixes it.", "confidence": 0.5}
        return {"text": "Explanation received. It addresses the behaviour; make sure it names the cause and the fix explicitly.", "confidence": 0.6}

    def __repr__(self) -> str:
        return "StubProvider()"
