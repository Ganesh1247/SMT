# Module: hr

**Responsibility:** recruiter portal back end: versioned RoleRequirements, coverage and gaps per competency, evidence page, receipt verification. Never a total, rank, score or recommendation.
**Owner:** stream A2 | **Status:** built (sandbox)

## Public surface (`api/`)
- `router` (recruiter role only): `GET|POST /hr/roles`, `GET|PUT /hr/roles/{id}` (`?version=`; every save increments the version and history is kept), `GET /hr/roles/{id}/results`, `GET /hr/evidence/{learner_alias}/{competency}?role_id=`, `POST /hr/receipts/verify {candidate_ref, competency_id, receipt_hash, role_id?}`.
- `configure(identity, evidence, review=None, clock=None, ids=None, store=None, data_dir=None)`.
- Port protocols: `IdentityPort, ReviewPort, EvidencePort, Principal`.

## Rules enforced
- Role body is validated against `role-requirement.schema.json` (no speed, weights, rank or personal attributes; unknown fields rejected with field-level details). The server assigns role_id, recipient_id (organisation) and version.
- Roles are scoped to the caller's organisation (foreign gives 404).
- The query to Trust carries competency ids only (invariant 14); recipient equals caller (16). The response is schema-validated, otherwise 502 (fail closed).
- Coverage: met, partly_met, not_met, no_evidence. A required competency that is not met or has no evidence is a gap. No grant, expired, revoked and nonexistent give the same empty result or identical 404 (15).
- Receipts verify only items present in the caller's shared evidence.
- Evidence page without `role_id` queries as `role_adhoc` v1, so grants limited to a role (`role_ref`) are not matched.

## Depends on (ports)
`ReviewPort.query_shared_evidence` (default adapter: review.api), `EvidencePort.verify_receipt(hash) -> {status: match|mismatch|unavailable, sequence?}` (the entrypoint bridges this to evidence.api verify), `IdentityPort.authenticate` (Principal carries `org_id`; derived from the user id when absent).

## Data owned
`roles, role_versions` in `DATA_DIR/hr.sqlite3`.
