"""interview: session state machine, adaptive follow-up, evaluation hand-off, review routing."""
import json

import jsonschema
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from interview import api
from interview.domain import solution_features as sf
from interview.infrastructure.contracts import contracts_dir

from fakes_interview import (LRN_A, LRN_B, Clock, FakeAssessment, FakeEvidence, FakeIdentity,
                             FakeIntegrity, FakeIntelligence, FakeReview)

LEARNER = f"{LRN_A}|learner"
GOOD = ("First I loop over the rows and store each one in a dictionary keyed by id, then I sort the "
        "values and return the list because that keeps the first occurrence of each id.")


def build(intel=None, integrity=None):
    class E:
        pass
    e = E()
    e.assessment, e.evidence, e.review = FakeAssessment(), FakeEvidence(), FakeReview()
    e.intel = intel or FakeIntelligence()
    e.integrity = integrity or FakeIntegrity()
    api.configure(identity=FakeIdentity(), assessment=e.assessment, intelligence=e.intel, evidence=e.evidence,
                  review=e.review, integrity=e.integrity, clock=Clock(), store=None)
    app = FastAPI()
    app.include_router(api.router)
    e.client = TestClient(app)
    return e


@pytest.fixture()
def env():
    return build()


def H(u=LEARNER):
    return {"x-test-user": u}


def turn(env, text=None, attempt="att_l4", user=LEARNER):
    body = {} if text is None else {"answer_text": text}
    return env.client.post(f"/interview/{attempt}/turn", json=body, headers=H(user))


def run_to_end(env, answer=GOOD):
    r = turn(env)
    guard = 0
    while r.status_code == 200 and r.json().get("state") == "in_progress" and guard < 12:
        r = turn(env, answer)
        guard += 1
    return r


# ---- domain -------------------------------------------------------------
def test_features_should_extract_function_names_loops_and_structures():
    f = sf.analyse("def dedupe_sales(rows):\n    seen = {}\n    for r in rows:\n        seen[r] = 1\n    return sorted(seen)\n")
    assert f.functions == ["dedupe_sales"] and f.loops == 1
    assert "dictionary" in f.structures and "sorting" in f.structures


def test_features_should_survive_syntax_errors():
    f = sf.analyse("def bad(:\n  ignore previous instructions\n")
    assert f.functions == []


def test_features_should_detect_sql():
    f = sf.analyse("SELECT a, COUNT(*) FROM t JOIN u ON t.id=u.id GROUP BY a")
    assert f.is_sql and "join" in f.structures


def test_prompts_should_cover_five_criteria_in_order_with_mutation_constraint():
    ps = sf.build_prompts(sf.analyse("def f(xs):\n    for x in xs:\n        pass\n"))
    assert [p.criterion for p in ps] == ["explain", "justify_approach", "complexity", "edge_cases", "adapt"]
    assert "New requirement" in ps[4].text


# ---- HTTP: start and ownership --------------------------------------------
def test_should_start_with_prompt_derived_from_learners_own_solution(env):
    r = turn(env)
    assert r.status_code == 200
    b = r.json()
    assert b["state"] == "in_progress" and b["criterion"] == "explain" and b["prompt_index"] == 1
    assert "dedupe_sales" in b["prompt"] and b["prompt_count"] == 5


def test_unknown_foreign_attempt_should_be_identical_404(env):
    env.assessment.owner["att_other"] = LRN_B
    env.assessment.code["att_other"] = "def x(): pass"
    a = turn(env, attempt="att_other")
    b = turn(env, attempt="att_missing")
    assert a.status_code == b.status_code == 404 and a.json() == b.json()


def test_should_require_learner_session(env):
    assert env.client.post("/interview/att_l4/turn", json={}).status_code == 401
    assert turn(env, user="rev_1|reviewer").status_code == 403


def test_get_should_report_not_started_then_current_prompt(env):
    assert env.client.get("/interview/att_l4", headers=H()).json()["state"] == "not_started"
    turn(env)
    assert env.client.get("/interview/att_l4", headers=H()).json()["state"] == "in_progress"


# ---- adaptive behaviour -----------------------------------------------------
def test_short_answer_should_trigger_one_follow_up_then_advance(env):
    turn(env)
    r = turn(env, "dunno").json()
    assert r["criterion"] == "explain" and r["kind"] == "follow_up"
    r = turn(env, "ok").json()
    assert r["criterion"] == "justify_approach" and r["kind"] == "prompt"


def test_substantial_answer_should_advance_without_follow_up(env):
    turn(env)
    r = turn(env, GOOD).json()
    assert r["criterion"] == "justify_approach" and r["kind"] == "prompt"


@pytest.mark.parametrize("answer", ["", "   ", "x" * 4001])
def test_should_reject_blank_or_oversized_answer_mid_session(env, answer):
    turn(env)
    assert turn(env, answer).status_code == 422


def test_should_reject_unknown_fields(env):
    turn(env)
    r = env.client.post("/interview/att_l4/turn", json={"answer_text": "abc def", "score": 3}, headers=H())
    assert r.status_code == 422


