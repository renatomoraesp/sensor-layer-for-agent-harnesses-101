"""Runtime logs and transcript collector."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from harness_sensors.evidence._utils import read_text_file, run_command


def collect_runtime_evidence(
    repo: Path,
    *,
    log_paths: list[str],
    runtime_commands: list[str],
    health_check_commands: list[str],
    e2e_commands: list[str],
    run_commands: bool,
) -> dict[str, Any]:
    """Collect configured runtime log, trace, or transcript files."""

    logs: list[dict[str, Any]] = []
    missing_logs: list[str] = []
    for configured_path in log_paths:
        path = repo / configured_path
        if path.is_dir():
            saw_file = False
            for child in sorted(path.iterdir())[:20]:
                if child.is_file():
                    saw_file = True
                    logs.append(read_text_file(child, max_chars=10_000))
            if not saw_file:
                missing_logs.append(configured_path)
        else:
            payload = read_text_file(path, max_chars=16_000)
            if payload.get("exists") is True:
                logs.append(payload)
            else:
                missing_logs.append(configured_path)
    return {
        "configured_log_paths": log_paths,
        "configured": bool(log_paths),
        "existing_logs": [item for item in logs if item.get("exists") is True],
        "missing_logs": missing_logs,
        "logs": logs,
        "available": any(item.get("exists") is True for item in logs),
        "runtime_commands": _collect_runtime_commands(
            repo, runtime_commands, run_commands=run_commands
        ),
        "health_check_commands": _collect_runtime_commands(
            repo, health_check_commands, run_commands=run_commands
        ),
        "e2e_commands": _collect_runtime_commands(repo, e2e_commands, run_commands=run_commands),
    }


def _collect_runtime_commands(
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
