"""Provider factory."""

from __future__ import annotations

from pathlib import Path

from harness_sensors.config import ProviderConfig
from harness_sensors.providers.anthropic import AnthropicProvider
from harness_sensors.providers.base import Provider
from harness_sensors.providers.local import LocalOpenAICompatibleProvider
from harness_sensors.providers.openai import OpenAIProvider
from harness_sensors.providers.prompt_only import PromptOnlyProvider


def build_provider(config: ProviderConfig, *, prompt_dir: Path) -> Provider:
    """Create the configured provider adapter."""

    if config.name == "prompt-only":
        return PromptOnlyProvider(prompt_dir)
    if config.name == "openai":
        if config.model is None:
            raise ValueError("openai provider requires a model")
        return OpenAIProvider(
            model=config.model,
            api_key_env=config.api_key_env or "OPENAI_API_KEY",
            endpoint=config.endpoint or "https://api.openai.com/v1/responses",
            timeout_seconds=config.timeout_seconds,
        )
    if config.name == "anthropic":
        if config.model is None:
            raise ValueError("anthropic provider requires a model")
        return AnthropicProvider(
            model=config.model,
            api_key_env=config.api_key_env or "ANTHROPIC_API_KEY",
            endpoint=config.endpoint or "https://api.anthropic.com/v1/messages",
            timeout_seconds=config.timeout_seconds,
        )
    if config.name == "local":
        if config.model is None or config.endpoint is None:
            raise ValueError("local provider requires model and endpoint")
        return LocalOpenAICompatibleProvider(
            model=config.model,
            endpoint=config.endpoint,
            timeout_seconds=config.timeout_seconds,
        )
    raise ValueError(f"unsupported provider: {config.name}")
