"""Use cases: rubric evaluation of the L4 interview and short feedback."""
from __future__ import annotations

from ..domain import rubric
from ..domain.injection import strip_instructions
from .ports import FeedbackProvider, ProviderRejected

MAX_TURNS = 40
MAX_TEXT = 4000
MAX_CODE = 20000
_ROLES = {"interviewer", "learner"}


class InvalidInput(ValueError):
    """Boundary validation failure (stable code in .code)."""

    def __init__(self, code: str):
        super().__init__(code)
        self.code = code


class UnsupportedFeedbackKind(InvalidInput):
    pass


def _clip(v, limit: int, code: str) -> str:
    if not isinstance(v, str) or len(v) > limit:
        raise InvalidInput(code)
    return v


class IntelligenceService:
    def __init__(self, provider: FeedbackProvider):
        self._p = provider

    # -- interview evaluation ------------------------------------------------
    def evaluate_interview(self, transcript, solution_code, rubric_version) -> dict:
        if rubric_version not in rubric.SUPPORTED_RUBRIC_VERSIONS:
            raise InvalidInput("unsupported_rubric_version")
        if not isinstance(transcript, list) or len(transcript) > MAX_TURNS:
            raise InvalidInput("invalid_transcript")
        code = _clip(solution_code, MAX_CODE, "invalid_solution_code")

        answers: dict[str, list[str]] = {c: [] for c in rubric.CRITERIA}
        events: list[dict] = []
        for i, turn in enumerate(transcript):
            if not isinstance(turn, dict) or turn.get("role") not in _ROLES:
                raise InvalidInput("invalid_transcript")
            text = _clip(turn.get("text"), MAX_TEXT, "invalid_transcript_text")
            if turn["role"] != "learner":
                continue
            crit = turn.get("criterion")
            if crit not in answers:
                raise InvalidInput("invalid_criterion")
            clean, matched = strip_instructions(text)
            for name in matched:
                events.append({"type": "injection_attempt", "criterion": crit, "turn_index": i, "pattern": name})
            if clean:
                answers[crit].append(clean)
        joined = {c: " ".join(v) for c, v in answers.items()}

        provided = {c: t for c, t in joined.items() if t}
        status = "evaluated"
        results: dict[str, dict] = {}
        try:
            for r in (self._p.evaluate(provided, code, rubric_version) if provided else []):
                results[r["criterion"]] = r
        except ProviderRejected:
            status = "unavailable"

        criteria = []
        for c in rubric.CRITERIA:
            if not joined[c]:
                # Nothing to judge: deterministic, does not depend on the provider.
                criteria.append(_criterion(c, 0, "No answer recorded for this criterion.", 1.0, []))
            elif status == "unavailable" or c not in results:
                status = "unavailable"
                criteria.append(_criterion(c, 0, "Automated assessment unavailable; routed to human review.", 0.0, []))
            else:
                r = results[c]
                criteria.append(_criterion(c, r["score"], r["rationale"], r["confidence"], r["evidence_quotes"]))
        total, passed = rubric.decide({c["criterion"]: c["score0to3"] for c in criteria})
        low = any(c["confidence"] < rubric.CONFIDENCE_FLOOR for c in criteria)
        return {
            "status": status,
            "criteria": criteria,
            "total": total,
            "passed": passed and status == "evaluated",
            "needs_human_review": low or status == "unavailable",
            "model_ref": self._p.model_ref,
            "provider_label": self._p.label,
            "ai_judged": True,
            "ai_disclosure": True,
            "rubric_version": rubric_version,
            "events": events,
        }

    # -- feedback --------------------------------------------------------------
    def feedback(self, kind, payload) -> dict:
        if kind not in _FEEDBACK_VALIDATORS:
            raise UnsupportedFeedbackKind("unsupported_feedback_kind")
        if not isinstance(payload, dict):
            raise InvalidInput("invalid_payload")
        safe, events = _FEEDBACK_VALIDATORS[kind](payload)
        base = {
            "kind": kind,
            "ai_judged": True,
            "ai_disclosure": True,
            "model_ref": self._p.model_ref,
            "provider_label": self._p.label,
            "events": events,
        }
        try:
            out = self._p.feedback(kind, safe)
        except ProviderRejected:
            return {**base, "status": "unavailable", "text": "Automated feedback is unavailable right now.", "confidence": 0.0}
        return {**base, "status": "evaluated", "text": out["text"], "confidence": out["confidence"]}


def _criterion(c: str, score: int, rationale: str, confidence: float, quotes: list[str]) -> dict:
    return {
        "criterion": c,
        "score0to3": max(0, min(rubric.MAX_SCORE, int(score))),
        "rationale": rationale[:500],
        "confidence": max(0.0, min(1.0, float(confidence))),
        "evidence_quotes": list(quotes)[:3],
    }


def _failing_tests(p: dict):
    failed = p.get("failed", [])
    if not isinstance(failed, list) or len(failed) > 20:
        raise InvalidInput("invalid_payload")
    safe = []
    for f in failed:
        if not isinstance(f, dict):
            raise InvalidInput("invalid_payload")
        safe.append({"id": _clip(f.get("id"), 64, "invalid_payload"),
                     "message_safe": _clip(f.get("message_safe", ""), 300, "invalid_payload")})
    passed = p.get("passed_count", 0)
    if not isinstance(passed, int) or isinstance(passed, bool) or not 0 <= passed <= 1000:
        raise InvalidInput("invalid_payload")
    title = _clip(p.get("task_title", ""), 120, "invalid_payload")
    return {"failed": safe, "passed_count": passed, "task_title": title}, []


def _debug_explanation(p: dict):
    text = _clip(p.get("explanation"), MAX_TEXT, "invalid_payload")
    clean, matched = strip_instructions(text)
    events = [{"type": "injection_attempt", "criterion": "debug_explanation", "turn_index": 0, "pattern": m} for m in matched]
    return {"explanation": clean}, events


_FEEDBACK_VALIDATORS = {"failing_tests": _failing_tests, "debug_explanation": _debug_explanation}
