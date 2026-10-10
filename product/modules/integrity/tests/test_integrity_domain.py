"""Integrity domain rules: events, consent, pre-check thresholds, risk label, Range parsing."""
import pytest

from integrity.domain import models as d

GOOD_REPORT = {"down_mbps": 10, "up_mbps": 5, "latency_ms": 50, "camera": True, "mic": True,
               "screen_surface": "monitor", "fullscreen": True, "single_display": True, "browser": "Chrome 126"}


def check(report, **over):
    return {c[0]: c[1] for c in d.evaluate_precheck({**report, **over}, d.PrecheckThresholds()).checks}


def test_should_pass_precheck_when_everything_meets_defaults():
    assert d.evaluate_precheck(GOOD_REPORT, d.PrecheckThresholds()).passed


@pytest.mark.parametrize("field,value,failing", [
    ("down_mbps", 1.9, "download"), ("up_mbps", 0.5, "upload"), ("latency_ms", 400, "latency"),
    ("camera", False, "camera"), ("mic", False, "microphone"), ("screen_surface", "window", "screen"),
    ("screen_surface", "browser", "screen"), ("fullscreen", False, "fullscreen"),
    ("single_display", False, "single_display"), ("browser", "Firefox 120", "browser"),
    ("down_mbps", "fast", "download"), ("down_mbps", True, "download"), ("latency_ms", float("nan"), "latency"),
])
def test_should_fail_precheck_when_a_requirement_is_not_met(field, value, failing):
    result = check(GOOD_REPORT, **{field: value})
    assert result[failing] is False
    assert not d.evaluate_precheck({**GOOD_REPORT, field: value}, d.PrecheckThresholds()).passed


def test_should_treat_unreported_single_display_as_not_failing():
    assert check(GOOD_REPORT, single_display=None)["single_display"] is True


def test_should_honour_configurable_thresholds():
    strict = d.PrecheckThresholds(min_down_mbps=50)
    assert not d.evaluate_precheck(GOOD_REPORT, strict).passed


def test_should_reject_unknown_report_fields():
    with pytest.raises(d.InvalidInput):
        d.evaluate_precheck({**GOOD_REPORT, "admin": True}, d.PrecheckThresholds())


def test_should_use_neutral_wording_in_precheck_messages():
    result = d.evaluate_precheck({**GOOD_REPORT, "camera": False}, d.PrecheckThresholds()).to_dict()
    text = str(result).lower()
    for banned in ("cheat", "misconduct", "suspicious", "ai detected"):
        assert banned not in text


@pytest.mark.parametrize("raw", [
    {"type": "paste", "t_ms": 12.5, "item_id": "q1abc"},
    {"type": "focus_loss", "t_ms": 0},
    {"type": "network_drop", "t_ms": 5, "detail": {"duration_ms": 300, "online": False}},
])
def test_should_accept_valid_events(raw):
    assert d.validate_event(raw).type == raw["type"]


@pytest.mark.parametrize("raw", [
    {"type": "cheated", "t_ms": 1}, {"type": "paste"}, {"type": "paste", "t_ms": -1},
    {"type": "paste", "t_ms": "1"}, {"type": "paste", "t_ms": float("inf")}, {"type": "paste", "t_ms": True},
    {"type": "paste", "t_ms": 1, "extra": 1}, {"type": "paste", "t_ms": 1, "item_id": "../x"},
    {"type": "paste", "t_ms": 1, "detail": {"k": "x" * 65}},
    {"type": "paste", "t_ms": 1, "detail": {"k": {"nested": 1}}},
    {"type": "paste", "t_ms": 1, "detail": {"BadKey": 1}},
    {"type": "paste", "t_ms": 1, "detail": {f"k{i}": 1 for i in range(9)}},
    "paste", None, 5,
])
def test_should_reject_invalid_events(raw):
    with pytest.raises(d.InvalidInput):
        d.validate_event(raw)


def test_should_cap_batch_size():
    ok = [{"type": "copy", "t_ms": i} for i in range(d.MAX_BATCH_EVENTS)]
    assert len(d.validate_events(ok)) == d.MAX_BATCH_EVENTS
    with pytest.raises(d.InvalidInput):
        d.validate_events(ok + [{"type": "copy", "t_ms": 1}])


def test_should_label_risk_from_weighted_counts():
    w = d.DEFAULT_WEIGHTS
    assert d.risk_summary({}, w, 5, 15) == (0, "low")
    assert d.risk_summary({"paste": 2}, w, 5, 15)[1] == "low"
    assert d.risk_summary({"paste": 3}, w, 5, 15)[1] == "medium"
    assert d.risk_summary({"screen_share_ended": 5}, w, 5, 15)[1] == "high"
    assert d.risk_summary({"unknown_type": 99}, w, 5, 15)[1] == "low"


@pytest.mark.parametrize("version,scopes", [("", ["camera"]), ("v1", []), ("v1", ["camera", "camera"]),
                                            ("v1", ["admin"]), ("v1", "camera"), ("../v", ["camera"]), (1, ["camera"])])
def test_should_reject_invalid_consent(version, scopes):
    with pytest.raises(d.InvalidInput):
        d.check_consent(version, scopes)


@pytest.mark.parametrize("bad", ["../x", "a/b", "a\\b", "", "short", "x" * 65, "..", "a b c d e f", None, 5, "att\x00id12"])
def test_should_reject_unsafe_attempt_ids(bad):
    with pytest.raises(d.InvalidInput):
        d.check_attempt_id(bad)


@pytest.mark.parametrize("header,total,expected", [
    (None, 100, None), ("bytes=0-9", 100, (0, 9)), ("bytes=90-", 100, (90, 99)), ("bytes=-10", 100, (90, 99)),
    ("bytes=50-500", 100, (50, 99)), ("bytes=0-0", 100, (0, 0)), ("garbage", 100, None), ("bytes=0-1,5-6", 100, None),
])
def test_should_parse_ranges(header, total, expected):
    assert d.parse_range(header, total) == expected


@pytest.mark.parametrize("header", ["bytes=100-", "bytes=200-300", "bytes=5-2", "bytes=-0"])
def test_should_reject_unsatisfiable_ranges(header):
    with pytest.raises(d.Unsatisfiable):
        d.parse_range(header, 100)
