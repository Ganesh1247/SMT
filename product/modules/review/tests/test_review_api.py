"""review.api behaviour + contract tests (grants, queue, decisions, appeals, recording, shared-evidence query)."""
import json
import pathlib

import jsonschema
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from review import api
from review.infrastructure.contracts import contracts_dir

from fakes_review import (LRN_A, LRN_B, Clock, FakeAssessment, FakeEvidence, FakeIdentity,
                          FakeIntegrity, FakeScoring, Ids)

LEARNER = f"{LRN_A}|learner"
OTHER = f"{LRN_B}|learner"
REVIEWER = "rev_0001|reviewer"
RECRUITER = "rec_0001|recruiter|org_demo_recruiter"
RECRUITER2 = "rec_0002|recruiter|org_other_firm"


@pytest.fixture()
def env():
    class E:
        pass
    e = E()
    e.identity, e.evidence, e.scoring = FakeIdentity(), FakeEvidence(), FakeScoring()
    e.integrity, e.assessment, e.clock, e.ids = FakeIntegrity(), FakeAssessment(), Clock(), Ids()
    api.configure(identity=e.identity, evidence=e.evidence, scoring=e.scoring, integrity=e.integrity,
                  assessment=e.assessment, clock=e.clock, ids=e.ids, store=None)
    app = FastAPI()
    app.include_router(api.router)
    e.client = TestClient(app)
    return e


def H(user):
    return {"x-test-user": user}


def grant_body(**over):
    b = {"recipient_id": "org_demo_recruiter", "competencies": ["cmp_python"],
         "expires_at": "2026-11-10T10:00:00Z", "consent_text_version": "1.0"}
    b.update(over)
    return b


def make_case(env, **over):
    args = dict(attempt_id="att_1", learner_id=LRN_A, reason="low_confidence", uncertainty=0.7,
                integrity_risk="low",
                summary={"criteria": [{"criterion": "explain", "score0to3": 2, "confidence": 0.4}], "passed": True},
                context={"competency_id": "cmp_python", "level": 4, "task_id": "tsk_l4_interview",
                         "task_version": "1.0.0", "rubric_id": "rbr_l4_interview", "rubric_version": "1.0.0",
                         "seed_id": "sd_9f8e7d6c5b4a", "kind": "interview_l4", "original_outcome": "pass"})
    args.update(over)
    return api.enqueue_case(**args)


def _schema(name):
    return json.loads((contracts_dir() / name).read_text(encoding="utf-8"))


# ---------------- grants ----------------
def test_should_create_grant_valid_against_contract_with_raw_submission_off(env):
    r = env.client.post("/me/grants", json=grant_body(), headers=H(LEARNER))
    assert r.status_code == 201
    g = r.json()
    assert "raw_submission" not in g["scope"]["include"]
    assert g["expires_at"] and g["status"] == "active"
    doc = {k: v for k, v in g.items() if k not in ("grant_id", "status")}
    jsonschema.validate(doc, _schema("share-grant.schema.json"))


def test_should_require_expiry_on_grant(env):
    b = grant_body()
    del b["expires_at"]
    assert env.client.post("/me/grants", json=b, headers=H(LEARNER)).status_code == 422


@pytest.mark.parametrize("exp", ["2026-10-09T10:00:00Z", "2028-01-01T00:00:00Z", "2026-11-10T10:00:00"])
def test_should_reject_past_overlong_or_naive_expiry(env, exp):
    r = env.client.post("/me/grants", json=grant_body(expires_at=exp), headers=H(LEARNER))
    assert r.status_code == 422


def test_should_include_raw_submission_only_when_explicitly_selected(env):
    scope = {"include": ["estimate_band", "method_labels", "understanding_status", "evidence_summary", "raw_submission"]}
    r = env.client.post("/me/grants", json=grant_body(scope=scope), headers=H(LEARNER))
    assert r.status_code == 201 and "raw_submission" in r.json()["scope"]["include"]


def test_should_reject_scope_missing_core_items(env):
    r = env.client.post("/me/grants", json=grant_body(scope={"include": ["estimate_band"]}), headers=H(LEARNER))
    assert r.status_code == 422


def test_should_reject_unknown_fields_and_bad_ids(env):
    assert env.client.post("/me/grants", json=grant_body(extra=1), headers=H(LEARNER)).status_code == 422
    assert env.client.post("/me/grants", json=grant_body(recipient_id="Bad Org"), headers=H(LEARNER)).status_code == 422


def test_should_deny_grant_creation_for_non_learner_and_anonymous(env):
    assert env.client.post("/me/grants", json=grant_body(), headers=H(RECRUITER)).status_code == 403
    assert env.client.post("/me/grants", json=grant_body()).status_code == 401


