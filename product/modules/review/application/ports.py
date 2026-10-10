"""Ports of the review module. Adapters over other modules' api/ are wired by the entrypoint.

All `learner_id` values crossing these ports are canonical `lrn_<16 hex>` references."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Mapping, Protocol


@dataclass(frozen=True)
class Principal:
    user_id: str
    role: str  # learner | reviewer | auditor | recruiter
    org_id: str | None = None  # recruiter organisation, `org_...`


class IdentityPort(Protocol):
    def authenticate(self, cookies: Mapping[str, str], headers: Mapping[str, str]) -> Principal | None: ...
    def alias_for(self, learner_id: str, recipient_id: str) -> str:
        """Per-recipient pseudonymous `cnd_<16 hex>` alias."""


class EvidencePort(Protocol):
    def append(self, event: dict) -> dict:
        """Append an EvidenceEvent (idempotent on idempotency_key). Return {event_id, sequence, hash}."""
    def list_for_learner(self, learner_id: str) -> list[dict]:
        """Events including `event_id` and `ledger{sequence,hash}`."""
    def head(self) -> dict:
        """{sequence, hash} of the ledger head (hash 'genesis' when empty)."""


class ScoringPort(Protocol):
    def competency_estimate(self, learner_id: str, competency_id: str) -> dict | None:
        """{estimate, lower, upper, as_of} or None when no gated estimate exists."""


class IntegrityPort(Protocol):
    def summary(self, attempt_id: str) -> dict | None: ...
    def recording_info(self, attempt_id: str, stream: str) -> dict | None:
        """{size, content_type} or None when no such recording."""
    def read_recording(self, attempt_id: str, stream: str, start: int, end: int) -> bytes:
        """Inclusive byte range."""


class AssessmentPort(Protocol):
    def record_level4_result(self, attempt_id: str, result: dict) -> None: ...


class Clock(Protocol):
    def now(self) -> datetime: ...


class Ids(Protocol):
    def new_id(self) -> str: ...


class DocStore(Protocol):
    def put(self, collection: str, key: str, doc: dict) -> None: ...
    def put_if_absent(self, collection: str, key: str, doc: dict) -> bool: ...
    def get(self, collection: str, key: str) -> dict | None: ...
    def all(self, collection: str) -> list[dict]: ...