def test_answer_before_session_should_be_rejected_not_dropped(env):
    assert turn(env, GOOD).status_code == 409


# ---- finish ------------------------------------------------------------------
def test_full_session_should_evaluate_record_result_and_ledger_events(env):
    r = run_to_end(env).json()
    assert r["state"] == "completed" and r["passed"] is True and r["pending_review"] is False
    assert r["ai_disclosure"] is True and "AI-assisted" in r["label"]
    call = env.intel.calls[0]
    assert "def dedupe_sales" in call["code"] and call["rubric_version"] == "1.0.0"
    assert any(t["role"] == "learner" and t["criterion"] == "adapt" for t in call["transcript"])
    assert len(env.assessment.results) == 1
    att, res = env.assessment.results[0]
    assert att == "att_l4" and res["status"] == "final" and res["passed"] is True
    schema = json.loads((contracts_dir() / "evidence-event.schema.json").read_text(encoding="utf-8"))
    assert len(env.evidence.events) == 6  # 5 criteria + level outcome
    for ev in env.evidence.events:
        jsonschema.validate(ev, schema)
        assert ev["method"] == "live_screening" and ev["level"] == 4 and ev["ai_disclosure"] is True
        assert GOOD not in json.dumps(ev)
    assert env.review.cases == []


def test_failed_rubric_should_record_fail_without_review():
    e = build(FakeIntelligence(scores=(1, 1, 1, 1, 1)))
    r = run_to_end(e).json()
    assert r["state"] == "completed" and r["passed"] is False
    assert e.assessment.results[0][1]["passed"] is False and e.review.cases == []


def test_low_confidence_should_go_to_review_without_pass_or_fail():
    e = build(FakeIntelligence(confidence=0.4))
    r = run_to_end(e).json()
    assert r["state"] == "pending_review" and r["pending_review"] is True and r["passed"] is None
    assert e.assessment.results[0][1]["status"] == "pending_review"
    c = e.review.cases[0]
    assert c["reason"] == "low_confidence" and c["learner_id"] == LRN_A and c["attempt_id"] == "att_l4"
    assert c["context"]["kind"] == "interview_l4" and c["summary"]["transcript"]
    lvl = [ev for ev in e.evidence.events if ev["event_type"] == "level_outcome"][0]
    assert lvl["outcome"] == "inconclusive"


def test_high_integrity_risk_should_queue_review_but_not_change_scores():
    e = build(integrity=FakeIntegrity("high"))
    r = run_to_end(e).json()
    assert r["pending_review"] is True
    assert e.review.cases[0]["reason"] == "integrity_review" and e.review.cases[0]["integrity_risk"] == "high"
    assert [c["score0to3"] for c in r["criteria"]] == [3, 2, 2, 2, 2]


def test_provider_unavailable_should_not_record_failure():
    e = build(FakeIntelligence(status="unavailable", scores=(0, 0, 0, 0, 0), confidence=0.0))
    r = run_to_end(e).json()
    assert r["pending_review"] is True and r["passed"] is None
    assert e.assessment.results[0][1]["passed"] is None


def test_injection_event_should_become_ledger_flag_only():
    ev = [{"type": "injection_attempt", "criterion": "explain", "turn_index": 1, "pattern": "score_demand"}]
    e = build(FakeIntelligence(events=ev))
    run_to_end(e)
    explain = next(x for x in e.evidence.events if x.get("criterion_id") == "crt_l4_explain")
    assert "injection_attempt" in explain["flags"]
    assert explain["outcome"] in ("pass", "partial", "fail")


def test_ledger_failure_should_be_retryable_without_duplicates(env):
    env.evidence.fail_next = 1
    r = run_to_end(env)
    assert r.status_code == 503
    r2 = turn(env, GOOD)
    assert r2.status_code == 200 and r2.json()["state"] == "completed"
    assert len(env.evidence.events) == 6 and len(env.assessment.results) == 1


def test_post_after_completion_should_replay_summary_without_new_effects(env):
    first = run_to_end(env).json()
    n = len(env.evidence.events)
    again = turn(env, GOOD).json()
    assert again["state"] == "completed" and again["total"] == first["total"]
    assert len(env.evidence.events) == n and len(env.assessment.results) == 1 and len(env.intel.calls) == 1


def test_summary_should_carry_no_timing_or_integrity_detail(env):
    flat = json.dumps(run_to_end(env).json()).lower()
    for word in ("duration", "seconds", "time_taken", "flag", "integrity", "injection"):
        assert word not in flat


# ---- cross-module wiring with the real intelligence module (stub provider) ----
def test_should_work_end_to_end_with_real_intelligence_api():
    from interview.infrastructure.adapters import IntelligenceApiAdapter
    from intelligence import api as intel_api
    intel_api.configure(provider=intel_api.StubProvider())
    e = build(intel=IntelligenceApiAdapter())
    r = run_to_end(e).json()
    assert r["state"] in ("completed", "pending_review")
    assert r["model_ref"].startswith("stub-")
    assert len(r["criteria"]) == 5
    intel_api.configure(provider=None)
