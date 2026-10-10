# Module: runner

**Responsibility:** Sandboxed execution of learner Python and SQL with deterministic hidden-test comparison (ADR-0003, SR-01, SR-22).
**Owner:** backend-engineer (stream B) | **Status:** built, awaiting quality-engineer and staff-code-reviewer

## Public surface (`runner.api`)
```
run_python(run_id, task_id, dataset_id, limits_profile, submission) -> RunResult
run_sql(run_id, task_id, dataset_id, limits_profile, submission)    -> RunResult
register_task(task_id, kind, spec_json)       # kind: "python" | "sql"; raises InvalidTaskSpec
isolation_status() -> "container" | "process-fallback" | "unavailable"   # health endpoint / reviewer banner
RunResult{run_id, status, tests[{id, passed, message_safe}], stdout_trunc, isolation_mode, reason}.to_dict()
```
- `status`: `passed | failed_tests | error | blocked | timeout | runner_unavailable`. Failures are returned, never raised.
- `isolation_mode`: `container | process-fallback | none` (none = nothing was executed). Also stored per run in `DATA_DIR/runner/runner.db` (`runs`).
- Request is closed (SR-01): `run_id`, `task_id`, `dataset_id` canonical lowercase UUIDs; `limits_profile` in `sql_check, sql_submit, sql_probe, py_check, py_tests` (python facade takes `py_*`, sql facade `sql_*`); `submission` 1..20480 bytes UTF-8, no NUL. Anything else returns `blocked` with a reason code and no executor is invoked.

### Task spec (hidden tests live only in the runner store)
Python: `{"function": "solve", "tests": [{"id", "args": [..], "kwargs": {..}?, "expected": <json>, "visible": bool?}], "datasets": {<uuid>: {"tests": [..]}}?}`
SQL: `{"setup_sql": "CREATE ...; INSERT ...", "tests": [{"id", "expected_query", "ordered": bool?, "setup_sql"?, "visible": bool?}], "datasets": {<uuid>: {"setup_sql"?, "tests": [..]}}?}`
- If `datasets` is declared, `dataset_id` must be one of its keys (else `blocked: unknown_dataset`). If omitted, any UUID `dataset_id` selects the top-level tests.
- Expected values / expected queries are used only in the trusted parent. The child process receives inputs only (SR-22). Visible tests (`visible: true`) show expected/actual and their stdout; hidden tests return only "passed / not passed" wording.

## Isolation
Order: Docker per run (flags in `infrastructure/docker_executor.py`: `--rm --network none --read-only --cap-drop ALL --security-opt no-new-privileges --pids-limit 64 --memory 128m --cpus 0.5 --user 65534`, tmpfs `/tmp`, no mounts, `--pull never`, run by immutable image ID) else restricted subprocess only if `RUNNER_ALLOW_FALLBACK=true`; otherwise `runner_unavailable` (fail closed).
Config (env only): `DATA_DIR`, `RUNNER_ALLOW_FALLBACK`, `RUNNER_DOCKER_BIN`, `RUNNER_IMAGE` (default `python:3.11-slim`), `RUNNER_IMAGE_ID` (optional pin; mismatch refuses runs).
The child harness (`infrastructure/child_harness.py`) also installs an audit hook (sockets, process creation, file writes, reads outside the interpreter prefix) as defence in depth; any hit returns `blocked` even if learner code catches the error.

## Depends on
No other module. Third-party: none at runtime (stdlib + Docker CLI). Tests: pytest.

## Data owned
`DATA_DIR/runner/runner.db`: `tasks` (hidden specs), `runs` (run_id, task_id, kind, status, isolation_mode, reason, duration). No submission text is stored or logged.

## Known limits
Process fallback has no network or filesystem namespace (audit hook and rlimits/Job Object only). Python timeouts per case need POSIX (`SIGALRM`); on the Windows fallback only the whole-run wall clock applies. One-bit-per-test side channel accepted (SR-22). Concurrency capped at 4 runs (`busy` otherwise).
