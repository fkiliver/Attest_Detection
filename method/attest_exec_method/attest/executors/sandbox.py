"""Low-level sandboxed process execution shared by all language executors.

Provides one primitive — :func:`run_guarded` — that launches a subprocess with:
  * an isolated working directory (caller-provided scratch);
  * a wall-clock timeout that kills the WHOLE process tree (not just the parent),
    using ``taskkill /T /F`` on Windows (``wmic`` is absent on this host) and a
    new session + ``killpg`` on POSIX;
  * stdin closed (``DEVNULL``) so a snippet that reads stdin hits EOF instead of
    blocking forever;
  * stdout/stderr captured to size-capped temp files (never unbounded pipes,
    which a chatty snippet could use to deadlock or exhaust memory);
  * POSIX resource limits (address space / CPU / file size) via ``preexec_fn``.

It also builds hardened ``docker run`` argument lists for the opt-in Docker
executor (``--network none``, read-only root, tmpfs scratch, mem/cpu/pids caps).
"""

from __future__ import annotations

import os
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path

IS_WINDOWS = os.name == "nt"


def _resolve_docker() -> str | None:
    """Locate the ``docker`` CLI by PATH, then known Docker Desktop locations.

    Like the JDK tools, ``docker`` is often absent from the PATH a bare Python
    process inherits on this Windows host (Git Bash injects it via profile), even
    though Docker Desktop is installed. Fall back to the standard install path so
    the executor works regardless of how Python was launched.
    """
    found = shutil.which("docker")
    if found:
        return found
    candidates = []
    if IS_WINDOWS:
        candidates = [
            Path(os.environ.get("ProgramFiles", r"C:\Program Files"))
            / "Docker" / "Docker" / "resources" / "bin" / "docker.exe",
            Path(r"C:\ProgramData\DockerDesktop\version-bin\docker.exe"),
        ]
    else:  # pragma: no cover
        candidates = [Path("/usr/bin/docker"), Path("/usr/local/bin/docker")]
    for c in candidates:
        if c.exists():
            return str(c)
    return None


DOCKER = _resolve_docker()


@dataclass
class ProcResult:
    """Outcome of a guarded subprocess run."""

    returncode: int | None          # None if killed before exit
    stdout: bytes
    stderr: bytes
    timed_out: bool
    duration_s: float

    @property
    def ok(self) -> bool:
        return self.returncode == 0 and not self.timed_out


def _read_capped(path: Path, cap: int) -> bytes:
    try:
        data = path.read_bytes()
    except OSError:
        return b""
    return data[:cap] + b"\n...[truncated]\n" if len(data) > cap else data


def _posix_limits(max_as_bytes: int, cpu_seconds: int, fsize_bytes: int):
    """Return a preexec_fn that detaches the session and applies rlimits.

    Only used on POSIX. Detaching the session (``setsid``) lets us signal the
    whole group; the rlimits are a defense-in-depth backstop on top of any JVM
    or Docker caps.
    """

    def _apply():  # pragma: no cover - exercised only on POSIX/Docker host
        import resource

        os.setsid()
        if max_as_bytes:
            resource.setrlimit(resource.RLIMIT_AS, (max_as_bytes, max_as_bytes))
        if cpu_seconds:
            resource.setrlimit(resource.RLIMIT_CPU, (cpu_seconds, cpu_seconds))
        if fsize_bytes:
            resource.setrlimit(resource.RLIMIT_FSIZE, (fsize_bytes, fsize_bytes))

    return _apply


