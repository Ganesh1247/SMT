"""Environment configuration for the HTTP composition root. No secrets are read from or written to files."""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Mapping, Optional


def _bool(value: Optional[str], default: bool) -> bool:
    if value is None or value == "":
        return default
    return value.strip().lower() in ("1", "true", "yes", "on")


@dataclass(frozen=True)
class Settings:
    data_dir: str = "./data"
    host: str = "127.0.0.1"
    port: int = 8000
    cookie_secure: bool = False
    allowed_origins: tuple = ("http://localhost:5173", "http://127.0.0.1:5173")
    max_body_bytes: int = 256 * 1024
    max_chunk_bytes: int = 8 * 1024 * 1024
    allow_missing_modules: bool = False
    serve_web: bool = True

    @staticmethod
    def from_env(env: Optional[Mapping[str, str]] = None) -> "Settings":
        e = os.environ if env is None else env
        origins = tuple(o.strip() for o in e.get(
            "CRUCIBLE_ALLOWED_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",") if o.strip())
        return Settings(
            data_dir=e.get("DATA_DIR", "./data"),
            host=e.get("CRUCIBLE_HOST", "127.0.0.1"),
            port=int(e.get("CRUCIBLE_PORT", "8000")),
            cookie_secure=_bool(e.get("CRUCIBLE_COOKIE_SECURE"), False),
            allowed_origins=origins,
            max_body_bytes=int(e.get("CRUCIBLE_MAX_BODY_BYTES", str(256 * 1024))),
            max_chunk_bytes=int(e.get("CRUCIBLE_MAX_CHUNK_BYTES", str(8 * 1024 * 1024))),
            allow_missing_modules=_bool(e.get("CRUCIBLE_ALLOW_MISSING_MODULES"), False),
            serve_web=_bool(e.get("CRUCIBLE_SERVE_WEB"), True),
        )
