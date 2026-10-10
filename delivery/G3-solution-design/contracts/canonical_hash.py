"""Reference implementation of Crucible canonical hashing, v1.

Turns an EvidenceEvent into exactly one byte string, so that two independent
implementations produce the same ledger hash. See hash-canonicalisation.md for
the rules this encodes and why they were chosen.

Self-test:  python canonical_hash.py
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


# --------------------------------------------------------------------------
# Self-test
# --------------------------------------------------------------------------

def _sample() -> dict[str, Any]:
    return {
        "schema_version": "0.1",
        "idempotency_key": "evt-0001-lrn_0a1b2c3d4e5f6071-crt_join_logic",
        "source_system": "sandbox",
        "event_type": "criterion_result",
        "learner_id": "lrn_0a1b2c3d4e5f6071",
        "competency_id": "cmp_data_analysis",
        "level": 2,
        "criterion_id": "crt_join_logic",
        "method": "deterministic_test",
        "outcome": "pass",
        "score": 1,
        "task_id": "tsk_sales_dedupe",
        "task_version": "1.0.0",
        "rubric_id": "rbr_data_analysis",
        "rubric_version": "1.0.0",
        "seed_id": "sd_9f8e7d6c5b4a",
        "submission_ref": "sha256:" + "a" * 64,
        "rationale": "Result set matched the hidden check on all seeded rows.",
        "occurred_at": "2026-10-10T09:15:00Z",
    }


def _main() -> int:
    checks: list[tuple[str, bool, str]] = []

    def check(label: str, ok: bool, detail: str = "") -> None:
        checks.append((label, ok, detail))

    base = _sample()
    h1 = event_hash(base, 1, GENESIS)

    # 1. Key order in the source dict must not change the hash.
    shuffled = dict(reversed(list(base.items())))
    check("key order does not affect the hash", event_hash(shuffled, 1, GENESIS) == h1)

    # 2. Numeric spelling must not change the hash.
    a = dict(base, score=0.6)
    b = dict(base, score=0.600000)
    c = dict(base, score=Decimal("0.6"))
    check(
        "0.6, 0.600000 and Decimal('0.6') agree",
        event_hash(a, 1, GENESIS) == event_hash(b, 1, GENESIS) == event_hash(c, 1, GENESIS),
    )

    # 3. Float artefacts must not change the hash.
    check(
        "0.1+0.2 matches 0.3 at six places",
        event_hash(dict(base, score=0.1 + 0.2), 1, GENESIS)
        == event_hash(dict(base, score=0.3), 1, GENESIS),
    )

    # 4. Timestamp spelling must not change the hash.
    check(
        "+00:00 offset matches Z",
        event_hash(dict(base, occurred_at="2026-10-10T09:15:00+00:00"), 1, GENESIS) == h1,
    )
    check(
        "a non-UTC offset normalises to the same instant",
        event_hash(dict(base, occurred_at="2026-10-10T14:45:00+05:30"), 1, GENESIS) == h1,
    )

    # 5. Flag order must not change the hash.
    check(
        "flag order does not affect the hash",
        event_hash(dict(base, flags=["low_confidence", "probe_failed"]), 1, GENESIS)
        == event_hash(dict(base, flags=["probe_failed", "low_confidence"]), 1, GENESIS),
    )

    # 6. Unicode spelling must not change the hash.
    check(
        "NFC and NFD spellings of the same text agree",
        event_hash(dict(base, rationale="résultat"), 1, GENESIS)
        == event_hash(dict(base, rationale="résultat"), 1, GENESIS),
    )

    # 7. Real changes must change the hash.
    check("a changed score changes the hash", event_hash(dict(base, score=0.9), 1, GENESIS) != h1)
    check(
        "a changed rubric version changes the hash",
        event_hash(dict(base, rubric_version="1.0.1"), 1, GENESIS) != h1,
    )
    check("chain position changes the hash", event_hash(base, 2, GENESIS) != h1)

    # 8. Absent must differ from present-but-empty.
    check(
        "absent rationale differs from empty rationale",
        event_hash({k: v for k, v in base.items() if k != "rationale"}, 1, GENESIS)
        != event_hash(dict(base, rationale=""), 1, GENESIS),
    )

    # 9. A field outside the hashed list must be refused, never ignored.
    try:
        event_hash(dict(base, smuggled="x"), 1, GENESIS)
        check("an uncovered field is refused", False, "it was accepted")
    except CanonicalisationError:
        check("an uncovered field is refused", True)

    # 10. Sub-second precision must be refused rather than silently truncated.
    try:
        event_hash(dict(base, occurred_at="2026-10-10T09:15:00.500Z"), 1, GENESIS)
        check("sub-second precision is refused", False, "it was accepted")
    except CanonicalisationError:
        check("sub-second precision is refused", True)

    # 11. A chain verifies, and tampering is caught at the altered entry.
    chain: list[dict[str, Any]] = []
    prev = GENESIS
    for position in range(1, 4):
        body = dict(base, idempotency_key=f"evt-{position:04d}", level=position if position < 4 else 3)
        digest = event_hash(body, position, prev)
        chain.append(
            dict(
                body,
                ledger={
                    "sequence": position,
                    "prev_hash": prev,
                    "hash": digest,
                    "recorded_at": "2026-10-10T09:20:00Z",
                },
            )
        )
        prev = digest
    ok, message = verify_chain(chain)
    check("a clean chain verifies", ok, message)

    tampered = [dict(entry) for entry in chain]
    tampered[1] = dict(tampered[1], score=0.99)
    ok, message = verify_chain(tampered)
    check("tampering with entry 2 is caught", not ok and "entry 2" in message, message)

    reordered = [chain[0], chain[2], chain[1]]
    ok, _ = verify_chain(reordered)
    check("reordering the chain is caught", not ok)

    width = max(len(label) for label, _, _ in checks)
    failures = 0
    for label, ok, detail in checks:
        suffix = f"  ({detail})" if detail else ""
        print(f"{'ok  ' if ok else 'FAIL'} {label.ljust(width)}{suffix}")
        failures += 0 if ok else 1
    print(f"\n{len(checks) - failures}/{len(checks)} checks passed")
    print(f"canonical form of the sample event, {len(canonical_bytes(base, 1, GENESIS))} bytes")
    print(f"hash: {h1}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(_main())
