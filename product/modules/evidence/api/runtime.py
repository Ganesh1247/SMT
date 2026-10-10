"""Module wiring (lazy singleton). Composition detail; not part of the public surface."""
from __future__ import annotations

import threading
from datetime import datetime, timezone
from typing import Callable, Optional

from evidence.application.ledger import LedgerService
from evidence.infrastructure.sqlite_store import SqlLedgerStore, default_database_url, make_engine

_lock = threading.Lock()
_state: dict = {}


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def configure(database_url: Optional[str] = None, data_dir: Optional[str] = None,
              clock: Optional[Callable[[], datetime]] = None) -> None:
    with _lock:
        engine = make_engine(database_url or default_database_url(data_dir))
        _state.clear()
        _state.update(engine=engine, service=LedgerService(SqlLedgerStore(engine), clock or _utc_now))


def reset() -> None:
    with _lock:
        eng = _state.get("engine")
        _state.clear()
        if eng is not None:
            eng.dispose()


def service() -> LedgerService:
    if "service" not in _state:
        configure()
    return _state["service"]


def get_engine():
    service()
    return _state["engine"]
