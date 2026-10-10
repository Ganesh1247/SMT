"""Document stores: in-memory (tests) and stdlib sqlite3 (one file per module under DATA_DIR)."""
from __future__ import annotations

import json
import sqlite3
import threading


class InMemoryDocStore:
    def __init__(self):
        self._d: dict[str, dict[str, str]] = {}
        self._lock = threading.Lock()

    def put(self, collection, key, doc):
        with self._lock:
            self._d.setdefault(collection, {})[key] = json.dumps(doc)

    def put_if_absent(self, collection, key, doc):
        with self._lock:
            c = self._d.setdefault(collection, {})
            if key in c:
                return False
            c[key] = json.dumps(doc)
            return True

    def get(self, collection, key):
        with self._lock:
            v = self._d.get(collection, {}).get(key)
        return json.loads(v) if v is not None else None

    def all(self, collection):
        with self._lock:
            vals = list(self._d.get(collection, {}).values())
        return [json.loads(v) for v in vals]


class SqliteDocStore:
    def __init__(self, path: str):
        self._db = sqlite3.connect(path, check_same_thread=False)
        self._lock = threading.Lock()
        with self._lock:
            self._db.execute(
                "CREATE TABLE IF NOT EXISTS docs (collection TEXT NOT NULL, key TEXT NOT NULL, "
                "body TEXT NOT NULL, PRIMARY KEY (collection, key))")
            self._db.commit()

    def put(self, collection, key, doc):
        with self._lock:
            self._db.execute("INSERT OR REPLACE INTO docs VALUES (?, ?, ?)", (collection, key, json.dumps(doc)))
            self._db.commit()

    def put_if_absent(self, collection, key, doc):
        with self._lock:
            cur = self._db.execute("INSERT OR IGNORE INTO docs VALUES (?, ?, ?)", (collection, key, json.dumps(doc)))
            self._db.commit()
            return cur.rowcount == 1

    def get(self, collection, key):
        with self._lock:
            row = self._db.execute("SELECT body FROM docs WHERE collection=? AND key=?", (collection, key)).fetchone()
        return json.loads(row[0]) if row else None

    def all(self, collection):
        with self._lock:
            rows = self._db.execute("SELECT body FROM docs WHERE collection=?", (collection,)).fetchall()
        return [json.loads(r[0]) for r in rows]
