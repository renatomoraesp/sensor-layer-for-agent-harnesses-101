"""Provider interface for model-backed sensor judgments."""

from __future__ import annotations

from typing import Any, Protocol


class Provider(Protocol):
    """Small replaceable model provider boundary."""

    def complete(self, prompt: str, *, schema: dict[str, Any] | None = None) -> str:
        """Return raw provider text for a rendered prompt."""
