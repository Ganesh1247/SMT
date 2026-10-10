"""In-memory fakes for the interview module's ports."""
from __future__ import annotations

from datetime import datetime, timezone

from interview.application.ports import Principal

LRN_A = "lrn_0a1b2c3d4e5f6071"
LRN_B = "lrn_1111111111111111"

L3_CODE = """
def dedupe_sales(rows):
    seen = {}
    for row in rows:
        key = row["id"]
        if key not in seen:
            seen[key] = row
    return sorted(seen.values(), key=lambda r: r["id"])
"""


class FakeIdentity:
    def authenticate(self, cookies, headers):
        raw = headers.get("x-test-user")
        if not raw:
            return None
        uid, role = raw.split("|")
        return Principal(user_id=uid, role=role)


class FakeAssessment:
    def __init__(self):
        self.owner = {"att_l4": LRN_A}
        self.code = {"att_l4": L3_CODE}
        self.results: list[tuple[str, dict]] = []

    def l3_solution(self, attempt_id, learner_id):
        if self.owner.get(attempt_id) != learner_id:
            return None
        return {"code": self.code[attempt_id], "competency_id": "cmp_python", "task_id": "tsk_sales_dedupe",
                "task_version": "1.0.0", "seed_id": "sd_9f8e7d6c5b4a"}

    def record_level4_result(self, attempt_id, result):
        self.results.append((attempt_id, result))


class FakeEvidence:
    def __init__(self):
        self.events: list[dict] = []
        self.fail_next = 0

    def append(self, event):
        if self.fail_next:
            self.fail_next -= 1
            raise RuntimeError("ledger down")
        for e in self.events:
            if e["idempotency_key"] == event["idempotency_key"]:
                return {"sequence": 1}
        self.events.append(dict(event))
        return {"sequence": len(self.events)}


class FakeReview:
    def __init__(self):
        self.cases: list[dict] = []

    def enqueue_case(self, **kw):
        self.cases.append(kw)
        return f"case_{len(self.cases)}"


class FakeIntegrity:
    def __init__(self, risk="low"):
        self.risk = risk

    def summary(self, attempt_id):
        return {"risk": self.risk}


class FakeIntelligence:
    """Returns canned evaluations; records what it was sent."""

    def __init__(self, scores=(3, 2, 2, 2, 2), confidence=0.8, status="evaluated", events=()):
        self.scores, self.confidence, self.status, self.events = scores, confidence, status, list(events)
        self.calls: list[dict] = []

    def evaluate_interview(self, transcript, solution_code, rubric_version):
        self.calls.append({"transcript": transcript, "code": solution_code, "rubric_version": rubric_version})
        crit = ["explain", "justify_approach", "complexity", "edge_cases", "adapt"]
        criteria = [{"criterion": c, "score0to3": s, "rationale": "r", "confidence": self.confidence,
                     "evidence_quotes": []} for c, s in zip(crit, self.scores)]
        total = sum(self.scores)
        return {"criteria": criteria, "total": total, "passed": total >= 10 and min(self.scores) > 0,
                "needs_human_review": self.confidence < 0.6 or self.status != "evaluated",
                "model_ref": "stub-test", "ai_disclosure": True, "status": self.status,
                "rubric_version": rubric_version, "events": self.events}


class Clock:
    def __init__(self):
        self.t = datetime(2026, 10, 10, 10, 0, tzinfo=timezone.utc)

    def now(self):
        return self.t
