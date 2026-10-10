"""Ports the assessment use cases depend on. Adapters live in infrastructure or the composition root."""
from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Any, Mapping, Optional, Protocol, Sequence


@dataclass(frozen=True)
class Attempt:
    id: str
    learner_id: str
    track: str
    level: int
    attempt_no: int
    seed: str  # 12 hex chars; used as the evidence seed id (sd_<seed>)
    status: str  # created | ready | in_progress | passed | failed | awaiting_review
    plan: tuple = ()
    consent: Optional[Mapping[str, Any]] = None
    result: Optional[Mapping[str, Any]] = None
    created_at: str = ""
    started_at: Optional[str] = None
    finished_at: Optional[str] = None

    def with_(self, **changes) -> "Attempt":
        return replace(self, **changes)


@dataclass(frozen=True)
class RunOutcome:
    status: str  # passed | failed_tests | error | blocked | timeout | runner_unavailable
    tests: tuple = ()  # ({"id", "passed", "message_safe"},...)
    stdout_trunc: str = ""
    isolation_mode: str = "unknown"


class AttemptRepository(Protocol):
    def add(self, attempt: Attempt) -> None: ...
    def get(self, attempt_id: str) -> Optional[Attempt]: ...
    def update(self, attempt: Attempt) -> None: ...
    def for_learner(self, learner_id: str, track: Optional[str] = None, level: Optional[int] = None) -> list[Attempt]: ...
    def upsert_answer(self, attempt_id: str, item_ref: str, answer: Any, explanation: Optional[str],
                      graded: Mapping[str, Any], at: str) -> None: ...
    def answers(self, attempt_id: str) -> dict[str, dict]: ...
    def count_runs(self, attempt_id: str, item_ref: str) -> int: ...
    def add_run(self, attempt_id: str, item_ref: str, at: str) -> None: ...


class RunnerPort(Protocol):
    def register(self, task_id: str, kind: str, spec: Mapping[str, Any]) -> None: ...
    def run(self, kind: str, task_id: str, dataset_id: str, profile: str, submission: str) -> RunOutcome: ...


class IntegrityPort(Protocol):
    def record_consent(self, attempt_id: str, learner_id: str, version: str, scopes: Sequence[str]) -> None: ...
    def ingest_events(self, attempt_id: str, learner_id: str, events: Sequence[Mapping[str, Any]]) -> None: ...
    def store_chunk(self, attempt_id: str, learner_id: str, stream: str, seq: int, data: bytes) -> Any: ...
    def finalize_recording(self, attempt_id: str, learner_id: str) -> Mapping[str, Any]: ...
    def fingerprint_submit(self, attempt_id: str, task_id: str, answer_values_hash: str) -> Any: ...


class LedgerPort(Protocol):
    def append(self, event_type: str, learner_id: str, payload: dict, idempotency_key: str) -> Any: ...


class ScoringPort(Protocol):
    def apply_gated_update(self, learner_id: str, competency: str) -> bool:
        """True when a new estimate was published; False when the gate withheld it."""


class FeedbackPort(Protocol):
    def explain_failures(self, task_title: str, failed: Sequence[Mapping[str, Any]], passed_count: int) -> Optional[str]: ...
    def explanation_feedback(self, explanation: str) -> Optional[Mapping[str, Any]]: ...


class BankPort(Protocol):
    rules: Any

    def items(self, track: str, level: int) -> list[dict]: ...
    def meta(self, track: str, level: int) -> Mapping[str, Any]: ...


class NullIntegrity:
    """Used when the integrity module is not wired; consent is still recorded in the attempt."""

    def record_consent(self, *a, **k): return None
    def ingest_events(self, *a, **k): return None
    def store_chunk(self, *a, **k): return {}
    def finalize_recording(self, *a, **k): return {"manifest_hash": None, "chunks": 0}
    def fingerprint_submit(self, *a, **k): return []


class NullFeedback:
    def explain_failures(self, *a, **k): return None
    def explanation_feedback(self, *a, **k): return None


__all__ = ["Attempt", "RunOutcome", "AttemptRepository", "RunnerPort", "IntegrityPort", "LedgerPort",
           "ScoringPort", "FeedbackPort", "BankPort", "NullIntegrity", "NullFeedback", "field"]
