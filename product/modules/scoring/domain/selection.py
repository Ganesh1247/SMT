"""Which ledger events count as scored evidence. Pure functions over event dicts."""
from __future__ import annotations

from typing import Iterable, Mapping

COMPETENCIES = ("python", "sql")
METHOD_WEIGHT = {"deterministic_test": 1.0, "probe": 0.8, "live_screening": 0.8, "human_review": 1.0}
# ai_judged (rubric-graded explanations) is recorded and shown but is not scored.
GROUP = {
    "deterministic_test": "automated_test",
    "ai_judged": "ai_rubric",
    "probe": "probe",
    "live_screening": "live_screening",
    "human_review": "human_review",
}
GROUPS = ("automated_test", "ai_rubric", "probe", "live_screening", "human_review")
LEVELS = (1, 2, 3, 4)
UNCONFIRMED_LABEL = "Output verified, understanding unconfirmed"


def competency_id(name: str) -> str:
    if name not in COMPETENCIES:
        raise ValueError("unknown competency")
    return "cmp_" + name


def levels_passed(events: Iterable[Mapping], competency: str) -> list[int]:
    cid = competency_id(competency)
    return sorted({e["level"] for e in events
                   if e.get("event_type") == "level_outcome" and e.get("outcome") == "pass"
                   and e.get("competency_id") == cid})


def qualifying_seeds(events: Iterable[Mapping], competency: str) -> dict[int, set[str]]:
    """Seeds (attempts) that produced a passing level outcome, per level."""
    cid = competency_id(competency)
    out: dict[int, set[str]] = {}
    for e in events:
        if (e.get("event_type") == "level_outcome" and e.get("outcome") == "pass"
                and e.get("competency_id") == cid):
            out.setdefault(e["level"], set()).add(e["seed_id"])
    return out


def scored_events(events: list[Mapping], competency: str) -> list[Mapping]:
    """criterion/probe events that belong to a passing attempt of the competency."""
    cid = competency_id(competency)
    seeds = qualifying_seeds(events, competency)
    return [e for e in events
            if e.get("event_type") in ("criterion_result", "probe_result")
            and e.get("competency_id") == cid
            and e.get("seed_id") in seeds.get(e.get("level"), set())]


def success_fraction(event: Mapping) -> float | None:
    outcome = event.get("outcome")
    if outcome == "inconclusive":
        return None
    if event.get("score") is not None:
        return float(event["score"])
    return {"pass": 1.0, "fail": 0.0, "partial": 0.5}.get(outcome)
