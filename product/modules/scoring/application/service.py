"""Scoring use cases: gated publish, estimate lookup, profile projection."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable, Optional, Protocol, Sequence

from scoring.domain import selection
from scoring.domain.estimator import estimate_from_items


class GateNotMet(Exception):
    """The Proof-of-Skill update is not allowed (levels incomplete or ledger not verified)."""

    code = "gate_not_met"


class EvidenceReader(Protocol):
    def list_for_learner(self, learner_id: str) -> Sequence[Any]: ...
    def verify(self, learner_id: Optional[str] = None) -> Any: ...


@dataclass(frozen=True)
class Published:
    learner_id: str
    competency: str
    estimate: float
    lower: float
    upper: float
    as_of: str
    counts: dict
    evidence_head: str


class SnapshotStore(Protocol):
    def latest(self, learner_id: str, competency: str, as_of: Optional[str] = None) -> Optional[Published]: ...
    def add(self, snap: Published) -> None: ...


def _iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).replace(microsecond=0).strftime("%Y-%m-%dT%H:%M:%SZ")


def _parse(ts: str) -> datetime:
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))


@dataclass(frozen=True)
class CompetencyView:
    competency: str
    published: Optional[Published]
    evidence: dict
    probe: dict
    levels_passed: list = field(default_factory=list)


class ScoringService:
    def __init__(self, evidence: EvidenceReader, store: SnapshotStore,
                 clock: Callable[[], datetime]) -> None:
        self._ev = evidence
        self._store = store
        self._clock = clock

    def _events(self, learner_id: str) -> tuple[list[dict], list[Any]]:
        entries = list(self._ev.list_for_learner(learner_id))
        events = [dict(e.event, event_type=e.event_type) for e in entries]
        return events, entries

    def _compute(self, events: list[dict], entries: list[Any], competency: str, now: datetime):
        scored = selection.scored_events(events, competency)
        items = []
        counts = {g: 0 for g in selection.GROUPS}
        probe = {"confirmed": 0, "unconfirmed": 0, "label_unconfirmed": selection.UNCONFIRMED_LABEL}
        for e in scored:
            counts[selection.GROUP.get(e.get("method"), "automated_test")] += 1
            if e.get("event_type") == "probe_result":
                status = e.get("understanding_status")
                if status in ("confirmed", "unconfirmed"):
                    probe[status] += 1
            weight = selection.METHOD_WEIGHT.get(e.get("method"))
            frac = selection.success_fraction(e)
            if weight is None or frac is None:
                continue
            age = max((now - _parse(e["occurred_at"])).total_seconds() / 86400.0, 0.0)
            items.append((weight, frac, age))
        return items, counts, probe

    def apply_gated_update(self, learner_id: str, competency: str) -> None:
        selection.competency_id(competency)
        events, entries = self._events(learner_id)
        passed = selection.levels_passed(events, competency)
        if passed != list(selection.LEVELS):
            raise GateNotMet("levels incomplete")
        verdict = self._ev.verify(learner_id)
        if not getattr(verdict, "ok", False):
            raise GateNotMet("ledger verification failed")
        head = entries[-1].hash if entries else ""
        latest = self._store.latest(learner_id, competency)
        if latest is not None and latest.evidence_head == head:
            return
        now = self._clock()
        items, counts, probe = self._compute(events, entries, competency, now)
        raw = estimate_from_items(items)
        self._store.add(Published(learner_id, competency, raw.estimate, raw.lower, raw.upper,
                                  _iso(now), {"evidence": counts, "probe": probe}, head))

    def competency_estimate(self, learner_id: str, competency: str,
                            as_of: Optional[datetime] = None) -> Optional[Published]:
        selection.competency_id(competency)
        return self._store.latest(learner_id, competency, _iso(as_of) if as_of else None)

    def views(self, learner_id: str) -> list[CompetencyView]:
        events, entries = self._events(learner_id)
        out = []
        now = self._clock()
        for comp in selection.COMPETENCIES:
            passed = selection.levels_passed(events, comp)
            _, counts, probe = self._compute(events, entries, comp, now)
            out.append(CompetencyView(comp, self._store.latest(learner_id, comp), counts, probe, passed))
        return out

    def evidence_items(self, learner_id: str) -> list[dict]:
        events, entries = self._events(learner_id)
        items = []
        for e, entry in zip(events, entries):
            if e["event_type"] in ("integrity_flag",):
                continue
            items.append({
                "recorded_at": entry.recorded_at, "event_type": e["event_type"],
                "competency": e.get("competency_id", "").replace("cmp_", "", 1),
                "level": e.get("level"), "method": e.get("method"),
                "method_group": selection.GROUP.get(e.get("method"), "automated_test"),
                "outcome": e.get("outcome"), "criterion_id": e.get("criterion_id"),
                "task_id": e.get("task_id"), "task_version": e.get("task_version"),
                "rubric_version": e.get("rubric_version"), "ai_disclosure": bool(e.get("ai_disclosure", False)),
                "model_ref": e.get("model_ref"), "understanding_status": e.get("understanding_status"),
                "rationale": e.get("rationale"), "entry_hash": entry.hash,
            })
        return items
