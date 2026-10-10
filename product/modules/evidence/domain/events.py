"""Evidence event validation and normalisation (EvidenceEvent schema 0.1). No I/O."""
from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from datetime import datetime, timezone
from decimal import ROUND_HALF_EVEN, Decimal
from typing import Any, Mapping, Optional

SCHEMA_VERSION = "0.1"
EVENT_TYPES = ("criterion_result", "probe_result", "level_outcome", "integrity_flag",
               "appeal_filed", "review_decision")
METHODS = ("deterministic_test", "probe", "ai_judged", "live_screening", "human_review")
OUTCOMES = ("pass", "fail", "partial", "inconclusive")
UNDERSTANDING = ("confirmed", "unconfirmed", "not_attempted")
FLAGS = ("injection_attempt", "cross_seed_match", "low_confidence", "method_conflict", "probe_failed")
SOURCES = ("sandbox", "trust")

_RE = {
    "learner_id": re.compile(r"^lrn_[a-f0-9]{16}$"),
    "competency_id": re.compile(r"^cmp_[a-z0-9_]{3,40}$"),
    "criterion_id": re.compile(r"^crt_[a-z0-9_]{3,40}$"),
    "task_id": re.compile(r"^tsk_[a-z0-9_]{3,40}$"),
    "task_version": re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+$"),
    "rubric_id": re.compile(r"^rbr_[a-z0-9_]{3,40}$"),
    "rubric_version": re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+$"),
    "seed_id": re.compile(r"^sd_[a-f0-9]{12}$"),
    "submission_ref": re.compile(r"^sha256:[a-f0-9]{64}$"),
}
ALLOWED = {
    "competency_id", "level", "criterion_id", "method", "outcome", "score", "confidence",
    "ai_disclosure", "understanding_status", "task_id", "task_version", "rubric_id",
    "rubric_version", "seed_id", "submission_ref", "rationale", "flags", "model_ref",
    "occurred_at", "source_system", "meta",
}
CONTEXT_REQUIRED = ("competency_id", "level", "method", "outcome", "task_id", "task_version",
                    "rubric_id", "rubric_version", "seed_id")
# Neutral context for event types that are not tied to one task (documented deviation).
NEUTRAL_DEFAULTS = {
    "competency_id": "cmp_platform", "level": 1, "task_id": "tsk_platform",
    "task_version": "1.0.0", "rubric_id": "rbr_platform", "rubric_version": "1.0.0",
    "seed_id": "sd_000000000000",
}
STRICT_TYPES = ("criterion_result", "probe_result", "level_outcome")


class EvidenceValidationError(ValueError):
    """The event does not satisfy the EvidenceEvent contract."""


def _fail(msg: str):
    raise EvidenceValidationError(msg)


def _round6(value: Any, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float, Decimal)):
        _fail(f"{name}: expected number")
    dec = Decimal(str(value))
    if not dec.is_finite():
        _fail(f"{name}: not finite")
    return float(dec.quantize(Decimal("0.000001"), rounding=ROUND_HALF_EVEN))


def _timestamp(value: Any) -> str:
    if not isinstance(value, str):
        _fail("occurred_at: expected string")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        _fail("occurred_at: invalid timestamp")
    if parsed.tzinfo is None:
        _fail("occurred_at: offset required")
    return parsed.astimezone(timezone.utc).replace(microsecond=0).strftime("%Y-%m-%dT%H:%M:%SZ")


