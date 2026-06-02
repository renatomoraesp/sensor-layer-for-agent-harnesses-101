"""Prompt-only provider."""

from __future__ import annotations

from pathlib import Path
from typing import Any


class PromptOnlyProvider:
    """Provider that writes prompts to disk instead of calling a model."""

    def __init__(self, output_dir: Path) -> None:
        self.output_dir = output_dir

    def complete(self, prompt: str, *, schema: dict[str, Any] | None = None) -> str:
        """Return the prompt text unchanged for protocol compatibility."""

        return prompt

    def write_prompt(self, sensor_id: str, prompt: str) -> Path:
        """Write a rendered prompt and return its path."""

        self.output_dir.mkdir(parents=True, exist_ok=True)
        path = self.output_dir / f"{sensor_id}.prompt.md"
        path.write_text(prompt, encoding="utf-8")
        return path
