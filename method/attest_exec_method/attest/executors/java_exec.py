"""Java executor: host ``javac``/``java`` by default, Docker (temurin) opt-in.

The harness source (LLM-filled ``Harness.java``) and the hand-written
``Json.java`` are compiled together in an isolated work directory. ``Json.java``
is copied from ``harness_support/java`` so the LLM never sees or edits it.

Class-name collisions between the two snippets in a pair are avoided at a higher
level by giving side A and side B *separate work directories*; within a dir the
fixed entry class is always ``Harness``.
"""

from __future__ import annotations

import json
import os
import shutil
from pathlib import Path

from ..config import DEFAULT, Config
from . import sandbox
from .base import CompileResult, Executor, RunResult, ToolchainStatus, recover_outputs

_HARNESS_SUPPORT = Path(__file__).resolve().parent.parent.parent / "harness_support" / "java"
_JSON_SRC = _HARNESS_SUPPORT / "Json.java"


def _resolve_jdk_tool(name: str) -> str | None:
    """Locate a JDK tool (``javac``/``java``) by PATH, then by ``JAVA_HOME``.

    On this Windows host the JDK ``bin`` is not on the PATH that a bare Python
    process sees (only Git Bash injects it), but ``JAVA_HOME`` is set. Falling
    back to ``$JAVA_HOME/bin`` makes the executor robust regardless of how it was
    launched.
    """
    found = shutil.which(name)
    if found:
        return found
    java_home = os.environ.get("JAVA_HOME")
    if java_home:
        exe = name + (".exe" if os.name == "nt" else "")
        candidate = Path(java_home) / "bin" / exe
        if candidate.exists():
            return str(candidate)
    return None


JAVAC = _resolve_jdk_tool("javac")
JAVA = _resolve_jdk_tool("java")


