"""Runner domain rules: closed request schema (SR-01), spec validation, comparison."""
import uuid

import pytest

from runner.domain import models as m

U = lambda: str(uuid.uuid4())  # noqa: E731


def valid(**over):
    base = dict(run_id=U(), task_id=U(), dataset_id=U(), limits_profile="py_tests", submission="print(1)")
    base.update(over)
    return base


def test_should_accept_valid_request():
    req = m.validate_request(**valid())
    assert req.limits_profile == "py_tests"


@pytest.mark.parametrize("field", ["run_id", "task_id", "dataset_id"])
@pytest.mark.parametrize("bad", ["../etc/passwd", "/var/run/docker.sock", "C:\\Windows", "\\\\host\\share",
                                 "file:///etc/passwd", "", "ABCDEF12-0000-0000-0000-000000000000",
                                 "١٢٣٤٥٦٧٨-0000-0000-0000-000000000000", 7, None])
def test_should_reject_non_canonical_ids_and_paths(field, bad):
    with pytest.raises(m.InvalidRunRequest):
        m.validate_request(**valid(**{field: bad}))


@pytest.mark.parametrize("bad", ["", "PY_TESTS", "Py_tests", "sql", "1", 1, None, "py_tests ", "../x", "privileged"])
def test_should_reject_unknown_limits_profile(bad):
    with pytest.raises(m.InvalidRunRequest):
        m.validate_request(**valid(limits_profile=bad))


def test_should_reject_oversized_submission_at_cap_plus_one():
    m.validate_request(**valid(submission="a" * m.MAX_SUBMISSION_BYTES))
    with pytest.raises(m.InvalidRunRequest):
        m.validate_request(**valid(submission="a" * (m.MAX_SUBMISSION_BYTES + 1)))


@pytest.mark.parametrize("bad", ["", b"bytes", None, "nul\x00byte", "\ud800"])
def test_should_reject_bad_submission(bad):
    with pytest.raises(m.InvalidRunRequest):
        m.validate_request(**valid(submission=bad))


def test_should_count_cap_in_bytes_not_characters():
    with pytest.raises(m.InvalidRunRequest):
        m.validate_request(**valid(submission="é" * (m.MAX_SUBMISSION_BYTES // 2 + 1)))


def test_should_parse_python_spec_and_resolve_dataset_variants():
    ds = U()
    spec = m.parse_task_spec("python", {
        "function": "solve",
        "tests": [{"id": "t1", "args": [1], "expected": 2}],
        "datasets": {ds: {"tests": [{"id": "v1", "args": [5], "expected": 6, "visible": True}]}},
    })
    assert spec.cases_for(ds)[0].id == "v1"
    assert spec.cases_for(U()) is None  # declared datasets: others unknown


def test_should_accept_any_dataset_when_task_declares_no_variants():
    spec = m.parse_task_spec("python", {"function": "f", "tests": [{"id": "a", "args": [], "expected": 1}]})
    assert spec.cases_for(U()) is not None


@pytest.mark.parametrize("bad", [
    {"function": "1bad", "tests": [{"id": "a", "args": [], "expected": 1}]},
    {"function": "f", "tests": []},
    {"function": "f", "tests": [{"id": "../x", "args": [], "expected": 1}]},
    {"function": "f", "tests": [{"id": "a", "args": "no", "expected": 1}]},
    {"function": "f", "tests": [{"id": "a", "args": [], "expected": 1}], "image": "evil"},
])
def test_should_reject_malformed_python_spec(bad):
    with pytest.raises(m.InvalidTaskSpec):
        m.parse_task_spec("python", bad)


def test_should_reject_unknown_task_kind():
    with pytest.raises(m.InvalidTaskSpec):
        m.parse_task_spec("bash", {})


@pytest.mark.parametrize("a,b,eq", [
    (1, 1.0, True), (True, 1, False), ([1, 2], [1, 2], True), ([1, 2], [2, 1], False),
    (0.1 + 0.2, 0.3, True), ({"a": 1}, {"a": 1}, True), ("1", 1, False), (None, None, True),
])
def test_should_compare_values_strictly_with_float_tolerance(a, b, eq):
    assert m.values_equal(a, b) is eq


def test_should_compare_rows_unordered_when_not_ordered():
    assert m.rows_equal([[1, "a"], [2, "b"]], [[2, "b"], [1, "a"]], ordered=False)
    assert not m.rows_equal([[1, "a"], [2, "b"]], [[2, "b"], [1, "a"]], ordered=True)
