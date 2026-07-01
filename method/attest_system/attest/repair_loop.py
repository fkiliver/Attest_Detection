"""Compile/startup repair loop for making a snippet runnable.

Drives the iterate-with-the-LLM process: fill the harness, compile, and on
failure feed the compiler diagnostics back to the LLM up to a budget. Two
failure classes are handled distinctly:

  * COMPILE failure  — ``javac``/``g++`` rejects the source; diagnostics fed back.
  * STARTUP failure  — compiles, but running it produces no usable output (it
    crashed before writing, or every case failed with the same infra error).
    A snippet that legitimately throws on inputs is NOT a startup failure — that
    is real behavioral evidence and is preserved.

An oscillation guard stops if the LLM regenerates a byte-identical harness. On
exhaustion the side is marked EXEC_FAIL, which the pipeline turns into an honest
``UNDECIDED_EXEC`` abstention rather than a forced verdict.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path

from .config import Config
from .executors.base import CompileResult, Executor
from .harness_fill import fill_template
from .llm import LLMClient
from .prompts import stage2_messages, stage2_repair_messages
from .schemas import Contract, Snippet


@dataclass
class BuildResult:
    ok: bool
    source: str
    compiled: CompileResult | None
    attempts: int
    diagnostics: str = ""
    holes_history: list[dict[str, str]] | None = None


def _holes_from_llm(data: dict) -> dict[str, str]:
    holes = data.get("holes", data)  # tolerate the model returning holes at top level
    if not isinstance(holes, dict):
        raise ValueError("LLM did not return a holes object")
    # keep only the recognized keys; stringify defensively
    return {k: str(holes.get(k, "")) for k in ("SNIPPET", "SETUP", "INVOKE", "OBSERVE")}


def build_runnable(
    snippet: Snippet,
    contract: Contract,
    executor: Executor,
    client: LLMClient,
    config: Config,
    workdir: Path,
    template: str,
) -> BuildResult:
    """Fill -> compile -> repair until it compiles or the budget is spent."""
    seen_hashes: set[str] = set()
    history: list[dict[str, str]] = []

    # initial generation
    data = client.chat_json(
        stage2_messages(snippet, contract, template),
        tag=f"stage2-{snippet.id}",
        max_tokens=8192,
    )
    holes = _holes_from_llm(data)

    last_diag = ""
    last_source = ""
    max_attempts = config.decision.max_compile_repairs + 1
    for attempt in range(1, max_attempts + 1):
        history.append(holes)
        try:
            source = fill_template(snippet.language, holes)
        except ValueError as e:
            # malformed holes; ask the LLM to regenerate from scratch
            last_diag = f"template fill error: {e}"
            data = client.chat_json(
                stage2_messages(snippet, contract, template),
                tag=f"stage2-{snippet.id}-refill{attempt}",
                max_tokens=8192,
            )
            holes = _holes_from_llm(data)
            continue

        last_source = source
        digest = hashlib.sha256(source.encode("utf-8")).hexdigest()
        if digest in seen_hashes:
            # oscillation: the model produced an identical harness again
            return BuildResult(
                ok=False, source=source, compiled=None, attempts=attempt,
                diagnostics="repair oscillation: identical harness regenerated\n" + last_diag,
                holes_history=history,
            )
        seen_hashes.add(digest)

        compiled = executor.compile(source, workdir)
        if compiled.ok:
            return BuildResult(
                ok=True, source=source, compiled=compiled, attempts=attempt,
                diagnostics="", holes_history=history,
            )

        last_diag = compiled.diagnostics
        if attempt >= max_attempts:
            break

        # feed diagnostics back
        data = client.chat_json(
            stage2_repair_messages(
                snippet, contract, template, source, compiled.diagnostics,
                compiled.command, kind="compile",
            ),
            tag=f"stage2-{snippet.id}-repair{attempt}",
            max_tokens=8192,
        )
        holes = _holes_from_llm(data)

    return BuildResult(
        ok=False, source=last_source, compiled=None,
        attempts=max_attempts, diagnostics=last_diag, holes_history=history,
    )
