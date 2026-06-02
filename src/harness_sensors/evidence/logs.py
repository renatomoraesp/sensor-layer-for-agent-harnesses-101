"""Runtime logs and transcript collector."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from harness_sensors.evidence._utils import read_text_file


def collect_runtime_evidence(repo: Path, *, log_paths: list[str]) -> dict[str, Any]:
    """Collect configured runtime log, trace, or transcript files."""

    logs: list[dict[str, Any]] = []
    for configured_path in log_paths:
        path = repo / configured_path
        if path.is_dir():
            for child in sorted(path.iterdir())[:20]:
                if child.is_file():
                    logs.append(read_text_file(child, max_chars=10_000))
        else:
            logs.append(read_text_file(path, max_chars=16_000))
    return {
        "configured_log_paths": log_paths,
        "logs": logs,
        "available": bool(logs),
    }