def test_should_revoke_own_grant_and_hide_foreign_or_unknown_identically(env):
    gid = env.client.post("/me/grants", json=grant_body(), headers=H(LEARNER)).json()["grant_id"]
    foreign = env.client.delete(f"/me/grants/{gid}", headers=H(OTHER))
    unknown = env.client.delete("/me/grants/00000000-0000-4000-8000-0000000000ff", headers=H(OTHER))
    assert foreign.status_code == unknown.status_code == 404
    assert foreign.json() == unknown.json()
    assert env.client.delete(f"/me/grants/{gid}", headers=H(LEARNER)).status_code == 204
    listed = env.client.get("/me/grants", headers=H(LEARNER)).json()["grants"]
    assert listed[0]["status"] == "revoked"


# ---------------- shared evidence query ----------------
def _query(env, **over):
    body = {"schema_version": "0.1", "request_id": "11111111-1111-4111-8111-111111111111",
            "recipient_id": "org_demo_recruiter", "role_id": "role_junior_python", "role_version": 1,
            "competency_ids": ["cmp_python"]}
    body.update(over)
    return api.query_shared_evidence(body, caller_recipient_id=body["recipient_id"])


def _shared_setup(env, **grant):
    env.evidence.seed(LRN_A, level=1)
    env.evidence.seed(LRN_A, event_type="level_outcome", criterion_id=None, level=1, outcome="pass",
                      submission_ref=None, idempotency_key="lvl-1-lrn-a-xxxxxxxx")
    env.evidence.seed(LRN_A, event_type="probe_result", method="probe", understanding_status="unconfirmed",
                      idempotency_key="probe-lrn-a-xxxxxxxxxxx")
    env.evidence.seed(LRN_A, event_type="integrity_flag", flags=["cross_seed_match"], outcome="inconclusive",
                      idempotency_key="flag-lrn-a-xxxxxxxxxxxx")
    env.scoring.set(LRN_A, "cmp_python")
    body = grant_body(**grant)
    return env.client.post("/me/grants", json=body, headers=H(LEARNER)).json()["grant_id"]


def test_should_return_nothing_when_no_grant_and_same_as_unknown_candidate(env):
    env.evidence.seed(LRN_A)
    env.scoring.set(LRN_A, "cmp_python")
    no_grant = _query(env)
    unknown = _query(env, candidate_refs=["cnd_ffffffffffffffff"])
    assert no_grant["results"] == [] and unknown["results"] == []
    assert no_grant["page"] == unknown["page"]
    jsonschema.validate(no_grant, _schema("shared-evidence-query-response.schema.json"),
                        registry=_registry(), format_checker=None)


def _registry():
    from review.infrastructure.contracts import registry
    return registry()


def test_should_return_contract_valid_evidence_for_active_grant_without_aggregates(env):
    _shared_setup(env)
    out = _query(env)
    jsonschema.Draft202012Validator(_schema("shared-evidence-query-response.schema.json"),
                                    registry=_registry()).validate(out)
    assert len(out["results"]) == 1
    res = out["results"][0]
    assert res["levels_passed"] == [1]
    assert res["understanding_status"] == "unconfirmed"
    assert res["labels"]["experimental"] is True
    methods = {i["method"] for i in res["evidence_items"]}
    assert "deterministic_test" in methods
    assert all(i["outcome"] != "inconclusive" or i["method"] != "integrity" for i in res["evidence_items"])
    flat = json.dumps(out)
    for forbidden in ("overall_score", "rank", "total", "omitted", LRN_A, "flags", "cross_seed_match"):
        assert forbidden not in flat


def test_alias_should_differ_per_recipient(env):
    _shared_setup(env)
    env.client.post("/me/grants", json=grant_body(recipient_id="org_other_firm"), headers=H(LEARNER))
    a = _query(env)["results"][0]["candidate_ref"]
    b = _query(env, recipient_id="org_other_firm")["results"][0]["candidate_ref"]
    assert a != b


def test_should_exclude_revoked_and_expired_grants(env):
    gid = _shared_setup(env)
    assert len(_query(env)["results"]) == 1
    env.client.delete(f"/me/grants/{gid}", headers=H(LEARNER))
    assert _query(env)["results"] == []
    gid2 = env.client.post("/me/grants", json=grant_body(), headers=H(LEARNER)).json()["grant_id"]
    assert gid2 and len(_query(env)["results"]) == 1
    env.clock.advance(days=40)
    assert _query(env)["results"] == []


def test_should_limit_to_granted_role_and_competency(env):
    _shared_setup(env, role_ref="role_other_role")
    assert _query(env)["results"] == []
    assert _query(env, role_id="role_other_role")["results"] != []
    env.scoring.set(LRN_A, "cmp_sql")
    assert _query(env, role_id="role_other_role", competency_ids=["cmp_sql"])["results"] == []


