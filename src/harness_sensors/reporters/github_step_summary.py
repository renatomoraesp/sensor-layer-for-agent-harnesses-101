"""GitHub Actions step-summary rendering."""

from __future__ import annotations

from collections import Counter

from harness_sensors.models import SensorResult
from harness_sensors.reporters.markdown import render_markdown_report


def render_github_step_summary(results: list[SensorResult]) -> str:
    """Render a concise markdown summary suitable for ``GITHUB_STEP_SUMMARY``."""

    counts = Counter(result.status.value for result in results)
    header = [
        "# Harness Sensors",
        "",
        f"PASS: {counts.get('PASS', 0)} | WARN: {counts.get('WARN', 0)} | "
        f"FAIL: {counts.get('FAIL', 0)} | ERROR: {counts.get('ERROR', 0)}",
        "",
    ]
    return "\n".join(header) + render_markdown_report(results)
