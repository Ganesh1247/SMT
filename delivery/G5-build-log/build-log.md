<!-- STATUS: TEMPLATE -->
# Build Log

One entry per slice, appended in order. Use `platform/templates/build-slice.md` for each entry.

<!-- entries below -->

---
<!-- STATUS: DRAFT -->
# Build Log Entry: SLICE-A2 (intelligence, interview, review, hr)

Owner: backend-engineer (stream A2) | Gate: G5 | Version: 0.1 | Date: 2026-10-10 | Reviewer: quality-engineer, then staff-code-reviewer (not yet requested)
Inputs: delivery/G4-delivery-plan/build-brief.md, delivery/G3-solution-design/contracts/ (share-grant, shared-evidence, role-requirement, query envelopes, evidence-event), ux-flows.md sections 3, 5, 6

## Summary
Four modules built test-first under `product/modules/`: `intelligence` (FeedbackProvider port, StubProvider, env-gated AnthropicProvider, L4 rubric evaluator, injection stripping and events), `interview` (5-prompt L4 state machine from the learner's L3 solution, adaptive follow-up, mutation constraint, evaluation hand-off, review routing), `review` (queue, case detail, decisions to ledger, appeals, ShareGrant create/revoke/list, reviewer Range playback via integrity port, contract-validated shared-evidence query), `hr` (versioned RoleRequirement CRUD, coverage and gaps, evidence page, receipt verify). Cross-module calls only through ports with in-memory fakes; default adapters import sibling `api` packages only.

## Files changed
`product/modules/{intelligence,interview,review,hr}/**` (domain, application, infrastructure, api, tests, MODULE.md); `delivery/G3-solution-design/dependency-register.md` (created, DRAFT, approvals PENDING).

## Tests and evidence
Command (from `product/`): `python -m pytest modules/intelligence modules/interview modules/review modules/hr -q` on 2026-10-10 gave `144 passed in 4.62s` (intelligence 34, interview 28, review 41, hr 41). Includes: contract-schema validation of grants, role requirements, evidence events, shared-evidence and query responses; invalid contract examples rejected; no-grant indistinguishable from nonexistent; revoke/expiry/role_ref honoured; thresholds never in the Trust query; injection text ignored for scoring and echoed nowhere; Anthropic adapter via httpx MockTransport (strict JSON, quote check, key not in repr); decision atomicity and retry without duplicate ledger event; interview-to-review-to-assessment hand-off with the real review module; per-module architecture tests (api-only cross-module imports, pure domain).
Not run: real Anthropic call (no key, by design), real browser, SQLite store under load (SqliteDocStore is exercised only through the same interface; no dedicated test yet).

## Deviations from plan
- Persistence uses stdlib sqlite3 document store (no SQLAlchemy) to avoid an extra dependency; behind a `DocStore` port, swap later.
- Anthropic via plain httpx, not the SDK.
- ShareGrant scope must contain the four core items (estimate_band, method_labels, understanding_status, evidence_summary) because SharedEvidence requires those fields; contract allows subsets (open item for Founder/architect).
- Evidence page without `role_id` queries as `role_adhoc`, so role-limited grants do not match.
- `submission_excerpt` never populated (no submission store port).
- Port signatures chosen by A2 (see MODULE.md): learner ids are canonical `lrn_<16 hex>`; `EvidencePort.head()`, `EvidencePort.verify_receipt()`, `IntegrityPort.recording_info/read_recording`, `AssessmentPort.l3_solution(attempt_id, learner_id)` and `record_level4_result(attempt_id, result)` need entrypoint adapters.
- Contract schemas are read from `delivery/G3-solution-design/contracts` at runtime (override env `CRUCIBLE_CONTRACTS_DIR`).

## Verification (quality-engineer)
Pending.

## Review (staff-code-reviewer)
Pending.

---

# Build Log Entry: SLICE-C1 (web frontend: learner exam, reviewer, recruiter, auditor)

Owner: frontend-engineer (stream C) | Gate: G5 | Version: 0.1 | Date: 2026-10-10 | Reviewer: quality-engineer, then staff-code-reviewer (not yet done)
Inputs: delivery/G4-delivery-plan/build-brief.md (s1-5, 8), delivery/G3-solution-design/ux-flows.md (G-rules, 9.1-9.3, A11Y 10)

## Summary
React 18 + TypeScript + Vite app at `product/entrypoints/web/`, talking only to `/api` (Vite dev proxy to 127.0.0.1:8000). Role comes from `GET /me`; `canAccess(role, path)` is deny-by-default. Built:
- Learner: sign in/register; My path (L1-L4, locked/resume/try again); check-in lobby wizard (confirm+track, consent, network speed test with live gauge, camera+mic preview, entire-screen share, full screen, rules, start); exam shell (fixed top bar with alias, L1-L4 progress, recording indicator, connection status, no timers; question navigator with answered/current/marked states; CodeMirror 6 Python/SQL editor with plain-textarea fallback, Run tests panel with test list and row/line diff; right panel with self-view and neutral session notes; full screen gate with re-prompt; finish confirm); Level 4 live interview screen (interviewer prompt, captions/transcript log, SpeechRecognition with typed fallback, turn-taking, read-aloud toggle, scripted label, AI-disclosed summary); level Result with appeal links; Profile (estimate + band + as-of + Experimental label, automated vs live evidence split, partial/empty states); Sharing (grants, preview, confirm-to-stop); Appeals.
- Integrity: detectors for all 12 event types (face_absent only when FaceDetector exists), batcher with retry/backoff to `/attempts/{id}/events`, neutral first-occurrence notices, threshold message "This session is flagged for human review", no accusation wording (tested).
- Recording: MediaRecorder camera+mic and screen, 5 s timeslice, ordered per-stream upload queue with exponential backoff, bounded memory, stall/retry, finalize.
- Reviewer: queue (filter), case detail (original work, AI rationale+confidence, rubric, integrity summary, recording playback via Range endpoint URL, transcript, decision form with confirm).
- Recruiter: roles list, role setup with read-back and error summary, results (coverage/gap, alias order, no ranking), evidence page with verify receipt.
- Auditor: ledger verify (verified / not verified / could not run kept distinct), copy head hash.

## Files changed
`product/entrypoints/web/**` (package.json, vite.config.ts, tsconfig.json, index.html, src/{api,auth,components,integrity,lib,pages,recording,styles,test}); `delivery/G3-solution-design/dependency-register.md` (10 rows, stream C).

## Tests and evidence
Tests written first for logic (red run: 6 files failed to import, "no tests"; then green).
- `npm test` (vitest run): 11 files, 132 tests passed (2026-10-10). Covers precheck evaluation (thresholds, boundaries, entire-screen rule), speed test, event batcher (batch size, interval, retry/backoff, order, single flight, cap), integrity policy wording, upload queue (order, backoff, cap, stall/resume), route guards (deny by default, traversal, lookalikes), detectors (jsdom events), token contrast ratios for light and dark (A11Y-6, computed from the CSS), axe-core runs on login, path, profile, sharing, reviewer queue/case, role setup, role results, evidence, ledger, exam shell, code editor, L4 screen; keyboard tests (Escape closes dialogs, Tab leaves the editor, focus moves to full screen prompt).
- Critical journey (`journey.test.tsx`): path -> check-in (consent before any capture, network, camera/mic, entire screen, full screen, rules) -> exam -> finish -> passed result, plus declined consent, window-share blocked, slow network blocked. This is an integration test in jsdom against a fake fetch, NOT a real-browser end-to-end test.
- `npm run build`: tsc --noEmit clean; vite build OK (index 666 kB JS / 218 kB gzip, CSS 13 kB; chunk-size warning only).

## Deviations from plan / honest gaps
- No real-browser E2E (Playwright not declared; no backend to run against yet). Camera, screen capture, MediaRecorder, SpeechRecognition, FaceDetector, fullscreen are covered by fakes only; nothing was exercised in a real Chrome. No screenshots taken.
- axe-core in jsdom cannot test colour contrast; contrast is checked from tokens only, not rendered pages. 320 px reflow and 200 % zoom not verified in a browser (CSS written for it).
- Not built: assessor health report screens (auditor flow A-2), probe alternative-format request, role edit of existing roles (only create/results), reviewer per-criterion decisions (one decision per case), draft autosave to local storage (answers saved on Save/Next only), code-splitting.
- API contract gaps (response shapes the brief does not define; frontend expectation is in `src/api/types.ts`): `GET /me` fields (role, alias, track); `GET /me/progress` levels[]; item shapes in `GET /attempts/{id}` (kind, options, task_id, starter_code, current_prompt for L4, result); no endpoint to LIST grants (assumed `GET /me/evidence` returns `{evidence_items, grants}`); `DELETE /me/grants` body `{grant_id}`; `POST /me/appeals` body `{event_id?, text}`; review queue/case shapes; hr results shape; receipt verify body `{receipt_hash}` -> `{status, entry}`; ledger verify shape; `POST /precheck/echo` accepts raw bytes; `/precheck/report` response may carry thresholds; events response may carry `{flagged}`; how L4 delivers its first prompt (assumed `current_prompt` on GET attempt); where the `cmp_` competency list comes from (hard-coded Python and SQL).
- Consent text version `2026-10-v1` is a frontend constant; the server should own it.

## Verification (quality-engineer)
Pending.

## Review (staff-code-reviewer)
Pending.

---
<!-- STATUS: DRAFT -->
# Build Log Entry: SLICE-B1 (runner)

Owner: backend-engineer (stream B) | Gate: G5 | Version: 0.1 | Date: 2026-10-10 | Reviewer: quality-engineer, then staff-code-reviewer (not yet requested)
Inputs: delivery/G4-delivery-plan/build-brief.md (s6, s7), ADR-0003, sandbox-environment.md s3.0, sandbox-security-review.md (SR-01, SR-22)

## Summary
Module `runner`: `run_python`, `run_sql`, `register_task` facades. Closed request schema (SR-01); Docker-per-run with fixed argv template, no mounts, run by immutable image ID, optional pin (`RUNNER_IMAGE_ID`); fail closed unless `RUNNER_ALLOW_FALLBACK=true` (then labelled `process-fallback`: `python -I`, scrubbed env, temp cwd, rlimits or Windows Job Object). Learner code runs in a child harness that never receives expected values/queries; the trusted parent compares (SR-22). SQL: fresh in-memory sqlite, authorizer deny-by-default, step budget, single SELECT, row/size caps. `isolation_mode` returned and stored on every run.

## Files changed
product/modules/runner/{domain/models.py, application/run_service.py, infrastructure/{child_harness,capped_process,docker_executor,process_executor,stores}.py, api/__init__.py, MODULE.md, tests/*}; delivery/G3-solution-design/dependency-register.md (Docker, image rows).

## Tests and evidence
`python -m pytest product/modules/runner/tests -q` (2026-10-10): 175 passed in 103s, on a machine with Docker 29.6.1 and python:3.11-slim. `-m docker`: 51 passed (real containers). Escape/abuse suite runs against both executors: import socket/subprocess/ctypes, os.system, network connect, file read/write, fork bomb, infinite loop (module level and in-case), memory bomb, stdout flood via os.write, print flood, forged result line, expected-value scan from learner code, ATTACH/PRAGMA/load_extension/multi-statement/DDL/DML/VACUUM, recursive CTE bomb, cross join, huge rows, huge strings, path traversal ids, unknown/case-variant enum, oversize submission. Container config proven by `docker inspect` on a live container (ReadonlyRootfs, NetworkMode none, CapDrop ALL, no-new-privileges, Pids 64, Memory 128m, NanoCpus 0.5, User 65534, no mounts, Image == resolved ID), in-container checks (no network, read-only root, uid 65534, no docker.sock, pids-limit stops fork loop), pin mismatch refused, zero `crucible-run-*` containers left after runs. Architecture tests: only runner infrastructure imports subprocess; no exec/eval in other layers.
Not verified: Linux host behaviour of the fallback rlimits (code path written, not run here); gVisor; image scanning.

## Deviations from plan
- No separate HTTP runner service: runner is an in-process module whose only Docker access is the CLI via fixed argv (ADR-0003 allows a helper process; build brief s6 specifies module facades). The API process on this laptop can reach Docker; SR-04 stands as documented.
- stdlib sqlite3 instead of SQLAlchemy; no new Python dependency.
- Task spec with no `datasets` accepts any UUID dataset_id (so assessment need not pre-publish a pool); declared `datasets` are strict.
- Per-case timeouts need SIGALRM (container/POSIX); Windows fallback only has the whole-run wall clock.
- The harness audit hook rejects `import socket` etc. as `blocked` even inside the container (defence in depth).

## Verification (quality-engineer)
Pending.

## Review (staff-code-reviewer)
Pending.

---
<!-- STATUS: DRAFT -->
# Build Log Entry: SLICE-B2 (integrity)

Owner: backend-engineer (stream B) | Gate: G5 | Version: 0.1 | Date: 2026-10-10 | Reviewer: quality-engineer, then staff-code-reviewer (not yet requested)
Inputs: delivery/G4-delivery-plan/build-brief.md (s4, s7, s8)

## Summary
Module `integrity`: facades `record_consent, ingest_events, store_chunk, finalize_recording, summary, fingerprint_submit` plus `playback_range` (Range-capable), `verify_recording`, `latest_precheck_passed`, `purge_expired`; `router` for /precheck/payload|echo|report and /attempts/{id}/consent|events|chunks/{stream}/{seq}|recording/finalize with injected `current_user_dependency`. Consent binds attempt to learner; unknown and foreign attempts give identical 404. Pre-check thresholds configurable. Events validated (closed types, size caps, atomic batches). Chunks stored under DATA_DIR/recordings/<attempt_id>/ with sha256 each; manifest hash (canonical JSON) returned for the ledger; tamper check. Summary is reviewer-only, advisory, neutral wording, never touches results. Similarity flag across seeds; retention purge.

## Files changed
product/modules/integrity/{domain/models.py, application/service.py, infrastructure/{sqlite_repo,fs_recordings,config}.py, api/{__init__,http}.py, MODULE.md, tests/*}.

## Tests and evidence
`python -m pytest product/modules/integrity/tests -q` (2026-10-10): 125 passed in 4.1s. Covers pre-check boundaries and neutral wording, event validation/caps, consent/ownership, chunk idempotency/conflict/size/path traversal, manifest hash vector, tamper detection, Range across chunk boundaries and 416, similarity rules, retention, HTTP 401/403/404-uniformity/413/422, architecture rules.
Not verified: real browser MediaRecorder output, real identity module wiring (fake user used), load/rate limiting, encryption at rest.

## Deviations from plan
- stdlib sqlite3 instead of SQLAlchemy.
- `fingerprint_submit` has an optional 4th arg `dataset_id` (needed to tell shared seeds from different seeds); `IntegritySummary` also exposes `risk` alias.
- Attempts are bound to a learner at first consent (integrity cannot import assessment); events/chunks before consent are rejected as 404.
- Auth via dependency override, not an import of identity.

## Verification (quality-engineer)
Pending.

## Review (staff-code-reviewer)
Pending.

---
<!-- STATUS: DRAFT -->
# Build Log Entry: SLICE-A1 (identity, evidence, scoring, assessment, http-api composition root)

Owner: backend-engineer (stream A1) | Gate: G5 | Version: 0.1 | Date: 2026-10-10 | Reviewer: quality-engineer, then staff-code-reviewer (not yet requested)
Inputs: delivery/G4-delivery-plan/build-brief.md (s2, s3, s7, s8, s9), contracts/ (evidence-event schema, canonical_hash.py, hash-canonicalisation.md), sandbox-security-review.md

## Summary
- identity: scrypt accounts, server sessions (HttpOnly, SameSite=Strict), server-side roles, aliases, track, login lockout.
- evidence: append-only hash chain, canonicalisation v1 copied with its test vector, idempotent append, per-learner verify, tamper/deletion detection.
- scoring: Beta estimate + 10-90 band, method weights, 180-day half-life, qualifying-attempt-only evidence, gated publish (4 levels + ledger verify), profile with method-separated counts.
- assessment: item bank (per track L1 12, L2 7, L3 4 tasks x base/mutated, 2 hidden datasets each; rules in bank/rules.json), qualify rules L1-L4, resume/retry with fresh seeds, run limits, integrity pass-through, runner task registration in B's published spec format, L4 result recording and review outcome.
- http-api: FastAPI composition (module wiring by signature, CORS allow-list, Origin check, body limits, security headers, typed error envelope, JSON logs), serve.py, seed.py (random passwords printed once), architecture test.

## Files changed
product/modules/{identity,evidence,scoring,assessment}/** (MODULE.md in each), product/entrypoints/http-api/{main,config,wiring,middleware,serve,seed}.py + tests/, product/architecture-tests/test_module_boundaries.py, product/pyproject.toml, product/entrypoints/http-api/requirements.txt, delivery/G3-solution-design/dependency-register.md (SQLAlchemy, uvicorn, starlette rows), .gitignore (data/).

## Tests and evidence (2026-10-10)
`python -m pytest product/modules/identity product/modules/evidence product/modules/scoring product/modules/assessment product/entrypoints/http-api product/architecture-tests -q` -> 161 passed, 1 failed in 38.8s. Per area: identity 13, evidence 24, scoring 18, assessment 79, http-api 14 (includes 2 end-to-end journeys through the REAL runner for both tracks: L1-L3 with reference solutions, L4 via facade, gated estimate published, ledger verified), architecture 14 (13 pass).
The 1 failure is the architecture test doing its job: `product/modules/interview/tests/test_interview_flow.py` imports `intelligence.infrastructure.stub_provider` (stream A2 must import via `intelligence.api`). Not weakened.
Whole suite `python -m pytest product -q`: 605 passed, 1 failed (same), 148 s.
Smoke: `python product/entrypoints/http-api/serve.py` served /api/health 200 and /api/me 401 with security headers.

## Deviations from plan
- evidence payload accepts `meta` bound to the hash via `submission_ref`; neutral context defaults for integrity_flag / appeal_filed / review_decision (documented in MODULE.md).
- Evidence from failed attempts is excluded from the estimate (qualifying attempts only), to honour "failures never change the score".
- ai_judged rubric explanations (L2) are recorded but not scored; keyword rubric is labelled model_ref `keyword-rubric-1.0.0` unless intelligence supplies one.
- Assessment owns the /attempts/{id}/consent|events|chunks|recording/finalize routes (mounted before integrity's duplicates) so ownership and state checks are in one place; integrity facades are still called through a port.
- Consent scope names follow integrity (camera, microphone, screen, events).

## Not built / partial
Understanding probe production; interview orchestration (A2); rate limiting beyond per-item run cap and login lockout; encryption at rest; migrations are create-if-not-exists only; lockout state is in-memory; deleting the newest ledger entries is undetectable without signed heads.

## Verification (quality-engineer)
Pending.

## Review (staff-code-reviewer)
Pending.
