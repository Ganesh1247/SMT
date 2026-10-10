"""hr: role CRUD with versioning, coverage and gaps (no totals or ranks), evidence page, receipt verify."""
import json

import jsonschema
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from hr import api
from hr.domain.coverage import evaluate
from hr.infrastructure.contracts import contracts_dir, validator

from fakes_hr import (ALIAS_1, ALIAS_2, H64, H64B, NOW, Clock, FakeEvidence, FakeIdentity, FakeReview, Ids,
                      shared)

REC = "rec_1|recruiter|org_demo_recruiter"
REC2 = "rec_2|recruiter|org_other_firm"
LEARNER = "lrn_0a1b2c3d4e5f6071|learner"


@pytest.fixture()
def env():
    class E:
        pass
    e = E()
    e.review, e.evidence = FakeReview(), FakeEvidence()
    api.configure(identity=FakeIdentity(), review=e.review, evidence=e.evidence, clock=Clock(), ids=Ids(), store=None)
    app = FastAPI()
    app.include_router(api.router)
    e.client = TestClient(app)
    return e


def H(u=REC):
    return {"x-test-user": u}


def role_body(**over):
    b = {"title": "Junior Python developer", "summary": "Backend basics",
         "competencies": [{"competency_id": "cmp_python", "priority": "required", "min_levels_passed": 3,
                           "min_estimate_lower": 0.4, "max_evidence_age_days": 180,
                           "require_understanding_confirmed": True}]}
    b.update(over)
    return b


def create_role(env, **over):
    r = env.client.post("/hr/roles", json=role_body(**over), headers=H())
    assert r.status_code == 201, r.text
    return r.json()


# ---------------- roles ----------------
def test_should_create_role_valid_against_contract_with_server_side_fields(env):
    r = create_role(env)
    assert r["version"] == 1 and r["recipient_id"] == "org_demo_recruiter" and r["role_id"].startswith("role_")
    doc = {k: v for k, v in r.items() if k != "readback"}
    jsonschema.validate(doc, json.loads((contracts_dir() / "role-requirement.schema.json").read_text(encoding="utf-8")))
    assert "Required" in r["readback"][0] and "level 3" in r["readback"][0] and "180 days" in r["readback"][0]


@pytest.mark.parametrize("name", [
    "invalid.role-requirement.speed-proxy.json", "invalid.role-requirement.threshold-out-of-range.json",
    "invalid.role-requirement.personal-attribute.json", "invalid.role-requirement.no-competencies.json"])
def test_should_reject_every_invalid_contract_example(env, name):
    ex = json.loads((contracts_dir() / "examples" / name).read_text(encoding="utf-8"))
    server_assigned = ("schema_version", "role_id", "recipient_id", "version", "created_at")
    body = {k: v for k, v in ex.items() if k not in server_assigned}
    r = env.client.post("/hr/roles", json=body, headers=H())
    assert r.status_code == 422, name
    assert r.json()["error"]["details"]


@pytest.mark.parametrize("mutate", [
    lambda b: b.update(title="ab"),
    lambda b: b.update(competencies=[]),
    lambda b: b.update(unexpected=1),
    lambda b: b.update(recipient_id="org_x_firm"),
    lambda b: b["competencies"][0].update(max_time_seconds=30),
    lambda b: b["competencies"][0].update(min_estimate_lower=1.5),
    lambda b: b["competencies"][0].update(priority="critical"),
    lambda b: b.update(competencies=[{"competency_id": f"cmp_skill{i}", "priority": "preferred"} for i in range(9)]),
])
def test_should_reject_invalid_role_bodies(env, mutate):
    b = role_body()
    mutate(b)
    assert env.client.post("/hr/roles", json=b, headers=H()).status_code == 422


def test_update_should_increment_version_and_keep_history(env):
    r = create_role(env)
    up = env.client.put(f"/hr/roles/{r['role_id']}", json=role_body(title="Senior Python developer"), headers=H())
    assert up.status_code == 200 and up.json()["version"] == 2
    old = env.client.get(f"/hr/roles/{r['role_id']}?version=1", headers=H()).json()
    cur = env.client.get(f"/hr/roles/{r['role_id']}", headers=H()).json()
    assert old["title"] == "Junior Python developer" and cur["title"] == "Senior Python developer"


