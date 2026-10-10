"""Module wiring (lazy singleton). Composition detail; not part of the public surface."""
from __future__ import annotations

import os
import threading
from datetime import datetime, timezone
from typing import Callable, Optional

from identity.application.service import IdentityService
from identity.infrastructure.adapters import (
    ScryptHasher,
    SqlSessionRepository,
    SqlUserRepository,
    default_database_url,
    make_engine,
)

COOKIE_NAME = "crucible_session"

_lock = threading.Lock()
_state: dict = {}


def _utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)


def configure(
    database_url: Optional[str] = None,
    data_dir: Optional[str] = None,
    clock: Optional[Callable[[], datetime]] = None,
    session_ttl_seconds: Optional[int] = None,
    cookie_secure: Optional[bool] = None,
) -> None:
    with _lock:
        url = database_url or default_database_url(data_dir)
        engine = make_engine(url)
        ttl = session_ttl_seconds or int(os.environ.get("SESSION_TTL_SECONDS", "28800"))
        secure = cookie_secure if cookie_secure is not None else os.environ.get(
            "CRUCIBLE_COOKIE_SECURE", "false").lower() == "true"
        _state.clear()
        _state.update(
            engine=engine,
            cookie_secure=secure,
            service=IdentityService(SqlUserRepository(engine), SqlSessionRepository(engine),
                                    ScryptHasher(), clock or _utc_now, ttl),
        )


def reset() -> None:
    with _lock:
        eng = _state.get("engine")
        _state.clear()
        if eng is not None:
            eng.dispose()


def service() -> IdentityService:
    if "service" not in _state:
        configure()
    return _state["service"]


def get_engine():
    service()
    return _state["engine"]


def cookie_secure() -> bool:
    service()
    return _state["cookie_secure"]
