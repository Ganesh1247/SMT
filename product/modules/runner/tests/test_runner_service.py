"""Runner service behaviour with a fake executor (fast, no process or Docker involved)."""
import json
import uuid

import pytest

from runner.application.run_service import ChildOutcome, RunService
from runner.domain import models as m
from runner.infrastructure.stores import SqliteExpected, SqliteStore

U = lambda: str(uuid.uuid4())  # noqa: E731
SECRET_EXPECTED = 987654321


class SpyExecutor:
    isolation_mode = "container"

    def __init__(self, behaviour):
        self.calls = []
        self.behaviour = behaviour

    def execute(self, run_id, payload, limits):
        self.calls.append(payload)
        return self.behaviour(payload)


class FixedSelector:
    def __init__(self, executor):
        self.executor = executor

    def select(self):
        return self.executor


def report(payload, results, violations=(), load_error=None, module_stdout=""):
    body = {"v": 1, "load_error": load_error, "violations": list(violations),
            "module_stdout": module_stdout, "results": results}
    return ChildOutcome("ok", (payload["nonce"] + json.dumps(body) + "\n").encode())


def make(executor, tmp_path):
    store = SqliteStore(tmp_path / "r.db")
    return RunService(store, FixedSelector(executor), SqliteExpected(), store), store


def py_spec(visible=False):
    return {"function": "solve", "tests": [
        {"id": "t1", "args": [3], "expected": SECRET_EXPECTED, "visible": visible},
        {"id": "t2", "args": [4], "expected": 8}]}


def test_should_never_send_expected_values_to_the_child(tmp_path):
    ex = SpyExecutor(lambda p: report(p, []))
    svc, _ = make(ex, tmp_path)
    task = U()
    svc.register_task(task, "python", py_spec())
    svc.run("python", U(), task, U(), "py_tests", "def solve(x): return x")
    assert ex.calls, "child should have been invoked"
    assert str(SECRET_EXPECTED) not in json.dumps(ex.calls[0])
    assert "expected" not in json.dumps(ex.calls[0])


def test_should_pass_when_child_outputs_match_in_trusted_parent(tmp_path):
    def beh(p):
        return report(p, [{"id": "t1", "ok": True, "value": SECRET_EXPECTED, "stdout": ""},
                          {"id": "t2", "ok": True, "value": 8, "stdout": ""}])
    svc, _ = make(SpyExecutor(beh), tmp_path)
    task = U()
    svc.register_task(task, "python", py_spec())
    res = svc.run("python", U(), task, U(), "py_tests", "x=1")
    assert res.status == "passed" and res.isolation_mode == "container"


def test_should_not_leak_hidden_inputs_expected_values_or_hidden_stdout(tmp_path):
    def beh(p):
        return report(p, [{"id": "t1", "ok": True, "value": 1, "stdout": "HIDDEN_INPUT_3"},
                          {"id": "t2", "ok": False, "etype": "ValueError", "emsg": "bad 4", "stdout": "HIDDEN_4"}],
                      module_stdout="hello")
    svc, _ = make(SpyExecutor(beh), tmp_path)
    task = U()
    svc.register_task(task, "python", py_spec())
    res = svc.run("python", U(), task, U(), "py_tests", "x=1")
    blob = json.dumps(res.to_dict())
    assert res.status == "failed_tests"
    for forbidden in (str(SECRET_EXPECTED), "HIDDEN_INPUT_3", "HIDDEN_4", "bad 4", "ValueError"):
        assert forbidden not in blob
    assert res.stdout_trunc == "hello"


def test_should_show_expected_and_actual_only_for_visible_tests(tmp_path):
    def beh(p):
        return report(p, [{"id": "t1", "ok": True, "value": 5, "stdout": "vis"},
                          {"id": "t2", "ok": True, "value": 8, "stdout": ""}])
    svc, _ = make(SpyExecutor(beh), tmp_path)
    task = U()
    svc.register_task(task, "python", py_spec(visible=True))
    res = svc.run("python", U(), task, U(), "py_tests", "x=1")
    assert f"Expected {SECRET_EXPECTED}" in res.tests[0].message_safe
    assert "vis" in res.stdout_trunc


def test_should_fail_closed_when_no_executor_is_available(tmp_path):
    svc, _ = make(None, tmp_path)
    task = U()
    svc.register_task(task, "python", py_spec())
    res = svc.run("python", U(), task, U(), "py_tests", "x=1")
    assert res.status == "runner_unavailable" and res.isolation_mode == "none"


