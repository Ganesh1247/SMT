"""Runner domain: closed request schema (SR-01), task specs, results, output comparison.

Pure rules only: no I/O, no frameworks, no subprocess.
"""
from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass, field
from typing import Any, Mapping

MAX_SUBMISSION_BYTES = 20 * 1024
MAX_SPEC_TESTS = 100
MAX_SETUP_SQL_BYTES = 1024 * 1024

_UUID_RE = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.ASCII)
_TEST_ID_RE = re.compile(r"^[A-Za-z0-9_.-]{1,40}$", re.ASCII)
_IDENT_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]{0,63}$", re.ASCII)

STATUSES = ("passed", "failed_tests", "error", "blocked", "timeout", "runner_unavailable")
ISOLATION_MODES = ("container", "process-fallback", "none")


class InvalidRunRequest(ValueError):
    """Raised for any request that violates the closed schema. Carries a stable code only."""

    def __init__(self, code: str):
        super().__init__(code)
        self.code = code


class InvalidTaskSpec(ValueError):
    pass


@dataclass(frozen=True)
class Limits:
    """Constant limits selected by the closed `limits_profile` enum."""
    kind: str  # python | sql
    wall_seconds: float
    case_seconds: float
    memory_mb: int
    max_output_bytes: int
    step_budget: int  # sqlite progress-handler callbacks (x1000 VM ops each)
    max_rows: int


PROFILES: dict[str, Limits] = {
    "sql_check": Limits("sql", 15, 5, 128, 256 * 1024, 2000, 1000),
    "sql_submit": Limits("sql", 20, 8, 128, 256 * 1024, 5000, 1000),
    "sql_probe": Limits("sql", 15, 5, 128, 256 * 1024, 2000, 1000),
    "py_check": Limits("python", 15, 2, 128, 256 * 1024, 0, 0),
    "py_tests": Limits("python", 30, 3, 128, 256 * 1024, 0, 0),
}


@dataclass(frozen=True)
class RunRequest:
    run_id: str
    task_id: str
    dataset_id: str
    limits_profile: str
    submission: str


def is_canonical_uuid(value: Any) -> bool:
    return isinstance(value, str) and bool(_UUID_RE.match(value))


def validate_request(run_id: Any, task_id: Any, dataset_id: Any, limits_profile: Any, submission: Any) -> RunRequest:
    """Closed schema: canonical lowercase UUIDs, enum profile, size-capped valid UTF-8 text."""
    for value in (run_id, task_id, dataset_id):
        if not is_canonical_uuid(value):
            raise InvalidRunRequest("invalid_id")
    if not isinstance(limits_profile, str) or limits_profile not in PROFILES:
        raise InvalidRunRequest("invalid_limits_profile")
    if not isinstance(submission, str) or not submission:
        raise InvalidRunRequest("invalid_submission")
    try:
        encoded = submission.encode("utf-8")
    except UnicodeEncodeError:
        raise InvalidRunRequest("invalid_submission") from None
    if len(encoded) > MAX_SUBMISSION_BYTES:
        raise InvalidRunRequest("submission_too_large")
    if "\x00" in submission:
        raise InvalidRunRequest("invalid_submission")
    return RunRequest(run_id, task_id, dataset_id, limits_profile, submission)


# ---------------------------------------------------------------- results

@dataclass(frozen=True)
class TestOutcome:
    __test__ = False  # not a pytest class
    id: str
    passed: bool
    message_safe: str


@dataclass(frozen=True)
class RunResult:
    run_id: str
    status: str
    tests: tuple[TestOutcome, ...] = ()
    stdout_trunc: str = ""
    isolation_mode: str = "none"
    reason: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "status": self.status,
            "tests": [{"id": t.id, "passed": t.passed, "message_safe": t.message_safe} for t in self.tests],
            "stdout_trunc": self.stdout_trunc,
            "isolation_mode": self.isolation_mode,
            "reason": self.reason,
        }


# ---------------------------------------------------------------- task specs

@dataclass(frozen=True)
class PyCase:
    id: str
    args: tuple
    kwargs: Mapping[str, Any]
    expected: Any
    visible: bool = False


@dataclass(frozen=True)
class SqlCase:
    id: str
    setup_sql: str
    expected_query: str
    ordered: bool = False
    visible: bool = False


@dataclass(frozen=True)
class TaskSpec:
    kind: str
    function: str = ""
    default_cases: tuple | None = None
    dataset_cases: Mapping[str, tuple] = field(default_factory=dict)
    has_variants: bool = False

    def cases_for(self, dataset_id: str) -> tuple | None:
        """Cases for a dataset, or None when the (task, dataset) pair is not published."""
        if dataset_id in self.dataset_cases:
            return self.dataset_cases[dataset_id]
        if not self.has_variants:
            return self.default_cases
        return None


def _require(cond: bool, msg: str) -> None:
    if not cond:
        raise InvalidTaskSpec(msg)


def _check_test_id(t: dict, seen: set) -> None:
    _require(isinstance(t.get("id"), str) and _TEST_ID_RE.match(t["id"]) is not None, "bad test id")
    _require(t["id"] not in seen, "duplicate test id")
    seen.add(t["id"])