def test_roles_should_be_scoped_to_organisation(env):
    r = create_role(env)
    assert env.client.get(f"/hr/roles/{r['role_id']}", headers=H(REC2)).status_code == 404
    assert env.client.put(f"/hr/roles/{r['role_id']}", json=role_body(), headers=H(REC2)).status_code == 404
    assert env.client.get("/hr/roles", headers=H(REC2)).json()["roles"] == []
    assert len(env.client.get("/hr/roles", headers=H()).json()["roles"]) == 1


def test_should_require_recruiter_role(env):
    assert env.client.get("/hr/roles").status_code == 401
    assert env.client.get("/hr/roles", headers=H(LEARNER)).status_code == 403
    assert env.client.post("/hr/roles", json=role_body(), headers=H("rev_1|reviewer")).status_code == 403


# ---------------- coverage (domain) ----------------
REQ = {"competency_id": "cmp_python", "priority": "required", "min_levels_passed": 3, "min_estimate_lower": 0.4,
       "max_evidence_age_days": 180, "require_understanding_confirmed": True}


def test_coverage_should_be_met_when_every_threshold_is_satisfied():
    c = evaluate(REQ, shared(), NOW)
    assert c["coverage"] == "met" and c["reasons"] == []


def test_coverage_should_be_partly_met_when_evidence_is_older_than_window():
    c = evaluate(REQ, shared(last="2026-02-01T00:00:00Z"), NOW)
    assert c["coverage"] == "partly_met" and "window is 180" in c["reasons"][0]


def test_coverage_should_name_unconfirmed_understanding_without_saying_failed():
    c = evaluate(REQ, shared(understanding="unconfirmed"), NOW)
    assert c["coverage"] == "partly_met"
    assert "Output verified, understanding unconfirmed" in " ".join(c["reasons"])
    assert "fail" not in " ".join(c["reasons"]).lower()


def test_coverage_should_be_not_met_when_every_check_falls_short():
    c = evaluate(REQ, shared(levels=(1,), lower=0.1, understanding="unconfirmed", last="2025-01-01T00:00:00Z"), NOW)
    assert c["coverage"] == "not_met"


def test_coverage_should_be_no_evidence_when_nothing_shared():
    assert evaluate(REQ, None, NOW)["coverage"] == "no_evidence"


def test_coverage_should_apply_allowed_methods():
    req = {**REQ, "allowed_methods": ["probe"]}
    assert evaluate(req, shared(methods=("deterministic_test",)), NOW)["coverage"] == "no_evidence"
    assert evaluate(req, shared(methods=("deterministic_test", "probe")), NOW)["coverage"] == "met"


def test_coverage_with_no_thresholds_should_be_met_when_evidence_exists():
    assert evaluate({"competency_id": "cmp_python", "priority": "preferred"}, shared(), NOW)["coverage"] == "met"


# ---------------- results ----------------
def test_results_should_show_coverage_and_gaps_without_totals_or_ranks(env):
    r = create_role(env, competencies=[
        {"competency_id": "cmp_python", "priority": "required", "min_levels_passed": 3},
        {"competency_id": "cmp_sql", "priority": "required", "min_levels_passed": 2}])
    env.review.docs = [shared(ALIAS_2, "cmp_python"), shared(ALIAS_1, "cmp_python", levels=(1,)),
                       shared(ALIAS_1, "cmp_sql")]
    out = env.client.get(f"/hr/roles/{r['role_id']}/results", headers=H()).json()
    assert [c["candidate_ref"] for c in out["candidates"]] == [ALIAS_1, ALIAS_2]
    c1 = {x["competency_id"]: x for x in out["candidates"][0]["competencies"]}
    assert c1["cmp_python"]["coverage"] == "not_met" and c1["cmp_python"]["gap"] is True
    assert c1["cmp_sql"]["coverage"] == "met" and c1["cmp_sql"]["gap"] is False
    c2 = {x["competency_id"]: x for x in out["candidates"][1]["competencies"]}
    assert c2["cmp_sql"]["coverage"] == "no_evidence" and c2["cmp_sql"]["gap"] is True
    flat = json.dumps(out).lower()
    for word in ("total", "rank\"", "score", "best", "recommend", "match_"):
        assert word not in flat
    assert "not a ranking" in out["note"].lower() and "experimental" in out["label"].lower()


def test_query_to_trust_should_carry_competency_ids_only_never_thresholds(env):
    r = create_role(env)
    env.client.get(f"/hr/roles/{r['role_id']}/results", headers=H())
    req = env.review.requests[0]
    assert set(req) <= {"schema_version", "request_id", "recipient_id", "role_id", "role_version",
                        "competency_ids", "candidate_refs", "page"}
    assert "0.4" not in json.dumps(req) and "180" not in json.dumps(req)
    assert req["recipient_id"] == env.review.callers[0] == "org_demo_recruiter"
    validator("shared-evidence-query-request.schema.json").validate(req)


