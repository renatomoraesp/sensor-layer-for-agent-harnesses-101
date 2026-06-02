"""Workspace cleanliness and handoff evidence collector."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from harness_sensors.evidence._utils import iter_repo_files, read_text_file, relative_path

TODO_MARKERS = ("TODO", "FIXME", "XXX")
TEMP_SUFFIXES = (".tmp", ".temp", ".bak", ".orig", ".rej")


def collect_workspace_evidence(repo: Path, *, status_short: list[str]) -> dict[str, Any]:
    """Collect TODO markers, temp files, and dirty workspace summary."""

    return {
        "dirty": bool(status_short),
        "status_short": status_short,
        "todo_markers": _find_todo_markers(repo),
        "temporary_files": _find_temporary_files(repo),
    }


def _find_todo_markers(repo: Path) -> list[dict[str, Any]]:
    markers: list[dict[str, Any]] = []
    for path in iter_repo_files(repo):
        if len(markers) >= 80:
            break
        if path.suffix.lower() not in {".py", ".md", ".json", ".yaml", ".yml", ".toml", ".txt"}:
            continue
        payload = read_text_file(path, max_chars=80_000)
        text = payload.get("text")
        if not isinstance(text, str):
            continue
        for line_number, line in enumerate(text.splitlines(), start=1):
            if any(marker in line for marker in TODO_MARKERS):
                markers.append(
                    {
                        "path": relative_path(repo, path),
                        "line": line_number,
                        "text": line.strip()[:300],
                    }
                )
                if len(markers) >= 80:
                    break
    return markers


def _find_temporary_files(repo: Path) -> list[str]:
    temporary: list[str] = []
    for path in iter_repo_files(repo):
        if path.name.endswith(TEMP_SUFFIXES) or path.name.startswith(".tmp"):
            temporary.append(relative_path(repo, path))
        if len(temporary) >= 80:
            break
    return temporary
