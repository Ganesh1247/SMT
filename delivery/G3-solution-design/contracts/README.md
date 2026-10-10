<!-- STATUS: DRAFT -->
# Contracts: EvidenceEvent, ShareGrant, SharedEvidence (v0.1)

Owner: principal-architect (Dev 2 owns the folder during build) | Gate: G3 | Date: 2026-10-10 | Reviewer: quality-engineer
These are the only data shapes shared between the Sandbox, the Trust service and the HR portal. Changes need all three developers.

## Who sends what

| Contract | Producer | Consumer | Direction |
|---|---|---|---|
| EvidenceEvent | Sandbox (and Trust for review decisions) | Trust ledger | `POST /events` |
| ShareGrant | Learner via Trust | Trust (enforces) | `POST /grants`, `DELETE /grants/{id}` |
| SharedEvidence | Trust | HR portal | `POST /shared-evidence/query` response |

The HR portal never calls the Sandbox, and never receives anything without an active ShareGrant.

## Invariants (each is tested)

1. **Provenance:** every criterion result carries task, task version, rubric, rubric version, seed, submission hash and date.
2. **Hash, not content:** the ledger stores `submission_ref` (SHA-256), never the submission text.
3. **Pseudonymous only:** no names, emails or phone numbers in any contract; extra fields are rejected.
4. **AI is disclosed:** `ai_judged` requires `ai_disclosure: true`, `confidence` and `model_ref`.
5. **Understanding is separate from outcome:** a probe result carries `understanding_status`; a correct output can be `unconfirmed`.
6. **Flags never lower a score:** `flags` raise review items only.
7. **Consent expires:** a ShareGrant requires `expires_at`; revoke takes effect on the next query.
8. **No aggregate:** SharedEvidence has no overall score, rank or hire field, and the schema rejects them.
9. **Always experimental:** `labels.experimental` is always `true`.
10. **Idempotent delivery:** the same `idempotency_key` is never stored twice, so outbox retries are safe.
11. **Tamper-evident:** Trust adds `ledger.sequence`, `prev_hash` and `hash`; senders never supply them.

## Method labels shown to recruiters

`deterministic_test`, `probe`, `ai_judged`, `live_screening`, `human_review`.

## Files

| File | Purpose |
|---|---|
| `evidence-event.schema.json` | JSON Schema 2020-12 |
| `share-grant.schema.json` | JSON Schema 2020-12 |
| `shared-evidence.schema.json` | JSON Schema 2020-12 |
| `examples/valid.*` | Must validate |
| `examples/invalid.*` | Must be rejected |
| `validate_examples.py` | Checks all examples (`python validate_examples.py`, needs `jsonschema`) |

## Open items

| # | Item | Owner |
|---|---|---|
| 1 | RoleRequirement contract (HR portal to Trust query) is not drafted yet | Dev 3 with Dev 2 |
| 2 | Hash canonicalisation rule (field order, number format) before the ledger is built | Dev 2 |
| 3 | `recipient_id` and `candidate_ref` derivation (per-recipient alias) | Dev 2 |
| 4 | Whether `submission_excerpt` is allowed in the MVP at all | Founder |
| 5 | Competency, task and rubric ID registries | Dev 1 and Dev 2 |
