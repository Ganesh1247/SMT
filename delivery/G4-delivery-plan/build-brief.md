<!-- STATUS: DRAFT -->
# Build Brief: Crucible functional sandbox (single source for parallel builders)

Owner: Chief of Staff | Gate: G5 | Date: 2026-10-10 | Founder-approved scope (chat): G3+G4 approved with open items; consent-based recording, integrity flags for human review only (never auto-fail); Level 4 = live video + AI interviewer.
Inputs: delivery/G0-intake/*, ux-flows.md, contracts/ (schemas authoritative), ADR-0001/0003, sandbox-environment.md, sandbox-security-review.md, Founder level spec (below).

## 1. Product in one paragraph
A browser exam environment where a learner picks a track (**Python developer** or **Data analyst**), passes four levels in order (L1 Conceptual, L2 Debugging, L3 Applied/Adaptive, L4 Live AI screening), with proctored-style integrity capture (consent, pre-checks, fullscreen, tab-switch/paste events, camera+screen+mic recording), deterministic grading in a sandboxed runner, an intelligence layer for rubric feedback and the L4 interviewer, a gated Proof-of-Skill estimate, and evidence for reviewers, recruiters (HR) and auditors.

## 2. Level rules (Founder spec, authoritative)
| Level | Content | Qualify rule (config in item bank) |
|---|---|---|
| L1 Conceptual | 5 items (predict output, variable change, definitions); single/multi choice + short answer | >= 4 of 5 correct |
| L2 Debugging | 3 broken programs; learner finds error, fixes code, explains | >= 2 of 3 pass hidden tests; explanation graded by rubric (recorded, does not block) |
| L3 Applied | 2 scenario tasks, each with a base problem then a **constraint-mutated variant** (adapt solution); edge cases | both variants of >= 1 task pass AND >= 70% hidden tests overall |
| L4 Live AI screening | Video session, 5 prompts derived from the learner's own L3 solution: explain, justify approach, complexity, edge cases, adapt to a new constraint; follow-ups | rubric: each of 5 criteria scored 0-3; pass if total >= 10 and no criterion 0; low confidence -> human review |
- Sequential unlock. Progress is retained; learner resumes without repeating passed levels. Failed level: retry with a fresh variant (new seed), attempt history kept.
- **Final score update only when all four levels are passed.** Passing one level, incomplete runs and failures never change the score. After L4 pass the platform verifies the ledger chain for that learner, then updates the score.
- Final profile separates **automated-test evidence** from **live-screening evidence** (method counts + labels).

## 3. Scoring metric
- Per competency (`python`, `sql`): evidence items weighted by method (automated 1.0, probe 0.8, live 0.8, human_review 1.0), recency half-life 180 days.
- Estimate = mean of Beta(1 + sum(w*pass), 1 + sum(w*fail)); band = 10th..90th percentile; always returned as {estimate, lower, upper, as_of}; never a bare number, never a total across competencies, no ranking (ux-flows G-1/G-2).
- Understanding probe (predict-output on the learner's own code with altered data) is recorded separately; unconfirmed probe never changes the output result.
- Integrity summary (reviewer-only): counts per event type + risk label low/medium/high from weighted counts; it NEVER modifies score or results automatically.

## 4. Integrity and recording policy
- Explicit consent screen before any capture; consent record stored (version, time, scopes). Declining = cannot start proctored attempt (no penalty text).
- Pre-checks (must pass to start): network speed (download + upload + latency vs `/api/precheck/*`, thresholds configurable, defaults >= 2 Mbps down, >= 1 Mbps up, < 400 ms), camera + mic permission with live preview, screen share must be entire display (`displaySurface === "monitor"`), fullscreen granted, supported browser (Chromium), single display (`screen.isExtended === false`) where API available.
- During attempt: fullscreen enforced (re-prompt on exit), events captured: `focus_loss`, `tab_hidden`, `fullscreen_exit`, `paste`, `copy`, `context_menu`, `devtools_heuristic`, `multi_display`, `camera_lost`, `screen_share_ended`, `network_drop`, `face_absent` (FaceDetector API if available), each with monotonic timestamp and attempt/item id. Warn on first occurrences; at threshold show "This session is flagged for human review" and continue. **No auto-fail, no accusation wording** (never: cheat, misconduct, suspicious, AI detected).
- Recording: MediaRecorder camera+mic and screen streams, chunked upload every 5 s; server stores files under `DATA_DIR/recordings/<attempt_id>/`, sha256 per chunk, manifest hash appended to ledger; reviewer playback via authenticated Range endpoint; retention days configurable.
- Similarity: answer-value fingerprints compared across seeds -> reviewer-only flag `similar_answer_values`.

## 5. Intelligence layer
- Port `FeedbackProvider` (explain failing tests, rubric-guided feedback for debugging explanations, L4 evaluation). Adapters: `StubProvider` (deterministic, offline, labelled) and `AnthropicProvider` (enabled only if env `ANTHROPIC_API_KEY` set; model id from env `CRUCIBLE_MODEL`; learner text sent as delimited untrusted data; output parsed to fixed JSON `{criterion, score, rationale, confidence}` or rejected). Keys from env only. Every AI result carries `ai_judged`, `ai_disclosure=true`, model_ref.
- L4 interviewer (`interview` module): builds prompts from the learner's L3 submission (function names, loops, data structures) + a mutation constraint; adaptive follow-up chosen by rules on previous answer length/keyword coverage (stub) or the provider; transcript via browser SpeechRecognition (fallback typed answer); stores transcript + evaluation + rubric version; confidence low or integrity risk high -> review queue.
- Prompt-injection: learner text never treated as instructions; instruction-like text logged as an event and ignored for scoring.

## 6. Runner (sandbox)
- Python and SQL tasks. Isolation order: **Docker per run** if `docker` usable (flags: `--rm --network none --read-only --cap-drop ALL --security-opt no-new-privileges --pids-limit 64 --memory 128m --cpus 0.5 --user 65534`, tmpfs /tmp, image `python:3.11-slim`), else **restricted subprocess** (`python -I`, rlimits/Job-object-style timeout, cwd temp, env scrubbed) with `isolation_mode` = `container` | `process-fallback` recorded on every run and shown to reviewers. Fallback must be explicit in config (`RUNNER_ALLOW_FALLBACK=true`), otherwise runs fail closed.
- Runner request is closed: `{run_id: uuid, task_id: uuid, dataset_id: uuid, limits_profile: enum, submission: string<=20KB via stdin}`; no paths or container args from callers (SR-01). Hidden tests live only in the runner-side task store and are applied by comparing outputs in the trusted parent; learner code runs in a child process that never receives expected values (SR-22).
- SQL: fresh in-memory sqlite, deny-by-default authorizer (SELECT/READ only), progress-handler step budget, single statement, row/size caps.
- Result: `{status: passed|failed_tests|error|blocked|timeout|runner_unavailable, tests: [{id, passed, message_safe}], stdout_trunc, isolation_mode}` - hidden test inputs/expected values never returned.

## 7. Modules (product/modules/<name>/ with domain/application/infrastructure/api/tests + MODULE.md; cross-module via api/ only)
| Module | Owner stream | Responsibility |
|---|---|---|
| identity | A | accounts, password hashing (stdlib scrypt), server sessions (HttpOnly SameSite=Strict cookie), roles learner/reviewer/auditor/recruiter assigned server-side only, track preference |
| assessment | A | item bank (JSON seed files under module), attempts, level state machine, grading orchestration, resume/retry with seeds |
| scoring | A | estimates/bands, gated Proof-of-Skill update, profile projection |
| evidence | A | append-only hash-chained ledger (reuse delivery/G3-solution-design/contracts/canonical_hash.py rule; copy implementation into module, keep test vector), verify |
| review | A | queue ordered by uncertainty/risk, decisions, appeals, consent grants (ShareGrant) , recruiter shared-evidence queries per contracts |
| intelligence | A | FeedbackProvider port + adapters, rubric evaluator |
| interview | A | L4 session orchestration + evaluation |
| runner | B | sandbox execution (section 6) |
| integrity | B | consent record, pre-check endpoints, event ingestion, recording storage + playback, summary + similarity flags |
Entry point: `product/entrypoints/http-api/` (FastAPI app composition; stream A owns wiring; B exposes `runner.api`, `integrity.api` facades). Frontend: `product/entrypoints/web/` (stream C).

### Facades B must expose (A calls these)
```
runner.api.run_python(run_id, task_id, dataset_id, limits_profile, submission) -> RunResult
runner.api.run_sql(run_id, task_id, dataset_id, limits_profile, submission) -> RunResult
runner.api.register_task(task_id, kind, spec_json)  # called by assessment seed loader; stores hidden tests runner-side
integrity.api.record_consent(attempt_id, learner_id, version, scopes) -> ConsentRecord
integrity.api.ingest_events(attempt_id, learner_id, events[]) -> None
integrity.api.store_chunk(attempt_id, learner_id, stream("camera"|"screen"), seq, bytes) -> ChunkReceipt
integrity.api.finalize_recording(attempt_id, learner_id) -> {manifest_hash, chunks}
integrity.api.summary(attempt_id) -> IntegritySummary   # reviewer-only
integrity.api.fingerprint_submit(attempt_id, task_id, answer_values_hash) -> list[Flag]
```

## 8. HTTP API (JSON, `/api`, cookie session; every route authorises by server-side role + object ownership; unknown or foreign IDs return identical 404)
```
POST /auth/register {email,password,display_name?}   -> learner only
POST /auth/login | POST /auth/logout | GET /me
PUT  /me/track {track:"python"|"data_analyst"}        # preference only
GET  /precheck/payload?size=...   POST /precheck/echo   POST /precheck/report {down_mbps,up_mbps,latency_ms,camera,mic,screen_surface,fullscreen,single_display,browser}
POST /attempts {level}  -> {attempt_id,consent_required}    GET /attempts/{id}   GET /me/progress
POST /attempts/{id}/consent {version,scopes}
POST /attempts/{id}/start | /submit-item {item_id,answer,explanation?} | /run {task_id,code} | /finish
POST /attempts/{id}/events [..]   POST /attempts/{id}/chunks/{stream}/{seq} (binary)   POST /attempts/{id}/recording/finalize
POST /interview/{attempt_id}/turn {answer_text}  -> next prompt | summary
GET  /me/profile    GET /me/evidence    POST|DELETE /me/grants    POST /me/appeals   GET /me/appeals
GET  /review/queue  GET /review/cases/{id}  POST /review/cases/{id}/decision {outcome,reason}  GET /review/attempts/{id}/recording/{stream}  (Range)
GET  /hr/roles POST /hr/roles   GET /hr/roles/{id}/results   GET /hr/evidence/{learner_alias}/{competency}   POST /hr/receipts/verify
GET  /audit/ledger/verify
GET  /health
```
Responses never include hidden test data, answer keys, other learners' data, speed/"time taken" in learner views, or personal contact details outside the learner's own session (aliases `cnd_...` elsewhere).

## 9. Engineering rules
- Python 3.11, FastAPI, Pydantic v2, SQLAlchemy 2 + SQLite (one DB file per module group under `DATA_DIR`, default `./data`, git-ignored), pytest. Frontend: React 18 + TypeScript + Vite + CodeMirror 6; Vitest; axe-core in tests.
- Tests first (red-green); architecture test that fails on cross-module imports not via `api/`; no secrets in files (env only); every third-party dependency recorded in `delivery/G3-solution-design/dependency-register.md`; append an entry per slice to `delivery/G5-build-log/build-log.md` with real test output.
- Content: neutral integrity wording; Experimental label beside every estimate; probe unconfirmed wording exactly "Output verified, understanding unconfirmed".
- Do not edit: reference/, delivery/state/lifecycle-state.yaml, other streams' modules. Report honestly what is built vs partial.
