"""Public contract of the evidence module (append-only hash-chained ledger)."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Optional

from evidence.api import runtime
from evidence.domain.events import EvidenceValidationError


@dataclass(frozen=True)
class LedgerEntry:
    sequence: int
    event_id: str
    event_type: str
    learner_id: str
    event: Mapping[str, Any]
    meta: Optional[Mapping[str, Any]]
    prev_hash: str
    hash: str
    recorded_at: str


@dataclass(frozen=True)
class VerifyResult:
    ok: bool
    entries_checked: int
    first_failure: Optional[int]
    message: str


def _dto(e) -> LedgerEntry:
    return LedgerEntry(e.sequence, e.event_id, e.event_type, e.learner_id, dict(e.event),
                       dict(e.meta) if e.meta is not None else None, e.prev_hash, e.hash, e.recorded_at)


def append(event_type: str, learner_id: str, payload: dict, idempotency_key: str) -> LedgerEntry:
    """Append an event. Idempotent on idempotency_key (returns the stored entry).

    Preconditions: payload satisfies EvidenceEvent 0.1 (see MODULE.md); `meta` (dict) is
    allowed and is bound to the hash through submission_ref.
    Raises EvidenceValidationError for anything else.
    """
    return _dto(runtime.service().append(event_type, learner_id, payload, idempotency_key))


def verify(learner_id: Optional[str] = None) -> VerifyResult:
    r = runtime.service().verify(learner_id)
    return VerifyResult(r.ok, r.entries_checked, r.first_failure, r.message)


def list_for_learner(learner_id: str) -> list[LedgerEntry]:
    return [_dto(e) for e in runtime.service().list_for_learner(learner_id)]


def head() -> dict:
    """Global ledger head: {"sequence": int, "hash": str}; sequence 0 / hash "genesis" when empty."""
    sequence, hash_ = runtime.service().head()
    return {"sequence": sequence, "hash": hash_}


configure = runtime.configure
reset = runtime.reset

from evidence.api.http import router  # noqa: E402  (after facade definitions)

__all__ = ["router", "append", "verify", "list_for_learner", "head", "configure", "reset",
           "LedgerEntry", "VerifyResult", "EvidenceValidationError"]
