"""Tests for the external-dependency gate detector (offline, no LLM)."""

from __future__ import annotations

from attest.depgate import detect, pair_has_external


def test_detects_network():
    code = 'String f() { URL u = new URL("http://x"); return u.openStream().toString(); }'
    r = detect(code)
    assert r.has_external and "network" in r.categories


def test_detects_filesystem():
    code = "void f() { FileInputStream in = new FileInputStream(path); }"
    assert "filesystem" in detect(code).categories


def test_detects_clock_and_random():
    assert "clock" in detect("long t = System.currentTimeMillis();").categories
    assert "random" in detect("int x = new Random().nextInt();").categories


def test_pure_computation_has_no_external():
    code = "int sum(int[] a){int s=0;for(int x:a)s+=x;return s;}"
    assert not detect(code).has_external


def test_ignores_dependency_word_in_comment_or_string():
    # 'new URL' only inside a comment / string must not trigger
    code = '// builds a new URL later\nString s = "new URL example"; int x = 1+1;'
    assert not detect(code).has_external


def test_pair_union():
    a = "int f(int x){return x*2;}"
    b = "String g(){ return new java.net.Socket().toString(); }"
    r = pair_has_external(a, b)
    assert r.has_external and "network" in r.categories
