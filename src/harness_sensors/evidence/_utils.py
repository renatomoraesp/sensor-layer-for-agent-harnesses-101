"""Shared evidence collector utilities."""

from __future__ import annotations

import os
import subprocess
import time
from pathlib import Path

from harness_sensors.models import CommandEvidence

SKIPPED_DIRS = {
    ".git",
    ".harness",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "htmlcov",
    "node_modules",
    "venv",
}


def run_command(command: str, repo: Path, *, timeout_seconds: float = 120.0) -> CommandEvidence:
    """Run a configured shell command and capture bounded evidence."""

    started = time.monotonic()
    try:
        completed = subprocess.run(
            command,
            cwd=repo,
            shell=True,
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return CommandEvidence(
            command=command,
            status="error",
            stderr=str(exc),
            duration_seconds=round(time.monotonic() - started, 3),
        )

    return CommandEvidence(
        command=command,
        status="passed" if completed.returncode == 0 else "failed",
        exit_code=completed.returncode,
        stdout=_truncate(completed.stdout),
        stderr=_truncate(completed.stderr),
        duration_seconds=round(time.monotonic() - started, 3),
    )


def read_text_file(path: Path, *, max_chars: int = 12_000) -> dict[str, str | int | bool]:
    """Read a text file with a bounded payload."""

    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return {"path": str(path), "exists": True, "text": "", "error": "not utf-8 text"}
    except OSError as exc:
        return {"path": str(path), "exists": False, "text": "", "error": str(exc)}

    truncated = len(text) > max_chars
    return {
        "path": str(path),
        "exists": True,
        "text": text[:max_chars],
        "truncated": truncated,
        "size": len(text),
    }


def iter_repo_files(repo: Path) -> list[Path]:
    """Return normal files under a repository, skipping generated folders."""

    files: list[Path] = []
    for root, dirs, names in os.walk(repo):
        dirs[:] = [directory for directory in dirs if directory not in SKIPPED_DIRS]
        root_path = Path(root)
        for name in names:
            files.append(root_path / name)
    return files


def relative_path(repo: Path, path: Path) -> str:
    """Return a stable repo-relative path string."""

    try:
        return path.relative_to(repo).as_posix()
    except ValueError:
        return path.as_posix()


def _truncate(text: str, *, max_chars: int = 16_000) -> str:
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "\n...[truncated]..."
