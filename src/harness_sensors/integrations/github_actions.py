"""GitHub Actions integration helpers."""

from __future__ import annotations

from pathlib import Path


def default_workflow_path(repo: Path) -> Path:
    """Return the expected target workflow path."""

    return repo / ".github" / "workflows" / "harness-sensors.yml"
