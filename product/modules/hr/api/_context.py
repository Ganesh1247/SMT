"""Composition state for the hr module."""
from __future__ import annotations

import hashlib
import os
import re
import uuid
from datetime import datetime, timezone

from ..application.service import HrService
from ..infrastructure.adapters import ReviewApiAdapter, SchemaContracts
from ..infrastructure.doc_store import InMemoryDocStore, SqliteDocStore

_ORG = re.compile(r"^org_[a-z0-9_]{3,40}$")


class _SystemClock:
    def now(self):
        return datetime.now(timezone.utc)


class _UuidIds:
    def new_id(self):
        return str(uuid.uuid4())


class Context:
    service: HrService | None = None
    identity = None


ctx = Context()


def configure(identity, evidence, review=None, clock=None, ids=None, store=None, data_dir: str | None = None,
              contracts=None) -> None:
    if store is None:
        if data_dir:
            os.makedirs(data_dir, exist_ok=True)
            store = SqliteDocStore(os.path.join(data_dir, "hr.sqlite3"))
        else:
            store = InMemoryDocStore()
    ctx.identity = identity
    ctx.service = HrService(store, review or ReviewApiAdapter(), evidence, clock or _SystemClock(),
                            ids or _UuidIds(), contracts or SchemaContracts())


def recipient_id(principal) -> str:
    """The recruiter organisation (`org_...`); derived from the user when identity supplies none."""
    if principal.org_id and _ORG.match(principal.org_id):
        return principal.org_id
    return "org_" + hashlib.sha256(principal.user_id.encode("utf-8")).hexdigest()[:12]
