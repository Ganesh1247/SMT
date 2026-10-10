"""Public contract of the assessment module."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Optional

from assessment.api import runtime
from assessment.application.service import CONSENT_VERSION, REQUIRED_SCOPES

RUN_LIMIT = runtime.bank().rules.run_limit


@dataclass(frozen=True)
class AttemptDTO:
    attempt_id: str
    learner_id: str
    level: int
    track: str
    status: str
    attempt_no: int
    seed_id: str
    consent_recorded: bool


def get_attempt(attempt_id: str, learner_id: str) -> Optional[AttemptDTO]:
    """The attempt if it belongs to learner_id, else None (unknown and foreign ids look identical)."""
    att = runtime.service().attempt_for(attempt_id, learner_id)
    if att is None:
        return None
    return AttemptDTO(att.id, att.learner_id, att.level, att.track, att.status, att.attempt_no,
                      "sd_" + att.seed, att.consent is not None)


def l3_solution(learner_id: str) -> Optional[dict]:
    """The learner's passed Level 3 solution {task_id, code, ...} or None. Used to build Level 4 prompts."""
    return runtime.service().l3_solution(learner_id)


def record_level4_result(attempt_id: str, evaluation: Mapping[str, Any]) -> None:
    """Apply the Level 4 qualify rule to an interview evaluation and record evidence.

    evaluation: {criteria: [{criterion, score0to3|score, rationale, confidence}] x5, model_ref,
    needs_human_review?}. Raises NotFound/Conflict/InvalidInput (typed, stable codes)."""
    runtime.service().record_level4_result(attempt_id, evaluation)


def record_review_outcome(attempt_id: str, outcome: str) -> None:
    """Final verdict of a human review of an awaiting_review Level 4 attempt ('pass' | 'fail')."""
    runtime.service().record_review_outcome(attempt_id, outcome)


def register_tasks() -> int:
    """Register all hidden-test tasks with the runner; returns how many were registered."""
    return runtime.service().register_tasks()


configure = runtime.configure
reset = runtime.reset

from assessment.api.http import router  # noqa: E402
from assessment.domain.rules import AssessmentError, Conflict, InvalidInput, NotFound  # noqa: E402

__all__ = ["router", "get_attempt", "l3_solution", "record_level4_result", "record_review_outcome",
           "register_tasks", "configure", "reset", "AttemptDTO", "CONSENT_VERSION", "REQUIRED_SCOPES",
           "RUN_LIMIT", "AssessmentError", "Conflict", "InvalidInput", "NotFound"]
