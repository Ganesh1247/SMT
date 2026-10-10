"""Qualify rules from the Founder level spec (build-brief section 2)."""
import json
import random
from pathlib import Path

import pytest

from assessment.domain import rules as r

BANK = Path(__file__).resolve().parent.parent / "bank"
RULES = r.Rules.from_json(json.loads((BANK / "rules.json").read_text(encoding="utf-8")))


@pytest.mark.parametrize("correct,expected", [(5, True), (4, True), (3, False), (0, False)])
def test_should_qualify_l1_at_four_of_five(correct, expected):
    assert r.qualify_l1(correct, RULES) is expected


@pytest.mark.parametrize("passed,expected", [(3, True), (2, True), (1, False), (0, False)])
def test_should_qualify_l2_at_two_of_three(passed, expected):
    assert r.qualify_l2(passed, RULES) is expected


def test_should_pass_l3_when_one_task_fully_passes_and_ratio_ok():
    res = {"a": [(4, 4), (5, 5)], "b": [(2, 4), (3, 5)]}
    assert r.qualify_l3(res, RULES)  # 14/18 = 0.78


def test_should_fail_l3_when_no_task_passes_both_variants():
    res = {"a": [(4, 4), (4, 5)], "b": [(4, 4), (4, 5)]}  # ratio 0.89 but no full task
    assert not r.qualify_l3(res, RULES)


def test_should_fail_l3_when_ratio_below_seventy_percent():
    res = {"a": [(4, 4), (5, 5)], "b": [(0, 5), (0, 5)]}  # 9/19 = 0.47
    assert not r.qualify_l3(res, RULES)


def test_should_pass_l3_at_exactly_seventy_percent():
    res = {"a": [(5, 5), (5, 5)], "b": [(0, 5), (0, 5)]}
    # 10/20 = 0.5 -> fail; build exact 0.7: 14 of 20
    res = {"a": [(5, 5), (5, 5)], "b": [(2, 5), (2, 5)]}
    assert r.l3_ratio(res) == pytest.approx(0.7) and r.qualify_l3(res, RULES)


def crit(scores, conf=0.9):
    return [{"criterion": c, "score0to3": s, "confidence": conf} for c, s in zip(r.L4_CRITERIA, scores)]


def test_should_pass_l4_at_total_ten_with_no_zero():
    v = r.qualify_l4(crit([2, 2, 2, 2, 2]), RULES)
    assert v.passed and v.total == 10 and not v.needs_review


def test_should_fail_l4_below_ten():
    assert not r.qualify_l4(crit([2, 2, 2, 2, 1]), RULES).passed


def test_should_fail_l4_when_any_criterion_is_zero_even_with_high_total():
    assert not r.qualify_l4(crit([3, 3, 3, 3, 0]), RULES).passed


def test_should_route_low_confidence_l4_to_review():
    assert r.qualify_l4(crit([3, 3, 3, 3, 3], conf=0.3), RULES).needs_review


@pytest.mark.parametrize("bad", [crit([4, 2, 2, 2, 2]), crit([2, 2, 2, 2]), crit([-1, 2, 2, 2, 2])])
def test_should_reject_malformed_l4_evaluation(bad):
    with pytest.raises(r.InvalidInput):
        r.qualify_l4(bad, RULES)


def test_should_check_l1_answers():
    single = {"kind": "single", "answer": ["b"]}
    multi = {"kind": "multi", "answer": ["a", "c"]}
    short = {"kind": "short", "accepted": ["cba"]}
    assert r.check_answer(single, {}, ["b"]) and not r.check_answer(single, {}, ["a"])
    assert r.check_answer(multi, {}, ["c", "a"]) and not r.check_answer(multi, {}, ["a"])
    assert not r.check_answer(multi, {}, ["a", "a", "c"])
    assert r.check_answer(short, {}, "  CBA ") and not r.check_answer(short, {}, "abc")
    assert not r.check_answer(short, {}, 5)


def test_should_draw_deterministically_and_prefer_unused():
    pool = [f"i{n}" for n in range(10)]
    a = r.draw(pool, 5, random.Random("seed1"))
    assert a == r.draw(pool, 5, random.Random("seed1"))
    b = r.draw(pool, 5, random.Random("seed2"), avoid=a)
    assert not set(a) & set(b)


def test_should_score_explanation_by_keyword_coverage():
    rubric = {"criteria": [{"id": "x", "keywords": ["denominator"]}, {"id": "y", "keywords": ["empty"]}]}
    assert r.explanation_coverage("The denominator was off", rubric) == (1, 2)
    assert r.explanation_coverage("", rubric) == (0, 2)
