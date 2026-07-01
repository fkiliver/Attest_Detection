from __future__ import annotations

import json
import re
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any

from .config import LLMConfig


class LLMError(RuntimeError):
    pass


NON_RETRYABLE_LLM_ERROR_MARKERS = [
    "http 401",
    "http 402",
    "http 403",
    "insufficient balance",
    "missing api key",
    "invalid api key",
    "unauthorized",
    "forbidden",
]


def is_non_retryable_llm_error(exc: Exception) -> bool:
    return contains_non_retryable_llm_error(str(exc))


def contains_non_retryable_llm_error(text: str) -> bool:
    lowered = str(text).lower()
    return any(marker in lowered for marker in NON_RETRYABLE_LLM_ERROR_MARKERS)



@dataclass(frozen=True)
class ChatClient:
    config: LLMConfig
    api_key: str

    def complete(self, *, system_prompt: str, user_prompt: str) -> str:
        if not self.api_key:
            raise LLMError(
                "missing API key; set LLM_API_KEY, EVICLONE_API_KEY, "
                "ATTEST_API_KEY, or OPENAI_API_KEY"
            )
        payload: dict[str, Any] = {
            "model": self.config.model,
            "temperature": self.config.temperature,
            "max_tokens": max(1, int(getattr(self.config, "max_tokens", 2048) or 2048)),
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        }
        thinking_type = str(getattr(self.config, "thinking_type", "") or "").strip()
        if thinking_type and self._supports_reasoning_toggle():
            payload["thinking"] = {"type": thinking_type}
        req = urllib.request.Request(
            url=self.config.endpoint_url,
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Authorization": f"Bearer {self.api_key}",
                "User-Agent": "EviClone-Prototype/0.1",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=self.config.timeout_sec) as resp:
                return resp.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", "replace")
            raise LLMError(f"HTTP {exc.code}: {body[:500]}") from exc
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            raise LLMError(f"{type(exc).__name__}: {exc}") from exc

    def _supports_reasoning_toggle(self) -> bool:
        model = str(getattr(self.config, "model", "") or "").lower()
        return model.startswith("configured-reasoning-model") or "reasoning" in model


def normalize_model_text(body: str) -> str:
    body = body.strip()
    try:
        obj = json.loads(body)
    except json.JSONDecodeError:
        return body
    choices = obj.get("choices", [])
    if choices:
        message = choices[0].get("message", {}) or {}
        content = message.get("content")
        if isinstance(content, str):
            return content
    return body


def extract_json_object(text: str) -> dict[str, Any]:
    normalized = normalize_model_text(text).strip()
    if normalized.startswith("```"):
        normalized = re.sub(r"^```(?:json)?", "", normalized, flags=re.IGNORECASE).strip()
        normalized = re.sub(r"```$", "", normalized).strip()
    if normalized.startswith("{") and normalized.endswith("}"):
        try:
            return json.loads(normalized)
        except json.JSONDecodeError:
            obj, _ = json.JSONDecoder().raw_decode(normalized)
            if isinstance(obj, dict):
                return obj
            raise
    match = re.search(r"\{[\s\S]*\}", normalized)
    if not match:
        raise ValueError("no JSON object found in model output")
    snippet = match.group(0)
    try:
        return json.loads(snippet)
    except json.JSONDecodeError:
        obj, _ = json.JSONDecoder().raw_decode(snippet)
        if isinstance(obj, dict):
            return obj
        raise
