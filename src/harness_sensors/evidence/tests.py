"""Test, build, and lint evidence collector."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from harness_sensors.evidence._utils import run_command


def collect_test_evidence(
    repo: Path,
    *,
    test_commands: list[str],
    build_commands: list[str],
    lint_commands: list[str],
    run_commands: bool,
) -> dict[str, Any]:
    """Collect configured command evidence without forcing execution by default."""

    return {
        "test_commands": _collect_commands(repo, test_commands, run_commands=run_commands),
        "build_commands": _collect_commands(repo, build_commands, run_commands=run_commands),
        "lint_commands": _collect_commands(repo, lint_commands, run_commands=run_commands),
        "commands_were_run": run_commands,
    }


def _collect_commands(
    repo: Path, commands: list[str], *, run_commands: bool
) -> list[dict[str, Any]]:
    if not commands:
        return []
    if not run_commands:
        return [
            {
                "command": command,
                "status": "not_run",
                "exit_code": None,
                "stdout": "",
                "stderr": "",
                "duration_seconds": None,
            }
            for command in commands
        ]
    return [run_command(command, repo).model_dump(mode="json") for command in commands]