def test_results_should_follow_pages_until_exhausted(env):
    r = create_role(env)
    env.review.pages = True
    env.review.docs = [shared(ALIAS_1), shared(ALIAS_2)]
    out = env.client.get(f"/hr/roles/{r['role_id']}/results", headers=H()).json()
    assert len(out["candidates"]) == 2


def test_results_with_no_grants_should_be_empty_without_reason(env):
    r = create_role(env)
    out = env.client.get(f"/hr/roles/{r['role_id']}/results", headers=H())
    assert out.status_code == 200 and out.json()["candidates"] == []
    assert "hidden" not in out.text.lower() and "withheld" not in out.text.lower()


def test_results_for_foreign_role_should_404(env):
    r = create_role(env)
    assert env.client.get(f"/hr/roles/{r['role_id']}/results", headers=H(REC2)).status_code == 404


def test_results_should_fail_closed_on_malformed_trust_response(env):
    r = create_role(env)
    bad = shared()
    bad["overall_score"] = 0.9
    env.review.docs = [bad]
    assert env.client.get(f"/hr/roles/{r['role_id']}/results", headers=H()).status_code == 502


# ---------------- evidence page ----------------
def test_evidence_page_should_return_contract_shape(env):
    env.review.docs = [shared()]
    out = env.client.get(f"/hr/evidence/{ALIAS_1}/cmp_python", headers=H())
    assert out.status_code == 200
    validator("shared-evidence.schema.json").validate(out.json())
    assert env.review.requests[0]["candidate_refs"] == [ALIAS_1]


def test_evidence_page_should_not_distinguish_no_grant_from_nonexistent(env):
    a = env.client.get(f"/hr/evidence/{ALIAS_1}/cmp_python", headers=H())
    b = env.client.get(f"/hr/evidence/cnd_{'f' * 16}/cmp_python", headers=H())
    assert a.status_code == b.status_code == 404 and a.json() == b.json()


@pytest.mark.parametrize("path", ["/hr/evidence/notalias/cmp_python", f"/hr/evidence/{ALIAS_1}/BAD"])
def test_evidence_page_should_reject_malformed_ids_as_404(env, path):
    assert env.client.get(path, headers=H()).status_code == 404


# ---------------- receipts ----------------
def verify(env, **over):
    body = {"candidate_ref": ALIAS_1, "competency_id": "cmp_python", "receipt_hash": H64}
    body.update(over)
    return env.client.post("/hr/receipts/verify", json=body, headers=H())


def test_receipt_verify_should_report_match_with_ledger_entry(env):
    env.review.docs = [shared()]
    r = verify(env)
    assert r.status_code == 200 and r.json() == {"status": "match", "ledger_entry": 214}


def test_receipt_verify_should_report_mismatch(env):
    env.review.docs = [shared()]
    env.evidence.status = "mismatch"
    assert verify(env).json()["status"] == "mismatch"


def test_receipt_verify_should_say_unavailable_when_ledger_unreachable(env):
    env.review.docs = [shared()]
    env.evidence.fail = True
    assert verify(env).json()["status"] == "unavailable"


def test_receipt_verify_should_404_for_receipt_not_in_shared_evidence(env):
    env.review.docs = [shared()]
    assert verify(env, receipt_hash=H64B).status_code == 404
    assert verify(env, candidate_ref="cnd_" + "f" * 16).status_code == 404


def test_receipt_verify_should_validate_input(env):
    assert verify(env, receipt_hash="nope").status_code == 422
    assert env.client.post("/hr/receipts/verify", json={"receipt_hash": H64, "extra": 1}, headers=H()).status_code == 422


# ---------------- default adapter ----------------
def test_default_review_adapter_should_forward_to_review_api(monkeypatch):
    from hr.infrastructure.adapters import ReviewApiAdapter
    from review import api as review_api
    seen = {}
    monkeypatch.setattr(review_api, "query_shared_evidence", lambda req, caller_recipient_id: seen.update(
        r=req, c=caller_recipient_id) or {"ok": True})
    assert ReviewApiAdapter().query_shared_evidence({"a": 1}, "org_x_firm") == {"ok": True}
    assert seen["c"] == "org_x_firm"
