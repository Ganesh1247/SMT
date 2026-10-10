"""L4 rubric: five criteria scored 0-3. Pure rules, no I/O."""
from __future__ import annotations

RUBRIC_VERSION = "1.0.0"
SUPPORTED_RUBRIC_VERSIONS = frozenset({RUBRIC_VERSION})
CRITERIA = ("explain", "justify_approach", "complexity", "edge_cases", "adapt")
MAX_SCORE = 3
PASS_TOTAL = 10
CONFIDENCE_FLOOR = 0.6  # below this a criterion is routed to human review


def decide(scores: dict[str, int]) -> tuple[int, bool]:
    """Pass if total >= 10 and no criterion scored 0 (Founder spec)."""
    total = sum(scores[c] for c in CRITERIA)
    passed = total >= PASS_TOTAL and all(scores[c] > 0 for c in CRITERIA)
    return total, passed
