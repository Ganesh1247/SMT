"""SQLite repository for the integrity module (stdlib sqlite3; schema owned by this module only)."""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from ..domain import models as d

SCHEMA = [
    "CREATE TABLE IF NOT EXISTS attempts(attempt_id TEXT PRIMARY KEY, learner_id TEXT NOT NULL)",
    "CREATE TABLE IF NOT EXISTS consents(id INTEGER PRIMARY KEY AUTOINCREMENT, attempt_id TEXT NOT NULL,"
    " learner_id TEXT NOT NULL, version TEXT NOT NULL, scopes TEXT NOT NULL, recorded_at REAL NOT NULL)",
    "CREATE TABLE IF NOT EXISTS events(id INTEGER PRIMARY KEY AUTOINCREMENT, attempt_id TEXT NOT NULL,"
    " type TEXT NOT NULL, t_ms REAL NOT NULL, item_id TEXT, detail TEXT NOT NULL, received_at REAL NOT NULL)",
    "CREATE INDEX IF NOT EXISTS ix_events_attempt ON events(attempt_id, type)",
    "CREATE TABLE IF NOT EXISTS event_meta(attempt_id TEXT PRIMARY KEY, dropped INTEGER NOT NULL DEFAULT 0)",
    "CREATE TABLE IF NOT EXISTS chunks(attempt_id TEXT NOT NULL, stream TEXT NOT NULL, seq INTEGER NOT NULL,"
    " sha256 TEXT NOT NULL, size INTEGER NOT NULL, created_at REAL NOT NULL, PRIMARY KEY(attempt_id, stream, seq))",
    "CREATE TABLE IF NOT EXISTS manifests(attempt_id TEXT PRIMARY KEY, manifest_hash TEXT NOT NULL,"
    " chunks INTEGER NOT NULL, created_at REAL NOT NULL, purged_at REAL)",
    "CREATE TABLE IF NOT EXISTS fingerprints(attempt_id TEXT NOT NULL, task_id TEXT NOT NULL, hash TEXT NOT NULL,"
    " dataset_id TEXT, created_at REAL NOT NULL, UNIQUE(attempt_id, task_id, hash))",
    "CREATE INDEX IF NOT EXISTS ix_fp ON fingerprints(task_id, hash)",
    "CREATE TABLE IF NOT EXISTS flags(attempt_id TEXT NOT NULL, code TEXT NOT NULL, task_id TEXT NOT NULL,"
    " matched INTEGER NOT NULL, created_at REAL NOT NULL, UNIQUE(attempt_id, code, task_id))",
    "CREATE TABLE IF NOT EXISTS prechecks(id INTEGER PRIMARY KEY AUTOINCREMENT, learner_id TEXT NOT NULL,"
    " passed INTEGER NOT NULL, created_at REAL NOT NULL)",
]


