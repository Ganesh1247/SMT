"""Composition state for the review module (set once by the entrypoint via api.configure)."""
from __future__ import annotations

import hashlib
import os
import re
import uuid
from datetime import datetime, timezone

from ..application.service import ReviewService
from ..infrastructure.contracts import is_valid
from ..infrastructure.doc_store import InMemoryDocStore, SqliteDocStore

_LRN = re.compile(r"^lrn_[a-f0-9]{16}$")


class _SystemClock:
    def now(self):
        return datetime.now(timezone.utc)


class _UuidIds:
    def new_id(self):
        return str(uuid.uuid4())


class _Contracts:
    def is_valid(self, name, doc):
        return is_valid(name, doc)


class Context:
    service: ReviewService | None = None
    identity = None


ctx = Context()


def configure(identity, evidence, scoring, integrity, assessment, clock=None, ids=None, store=None,
              data_dir: str | None = None, contracts=None) -> None:
    if store is None:
        if data_dir:
            os.makedirs(data_dir, exist_ok=True)
            store = SqliteDocStore(os.path.join(data_dir, "review.sqlite3"))
        else:
            store = InMemoryDocStore()
    ctx.identity = identity
    ctx.service = ReviewService(store, identity, evidence, scoring, integrity, assessment,
                                clock or _SystemClock(), ids or _UuidIds(), contracts or _Contracts())


def learner_ref(user_id: str) -> str:
    """Canonical `lrn_<16 hex>` reference: pass-through when already canonical, else derived."""
    if _LRN.match(user_id):
        return user_id
    return "lrn_" + hashlib.sha256(user_id.encode("utf-8")).hexdigest()[:16]
