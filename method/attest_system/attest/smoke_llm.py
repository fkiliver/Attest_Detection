"""Live smoke test for the LLM client.

Run directly:  python -m attest.smoke_llm
This makes ONE real API call, so it is not part of the offline pytest suite.
"""

from __future__ import annotations

import sys

from .llm import LLMClient


def main() -> int:
    client = LLMClient()
    print(f"Endpoint : {client.cfg.base_url}")
    print(f"Model    : {client.cfg.model}")

    # 1) Plain text round-trip. configured-reasoning-model is a reasoning model, so give it
    # enough headroom that `content` is actually populated after reasoning.
    r1 = client.chat(
        [{"role": "user", "content": "Reply with exactly the word: pong"}],
        tag="smoke-text",
        max_tokens=512,
    )
    print(f"\n[text] -> {r1.text.strip()!r}  (cached={r1.cached})")

    # 2) JSON-mode round-trip + parse.
    obj = client.chat_json(
        [
            {
                "role": "user",
                "content": (
                    "Return a JSON object with keys 'lang' (value 'java') and "
                    "'ok' (boolean true). No prose."
                ),
            }
        ],
        tag="smoke-json",
        max_tokens=64,
    )
    print(f"[json] -> {obj!r}")

    ok = (
        isinstance(obj, dict)
        and obj.get("lang") == "java"
        and obj.get("ok") is True
    )
    print("\n" + client.cost_summary())
    if not ok:
        print("SMOKE FAILED: JSON body did not match expectation", file=sys.stderr)
        return 1
    print("SMOKE OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
