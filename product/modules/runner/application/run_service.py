"""Run orchestration: validate, resolve task, execute in child, compare in the trusted parent.

Learner text only ever travels to an Executor (container or restricted subprocess).
Expected values and expected queries are used here, in the parent, and never put in
the child payload (SR-22).
"""
from __future__ import annotations

import json
import secrets
import threading
import time
from dataclasses import dataclass
from typing import Any, Callable, Protocol

from ..domain import models as m

STDOUT_RETURN_CAP = 4096


@dataclass(frozen=True)
class ChildOutcome:
    kind: str  # ok | timeout | oom | output_too_large | crashed | unavailable
    stdout: bytes = b""


class Executor(Protocol):
    isolation_mode: str

    def execute(self, run_id: str, payload: dict, limits: m.Limits) -> ChildOutcome: ...


class ExecutorSelector(Protocol):
    def select(self) -> Executor | None: ...


class TaskStore(Protocol):
    def put(self, task_id: str, kind: str, spec: dict) -> None: ...
    def get(self, task_id: str) -> tuple[str, dict] | None: ...


class SqlExpected(Protocol):
    def rows(self, setup_sql: str, query: str) -> list: ...


class RunLog(Protocol):
    def record(self, run_id: str, task_id: str, kind: str, status: str, isolation_mode: str,
               reason: str, duration_ms: int) -> None: ...


