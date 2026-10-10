# Module: scoring

**Responsibility:** Competency estimates and bands (Beta posterior, 10th-90th percentile), gated Proof-of-Skill update, learner profile and evidence projection.
**Owner:** stream A1 | **Status:** built (tests pass; not yet independently reviewed)

## Metric (build-brief section 3)
Per competency (`python`, `sql`): evidence weighted by method (deterministic_test 1.0, probe 0.8, live_screening 0.8, human_review 1.0; `ai_judged` rubric explanations are recorded and counted but not scored), recency half-life 180 days, success fraction = event `score` (else pass 1 / partial 0.5 / fail 0, inconclusive skipped). Estimate = mean of Beta(1+sum w*s, 1+sum w*(1-s)); band = 10th..90th percentile. Never a bare number, never a cross-competency total, no ranking.
Only evidence from a **qualifying attempt** (an attempt whose `seed_id` has a passing `level_outcome` for that level) is scored, so failed attempts never change the estimate.

## Public surface (`scoring.api`)
| Member | Contract |
|---|---|
| `competency_estimate(learner_id, competency, as_of=None) -> Estimate{estimate, lower, upper, as_of, label="Experimental"} \| None` | the **published** snapshot (latest at or before `as_of`); None until published. `ValueError` for unknown competency |
| `apply_gated_update(learner_id, competency) -> None` | publishes a snapshot only if level_outcome pass exists for levels 1-4 of that competency AND `evidence.verify(learner_id)` is ok; else `GateNotMet`. Idempotent for unchanged evidence |
| `profile(learner_id) -> ProfileDTO` | per competency: estimate or None, evidence counts by group (automated_test, ai_rubric, probe, live_screening, human_review), probe counts with the wording "Output verified, understanding unconfirmed", levels passed, label Experimental |
| `router` | `GET /me/profile`, `GET /me/evidence?limit&offset` (learner only, own data, no timing fields) |
| `configure(database_url \| data_dir, evidence, clock)`, `reset()` | composition and tests |

## Depends on
`evidence.api` (read ledger, verify), `identity.api` (roles).

## Data owned
`published_estimates(id, learner_id, competency, estimate, lower, upper, as_of, counts_json, evidence_head)` in `DATA_DIR/scoring.db` (history kept).

## Not built
Integrity risk label (owned by integrity). Probe production (understanding probe) is not implemented in this stream; scoring only consumes `probe_result` events.