def test_should_omit_competency_without_estimate(env):
    _shared_setup(env)
    env.scoring.table.clear()
    assert _query(env)["results"] == []


def test_should_reject_recipient_mismatch_and_invalid_request(env):
    with pytest.raises(api.QueryError) as e:
        api.query_shared_evidence({"schema_version": "0.1", "request_id": "11111111-1111-4111-8111-111111111111",
                                   "recipient_id": "org_demo_recruiter", "role_id": "role_abc", "role_version": 1,
                                   "competency_ids": ["cmp_python"]}, caller_recipient_id="org_other_firm")
    assert e.value.code == "recipient_mismatch"
    with pytest.raises(api.QueryError):
        _query(env, min_estimate_lower=0.5)  # thresholds must never reach Trust (invariant 14)


def test_should_page_without_revealing_totals(env):
    for i in range(3):
        lid = f"lrn_{i:016x}"
        env.evidence.seed(lid)
        env.scoring.set(lid, "cmp_python")
        env.client.post("/me/grants", json=grant_body(), headers={"x-test-user": f"{lid}|learner"})
    p1 = _query(env, page={"limit": 2})
    assert p1["page"]["returned"] == 2 and p1["page"]["next_cursor"]
    p2 = _query(env, page={"limit": 2, "cursor": p1["page"]["next_cursor"]})
    assert p2["page"]["returned"] == 1 and p2["page"]["next_cursor"] is None
    refs = [r["candidate_ref"] for r in p1["results"] + p2["results"]]
    assert refs == sorted(refs)


# ---------------- queue and decisions ----------------
def test_queue_should_order_by_uncertainty_then_integrity_risk(env):
    a = make_case(env, attempt_id="att_a", uncertainty=0.5, integrity_risk="high")
    b = make_case(env, attempt_id="att_b", uncertainty=0.9, integrity_risk="low")
    c = make_case(env, attempt_id="att_c", uncertainty=0.5, integrity_risk="low")
    items = env.client.get("/review/queue", headers=H(REVIEWER)).json()["cases"]
    assert [i["case_id"] for i in items] == [b, a, c]
    assert "learner_id" not in json.dumps(items) and LRN_A not in json.dumps(items)


def test_queue_should_be_reviewer_only(env):
    assert env.client.get("/review/queue", headers=H(LEARNER)).status_code == 403
    assert env.client.get("/review/queue", headers=H(RECRUITER)).status_code == 403
    assert env.client.get("/review/queue").status_code == 401


def test_enqueue_should_be_idempotent_per_attempt_and_reason(env):
    assert make_case(env) == make_case(env)


def test_case_detail_should_show_integrity_summary_and_hide_identity(env):
    cid = make_case(env)
    d = env.client.get(f"/review/cases/{cid}", headers=H(REVIEWER)).json()
    assert d["integrity"]["risk"] == "medium"
    assert set(d["recordings"]) == {"camera", "screen"}
    assert LRN_A not in json.dumps(d)
    assert env.client.get("/review/cases/nope", headers=H(REVIEWER)).status_code == 404


def test_decision_should_append_ledger_event_and_notify_assessment(env):
    cid = make_case(env)
    r = env.client.post(f"/review/cases/{cid}/decision",
                        json={"outcome": "change", "new_outcome": "fail", "reason": "Complexity answer lacks a bound."},
                        headers=H(REVIEWER))
    assert r.status_code == 201 and r.json()["ledger_entry"] >= 1
    ev = env.evidence.events[-1]
    jsonschema.validate({k: v for k, v in ev.items() if k not in ("event_id", "ledger")},
                        _schema("evidence-event.schema.json"))
    assert ev["event_type"] == "review_decision" and ev["method"] == "human_review" and ev["outcome"] == "fail"
    assert env.assessment.calls[-1][0] == "att_1" and env.assessment.calls[-1][1]["passed"] is False


def test_uphold_should_keep_original_outcome(env):
    cid = make_case(env)
    env.client.post(f"/review/cases/{cid}/decision", json={"outcome": "uphold", "reason": "Rubric criteria met."},
                    headers=H(REVIEWER))
    assert env.evidence.events[-1]["outcome"] == "pass"


def test_needs_more_info_should_not_touch_assessment(env):
    cid = make_case(env)
    r = env.client.post(f"/review/cases/{cid}/decision", json={"outcome": "needs_more_info", "reason": "Need transcript."},
                        headers=H(REVIEWER))
    assert r.status_code == 201 and env.assessment.calls == []


def test_second_decision_should_conflict_without_new_ledger_event(env):
    cid = make_case(env)
    body = {"outcome": "uphold", "reason": "Rubric criteria met."}
    env.client.post(f"/review/cases/{cid}/decision", json=body, headers=H(REVIEWER))
    n = len(env.evidence.events)
    r = env.client.post(f"/review/cases/{cid}/decision", json=body, headers=H(REVIEWER))
    assert r.status_code == 409 and len(env.evidence.events) == n