def _parse_py_cases(tests: Any) -> tuple:
    _require(isinstance(tests, list) and 1 <= len(tests) <= MAX_SPEC_TESTS, "tests must be a list of 1..100")
    out: list[PyCase] = []
    seen: set = set()
    for t in tests:
        _require(isinstance(t, dict) and set(t) <= {"id", "args", "kwargs", "expected", "visible"}, "bad test")
        _check_test_id(t, seen)
        args = t.get("args", [])
        kwargs = t.get("kwargs", {})
        _require(isinstance(args, list), "args must be a list")
        _require(isinstance(kwargs, dict) and all(isinstance(k, str) for k in kwargs), "kwargs must be an object")
        _require("expected" in t, "expected missing")
        out.append(PyCase(t["id"], tuple(args), dict(kwargs), t["expected"], bool(t.get("visible", False))))
    return tuple(out)


def _parse_sql_cases(tests: Any, default_setup: str) -> tuple:
    _require(isinstance(tests, list) and 1 <= len(tests) <= MAX_SPEC_TESTS, "tests must be a list of 1..100")
    out: list[SqlCase] = []
    seen: set = set()
    for t in tests:
        _require(isinstance(t, dict) and set(t) <= {"id", "expected_query", "ordered", "setup_sql", "visible"}, "bad test")
        _check_test_id(t, seen)
        _require(isinstance(t.get("expected_query"), str) and t["expected_query"].strip() != "", "expected_query")
        setup = t.get("setup_sql", default_setup)
        _require(isinstance(setup, str) and setup.strip() != "", "setup_sql required")
        _require(len(setup.encode("utf-8")) <= MAX_SETUP_SQL_BYTES, "setup_sql too large")
        out.append(SqlCase(t["id"], setup, t["expected_query"], bool(t.get("ordered", False)), bool(t.get("visible", False))))
    return tuple(out)


def parse_task_spec(kind: Any, spec: Any) -> TaskSpec:
    """Validate a runner-side task spec (hidden tests live only here)."""
    _require(kind in ("python", "sql"), "unknown kind")
    _require(isinstance(spec, dict), "spec must be an object")
    allowed = {"function", "tests", "datasets"} if kind == "python" else {"setup_sql", "tests", "datasets"}
    _require(set(spec) <= allowed, "unknown spec field")
    datasets = spec.get("datasets")
    has_variants = datasets is not None
    by_dataset: dict[str, tuple] = {}
    if kind == "python":
        function = spec.get("function")
        _require(isinstance(function, str) and _IDENT_RE.match(function) is not None, "bad function name")
        default = _parse_py_cases(spec["tests"]) if "tests" in spec else None
        if has_variants:
            _require(isinstance(datasets, dict) and 1 <= len(datasets) <= 1000, "datasets must be an object")
            for ds_id, ds in datasets.items():
                _require(is_canonical_uuid(ds_id), "dataset id must be a UUID")
                _require(isinstance(ds, dict) and "tests" in ds and set(ds) <= {"tests"}, "bad dataset")
                by_dataset[ds_id] = _parse_py_cases(ds["tests"])
    else:
        function = ""
        base_setup = spec.get("setup_sql", "")
        _require(isinstance(base_setup, str), "setup_sql must be text")
        default = _parse_sql_cases(spec["tests"], base_setup) if "tests" in spec else None
        if has_variants:
            _require(isinstance(datasets, dict) and 1 <= len(datasets) <= 1000, "datasets must be an object")
            for ds_id, ds in datasets.items():
                _require(is_canonical_uuid(ds_id), "dataset id must be a UUID")
                _require(isinstance(ds, dict) and "tests" in ds and set(ds) <= {"tests", "setup_sql"}, "bad dataset")
                setup = ds.get("setup_sql", base_setup)
                _require(isinstance(setup, str), "setup_sql must be text")
                by_dataset[ds_id] = _parse_sql_cases(ds["tests"], setup)
    _require(default is not None or bool(by_dataset), "no tests")
    return TaskSpec(kind, function, default, by_dataset, has_variants)


# ---------------------------------------------------------------- comparison

def values_equal(a: Any, b: Any) -> bool:
    """Strict JSON-value equality; bool is not a number; floats compared with tolerance."""
    if isinstance(a, bool) or isinstance(b, bool):
        return isinstance(a, bool) and isinstance(b, bool) and a == b
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        if isinstance(a, float) or isinstance(b, float):
            return math.isclose(a, b, rel_tol=1e-9, abs_tol=1e-9)
        return a == b
    if isinstance(a, (list, tuple)) and isinstance(b, (list, tuple)):
        return len(a) == len(b) and all(values_equal(x, y) for x, y in zip(a, b))
    if isinstance(a, dict) and isinstance(b, dict):
        return a.keys() == b.keys() and all(values_equal(a[k], b[k]) for k in a)
    if type(a) is not type(b):
        return False
    return a == b


def _round(v: Any) -> Any:
    if isinstance(v, float):
        return round(v, 6)
    if isinstance(v, (list, tuple)):
        return [_round(x) for x in v]
    return v


def _row_key(row: Any) -> str:
    return json.dumps(_round(row), sort_keys=True, default=str)


def rows_equal(actual: list, expected: list, ordered: bool) -> bool:
    if len(actual) != len(expected):
        return False
    if ordered:
        return all(values_equal(_round(a), _round(e)) for a, e in zip(actual, expected))
    return sorted(_row_key(r) for r in actual) == sorted(_row_key(r) for r in expected)
