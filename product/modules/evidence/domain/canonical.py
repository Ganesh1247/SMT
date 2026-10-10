"""Copy of contracts/canonical_hash.py (crucible-evidence-event-v1). Do not change the rules;
a new rule means a new CANON_VERSION. Test vector lives in evidence/tests.

Reference implementation of Crucible canonical hashing, v1.

Turns an EvidenceEvent into exactly one byte string, so that two independent
implementations produce the same ledger hash. See hash-canonicalisation.md for
the rules this encodes and why they were chosen.

"""
from __future__ import annotations

import hashlib
import unicodedata
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_EVEN
from typing import Any, Mapping, Sequence

CANON_VERSION = "crucible-evidence-event-v1"
DOMAIN = CANON_VERSION.encode("ascii") + b"\n"
GENESIS = "genesis"
DECIMAL_PLACES = 6

# Ordered, explicit field list. Order here IS the canonical order: it never
# depends on dictionary ordering, and adding a field means a new CANON_VERSION.
FIELDS: tuple[tuple[str, str], ...] = (
    ("schema_version", "str"),
    ("idempotency_key", "str"),
    ("source_system", "str"),
    ("event_type", "str"),
    ("learner_id", "str"),
    ("competency_id", "str"),
    ("level", "int"),
    ("criterion_id", "str"),
    ("method", "str"),
    ("outcome", "str"),
    ("score", "dec"),
    ("confidence", "dec"),
    ("ai_disclosure", "bool"),
    ("understanding_status", "str"),
    ("task_id", "str"),
    ("task_version", "str"),
    ("rubric_id", "str"),
    ("rubric_version", "str"),
    ("seed_id", "str"),
    ("submission_ref", "str"),
    ("rationale", "str"),
    ("flags", "strlist"),
    ("model_ref", "str"),
    ("occurred_at", "ts"),
)


class CanonicalisationError(ValueError):
    """The event cannot be rendered deterministically."""


def _render(name: str, kind: str, value: Any) -> bytes:
    if kind == "str":
        if not isinstance(value, str):
            raise CanonicalisationError(f"{name}: expected string, got {type(value).__name__}")
        return unicodedata.normalize("NFC", value).encode("utf-8")

    if kind == "int":
        if isinstance(value, bool) or not isinstance(value, int):
            raise CanonicalisationError(f"{name}: expected integer, got {type(value).__name__}")
        return str(value).encode("ascii")

    if kind == "bool":
        if not isinstance(value, bool):
            raise CanonicalisationError(f"{name}: expected boolean, got {type(value).__name__}")
        return (b"true" if value else b"false")

    if kind == "dec":
        if isinstance(value, bool) or not isinstance(value, (int, float, Decimal)):
            raise CanonicalisationError(f"{name}: expected number, got {type(value).__name__}")
        # str() first, so a float's shortest round-trip form is what we quantise.
        dec = Decimal(str(value))
        if not dec.is_finite():
            raise CanonicalisationError(f"{name}: non-finite numbers are not allowed")
        quantum = Decimal(1).scaleb(-DECIMAL_PLACES)
        return format(dec.quantize(quantum, rounding=ROUND_HALF_EVEN), "f").encode("ascii")

    if kind == "strlist":
        if isinstance(value, (str, bytes)) or not isinstance(value, Sequence):
            raise CanonicalisationError(f"{name}: expected a list of strings")
        items = [unicodedata.normalize("NFC", v) for v in value]
        if len(set(items)) != len(items):
            raise CanonicalisationError(f"{name}: duplicate entries are not allowed")
        return ",".join(sorted(items)).encode("utf-8")

    if kind == "ts":
        if not isinstance(value, str):
            raise CanonicalisationError(f"{name}: expected an RFC 3339 timestamp string")
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError as exc:
            raise CanonicalisationError(f"{name}: not a valid timestamp: {value}") from exc
        if parsed.tzinfo is None:
            raise CanonicalisationError(f"{name}: timestamp must carry an offset")
        if parsed.microsecond:
            raise CanonicalisationError(f"{name}: sub-second precision is not allowed")
        return parsed.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ").encode("ascii")

    raise CanonicalisationError(f"{name}: unknown field kind {kind!r}")


def canonical_bytes(event: Mapping[str, Any], sequence: int, prev_hash: str) -> bytes:
    """Render an event plus its chain position as the exact bytes to be hashed.

    Absent and null fields are skipped entirely, so an absent field and a
    present-but-empty one never produce the same bytes.
    """
    if isinstance(sequence, bool) or not isinstance(sequence, int) or sequence < 1:
        raise CanonicalisationError("sequence must be an integer of 1 or more")
    if prev_hash != GENESIS and not (
        prev_hash.startswith("sha256:") and len(prev_hash) == 71
    ):
        raise CanonicalisationError(f"prev_hash must be 'genesis' or sha256:<64 hex>, got {prev_hash!r}")

    known = {name for name, _ in FIELDS}
    unknown = sorted(set(event) - known - {"event_id", "ledger"})
    if unknown:
        # Refuse rather than silently leaving a field outside the hash.
        raise CanonicalisationError(f"fields not covered by {CANON_VERSION}: {', '.join(unknown)}")

    out = bytearray(DOMAIN)
    for name, kind in FIELDS:
        if name not in event or event[name] is None:
            continue
        rendered = _render(name, kind, event[name])
        # Length prefix: a value may contain any byte, including the separators,
        # without shifting a field boundary.
        out += f"{name}={len(rendered)}:".encode("ascii") + rendered + b"\n"
    out += f"ledger.sequence={sequence}\n".encode("ascii")
    out += f"ledger.prev_hash={prev_hash}\n".encode("ascii")
    return bytes(out)


def event_hash(event: Mapping[str, Any], sequence: int, prev_hash: str) -> str:
    digest = hashlib.sha256(canonical_bytes(event, sequence, prev_hash)).hexdigest()
    return f"sha256:{digest}"


def verify_chain(entries: Sequence[Mapping[str, Any]]) -> tuple[bool, str]:
    """Check a whole ledger. Returns (ok, message).

    Each entry is an event dict carrying its own 'ledger' block.
    """
    prev = GENESIS
    for position, entry in enumerate(entries, start=1):
        block = entry.get("ledger")
        if not block:
            return False, f"entry {position}: no ledger block"
        body = {k: v for k, v in entry.items() if k not in ("ledger", "event_id")}
        if block["sequence"] != position:
            return False, f"entry {position}: sequence is {block['sequence']}, expected {position}"
        if block["prev_hash"] != prev:
            return False, f"entry {position}: prev_hash does not match the previous entry"
        expected = event_hash(body, block["sequence"], block["prev_hash"])
        if expected != block["hash"]:
            return False, f"entry {position}: hash mismatch, the event was altered after it was recorded"
        prev = block["hash"]
    return True, f"{len(entries)} entries verified"
