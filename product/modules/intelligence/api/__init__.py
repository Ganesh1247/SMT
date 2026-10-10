"""Public surface of the intelligence module.

feedback(kind, payload) -> FeedbackResult
evaluate_interview(transcript, solution_code, rubric_version) -> Evaluation
configure(provider=None)  # composition root; default reads env (stub when no key)
router                   # empty APIRouter (module has no HTTP surface)
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any

from fastapi import APIRouter

from ..application.ports import FeedbackProvider, ProviderRejected  # noqa: F401
from ..application.service import IntelligenceService, InvalidInput, UnsupportedFeedbackKind
from ..domain.rubric import CRITERIA, PASS_TOTAL, RUBRIC_VERSION  # noqa: F401
from ..infrastructure.factory import provider_from_env
from ..infrastructure.stub_provider import StubProvider  # noqa: F401

router = APIRouter()
_service: IntelligenceService | None = None


class _Dto:
    def to_dict(self) -> dict:
        return {k: v for k, v in self.__dict__.items()}

    def __getitem__(self, key: str) -> Any:
        return self.__dict__[key]

    def get(self, key: str, default: Any = None) -> Any:
        return self.__dict__.get(key, default)


@dataclass(frozen=True)
class Evaluation(_Dto):
    """criteria: [{criterion, score0to3, rationale, confidence, evidence_quotes}]"""
    criteria: list
    total: int
    passed: bool
    needs_human_review: bool
    model_ref: str
    ai_disclosure: bool
    status: str  # "evaluated" | "unavailable"
    rubric_version: str
    ai_judged: bool = True
    provider_label: str = ""
    events: list = field(default_factory=list)  # [{type:"injection_attempt", criterion, turn_index, pattern}]


@dataclass(frozen=True)
class FeedbackResult(_Dto):
    kind: str
    text: str
    confidence: float
    model_ref: str
    ai_disclosure: bool
    status: str
    ai_judged: bool = True
    provider_label: str = ""
    events: list = field(default_factory=list)


def configure(provider: FeedbackProvider | None = None) -> None:
    """Set the provider (None resets to env-selected default on next call)."""
    global _service
    _service = IntelligenceService(provider) if provider is not None else None


def _svc() -> IntelligenceService:
    global _service
    if _service is None:
        _service = IntelligenceService(provider_from_env(os.environ))
    return _service


def evaluate_interview(transcript: list[dict], solution_code: str, rubric_version: str) -> Evaluation:
    """Pre: transcript is a list of {role: interviewer|learner, criterion, text}; <=40 turns, <=4000 chars each.
    Post: five criteria scored 0-3; instruction-like learner text removed and reported in `events`.
    Errors: InvalidInput(code). A provider failure yields status="unavailable", needs_human_review=True."""
    return Evaluation(**_svc().evaluate_interview(transcript, solution_code, rubric_version))


def feedback(kind: str, payload: dict) -> FeedbackResult:
    """kinds: failing_tests {failed:[{id,message_safe}], passed_count, task_title}, debug_explanation {explanation}.
    Errors: UnsupportedFeedbackKind, InvalidInput."""
    return FeedbackResult(**_svc().feedback(kind, payload))


__all__ = [
    "router", "configure", "feedback", "evaluate_interview", "Evaluation", "FeedbackResult",
    "InvalidInput", "UnsupportedFeedbackKind", "CRITERIA", "RUBRIC_VERSION", "PASS_TOTAL", "StubProvider",
]
