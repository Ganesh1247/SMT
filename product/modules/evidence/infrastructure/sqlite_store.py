"""SQLite persistence for the evidence ledger (table `ledger`)."""
from __future__ import annotations

import json
import os
from typing import Optional

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.pool import StaticPool

from evidence.application.ledger import StoredEntry

SCHEMA = [
    """CREATE TABLE IF NOT EXISTS ledger (
        sequence INTEGER PRIMARY KEY, idempotency_key TEXT NOT NULL UNIQUE,
        event_id TEXT NOT NULL, event_type TEXT NOT NULL, learner_id TEXT NOT NULL,
        event_json TEXT NOT NULL, meta_json TEXT, meta_bound INTEGER NOT NULL DEFAULT 0,
        prev_hash TEXT NOT NULL, hash TEXT NOT NULL, recorded_at TEXT NOT NULL)""",
    "CREATE INDEX IF NOT EXISTS ix_ledger_learner ON ledger(learner_id, sequence)",
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


def default_database_url(data_dir: Optional[str] = None) -> str:
    base = data_dir or os.environ.get("DATA_DIR", "./data")
    os.makedirs(base, exist_ok=True)
    return "sqlite:///" + os.path.join(base, "evidence.db").replace("\\", "/")


def _entry(row) -> StoredEntry:
    return StoredEntry(
        sequence=row.sequence, event_id=row.event_id, event_type=row.event_type,
        learner_id=row.learner_id, event=json.loads(row.event_json),
        meta=json.loads(row.meta_json) if row.meta_json else None,
        prev_hash=row.prev_hash, hash=row.hash, recorded_at=row.recorded_at,
        meta_bound=bool(row.meta_bound),
    )


class SqlLedgerStore:
    def __init__(self, engine: Engine) -> None:
        self._e = engine

    def by_key(self, key: str) -> Optional[StoredEntry]:
        with self._e.connect() as c:
            row = c.execute(text("SELECT * FROM ledger WHERE idempotency_key=:k"), {"k": key}).first()
        return _entry(row) if row else None

    def last(self) -> Optional[StoredEntry]:
        with self._e.connect() as c:
            row = c.execute(text("SELECT * FROM ledger ORDER BY sequence DESC LIMIT 1")).first()
        return _entry(row) if row else None

    def insert(self, entry: StoredEntry, key: str) -> None:
        with self._e.begin() as c:
            c.execute(text(
                "INSERT INTO ledger(sequence,idempotency_key,event_id,event_type,learner_id,event_json,"
                "meta_json,meta_bound,prev_hash,hash,recorded_at) VALUES(:s,:k,:id,:t,:l,:e,:m,:b,:p,:h,:r)"),
                {"s": entry.sequence, "k": key, "id": entry.event_id, "t": entry.event_type,
                 "l": entry.learner_id, "e": json.dumps(dict(entry.event), sort_keys=True),
                 "m": json.dumps(dict(entry.meta), sort_keys=True) if entry.meta is not None else None,
                 "b": 1 if entry.meta_bound else 0, "p": entry.prev_hash, "h": entry.hash,
                 "r": entry.recorded_at})

    def all(self) -> list[StoredEntry]:
        with self._e.connect() as c:
            rows = c.execute(text("SELECT * FROM ledger ORDER BY sequence")).all()
        return [_entry(r) for r in rows]

    def for_learner(self, learner_id: str) -> list[StoredEntry]:
        with self._e.connect() as c:
            rows = c.execute(text("SELECT * FROM ledger WHERE learner_id=:l ORDER BY sequence"),
                             {"l": learner_id}).all()
        return [_entry(r) for r in rows]


__all__ = ["SqlLedgerStore", "make_engine", "default_database_url", "IntegrityError"]
