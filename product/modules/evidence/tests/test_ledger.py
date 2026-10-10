"""Evidence ledger behaviour (REQ ledger integrity, hash canonicalisation v1)."""
import json
from datetime import datetime, timezone

import pytest
from sqlalchemy import text

import evidence.api as ev
from evidence.domain import canonical

LRN_A = "lrn_0a1b2c3d4e5f6071"
LRN_B = "lrn_ffffffffffffffff"
VECTOR = "sha256:cd2f785ff97fa7a4a94446a507a7a6d2e514ab54b1ae0a22f05a8027c81dc0d6"


def sample_event():
    return {
        "schema_version": "0.1",
        "idempotency_key": "evt-0001-lrn_0a1b2c3d4e5f6071-crt_join_logic",
        "source_system": "sandbox",
        "event_type": "criterion_result",
        "learner_id": LRN_A,
        "competency_id": "cmp_data_analysis",
        "level": 2,
        "criterion_id": "crt_join_logic",
        "method": "deterministic_test",
        "outcome": "pass",
        "score": 1,
        "task_id": "tsk_sales_dedupe",
        "task_version": "1.0.0",
        "rubric_id": "rbr_data_analysis",
        "rubric_version": "1.0.0",
        "seed_id": "sd_9f8e7d6c5b4a",
        "submission_ref": "sha256:" + "a" * 64,
        "rationale": "Result set matched the hidden check on all seeded rows.",
        "occurred_at": "2026-10-10T09:15:00Z",
    }


def payload(**over):
    p = {
        "competency_id": "cmp_python", "level": 1, "criterion_id": "crt_item_one",
        "method": "deterministic_test", "outcome": "pass", "score": 1,
        "task_id": "tsk_l1_item_one", "task_version": "1.0.0", "rubric_id": "rbr_python_l1",
        "rubric_version": "1.0.0", "seed_id": "sd_0123456789ab",
        "submission_ref": "sha256:" + "b" * 64,
    }
    p.update(over)
    return p


@pytest.fixture(autouse=True)
def fresh_ledger():
    ev.configure(database_url="sqlite://", clock=lambda: datetime(2026, 10, 10, 9, 0, 0, tzinfo=timezone.utc))
    yield
    ev.reset()


def test_should_reproduce_the_published_test_vector():
    h = canonical.event_hash(sample_event(), 1, canonical.GENESIS)
    assert h == VECTOR
    assert len(canonical.canonical_bytes(sample_event(), 1, canonical.GENESIS)) == 707


def test_should_chain_entries_from_genesis():
    a = ev.append("criterion_result", LRN_A, payload(), "key-one-0000000001")
    b = ev.append("criterion_result", LRN_A, payload(criterion_id="crt_item_two"), "key-two-0000000002")
    assert (a.sequence, a.prev_hash) == (1, "genesis")
    assert (b.sequence, b.prev_hash) == (2, a.hash)
    assert a.hash.startswith("sha256:") and len(a.hash) == 71


def test_should_be_idempotent_when_same_key_is_appended_twice():
    a = ev.append("criterion_result", LRN_A, payload(), "key-one-0000000001")
    again = ev.append("criterion_result", LRN_A, payload(), "key-one-0000000001")
    assert again.sequence == a.sequence and again.hash == a.hash
    assert len(ev.list_for_learner(LRN_A)) == 1


def test_should_store_normalised_values():
    a = ev.append("criterion_result", LRN_A, payload(score=0.6000004), "key-one-0000000001")
    assert a.event["score"] == 0.6
    assert a.event["occurred_at"] == "2026-10-10T09:00:00Z"


@pytest.mark.parametrize("bad", [
    {"outcome": "excellent"},
    {"level": 5},
    {"score": 1.5},
    {"competency_id": "Python"},
    {"seed_id": "seed"},
    {"smuggled": "x"},
    {"ledger": {"sequence": 9}},
    {"rationale": "x" * 1001},
])
def test_should_reject_invalid_payload(bad):
    with pytest.raises(ev.EvidenceValidationError):
        ev.append("criterion_result", LRN_A, payload(**bad), "key-bad-00000000001")


