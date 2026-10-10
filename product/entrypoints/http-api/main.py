"""Crucible HTTP API composition root (FastAPI). Transport, wiring and config only.

Run:  python product/entrypoints/http-api/serve.py
  or: uvicorn main:create_app --factory --app-dir product/entrypoints/http-api
"""
from __future__ import annotations

import json
import logging
import sys
from pathlib import Path
from typing import Any, Mapping, Optional

_PRODUCT = Path(__file__).resolve().parents[2]
for _p in (_PRODUCT / "modules", _PRODUCT / "shared-kernel", Path(__file__).resolve().parent):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from fastapi import FastAPI, HTTPException, Request  # noqa: E402
from fastapi.exceptions import RequestValidationError  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402
from fastapi.responses import JSONResponse  # noqa: E402
from fastapi.staticfiles import StaticFiles  # noqa: E402

import wiring  # noqa: E402
from config import Settings  # noqa: E402
from middleware import BodyLimitMiddleware, OriginCheckMiddleware, SecurityHeadersMiddleware  # noqa: E402

log = logging.getLogger("crucible.api")


class JsonFormatter(logging.Formatter):
    """Structured logs. Only whitelisted fields; never request bodies, tokens or personal data."""

    FIELDS = ("event", "mod", "attempt", "level", "outcome", "count", "path", "status")

    def format(self, record: logging.LogRecord) -> str:
        data = {"ts": self.formatTime(record, "%Y-%m-%dT%H:%M:%S"), "level": record.levelname,
                "logger": record.name, "msg": record.getMessage()}
        for f in self.FIELDS:
            if hasattr(record, f):
                data[f] = getattr(record, f)
        if record.exc_info:
            data["error"] = record.exc_info[0].__name__ if record.exc_info[0] else "error"
        return json.dumps(data)


def configure_logging() -> None:
    root = logging.getLogger()
    if any(isinstance(h.formatter, JsonFormatter) for h in root.handlers):
        return
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    root.handlers = [handler]
    root.setLevel(logging.INFO)


def _error(status: int, code: str, message: str) -> JSONResponse:
    return JSONResponse({"error": {"code": code, "message": message}}, status_code=status)


def create_app(settings: Optional[Settings] = None, apis: Optional[Mapping[str, Any]] = None) -> FastAPI:
    """Build the app. `apis` may override module api objects (tests inject fakes for stream B modules)."""
    settings = settings or Settings.from_env()
    configure_logging()
    loaded = wiring.load_all(settings, apis)
    wiring.configure_all(loaded, settings)

    app = FastAPI(title="Crucible API", version="0.1.0", docs_url=None, redoc_url=None, openapi_url=None)
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(OriginCheckMiddleware, allowed_origins=settings.allowed_origins)
    app.add_middleware(BodyLimitMiddleware, max_body=settings.max_body_bytes, max_chunk=settings.max_chunk_bytes)
    app.add_middleware(CORSMiddleware, allow_origins=list(settings.allowed_origins), allow_credentials=True,
                       allow_methods=["GET", "POST", "PUT", "DELETE"], allow_headers=["content-type", "range"])

    @app.exception_handler(HTTPException)
    async def http_error(_: Request, exc: HTTPException):
        detail = exc.detail if isinstance(exc.detail, dict) else {}
        return _error(exc.status_code, str(detail.get("code", "error")), str(detail.get("message", "Request failed")))

    @app.exception_handler(RequestValidationError)
    async def invalid(_: Request, __: RequestValidationError):
        return _error(422, "invalid_input", "The request was not valid")

    @app.exception_handler(Exception)
    async def unexpected(request: Request, exc: Exception):
        log.error("unhandled_error", extra={"event": "unhandled_error", "path": request.url.path}, exc_info=exc)
        return _error(500, "internal_error", "Something went wrong")

    for name, router in wiring.routers(loaded):
        app.include_router(router, prefix="/api")
    wiring.wire_dependencies(app, loaded)

    @app.get("/api/health")
    def health():
        runner = loaded.get("runner")
        isolation = None
        if runner is not None and hasattr(runner, "isolation_status"):
            try:
                isolation = runner.isolation_status()
            except Exception:
                isolation = "unavailable"
        return {"status": "ok", "modules": sorted(loaded), "runner_isolation": isolation}

    dist = _PRODUCT / "entrypoints" / "web" / "dist"
    if settings.serve_web and dist.is_dir():
        app.mount("/", StaticFiles(directory=str(dist), html=True), name="web")
    app.state.apis = loaded
    return app
