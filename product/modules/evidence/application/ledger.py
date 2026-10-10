"""Ledger use cases: append (idempotent, chained) and verify."""
from __future__ import annotations

import threading
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Callable, Mapping, Optional, Protocol

from evidence.domain import canonical
from evidence.domain.events import build_event, meta_digest


@dataclass(frozen=True)
class StoredEntry:
    sequence: int
    event_id: str
    event_type: str
    learner_id: str
    event: Mapping[str, Any]
    meta: Optional[Mapping[str, Any]]
    prev_hash: str
    hash: str
    recorded_at: str
    meta_bound: bool = False


@dataclass(frozen=True)
class Verification:
    ok: bool
    entries_checked: int
    first_failure: Optional[int]
    message: str


class LedgerStore(Protocol):
    def by_key(self, key: str) -> Optional[StoredEntry]: ...
    def last(self) -> Optional[StoredEntry]: ...
    def insert(self, entry: StoredEntry, key: str) -> None: ...
    def all(self) -> list[StoredEntry]: ...
    def for_learner(self, learner_id: str) -> list[StoredEntry]: ...


class LedgerService:
    def __init__(self, store: LedgerStore, clock: Callable[[], datetime]) -> None:
        self._store = store
        self._clock = clock
        self._lock = threading.Lock()

    def append(self, event_type: str, learner_id: str, payload: Mapping[str, Any],
               idempotency_key: str) -> StoredEntry:
        now = self._clock().astimezone(timezone.utc)
        event, meta = build_event(event_type, learner_id, payload, idempotency_key, now)
        with self._lock:
            existing = self._store.by_key(idempotency_key)
            if existing is not None:
                return existing
            last = self._store.last()
            sequence = (last.sequence + 1) if last else 1
            prev = last.hash if last else canonical.GENESIS
            digest = canonical.event_hash(event, sequence, prev)
            bound = meta is not None and "submission_ref" not in payload
            entry = StoredEntry(
                sequence=sequence, event_id=str(uuid.uuid4()), event_type=event_type,
                learner_id=learner_id, event=event, meta=meta, prev_hash=prev, hash=digest,
                recorded_at=now.replace(microsecond=0).strftime("%Y-%m-%dT%H:%M:%SZ"),
                meta_bound=bound,
            )
            self._store.insert(entry, idempotency_key)
            return entry

    def list_for_learner(self, learner_id: str) -> list[StoredEntry]:
        return self._store.for_learner(learner_id)

    def head(self) -> tuple[int, str]:
        """Global ledger head as (sequence, hash); (0, "genesis") when the ledger is empty."""
        last = self._store.last()
        return (last.sequence, last.hash) if last else (0, canonical.GENESIS)

    def verify(self, learner_id: Optional[str] = None) -> Verification:
        """Verify the chain. With learner_id, only that learner's entries are judged.

        Each entry is checked locally: hash recomputed from its own content, its
        sequence and prev_hash linked to the previous global entry.
        """
        entries = self._store.all()
        prev_hash, prev_seq = canonical.GENESIS, 0
        checked = 0
        for entry in entries:
            in_scope = learner_id is None or entry.learner_id == learner_id
            problem = None
            if entry.sequence != prev_seq + 1:
                problem = "sequence gap: an earlier entry is missing"
            elif entry.prev_hash != prev_hash:
                problem = "prev_hash does not match the previous entry"
            else:
                try:
                    expected = canonical.event_hash(entry.event, entry.sequence, entry.prev_hash)
                except canonical.CanonicalisationError as exc:
                    expected, problem = None, f"cannot canonicalise: {exc}"
                if problem is None and expected != entry.hash:
                    problem = "hash mismatch: the event was altered after it was recorded"
                if (problem is None and entry.meta_bound
                        and entry.event.get("submission_ref") != meta_digest(entry.meta or {})):
                    problem = "meta does not match its recorded digest"
            if in_scope:
                checked += 1
                if problem:
                    return Verification(False, checked, entry.sequence,
                                        f"entry {entry.sequence}: {problem}")
            prev_hash, prev_seq = entry.hash, entry.sequence
        return Verification(True, checked, None, f"{checked} entries verified")
