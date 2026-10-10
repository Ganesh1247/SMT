"""HTTP surface for attempts (build-brief section 8). Learner-only; object ownership enforced in the service."""
from __future__ import annotations

from typing import Annotated, Any, Callable, Optional

from fastapi import APIRouter, Body, Depends, HTTPException, Path, Request, Response
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute
from pydantic import BaseModel, ConfigDict, Field
from starlette.concurrency import run_in_threadpool

import identity.api as identity
from assessment.api import runtime
from assessment.domain.rules import AssessmentError

_MESSAGES = {
    "not_found": "Not found",
    "unauthenticated": "Authentication required",
    "forbidden": "Not permitted",
    "level_locked": "That level is not unlocked yet",
    "already_passed": "That level is already passed",
    "consent_required": "Consent is needed before the session can start",
    "consent_incomplete": "All consent items are needed to start a recorded session",
    "track_required": "Choose a track first",
    "run_limit_reached": "Run limit reached for this item",
    "runner_unavailable": "The runner is unavailable; your answer was not recorded",
    "variant_locked": "Submit the first version before the changed version",
    "use_interview": "This level is completed through the live session",
    "attempt_not_active": "This attempt is not active",
    "attempt_closed": "This attempt is closed",
    "awaiting_review": "This level is awaiting review",
}


def _body(code: str, message: Optional[str] = None) -> dict:
    return {"error": {"code": code, "message": message or _MESSAGES.get(code, "Request could not be processed")}}


class EnvelopeRoute(APIRoute):
    """Return typed, stable error bodies: {"error": {"code", "message"}}; never internals."""

    def get_route_handler(self) -> Callable:
        original = super().get_route_handler()

        async def handler(request: Request):
            try:
                return await original(request)
            except AssessmentError as exc:
                return JSONResponse(_body(exc.code), status_code=exc.status)
            except HTTPException as exc:
                detail = exc.detail if isinstance(exc.detail, dict) else {}
                return JSONResponse(_body(detail.get("code", "error"), detail.get("message")),
                                    status_code=exc.status_code)

        return handler


router = APIRouter(route_class=EnvelopeRoute)
learner = identity.require_role("learner")
AttemptId = Annotated[str, Path(min_length=1, max_length=64)]


class CreateBody(BaseModel):
    model_config = ConfigDict(extra="forbid")
    level: int = Field(ge=1, le=4)


class ConsentBody(BaseModel):
    model_config = ConfigDict(extra="forbid")
    version: str = Field(max_length=40)
    scopes: list[Annotated[str, Field(max_length=40)]] = Field(max_length=10)


class SubmitBody(BaseModel):
    model_config = ConfigDict(extra="forbid")
    item_id: str = Field(max_length=64)
    answer: Any
    explanation: Optional[str] = Field(default=None, max_length=2000)


class RunBody(BaseModel):
    model_config = ConfigDict(extra="forbid")
    task_id: str = Field(max_length=64)
    code: str = Field(max_length=40000)


@router.post("/attempts")
def create_attempt(body: CreateBody, response: Response, user=Depends(learner)):
    att, created = runtime.service().create_attempt(user.id, user.track, body.level)
    response.status_code = 201 if created else 200
    return {"attempt_id": att.id, "level": att.level, "status": att.status,
            "consent_required": runtime.service().view_of(att)["consent_required"]}


@router.get("/attempts/{attempt_id}")
def get_attempt(attempt_id: AttemptId, user=Depends(learner)):
    return runtime.service().view(attempt_id, user.id)


@router.get("/me/progress")
def my_progress(user=Depends(learner)):
    return runtime.service().progress(user.id, user.track)


@router.post("/attempts/{attempt_id}/consent")
def consent(attempt_id: AttemptId, body: ConsentBody, user=Depends(learner)):
    att = runtime.service().record_consent(attempt_id, user.id, body.version, body.scopes)
    return {"attempt_id": att.id, "status": att.status, "consent": {"version": att.consent["version"]}}


@router.post("/attempts/{attempt_id}/start")
def start(attempt_id: AttemptId, user=Depends(learner)):
    att = runtime.service().start(attempt_id, user.id)
    return runtime.service().view_of(att)


@router.post("/attempts/{attempt_id}/submit-item")
def submit_item(attempt_id: AttemptId, body: SubmitBody, user=Depends(learner)):
    return runtime.service().submit_item(attempt_id, user.id, body.item_id, body.answer, body.explanation)


@router.post("/attempts/{attempt_id}/run")
def run(attempt_id: AttemptId, body: RunBody, user=Depends(learner)):
    return runtime.service().run(attempt_id, user.id, body.task_id, body.code)


@router.post("/attempts/{attempt_id}/finish")
def finish(attempt_id: AttemptId, user=Depends(learner)):
    return runtime.service().finish(attempt_id, user.id)


@router.post("/attempts/{attempt_id}/events")
def events(attempt_id: AttemptId, body: Annotated[list[dict[str, Any]], Body(max_length=100)],
           user=Depends(learner)):
    return {"accepted": runtime.service().ingest_events(attempt_id, user.id, body)}


@router.post("/attempts/{attempt_id}/chunks/{stream}/{seq}")
async def chunk(attempt_id: AttemptId, stream: Annotated[str, Path(max_length=16)],
                seq: Annotated[int, Path(ge=0, le=100000)], request: Request, user=Depends(learner)):
    declared = request.headers.get("content-length")
    if declared and declared.isdigit() and int(declared) > 8 * 1024 * 1024:
        return JSONResponse(_body("payload_too_large", "Chunk too large"), status_code=413)
    data = await request.body()
    await run_in_threadpool(runtime.service().store_chunk, attempt_id, user.id, stream, seq, data)
    return {"stored": True, "seq": seq}


@router.post("/attempts/{attempt_id}/recording/finalize")
def finalize(attempt_id: AttemptId, user=Depends(learner)):
    return runtime.service().finalize_recording(attempt_id, user.id)
