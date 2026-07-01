"""Offline executor + protocol tests (no LLM).

Covers the three observable-output shapes (value, exception, side-effect bytes),
plus the timeout/process-tree-kill path. Skips automatically if no host JDK.
"""

from __future__ import annotations

import base64
import json
import shutil
from pathlib import Path

import pytest

from attest.config import DEFAULT
from attest.executors.java_exec import JAVA, JAVAC, JavaExecutor
from attest.executors import sandbox
from attest.harness_fill import fill_template

from .java_fixtures import COPY_HOLES, INFLOOP_HOLES, SUM_HOLES, THROW_HOLES

pytestmark = pytest.mark.skipif(
    JAVAC is None or JAVA is None,
    reason="host JDK (javac/java) not available via PATH or JAVA_HOME",
)


def _b64(s: str) -> str:
    return base64.b64encode(s.encode("utf-8")).decode("ascii")


def _write_inputs(path: Path, observe: dict, cases: list[dict]) -> None:
    path.write_text(
        json.dumps({"protocol": 1, "observe": observe, "cases": cases}, ensure_ascii=False),
        encoding="utf-8",
    )


def _compile_and_run(tmp_path: Path, holes: dict, observe: dict, cases: list[dict]):
    ex = JavaExecutor(DEFAULT)
    status = ex.probe()
    assert status.available, status.detail
    src = fill_template("java", holes)
    workdir = tmp_path / "side"
    compiled = ex.compile(src, workdir)
    assert compiled.ok, f"compile failed:\n{compiled.diagnostics}"
    inputs = tmp_path / "inputs.json"
    _write_inputs(inputs, observe, cases)
    return ex.run(compiled, inputs)


def test_return_value_path(tmp_path):
    res = _compile_and_run(
        tmp_path,
        SUM_HOLES,
        {"mode": "return"},
        [
            {"id": "c0", "args": {"arr": [1, 2, 3, 4]}},
            {"id": "c1", "args": {"arr": []}},
        ],
    )
    assert res.ok, res.error + res.stderr.decode("utf-8", "replace")
    by_id = {r["id"]: r for r in res.outputs["results"]}
    assert by_id["c0"]["ok"] == 10
    assert by_id["c1"]["ok"] == 0


def test_exception_is_captured_and_run_continues(tmp_path):
    res = _compile_and_run(
        tmp_path,
        THROW_HOLES,
        {"mode": "return"},
        [
            {"id": "c0", "args": {"arr": [7]}},      # ok -> 7
            {"id": "c1", "args": {"arr": []}},        # AIOOBE
            {"id": "c2", "args": {"arr": [9]}},      # ok -> 9 (proves continuation)
        ],
    )
    assert res.ok, res.error
    by_id = {r["id"]: r for r in res.outputs["results"]}
    assert by_id["c0"]["ok"] == 7
    assert "error" in by_id["c1"]
    assert "ArrayIndexOutOfBounds" in by_id["c1"]["error"]["type"]
    assert by_id["c2"]["ok"] == 9


def test_side_effect_bytes_path(tmp_path):
    payloads = {"c0": "hello world", "c1": "café 🚀 déjà", "c2": ""}
    res = _compile_and_run(
        tmp_path,
        COPY_HOLES,
        {"mode": "artifact", "artifact": {"kind": "file_bytes", "path_role": "dest"}},
        [{"id": k, "args": {"src_b64": _b64(v)}} for k, v in payloads.items()],
    )
    assert res.ok, res.error
    by_id = {r["id"]: r for r in res.outputs["results"]}
    for k, v in payloads.items():
        ok = by_id[k]["ok"]
        assert "__bytes__" in ok
        assert ok["len"] == len(v.encode("utf-8"))
        assert base64.b64decode(ok["__bytes__"]).decode("utf-8") == v


def test_infinite_loop_times_out_and_is_killed(tmp_path):
    # Shrink the per-harness timeout so the test is fast.
    cfg = DEFAULT
    from dataclasses import replace

    cfg = replace(cfg, exec=replace(cfg.exec, harness_timeout_s=4.0))
    ex = JavaExecutor(cfg)
    src = fill_template("java", INFLOOP_HOLES)
    workdir = tmp_path / "side"
    compiled = ex.compile(src, workdir)
    assert compiled.ok, compiled.diagnostics
    inputs = tmp_path / "inputs.json"
    _write_inputs(inputs, {"mode": "return"}, [{"id": "c0", "args": {}}])
    res = ex.run(compiled, inputs)
    assert res.timed_out, "expected a wall-clock timeout"
    assert not res.ok


def test_sandbox_docker_path_builder_shape():
    # Pure unit check of the docker argv builder (no daemon needed).
    argv = sandbox.build_docker_run(
        image="eclipse-temurin:21",
        inner_argv=["java", "Harness"],
        mounts_ro=[(Path.cwd(), "/in")],
        mounts_rw=[(Path.cwd(), "/out")],
    )
    assert argv[1:3] == ["run", "--rm"]
    assert argv[0].endswith("docker") or argv[0].endswith("docker.exe")
    assert "--network" in argv and "none" in argv
    assert "--read-only" in argv
    assert argv[-2:] == ["java", "Harness"]