class JavaExecutor(Executor):
    language = "java"

    def __init__(self, config: Config | None = None):
        self.config = config or DEFAULT
        self.exec_cfg = self.config.exec

    # -- toolchain --------------------------------------------------------- #

    def probe(self) -> ToolchainStatus:
        if self.exec_cfg.use_docker:
            if not sandbox.docker_available():
                return ToolchainStatus(False, "Docker requested but not available")
            return ToolchainStatus(True, f"docker:{self.exec_cfg.docker_java_image}")
        if shutil.which("javac") is None and JAVAC is None:
            return ToolchainStatus(False, "javac not found on PATH or JAVA_HOME")
        if JAVA is None:
            return ToolchainStatus(False, "java not found on PATH or JAVA_HOME")
        if not _JSON_SRC.exists():
            return ToolchainStatus(False, f"missing support lib: {_JSON_SRC}")
        return ToolchainStatus(True, f"host javac/java ({JAVAC})")

    # -- compile ----------------------------------------------------------- #

    def compile(self, harness_source: str, workdir: Path) -> CompileResult:
        workdir.mkdir(parents=True, exist_ok=True)
        # Lay down sources. Both files share the default package in this dir.
        (workdir / "Json.java").write_text(
            _JSON_SRC.read_text(encoding="utf-8"), encoding="utf-8"
        )
        (workdir / "Harness.java").write_text(harness_source, encoding="utf-8")

        if self.exec_cfg.use_docker:
            return self._compile_docker(workdir)
        return self._compile_host(workdir)

    def _compile_host(self, workdir: Path) -> CompileResult:
        classes = workdir / "classes"
        classes.mkdir(exist_ok=True)
        argv = [
            JAVAC,
            "-encoding", "UTF-8",
            "-d", str(classes),
            str(workdir / "Json.java"),
            str(workdir / "Harness.java"),
        ]
        res = sandbox.run_guarded(
            argv,
            cwd=workdir,
            timeout_s=self.exec_cfg.compile_timeout_s,
        )
        diagnostics = (res.stdout + res.stderr).decode("utf-8", "replace")
        return CompileResult(
            ok=res.ok,
            workdir=workdir,
            diagnostics=diagnostics,
            command=" ".join(argv),
            duration_s=res.duration_s,
        )

    def _compile_docker(self, workdir: Path) -> CompileResult:
        classes = workdir / "classes"
        classes.mkdir(exist_ok=True)
        inner = [
            "javac", "-encoding", "UTF-8", "-d", "/work/classes",
            "/src/Json.java", "/src/Harness.java",
        ]
        argv = sandbox.build_docker_run(
            image=self.exec_cfg.docker_java_image,
            inner_argv=inner,
            mounts_ro=[(workdir, "/src")],
            mounts_rw=[(classes, "/work/classes")],
            memory=self.exec_cfg.docker_memory,
            cpus=self.exec_cfg.docker_cpus,
            pids_limit=self.exec_cfg.docker_pids_limit,
            tmpfs_size=self.exec_cfg.docker_tmpfs_size,
            read_only_root=False,  # compiler needs to write classes via the bind
        )
        res = sandbox.run_guarded(argv, cwd=workdir, timeout_s=self.exec_cfg.compile_timeout_s)
        diagnostics = (res.stdout + res.stderr).decode("utf-8", "replace")
        return CompileResult(
            ok=res.ok and (classes / "Harness.class").exists(),
            workdir=workdir,
            diagnostics=diagnostics,
            command=" ".join(inner),
            duration_s=res.duration_s,
        )

    # -- run --------------------------------------------------------------- #

    def run(self, compiled: CompileResult, inputs_path: Path) -> RunResult:
        if not compiled.ok:
            return RunResult(ok=False, error="compile failed")
        workdir = compiled.workdir
        outputs_path = workdir / "outputs.json"
        # ensure a stale output from a previous attempt can't be misread
        try:
            outputs_path.unlink()
        except OSError:
            pass

        if self.exec_cfg.use_docker:
            res, produced = self._run_docker(workdir, inputs_path, outputs_path)
        else:
            res, produced = self._run_host(workdir, inputs_path, outputs_path)

        outputs, parse_err = recover_outputs(
            outputs_path, self.exec_cfg.max_output_file_bytes
        )

        return RunResult(
            # "ok" means usable observations exist; a crash mid-run still yields
            # recovered partial output (the crash becomes a comparable result).
            ok=outputs is not None,
            outputs=outputs,
            stdout=res.stdout,
            stderr=res.stderr,
            timed_out=res.timed_out,
            returncode=res.returncode,
            duration_s=res.duration_s,
            error=parse_err,
        )

    def _java_flags(self) -> list[str]:
        return [f"-Xmx{self.exec_cfg.java_max_heap}", *self.exec_cfg.java_extra_flags]

    def _run_host(self, workdir: Path, inputs_path: Path, outputs_path: Path):
        argv = [
            JAVA,
            *self._java_flags(),
            f"-Djava.io.tmpdir={workdir}",
            "-cp", str(workdir / "classes"),
            "Harness",
            str(inputs_path),
            str(outputs_path),
        ]
        res = sandbox.run_guarded(
            argv,
            cwd=workdir,
            timeout_s=self.exec_cfg.harness_timeout_s,
            max_stdout_bytes=self.exec_cfg.max_log_bytes,
            max_stderr_bytes=self.exec_cfg.max_log_bytes,
        )
        return res, True

    def _run_docker(self, workdir: Path, inputs_path: Path, outputs_path: Path):
        classes = workdir / "classes"
        # outputs.json is written to a dedicated rw out-dir bind (root is read-only)
        out_dir = workdir / "out"
        out_dir.mkdir(exist_ok=True)
        inner = [
            "java", *self._java_flags(),
            "-Djava.io.tmpdir=/work",
            "-cp", "/classes",
            "Harness",
            "/in/inputs.json",
            "/out/outputs.json",
        ]
        # stage inputs into the workdir so the bind is a stable dir
        staged_in = workdir / "in"
        staged_in.mkdir(exist_ok=True)
        (staged_in / "inputs.json").write_text(
            inputs_path.read_text(encoding="utf-8"), encoding="utf-8"
        )
        argv = sandbox.build_docker_run(
            image=self.exec_cfg.docker_java_image,
            inner_argv=inner,
            mounts_ro=[(classes, "/classes"), (staged_in, "/in")],
            mounts_rw=[(out_dir, "/out")],
            memory=self.exec_cfg.docker_memory,
            cpus=self.exec_cfg.docker_cpus,
            pids_limit=self.exec_cfg.docker_pids_limit,
            tmpfs_size=self.exec_cfg.docker_tmpfs_size,
        )
        res = sandbox.run_guarded(
            argv,
            cwd=workdir,
            timeout_s=self.exec_cfg.harness_timeout_s,
            max_stdout_bytes=self.exec_cfg.max_log_bytes,
            max_stderr_bytes=self.exec_cfg.max_log_bytes,
        )
        # Copy back whatever the harness produced (final or partial .tmp) to the
        # canonical path the caller reads, so partial-crash recovery works in
        # Docker mode too.
        for name in ("outputs.json", "outputs.json.tmp"):
            src = out_dir / name
            if src.exists():
                (outputs_path.parent / name).write_text(
                    src.read_text(encoding="utf-8"), encoding="utf-8"
                )
        return res, (out_dir / "outputs.json").exists()
