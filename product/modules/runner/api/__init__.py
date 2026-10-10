"""Public surface of the runner module. Other modules import only from here.

    run_python(run_id, task_id, dataset_id, limits_profile, submission) -> RunResult
    run_sql(run_id, task_id, dataset_id, limits_profile, submission)    -> RunResult
    register_task(task_id, kind, spec_json)                             -> None

Run failures are returned as RunResult statuses, never raised. `register_task` raises
`InvalidTaskSpec` (a ValueError) for a malformed spec.
"""
from __future__ import annotations

import threading
from typing import Any

from ..application.run_service import RunService
from ..domain.models import InvalidTaskSpec, RunResult, TestOutcome

__all__ = ["run_python", "run_sql", "register_task", "RunResult", "TestOutcome", "InvalidTaskSpec",
           "isolation_status"]

_lock = threading.Lock()
_service: RunService | None = None
_store = None
_selector = None


def _get() -> RunService:
    global _service, _store, _selector
    with _lock:
        if _service is None:
            from ..infrastructure.stores import ConfiguredSelector, SqliteExpected, SqliteStore
            _store = SqliteStore()
            _selector = ConfiguredSelector()
            _service = RunService(_store, _selector, SqliteExpected(), _store)
        return _service


def _reset_for_tests(service: RunService | None = None) -> None:
    """Test hook: drop the singleton (re-read DATA_DIR and env) or inject a prepared service."""
    global _service, _store, _selector
    with _lock:
        _service, _store, _selector = service, None, None


def run_python(run_id: Any, task_id: Any, dataset_id: Any, limits_profile: Any, submission: Any) -> RunResult:
    return _get().run("python", run_id, task_id, dataset_id, limits_profile, submission)


def run_sql(run_id: Any, task_id: Any, dataset_id: Any, limits_profile: Any, submission: Any) -> RunResult:
    return _get().run("sql", run_id, task_id, dataset_id, limits_profile, submission)


def register_task(task_id: Any, kind: Any, spec_json: Any) -> None:
    _get().register_task(task_id, kind, spec_json)


def isolation_status() -> str:
    """`container`, `process-fallback` or `unavailable` for the health endpoint / reviewer banner."""
    _get()
    executor = _selector.select() if _selector else None
    return executor.isolation_mode if executor else "unavailable"
