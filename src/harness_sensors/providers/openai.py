"""OpenAI provider adapter using the Responses-style chat-compatible endpoint."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any


class OpenAIProvider:
    """Minimal OpenAI API adapter isolated behind the provider interface."""

    def __init__(
        self,
        *,
        model: str,
        api_key_env: str = "OPENAI_API_KEY",
        endpoint: str = "https://api.openai.com/v1/responses",
        timeout_seconds: float = 60.0,
    ) -> None:
        self.model = model
        self.api_key_env = api_key_env
        self.endpoint = endpoint
        self.timeout_seconds = timeout_seconds

    def complete(self, prompt: str, *, schema: dict[str, Any] | None = None) -> str:
        """Call OpenAI and return text output."""

        api_key = os.environ.get(self.api_key_env)
        if not api_key:
            raise RuntimeError(f"missing API key environment variable: {self.api_key_env}")
        payload: dict[str, Any] = {
            "model": self.model,
            "input": prompt,
        }
        if schema is not None:
            payload["text"] = {
                "format": {
                    "type": "json_schema",
                    "name": "sensor_result",
                    "schema": schema,
                    "strict": True,
                }
            }
        return _post_json(self.endpoint, payload, api_key, self.timeout_seconds)


def _post_json(endpoint: str, payload: dict[str, Any], api_key: str, timeout_seconds: float) -> str:
    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        endpoint,
        data=data,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
            raw = response.read().decode("utf-8")
    except urllib.error.URLError as exc:
        raise RuntimeError(f"provider request failed: {exc}") from exc
    decoded = json.loads(raw)
    text = decoded.get("output_text")
    if isinstance(text, str):
        return text
    output = decoded.get("output")
    if isinstance(output, list):
        chunks: list[str] = []
        for item in output:
            if not isinstance(item, dict):
                continue
            content = item.get("content")
            if not isinstance(content, list):
                continue
            for content_item in content:
                if isinstance(content_item, dict) and isinstance(content_item.get("text"), str):
                    chunks.append(str(content_item["text"]))
        if chunks:
            return "\n".join(chunks)
    return str(raw)
