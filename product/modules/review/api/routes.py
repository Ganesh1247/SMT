"""HTTP routes of the review module. Mounted under /api by the entrypoint."""
from __future__ import annotations

import functools
import inspect
import re
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel, ConfigDict, Field

from ..application import service as svc
from ._context import ctx, learner_ref

router = APIRouter()

_RECIPIENT = r"^org_[a-z0-9_]{3,40}$"
_COMPETENCY = r"^cmp_[a-z0-9_]{3,40}$"
_ROLE = r"^role_[a-z0-9_]{3,40}$"
MAX_RECORDING_SLICE = 8 * 1024 * 1024
_RANGE = re.compile(r"^bytes=(\d*)-(\d*)$")


def _err(status: int, code: str, message: str) -> JSONResponse:
    return JSONResponse(status_code=status, content={"error": {"code": code, "message": message}})


def _not_found() -> JSONResponse:
    return _err(404, "not_found", "Not found")


_STATUS = {svc.NotFound: 404, svc.Conflict: 409, svc.Invalid: 422, svc.Unavailable: 503, svc.QueryError: 422}


def _guard(roles: tuple[str, ...]):
    """Authenticate, authorise by server-side role, translate domain errors to stable JSON errors."""
    def deco(fn):
        @functools.wraps(fn)
        def wrapper(request: Request, *a, **kw):
            if ctx.service is None or ctx.identity is None:
                return _err(503, "unavailable", "Service not available")
            p = ctx.identity.authenticate(request.cookies, request.headers)
            if p is None:
                return _err(401, "unauthenticated", "Sign in required")
            if p.role not in roles:
                return _err(403, "forbidden", "Not allowed")
            try:
                return fn(request, p, *a, **kw)
            except svc.NotFound:
                return _not_found()
            except svc.ReviewError as exc:
                status = next((s for t, s in _STATUS.items() if isinstance(exc, t)), 500)
                msg = {503: "Not recorded yet. Try again.", 409: "This case was decided by another reviewer."}.get(status, "Request could not be processed")
                return _err(status, exc.code, msg)
        sig = inspect.signature(fn)
        wrapper.__signature__ = sig.replace(parameters=[v for k, v in sig.parameters.items() if k != "p"])
        return wrapper
    return deco


class _Scope(BaseModel):
    model_config = ConfigDict(extra="forbid")
    include: list[str] = Field(min_length=1, max_length=5)


class GrantIn(BaseModel):
    model_config = ConfigDict(extra="forbid")
    recipient_id: str = Field(pattern=_RECIPIENT)
    competencies: list[str] = Field(min_length=1, max_length=8)
    scope: Optional[_Scope] = None
    role_ref: Optional[str] = Field(default=None, pattern=_ROLE)
    expires_at: datetime
    consent_text_version: str = Field(pattern=r"^[0-9]+\.[0-9]+$")


class DecisionIn(BaseModel):
    model_config = ConfigDict(extra="forbid")
    outcome: str = Field(max_length=32)
    new_outcome: Optional[str] = Field(default=None, max_length=32)
    reason: str = Field(max_length=1000)


class AppealIn(BaseModel):
    model_config = ConfigDict(extra="forbid")
    event_id: str = Field(max_length=64)
    reason: str = Field(max_length=1000)


# ---------------------------------------------------------------- grants
@router.post("/me/grants", status_code=201)
@_guard(("learner",))
def create_grant(request: Request, p, body: GrantIn):
    for c in body.competencies:
        if not re.match(_COMPETENCY, c):
            return _err(422, "invalid", "Invalid competency")
    g = ctx.service.create_grant(learner_ref(p.user_id), body.recipient_id, body.competencies,
                                 body.scope.include if body.scope else None, body.role_ref,
                                 body.expires_at, body.consent_text_version)
    return JSONResponse(status_code=201, content=g)


@router.get("/me/grants")
@_guard(("learner",))
def list_grants(request: Request, p):
    return {"grants": ctx.service.list_grants(learner_ref(p.user_id))}


@router.delete("/me/grants/{grant_id}", status_code=204)
@_guard(("learner",))
def revoke_grant(request: Request, p, grant_id: str):
    ctx.service.revoke_grant(learner_ref(p.user_id), grant_id[:64])
    return Response(status_code=204)


# ---------------------------------------------------------------- appeals
@router.post("/me/appeals", status_code=201)
@_guard(("learner",))
def file_appeal(request: Request, p, body: AppealIn):
    return JSONResponse(status_code=201, content=ctx.service.file_appeal(learner_ref(p.user_id), body.event_id, body.reason))


@router.get("/me/appeals")
@_guard(("learner",))
def list_appeals(request: Request, p):
    return {"appeals": ctx.service.list_appeals(learner_ref(p.user_id))}


# ---------------------------------------------------------------- reviewer queue
@router.get("/review/queue")
@_guard(("reviewer",))
def queue(request: Request, p, reason: Optional[str] = None, limit: int = 25, offset: int = 0):
    limit = max(1, min(limit, 100))
    offset = max(0, offset)
    return {"cases": ctx.service.list_queue(reason, limit, offset)}


@router.get("/review/cases/{case_id}")
@_guard(("reviewer",))
def case_detail(request: Request, p, case_id: str):
    return ctx.service.case_detail(case_id[:64])


@router.post("/review/cases/{case_id}/decision", status_code=201)
@_guard(("reviewer",))
def decide(request: Request, p, case_id: str, body: DecisionIn):
    out = ctx.service.decide(case_id[:64], p.user_id, body.outcome, body.new_outcome, body.reason)
    return JSONResponse(status_code=201, content=out)


@router.get("/review/attempts/{attempt_id}/recording/{stream}")
@_guard(("reviewer",))
def recording(request: Request, p, attempt_id: str, stream: str):
    info = ctx.service.recording_info(attempt_id, stream)
    size = int(info["size"])
    header = request.headers.get("range")
    if header is None:
        start, end = 0, min(size - 1, MAX_RECORDING_SLICE - 1)
    else:
        m = _RANGE.match(header.strip())
        if not m or (m.group(1) == "" and m.group(2) == ""):
            return Response(status_code=416, headers={"Content-Range": f"bytes */{size}"})
        if m.group(1) == "":
            start, end = max(0, size - int(m.group(2))), size - 1
        else:
            start = int(m.group(1))
            end = int(m.group(2)) if m.group(2) else size - 1
        end = min(end, size - 1, start + MAX_RECORDING_SLICE - 1)
        if start >= size or end < start:
            return Response(status_code=416, headers={"Content-Range": f"bytes */{size}"})
    body = ctx.service.read_recording(attempt_id, stream, start, end)
    headers = {"Accept-Ranges": "bytes", "Cache-Control": "no-store",
               "Content-Range": f"bytes {start}-{end}/{size}", "X-Content-Type-Options": "nosniff"}
    whole = header is None and start == 0 and end == size - 1
    return Response(content=body, status_code=200 if whole else 206, media_type=info.get("content_type", "video/webm"),
                    headers=headers)
