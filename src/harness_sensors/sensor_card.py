"""Sensor-card discovery, parsing, and validation."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from pydantic import ValidationError

from harness_sensors.models import SensorCard, SensorCardMetadata
from harness_sensors.simple_yaml import load_yaml


class SensorCardError(ValueError):
    """Raised when a sensor card cannot be parsed or validated."""


def default_sensor_dir() -> Path:
    """Return the canonical sensor-card directory for a source checkout."""

    package_path = Path(__file__).resolve()
    candidates = [
        Path.cwd() / "sensors",
        package_path.parents[2] / "sensors",
        package_path.parents[1] / "sensors",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return candidates[1]


def load_sensor_card(path: Path) -> SensorCard:
    """Load and validate one markdown sensor card."""

    text = path.read_text(encoding="utf-8")
    frontmatter, body = _split_frontmatter(text, path)
    raw_metadata = load_yaml(frontmatter)
    if not isinstance(raw_metadata, dict):
        raise SensorCardError(f"{path} frontmatter must be a mapping")
    try:
        metadata = SensorCardMetadata.model_validate(raw_metadata)
    except ValidationError as exc:
        raise SensorCardError(f"{path} has invalid frontmatter: {exc}") from exc
    if "## Judgment rubric" not in body:
        raise SensorCardError(f"{path} must include a '## Judgment rubric' section")
    if "## Output contract" not in body:
        raise SensorCardError(f"{path} must include a '## Output contract' section")
    return SensorCard(metadata=metadata, body=body.strip(), source_path=path)


def discover_sensor_cards(sensor_dir: Path | None = None) -> list[SensorCard]:
    """Discover all canonical sensor cards from a directory."""

    root = sensor_dir or default_sensor_dir()
    cards: list[SensorCard] = []
    for path in sorted(root.glob("*.md")):
        if path.name == "README.md":
            continue
        cards.append(load_sensor_card(path))
    return cards


def load_sensor_index(sensor_dir: Path | None = None) -> dict[str, SensorCard]:
    """Return discovered cards keyed by sensor id."""

    cards = discover_sensor_cards(sensor_dir)
    index: dict[str, SensorCard] = {}
    for card in cards:
        if card.id in index:
            raise SensorCardError(f"duplicate sensor id: {card.id}")
        index[card.id] = card
    return index


def _split_frontmatter(text: str, path: Path) -> tuple[str, str]:
    if not text.startswith("---\n"):
        raise SensorCardError(f"{path} must start with YAML frontmatter")
    parts = text.split("\n---\n", 1)
    if len(parts) != 2:
        raise SensorCardError(f"{path} frontmatter is not closed")
    return parts[0].removeprefix("---\n"), parts[1]


def metadata_to_json_schema() -> dict[str, Any]:
    """Return the current JSON schema for sensor-card frontmatter."""

    return SensorCardMetadata.model_json_schema()
