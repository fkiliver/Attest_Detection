"""Stage 2 — make each snippet runnable.

For one side, this loads the language's harness template and drives the repair
loop to fill + compile it. The result is a compiled harness (or an EXEC_FAIL
signal) that Stage 4 will run.
"""

from __future__ import annotations

from pathlib import Path

from .config import Config
from .executors.base import Executor
from .harness_fill import load_template
from .llm import LLMClient
from .repair_loop import BuildResult, build_runnable
from .schemas import Contract, Snippet


def make_runnable(
    snippet: Snippet,
    contract: Contract,
    executor: Executor,
    client: LLMClient,
    config: Config,
    workdir: Path,
) -> BuildResult:
    """Build a compiled harness for ``snippet`` under ``workdir``."""
    template = load_template(snippet.language)
    workdir.mkdir(parents=True, exist_ok=True)
    return build_runnable(
        snippet=snippet,
        contract=contract,
        executor=executor,
        client=client,
        config=config,
        workdir=workdir,
        template=template,
    )
