"""Public surface of the review module.

router                         FastAPI APIRouter (mount under /api)
configure(identity, evidence, scoring, integrity, assessment, clock=None, ids=None, store=None, data_dir=None)
enqueue_case(attempt_id, learner_id, reason, uncertainty, integrity_risk, summary, context) -> case_id
query_shared_evidence(request, caller_recipient_id) -> SharedEvidenceQueryResponse dict (contract v0.1)
Port protocols: see application/ports.py (re-exported below)
"""
from __future__ import annotations

from ..application.ports import (AssessmentPort, EvidencePort, IdentityPort, IntegrityPort, Principal,  # noqa: F401
                                 ScoringPort)
from ..application.service import QueryError, ReviewError  # noqa: F401
from ..domain.rules import REASONS  # noqa: F401
from ._context import configure as _configure, ctx
from .routes import router

__all__ = ["router", "configure", "enqueue_case", "query_shared_evidence", "QueryError", "ReviewError",
           "Principal", "IdentityPort", "EvidencePort", "ScoringPort", "IntegrityPort", "AssessmentPort", "REASONS"]


def configure(identity, evidence, scoring, integrity, assessment, clock=None, ids=None, store=None,
              data_dir=None, contracts=None) -> None:
    _configure(identity, evidence, scoring, integrity, assessment, clock=clock, ids=ids, store=store,
               data_dir=data_dir, contracts=contracts)


def _service():
    if ctx.service is None:
        raise ReviewError("not_configured")
    return ctx.service


def enqueue_case(attempt_id: str, learner_id: str, reason: str, uncertainty: float, integrity_risk: str,
                 summary: dict, context: dict) -> str:
    """Pre: reason in REASONS; uncertainty 0..1; integrity_risk low|medium|high; context carries the
    evidence-event provenance fields (competency_id, level, task_id, task_version, rubric_id, rubric_version,
    seed_id) plus kind and original_outcome. Post: idempotent per (attempt_id, reason); returns case_id."""
    return _service().enqueue_case(attempt_id, learner_id, reason, uncertainty, integrity_risk, summary, context)


def query_shared_evidence(request: dict, caller_recipient_id: str) -> dict:
    """Pre: request validates against shared-evidence-query-request.schema.json and recipient_id equals
    caller_recipient_id. Post: only evidence covered by an active ShareGrant; no totals or omitted counts.
    Errors: QueryError(invalid_request | recipient_mismatch | invalid_cursor)."""
    return _service().query_shared_evidence(request, caller_recipient_id)
