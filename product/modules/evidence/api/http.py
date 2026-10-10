"""GET /audit/ledger/verify (auditor or reviewer)."""
from __future__ import annotations

from fastapi import APIRouter, Depends

import identity.api as identity
from evidence.api import runtime

router = APIRouter()


@router.get("/audit/ledger/verify")
def verify_ledger(_user=Depends(identity.require_role("auditor", "reviewer"))):
    r = runtime.service().verify(None)
    return {"ok": r.ok, "entries_checked": r.entries_checked, "first_failure": r.first_failure,
            "message": r.message, "canonicalisation": "crucible-evidence-event-v1"}
