<!-- STATUS: DRAFT -->
# Hash Canonicalisation: `crucible-evidence-event-v1`

Owner: principal-architect (Dev 2 implements in Trust `ledger`) | Gate: G3 | Date: 2026-10-10 | Reviewer: security-engineer, then quality-engineer
Inputs: evidence-event.schema.json; reference implementation `canonical_hash.py`

## Purpose
The ledger is only tamper-evident if every implementation turns the same event into exactly the same bytes. JSON does not guarantee that: key order, number spelling (`0.6` vs `0.60`), timestamp offsets and Unicode forms all vary. This rule fixes one byte form per event.

## Decision
Use an **explicit, versioned field list with per-type rendering rules**, not general-purpose JSON canonicalisation.

| Option | Verdict | Reason |
|---|---|---|
| **Explicit field list (chosen)** | Adopt for MVP | Implementable identically in any language in under 100 lines; readable by eye; no float-formatting library needed |
| RFC 8785 JSON Canonicalization Scheme | Roadmap | The standard choice, but needs ECMAScript-exact number formatting and UTF-16 key ordering; Python's standard library does not provide either, so it adds a dependency and a subtle failure mode within 24 hours. I did not verify the RFC text directly. |
| Hash the raw request body | Rejected | Two senders that spell the same event differently would produce different hashes |

## Rules

### 1. Domain separation
The bytes start with `crucible-evidence-event-v1` and a newline. A hash for one purpose can never be replayed as another.

### 2. Field order
Fields are emitted in the fixed order below. Dictionary order never matters.

`schema_version, idempotency_key, source_system, event_type, learner_id, competency_id, level, criterion_id, method, outcome, score, confidence, ai_disclosure, understanding_status, task_id, task_version, rubric_id, rubric_version, seed_id, submission_ref, rationale, flags, model_ref, occurred_at`

### 3. Rendering per type

| Type | Fields | Rule |
|---|---|---|
| String | most fields | Unicode NFC, then UTF-8 |
| Integer | `level` | Base 10, no sign or leading zeros; booleans refused |
| Decimal | `score`, `confidence` | Exactly 6 decimal places, round half to even, from the value's shortest string form; NaN and infinity refused |
| Boolean | `ai_disclosure` | `true` or `false` |
| String list | `flags` | NFC each, duplicates refused, sorted ascending, joined with `,` |
| Timestamp | `occurred_at` | Converted to UTC, rendered `YYYY-MM-DDTHH:MM:SSZ`; missing offset or sub-second precision refused |

### 4. Absent fields
Absent or `null` fields are **skipped entirely**. A present-but-empty value is emitted with length 0, so "absent" and "empty" never collide.

### 5. Length-prefixed lines
Each field is emitted as `name=<byte length>:<value>` followed by a newline. Because the length is explicit, a value may contain newlines, `=` or `:` without shifting any field boundary.

### 6. Chain position
After the fields, two lines are appended: `ledger.sequence=<n>` and `ledger.prev_hash=<hash or genesis>`. An event therefore cannot be moved to another position without changing its hash.

### 7. Hash
`sha256:` followed by the lowercase hex SHA-256 of the bytes.

### 8. Unknown fields are refused
If an event contains a field that is not in the list (other than `event_id` and `ledger`), canonicalisation **fails** rather than silently leaving the field outside the hash.

### 9. Store what you hash
Trust normalises on append and **stores the normalised values** (six-place decimals, UTC timestamps, NFC text, sorted flags). Without this, two different stored values could round to the same hash, for example `0.6` and `0.6000004`, and a change below six places would go undetected.

### 10. Versioning
Any change to the field list or a rendering rule creates a new version string (`...-v2`). Each event's version is recorded, and old entries keep verifying under their own version.

## Verification
To verify a ledger: start with `prev_hash = genesis`; for each entry in sequence order, check that `sequence` is the expected position, `prev_hash` equals the previous entry's hash, and the recomputed hash equals the stored hash. The first failure names the altered entry.

## Test vector
The sample event in `canonical_hash.py` (criterion result, sequence 1, prev_hash `genesis`) renders to 707 bytes with hash:

`sha256:cd2f785ff97fa7a4a94446a507a7a6d2e514ab54b1ae0a22f05a8027c81dc0d6`

Any second implementation (for example in the HR portal, to verify receipts) must reproduce this value exactly.

## Self-test results (`python canonical_hash.py`, 2026-10-10)
16 of 16 checks passed:

| Property | Result |
|---|---|
| Key order, number spelling (`0.6`, `0.600000`, `Decimal`), float artefacts (`0.1+0.2`), timestamp offsets, flag order and Unicode form do not change the hash | Pass |
| A changed score, rubric version or chain position changes the hash | Pass |
| Absent and empty values hash differently | Pass |
| Unknown fields and sub-second timestamps are refused | Pass |
| A clean three-entry chain verifies; tampering with entry 2 is caught at entry 2; reordering is caught | Pass |

## Limits
- The chain proves the log was not altered **after** recording. It does not prove the event was true when written, and in the prototype the operator controls both writing and verifying. Independent assurance would need an outside party to hold signed chain heads (roadmap).
- Six decimal places is a precision decision. Scores more precise than that are rounded on ingest by design.

## Open items
| # | Item | Owner |
|---|---|---|
| 1 | Sign chain heads with a Trust key so receipts can be checked offline | Dev 2 (stretch) |
| 2 | Equivalent rule for ShareGrant changes, if grants are also chained | Dev 2 |
| 3 | Independent reimplementation in the HR portal language to confirm the test vector | Dev 3 |
