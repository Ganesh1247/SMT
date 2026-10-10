"""HTTP routes of the interview module (mounted under /api by the entrypoint)."""
from __future__ import annotations

import re
from typing import Optional

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field

from ..application import service as svc
from ._context import ctx, learner_ref

router = APIRouter()
_ATTEMPT = re.compile(r"^[A-Za-z0-9_-]{1,64}$")


def _err(status: int, code: str, message: str) -> JSONResponse:
    return JSONResponse(status_code=status, content={"error": {"code": code, "message": message}})


class TurnIn(BaseModel):
    model_config = ConfigDict(extra="forbid")
    answer_text: Optional[str] = Field(default=None, max_length=20000)


def _authorise(request: Request):
    if ctx.service is None or ctx.identity is None:
        return None, _err(503, "unavailable", "Service not available")
    p = ctx.identity.authenticate(request.cookies, request.headers)
    if p is None:
        return None, _err(401, "unauthenticated", "Sign in required")
    if p.role != "learner":
        return None, _err(403, "forbidden", "Not allowed")
    return p, None


def _run(fn):
    try:
        return JSONResponse(content=fn())
    except svc.NotFound:
        return _err(404, "not_found", "Not found")
    except svc.Conflict:
        return _err(409, "session_not_started", "Start the session before answering")
    except svc.Invalid:
        return _err(422, "invalid_answer", "Answer must be 1 to 4000 characters")
    except svc.Unavailable:
        return _err(503, "unavailable", "Not recorded yet. Try again.")


@router.post("/interview/{attempt_id}/turn")
def post_turn(attempt_id: str, body: TurnIn, request: Request):
    p, err = _authorise(request)
    if err:
        return err
    if not _ATTEMPT.match(attempt_id):
        return _err(404, "not_found", "Not found")
    return _run(lambda: ctx.service.turn(learner_ref(p.user_id), attempt_id, body.answer_text))


@router.get("/interview/{attempt_id}")
def get_state(attempt_id: str, request: Request):
    p, err = _authorise(request)
    if err:
        return err
    if not _ATTEMPT.match(attempt_id):
        return _err(404, "not_found", "Not found")
    return _run(lambda: ctx.service.state(learner_ref(p.user_id), attempt_id))
