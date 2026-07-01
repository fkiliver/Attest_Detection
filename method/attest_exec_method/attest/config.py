"""Central configuration for Attest.

All tunable knobs live here: the LLM endpoint/model, decision thresholds,
execution timeouts and resource caps, and the canonical filesystem layout for
run artifacts. Values can be overridden via environment variables (and a
project-local ``.env`` file, which we parse ourselves to avoid an extra
dependency).
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

# --------------------------------------------------------------------------- #
# Paths
# --------------------------------------------------------------------------- #

# repo root = the directory that contains this package
PROJECT_ROOT: Path = Path(__file__).resolve().parent.parent
HARNESS_SUPPORT_DIR: Path = PROJECT_ROOT / "harness_support"
RUNS_DIR: Path = PROJECT_ROOT / "runs"
LLM_CACHE_DIR: Path = PROJECT_ROOT / ".llm_cache"
ENV_FILE: Path = PROJECT_ROOT / ".env"


def _load_dotenv(path: Path = ENV_FILE) -> None:
    """Populate ``os.environ`` from a simple ``KEY=value`` .env file.

    Existing environment variables win over the file (standard dotenv
    semantics). Lines that are blank or start with ``#`` are ignored. We keep
    this tiny on purpose — no quoting/escaping rules beyond stripping a single
    layer of surrounding quotes.
    """
    if not path.exists():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


_load_dotenv()


# --------------------------------------------------------------------------- #
# LLM
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class LLMConfig:
    """configured LLM (OpenAI-compatible) client configuration."""

    base_url: str = os.environ.get("LLM_BASE_URL", "https://llm-provider.example/v1")
    model: str = os.environ.get("LLM_MODEL", "configured-llm")
    api_key_env: str = "LLM_API_KEY"
    # Deterministic decoding by default — reproducibility matters for the paper.
    temperature: float = 0.0
    max_tokens: int = 8192
    request_timeout_s: int = 180
    max_retries: int = 4
    retry_backoff_s: float = 2.0
    # On-disk response cache keyed by (model, messages, params). Saves cost and
    # makes re-runs of the pipeline reproducible.
    cache_enabled: bool = True

    # Pricing (USD per 1M tokens) purely for the cost log / guardrail. These are
    # placeholders for telemetry only and never affect behavior; adjust freely.
    price_in_per_mtok: float = 0.0
    price_out_per_mtok: float = 0.0

    @property
    def api_key(self) -> str:
        key = os.environ.get(self.api_key_env, "")
        if not key:
            raise RuntimeError(
                f"Missing {self.api_key_env}. Put it in {ENV_FILE} "
                f"(LLM_API_KEY=...) or export it in the environment."
            )
        return key


# --------------------------------------------------------------------------- #
# Execution / sandbox
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class ExecConfig:
    """Limits and toggles for compiling and running candidate harnesses."""

    # Per-case soft timeout (one input case) and whole-harness hard timeout.
    case_timeout_s: float = 5.0
    harness_timeout_s: float = 60.0
    compile_timeout_s: float = 120.0

    # JVM resource caps applied to every host Java run.
    java_max_heap: str = "256m"
    java_extra_flags: tuple[str, ...] = (
        "-XX:+ExitOnOutOfMemoryError",
        "-XX:+UseSerialGC",
        "-Dfile.encoding=UTF-8",
        "-Duser.language=en",
        "-Duser.country=US",
        "-Duser.timezone=UTC",
        "-Djava.awt.headless=true",
        "-XX:TieredStopAtLevel=1",
        "-XX:-UsePerfData",
    )

    # Output size caps (bytes / element counts) — also enforced inside the
    # harness, these are the orchestrator-side backstops when reading files.
    max_output_file_bytes: int = 32 * 1024 * 1024
    max_log_bytes: int = 1 * 1024 * 1024

    # Docker hardening (opt-in for Java; mandatory for C/C++ since no host gcc).
    use_docker: bool = False
    docker_java_image: str = "eclipse-temurin:21"
    docker_cpp_image: str = "gcc:14"
    docker_memory: str = "512m"
    docker_cpus: str = "1.0"
    docker_pids_limit: int = 256
    docker_tmpfs_size: str = "256m"


# --------------------------------------------------------------------------- #
# Decision thresholds
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class DecisionConfig:
    """Verdict thresholds and repair budgets."""

    # Fraction of input cases that must match for a Clone verdict.
    pass_rate_theta: float = 0.85
    # When the in-domain pass-rate is below theta, invoke the LLM adjudicator to
    # make a holistic clone judgment from the code plus the concrete divergences,
    # rather than auto-deciding non-clone. A low pass-rate is NOT necessarily a
    # different function: in benchmarks like OJClone, two same-problem solutions
    # can each carry incidental bugs / narrower input checks that make them differ
    # on many synthesized inputs while still being "clones" (both AC on the
    # problem's intended data). The adjudicator reads the source to tell "same
    # task, incidental divergence" from "genuinely different function". This floor
    # is the minimum pass-rate that still triggers adjudication; default 0.0 means
    # every below-threshold pair with same_function is adjudicated. Set to 1.0 to
    # disable adjudication (pure pass-rate verdict).
    adjudicate_floor: float = 0.0
    # Float comparison tolerance.
    float_abs_eps: float = 1e-9
    float_rel_eps: float = 1e-6
    # Repair budgets: compile failures vs startup (ran-but-no-output) failures.
    max_compile_repairs: int = 6
    max_startup_repairs: int = 2

    # When the pipeline cannot construct behavioral evidence (a snippet can't be
    # made runnable, no inputs synthesized, toolchain missing, or a Stage-4 exec
    # failure), fall back to the LLM-direct judgment instead of abstaining. The
    # fallback verdict is flagged in PairOutcome.extra['fallback'] = 'llm_direct'.
    # Set False to restore pure abstention (UNDECIDED_EXEC) — e.g. to measure the
    # raw coverage/abstention rate of the execution pipeline alone.
    llm_fallback_on_exec_fail: bool = True

    # External-dependency gate: when a snippet depends on the network, filesystem,
    # clock, randomness, etc., the reconstruction may stub that dependency into an
    # identical mock on both sides, manufacturing a false 'clone'. When this gate
    # is on and an execution-grounded CLONE verdict involves such a dependency, we
    # treat the execution evidence as untrusted and defer to a behavior-focused
    # code reading (improved direct judge). Only overrides clone->non-clone, so it
    # cannot reduce recall. Reads only code, never labels.
    external_dependency_gate: bool = True


@dataclass(frozen=True)
class AblationConfig:
    """Toggles for ablation studies (all False = full system).

    Each flag disables one sub-component so its contribution can be measured:
      * no_label        — skip Stage 1 functional labels/contract guidance; the
                          LLM generates inputs from bare code (tests intent
                          coverage of the labels).
      * no_diff_explainer — after normalization, any residual difference counts
                          as a mismatch (no LLM adjudication); tests precision
                          recovered by the explainer.
      * no_execution    — build runnable harnesses + inputs as usual, but decide
                          the verdict from text/structure similarity of the
                          completed code instead of runtime behavior; tests that
                          gains come from execution, not from the completion step.
    """

    no_label: bool = False
    no_diff_explainer: bool = False
    no_execution: bool = False
    # Similarity threshold used only when no_execution is set.
    text_sim_threshold: float = 0.6


@dataclass(frozen=True)
class Config:
    """Top-level config aggregate, passed through the pipeline."""

    llm: LLMConfig = field(default_factory=LLMConfig)
    exec: ExecConfig = field(default_factory=ExecConfig)
    decision: DecisionConfig = field(default_factory=DecisionConfig)
    ablation: AblationConfig = field(default_factory=AblationConfig)
    runs_dir: Path = RUNS_DIR

    def with_docker(self, enabled: bool = True) -> "Config":
        """Return a copy with the Docker executor toggled."""
        from dataclasses import replace

        return replace(self, exec=replace(self.exec, use_docker=enabled))

    def with_ablation(self, **flags) -> "Config":
        """Return a copy with ablation flags overridden."""
        from dataclasses import replace

        return replace(self, ablation=replace(self.ablation, **flags))


# A ready-to-use default. Most call sites can just import ``DEFAULT``.
DEFAULT = Config()

# JSON wire-protocol version shared with the Java/C++ harnesses. Bump in lockstep
# with the harness templates if the schema changes.
PROTOCOL_VERSION = 1
