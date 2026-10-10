"""Ports of the intelligence module."""
from __future__ import annotations

from typing import Protocol


class ProviderRejected(Exception):
    """The provider output could not be trusted (bad shape, bad JSON, transport error)."""


class FeedbackProvider(Protocol):
    #: pinned identifier recorded on every AI result
    model_ref: str
    #: human-readable label shown next to results, for example "offline-stub"
    label: str

    def feedback(self, kind: str, payload: dict) -> dict:
        """Return {"text": str, "confidence": float 0..1}. Raise ProviderRejected if unusable."""

    def evaluate(self, answers: dict[str, str], solution_code: str, rubric_version: str) -> list[dict]:
        """`answers` maps criterion -> learner text with instruction-like spans already removed.

        Return one dict per criterion: {criterion, score, rationale, confidence, evidence_quotes}.
        Raise ProviderRejected if unusable."""
