"""Export sensor cards into Continue-style markdown checks."""

from __future__ import annotations

from pathlib import Path

from harness_sensors.sensor_card import load_sensor_index

DEFAULT_CONTINUE_SENSOR_IDS = [
    "completion-calibration",
    "feature-wip-boundary",
    "test-adequacy",
    "architecture-drift",
]


def export_continue_checks(
    *,
    sensor_dir: Path,
    out_dir: Path,
    sensor_ids: list[str] | None = None,
) -> list[Path]:
    """Export compatible sensor cards to markdown checks."""

    cards = load_sensor_index(sensor_dir)
    selected = sensor_ids or DEFAULT_CONTINUE_SENSOR_IDS
    out_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for sensor_id in selected:
        card = cards[sensor_id]
        path = out_dir / f"{sensor_id}.md"
        path.write_text(
            render_continue_check(sensor_id=card.id, title=card.metadata.name, body=card.body),
            encoding="utf-8",
        )
        written.append(path)
    return written


def render_continue_check(*, sensor_id: str, title: str, body: str) -> str:
    """Render one Continue check file."""

    return f"""# {title}

Use this check as an inferential review rubric for `{sensor_id}`.

{body}

## Continue check instruction

Review only the pull request evidence available to Continue. Return a structured
finding with concrete repair instructions when the evidence does not satisfy
the rubric.
"""
