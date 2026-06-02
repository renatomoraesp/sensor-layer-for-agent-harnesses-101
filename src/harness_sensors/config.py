"""Configuration loading for portable sensor runs."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, Field

from harness_sensors.simple_yaml import load_yaml


class SensorToggle(BaseModel):
    """Per-sensor configuration."""

    enabled: bool = True
    triggers: list[str] = Field(default_factory=list)
    options: dict[str, Any] = Field(default_factory=dict)


class ProviderConfig(BaseModel):
    """Provider adapter configuration."""

    name: Literal["prompt-only", "openai", "anthropic", "local"] = "prompt-only"
    model: str | None = None
    endpoint: str | None = None
    api_key_env: str | None = None
    timeout_seconds: float = 60.0


class TargetRepoConfig(BaseModel):
    """Target repository paths and commands."""

    harness_dir: str = "harness"
    docs_paths: list[str] = Field(default_factory=lambda: ["AGENTS.md", "docs", "harness"])
    test_commands: list[str] = Field(default_factory=list)
    build_commands: list[str] = Field(default_factory=list)
    lint_commands: list[str] = Field(default_factory=list)
    log_paths: list[str] = Field(default_factory=list)
    report_dir: str = ".harness/reports"
    prompt_dir: str = ".harness/prompts"
    evidence_dir: str = ".harness/evidence"


class RuntimeConfig(BaseModel):
    """Complete runtime configuration."""

    sensors: dict[str, SensorToggle] = Field(default_factory=dict)
    provider: ProviderConfig = Field(default_factory=ProviderConfig)
    target: TargetRepoConfig = Field(default_factory=TargetRepoConfig)


def default_config() -> RuntimeConfig:
    """Return conservative prompt-only defaults."""

    return RuntimeConfig()


def load_runtime_config(path: Path | None = None) -> RuntimeConfig:
    """Load a runtime config file, or return defaults when omitted."""

    if path is None:
        return default_config()
    raw = load_yaml(path.read_text(encoding="utf-8"))
    if raw is None:
        return default_config()
    if not isinstance(raw, dict):
        raise ValueError(f"{path} must contain a YAML mapping")
    normalized = _normalize_config(raw)
    return RuntimeConfig.model_validate(normalized)


def _normalize_config(raw: dict[str, Any]) -> dict[str, Any]:
    normalized: dict[str, Any] = {}
    if "sensors" in raw:
        normalized["sensors"] = raw["sensors"]
    if "provider" in raw:
        normalized["provider"] = raw["provider"]
    elif "providers" in raw and isinstance(raw["providers"], dict):
        active = raw["providers"].get("active", "prompt-only")
        provider_data = raw["providers"].get(active, {})
        if isinstance(provider_data, dict):
            normalized["provider"] = {"name": active, **provider_data}
    if "target" in raw:
        normalized["target"] = raw["target"]
    elif "target_repo" in raw:
        normalized["target"] = raw["target_repo"]
    return normalized
