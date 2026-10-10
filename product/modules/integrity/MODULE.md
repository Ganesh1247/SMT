# Module: integrity

**Responsibility:** Consent records, pre-check evaluation, integrity event ingestion, recording storage and playback, reviewer-only summary and similarity flags. Advisory only: it never alters a score or result and never uses accusatory wording.
**Owner:** backend-engineer (stream B) | **Status:** built, awaiting quality-engineer and staff-code-reviewer

## Public surface (`integrity.api`)
```
record_consent(attempt_id, learner_id, version, scopes) -> ConsentRecord     # binds attempt -> learner
ingest_events(attempt_id, learner_id, events[]) -> None                      # batch is atomic, <=100, 5000/attempt
store_chunk(attempt_id, learner_id, stream, seq, data) -> ChunkReceipt{sha256,size,..}
finalize_recording(attempt_id, learner_id) -> {"manifest_hash", "chunks"}   # manifest_hash goes in the ledger
summary(attempt_id) -> IntegritySummary   # REVIEWER-ONLY; counts, risk_label/risk low|medium|high, flags, recording
fingerprint_submit(attempt_id, task_id, answer_values_hash(64 hex), dataset_id=None) -> list[Flag]
# reviewer helpers (caller enforces reviewer role): playback_range(attempt_id, stream, range_header) -> PlaybackSlice{status 200|206|416, headers, body iterator}; verify_recording(attempt_id) -> bool
# misc: latest_precheck_passed(learner_id) -> bool; purge_expired(now=None) -> int
router            # APIRouter, mount under /api
current_user_dependency   # wire: app.dependency_overrides[integrity.api.current_user_dependency] = identity.api.current_user
```
Errors (typed, `.code`): `InvalidInput` 422, `NotFound` 404 (unknown and foreign attempts are identical), `TooLarge` 413, `Conflict` 409.
`current_user` result needs `user_id` (or `id`) and optionally `role` (must be `learner` for attempt routes); object or dict.

### HTTP (all require the injected user)
`GET /precheck/payload?size=` (<= 2 MiB), `POST /precheck/echo`, `POST /precheck/report` (thresholds `PRECHECK_MIN_DOWN_MBPS`=2, `PRECHECK_MIN_UP_MBPS`=1, `PRECHECK_MAX_LATENCY_MS`=400), `POST /attempts/{id}/consent {version, scopes}`, `POST /attempts/{id}/events` (array, 64 KiB), `POST /attempts/{id}/chunks/{camera|screen}/{seq}` (binary, 5 MiB), `POST /attempts/{id}/recording/finalize`.
Event types: focus_loss, tab_hidden, fullscreen_exit, paste, copy, context_menu, devtools_heuristic, multi_display, camera_lost, screen_share_ended, network_drop, face_absent, instruction_like_text. Consent scopes: camera, screen, microphone, events. A stream is accepted only if its scope was consented.

## Rules
Ownership: an attempt is bound to the learner who records consent; every other operation checks it. Recording path `DATA_DIR/recordings/<attempt_id>/<stream>/<seq>.chunk` plus `manifest.json`; attempt ids match `^[A-Za-z0-9][A-Za-z0-9_.:-]{5,63}$` and the resolved path is checked for containment. Manifest hash = sha256 of canonical JSON (sorted keys, compact) of per-chunk sha256/size. Risk weights/thresholds/retention via env: `INTEGRITY_EVENT_WEIGHTS` (JSON), `INTEGRITY_RISK_MEDIUM`=5, `INTEGRITY_RISK_HIGH`=15, `INTEGRITY_RETENTION_DAYS`=30, `INTEGRITY_CHUNK_MAX_BYTES`, `INTEGRITY_MAX_EVENTS`.
Similarity: same task + same answer-values hash, different learner, differing or unknown dataset (seed) -> reviewer-only flag `similar_answer_values`.

## Depends on
No other module. Third-party: fastapi (router only).

## Data owned
`DATA_DIR/integrity/integrity.db` (attempts binding, consents, events, chunks, manifests, fingerprints, flags, prechecks) and `DATA_DIR/recordings/`.

## Known limits
No rate limiting yet; no encryption at rest; recordings are not auto-purged until `purge_expired` is scheduled by the entrypoint.
