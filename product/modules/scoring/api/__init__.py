"""Public contract of the scoring module."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from scoring.api import runtime
from scoring.application.service import GateNotMet, Published
from scoring.domain.selection import COMPETENCIES, UNCONFIRMED_LABEL

LABEL = "Experimental"


@dataclass(frozen=True)
class Estimate:
    estimate: float
    lower: float
    upper: float
    as_of: str
    label: str = LABEL


@dataclass(frozen=True)
class CompetencyProfile:
    competency: str
    estimate: Optional[Estimate]
    evidence: dict
    probe: dict
    levels_passed: list = field(default_factory=list)
    label: str = LABEL


@dataclass(frozen=True)
class ProfileDTO:
    learner_id: str
    competencies: list
    note: str


def _est(p: Optional[Published]) -> Optional[Estimate]:
    return Estimate(p.estimate, p.lower, p.upper, p.as_of) if p else None


def competency_estimate(learner_id: str, competency: str, as_of: Optional[datetime] = None) -> Optional[Estimate]:
    """Published estimate (never a bare number). None until the gated update has run.

    as_of returns the latest published snapshot at or before that time.
    Raises ValueError for an unknown competency ('python' | 'sql').
    """
    return _est(runtime.service().competency_estimate(learner_id, competency, as_of))


def apply_gated_update(learner_id: str, competency: str) -> None:
    """Publish a new estimate. Raises GateNotMet unless levels 1-4 are passed and the
    learner's ledger entries verify. Idempotent for unchanged evidence."""
    runtime.service().apply_gated_update(learner_id, competency)


def profile(learner_id: str) -> ProfileDTO:
    views = runtime.service().views(learner_id)
    comps = [CompetencyProfile(v.competency, _est(v.published), dict(v.evidence), dict(v.probe),
                               list(v.levels_passed)) for v in views]
    return ProfileDTO(learner_id, comps,
                      "Estimates are experimental, always shown with a band, and update only after all four levels are passed.")


configure = runtime.configure
reset = runtime.reset

from scoring.api.http import router  # noqa: E402

__all__ = ["router", "profile", "competency_estimate", "apply_gated_update", "configure", "reset",
           "Estimate", "ProfileDTO", "CompetencyProfile", "GateNotMet", "COMPETENCIES", "UNCONFIRMED_LABEL"]
