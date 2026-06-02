"""Agent-oriented repair block rendering."""

from __future__ import annotations

from harness_sensors.models import SensorResult


def render_agent_repair_block(results: list[SensorResult]) -> str:
    """Render compact repair instructions for pasting into a coding agent."""

    lines = ["# Sensor Repair Block", ""]
    for result in results:
        lines.extend([f"## {result.sensor_id}: {result.status}", result.summary, ""])
        for action in result.next_actions:
            lines.append(f"- {action}")
        if result.missing_evidence:
            lines.append("")
            lines.append("Missing evidence:")
            lines.extend(f"- {item}" for item in result.missing_evidence)
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"
