"""configured LLM LLM client (OpenAI-compatible chat completions over plain HTTPS).

Responsibilities:
  * one ``chat()`` entry point with optional JSON-mode (``response_format``);
  * automatic retry with exponential backoff on transient/network/5xx errors;
  * an on-disk response cache keyed by (model, messages, params) so repeated
    pipeline runs are reproducible and cheap;
  * token + (optional) cost accounting, aggregated process-wide for a guardrail.

We intentionally depend only on ``requests`` — the configured LLM endpoint speaks the
OpenAI wire format, so the SDK buys us nothing here.
"""

from __future__ import annotations

import hashlib
import json
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import requests

from .config import DEFAULT, Config, LLMConfig


class LLMError(RuntimeError):
    """Raised when the LLM call ultimately fails after retries."""


@dataclass
class Usage:
    """Token + wall-time accounting for a single call (and summable)."""

    prompt_tokens: int = 0
    completion_tokens: int = 0
    cached_tokens: int = 0
    calls: int = 0
    seconds: float = 0.0  # wall-clock spent in the LLM request(s)

    def add(self, other: "Usage") -> None:
        self.prompt_tokens += other.prompt_tokens
        self.completion_tokens += other.completion_tokens
        self.cached_tokens += other.cached_tokens
        self.calls += other.calls
        self.seconds += other.seconds

    def snapshot(self) -> "Usage":
        """A copy, for measuring per-stage deltas."""
        return Usage(
            self.prompt_tokens, self.completion_tokens, self.cached_tokens,
            self.calls, self.seconds,
        )

    def delta(self, earlier: "Usage") -> "Usage":
        """This minus an earlier snapshot."""
        return Usage(
            self.prompt_tokens - earlier.prompt_tokens,
            self.completion_tokens - earlier.completion_tokens,
            self.cached_tokens - earlier.cached_tokens,
            self.calls - earlier.calls,
            self.seconds - earlier.seconds,
        )

    @property
    def total_tokens(self) -> int:
        return self.prompt_tokens + self.completion_tokens


@dataclass
class LLMResponse:
    """A normalized chat response."""

    text: str
    usage: Usage
    raw: dict[str, Any] = field(default_factory=dict)
    cached: bool = False

    def json(self) -> Any:
        """Parse ``text`` as JSON.

        Tolerates a model that wraps the object in ```` ```json ```` fences
        despite JSON mode, and trims any leading/trailing prose.
        """
        return _extract_json(self.text)


# --------------------------------------------------------------------------- #
# JSON extraction helpers
# --------------------------------------------------------------------------- #


def _extract_json(text: str) -> Any:
    """Best-effort parse of a JSON value possibly surrounded by noise."""
    s = text.strip()
    if not s:
        raise LLMError("empty LLM response, expected JSON")
    # Fast path: already valid.
    try:
        return json.loads(s)
    except json.JSONDecodeError:
        pass
    # Strip ```json ... ``` or ``` ... ``` fences.
    if s.startswith("```"):
        s = s.split("\n", 1)[1] if "\n" in s else s
        if s.endswith("```"):
            s = s[: s.rfind("```")]
        s = s.strip()
        # ``` may have started with a language tag line we already dropped
        try:
            return json.loads(s)
        except json.JSONDecodeError:
            pass
    # Last resort: grab the outermost {...} or [...] span.
    start = min(
        (i for i in (s.find("{"), s.find("[")) if i != -1),
        default=-1,
    )
    if start != -1:
        opener = s[start]
        closer = "}" if opener == "{" else "]"
        end = s.rfind(closer)
        if end > start:
            try:
                return json.loads(s[start : end + 1])
            except json.JSONDecodeError:
                pass
    raise LLMError(f"could not parse JSON from LLM response: {text[:200]!r}")


# --------------------------------------------------------------------------- #
# Client
# --------------------------------------------------------------------------- #


