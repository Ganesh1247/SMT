"""Scoring: Beta estimate + band, method weights, recency, gated update (REQ-score-gating)."""
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

import pytest

import scoring.api as scoring
from scoring.domain.estimator import estimate_from_items

NOW = datetime(2026, 10, 10, 12, 0, 0, tzinfo=timezone.utc)
LRN = "lrn_0a1b2c3d4e5f6071"


@dataclass
class Entry:
    sequence: int
    event_type: str
    learner_id: str
    event: dict
    recorded_at: str
    hash: str = "sha256:" + "0" * 64
    meta: Any = None


@dataclass
class Verify:
    ok: bool = True
    message: str = "ok"
    first_failure: Optional[int] = None
    entries_checked: int = 0


class FakeEvidence:
    def __init__(self):
        self.entries: list[Entry] = []
        self.verify_ok = True

    def add(self, event_type, *, level, outcome="pass", method="deterministic_test", seed="sd_000000000001",
            competency="cmp_python", score=None, learner=LRN, at=NOW, criterion="crt_item_one", **extra):
        ev = {"event_type": event_type, "learner_id": learner, "competency_id": competency, "level": level,
              "method": method, "outcome": outcome, "seed_id": seed, "criterion_id": criterion,
              "task_id": "tsk_x_item", "task_version": "1.0.0", "rubric_id": "rbr_python_l1",
              "rubric_version": "1.0.0", "occurred_at": at.strftime("%Y-%m-%dT%H:%M:%SZ")}
        if score is not None:
            ev["score"] = score
        ev.update(extra)
        self.entries.append(Entry(len(self.entries) + 1, event_type, learner, ev,
                                  at.strftime("%Y-%m-%dT%H:%M:%SZ")))

    def list_for_learner(self, learner_id):
        return [e for e in self.entries if e.learner_id == learner_id]

    def verify(self, learner_id=None):
        return Verify(self.verify_ok)


@pytest.fixture()
def ev():
    fake = FakeEvidence()
    scoring.configure(database_url="sqlite://", evidence=fake, clock=lambda: NOW)
    yield fake
    scoring.reset()


def pass_all_levels(ev, seeds=("sd_000000000001", "sd_000000000002", "sd_000000000003", "sd_000000000004")):
    for level, seed in enumerate(seeds, start=1):
        method = "live_screening" if level == 4 else "deterministic_test"
        extra = {"confidence": 0.9, "ai_disclosure": True} if level == 4 else {}
        ev.add("criterion_result", level=level, seed=seed, method=method, **extra)
        ev.add("level_outcome", level=level, seed=seed, method=method, criterion=None, **extra)


# ---- domain math -----------------------------------------------------------
def test_should_return_mean_within_band_for_mixed_evidence():
    est = estimate_from_items([(1.0, 1.0, 0)] * 8 + [(1.0, 0.0, 0)] * 2)
    assert est.lower < est.estimate < est.upper
    assert est.estimate == pytest.approx(9 / 12, abs=1e-3)


def test_should_widen_band_when_evidence_is_scarce():
    few = estimate_from_items([(1.0, 1.0, 0)] * 2)
    many = estimate_from_items([(1.0, 1.0, 0)] * 40)
    assert (few.upper - few.lower) > (many.upper - many.lower)


def test_should_down_weight_old_evidence_with_half_life_180_days():
    old = estimate_from_items([(1.0, 0.0, 0)] * 5 + [(1.0, 1.0, 0)] * 5)
    aged = estimate_from_items([(1.0, 0.0, 360)] * 5 + [(1.0, 1.0, 0)] * 5)
    assert aged.estimate > old.estimate


def test_should_weight_methods_by_configured_weights():
    heavy = estimate_from_items([(1.0, 0.0, 0)] * 5 + [(0.8, 1.0, 0)] * 5)
    assert heavy.estimate < 0.5


def test_should_keep_estimate_inside_zero_one_with_ordered_band():
    est = estimate_from_items([(1.0, 1.0, 0)] * 100)
    assert 0 <= est.lower <= est.estimate <= est.upper <= 1


