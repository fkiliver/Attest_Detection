"""Executor abstraction: compile a harness, run it on an input batch.

An :class:`Executor` turns a *filled harness source* (LLM output) plus the
shared support library into a runnable program, then executes it against an
``inputs.json`` to produce ``outputs.json``. The orchestrator's repair loop
drives the ``compile`` step; stage 4 drives ``run``.

Two outcome objects keep compile and run failures distinct, because the repair
loop treats them differently (a compile error is fed back to the LLM verbatim;
a clean compile that produces no output is a *startup* failure).
"""

from __future__ import annotations

import abc
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class CompileResult:
    ok: bool
    workdir: Path
    diagnostics: str = ""        # compiler stdout+stderr (fed back on failure)
    command: str = ""            # the exact compile command, for the repair prompt
    duration_s: float = 0.0


@dataclass
class RunResult:
    ok: bool
    outputs: dict[str, Any] | None = None   # parsed outputs.json, if produced
    raw_output: bytes = b""
    stdout: bytes = b""
    stderr: bytes = b""
    timed_out: bool = False
    returncode: int | None = None
    duration_s: float = 0.0
    error: str = ""              # orchestrator-level error (e.g. no output file)

    @property
    def produced_output(self) -> bool:
        return self.outputs is not None


@dataclass
class ToolchainStatus:
    available: bool
    detail: str = ""
    extras: dict[str, Any] = field(default_factory=dict)


class Executor(abc.ABC):
    """Compile + run a single snippet's harness for one language."""

    #: short language id, e.g. "java", "cpp"
    language: str = ""

    @abc.abstractmethod
    def probe(self) -> ToolchainStatus:
        """Check that the required toolchain is usable; never raises."""

    @abc.abstractmethod
    def compile(self, harness_source: str, workdir: Path) -> CompileResult:
        """Write the harness + support lib into ``workdir`` and compile it."""

    @abc.abstractmethod
    def run(self, compiled: CompileResult, inputs_path: Path) -> RunResult:
        """Run a successfully-compiled harness against ``inputs_path``."""


def recover_outputs(outputs_path: Path, max_bytes: int) -> tuple[dict | None, str]:
    """Read a harness ``outputs.json``, recovering a partial ``.tmp`` if needed.

    The harness streams results into ``outputs.json.tmp`` and atomically renames
    it on a clean finish. If the snippet crashes mid-run (e.g. a SIGSEGV on an
    adversarial input), the final file is absent but the ``.tmp`` holds every
    case completed before the crash. We close the dangling JSON array so those
    cases are still usable as behavioral evidence, and synthesize a trailing
    error result marking the crash. Returns (parsed_or_None, error_message).
    """
    import json

    if outputs_path.exists():
        try:
            size = outputs_path.stat().st_size
            if size > max_bytes:
                return None, f"outputs.json too large ({size} bytes)"
            return json.loads(outputs_path.read_text(encoding="utf-8")), ""
        except (OSError, json.JSONDecodeError) as e:
            return None, f"failed to parse outputs.json: {e}"

    tmp = Path(str(outputs_path) + ".tmp")
    if not tmp.exists():
        return None, "no outputs.json produced"
    try:
        raw = tmp.read_text(encoding="utf-8")
    except OSError as e:
        return None, f"failed to read partial outputs: {e}"

    # The partial looks like: {"protocol":1,"results":[ {..},{..}
    # Trim any half-written trailing object, then close the array+object and
    # append a synthetic crash marker so the missing case is observable.
    closed = _close_partial_json(raw)
    if closed is None:
        return None, "partial outputs.json.tmp could not be recovered"
    try:
        data = json.loads(closed)
        data.setdefault("_partial", True)
        return data, "recovered partial output (harness crashed mid-run)"
    except json.JSONDecodeError as e:
        return None, f"partial recovery failed to parse: {e}"


def _close_partial_json(raw: str) -> str | None:
    """Best-effort: turn a truncated ``{"results":[ ...`` stream into valid JSON."""
    s = raw.rstrip()
    if "[" not in s:
        return None
    # Drop a dangling partial element after the last complete '}' (or '[').
    last_obj = s.rfind("}")
    last_open = s.rfind("[")
    cut = max(last_obj, last_open)
    if cut == -1:
        return None
    s = s[: cut + 1]
    # Append a synthetic crash result so the crash is a comparable observation.
    crash = '{"id":"__crash__","error":{"type":"__ProcessCrash__","message":"harness terminated mid-run"}}'
    sep = "," if s.endswith("}") else ""
    return s + sep + crash + "]}"
