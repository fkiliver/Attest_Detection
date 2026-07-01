"""C/C++ executor tests (require Docker; skipped if unavailable).

Validates the gcc-in-Docker compile+run path and the stdin/stdout observation
mode used by OJClone-style programs.
"""

from __future__ import annotations

import json

import pytest

from attest.config import DEFAULT
from attest.executors import sandbox
from attest.executors.cpp_exec import CppExecutor
from attest.harness_fill import fill_template

from .cpp_fixtures import ECHO_STDIN_HOLES, SUM_STDIN_HOLES

pytestmark = pytest.mark.skipif(
    not sandbox.docker_available(),
    reason="Docker not available (required for C/C++ executor)",
)


def _compile_and_run(tmp_path, holes, cases):
    ex = CppExecutor(DEFAULT)
    assert ex.probe().available
    src = fill_template("cpp", holes)
    compiled = ex.compile(src, tmp_path / "side")
    assert compiled.ok, f"compile failed:\n{compiled.diagnostics}"
    inputs = tmp_path / "inputs.json"
    inputs.write_text(
        json.dumps(
            {
                "protocol": 1,
                "observe": {"mode": "artifact", "artifact": {"kind": "stdout"}},
                "cases": cases,
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    return ex.run(compiled, inputs)


def test_cpp_stdin_sum(tmp_path):
    res = _compile_and_run(
        tmp_path,
        SUM_STDIN_HOLES,
        [
            {"id": "c0", "args": {"stdin": "3 4\n"}},
            {"id": "c1", "args": {"stdin": "100 -7\n"}},
        ],
    )
    assert res.ok, res.error + res.stderr.decode("utf-8", "replace")
    by_id = {r["id"]: r for r in res.outputs["results"]}
    assert by_id["c0"]["ok"].strip() == "7"
    assert by_id["c1"]["ok"].strip() == "93"


def test_cpp_stdin_nonascii_roundtrip(tmp_path):
    res = _compile_and_run(
        tmp_path,
        ECHO_STDIN_HOLES,
        [{"id": "c0", "args": {"stdin": "café 🚀 déjà"}}],
    )
    assert res.ok, res.error
    by_id = {r["id"]: r for r in res.outputs["results"]}
    assert by_id["c0"]["ok"] == "café 🚀 déjà"
