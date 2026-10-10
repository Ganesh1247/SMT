<!-- STATUS: DRAFT -->
# Contracts: EvidenceEvent, ShareGrant, SharedEvidence, RoleRequirement (v0.1)

Owner: principal-architect (Dev 2 owns the folder during build) | Gate: G3 | Date: 2026-10-10 | Reviewer: quality-engineer
These are the only data shapes shared between the Sandbox, the Trust service and the HR portal. Changes need all three developers.

## Who sends what

| Contract | Producer | Consumer | Direction |
|---|---|---|---|
| EvidenceEvent | Sandbox (and Trust for review decisions) | Trust ledger | `POST /events` |
| ShareGrant | Learner via Trust | Trust (enforces) | `POST /grants`, `DELETE /grants/{id}` |
| SharedEvidence | Trust | HR portal | `POST /shared-evidence/query` response |
| RoleRequirement | HR portal (recruiter) | HR portal; Trust receives only recipient and competency IDs | `POST /shared-evidence/query` request |

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
12. **Requirements are evidence-only:** RoleRequirement can express competency, level, estimate floor, recency, method and understanding. It has no weights, rank, speed, time or personal-attribute fields, and the schema rejects them.
13. **Gaps, not ranks:** a requirement not met is reported as a gap per competency; there is no combined match score.

## Method labels shown to recruiters

`deterministic_test`, `probe`, `ai_judged`, `live_screening`, `human_review`.

## Files

| File | Purpose |
|---|---|
| `evidence-event.schema.json` | JSON Schema 2020-12 |
| `share-grant.schema.json` | JSON Schema 2020-12 |
| `shared-evidence.schema.json` | JSON Schema 2020-12 |
| `role-requirement.schema.json` | JSON Schema 2020-12 |
| `examples/valid.*` | Must validate |
| `examples/invalid.*` | Must be rejected |
| `validate_examples.py` | Checks all examples (`python validate_examples.py`, needs `jsonschema`) |
| `hash-canonicalisation.md` | The byte-exact hashing rule for ledger events |
| `canonical_hash.py` | Reference implementation and self-test (`python canonical_hash.py`, standard library only) |

## Open items

| # | Item | Owner |
|---|---|---|
| 1 | Query envelope fields (pagination, candidate filter) around RoleRequirement | Dev 3 with Dev 2 |
| 2 | ~~Hash canonicalisation rule~~ drafted: see `hash-canonicalisation.md` (16/16 self-tests pass) | Dev 2 |
| 3 | `recipient_id` and `candidate_ref` derivation (per-recipient alias) | Dev 2 |
| 4 | Whether `submission_excerpt` is allowed in the MVP at all | Founder |
| 5 | Competency, task and rubric ID registries | Dev 1 and Dev 2 |

## How a RoleRequirement is used

1. The recruiter saves a RoleRequirement in the HR portal (`version` increments on every edit).
2. The portal asks Trust for SharedEvidence for the listed competencies, as recipient `recipient_id`. Trust returns only what an active ShareGrant allows.
3. The portal computes coverage per competency, per candidate:

| Result | Meaning |
|---|---|
| `met` | Every stated threshold is satisfied by shared evidence |
| `partly_met` | Some thresholds satisfied (for example level passed but evidence is older than the window) |
| `not_met` | Evidence exists and falls short |
| `no_evidence` | Nothing shared, or no grant for this competency |

4. Results are shown as coverage and gaps with the evidence behind each. A `required` gap is highlighted, and there is no total or ranking.

`min_estimate_lower` applies to the lower edge of the band, so thin evidence cannot pass a high threshold by luck.
