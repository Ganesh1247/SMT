"""Public surface of the integrity module. Other modules import only from here.

Facades (A1/A2 call these):
    record_consent(attempt_id, learner_id, version, scopes)             -> ConsentRecord
    ingest_events(attempt_id, learner_id, events)                       -> None
    store_chunk(attempt_id, learner_id, stream, seq, data)              -> ChunkReceipt
    finalize_recording(attempt_id, learner_id)                          -> {"manifest_hash", "chunks"}
    summary(attempt_id)                                                 -> IntegritySummary  (reviewer-only)
    fingerprint_submit(attempt_id, task_id, answer_values_hash, dataset_id=None) -> list[Flag]
Reviewer helpers (the caller authorises the reviewer role):
    playback_range(attempt_id, stream, range_header)                    -> PlaybackSlice
    verify_recording(attempt_id)                                        -> bool
Other:
    latest_precheck_passed(learner_id) -> bool, purge_expired(now=None) -> int
    router: FastAPI APIRouter (mount under /api); wire auth with
            app.dependency_overrides[integrity.api.current_user_dependency] = identity.api.current_user

Errors are typed: InvalidInput, NotFound (unknown and foreign are identical), TooLarge, Conflict.
Nothing here ever changes a score or result.
"""
from __future__ import annotations

import threading
from typing import Any

from ..application.service import (ChunkReceipt, Flag, IntegrityConfig, IntegrityService, IntegritySummary,
                                   PlaybackSlice)
from ..domain.models import (EVENT_TYPES, STREAMS, ConsentRecord, Conflict, IntegrityError, InvalidInput,
                             NotFound, TooLarge)

_lock = threading.Lock()
_service: IntegrityService | None = None


def get_service() -> IntegrityService:
    global _service
    with _lock:
        if _service is None:
            from ..infrastructure.config import data_dir, load_config
            from ..infrastructure.fs_recordings import FsRecordings
            from ..infrastructure.sqlite_repo import SqliteRepo
            base = data_dir()
            _service = IntegrityService(SqliteRepo(base / "integrity" / "integrity.db"),
                                        FsRecordings(base / "recordings"), load_config())
        return _service


def _reset_for_tests(service: IntegrityService | None = None) -> None:
    global _service
    with _lock:
        _service = service


def record_consent(attempt_id: str, learner_id: str, version: str, scopes: list[str]) -> ConsentRecord:
    return get_service().record_consent(attempt_id, learner_id, version, scopes)


def ingest_events(attempt_id: str, learner_id: str, events: list[Any]) -> None:
    get_service().ingest_events(attempt_id, learner_id, events)


def store_chunk(attempt_id: str, learner_id: str, stream: str, seq: int, data: bytes) -> ChunkReceipt:
    return get_service().store_chunk(attempt_id, learner_id, stream, seq, data)


def finalize_recording(attempt_id: str, learner_id: str) -> dict:
    return get_service().finalize_recording(attempt_id, learner_id)


def summary(attempt_id: str) -> IntegritySummary:
    return get_service().summary(attempt_id)


def fingerprint_submit(attempt_id: str, task_id: str, answer_values_hash: str,
                       dataset_id: str | None = None) -> list[Flag]:
    return get_service().fingerprint_submit(attempt_id, task_id, answer_values_hash, dataset_id)


def playback_range(attempt_id: str, stream: str, range_header: str | None) -> PlaybackSlice:
    return get_service().playback_range(attempt_id, stream, range_header)


def verify_recording(attempt_id: str) -> bool:
    return get_service().verify_recording(attempt_id)


def latest_precheck_passed(learner_id: str) -> bool:
    return get_service().latest_precheck_passed(learner_id)


def purge_expired(now: float | None = None) -> int:
    return get_service().purge_expired(now)


from .http import current_user_dependency, router  # noqa: E402  (after facades; http uses get_service)

__all__ = [
    "record_consent", "ingest_events", "store_chunk", "finalize_recording", "summary", "fingerprint_submit",
    "playback_range", "verify_recording", "latest_precheck_passed", "purge_expired", "router",
    "current_user_dependency", "ConsentRecord", "ChunkReceipt", "Flag", "IntegritySummary", "PlaybackSlice",
    "IntegrityConfig", "IntegrityError", "InvalidInput", "NotFound", "TooLarge", "Conflict", "EVENT_TYPES", "STREAMS",
]
