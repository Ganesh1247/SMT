"""SQLite repositories and scrypt hasher for identity."""
from __future__ import annotations

import base64
import hashlib
import hmac
import os
import secrets
from datetime import datetime
from typing import Optional

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.pool import StaticPool

from identity.domain.model import User

SCHEMA = [
    """CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY, alias TEXT NOT NULL UNIQUE, email TEXT NOT NULL UNIQUE,
        display_name TEXT NOT NULL, role TEXT NOT NULL, track TEXT,
        password_hash TEXT NOT NULL, created_at TEXT NOT NULL)""",
    """CREATE TABLE IF NOT EXISTS sessions (
        token_hash TEXT PRIMARY KEY, user_id TEXT NOT NULL, expires_at TEXT NOT NULL,
        created_at TEXT NOT NULL)""",
    "CREATE INDEX IF NOT EXISTS ix_sessions_user ON sessions(user_id)",
]


def make_engine(database_url: str) -> Engine:
    if database_url in ("sqlite://", "sqlite:///:memory:"):
        engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    else:
        engine = create_engine(database_url, connect_args={"check_same_thread": False})
    with engine.begin() as conn:
        for stmt in SCHEMA:
            conn.execute(text(stmt))
    return engine


class ScryptHasher:
    """scrypt via the standard library; format scrypt$n$r$p$salt$hash."""

    N, R, P = 2 ** 14, 8, 1

    def hash(self, password: str) -> str:
        salt = secrets.token_bytes(16)
        dk = hashlib.scrypt(password.encode("utf-8"), salt=salt, n=self.N, r=self.R, p=self.P, dklen=32)
        return "scrypt$%d$%d$%d$%s$%s" % (
            self.N, self.R, self.P, base64.b64encode(salt).decode(), base64.b64encode(dk).decode())

    def verify(self, password: str, stored: str) -> bool:
        try:
            _, n, r, p, salt_b64, dk_b64 = stored.split("$")
            salt, expected = base64.b64decode(salt_b64), base64.b64decode(dk_b64)
            dk = hashlib.scrypt(password.encode("utf-8"), salt=salt, n=int(n), r=int(r), p=int(p), dklen=len(expected))
        except (ValueError, TypeError):
            return False
        return hmac.compare_digest(dk, expected)


def _iso(dt: datetime) -> str:
    return dt.isoformat()


def _user(row) -> User:
    return User(id=row.id, alias=row.alias, role=row.role, track=row.track,
                email=row.email, display_name=row.display_name)


class SqlUserRepository:
    def __init__(self, engine: Engine) -> None:
        self._e = engine

    def add(self, user: User, password_hash: str, now: datetime) -> bool:
        try:
            with self._e.begin() as c:
                c.execute(text(
                    "INSERT INTO users(id,alias,email,display_name,role,track,password_hash,created_at) "
                    "VALUES(:id,:alias,:email,:dn,:role,:track,:ph,:ca)"),
                    {"id": user.id, "alias": user.alias, "email": user.email, "dn": user.display_name,
                     "role": user.role, "track": user.track, "ph": password_hash, "ca": _iso(now)})
            return True
        except IntegrityError:
            return False

    def by_email(self, email: str) -> Optional[tuple[User, str]]:
        with self._e.connect() as c:
            row = c.execute(text("SELECT * FROM users WHERE email=:e"), {"e": email}).first()
        return (_user(row), row.password_hash) if row else None

    def by_id(self, user_id: str) -> Optional[User]:
        with self._e.connect() as c:
            row = c.execute(text("SELECT * FROM users WHERE id=:i"), {"i": user_id}).first()
        return _user(row) if row else None

    def by_alias(self, alias: str) -> Optional[User]:
        with self._e.connect() as c:
            row = c.execute(text("SELECT * FROM users WHERE alias=:a"), {"a": alias}).first()
        return _user(row) if row else None

    def set_track(self, user_id: str, track: str) -> None:
        with self._e.begin() as c:
            c.execute(text("UPDATE users SET track=:t WHERE id=:i"), {"t": track, "i": user_id})


class SqlSessionRepository:
    def __init__(self, engine: Engine) -> None:
        self._e = engine

    def create(self, token_hash: str, user_id: str, expires_at: datetime, now: datetime) -> None:
        with self._e.begin() as c:
            c.execute(text("INSERT INTO sessions(token_hash,user_id,expires_at,created_at) VALUES(:t,:u,:x,:c)"),
                      {"t": token_hash, "u": user_id, "x": _iso(expires_at), "c": _iso(now)})

    def user_id_for(self, token_hash: str, now: datetime) -> Optional[str]:
        with self._e.connect() as c:
            row = c.execute(text("SELECT user_id, expires_at FROM sessions WHERE token_hash=:t"),
                            {"t": token_hash}).first()
        if not row or datetime.fromisoformat(row.expires_at) <= now:
            return None
        return row.user_id

    def delete(self, token_hash: str) -> None:
        with self._e.begin() as c:
            c.execute(text("DELETE FROM sessions WHERE token_hash=:t"), {"t": token_hash})


def default_database_url(data_dir: Optional[str] = None) -> str:
    base = data_dir or os.environ.get("DATA_DIR", "./data")
    os.makedirs(base, exist_ok=True)
    return "sqlite:///" + os.path.join(base, "identity.db").replace("\\", "/")
