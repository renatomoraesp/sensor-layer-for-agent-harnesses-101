"""Git evidence collector."""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any, TypedDict


class _GitCommand(TypedDict):
    exit_code: int
    stdout: str
    stderr: str


def collect_git_evidence(repo: Path) -> dict[str, Any]:
    """Collect status, diff, branch, and commit metadata from Git."""

    if _git(repo, "rev-parse", "--is-inside-work-tree")["exit_code"] != 0:
        return {"available": False, "error": "target path is not a Git worktree"}

    status = _git(repo, "status", "--short")
    diff = _git(repo, "diff", "--no-ext-diff", "--")
    staged_diff = _git(repo, "diff", "--cached", "--no-ext-diff", "--")
    branch = _git(repo, "branch", "--show-current")
    commit = _git(repo, "rev-parse", "HEAD")

    status_lines = status["stdout"].splitlines()
    return {
        "available": True,
        "branch": branch["stdout"].strip(),
        "commit": commit["stdout"].strip(),
        "status_short": status_lines,
        "changed_files": _changed_files(status_lines),
        "untracked_files": [line[3:] for line in status_lines if line.startswith("?? ")],
        "diff": diff["stdout"],
        "staged_diff": staged_diff["stdout"],
        "errors": [
            item["stderr"]
            for item in [status, diff, staged_diff, branch, commit]
            if item["exit_code"] != 0 and item["stderr"]
        ],
    }


def _git(repo: Path, *args: str) -> _GitCommand:
    try:
        completed = subprocess.run(
            ["git", *args],
            cwd=repo,
            check=False,
            capture_output=True,
            text=True,
            timeout=20,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"exit_code": 1, "stdout": "", "stderr": str(exc)}
    return {
        "exit_code": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    }


def _changed_files(status_lines: list[str]) -> list[str]:
    changed: list[str] = []
    for line in status_lines:
        if len(line) < 4:
            continue
        path = line[3:]
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        changed.append(path)
    return changed
