"""ASGI middleware: security headers, request-size limits, cross-site request origin check."""
from __future__ import annotations

import json
from typing import Iterable
from urllib.parse import urlsplit

SAFE_METHODS = {"GET", "HEAD", "OPTIONS"}


def _json_response(status: int, code: str, message: str):
    body = json.dumps({"error": {"code": code, "message": message}}).encode()
    start = {"type": "http.response.start", "status": status,
             "headers": [(b"content-type", b"application/json"), (b"content-length", str(len(body)).encode())]}
    return start, {"type": "http.response.body", "body": body}


class SecurityHeadersMiddleware:
    HEADERS = [
        (b"x-content-type-options", b"nosniff"),
        (b"x-frame-options", b"DENY"),
        (b"referrer-policy", b"no-referrer"),
        (b"permissions-policy", b"camera=(self), microphone=(self), display-capture=(self), fullscreen=(self)"),
        (b"cross-origin-opener-policy", b"same-origin"),
    ]

    def __init__(self, app) -> None:
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        api = scope["path"].startswith("/api")

        async def wrapped(message):
            if message["type"] == "http.response.start":
                headers = list(message.get("headers", []))
                present = {k.lower() for k, _ in headers}
                for k, v in self.HEADERS:
                    if k not in present:
                        headers.append((k, v))
                if api and b"cache-control" not in present:
                    headers.append((b"cache-control", b"no-store"))
                if api and b"content-security-policy" not in present:
                    headers.append((b"content-security-policy", b"default-src 'none'; frame-ancestors 'none'"))
                message = dict(message, headers=headers)
            await send(message)

        await self.app(scope, receive, wrapped)


class BodyLimitMiddleware:
    """Reject oversized bodies by declared length and by streamed bytes. Recording chunks get a larger cap."""

    def __init__(self, app, max_body: int, max_chunk: int) -> None:
        self.app, self.max_body, self.max_chunk = app, max_body, max_chunk

    def _limit(self, path: str) -> int:
        return self.max_chunk if "/chunks/" in path else self.max_body

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http" or scope["method"] in SAFE_METHODS:
            return await self.app(scope, receive, send)
        limit = self._limit(scope["path"])
        for k, v in scope["headers"]:
            if k == b"content-length" and v.isdigit() and int(v) > limit:
                start, body = _json_response(413, "payload_too_large", "Request body too large")
                await send(start)
                return await send(body)
        seen = 0
        too_big = False

        async def limited():
            nonlocal seen, too_big
            message = await receive()
            if message["type"] == "http.request":
                seen += len(message.get("body", b""))
                if seen > limit:
                    too_big = True
                    return {"type": "http.disconnect"}  # abort the handler before it can store a partial body
            return message

        sent = False

        async def guarded_send(message):
            nonlocal sent
            if too_big and not sent and message["type"] == "http.response.start":
                sent = True
                start, body = _json_response(413, "payload_too_large", "Request body too large")
                await send(start)
                await send(body)
                return
            if sent:
                return
            await send(message)

        await self.app(scope, limited, guarded_send)


class OriginCheckMiddleware:
    """CSRF defence for cookie auth (in addition to SameSite=Strict): state-changing requests that carry an
    Origin header must come from an allowed origin or the same host."""

    def __init__(self, app, allowed_origins: Iterable[str]) -> None:
        self.app = app
        self.allowed = {o.rstrip("/").lower() for o in allowed_origins}

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http" or scope["method"] in SAFE_METHODS:
            return await self.app(scope, receive, send)
        headers = {k: v for k, v in scope["headers"]}
        origin = headers.get(b"origin", b"").decode("latin-1").rstrip("/").lower()
        if origin and origin not in self.allowed:
            host = headers.get(b"host", b"").decode("latin-1").lower()
            if urlsplit(origin).netloc != host:
                start, body = _json_response(403, "forbidden", "Not permitted")
                await send(start)
                return await send(body)
        await self.app(scope, receive, send)
