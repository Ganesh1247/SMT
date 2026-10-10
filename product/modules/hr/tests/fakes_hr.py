"""Fakes for the hr module's ports."""
from __future__ import annotations

import base64
from datetime import datetime, timezone

from hr.application.ports import Principal

NOW = datetime(2026, 10, 10, 10, 0, tzinfo=timezone.utc)
H64 = "sha256:" + "a" * 64
H64B = "sha256:" + "b" * 64
ALIAS_1 = "cnd_" + "1" * 16
ALIAS_2 = "cnd_" + "2" * 16


class FakeIdentity:
    def authenticate(self, cookies, headers):
        raw = headers.get("x-test-user")
        if not raw:
            return None
        p = raw.split("|")
        return Principal(user_id=p[0], role=p[1], org_id=p[2] if len(p) > 2 else None)


class Clock:
    def now(self):
        return NOW


class Ids:
    def __init__(self):
        self.n = 0

    def new_id(self):
        self.n += 1
        return f"00000000-0000-4000-9000-{self.n:012d}"


def shared(alias=ALIAS_1, competency="cmp_python", levels=(1, 2, 3), lower=0.5, understanding="confirmed",
           last="2026-09-20T09:00:00Z", methods=("deterministic_test",), receipt=H64):
    counts = {m: 0 for m in ("deterministic_test", "probe", "ai_judged", "live_screening", "human_review")}
    items = []
    for i, m in enumerate(methods):
        counts[m] += 1
        items.append({"event_id": f"00000000-0000-4000-8000-{i + 1:012d}", "method": m, "outcome": "pass",
                      "occurred_at": last, "task_version": "1.0.0", "rubric_version": "1.0.0",
                      "receipt_hash": receipt})
    return {
        "schema_version": "0.1", "candidate_ref": alias, "grant_id": "00000000-0000-4000-8000-0000000000aa",
        "competency_id": competency,
        "proficiency": {"estimate": 0.6, "lower": lower, "upper": 0.75, "scale": "0-1", "as_of": "2026-10-10T10:00:00Z"},
        "levels_passed": list(levels), "method_counts": counts, "understanding_status": understanding,
        "evidence_items": items, "last_evidence_at": last, "ledger_proof": {"head_hash": H64, "head_sequence": 9},
        "labels": {"experimental": True, "ai_used": False},
    }


class FakeReview:
    def __init__(self):
        self.docs: list[dict] = []
        self.requests: list[dict] = []
        self.callers: list[str] = []
        self.pages = False

    def query_shared_evidence(self, request, caller_recipient_id):
        self.requests.append(request)
        self.callers.append(caller_recipient_id)
        wanted = set(request["competency_ids"])
        refs = set(request.get("candidate_refs", []))
        out = [d for d in self.docs if d["competency_id"] in wanted and (not refs or d["candidate_ref"] in refs)]
        out.sort(key=lambda d: (d["candidate_ref"], d["competency_id"]))
        limit = request.get("page", {}).get("limit", 25)
        if self.pages:
            limit = 1
        cursor = request.get("page", {}).get("cursor")
        start = int(base64.urlsafe_b64decode(cursor.encode()).decode()) if cursor else 0
        window = out[start:start + limit]
        nxt = base64.urlsafe_b64encode(str(start + limit).encode()).decode() if start + limit < len(out) else None
        return {"schema_version": "0.1", "request_id": request["request_id"], "recipient_id": request["recipient_id"],
                "as_of": "2026-10-10T10:00:00Z", "results": window,
                "page": {"returned": len(window), "next_cursor": nxt},
                "ledger_head": {"sequence": 9, "hash": H64}}


class FakeEvidence:
    def __init__(self, status="match"):
        self.status = status
        self.fail = False

    def verify_receipt(self, receipt_hash):
        if self.fail:
            raise RuntimeError("down")
        return {"status": self.status, "sequence": 214}
