"""Module wiring (lazy singleton)."""
from __future__ import annotations

import threading
from datetime import datetime, timezone
from typing import Any, Callable, Optional

from scoring.application.service import ScoringService
from scoring.infrastructure.adapters import (
    LedgerEvidenceReader,
    SqlSnapshotStore,
    default_database_url,
    make_engine,
)

_lock = threading.Lock()
_state: dict = {}


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def configure(database_url: Optional[str] = None, data_dir: Optional[str] = None,
              evidence: Any = None, clock: Optional[Callable[[], datetime]] = None) -> None:
    with _lock:
        engine = make_engine(database_url or default_database_url(data_dir))
        _state.clear()
        _state.update(engine=engine, service=ScoringService(
            evidence or LedgerEvidenceReader(), SqlSnapshotStore(engine), clock or _utc_now))


def reset() -> None:
    with _lock:
        eng = _state.get("engine")
        _state.clear()
        if eng is not None:
            eng.dispose()


def service() -> ScoringService:
    if "service" not in _state:
        configure()
    return _state["service"]


def get_engine():
    service()
    return _state["engine"]
