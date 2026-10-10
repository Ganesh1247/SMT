"""Module wiring (lazy singleton)."""
from __future__ import annotations

import os
import threading
from datetime import datetime, timezone
from typing import Any, Callable, Optional

from assessment.application.service import AssessmentService
from assessment.infrastructure.adapters import (
    EvidenceLedgerAdapter,
    IntelligenceFeedbackAdapter,
    ModuleIntegrityAdapter,
    ModuleRunnerAdapter,
    ScoringGateAdapter,
)
from assessment.infrastructure.bank import JsonBank
from assessment.infrastructure.sqlite_repo import SqlAttemptRepository, default_database_url, make_engine

_lock = threading.Lock()
_state: dict = {}
_bank: Optional[JsonBank] = None


def bank() -> JsonBank:
    global _bank
    if _bank is None:
        _bank = JsonBank()
    return _bank


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class _UnconfiguredRunner:
    def register(self, *a, **k):
        raise RuntimeError("assessment: runner not configured")

    def run(self, *a, **k):
        from assessment.application.ports import RunOutcome
        return RunOutcome(status="runner_unavailable")


def configure(database_url: Optional[str] = None, data_dir: Optional[str] = None,
              clock: Optional[Callable[[], datetime]] = None, runner: Any = None, integrity: Any = None,
              intelligence: Any = None, proctoring_required: Optional[bool] = None) -> None:
    """Wire the module. `runner`, `integrity`, `intelligence` are the other modules' api objects (duck-typed)."""
    with _lock:
        engine = make_engine(database_url or default_database_url(data_dir))
        proctoring = proctoring_required if proctoring_required is not None else \
            os.environ.get("CRUCIBLE_PROCTORING_REQUIRED", "true").lower() != "false"
        _state.clear()
        _state.update(engine=engine, service=AssessmentService(
            bank=bank(), repo=SqlAttemptRepository(engine),
            runner=ModuleRunnerAdapter(runner) if runner is not None else _UnconfiguredRunner(),
            ledger=EvidenceLedgerAdapter(), scoring=ScoringGateAdapter(), clock=clock or _utc_now,
            integrity=ModuleIntegrityAdapter(integrity) if integrity is not None else None,
            feedback=IntelligenceFeedbackAdapter(intelligence) if intelligence is not None else None,
            proctoring_required=proctoring))


def reset() -> None:
    with _lock:
        eng = _state.get("engine")
        _state.clear()
        if eng is not None:
            eng.dispose()


def service() -> AssessmentService:
    if "service" not in _state:
        configure()
    return _state["service"]