# ---- gating ----------------------------------------------------------------
def test_should_publish_nothing_before_all_four_levels_pass(ev):
    for level in (1, 2, 3):
        ev.add("criterion_result", level=level, seed=f"sd_00000000000{level}")
        ev.add("level_outcome", level=level, seed=f"sd_00000000000{level}", criterion=None)
    with pytest.raises(scoring.GateNotMet):
        scoring.apply_gated_update(LRN, "python")
    assert scoring.competency_estimate(LRN, "python") is None
    prof = scoring.profile(LRN)
    assert all(c.estimate is None for c in prof.competencies)


def test_should_refuse_update_when_ledger_does_not_verify(ev):
    pass_all_levels(ev)
    ev.verify_ok = False
    with pytest.raises(scoring.GateNotMet):
        scoring.apply_gated_update(LRN, "python")
    assert scoring.competency_estimate(LRN, "python") is None


def test_should_publish_estimate_after_four_levels_with_band_and_label(ev):
    pass_all_levels(ev)
    scoring.apply_gated_update(LRN, "python")
    est = scoring.competency_estimate(LRN, "python")
    assert est.lower <= est.estimate <= est.upper
    assert est.as_of == "2026-10-10T12:00:00Z"
    prof = scoring.profile(LRN)
    py = next(c for c in prof.competencies if c.competency == "python")
    assert py.estimate is not None and py.label == "Experimental"
    assert py.levels_passed == [1, 2, 3, 4]


def test_should_not_change_published_estimate_when_later_evidence_arrives_without_update(ev):
    pass_all_levels(ev)
    scoring.apply_gated_update(LRN, "python")
    before = scoring.competency_estimate(LRN, "python")
    ev.add("criterion_result", level=1, outcome="fail", seed="sd_0000000000ff")
    assert scoring.competency_estimate(LRN, "python") == before


def test_should_ignore_evidence_from_failed_attempts(ev):
    ev.add("criterion_result", level=1, outcome="fail", seed="sd_0000000000aa")
    ev.add("level_outcome", level=1, outcome="fail", seed="sd_0000000000aa", criterion=None)
    pass_all_levels(ev)
    scoring.apply_gated_update(LRN, "python")
    assert scoring.profile(LRN).competencies[0].evidence["automated_test"] == 3


def test_should_separate_automated_and_live_evidence_counts(ev):
    pass_all_levels(ev)
    scoring.apply_gated_update(LRN, "python")
    py = next(c for c in scoring.profile(LRN).competencies if c.competency == "python")
    assert py.evidence["automated_test"] == 3 and py.evidence["live_screening"] == 1


def test_should_not_let_unconfirmed_probe_change_the_output_result(ev):
    pass_all_levels(ev)
    ev.add("probe_result", level=3, seed="sd_000000000003", method="probe", outcome="inconclusive",
           understanding_status="unconfirmed")
    scoring.apply_gated_update(LRN, "python")
    py = next(c for c in scoring.profile(LRN).competencies if c.competency == "python")
    assert py.probe["unconfirmed"] == 1
    assert py.probe["label_unconfirmed"] == "Output verified, understanding unconfirmed"
    assert py.estimate.estimate > 0.5


def test_should_return_historical_snapshot_for_as_of(ev):
    pass_all_levels(ev)
    scoring.apply_gated_update(LRN, "python")
    assert scoring.competency_estimate(LRN, "python", as_of=NOW - timedelta(days=1)) is None
    assert scoring.competency_estimate(LRN, "python", as_of=NOW) is not None


def test_should_be_idempotent_when_evidence_is_unchanged(ev):
    pass_all_levels(ev)
    scoring.apply_gated_update(LRN, "python")
    scoring.apply_gated_update(LRN, "python")
    from scoring.api import runtime
    from sqlalchemy import text
    with runtime.get_engine().connect() as c:
        assert c.execute(text("SELECT COUNT(*) FROM published_estimates")).scalar_one() == 1


def test_should_reject_unknown_competency(ev):
    with pytest.raises(ValueError):
        scoring.apply_gated_update(LRN, "cobol")