def test_should_reject_invalid_learner_id_and_short_key():
    with pytest.raises(ev.EvidenceValidationError):
        ev.append("criterion_result", "alice@example.com", payload(), "key-one-0000000001")
    with pytest.raises(ev.EvidenceValidationError):
        ev.append("criterion_result", LRN_A, payload(), "short")


def test_should_require_ai_disclosure_fields_for_ai_judged():
    with pytest.raises(ev.EvidenceValidationError):
        ev.append("criterion_result", LRN_A, payload(method="ai_judged"), "key-ai-000000000001")
    ok = ev.append("criterion_result", LRN_A, payload(method="ai_judged", confidence=0.7, ai_disclosure=True, model_ref="stub-v1"), "key-ai-000000000002")
    assert ok.event["ai_disclosure"] is True


def test_should_bind_meta_to_the_hash_via_submission_ref():
    p = payload()
    del p["submission_ref"]
    e = ev.append("integrity_flag", LRN_A, dict(p, meta={"manifest_hash": "abc", "chunks": 3}), "key-meta-0000000001")
    assert e.event["submission_ref"].startswith("sha256:")
    assert e.meta == {"manifest_hash": "abc", "chunks": 3}
    assert ev.verify().ok


def test_should_fill_neutral_context_for_integrity_events():
    e = ev.append("integrity_flag", LRN_A, {"method": "deterministic_test", "outcome": "inconclusive", "meta": {"k": 1}}, "key-int-00000000001")
    assert e.event["competency_id"] == "cmp_platform"
    assert ev.verify().ok


def test_should_verify_clean_chain():
    for i in range(3):
        ev.append("criterion_result", LRN_A, payload(criterion_id=f"crt_item_{i}"), f"key-clean-00000000{i}")
    res = ev.verify()
    assert res.ok and res.entries_checked == 3 and res.first_failure is None


def _tamper(sequence, **changes):
    from evidence.api import runtime
    eng = runtime.get_engine()
    with eng.begin() as c:
        row = c.execute(text("SELECT event_json FROM ledger WHERE sequence=:s"), {"s": sequence}).one()
        event = json.loads(row[0])
        event.update(changes)
        c.execute(text("UPDATE ledger SET event_json=:j WHERE sequence=:s"), {"j": json.dumps(event), "s": sequence})


def test_should_detect_tampering_and_name_the_entry():
    for i in range(3):
        ev.append("criterion_result", LRN_A, payload(criterion_id=f"crt_item_{i}"), f"key-t-000000000{i}")
    _tamper(2, outcome="fail")
    res = ev.verify()
    assert not res.ok and res.first_failure == 2


def test_should_scope_verification_to_learner():
    ev.append("criterion_result", LRN_A, payload(), "key-a-0000000000001")
    ev.append("criterion_result", LRN_B, payload(), "key-b-0000000000001")
    _tamper(2, outcome="fail")
    assert ev.verify(LRN_A).ok
    assert not ev.verify(LRN_B).ok
    assert not ev.verify().ok


def test_should_detect_deleted_entry():
    from evidence.api import runtime
    for i in range(3):
        ev.append("criterion_result", LRN_A, payload(criterion_id=f"crt_item_{i}"), f"key-d-000000000{i}")
    with runtime.get_engine().begin() as c:
        c.execute(text("DELETE FROM ledger WHERE sequence=2"))
    assert not ev.verify().ok


def test_should_list_only_the_learners_entries():
    ev.append("criterion_result", LRN_A, payload(), "key-a-0000000000001")
    ev.append("criterion_result", LRN_B, payload(), "key-b-0000000000001")
    assert [e.learner_id for e in ev.list_for_learner(LRN_A)] == [LRN_A]
