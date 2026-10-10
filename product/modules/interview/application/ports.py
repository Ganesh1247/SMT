"""Ports of the interview module (adapters over other modules' api/ are wired by the entrypoint)."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Mapping, Protocol


@dataclass(frozen=True)
class Principal:
    user_id: str
    role: str


class IdentityPort(Protocol):
    def authenticate(self, cookies: Mapping[str, str], headers: Mapping[str, str]) -> Principal | None: ...


class AssessmentPort(Protocol):
    def l3_solution(self, attempt_id: str, learner_id: str) -> dict | None:
        """The learner's own L3 submission for the L4 attempt, or None when unknown or not theirs.
        Keys: code, competency_id, task_id, task_version, seed_id."""
    def record_level4_result(self, attempt_id: str, result: dict) -> None:
        """result: {status: final|pending_review, passed: bool|None, total, criteria, rubric_version,
        model_ref, ai_disclosure, case_id?}"""


class IntelligencePort(Protocol):
    def evaluate_interview(self, transcript: list[dict], solution_code: str, rubric_version: str) -> dict: ...


class EvidencePort(Protocol):
    def append(self, event: dict) -> dict: ...


class ReviewPort(Protocol):
    def enqueue_case(self, *, attempt_id: str, learner_id: str, reason: str, uncertainty: float,
                     integrity_risk: str, summary: dict, context: dict) -> str: ...


class IntegrityPort(Protocol):
    def summary(self, attempt_id: str) -> dict | None:
        """Reviewer-only summary; only the `risk` label (low|medium|high) is used here."""


class Clock(Protocol):
    def now(self) -> datetime: ...


class DocStore(Protocol):
    def put(self, collection: str, key: str, doc: dict) -> None: ...
    def put_if_absent(self, collection: str, key: str, doc: dict) -> bool: ...
    def get(self, collection: str, key: str) -> dict | None: ...
    def all(self, collection: str) -> list[dict]: ...
