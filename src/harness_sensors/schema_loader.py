"""Schema helpers."""

from __future__ import annotations

import json
from importlib import resources
from typing import Any


def load_schema(name: str) -> dict[str, Any]:
    """Load a bundled JSON schema by filename."""

    schema_path = resources.files("harness_sensors.schemas").joinpath(name)
    with schema_path.open("r", encoding="utf-8") as handle:
        raw = json.load(handle)
    if not isinstance(raw, dict):
        raise ValueError(f"{name} did not contain a JSON object")
    return raw
