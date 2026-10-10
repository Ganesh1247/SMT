# Module: review

**Responsibility:** human-review queue, recorded decisions, appeals, learner consent grants (ShareGrant), and the shared-evidence query that serves recruiters (contracts v0.1).
**Owner:** stream A2 | **Status:** built (sandbox)

## Public surface (`api/`)
- `router` (mount under /api):
  - Learner: `POST|GET /me/grants`, `DELETE /me/grants/{grant_id}`, `POST|GET /me/appeals`.
  - Reviewer: `GET /review/queue?reason&limit&offset`, `GET /review/cases/{id}`, `POST /review/cases/{id}/decision {outcome: uphold|change|needs_more_info (or a final outcome), new_outcome?, reason}`, `GET /review/attempts/{id}/recording/{camera|screen}` (Range, 206/416, no-store).
- `enqueue_case(attempt_id, learner_id, reason, uncertainty, integrity_risk, summary, context) -> case_id` (idempotent per attempt and reason).
- `query_shared_evidence(request, caller_recipient_id) -> SharedEvidenceQueryResponse` (errors: `QueryError`).
- `configure(identity, evidence, scoring, integrity, assessment, clock=None, ids=None, store=None, data_dir=None)`; port protocols re-exported.

## Rules enforced
- Queue order: uncertainty desc, integrity risk desc, oldest first.
- Decision: one per case (409 afterwards); appended to the ledger as `review_decision` (human_review, idempotent key). A failed append leaves the case open and a retry creates no duplicate. Level-4 cases also call `assessment.record_level4_result` with `source=human_review`.
- Appeals only on the learner's own ledger events (foreign or unknown gives an identical 404).
- Grants: expiry required (future, max 365 days, timezone required); scope must contain the four core items; `raw_submission` only when explicitly selected; revoke takes effect on the next query.
- Query: recipient must equal caller; no totals, omitted counts, thresholds or flags; per-recipient aliases; ordered by alias; opaque cursor; a result is omitted when there is no active grant, no gated estimate, or schema validation fails. An access log entry is kept per returned learner.
- `submission_excerpt` is never populated (no submission store in this build).

## Depends on (ports)
`IdentityPort.authenticate/alias_for`, `EvidencePort.append/list_for_learner/head`, `ScoringPort.competency_estimate`, `IntegrityPort.summary/recording_info/read_recording`, `AssessmentPort.record_level4_result`. Contract schemas are read from `delivery/G3-solution-design/contracts` (override with `CRUCIBLE_CONTRACTS_DIR`); it fails closed if they are missing.

## Data owned
`cases, case_index, decisions, appeals, grants, access_log` in `DATA_DIR/review.sqlite3`.
