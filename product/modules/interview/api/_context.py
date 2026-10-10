"""Composition state for the interview module."""
from __future__ import annotations

import hashlib
import os
import re
from datetime import datetime, timezone

from ..application.service import InterviewService
from ..infrastructure.adapters import IntelligenceApiAdapter, ReviewApiAdapter
from ..infrastructure.doc_store import InMemoryDocStore, SqliteDocStore

_LRN = re.compile(r"^lrn_[a-f0-9]{16}$")


class _SystemClock:
    def now(self):
        return datetime.now(timezone.utc)


class Context:
    service: InterviewService | None = None
    identity = None


ctx = Context()


def configure(identity, assessment, evidence, intelligence=None, review=None, integrity=None, clock=None,
              store=None, data_dir: str | None = None) -> None:
    if store is None:
        if data_dir:
            os.makedirs(data_dir, exist_ok=True)
            store = SqliteDocStore(os.path.join(data_dir, "interview.sqlite3"))
        else:
            store = InMemoryDocStore()
    ctx.identity = identity
    ctx.service = InterviewService(store, assessment, intelligence or IntelligenceApiAdapter(), evidence,
                                   review or ReviewApiAdapter(), integrity, clock or _SystemClock())


def learner_ref(user_id: str) -> str:
    """Canonical `lrn_<16 hex>`: pass-through when canonical, else a stable derived reference."""
    if _LRN.match(user_id):
        return user_id
    return "lrn_" + hashlib.sha256(user_id.encode("utf-8")).hexdigest()[:16]
