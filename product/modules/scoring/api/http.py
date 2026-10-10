"""GET /me/profile, GET /me/evidence (learner's own data only)."""
from __future__ import annotations

from dataclasses import asdict

from fastapi import APIRouter, Depends, Query

import identity.api as identity
from scoring.api import runtime

router = APIRouter()


@router.get("/me/profile")
def my_profile(user=Depends(identity.require_role("learner"))):
    import scoring.api as api
    prof = api.profile(user.id)
    return {"alias": user.alias, "note": prof.note, "competencies": [asdict(c) for c in prof.competencies]}


@router.get("/me/evidence")
def my_evidence(limit: int = Query(100, ge=1, le=200), offset: int = Query(0, ge=0, le=100000),
                user=Depends(identity.require_role("learner"))):
    items = runtime.service().evidence_items(user.id)
    return {"total": len(items), "limit": limit, "offset": offset, "items": items[offset:offset + limit]}
