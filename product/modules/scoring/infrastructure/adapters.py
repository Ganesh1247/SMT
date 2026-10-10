"""SQLite snapshot store and evidence reader for scoring."""
from __future__ import annotations

import json
import os
from typing import Optional, Sequence

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.pool import StaticPool

from scoring.application.service import Published

SCHEMA = [
    """CREATE TABLE IF NOT EXISTS published_estimates (
        id INTEGER PRIMARY KEY AUTOINCREMENT, learner_id TEXT NOT NULL, competency TEXT NOT NULL,
        estimate REAL NOT NULL, lower REAL NOT NULL, upper REAL NOT NULL, as_of TEXT NOT NULL,
        counts_json TEXT NOT NULL, evidence_head TEXT NOT NULL)""",
    "CREATE INDEX IF NOT EXISTS ix_pub_learner ON published_estimates(learner_id, competency, as_of)",
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
    return "sqlite:///" + os.path.join(base, "scoring.db").replace("\\", "/")


class SqlSnapshotStore:
    def __init__(self, engine: Engine) -> None:
        self._e = engine

    def latest(self, learner_id: str, competency: str, as_of: Optional[str] = None) -> Optional[Published]:
        sql = "SELECT * FROM published_estimates WHERE learner_id=:l AND competency=:c"
        params = {"l": learner_id, "c": competency}
        if as_of is not None:
            sql += " AND as_of<=:a"
            params["a"] = as_of
        sql += " ORDER BY as_of DESC, id DESC LIMIT 1"
        with self._e.connect() as c:
            row = c.execute(text(sql), params).first()
        if row is None:
            return None
        return Published(row.learner_id, row.competency, row.estimate, row.lower, row.upper,
                         row.as_of, json.loads(row.counts_json), row.evidence_head)

    def add(self, snap: Published) -> None:
        with self._e.begin() as c:
            c.execute(text(
                "INSERT INTO published_estimates(learner_id,competency,estimate,lower,upper,as_of,"
                "counts_json,evidence_head) VALUES(:l,:c,:e,:lo,:u,:a,:j,:h)"),
                {"l": snap.learner_id, "c": snap.competency, "e": snap.estimate, "lo": snap.lower,
                 "u": snap.upper, "a": snap.as_of, "j": json.dumps(snap.counts), "h": snap.evidence_head})


class LedgerEvidenceReader:
    """Reads the learner's evidence through evidence.api only."""

    def __init__(self) -> None:
        import evidence.api as evidence  # cross-module access only via api/
        self._api = evidence

    def list_for_learner(self, learner_id: str) -> Sequence:
        return self._api.list_for_learner(learner_id)

    def verify(self, learner_id: Optional[str] = None):
        return self._api.verify(learner_id)
