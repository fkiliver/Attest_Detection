"""Offline unit tests for the rule-based normalizer/comparator."""

from __future__ import annotations

from attest.config import DecisionConfig
from attest.normalize import compare_result, text_values_equal, values_equivalent

CFG = DecisionConfig()


def _ok(v):
    return {"id": "c0", "ok": v}


def test_equal_integers():
    assert values_equivalent(10, 10, CFG)
    assert not values_equivalent(10, 11, CFG)


def test_float_tolerance():
    a = {"__f64__": 0.1 + 0.2}
    b = {"__f64__": 0.3}
    assert values_equivalent(a, b, CFG)
    assert not values_equivalent({"__f64__": 1.0}, {"__f64__": 2.0}, CFG)


def test_float_nan_and_inf():
    assert values_equivalent({"__f64__": "NaN"}, {"__f64__": "NaN"}, CFG)
    assert values_equivalent({"__f64__": "Infinity"}, {"__f64__": "Infinity"}, CFG)
    assert not values_equivalent({"__f64__": "Infinity"}, {"__f64__": "-Infinity"}, CFG)


def test_bytes_equal_by_sha():
    a = {"__bytes__": "aGk=", "len": 2, "sha256": "deadbeef"}
    b = {"__bytes__": "aGk=", "len": 2, "sha256": "deadbeef"}
    c = {"__bytes__": "Ynk=", "len": 2, "sha256": "feedface"}
    assert values_equivalent(a, b, CFG)
    assert not values_equivalent(a, c, CFG)


def test_bytes_ref_matches_inline_sha():
    inline = {"__bytes__": "x", "len": 100, "sha256": "abc"}
    ref = {"__bytes_ref__": {"sha256": "abc", "len": 100}}
    assert values_equivalent(inline, ref, CFG)


def test_lists_ordered_vs_unordered():
    assert values_equivalent([1, 2, 3], [1, 2, 3], CFG)
    assert not values_equivalent([1, 2, 3], [3, 2, 1], CFG)
    assert values_equivalent([1, 2, 3], [3, 2, 1], CFG, unordered=True)


def test_nested_dict():
    a = {"x": 1, "y": {"__f64__": 1.0000000001}}
    b = {"x": 1, "y": {"__f64__": 1.0}}
    assert values_equivalent(a, b, CFG)
    assert not values_equivalent({"x": 1}, {"x": 1, "z": 2}, CFG)


def test_compare_result_errors_match_on_type():
    a = {"id": "c0", "error": {"type": "java.lang.NullPointerException", "message": "x is null"}}
    b = {"id": "c0", "error": {"type": "java.lang.NullPointerException", "message": "different msg"}}
    match, reason = compare_result(a, b, CFG)
    assert match, reason


def test_compare_result_error_vs_value_is_mismatch():
    a = {"id": "c0", "error": {"type": "E"}}
    b = _ok(5)
    match, _ = compare_result(a, b, CFG)
    assert not match


def test_compare_result_void_both():
    a = {"id": "c0", "ok": None, "void": True}
    b = {"id": "c0", "ok": None, "void": True}
    match, _ = compare_result(a, b, CFG)
    assert match


def test_compare_result_void_vs_value():
    a = {"id": "c0", "ok": None, "void": True}
    b = _ok(5)
    match, _ = compare_result(a, b, CFG)
    assert not match


def test_opaque_only_equal_when_identical():
    a = {"__opaque__": "com.Foo", "toString": "Foo@1"}
    b = {"__opaque__": "com.Foo", "toString": "Foo@1"}
    c = {"__opaque__": "com.Foo", "toString": "Foo@2"}
    assert values_equivalent(a, b, CFG)
    assert not values_equivalent(a, c, CFG)


def test_text_values_equal_trailing_whitespace():
    # stdout-style outputs differing only in trailing newline / spaces.
    assert text_values_equal("1 2 3", "1 2 3\n")
    assert text_values_equal("1 2 3", "1 2 3   ")
    assert text_values_equal("a\nb\n", "a\nb")
    assert text_values_equal("Case #1: 5\r\n", "Case #1: 5\n")
    # line-internal differences are still real
    assert not text_values_equal("1 2 3", "1  2 3")
    assert not text_values_equal("1 2 3", "1 2 4")


def test_compare_result_text_mode_normalizes_whitespace():
    a = {"id": "c0", "ok": "0 1 2 3"}
    b = {"id": "c0", "ok": "0 1 2 3\n"}
    # strict mode: mismatch
    m_strict, _ = compare_result(a, b, CFG, text_mode=False)
    assert not m_strict
    # text mode: match
    m_text, reason = compare_result(a, b, CFG, text_mode=True)
    assert m_text, reason


def test_compare_result_text_mode_keeps_real_diffs():
    a = {"id": "c0", "ok": "5"}
    b = {"id": "c0", "ok": "0"}
    m, _ = compare_result(a, b, CFG, text_mode=True)
    assert not m
