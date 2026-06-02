"""Report rendering facade."""

from __future__ import annotations

from typing import Literal

from harness_sensors.models import EvidenceBundle, SensorResult
from harness_sensors.reporters.agent_repair import render_agent_repair_block
from harness_sensors.reporters.github_step_summary import render_github_step_summary
from harness_sensors.reporters.jsonl import render_jsonl_report
from harness_sensors.reporters.markdown import render_markdown_report

ReportFormat = Literal["markdown", "jsonl", "github", "agent"]


def render_report(
    results: list[SensorResult],
    *,
    output_format: ReportFormat,
    bundle: EvidenceBundle | None = None,
) -> str:
    """Render results in the requested format."""

    if output_format == "markdown":
        return render_markdown_report(results, bundle=bundle)
    if output_format == "jsonl":
        return render_jsonl_report(results)
    if output_format == "github":
        return render_github_step_summary(results)
    if output_format == "agent":
        return render_agent_repair_block(results)
    raise ValueError(f"unknown report format: {output_format}")
