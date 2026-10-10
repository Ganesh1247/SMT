# Module: intelligence

**Responsibility:** FeedbackProvider port and adapters; rubric evaluation of the Level 4 interview; short rubric-guided feedback. Learner text is data, never instructions.
**Owner:** stream A2 | **Status:** built (sandbox)

## Public surface (`api/`)
| Member | Contract |
|---|---|
| `evaluate_interview(transcript, solution_code, rubric_version) -> Evaluation` | Pre: transcript is a list of `{role: interviewer or learner, criterion, text}`, max 40 turns, 4000 chars each; rubric_version `1.0.0`. Post: five criteria, each `{criterion, score0to3, rationale, confidence, evidence_quotes}`; `total`; `passed` = total >= 10 and no criterion 0; `needs_human_review` when any confidence < 0.6 or status unavailable; `model_ref`, `ai_disclosure=true`, `events` (injection attempts, pattern name only). Errors: `InvalidInput(code)`. A provider failure gives `status="unavailable"`, `passed=false`, `needs_human_review=true` (never a silent fail). |
| `feedback(kind, payload) -> FeedbackResult` | kinds `failing_tests`, `debug_explanation`. Result has `text, confidence, model_ref, ai_judged=true, ai_disclosure=true, status, events`. Errors: `UnsupportedFeedbackKind`, `InvalidInput`. |
| `configure(provider=None)` | composition root; default `provider_from_env(os.environ)`. |
| `router` | empty `APIRouter` (no HTTP surface). |

DTOs are frozen dataclasses with `to_dict()`, `obj["key"]` and `.get`.

## Providers
`StubProvider`: deterministic, offline, `model_ref=stub-deterministic-v1`, label offline-stub. `AnthropicProvider` over httpx, enabled only when env `ANTHROPIC_API_KEY` and `CRUCIBLE_MODEL` are both set; learner text is wrapped in `<untrusted_learner_text>` tags with angle brackets escaped; the reply must be exact JSON of the fixed shape or it is rejected; evidence quotes not found in the learner text are dropped. Instruction-like learner sentences are removed before scoring and reported as events.

## Depends on
None.

## Data owned
None (stateless).

## Events
Returns injection events to the caller; the caller records them as ledger flags.