def _kill_tree(proc: subprocess.Popen) -> None:
    """Forcibly kill a process and all of its descendants."""
    if proc.poll() is not None:
        return
    if IS_WINDOWS:
        # taskkill /T kills the whole tree; /F forces it. wmic is unavailable on
        # this Windows build, so we rely on taskkill which ships with Windows.
        try:
            subprocess.run(
                ["taskkill", "/T", "/F", "/PID", str(proc.pid)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=15,
                check=False,
            )
        except Exception:
            pass
        try:
            proc.kill()
        except Exception:
            pass
    else:  # pragma: no cover - POSIX/Docker
        try:
            os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
        except Exception:
            try:
                proc.kill()
            except Exception:
                pass


def run_guarded(
    argv: list[str],
    *,
    cwd: Path,
    timeout_s: float,
    max_stdout_bytes: int = 1 * 1024 * 1024,
    max_stderr_bytes: int = 1 * 1024 * 1024,
    max_as_bytes: int = 1024 * 1024 * 1024,
    cpu_seconds: int = 0,
    fsize_bytes: int = 256 * 1024 * 1024,
    env: dict[str, str] | None = None,
) -> ProcResult:
    """Run ``argv`` in ``cwd`` with a hard timeout and tree-kill on expiry.

    stdin is closed; stdout/stderr go to capped temp files. Returns a
    :class:`ProcResult`; never raises for non-zero exit or timeout.
    """
    cwd.mkdir(parents=True, exist_ok=True)
    out_f = tempfile.NamedTemporaryFile(
        delete=False, dir=cwd, prefix=".stdout_", suffix=".log"
    )
    err_f = tempfile.NamedTemporaryFile(
        delete=False, dir=cwd, prefix=".stderr_", suffix=".log"
    )
    out_path, err_path = Path(out_f.name), Path(err_f.name)

    run_env = dict(os.environ)
    if env:
        run_env.update(env)

    popen_kwargs: dict = dict(
        cwd=str(cwd),
        stdin=subprocess.DEVNULL,
        stdout=out_f,
        stderr=err_f,
        env=run_env,
    )
    if IS_WINDOWS:
        # CREATE_NEW_PROCESS_GROUP lets us target the group; taskkill /T does the
        # actual descendant cleanup.
        popen_kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP
    else:  # pragma: no cover - POSIX/Docker
        popen_kwargs["preexec_fn"] = _posix_limits(
            max_as_bytes, cpu_seconds, fsize_bytes
        )

    start = time.monotonic()
    timed_out = False
    try:
        proc = subprocess.Popen(argv, **popen_kwargs)
    finally:
        out_f.close()
        err_f.close()

    try:
        proc.wait(timeout=timeout_s)
    except subprocess.TimeoutExpired:
        timed_out = True
        _kill_tree(proc)
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            pass
    duration = time.monotonic() - start

    stdout = _read_capped(out_path, max_stdout_bytes)
    stderr = _read_capped(err_path, max_stderr_bytes)
    for p in (out_path, err_path):
        try:
            p.unlink()
        except OSError:
            pass

    return ProcResult(
        returncode=proc.returncode,
        stdout=stdout,
        stderr=stderr,
        timed_out=timed_out,
        duration_s=duration,
    )


# --------------------------------------------------------------------------- #
# Scratch directories
# --------------------------------------------------------------------------- #


def make_scratch(prefix: str = "sce_") -> Path:
    """Create a fresh temp scratch directory and return its path."""
    return Path(tempfile.mkdtemp(prefix=prefix))


def rmtree_quiet(path: Path, retries: int = 3) -> None:
    """Remove a directory tree, tolerating Windows file-lock races.

    On Windows a just-exited JVM can momentarily hold a ``.class`` or output
    file open (also Defender), so ``rmtree`` may raise WinError 32. We retry with
    a short backoff rather than failing the run.
    """
    for attempt in range(retries):
        try:
            shutil.rmtree(path, ignore_errors=False)
            return
        except OSError:
            if attempt == retries - 1:
                shutil.rmtree(path, ignore_errors=True)
                return
            time.sleep(0.2 * (attempt + 1))


# --------------------------------------------------------------------------- #
# Docker
# --------------------------------------------------------------------------- #


def docker_available() -> bool:
    """True if the ``docker`` CLI is present and the daemon answers."""
    if DOCKER is None:
        return False
    try:
        r = subprocess.run(
            [DOCKER, "info"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=30,
            check=False,
        )
        return r.returncode == 0
    except Exception:
        return False


def to_docker_path(p: Path) -> str:
    """Convert a host path to a form acceptable as a Docker bind source.

    On Windows, Docker Desktop accepts forward-slashed absolute paths;
    we also normalize the drive-letter form.
    """
    s = str(p.resolve())
    if IS_WINDOWS:
        s = s.replace("\\", "/")
    return s


def build_docker_run(
    *,
    image: str,
    inner_argv: list[str],
    mounts_ro: list[tuple[Path, str]],
    mounts_rw: list[tuple[Path, str]],
    workdir: str = "/work",
    memory: str = "512m",
    cpus: str = "1.0",
    pids_limit: int = 256,
    tmpfs_size: str = "256m",
    network_none: bool = True,
    read_only_root: bool = True,
    run_as_nobody: bool = True,
) -> list[str]:
    """Assemble a hardened ``docker run`` argv.

    The container root is read-only with a writable tmpfs at ``workdir``;
    networking is disabled; capabilities are dropped; mem/cpu/pids are capped.
    ``mounts_ro``/``mounts_rw`` are ``(host_path, container_path)`` pairs.
    """
    argv: list[str] = [
        DOCKER or "docker", "run", "--rm",
        "--memory", memory,
        "--memory-swap", memory,
        "--cpus", cpus,
        "--pids-limit", str(pids_limit),
        "--cap-drop", "ALL",
        "--security-opt", "no-new-privileges",
        "-w", workdir,
    ]
    if network_none:
        argv += ["--network", "none"]
    if read_only_root:
        argv += ["--read-only", "--tmpfs", f"{workdir}:rw,size={tmpfs_size},nosuid"]
    if run_as_nobody:
        argv += ["--user", "65534:65534"]
    for host, cont in mounts_ro:
        argv += ["--mount", f"type=bind,src={to_docker_path(host)},dst={cont},ro"]
    for host, cont in mounts_rw:
        argv += ["--mount", f"type=bind,src={to_docker_path(host)},dst={cont}"]
    argv.append(image)
    argv += inner_argv
    return argv


def docker_kill_by_name(name: str) -> None:
    """Best-effort ``docker kill`` of a named container (timeout path)."""
    try:
        subprocess.run(
            [DOCKER or "docker", "kill", name],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=20,
            check=False,
        )
    except Exception:
        pass