class RunService:
    def __init__(self, store: TaskStore, selector: ExecutorSelector, sql_expected: SqlExpected,
                 run_log: RunLog, max_concurrent: int = 4, clock: Callable[[], float] = time.monotonic):
        self._store = store
        self._selector = selector
        self._sql_expected = sql_expected
        self._log = run_log
        self._slots = threading.BoundedSemaphore(max_concurrent)
        self._clock = clock
        self._spec_cache: dict[str, tuple[str, m.TaskSpec]] = {}
        self._lock = threading.Lock()

    # ------------------------------------------------------------ registry
    def register_task(self, task_id: Any, kind: Any, spec: Any) -> None:
        if not m.is_canonical_uuid(task_id):
            raise m.InvalidTaskSpec("task_id must be a canonical UUID")
        if isinstance(spec, (str, bytes)):
            try:
                spec = json.loads(spec)
            except ValueError:
                raise m.InvalidTaskSpec("spec is not valid JSON") from None
        parsed = m.parse_task_spec(kind, spec)
        self._store.put(task_id, kind, spec)
        with self._lock:
            self._spec_cache[task_id] = (kind, parsed)

    def _resolve(self, task_id: str) -> tuple[str, m.TaskSpec] | None:
        with self._lock:
            hit = self._spec_cache.get(task_id)
        if hit:
            return hit
        row = self._store.get(task_id)
        if row is None:
            return None
        kind, raw = row
        parsed = m.parse_task_spec(kind, raw)
        with self._lock:
            self._spec_cache[task_id] = (kind, parsed)
        return kind, parsed

    # ------------------------------------------------------------ run
    def run(self, kind: str, run_id: Any, task_id: Any, dataset_id: Any, limits_profile: Any,
            submission: Any) -> m.RunResult:
        started = self._clock()
        rid = run_id if isinstance(run_id, str) else str(run_id)
        result = self._run(kind, run_id, task_id, dataset_id, limits_profile, submission)
        if result.run_id != rid and m.is_canonical_uuid(rid):
            result = m.RunResult(rid, result.status, result.tests, result.stdout_trunc,
                                 result.isolation_mode, result.reason)
        try:
            self._log.record(result.run_id, str(task_id)[:36], kind, result.status, result.isolation_mode,
                             result.reason, int((self._clock() - started) * 1000))
        except Exception:  # noqa: BLE001 - logging must never change a run outcome
            pass
        return result

    def _blocked(self, run_id: Any, reason: str) -> m.RunResult:
        rid = run_id if m.is_canonical_uuid(run_id) else "00000000-0000-0000-0000-000000000000"
        return m.RunResult(rid, "blocked", (), "", "none", reason)

    def _run(self, kind, run_id, task_id, dataset_id, limits_profile, submission) -> m.RunResult:
        try:
            req = m.validate_request(run_id, task_id, dataset_id, limits_profile, submission)
        except m.InvalidRunRequest as exc:
            return self._blocked(run_id, exc.code)
        limits = m.PROFILES[req.limits_profile]
        if limits.kind != kind:
            return self._blocked(req.run_id, "profile_kind_mismatch")
        resolved = self._resolve(req.task_id)
        if resolved is None:
            return self._blocked(req.run_id, "unknown_task")
        task_kind, spec = resolved
        if task_kind != kind:
            return self._blocked(req.run_id, "task_kind_mismatch")
        cases = spec.cases_for(req.dataset_id)
        if cases is None:
            return self._blocked(req.run_id, "unknown_dataset")

        # expected SQL rows are computed here, in the trusted parent, before any child starts
        expected_rows: dict[str, list] = {}
        if kind == "sql":
            try:
                for c in cases:
                    expected_rows[c.id] = self._sql_expected.rows(c.setup_sql, c.expected_query)
            except Exception:  # noqa: BLE001
                return m.RunResult(req.run_id, "error", (), "", "none", "task_misconfigured")

        if not self._slots.acquire(blocking=False):
            return m.RunResult(req.run_id, "runner_unavailable", (), "", "none", "busy")
        try:
            executor = self._selector.select()
            if executor is None:
                return m.RunResult(req.run_id, "runner_unavailable", (), "", "none", "sandbox_unavailable")
            nonce = secrets.token_hex(16)
            payload = self._payload(kind, spec, cases, req, limits, nonce)
            outcome = executor.execute(req.run_id, payload, limits)
        finally:
            self._slots.release()

        mode = executor.isolation_mode
        if outcome.kind == "unavailable":
            return m.RunResult(req.run_id, "runner_unavailable", (), "", "none", "sandbox_unavailable")
        if outcome.kind == "timeout":
            return m.RunResult(req.run_id, "timeout", (), "", mode, "wall_timeout")
        if outcome.kind == "oom":
            return m.RunResult(req.run_id, "error", (), "", mode, "memory_limit")
        if outcome.kind == "output_too_large":
            return m.RunResult(req.run_id, "error", (), "", mode, "output_too_large")
        if outcome.kind != "ok":
            return m.RunResult(req.run_id, "error", (), "", mode, "child_failed")
        report = self._parse_report(outcome.stdout, nonce)
        if report is None:
            return m.RunResult(req.run_id, "error", (), "", mode, "malformed_child_output")
        if report.get("violations"):
            return m.RunResult(req.run_id, "blocked", (), "", mode, "policy_violation")
        if kind == "python":
            return self._grade_python(req, cases, report, mode)
        return self._grade_sql(req, cases, report, expected_rows, mode)

    # ------------------------------------------------------------ payload
    @staticmethod
    def _payload(kind, spec, cases, req, limits, nonce) -> dict:
        base = {"nonce": nonce, "kind": kind, "code": req.submission,
                "max_stdout": STDOUT_RETURN_CAP, "case_seconds": limits.case_seconds}
        if kind == "python":
            # inputs only; `expected` is deliberately absent from this structure
            base["function"] = spec.function
            base["cases"] = [{"id": c.id, "args": list(c.args), "kwargs": dict(c.kwargs)} for c in cases]
        else:
            base["max_rows"] = limits.max_rows
            base["step_budget"] = limits.step_budget
            base["cases"] = [{"id": c.id, "setup_sql": c.setup_sql} for c in cases]
        return base

    @staticmethod
    def _parse_report(stdout: bytes, nonce: str) -> dict | None:
        try:
            text = stdout.decode("utf-8", "replace")
        except Exception:  # noqa: BLE001
            return None
        report = None
        for line in text.splitlines():
            if line.startswith(nonce):
                try:
                    candidate = json.loads(line[len(nonce):])
                except ValueError:
                    continue
                if isinstance(candidate, dict) and candidate.get("v") == 1:
                    report = candidate
        return report

    # ------------------------------------------------------------ grading
    def _grade_python(self, req, cases, report, mode) -> m.RunResult:
        le = report.get("load_error")
        if le:
            code = str(le[0])
            if code == "timeout":
                return m.RunResult(req.run_id, "timeout", (), "", mode, "load_timeout")
            msg = {"syntax": "Your code has a syntax error (%s)." % str(le[1])[:20],
                   "exception": "Your code raised an error when it was loaded.",
                   }.get(code, "Your code could not be run.")
            return m.RunResult(req.run_id, "error", (m.TestOutcome("load", False, msg),),
                               str(report.get("module_stdout", ""))[:STDOUT_RETURN_CAP], mode, "load_error")
        by_id = {r.get("id"): r for r in report.get("results", []) if isinstance(r, dict)}
        outcomes, stdout_parts = [], [str(report.get("module_stdout", ""))]
        timeouts = failures = 0
        for case in cases:
            r = by_id.get(case.id)
            if r is None:
                outcomes.append(m.TestOutcome(case.id, False, "No result was produced."))
                failures += 1
                continue
            if case.visible:
                stdout_parts.append(str(r.get("stdout", "")))
            if r.get("ok") and m.values_equal(r.get("value"), case.expected):
                outcomes.append(m.TestOutcome(case.id, True, "Passed."))
                continue
            failures += 1
            etype = str(r.get("etype", ""))
            if etype == "timeout":
                timeouts += 1
                msg = "This test did not finish in time."
            elif etype == "missing_function":
                msg = "The expected function was not found."
            elif etype == "not_serialisable":
                msg = "The returned value is not a plain value."
            elif etype:
                msg = "The code raised an error on this test."
                if case.visible:
                    msg = ("The code raised %s: %s" % (etype, str(r.get("emsg", ""))))[:200]
            else:
                msg = "The output did not match what was expected."
                if case.visible:
                    msg = ("Expected %r but got %r" % (case.expected, r.get("value")))[:200]
            outcomes.append(m.TestOutcome(case.id, False, msg))
        stdout = "".join(stdout_parts)[:STDOUT_RETURN_CAP]
        if failures == 0:
            status = "passed"
        elif timeouts == failures and timeouts == len(cases):
            status = "timeout"
        else:
            status = "failed_tests"
        return m.RunResult(req.run_id, status, tuple(outcomes), stdout, mode, "")

    def _grade_sql(self, req, cases, report, expected_rows, mode) -> m.RunResult:
        le = report.get("load_error")
        if le:
            return m.RunResult(req.run_id, "error", (), "", mode, "child_failed")
        by_id = {r.get("id"): r for r in report.get("results", []) if isinstance(r, dict)}
        outcomes = []
        etypes = []
        for case in cases:
            r = by_id.get(case.id)
            if r is None:
                outcomes.append(m.TestOutcome(case.id, False, "No result was produced."))
                etypes.append("missing")
                continue
            if r.get("ok"):
                actual = r.get("rows") or []
                if m.rows_equal(actual, expected_rows[case.id], case.ordered):
                    outcomes.append(m.TestOutcome(case.id, True, "Passed."))
                else:
                    outcomes.append(m.TestOutcome(case.id, False, "The query result did not match what was expected."))
                    etypes.append("mismatch")
                continue
            etype = str(r.get("etype", "sql_error"))
            etypes.append(etype)
            msg = {"timeout": "The query took too long to run.",
                   "too_many_rows": "The result was too large to show.",
                   "not_authorized": "Only a single read-only SELECT query is allowed.",
                   "multi_statement": "Only a single read-only SELECT query is allowed.",
                   }.get(etype, "The query could not be run.")
            outcomes.append(m.TestOutcome(case.id, False, msg))
        if not etypes:
            status = "passed"
        elif any(e in ("not_authorized", "multi_statement") for e in etypes):
            status = "blocked"
        elif all(e == "timeout" for e in etypes) and len(etypes) == len(cases):
            status = "timeout"
        elif any(e in ("sql_error", "too_many_rows", "missing") for e in etypes):
            status = "error"
        else:
            status = "failed_tests"
        return m.RunResult(req.run_id, status, tuple(outcomes), "", mode,
                           "policy_violation" if status == "blocked" else "")
