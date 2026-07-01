"""C/C++ executor: compile + run inside a hardened ``gcc`` Docker container.

There is no host C/C++ toolchain on the dev machine, so all C/C++ work runs in
the ``gcc`` image. Compilation and execution happen in the SAME container
invocation per step, with the work directory bind-mounted. The harness reads
``inputs.json`` and writes ``outputs.json`` exactly like the Java harness.

The driver template and ``json.hpp`` are copied into the work directory; the LLM
fills the template holes (and, for OJClone-style stdin/stdout programs, renames
the snippet's ``main`` to ``snippet_entry``).
"""

from __future__ import annotations

import json
from pathlib import Path

from ..config import DEFAULT, Config
from . import sandbox
from .base import CompileResult, Executor, RunResult, ToolchainStatus, recover_outputs

_SUPPORT = Path(__file__).resolve().parent.parent.parent / "harness_support" / "cpp"
_JSON_HPP = _SUPPORT / "json.hpp"

# container-internal layout
_C_WORK = "/work"
_BIN_NAME = "harness.bin"


class CppExecutor(Executor):
    language = "cpp"

    def __init__(self, config: Config | None = None):
        self.config = config or DEFAULT
        self.exec_cfg = self.config.exec

    def probe(self) -> ToolchainStatus:
        if not sandbox.docker_available():
            return ToolchainStatus(False, "Docker not available (required for C/C++)")
        if not _JSON_HPP.exists():
            return ToolchainStatus(False, f"missing support lib: {_JSON_HPP}")
        return ToolchainStatus(True, f"docker:{self.exec_cfg.docker_cpp_image}")

    # -- compile ----------------------------------------------------------- #

    def compile(self, harness_source: str, workdir: Path) -> CompileResult:
        workdir.mkdir(parents=True, exist_ok=True)
        (workdir / "json.hpp").write_text(_JSON_HPP.read_text(encoding="utf-8"), encoding="utf-8")
        # The snippet language is C++ (we compile C snippets as C++ too; OJClone's
        # C is valid C++ for these programs). File name drives g++ language mode.
        (workdir / "harness.cpp").write_text(harness_source, encoding="utf-8")

        inner = [
            "bash", "-lc",
            # -Werror=return-type turns "control reaches end of non-void function"
            # (undefined behavior — a frequent OJClone hazard when main() is
            # renamed to snippet_entry without a trailing return) into a COMPILE
            # error, so the repair loop fixes it instead of a silent segfault.
            f"g++ -std=c++17 -O1 -pipe -Werror=return-type -w "
            f"-o {_C_WORK}/{_BIN_NAME} {_C_WORK}/harness.cpp "
            f"2> {_C_WORK}/compile.err; echo EXIT=$? > {_C_WORK}/compile.status",
        ]
        argv = sandbox.build_docker_run(
            image=self.exec_cfg.docker_cpp_image,
            inner_argv=inner,
            mounts_ro=[],
            mounts_rw=[(workdir, _C_WORK)],
            memory=self.exec_cfg.docker_memory,
            cpus=self.exec_cfg.docker_cpus,
            pids_limit=self.exec_cfg.docker_pids_limit,
            tmpfs_size=self.exec_cfg.docker_tmpfs_size,
            read_only_root=False,  # need to write the binary into the bind mount
        )
        res = sandbox.run_guarded(argv, cwd=workdir, timeout_s=self.exec_cfg.compile_timeout_s)

        err = ""
        if (workdir / "compile.err").exists():
            err = (workdir / "compile.err").read_text(encoding="utf-8", errors="replace")
        ok = (workdir / _BIN_NAME).exists() and not res.timed_out
        # surface docker-level failures (e.g. image issues) in diagnostics
        diagnostics = err or (res.stdout + res.stderr).decode("utf-8", "replace")
        return CompileResult(
            ok=ok,
            workdir=workdir,
            diagnostics=diagnostics,
            command="g++ -std=c++17 -O1 -o harness.bin harness.cpp",
            duration_s=res.duration_s,
        )

    # -- run --------------------------------------------------------------- #

    def run(self, compiled: CompileResult, inputs_path: Path) -> RunResult:
        if not compiled.ok:
            return RunResult(ok=False, error="compile failed")
        workdir = compiled.workdir
        # stage inputs + clear any stale output
        (workdir / "inputs.json").write_text(
            inputs_path.read_text(encoding="utf-8"), encoding="utf-8"
        )
        outputs_path = workdir / "outputs.json"
        try:
            outputs_path.unlink()
        except OSError:
            pass

        inner = [
            "bash", "-lc",
            f"{_C_WORK}/{_BIN_NAME} {_C_WORK}/inputs.json {_C_WORK}/outputs.json",
        ]
        argv = sandbox.build_docker_run(
            image=self.exec_cfg.docker_cpp_image,
            inner_argv=inner,
            mounts_ro=[],
            mounts_rw=[(workdir, _C_WORK)],
            memory=self.exec_cfg.docker_memory,
            cpus=self.exec_cfg.docker_cpus,
            pids_limit=self.exec_cfg.docker_pids_limit,
            tmpfs_size=self.exec_cfg.docker_tmpfs_size,
            read_only_root=False,
        )
        res = sandbox.run_guarded(
            argv,
            cwd=workdir,
            timeout_s=self.exec_cfg.harness_timeout_s,
            max_stdout_bytes=self.exec_cfg.max_log_bytes,
            max_stderr_bytes=self.exec_cfg.max_log_bytes,
        )

        outputs, parse_err = recover_outputs(
            outputs_path, self.exec_cfg.max_output_file_bytes
        )

        return RunResult(
            # "ok" means we have usable observations to compare. A snippet that
            # crashed mid-run still yields recovered partial output (the crash
            # becomes a comparable observation), so we key on having outputs.
            ok=outputs is not None,
            outputs=outputs,
            stdout=res.stdout,
            stderr=res.stderr,
            timed_out=res.timed_out,
            returncode=res.returncode,
            duration_s=res.duration_s,
            error=parse_err,
        )
