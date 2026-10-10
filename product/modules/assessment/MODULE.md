# Module: assessment

**Responsibility:** Item bank (JSON under `bank/`), attempts, level state machine, grading orchestration, resume and retry with seeded variants, evidence emission, gated score trigger.
**Owner:** stream A1 | **Status:** built (tests pass; not yet independently reviewed)

## Level rules (config: `bank/rules.json`)
L1 >= 4 of 5 correct | L2 >= 2 of 3 pass hidden tests (explanation rubric recorded, never blocks) | L3 both variants of >= 1 task pass AND >= 70% hidden tests overall | L4 five criteria 0-3, pass if total >= 10 and none 0, low confidence -> `awaiting_review`.
Sequential unlock; a passed level is never repeated; a failed level retries with a new seed (items drawn to avoid earlier ones, shuffled options, other dataset variants) and attempt history is kept. The score is published only by `scoring.apply_gated_update` after L4 passes and the learner's ledger verifies (status `score_update`: `applied` | `withheld`).

## Item bank
Per track (`python`, `data_analyst`): L1 12 items (single / multi / short, some with variants), L2 7 broken programs / queries, L3 4 tasks each with a base and a constraint-mutated stage; 2 hidden test datasets per task. Generated and validated with reference solutions (`tests/reference_solutions.json`, never served).

## Public surface (`assessment.api`)
| Member | Contract |
|---|---|
| `router` | `POST /attempts {level}` (201 new, 200 resume), `GET /attempts/{id}`, `GET /me/progress`, `POST /attempts/{id}/consent|start|submit-item|run|finish|events|recording/finalize`, `POST /attempts/{id}/chunks/{camera|screen}/{seq}`. Learner only; unknown and foreign ids give an identical 404 `{"error":{"code":"not_found","message":"Not found"}}` |
| `get_attempt(attempt_id, learner_id) -> AttemptDTO \| None` | None for unknown or foreign |
| `l3_solution(learner_id) -> {task_id, code, mutated_code, title, language, track, base_prompt, mutated_prompt} \| None` | a passed task whose base and mutated variants both fully passed |
| `record_level4_result(attempt_id, evaluation) -> None` | evaluation `{criteria:[{criterion in explain/justify_approach/complexity/edge_cases/adapt_constraint, score0to3\|score, rationale, confidence}], model_ref, needs_human_review?}`. Applies the L4 rule itself (does not trust a supplied `passed`), writes live_screening evidence, publishes the gated score on pass |
| `record_review_outcome(attempt_id, "pass"\|"fail") -> None` | closes an `awaiting_review` L4 attempt (called by review) |
| `register_tasks() -> int` | registers hidden-test tasks with the runner (`runner.register_task`) |
| `configure(database_url \| data_dir, clock, runner, integrity, intelligence, proctoring_required)`, `reset()` | other modules' api objects are injected (duck-typed) |
| constants | `CONSENT_VERSION`, `REQUIRED_SCOPES` (camera, microphone, screen, events), `RUN_LIMIT` |

## Runner task spec published (matches runner.domain.parse_task_spec)
python: `{"function": name, "datasets": {<dataset uuid>: {"tests": [{"id","args","expected"}]}}}`
sql: `{"datasets": {<dataset uuid>: {"setup_sql": text, "tests": [{"id","expected_query","ordered","setup_sql"?}]}}}`
Task ids are `uuid5(NAMESPACE, track/bank-id/stage)`, dataset ids `uuid5(task, name)`. Profiles: practice runs `py_check`/`sql_check`, graded submits `py_tests`/`sql_submit`.

## Depends on (api only)
`identity.api` (auth), `evidence.api` (append), `scoring.api` (gated update); injected: `runner.api`, `integrity.api`, `intelligence.api` (optional feedback).

## Data owned
`attempts`, `answers`, `runs` in `DATA_DIR/assessment.db`. Answers are stored for the learner's own resume and L4 prompts; the ledger holds only hashes.

## Not built here
The interview (stream A2) and review queue; understanding probe generation; live item-level feedback beyond runner messages.