class LLMClient:
    """Thread-safe LLM chat client with caching and accounting."""

    def __init__(self, config: Config | None = None):
        self.config: Config = config or DEFAULT
        self.cfg: LLMConfig = self.config.llm
        self._session = requests.Session()
        self._lock = threading.Lock()
        self.usage = Usage()
        self._cache_dir: Path = Path(__file__).resolve().parent.parent / ".llm_cache"
        if self.cfg.cache_enabled:
            self._cache_dir.mkdir(parents=True, exist_ok=True)

    # -- public API -------------------------------------------------------- #

    def chat(
        self,
        messages: list[dict[str, str]],
        *,
        json_mode: bool = False,
        temperature: float | None = None,
        max_tokens: int | None = None,
        tag: str = "",
    ) -> LLMResponse:
        """Run one chat completion.

        Args:
            messages: OpenAI-style ``[{"role": ..., "content": ...}]``.
            json_mode: if True, request ``response_format={"type":"json_object"}``.
            temperature/max_tokens: per-call overrides of the config defaults.
            tag: short label recorded in the cache filename for debuggability.
        """
        payload: dict[str, Any] = {
            "model": self.cfg.model,
            "messages": messages,
            "temperature": self.cfg.temperature if temperature is None else temperature,
            "max_tokens": self.cfg.max_tokens if max_tokens is None else max_tokens,
        }
        if json_mode:
            payload["response_format"] = {"type": "json_object"}

        cache_path = self._cache_path(payload, tag) if self.cfg.cache_enabled else None
        if cache_path is not None and cache_path.exists():
            cached = json.loads(cache_path.read_text(encoding="utf-8"))
            resp = self._normalize(cached, cached=True)
            self._record(resp.usage)  # cached: seconds stays ~0
            return resp

        _t = time.monotonic()
        raw = self._post_with_retries(payload)
        elapsed = time.monotonic() - _t
        resp = self._normalize(raw, cached=False)
        resp.usage.seconds = elapsed
        self._record(resp.usage)
        if cache_path is not None:
            cache_path.write_text(
                json.dumps(raw, ensure_ascii=False), encoding="utf-8"
            )
        return resp

    def chat_json(self, messages: list[dict[str, str]], **kw: Any) -> Any:
        """Convenience: ``chat(..., json_mode=True)`` then parse the JSON body."""
        return self.chat(messages, json_mode=True, **kw).json()

    def cost_summary(self) -> str:
        """Human-readable token/cost summary for the process so far."""
        u = self.usage
        cost = (
            u.prompt_tokens / 1_000_000 * self.cfg.price_in_per_mtok
            + u.completion_tokens / 1_000_000 * self.cfg.price_out_per_mtok
        )
        return (
            f"[LLM] calls={u.calls} prompt={u.prompt_tokens} "
            f"completion={u.completion_tokens} cached={u.cached_tokens} "
            f"total={u.total_tokens} est_cost=${cost:.4f}"
        )

    # -- internals --------------------------------------------------------- #

    def _record(self, usage: Usage) -> None:
        with self._lock:
            self.usage.add(usage)

    def _cache_path(self, payload: dict[str, Any], tag: str) -> Path:
        blob = json.dumps(payload, ensure_ascii=False, sort_keys=True)
        digest = hashlib.sha256(blob.encode("utf-8")).hexdigest()[:24]
        safe_tag = "".join(c for c in tag if c.isalnum() or c in "-_")[:40]
        name = f"{safe_tag}_{digest}.json" if safe_tag else f"{digest}.json"
        return self._cache_dir / name

    def _post_with_retries(self, payload: dict[str, Any]) -> dict[str, Any]:
        url = f"{self.cfg.base_url.rstrip('/')}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.cfg.api_key}",
            "Content-Type": "application/json",
        }
        last_err: Exception | None = None
        for attempt in range(self.cfg.max_retries):
            try:
                r = self._session.post(
                    url,
                    headers=headers,
                    json=payload,
                    timeout=self.cfg.request_timeout_s,
                )
            except requests.RequestException as e:  # network/timeout
                last_err = e
            else:
                if r.status_code == 200:
                    return r.json()
                # Retry on rate-limit and server errors; fail fast otherwise.
                if r.status_code in (429, 500, 502, 503, 504):
                    last_err = LLMError(f"HTTP {r.status_code}: {r.text[:200]}")
                else:
                    raise LLMError(f"HTTP {r.status_code}: {r.text[:500]}")
            sleep_s = self.cfg.retry_backoff_s * (2**attempt)
            time.sleep(sleep_s)
        raise LLMError(
            f"LLM call failed after {self.cfg.max_retries} attempts: {last_err}"
        )

    @staticmethod
    def _normalize(raw: dict[str, Any], *, cached: bool) -> LLMResponse:
        try:
            choice = raw["choices"][0]
            text = choice["message"]["content"] or ""
            finish = choice.get("finish_reason")
        except (KeyError, IndexError, TypeError) as e:
            raise LLMError(f"malformed LLM response: {e}: {str(raw)[:300]}")
        # configured-reasoning-model is a reasoning model: it emits `reasoning_content` first and
        # only fills `content` afterwards. If the token budget is exhausted, the
        # response is truncated — either with no content at all, or with content
        # cut off mid-value (which would then fail JSON parsing opaquely). Surface
        # both as a legible truncation error so callers can raise max_tokens.
        if finish == "length":
            if not text:
                raise LLMError(
                    "LLM response truncated (finish_reason=length) before any "
                    "content was produced — increase max_tokens for this call."
                )
            raise LLMError(
                "LLM response truncated (finish_reason=length) with "
                f"{len(text)} chars of content — output did not fit in max_tokens; "
                "increase max_tokens or reduce requested output size."
            )
        u = raw.get("usage", {}) or {}
        details = u.get("prompt_tokens_details", {}) or {}
        usage = Usage(
            prompt_tokens=int(u.get("prompt_tokens", 0)),
            completion_tokens=int(u.get("completion_tokens", 0)),
            cached_tokens=int(
                details.get("cached_tokens", u.get("prompt_cache_hit_tokens", 0)) or 0
            ),
            calls=1,
        )
        return LLMResponse(text=text, usage=usage, raw=raw, cached=cached)


# A lazily-created module-level default client for simple call sites.
_default_client: LLMClient | None = None
_default_lock = threading.Lock()


def get_client(config: Config | None = None) -> LLMClient:
    """Return a shared default client (created on first use)."""
    global _default_client
    with _default_lock:
        if _default_client is None:
            _default_client = LLMClient(config)
        return _default_client