def meta_digest(meta: Mapping[str, Any]) -> str:
    raw = json.dumps(meta, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def build_event(event_type: str, learner_id: str, payload: Mapping[str, Any],
                idempotency_key: str, now: datetime) -> tuple[dict[str, Any], Optional[dict]]:
    """Validate and normalise. Returns (event fields to hash and store, meta or None)."""
    if event_type not in EVENT_TYPES:
        _fail("event_type")
    if not isinstance(learner_id, str) or not _RE["learner_id"].match(learner_id):
        _fail("learner_id")
    if not isinstance(idempotency_key, str) or not (16 <= len(idempotency_key) <= 128):
        _fail("idempotency_key")
    unknown = sorted(set(payload) - ALLOWED)
    if unknown:
        _fail("unknown fields: " + ", ".join(unknown))

    data = dict(payload)
    meta = data.pop("meta", None)
    if meta is not None and not isinstance(meta, dict):
        _fail("meta: expected object")
    if event_type not in STRICT_TYPES:
        for key, val in NEUTRAL_DEFAULTS.items():
            data.setdefault(key, val)
    missing = [f for f in CONTEXT_REQUIRED if f not in data or data[f] is None]
    if missing:
        _fail("missing: " + ", ".join(missing))

    event: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "idempotency_key": idempotency_key,
        "source_system": data.get("source_system", "trust" if event_type == "review_decision" else "sandbox"),
        "event_type": event_type,
        "learner_id": learner_id,
    }
    if event["source_system"] not in SOURCES:
        _fail("source_system")

    for name in ("competency_id", "criterion_id", "task_id", "task_version", "rubric_id",
                 "rubric_version", "seed_id", "submission_ref"):
        if data.get(name) is not None:
            val = data[name]
            if not isinstance(val, str) or not _RE[name].match(val):
                _fail(name)
            event[name] = val
    lvl = data["level"]
    if isinstance(lvl, bool) or not isinstance(lvl, int) or not 1 <= lvl <= 4:
        _fail("level")
    event["level"] = lvl
    if data["method"] not in METHODS:
        _fail("method")
    if data["outcome"] not in OUTCOMES:
        _fail("outcome")
    event["method"], event["outcome"] = data["method"], data["outcome"]
    for name in ("score", "confidence"):
        if data.get(name) is not None:
            val = _round6(data[name], name)
            if not 0 <= val <= 1:
                _fail(f"{name}: range")
            event[name] = val
    if data.get("ai_disclosure") is not None:
        if not isinstance(data["ai_disclosure"], bool):
            _fail("ai_disclosure")
        event["ai_disclosure"] = data["ai_disclosure"]
    if data.get("understanding_status") is not None:
        if data["understanding_status"] not in UNDERSTANDING:
            _fail("understanding_status")
        event["understanding_status"] = data["understanding_status"]
    if data.get("rationale") is not None:
        r = data["rationale"]
        if not isinstance(r, str) or len(r) > 1000:
            _fail("rationale")
        event["rationale"] = unicodedata.normalize("NFC", r)
    if data.get("flags") is not None:
        fl = data["flags"]
        if not isinstance(fl, (list, tuple)) or any(f not in FLAGS for f in fl) or len(set(fl)) != len(fl):
            _fail("flags")
        event["flags"] = sorted(fl)
    if data.get("model_ref") is not None:
        m = data["model_ref"]
        if not isinstance(m, str) or len(m) > 80:
            _fail("model_ref")
        event["model_ref"] = unicodedata.normalize("NFC", m)
    event["occurred_at"] = _timestamp(data["occurred_at"]) if data.get("occurred_at") else \
        now.astimezone(timezone.utc).replace(microsecond=0).strftime("%Y-%m-%dT%H:%M:%SZ")

    # Conditional rules from the schema.
    if event["method"] == "ai_judged":
        if event.get("confidence") is None or event.get("model_ref") is None or event.get("ai_disclosure") is not True:
            _fail("ai_judged requires confidence, ai_disclosure=true and model_ref")
    if event["method"] == "live_screening":
        if event.get("confidence") is None or event.get("ai_disclosure") is None:
            _fail("live_screening requires confidence and ai_disclosure")
    if meta is not None and "submission_ref" not in event:
        event["submission_ref"] = meta_digest(meta)
    if event_type == "criterion_result" and ("criterion_id" not in event or "submission_ref" not in event):
        _fail("criterion_result requires criterion_id and submission_ref")
    if event_type == "probe_result" and ("understanding_status" not in event or "submission_ref" not in event):
        _fail("probe_result requires understanding_status and submission_ref")
    if event_type == "review_decision":
        if "rationale" not in event or event["method"] != "human_review" or event["source_system"] != "trust":
            _fail("review_decision requires rationale, method human_review, source trust")
    return event, meta
