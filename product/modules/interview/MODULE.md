# Module: interview

**Responsibility:** Level 4 live screening session: five prompts derived from the learner's own L3 solution, rule-based adaptive follow-up, a mutation constraint, transcript storage, evaluation hand-off.
**Owner:** stream A2 | **Status:** built (sandbox)

## Public surface (`api/`)
- `router`: `POST /interview/{attempt_id}/turn {answer_text?}` returns the next prompt or the summary (the first call has no answer and starts the session; an answer before start gives 409). `GET /interview/{attempt_id}` returns state. Learner role only; unknown or foreign attempt gives an identical 404; answers 1..4000 chars; unknown fields rejected.
- `configure(identity, assessment, evidence, intelligence=None, review=None, integrity=None, clock=None, store=None, data_dir=None)`.
- Port protocols: `IdentityPort, AssessmentPort, IntelligencePort, EvidencePort, ReviewPort, IntegrityPort`, `Principal`.

## Behaviour
Prompts in order: explain, justify_approach, complexity, edge_cases, adapt (the adapt prompt carries the mutation constraint). One follow-up per prompt when the answer is under 12 words or has no expected keyword. At the end: `intelligence.evaluate_interview`, then idempotent, retryable steps: review enqueue, ledger events (`criterion_result` per criterion plus a `level_outcome`, method `live_screening`, ai_disclosure true, hashes only), `assessment.record_level4_result`. Low confidence, provider unavailable, or integrity risk label high gives `pending_review` (no pass or fail is recorded or shown). The learner summary has no timing and no integrity detail.

## Depends on (ports; adapters wired by the entrypoint)
| Port method | Expected sibling |
|---|---|
| `AssessmentPort.l3_solution(attempt_id, learner_id) -> {code, competency_id, task_id, task_version, seed_id}` or None | assessment.api |
| `AssessmentPort.record_level4_result(attempt_id, result)`; result `{status: final or pending_review, passed: bool or None, total, criteria, rubric_version, model_ref, ai_disclosure, case_id}` | assessment.api |
| `EvidencePort.append(event)` | evidence.api (EvidenceEvent v0.1, idempotent on idempotency_key) |
| `IntegrityPort.summary(attempt_id)`, only `risk` is used | integrity.api |
| `IntelligencePort`, `ReviewPort` | default adapters call intelligence.api and review.api |

All `learner_id` values are canonical `lrn_<16 hex>` (derived by sha256 when the identity id is not canonical).

## Data owned
`sessions` documents (transcript, prompts, evaluation, step progress) in `DATA_DIR/interview.sqlite3`. The transcript is learner speech or text; retention follows the recording retention setting (to be applied by the entrypoint).

## Events
Appends EvidenceEvents to the ledger via the evidence port.
