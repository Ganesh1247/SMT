"""HTTP routes of the hr module (mounted under /api by the entrypoint). Recruiter role only."""
from __future__ import annotations

import functools
import inspect
import re
from typing import Any, Optional

from fastapi import APIRouter, Body, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field

from ..application import service as svc
from ._context import ctx, recipient_id

router = APIRouter()
_ALIAS = re.compile(r"^cnd_[a-f0-9]{16}$")
_COMPETENCY = re.compile(r"^cmp_[a-z0-9_]{3,40}$")
_ROLE = re.compile(r"^role_[a-z0-9_]{3,40}$")


def _err(status: int, code: str, message: str, details: list | None = None) -> JSONResponse:
    body: dict[str, Any] = {"code": code, "message": message}
    if details:
        body["details"] = details
    return JSONResponse(status_code=status, content={"error": body})


def _guard(fn):
    """Authenticate (recruiter only), derive the organisation server-side, map errors to stable JSON."""
    @functools.wraps(fn)
    def wrapper(request: Request, *a, **kw):
        if ctx.service is None or ctx.identity is None:
            return _err(503, "unavailable", "Service not available")
        p = ctx.identity.authenticate(request.cookies, request.headers)
        if p is None:
            return _err(401, "unauthenticated", "Sign in required")
        if p.role != "recruiter":
            return _err(403, "forbidden", "Not allowed")
        try:
            return fn(request, recipient_id(p), *a, **kw)
        except svc.NotFound:
            return _err(404, "not_found", "No shared evidence for this competency" if kw.get("competency") else "Not found")
        except svc.Invalid as exc:
            return _err(422, exc.code, "The role could not be saved. Fix the listed fields.", exc.details)
        except svc.Upstream:
            return _err(502, "upstream_unavailable", "We could not load shared evidence. Try again.")
    sig = inspect.signature(fn)
    wrapper.__signature__ = sig.replace(parameters=[v for k, v in sig.parameters.items() if k != "org"])
    return wrapper


class ReceiptIn(BaseModel):
    model_config = ConfigDict(extra="forbid")
    candidate_ref: str = Field(pattern=_ALIAS.pattern)
    competency_id: str = Field(pattern=_COMPETENCY.pattern)
    receipt_hash: str = Field(pattern=r"^sha256:[a-f0-9]{64}$")
    role_id: Optional[str] = Field(default=None, pattern=_ROLE.pattern)


@router.get("/hr/roles")
@_guard
def list_roles(request: Request, org):
    return {"roles": ctx.service.list_roles(org)}


@router.post("/hr/roles", status_code=201)
@_guard
def create_role(request: Request, org, body: Any = Body(...)):
    return JSONResponse(status_code=201, content=ctx.service.create_role(org, body))


@router.get("/hr/roles/{role_id}")
@_guard
def get_role(request: Request, org, role_id: str, version: Optional[int] = None):
    return ctx.service.get_role(org, role_id[:64], version)


@router.put("/hr/roles/{role_id}")
@_guard
def update_role(request: Request, org, role_id: str, body: Any = Body(...)):
    return ctx.service.update_role(org, role_id[:64], body)


@router.get("/hr/roles/{role_id}/results")
@_guard
def role_results(request: Request, org, role_id: str):
    return ctx.service.results(org, role_id[:64])


@router.get("/hr/evidence/{learner_alias}/{competency}")
@_guard
def evidence_page(request: Request, org, learner_alias: str, competency: str, role_id: Optional[str] = None):
    if not _ALIAS.match(learner_alias) or not _COMPETENCY.match(competency) or (role_id and not _ROLE.match(role_id)):
        raise svc.NotFound()
    return ctx.service.evidence_page(org, learner_alias, competency, role_id)


@router.post("/hr/receipts/verify")
@_guard
def verify_receipt(request: Request, org, body: ReceiptIn):
    return ctx.service.verify_receipt(org, body.candidate_ref, body.competency_id, body.receipt_hash, body.role_id)
