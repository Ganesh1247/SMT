"""Hand-off from a low-confidence L4 session into the real review module, then a reviewer decision."""
from fastapi import FastAPI
from fastapi.testclient import TestClient

from interview import api as interview_api
from review import api as review_api

from fakes_interview import (LRN_A, Clock, FakeAssessment, FakeEvidence, FakeIdentity, FakeIntegrity,
                             FakeIntelligence)


class _Ident:
    def authenticate(self, cookies, headers):
        raw = headers.get("x-test-user")
        if not raw:
            return None
        uid, role = raw.split("|")
        return review_api.Principal(user_id=uid, role=role)

    def alias_for(self, learner_id, recipient_id):
        return "cnd_" + "0" * 16


class _Ledger(FakeEvidence):
    def list_for_learner(self, learner_id):
        return []

    def head(self):
        return {"sequence": 0, "hash": "genesis"}


def test_low_confidence_session_should_reach_reviewer_and_settle_level_four():
    assessment, ledger = FakeAssessment(), _Ledger()
    review_api.configure(identity=_Ident(), evidence=ledger, scoring=object(), integrity=FakeIntegrity(),
                         assessment=assessment)
    interview_api.configure(identity=FakeIdentity(), assessment=assessment, intelligence=FakeIntelligence(confidence=0.3),
                            evidence=ledger, integrity=FakeIntegrity(), clock=Clock(), store=None)  # default review adapter
    app = FastAPI()
    app.include_router(interview_api.router)
    app.include_router(review_api.router)
    c = TestClient(app)
    learner = {"x-test-user": f"{LRN_A}|learner"}
    r = c.post("/interview/att_l4/turn", json={}, headers=learner)
    for _ in range(12):
        if r.json().get("state") != "in_progress":
            break
        r = c.post("/interview/att_l4/turn", json={"answer_text": "I loop over the rows and store them in a dictionary."},
                   headers=learner)
    assert r.json()["state"] == "pending_review"
    rev = {"x-test-user": "rev_1|reviewer"}
    cases = c.get("/review/queue", headers=rev).json()["cases"]
    assert len(cases) == 1 and cases[0]["reason"] == "low_confidence"
    d = c.post(f"/review/cases/{cases[0]['case_id']}/decision",
               json={"outcome": "change", "new_outcome": "pass", "reason": "Rubric met on re-read of the transcript."},
               headers=rev)
    assert d.status_code == 201
    final = assessment.results[-1][1]
    assert final["status"] == "final" and final["passed"] is True and final["source"] == "human_review"
