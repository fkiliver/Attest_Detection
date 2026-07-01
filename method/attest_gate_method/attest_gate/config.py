from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


DEFAULT_BASE_URL = os.getenv("LLM_BASE_URL", "https://llm-provider.example/v1")
DEFAULT_MODEL = os.getenv("LLM_MODEL", "configured-llm")
DEFAULT_API_KEY_ENV = os.getenv("LLM_API_KEY_ENV", "LLM_API_KEY")
FALLBACK_API_KEY_ENVS = ("ATTEST_API_KEY", "EVICLONE_API_KEY", "OPENAI_API_KEY")
DEFAULT_OUTPUT_DIR = Path("attest_runs")
DEFAULT_BASE_MODEL = "dsfm"
DEFAULT_DSFM_REPO_URL = "https://github.com/xu-zhiwei/DSFM"
DEFAULT_DSFM_REPO_DIR = Path("external") / "DSFM"
DEFAULT_BASE_PREDICTIONS = Path("attest_runs") / "dsfm_base_predictions" / "predictions.txt"
DEFAULT_BASE_PREDICTION_FORMAT = "function_id_a function_id_b label [confidence] [margin]"


@dataclass(frozen=True)
class LLMConfig:
    base_url: str = DEFAULT_BASE_URL
    model: str = DEFAULT_MODEL
    timeout_sec: int = 120
    temperature: float = 0.0
    max_tokens: int = 2048
    thinking_type: str = "disabled"
    api_key_env: str = DEFAULT_API_KEY_ENV
    fallback_api_key_env: str = "ATTEST_API_KEY"

    def resolve_api_key(self, explicit_api_key: str = "") -> str:
        if explicit_api_key:
            return explicit_api_key
        candidates = [self.api_key_env, self.fallback_api_key_env, *FALLBACK_API_KEY_ENVS]
        for env_name in dict.fromkeys(name for name in candidates if name):
            value = os.getenv(env_name, "")
            if value:
                return value
        return ""

    @property
    def endpoint_url(self) -> str:
        return normalize_chat_endpoint(self.base_url)


def normalize_chat_endpoint(base_or_endpoint: str) -> str:
    value = (base_or_endpoint or DEFAULT_BASE_URL).strip().rstrip("/")
    parsed = urlparse(value)
    path = parsed.path.rstrip("/")
    if path.endswith("/chat/completions"):
        return value
    if path.endswith("/v1"):
        return value + "/chat/completions"
    return value + "/v1/chat/completions"


def load_json_config(path: Path | None) -> dict[str, Any]:
    if not path:
        return {}
    if not path.exists():
        raise FileNotFoundError(f"config file not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def find_default_dataset(start_dir: Path | None = None) -> Path:
    root = (start_dir or Path.cwd()).resolve()
    candidates = [
        root / "data" / "bcb_exported_balanced_1000.jsonl",
        root / "dataset" / "bcb_llm_refined_hard_cases" / "pairs.jsonl",
        root / "release_inputs" / "bcb_exported_balanced_1000.jsonl",
        root.parent / "dataset" / "bcb_llm_refined_hard_cases" / "pairs.jsonl",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return candidates[0]


def coerce_path(value: str | Path | None, default: Path) -> Path:
    if value is None or str(value).strip() == "":
        return default
    return Path(value)
