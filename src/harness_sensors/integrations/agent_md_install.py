"""Target-repository template installation."""

from __future__ import annotations

import shutil
from pathlib import Path


def default_template_dir() -> Path:
    """Return the bundled target-repo template directory for a source checkout."""

    package_path = Path(__file__).resolve()
    candidates = [
        Path.cwd() / "templates" / "target-repo",
        package_path.parents[3] / "templates" / "target-repo",
        package_path.parents[2] / "templates" / "target-repo",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return candidates[1]


def install_target_template(
    repo: Path, *, template_dir: Path | None = None, force: bool = False
) -> list[Path]:
    """Copy the minimal harness template into a target repository."""

    source = template_dir or default_template_dir()
    if not source.exists():
        raise FileNotFoundError(f"template directory not found: {source}")
    written: list[Path] = []
    for path in sorted(source.rglob("*")):
        if path.is_dir():
            continue
        relative = path.relative_to(source)
        destination = repo / relative
        if destination.exists() and not force:
            continue
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, destination)
        written.append(destination)
    return written