class SqliteRepo:
    def __init__(self, path: Path):
        self._path = path
        path.parent.mkdir(parents=True, exist_ok=True)
        with self._conn() as c:
            for stmt in SCHEMA:
                c.execute(stmt)

    def _conn(self) -> sqlite3.Connection:
        c = sqlite3.connect(str(self._path), timeout=10)
        c.execute("PRAGMA foreign_keys=ON")
        return c

    # consent ---------------------------------------------------------
    def attempt_owner(self, attempt_id):
        with self._conn() as c:
            row = c.execute("SELECT learner_id FROM attempts WHERE attempt_id=?", (attempt_id,)).fetchone()
        return row[0] if row else None

    def save_consent(self, rec):
        with self._conn() as c:
            c.execute("INSERT OR IGNORE INTO attempts(attempt_id, learner_id) VALUES (?,?)",
                      (rec.attempt_id, rec.learner_id))
            c.execute("INSERT INTO consents(attempt_id, learner_id, version, scopes, recorded_at) VALUES (?,?,?,?,?)",
                      (rec.attempt_id, rec.learner_id, rec.version, json.dumps(list(rec.scopes)), rec.recorded_at))

    def latest_consent(self, attempt_id):
        with self._conn() as c:
            row = c.execute("SELECT learner_id, version, scopes, recorded_at FROM consents WHERE attempt_id=?"
                            " ORDER BY id DESC LIMIT 1", (attempt_id,)).fetchone()
        if not row:
            return None
        return d.ConsentRecord(attempt_id, row[0], row[1], tuple(json.loads(row[2])), row[3])

    # events ----------------------------------------------------------
    def add_events(self, attempt_id, events, cap, now):
        with self._conn() as c:
            have = c.execute("SELECT COUNT(*) FROM events WHERE attempt_id=?", (attempt_id,)).fetchone()[0]
            room = max(cap - have, 0)
            take = events[:room]
            c.executemany("INSERT INTO events(attempt_id, type, t_ms, item_id, detail, received_at) VALUES (?,?,?,?,?,?)",
                          [(attempt_id, e.type, e.t_ms, e.item_id, json.dumps(dict(e.detail), sort_keys=True), now)
                           for e in take])
            dropped = len(events) - len(take)
            if dropped:
                c.execute("INSERT INTO event_meta(attempt_id, dropped) VALUES (?,?) "
                          "ON CONFLICT(attempt_id) DO UPDATE SET dropped = dropped + excluded.dropped",
                          (attempt_id, dropped))
        return len(take), dropped

    def event_counts(self, attempt_id):
        with self._conn() as c:
            counts = dict(c.execute("SELECT type, COUNT(*) FROM events WHERE attempt_id=? GROUP BY type",
                                    (attempt_id,)).fetchall())
            row = c.execute("SELECT dropped FROM event_meta WHERE attempt_id=?", (attempt_id,)).fetchone()
        return counts, (row[0] if row else 0)

    # chunks ----------------------------------------------------------
    def chunk(self, attempt_id, stream, seq):
        with self._conn() as c:
            row = c.execute("SELECT sha256, size FROM chunks WHERE attempt_id=? AND stream=? AND seq=?",
                            (attempt_id, stream, seq)).fetchone()
        return (row[0], row[1]) if row else None

    def put_chunk(self, attempt_id, stream, seq, sha, size, now):
        with self._conn() as c:
            c.execute("INSERT INTO chunks VALUES (?,?,?,?,?,?)", (attempt_id, stream, seq, sha, size, now))

    def chunks(self, attempt_id):
        with self._conn() as c:
            return c.execute("SELECT stream, seq, sha256, size FROM chunks WHERE attempt_id=?"
                             " ORDER BY stream, seq", (attempt_id,)).fetchall()

    def manifest(self, attempt_id):
        with self._conn() as c:
            row = c.execute("SELECT manifest_hash, chunks FROM manifests WHERE attempt_id=?", (attempt_id,)).fetchone()
        return (row[0], row[1]) if row else None

    def save_manifest(self, attempt_id, manifest_hash, chunks, now):
        with self._conn() as c:
            c.execute("INSERT INTO manifests(attempt_id, manifest_hash, chunks, created_at) VALUES (?,?,?,?)",
                      (attempt_id, manifest_hash, chunks, now))

    # similarity ------------------------------------------------------
    def add_fingerprint(self, attempt_id, task_id, h, dataset_id, now):
        with self._conn() as c:
            c.execute("INSERT OR IGNORE INTO fingerprints VALUES (?,?,?,?,?)", (attempt_id, task_id, h, dataset_id, now))

    def matching_attempts(self, attempt_id, task_id, h, dataset_id):
        sql = (
            "SELECT DISTINCT f.attempt_id FROM fingerprints f LEFT JOIN attempts a ON a.attempt_id=f.attempt_id "
            "WHERE f.task_id=? AND f.hash=? AND f.attempt_id<>? "
            "AND COALESCE(a.learner_id,'') <> COALESCE((SELECT learner_id FROM attempts WHERE attempt_id=?),'<none>') "
            "AND (f.dataset_id IS NULL OR ? IS NULL OR f.dataset_id <> ?)")
        with self._conn() as c:
            return [r[0] for r in c.execute(sql, (task_id, h, attempt_id, attempt_id, dataset_id, dataset_id))]

    def add_flag(self, attempt_id, code, task_id, matched, now):
        with self._conn() as c:
            c.execute("INSERT INTO flags(attempt_id, code, task_id, matched, created_at) VALUES (?,?,?,?,?) "
                      "ON CONFLICT(attempt_id, code, task_id) DO UPDATE SET matched=excluded.matched",
                      (attempt_id, code, task_id, matched, now))

    def flags(self, attempt_id):
        with self._conn() as c:
            return c.execute("SELECT code, task_id, matched FROM flags WHERE attempt_id=? ORDER BY task_id",
                             (attempt_id,)).fetchall()

    # prechecks -------------------------------------------------------
    def save_precheck(self, learner_id, passed, now):
        with self._conn() as c:
            c.execute("INSERT INTO prechecks(learner_id, passed, created_at) VALUES (?,?,?)",
                      (learner_id, 1 if passed else 0, now))

    def latest_precheck(self, learner_id):
        with self._conn() as c:
            row = c.execute("SELECT passed FROM prechecks WHERE learner_id=? ORDER BY id DESC LIMIT 1",
                            (learner_id,)).fetchone()
        return bool(row and row[0])

    # retention -------------------------------------------------------
    def expired_attempts(self, before):
        with self._conn() as c:
            rows = c.execute(
                "SELECT ch.attempt_id FROM chunks ch GROUP BY ch.attempt_id HAVING MIN(ch.created_at) < ?", (before,)
            ).fetchall()
        return [r[0] for r in rows]

    def mark_purged(self, attempt_id, now):
        with self._conn() as c:
            c.execute("DELETE FROM chunks WHERE attempt_id=?", (attempt_id,))
            c.execute("UPDATE manifests SET purged_at=? WHERE attempt_id=?", (now, attempt_id))
