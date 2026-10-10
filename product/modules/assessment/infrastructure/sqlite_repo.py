"""SQLite persistence for assessment (tables attempts, answers, runs)."""
from __future__ import annotations

import json
import os
from typing import Any, Mapping, Optional

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.pool import StaticPool

from assessment.application.ports import Attempt

SCHEMA = [
    """CREATE TABLE IF NOT EXISTS attempts (
        id TEXT PRIMARY KEY, learner_id TEXT NOT NULL, track TEXT NOT NULL, level INTEGER NOT NULL,
        attempt_no INTEGER NOT NULL, seed TEXT NOT NULL, status TEXT NOT NULL, plan_json TEXT NOT NULL,
        consent_json TEXT, result_json TEXT, created_at TEXT NOT NULL, started_at TEXT, finished_at TEXT)""",
    "CREATE INDEX IF NOT EXISTS ix_attempts_learner ON attempts(learner_id, track, level, attempt_no)",
    """CREATE TABLE IF NOT EXISTS answers (
        attempt_id TEXT NOT NULL, item_ref TEXT NOT NULL, answer_json TEXT NOT NULL, explanation TEXT,
        graded_json TEXT NOT NULL, submitted_at TEXT NOT NULL, PRIMARY KEY (attempt_id, item_ref))""",
    """CREATE TABLE IF NOT EXISTS runs (
        id INTEGER PRIMARY KEY AUTOINCREMENT, attempt_id TEXT NOT NULL, item_ref TEXT NOT NULL, at TEXT NOT NULL)""",
    "CREATE INDEX IF NOT EXISTS ix_runs_item ON runs(attempt_id, item_ref)",
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
    return "sqlite:///" + os.path.join(base, "assessment.db").replace("\\", "/")


def _attempt(row) -> Attempt:
    return Attempt(
        id=row.id, learner_id=row.learner_id, track=row.track, level=row.level, attempt_no=row.attempt_no,
        seed=row.seed, status=row.status, plan=tuple(json.loads(row.plan_json)),
        consent=json.loads(row.consent_json) if row.consent_json else None,
        result=json.loads(row.result_json) if row.result_json else None,
        created_at=row.created_at, started_at=row.started_at, finished_at=row.finished_at)


class SqlAttemptRepository:
    def __init__(self, engine: Engine) -> None:
        self._e = engine

    def add(self, a: Attempt) -> None:
        with self._e.begin() as c:
            c.execute(text(
                "INSERT INTO attempts(id,learner_id,track,level,attempt_no,seed,status,plan_json,consent_json,"
                "result_json,created_at,started_at,finished_at) VALUES(:id,:l,:t,:lv,:n,:s,:st,:p,:c,:r,:ca,:sa,:fa)"),
                self._params(a))

    @staticmethod
    def _params(a: Attempt) -> dict:
        return {"id": a.id, "l": a.learner_id, "t": a.track, "lv": a.level, "n": a.attempt_no, "s": a.seed,
                "st": a.status, "p": json.dumps(list(a.plan)),
                "c": json.dumps(dict(a.consent)) if a.consent is not None else None,
                "r": json.dumps(dict(a.result)) if a.result is not None else None,
                "ca": a.created_at, "sa": a.started_at, "fa": a.finished_at}

    def update(self, a: Attempt) -> None:
        with self._e.begin() as c:
            c.execute(text(
                "UPDATE attempts SET status=:st, plan_json=:p, consent_json=:c, result_json=:r, "
                "started_at=:sa, finished_at=:fa WHERE id=:id"), self._params(a))

    def get(self, attempt_id: str) -> Optional[Attempt]:
        with self._e.connect() as c:
            row = c.execute(text("SELECT * FROM attempts WHERE id=:i"), {"i": attempt_id}).first()
        return _attempt(row) if row else None

    def for_learner(self, learner_id: str, track: Optional[str] = None, level: Optional[int] = None) -> list[Attempt]:
        sql = "SELECT * FROM attempts WHERE learner_id=:l"
        params: dict[str, Any] = {"l": learner_id}
        if track is not None:
            sql += " AND track=:t"
            params["t"] = track
        if level is not None:
            sql += " AND level=:lv"
            params["lv"] = level
        sql += " ORDER BY level, attempt_no"
        with self._e.connect() as c:
            return [_attempt(r) for r in c.execute(text(sql), params).all()]

    def upsert_answer(self, attempt_id: str, item_ref: str, answer: Any, explanation: Optional[str],
                      graded: Mapping[str, Any], at: str) -> None:
        with self._e.begin() as c:
            c.execute(text(
                "INSERT INTO answers(attempt_id,item_ref,answer_json,explanation,graded_json,submitted_at) "
                "VALUES(:a,:r,:j,:e,:g,:t) ON CONFLICT(attempt_id,item_ref) DO UPDATE SET "
                "answer_json=:j, explanation=:e, graded_json=:g, submitted_at=:t"),
                {"a": attempt_id, "r": item_ref, "j": json.dumps(answer), "e": explanation,
                 "g": json.dumps(dict(graded)), "t": at})

    def answers(self, attempt_id: str) -> dict[str, dict]:
        with self._e.connect() as c:
            rows = c.execute(text("SELECT * FROM answers WHERE attempt_id=:a"), {"a": attempt_id}).all()
        return {r.item_ref: {"answer": json.loads(r.answer_json), "explanation": r.explanation,
                             "graded": json.loads(r.graded_json), "submitted_at": r.submitted_at} for r in rows}

    def count_runs(self, attempt_id: str, item_ref: str) -> int:
        with self._e.connect() as c:
            return c.execute(text("SELECT COUNT(*) FROM runs WHERE attempt_id=:a AND item_ref=:r"),
                             {"a": attempt_id, "r": item_ref}).scalar_one()

    def add_run(self, attempt_id: str, item_ref: str, at: str) -> None:
        with self._e.begin() as c:
            c.execute(text("INSERT INTO runs(attempt_id,item_ref,at) VALUES(:a,:r,:t)"),
                      {"a": attempt_id, "r": item_ref, "t": at})
