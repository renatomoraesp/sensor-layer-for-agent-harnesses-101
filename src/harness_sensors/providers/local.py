"""OpenAI-compatible local provider adapter."""

from __future__ import annotations

from typing import Any

from harness_sensors.providers.openai import _post_json, extract_openai_chat_completions_text


class LocalOpenAICompatibleProvider:
    """Adapter for local or self-hosted OpenAI-compatible endpoints."""

    def __init__(
        self,
        *,
        model: str,
        endpoint: str,
        api_key: str = "local",
        timeout_seconds: float = 60.0,
    ) -> None:
        self.model = model
        self.endpoint = endpoint
        self.api_key = api_key
        self.timeout_seconds = timeout_seconds

    def complete(self, prompt: str, *, schema: dict[str, Any] | None = None) -> str:
        """Call a local OpenAI-compatible endpoint and return text output."""

        payload: dict[str, Any] = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
        }
        if schema is not None:
            payload["response_format"] = {
                "type": "json_schema",
                "json_schema": {"name": "sensor_result", "schema": schema},
            }
        return _post_json(
            self.endpoint,
            payload,
            self.api_key,
            self.timeout_seconds,
            extractor=extract_openai_chat_completions_text,
        )
