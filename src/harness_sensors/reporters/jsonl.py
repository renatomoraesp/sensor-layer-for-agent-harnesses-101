"""JSONL report rendering."""

from __future__ import annotations

import json

from harness_sensors.models import SensorResult


def render_jsonl_report(results: list[SensorResult]) -> str:
    """Render one structured sensor result per line."""

    return (
        "\n".join(json.dumps(result.model_dump(mode="json"), sort_keys=True) for result in results)
        + "\n"
    )
