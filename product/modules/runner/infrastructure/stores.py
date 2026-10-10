"""SQLite-backed runner-side task store (hidden tests live only here) and run log;
trusted-parent SQL evaluator; executor selector driven by explicit configuration."""
from __future__ import annotations

import json
import os
import sqlite3
import time
from pathlib import Path

from ..application.run_service import Executor
from .docker_executor import DockerExecutor
from .process_executor import ProcessFallbackExecutor


def data_dir() -> Path:
    return Path(os.environ.get("DATA_DIR") or "./data")


class SqliteStore:
    """One DB file for the runner: `tasks` (hidden specs) and `runs` (isolation_mode on every run)."""

    def __init__(self, path: Path | None = None):
        self._path = path or (data_dir() / "runner" / "runner.db")
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with self._conn() as c:
            c.execute("CREATE TABLE IF NOT EXISTS tasks(task_id TEXT PRIMARY KEY, kind TEXT NOT NULL, spec TEXT NOT NULL)")
            c.execute("CREATE TABLE IF NOT EXISTS runs(run_id TEXT NOT NULL, task_id TEXT NOT NULL, kind TEXT NOT NULL,"
                      " status TEXT NOT NULL, isolation_mode TEXT NOT NULL, reason TEXT NOT NULL,"
                      " duration_ms INTEGER NOT NULL, created_at REAL NOT NULL)")

    def _conn(self) -> sqlite3.Connection:
        return sqlite3.connect(str(self._path))

    # TaskStore
    def put(self, task_id: str, kind: str, spec: dict) -> None:
        with self._conn() as c:
            c.execute("INSERT OR REPLACE INTO tasks(task_id, kind, spec) VALUES (?,?,?)",
                      (task_id, kind, json.dumps(spec, sort_keys=True)))

    def get(self, task_id: str):
        with self._conn() as c:
            row = c.execute("SELECT kind, spec FROM tasks WHERE task_id=?", (task_id,)).fetchone()
        return (row[0], json.loads(row[1])) if row else None

    # RunLog
    def record(self, run_id, task_id, kind, status, isolation_mode, reason, duration_ms) -> None:
        with self._conn() as c:
            c.execute("INSERT INTO runs VALUES (?,?,?,?,?,?,?,?)",
                      (run_id, task_id, kind, status, isolation_mode, reason, duration_ms, time.time()))

    def runs(self) -> list[dict]:
        with self._conn() as c:
            rows = c.execute("SELECT run_id, task_id, kind, status, isolation_mode, reason FROM runs ORDER BY rowid").fetchall()
        return [dict(zip(("run_id", "task_id", "kind", "status", "isolation_mode", "reason"), r)) for r in rows]


class SqliteExpected:
    """Server-authored SQL evaluated in the trusted parent (never inside the child)."""

    def rows(self, setup_sql: str, query: str) -> list:
        conn = sqlite3.connect(":memory:")
        try:
            conn.executescript(setup_sql)
            out = []
            for row in conn.execute(query.strip()).fetchall():
                out.append([v.hex() if isinstance(v, bytes) else (None if isinstance(v, float) and v != v else v)
                            for v in row])
            return out
        finally:
            conn.close()


class ConfiguredSelector:
    """Docker first; process fallback only if RUNNER_ALLOW_FALLBACK=true; otherwise fail closed."""

    def __init__(self, docker: DockerExecutor | None = None, fallback: Executor | None = None):
        self._docker = docker or DockerExecutor()
        self._fallback = fallback or ProcessFallbackExecutor()

    def select(self) -> Executor | None:
        if self._docker.available():
            return self._docker
        if os.environ.get("RUNNER_ALLOW_FALLBACK", "").strip().lower() == "true":
            return self._fallback
        return None
