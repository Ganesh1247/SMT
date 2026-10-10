"""Coverage of one role requirement by one competency's shared evidence. Pure, no ranking, no totals.

States: met | partly_met | not_met | no_evidence (contracts README, 'How a RoleRequirement is used')."""
from __future__ import annotations

from datetime import datetime


def _ts(s: str) -> datetime:
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


NO_EVIDENCE_TEXT = "No shared evidence for this competency"


def evaluate(req: dict, shared: dict | None, as_of: datetime) -> dict:
    if shared is None:
        return {"coverage": "no_evidence", "reasons": [NO_EVIDENCE_TEXT], "last_evidence_at": None}
    items = shared["evidence_items"]
    last = shared["last_evidence_at"]
    allowed = req.get("allowed_methods")
    if allowed:
        items = [i for i in items if i["method"] in allowed]
        if not items:
            return {"coverage": "no_evidence", "reasons": ["No shared evidence from the allowed methods"],
                    "last_evidence_at": None}
        last = max((i["occurred_at"] for i in items), key=_ts)
    checks: list[tuple[bool, str]] = []
    if "min_levels_passed" in req:
        top = max(shared["levels_passed"], default=0)
        checks.append((top >= req["min_levels_passed"],
                       f"Level {req['min_levels_passed']} or higher required; highest level passed is {top}"))
    if "min_estimate_lower" in req:
        low = shared["proficiency"]["lower"]
        checks.append((low >= req["min_estimate_lower"],
                       f"Lowest likely value of at least {req['min_estimate_lower']:.2f} required; shared evidence shows {low:.2f}"))
    if "max_evidence_age_days" in req:
        days = (as_of - _ts(last)).days
        checks.append((days <= req["max_evidence_age_days"],
                       f"Newest evidence is {days} days old; window is {req['max_evidence_age_days']}"))
    if req.get("require_understanding_confirmed"):
        status = shared["understanding_status"]
        text = ("Output verified, understanding unconfirmed" if status == "unconfirmed"
                else "Understanding probe not attempted")
        checks.append((status == "confirmed", text))
    reasons = [text for ok, text in checks if not ok]
    if not checks or not reasons:
        state = "met"
    elif len(reasons) == len(checks):
        state = "not_met"
    else:
        state = "partly_met"
    return {"coverage": state, "reasons": reasons, "last_evidence_at": last}


def readback(req: dict) -> str:
    """Plain-language statement of one requirement."""
    name = req["competency_id"].removeprefix("cmp_").replace("_", " ")
    parts = [f"{'Required' if req['priority'] == 'required' else 'Preferred'}: {name}"]
    if "min_levels_passed" in req:
        parts.append(f"level {req['min_levels_passed']} or higher")
    if "min_estimate_lower" in req:
        parts.append(f"lowest likely value of at least {req['min_estimate_lower']:.2f}")
    if "max_evidence_age_days" in req:
        parts.append(f"evidence from the last {req['max_evidence_age_days']} days")
    if req.get("require_understanding_confirmed"):
        parts.append("understanding confirmed")
    if req.get("allowed_methods"):
        parts.append("methods: " + ", ".join(m.replace("_", " ") for m in req["allowed_methods"]))
    return ", ".join(parts) + "."
