"""Public surface of the hr module.

router     /hr/roles (CRUD, versioned), /hr/roles/{id}/results, /hr/evidence/{alias}/{competency},
           /hr/receipts/verify  (recruiter role only)
configure(identity, evidence, review=None, clock=None, ids=None, store=None, data_dir=None)
Default review port -> review.api.query_shared_evidence; evidence port must supply verify_receipt(hash).
"""
from __future__ import annotations

from ..application.ports import EvidencePort, IdentityPort, Principal, ReviewPort  # noqa: F401
from ._context import configure, ctx  # noqa: F401
from .routes import router

__all__ = ["router", "configure", "Principal", "IdentityPort", "ReviewPort", "EvidencePort"]
