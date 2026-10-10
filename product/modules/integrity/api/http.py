"""HTTP router for the integrity module (mounted by the entrypoint under /api).

Authentication is injected: the entrypoint overrides `current_user_dependency` with
`identity.api.current_user`. Without an override every call is rejected (deny by default).
Object ownership is enforced in the service; unknown and foreign attempts both return the
identical 404.
"""
from __future__ import annotations

import json
import logging
import os
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response

from ..domain import models as d

log = logging.getLogger("crucible.integrity")
router = APIRouter(tags=["integrity"])

MAX_JSON_BODY = 64 * 1024
MAX_SMALL_BODY = 4 * 1024


def current_user_dependency() -> Any:
    """Placeholder port. Overridden at composition time by identity.api.current_user."""
    raise HTTPException(status_code=401, detail={"code": "unauthenticated"})


def _learner_id(user: Any) -> str:
    for name in ("user_id", "id", "learner_id"):
        value = user.get(name) if isinstance(user, dict) else getattr(user, name, None)
        if value:
            return str(value)
    raise HTTPException(status_code=401, detail={"code": "unauthenticated"})


def _require_learner(user: Any) -> str:
    role = user.get("role") if isinstance(user, dict) else getattr(user, "role", None)
    if role is not None and str(getattr(role, "value", role)) != "learner":
        raise HTTPException(status_code=403, detail={"code": "forbidden"})
    return _learner_id(user)


def _service():
    from . import get_service
    return get_service()


def _http(exc: d.IntegrityError) -> HTTPException:
    status = {"not_found": 404, "invalid_input": 422, "too_large": 413, "conflict": 409}.get(exc.code, 400)
    return HTTPException(status_code=status, detail={"code": exc.code})


async def _body(request: Request, cap: int) -> bytes:
    declared = request.headers.get("content-length")
    if declared and declared.isdigit() and int(declared) > cap:
        raise d.TooLarge("body")
    buf = bytearray()
    async for part in request.stream():
        buf += part
        if len(buf) > cap:
            raise d.TooLarge("body")
    return bytes(buf)


async def _json(request: Request, cap: int) -> Any:
    raw = await _body(request, cap)
    try:
        return json.loads(raw.decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        raise d.InvalidInput("json") from None


# ------------------------------------------------------------------ pre-check

@router.get("/precheck/payload")
def precheck_payload(size: int = Query(..., ge=1), user: Any = Depends(current_user_dependency)) -> Response:
    _learner_id(user)
    cap = _service()._cfg.precheck_payload_max_bytes
    if size > cap:
        raise HTTPException(status_code=422, detail={"code": "invalid_input"})
    return Response(content=os.urandom(size), media_type="application/octet-stream",
                    headers={"Cache-Control": "no-store"})


@router.post("/precheck/echo")
async def precheck_echo(request: Request, user: Any = Depends(current_user_dependency)) -> dict:
    _learner_id(user)
    try:
        data = await _body(request, _service()._cfg.precheck_payload_max_bytes)
    except d.IntegrityError as exc:
        raise _http(exc) from None
    return {"received": len(data)}


@router.post("/precheck/report")
async def precheck_report(request: Request, user: Any = Depends(current_user_dependency)) -> dict:
    learner = _learner_id(user)
    try:
        report = await _json(request, MAX_SMALL_BODY)
        return _service().evaluate_precheck(learner, report).to_dict()
    except d.IntegrityError as exc:
        raise _http(exc) from None


# ------------------------------------------------------------------ attempt-scoped

@router.post("/attempts/{attempt_id}/consent")
async def post_consent(attempt_id: str, request: Request, user: Any = Depends(current_user_dependency)) -> dict:
    learner = _require_learner(user)
    try:
        body = await _json(request, MAX_SMALL_BODY)
        if not isinstance(body, dict) or set(body) != {"version", "scopes"}:
            raise d.InvalidInput("consent")
        rec = _service().record_consent(attempt_id, learner, body["version"], body["scopes"])
    except d.IntegrityError as exc:
        raise _http(exc) from None
    log.info("consent_recorded", extra={"attempt_id": attempt_id, "version": rec.version})
    return {"recorded": True, "version": rec.version, "scopes": list(rec.scopes)}


@router.post("/attempts/{attempt_id}/events", status_code=202)
async def post_events(attempt_id: str, request: Request, user: Any = Depends(current_user_dependency)) -> dict:
    learner = _require_learner(user)
    try:
        body = await _json(request, MAX_JSON_BODY)
        events = body.get("events") if isinstance(body, dict) and set(body) == {"events"} else body
        stored = _service().ingest_events(attempt_id, learner, events)
    except d.IntegrityError as exc:
        raise _http(exc) from None
    return {"accepted": stored}


@router.post("/attempts/{attempt_id}/chunks/{stream}/{seq}")
async def post_chunk(attempt_id: str, stream: str, seq: int, request: Request,
                     user: Any = Depends(current_user_dependency)) -> dict:
    learner = _require_learner(user)
    service = _service()
    try:
        service._owned(attempt_id, learner)  # ownership before consuming the body
        data = await _body(request, service._cfg.chunk_max_bytes)
        receipt = service.store_chunk(attempt_id, learner, stream, seq, data)
    except d.IntegrityError as exc:
        raise _http(exc) from None
    return {"seq": receipt.seq, "sha256": receipt.sha256, "size": receipt.size}


@router.post("/attempts/{attempt_id}/recording/finalize")
def post_finalize(attempt_id: str, user: Any = Depends(current_user_dependency)) -> dict:
    learner = _require_learner(user)
    try:
        return _service().finalize_recording(attempt_id, learner)
    except d.IntegrityError as exc:
        raise _http(exc) from None
