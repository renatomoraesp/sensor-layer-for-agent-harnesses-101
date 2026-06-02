"""Anthropic provider adapter."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any


class AnthropicProvider:
    """Minimal Anthropic Messages API adapter."""

    def __init__(
        self,
        *,
        model: str,
        api_key_env: str = "ANTHROPIC_API_KEY",
        endpoint: str = "https://api.anthropic.com/v1/messages",
        timeout_seconds: float = 60.0,
    ) -> None:
        self.model = model
        self.api_key_env = api_key_env
        self.endpoint = endpoint
        self.timeout_seconds = timeout_seconds

    def complete(self, prompt: str, *, schema: dict[str, Any] | None = None) -> str:
        """Call Anthropic and return text output."""

        api_key = os.environ.get(self.api_key_env)
        if not api_key:
            raise RuntimeError(f"missing API key environment variable: {self.api_key_env}")
        payload: dict[str, Any] = {
            "model": self.model,
            "max_tokens": 4000,
            "messages": [{"role": "user", "content": prompt}],
        }
        if schema is not None:
            payload["system"] = "Return only JSON that validates against the provided schema."
        data = json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(
            self.endpoint,
            data=data,
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                raw = response.read().decode("utf-8")
        except urllib.error.URLError as exc:
            raise RuntimeError(f"provider request failed: {exc}") from exc
        decoded = json.loads(raw)
        return extract_anthropic_messages_text(decoded)


def extract_anthropic_messages_text(decoded: dict[str, Any]) -> str:
    """Extract model text from an Anthropic Messages response."""

    content = decoded.get("content")
    if isinstance(content, list):
        chunks = [
            str(item["text"])
            for item in content
            if isinstance(item, dict)
            and item.get("type") == "text"
            and isinstance(item.get("text"), str)
        ]
        if chunks:
            return "\n".join(chunks)
    return json.dumps(decoded)
