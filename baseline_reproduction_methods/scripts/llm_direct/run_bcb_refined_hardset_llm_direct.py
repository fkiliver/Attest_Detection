from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from dotenv_api_key import load_api_key_from_dotenv


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTDIR = (
    REPO_ROOT
    / "eviclone_runs"
    / "baseline_reproduction"
    / "bcb_llm_refined_hard_cases_baselines"
    / "llm_direct_input"
)


def main() -> int:
    status = load_api_key_from_dotenv(REPO_ROOT / ".env", "LLM_API_KEY")
    if not os.environ.get("LLM_API_KEY"):
        print(json.dumps({"status": "missing_api_key", "dotenv": redact_status(status)}, ensure_ascii=False))
        return 2

    outdir = Path(os.environ.get("LLM_DIRECT_OUTDIR", str(DEFAULT_OUTDIR)))
    if not outdir.is_absolute():
        outdir = REPO_ROOT / outdir
    dataset = Path(os.environ.get("LLM_DIRECT_DATASET", str(outdir / "pairs.jsonl")))
    split_dir = Path(os.environ.get("LLM_DIRECT_SPLIT_DIR", str(outdir / "splits")))
    if not dataset.is_absolute():
        dataset = REPO_ROOT / dataset
    if not split_dir.is_absolute():
        split_dir = REPO_ROOT / split_dir
    policy = os.environ.get("LLM_DIRECT_POLICY", "bcb-alignment")

    outdir.mkdir(parents=True, exist_ok=True)
    log_path = outdir / "llm_direct_run.log"
    cmd = [
        sys.executable,
        "scripts/run_llm_unordered.py",
        "--dataset",
        str(dataset),
        "--split-dir",
        str(split_dir),
        "--splits",
        "test",
        "--output",
        str(outdir / "llm_direct_cards.jsonl"),
        "--report-path",
        str(outdir / "llm_direct_cards.report.md"),
        "--workers",
        os.environ.get("LLM_DIRECT_WORKERS", "64"),
        "--policy",
        policy,
        "--llm-retries",
        os.environ.get("LLM_DIRECT_RETRIES", "1"),
        "--timeout-sec",
        os.environ.get("LLM_DIRECT_TIMEOUT_SEC", "90"),
        "--model",
        os.environ.get("LLM_DIRECT_MODEL", "configured-llm"),
        "--base-url",
        os.environ.get("LLM_DIRECT_BASE_URL", "https://llm-provider.example/v1"),
        "--api-key-env",
        "LLM_API_KEY",
        "--temperature",
        "0",
        "--max-tokens",
        os.environ.get("LLM_DIRECT_MAX_TOKENS", "2048"),
        "--thinking-type",
        os.environ.get("LLM_DIRECT_THINKING_TYPE", "disabled"),
        "--resume-existing",
        "--resume-decision-source",
        "llm_bcb_gold",
        "--resume-accept-abstain",
    ]
    with log_path.open("a", encoding="utf-8", errors="replace") as log:
        log.write("\n=== bcb refined hardset llm-direct run ===\n")
        log.write(
            json.dumps(
                {
                    "dotenv": redact_status(status),
                    "workers": cmd[cmd.index("--workers") + 1],
                    "policy": policy,
                    "dataset": str(dataset),
                    "split_dir": str(split_dir),
                    "outdir": str(outdir),
                },
                ensure_ascii=False,
            )
            + "\n"
        )
        proc = subprocess.run(cmd, cwd=REPO_ROOT, stdout=log, stderr=subprocess.STDOUT, text=True)
    print(
        json.dumps(
            {
                "returncode": proc.returncode,
                "log": str(log_path),
                "cards": str(outdir / "llm_direct_cards.jsonl"),
                "report": str(outdir / "llm_direct_cards.report.md"),
            },
            ensure_ascii=False,
        )
    )
    return proc.returncode


def redact_status(status: dict[str, object]) -> dict[str, object]:
    return {k: status.get(k) for k in ("exists", "contains_key", "loaded", "available")}


if __name__ == "__main__":
    raise SystemExit(main())