@pytest.mark.parametrize("body", [
    {"outcome": "uphold"}, {"outcome": "uphold", "reason": ""}, {"outcome": "change", "reason": "abc def"},
    {"outcome": "weird", "reason": "abc def"}, {"outcome": "change", "new_outcome": "banana", "reason": "abc def"},
])
def test_decision_should_validate_input(env, body):
    cid = make_case(env)
    assert env.client.post(f"/review/cases/{cid}/decision", json=body, headers=H(REVIEWER)).status_code == 422


def test_ledger_failure_should_not_record_and_retry_should_not_duplicate(env):
    cid = make_case(env)
    body = {"outcome": "uphold", "reason": "Rubric criteria met."}
    env.evidence.fail_next = 1
    assert env.client.post(f"/review/cases/{cid}/decision", json=body, headers=H(REVIEWER)).status_code == 503
    assert env.client.get(f"/review/cases/{cid}", headers=H(REVIEWER)).json()["status"] == "open"
    assert env.client.post(f"/review/cases/{cid}/decision", json=body, headers=H(REVIEWER)).status_code == 201
    assert len([e for e in env.evidence.events if e["event_type"] == "review_decision"]) == 1


def test_decision_should_be_reviewer_only(env):
    cid = make_case(env)
    r = env.client.post(f"/review/cases/{cid}/decision", json={"outcome": "uphold", "reason": "abc def"},
                        headers=H(LEARNER))
    assert r.status_code == 403


# ---------------- appeals ----------------
def test_learner_should_appeal_own_evidence_and_it_enters_queue(env):
    rec = env.evidence.seed(LRN_A)
    r = env.client.post("/me/appeals", json={"event_id": rec["event_id"], "reason": "I think this was marked wrongly."},
                        headers=H(LEARNER))
    assert r.status_code == 201
    q = env.client.get("/review/queue", headers=H(REVIEWER)).json()["cases"]
    assert q[0]["reason"] == "appeal"
    mine = env.client.get("/me/appeals", headers=H(LEARNER)).json()["appeals"]
    assert len(mine) == 1 and mine[0]["status"] == "open"
    assert env.evidence.events[-1]["event_type"] == "appeal_filed"


def test_appeal_on_foreign_or_unknown_event_should_be_identical_404(env):
    rec = env.evidence.seed(LRN_A)
    foreign = env.client.post("/me/appeals", json={"event_id": rec["event_id"], "reason": "wrong marking here"},
                              headers=H(OTHER))
    unknown = env.client.post("/me/appeals", json={"event_id": "00000000-0000-4000-8000-0000000000ff",
                                                   "reason": "wrong marking here"}, headers=H(OTHER))
    assert foreign.status_code == unknown.status_code == 404 and foreign.json() == unknown.json()


def test_appeals_listing_should_not_leak_other_learners(env):
    rec = env.evidence.seed(LRN_A)
    env.client.post("/me/appeals", json={"event_id": rec["event_id"], "reason": "wrong marking here"}, headers=H(LEARNER))
    assert env.client.get("/me/appeals", headers=H(OTHER)).json()["appeals"] == []


# ---------------- recording playback ----------------
def test_recording_should_serve_range_to_reviewer_only(env):
    r = env.client.get("/review/attempts/att_1/recording/camera", headers={**H(REVIEWER), "Range": "bytes=10-19"})
    assert r.status_code == 206
    assert r.headers["content-range"] == "bytes 10-19/1024" and r.content == env.integrity.blob[10:20]
    assert env.client.get("/review/attempts/att_1/recording/camera", headers=H(LEARNER)).status_code == 403
    assert env.client.get("/review/attempts/att_1/recording/camera").status_code == 401


def test_recording_should_404_unknown_attempt_or_stream_identically(env):
    a = env.client.get("/review/attempts/att_zzz/recording/camera", headers=H(REVIEWER))
    b = env.client.get("/review/attempts/att_1/recording/microphone", headers=H(REVIEWER))
    c = env.client.get("/review/attempts/bad.id/recording/camera", headers=H(REVIEWER))
    assert a.status_code == b.status_code == c.status_code == 404
    assert a.json() == b.json() == c.json()


def test_recording_should_reject_unsatisfiable_range(env):
    r = env.client.get("/review/attempts/att_1/recording/screen", headers={**H(REVIEWER), "Range": "bytes=5000-6000"})
    assert r.status_code == 416
    r = env.client.get("/review/attempts/att_1/recording/screen", headers={**H(REVIEWER), "Range": "bytes=abc"})
    assert r.status_code == 416
