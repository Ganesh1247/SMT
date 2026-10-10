"""In-memory fakes for the review module's ports (wired by the entrypoint in production)."""
from __future__ import annotations

import hashlib
from datetime import datetime, timedelta, timezone

from review.application.ports import Principal

LRN_A = "lrn_0a1b2c3d4e5f6071"
LRN_B = "lrn_1111111111111111"


class FakeIdentity:
    """Header `x-test-user: <id>|<role>[|<org>]`."""

    def authenticate(self, cookies, headers):
        raw = headers.get("x-test-user")
        if not raw:
            return None
        parts = raw.split("|")
        return Principal(user_id=parts[0], role=parts[1], org_id=parts[2] if len(parts) > 2 else None)

    def alias_for(self, learner_id, recipient_id):
        return "cnd_" + hashlib.sha256(f"{learner_id}:{recipient_id}".encode()).hexdigest()[:16]


class FakeEvidence:
    def __init__(self):
        self.events: list[dict] = []
        self.fail_next = 0
        self.append_calls = 0

    def append(self, event):
        self.append_calls += 1
        if self.fail_next:
            self.fail_next -= 1
            raise RuntimeError("ledger down")
        for e in self.events:
            if e["idempotency_key"] == event["idempotency_key"]:
                return {"event_id": e["event_id"], "sequence": e["ledger"]["sequence"], "hash": e["ledger"]["hash"]}
        seq = len(self.events) + 1
        h = "sha256:" + hashlib.sha256(f"{seq}".encode()).hexdigest()
        stored = dict(event)
        stored["event_id"] = f"00000000-0000-4000-8000-{seq:012d}"
        stored["ledger"] = {"sequence": seq, "prev_hash": "genesis", "hash": h, "recorded_at": "2026-10-10T10:00:00Z"}
        self.events.append(stored)
        return {"event_id": stored["event_id"], "sequence": seq, "hash": h}

    def list_for_learner(self, learner_id):
        return [dict(e) for e in self.events if e["learner_id"] == learner_id]

    def head(self):
        if not self.events:
            return {"sequence": 0, "hash": "genesis"}
        e = self.events[-1]
        return {"sequence": e["ledger"]["sequence"], "hash": e["ledger"]["hash"]}

    def seed(self, learner_id, competency="cmp_python", **over):
        base = {
            "schema_version": "0.1", "idempotency_key": f"seed-{len(self.events)}-{learner_id}-xx",
            "source_system": "sandbox", "event_type": "criterion_result", "learner_id": learner_id,
            "competency_id": competency, "level": 1, "criterion_id": "crt_basics", "method": "deterministic_test",
            "outcome": "pass", "task_id": "tsk_l1_basics", "task_version": "1.0.0", "rubric_id": "rbr_python",
            "rubric_version": "1.0.0", "seed_id": "sd_9f8e7d6c5b4a", "submission_ref": "sha256:" + "b" * 64,
            "occurred_at": "2026-10-01T09:00:00Z",
        }
        base.update(over)
        return self.append({k: v for k, v in base.items() if v is not None})


class FakeScoring:
    def __init__(self):
        self.table: dict[tuple[str, str], dict] = {}

    def set(self, learner_id, competency, estimate=0.6, lower=0.45, upper=0.75):
        self.table[(learner_id, competency)] = {
            "estimate": estimate, "lower": lower, "upper": upper, "as_of": "2026-10-10T10:00:00Z"}

    def competency_estimate(self, learner_id, competency_id):
        return self.table.get((learner_id, competency_id))


class FakeIntegrity:
    def __init__(self):
        self.blob = bytes(range(256)) * 4  # 1024 bytes
        self.known = {("att_1", "camera"), ("att_1", "screen")}

    def summary(self, attempt_id):
        return {"risk": "medium", "counts": {"focus_loss": 3, "paste": 1}}

    def recording_info(self, attempt_id, stream):
        if (attempt_id, stream) not in self.known:
            return None
        return {"size": len(self.blob), "content_type": "video/webm"}

    def read_recording(self, attempt_id, stream, start, end):
        return self.blob[start:end + 1]


class FakeAssessment:
    def __init__(self):
        self.calls: list[tuple[str, dict]] = []

    def record_level4_result(self, attempt_id, result):
        self.calls.append((attempt_id, result))


class Clock:
    def __init__(self, now=None):
        self.t = now or datetime(2026, 10, 10, 10, 0, tzinfo=timezone.utc)

    def now(self):
        return self.t

    def advance(self, **kw):
        self.t += timedelta(**kw)


class Ids:
    def __init__(self):
        self.n = 0

    def new_id(self):
        self.n += 1
        return f"00000000-0000-4000-9000-{self.n:012d}"