def test_should_block_invalid_request_before_any_executor_call(tmp_path):
    ex = SpyExecutor(lambda p: report(p, []))
    svc, _ = make(ex, tmp_path)
    task = U()
    svc.register_task(task, "python", py_spec())
    bad = [
        dict(run_id="../x", task_id=task, dataset_id=U(), limits_profile="py_tests", submission="x"),
        dict(run_id=U(), task_id="/var/run/docker.sock", dataset_id=U(), limits_profile="py_tests", submission="x"),
        dict(run_id=U(), task_id=task, dataset_id="C:\\x", limits_profile="py_tests", submission="x"),
        dict(run_id=U(), task_id=task, dataset_id=U(), limits_profile="PY_TESTS", submission="x"),
        dict(run_id=U(), task_id=task, dataset_id=U(), limits_profile="py_tests", submission="x" * 30000),
        dict(run_id=U(), task_id=U(), dataset_id=U(), limits_profile="py_tests", submission="x"),  # unknown task
        dict(run_id=U(), task_id=task, dataset_id=U(), limits_profile="sql_check", submission="x"),  # profile kind
    ]
    for kw in bad:
        res = svc.run("python", **kw)
        assert res.status == "blocked", kw
    assert ex.calls == []


def test_should_block_unknown_dataset_for_task_with_declared_variants(tmp_path):
    ex = SpyExecutor(lambda p: report(p, []))
    svc, _ = make(ex, tmp_path)
    task, ds = U(), U()
    svc.register_task(task, "python", {"function": "f", "datasets": {ds: {"tests": [
        {"id": "a", "args": [], "expected": 1}]}}})
    assert svc.run("python", U(), task, U(), "py_tests", "x=1").reason == "unknown_dataset"
    assert svc.run("python", U(), task, ds, "py_tests", "x=1").status in ("passed", "failed_tests", "error")
    assert len(ex.calls) == 1


def test_should_map_policy_violation_to_blocked(tmp_path):
    svc, _ = make(SpyExecutor(lambda p: report(p, [], violations=["import"])), tmp_path)
    task = U()
    svc.register_task(task, "python", py_spec())
    assert svc.run("python", U(), task, U(), "py_tests", "import socket").status == "blocked"


def test_should_ignore_unauthenticated_child_lines_without_nonce(tmp_path):
    forged = {"v": 1, "load_error": None, "violations": [], "module_stdout": "",
              "results": [{"id": "t1", "ok": True, "value": 1}, {"id": "t2", "ok": True, "value": 8}]}
    svc, _ = make(SpyExecutor(lambda p: ChildOutcome("ok", (json.dumps(forged) + "\n").encode())), tmp_path)
    task = U()
    svc.register_task(task, "python", py_spec())
    assert svc.run("python", U(), task, U(), "py_tests", "x=1").status == "error"


def test_should_record_isolation_mode_on_every_run(tmp_path):
    svc, store = make(SpyExecutor(lambda p: report(p, [])), tmp_path)
    task = U()
    svc.register_task(task, "python", py_spec())
    svc.run("python", U(), task, U(), "py_tests", "x=1")
    svc.run("python", "bad", task, U(), "py_tests", "x=1")
    runs = store.runs()
    assert len(runs) == 2 and all(r["isolation_mode"] for r in runs)
    assert runs[0]["isolation_mode"] == "container" and runs[1]["isolation_mode"] == "none"


def test_should_persist_registered_tasks_across_service_restart(tmp_path):
    svc, store = make(SpyExecutor(lambda p: report(p, [])), tmp_path)
    task = U()
    svc.register_task(task, "python", py_spec())
    ex2 = SpyExecutor(lambda p: report(p, []))
    svc2 = RunService(store, FixedSelector(ex2), SqliteExpected(), store)
    svc2.run("python", U(), task, U(), "py_tests", "x=1")
    assert len(ex2.calls) == 1


def test_should_report_busy_when_all_slots_taken(tmp_path):
    store = SqliteStore(tmp_path / "r.db")
    svc = RunService(store, FixedSelector(SpyExecutor(lambda p: report(p, []))), SqliteExpected(), store, max_concurrent=1)
    task = U()
    svc.register_task(task, "python", py_spec())
    assert svc._slots.acquire(blocking=False)
    res = svc.run("python", U(), task, U(), "py_tests", "x=1")
    assert res.status == "runner_unavailable" and res.reason == "busy"


def test_should_reject_malformed_spec_on_register(tmp_path):
    svc, _ = make(None, tmp_path)
    with pytest.raises(m.InvalidTaskSpec):
        svc.register_task("not-a-uuid", "python", py_spec())
    with pytest.raises(m.InvalidTaskSpec):
        svc.register_task(U(), "python", "{not json")


def test_should_expose_facades_with_exact_names():
    from runner import api
    for name in ("run_python", "run_sql", "register_task"):
        assert callable(getattr(api, name))


def test_should_fail_closed_via_facade_without_docker_and_without_fallback(monkeypatch):
    from runner import api
    monkeypatch.setenv("RUNNER_DOCKER_BIN", "definitely-not-docker-xyz")
    api._reset_for_tests()
    task = U()
    api.register_task(task, "python", py_spec())
    res = api.run_python(U(), task, U(), "py_tests", "def solve(x): return x")
    assert res.status == "runner_unavailable"
    assert api.isolation_status() == "unavailable"
