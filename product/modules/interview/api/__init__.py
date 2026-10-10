"""Public surface of the interview module.

router     POST /interview/{attempt_id}/turn {answer_text?} ; GET /interview/{attempt_id}
configure(identity, assessment, evidence, intelligence=None, review=None, integrity=None, clock=None,
          store=None, data_dir=None)
Defaults: intelligence -> intelligence.api, review -> review.api (via infrastructure adapters).
"""
from __future__ import annotations

from ._context import configure, ctx  # noqa: F401
from .routes import router
from ..application.ports import (AssessmentPort, EvidencePort, IdentityPort, IntegrityPort,  # noqa: F401
                                 IntelligencePort, Principal, ReviewPort)

__all__ = ["router", "configure", "Principal", "IdentityPort", "AssessmentPort", "IntelligencePort",
           "EvidencePort", "ReviewPort", "IntegrityPort"]
