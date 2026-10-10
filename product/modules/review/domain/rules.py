"""Pure review rules: ordering, grant lifecycle, scope, decision mapping."""
from __future__ import annotations

from datetime import datetime, timedelta

REASONS = ("low_confidence", "appeal", "method_conflict", "integrity_review")
RISK_RANK = {"low": 0, "medium": 1, "high": 2}
CORE_SCOPE = ("estimate_band", "method_labels", "understanding_status", "evidence_summary")
ALLOWED_SCOPE = CORE_SCOPE + ("raw_submission",)
MAX_GRANT_DAYS = 365
FINAL_OUTCOMES = ("pass", "fail", "partial", "inconclusive")
DECISIONS = ("uphold", "change", "needs_more_info")
RECORDING_STREAMS = ("camera", "screen")


def queue_key(case: dict) -> tuple:
    """Highest uncertainty first, then highest integrity risk, then oldest."""
    return (-float(case["uncertainty"]), -RISK_RANK.get(case["integrity_risk"], 0), case["created_at"], case["case_id"])


def default_scope() -> list[str]:
    return list(CORE_SCOPE)  # raw_submission is never on by default


def scope_problem(include: list[str]) -> str | None:
    if len(set(include)) != len(include) or any(s not in ALLOWED_SCOPE for s in include):
        return "invalid_scope"
    if any(s not in include for s in CORE_SCOPE):
        return "scope_incomplete"
    return None


def expiry_problem(expires_at: datetime, now: datetime) -> str | None:
    if expires_at.tzinfo is None:
        return "expiry_needs_timezone"
    if expires_at <= now:
        return "expiry_in_past"
    if expires_at > now + timedelta(days=MAX_GRANT_DAYS):
        return "expiry_too_far"
    return None


def grant_status(grant: dict, now: datetime) -> str:
    if grant.get("revoked_at"):
        return "revoked"
    if datetime.fromisoformat(grant["expires_at"]) <= now:
        return "expired"
    return "active"


def resolve_decision(outcome: str, new_outcome: str | None, original_outcome: str) -> tuple[str, str] | None:
    """Return (decision, final_outcome) or None when the combination is invalid.

    Accepts the decision kinds, or a bare final outcome which means 'change to that'."""
    if outcome in FINAL_OUTCOMES:
        return "change", outcome
    if outcome == "uphold":
        return "uphold", original_outcome
    if outcome == "needs_more_info":
        return "needs_more_info", "inconclusive"
    if outcome == "change" and new_outcome in FINAL_OUTCOMES:
        return "change", new_outcome
    return None
