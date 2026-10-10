# Module: evidence

**Responsibility:** Append-only, hash-chained evidence ledger using canonicalisation rule `crucible-evidence-event-v1` (copy of `delivery/G3-solution-design/contracts/canonical_hash.py` in `domain/canonical.py`; the 707-byte test vector `sha256:cd2f785f...c0d6` is asserted in `tests/test_ledger.py`).
**Owner:** stream A1 | **Status:** built (tests pass; not yet independently reviewed)

## Public surface (`evidence.api`)
| Member | Contract |
|---|---|
| `append(event_type, learner_id, payload, idempotency_key) -> LedgerEntry` | Validates against EvidenceEvent 0.1 (enums, patterns, ranges, ai_judged / live_screening disclosure rules, extra fields rejected), stores the normalised values (6-place decimals, UTC seconds, NFC, sorted flags), chains `prev_hash`. Idempotent on the key (returns the stored entry). `EvidenceValidationError` otherwise |
| `verify(learner_id=None) -> VerifyResult{ok, entries_checked, first_failure, message}` | Recomputes every hash, sequence and `prev_hash` link. With `learner_id` only that learner's entries are judged |
| `list_for_learner(learner_id) -> list[LedgerEntry]` | ordered by sequence |
| `router` | `GET /audit/ledger/verify` (roles auditor, reviewer) |
| `configure(database_url \| data_dir, clock)`, `reset()` | composition and tests |

Payload extension: `meta` (dict) is stored with the entry and bound to the hash by setting `submission_ref` to the SHA-256 of its canonical JSON when the caller gives no `submission_ref`; `verify` rechecks the binding. Used for recording manifests.
Deviation (documented): for `integrity_flag`, `appeal_filed`, `review_decision` the required task-context fields default to neutral values (`cmp_platform`, `tsk_platform`, `rbr_platform`, `sd_000000000000`, level 1) so platform events fit the same schema.

## Depends on
`identity.api` (role dependency on the verify route).

## Data owned
`ledger(sequence, idempotency_key, event_id, event_type, learner_id, event_json, meta_json, meta_bound, prev_hash, hash, recorded_at)` in `DATA_DIR/evidence.db`. No submission text, only hashes.

## Limits
Deleting the newest entries is not detectable without signed chain heads (roadmap item 1 in hash-canonicalisation.md). Single process: appends are serialised with a lock.
