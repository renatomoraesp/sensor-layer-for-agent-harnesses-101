"""Markdown report rendering."""

from __future__ import annotations

from harness_sensors.models import EvidenceBundle, SensorResult


def render_markdown_report(
    results: list[SensorResult],
    *,
    bundle: EvidenceBundle | None = None,
) -> str:
    """Render sensor results as human-readable markdown."""

    lines = ["# Harness Sensor Report", ""]
    if bundle is not None:
        lines.extend(
            [
                f"- Repository: `{bundle.repo_path}`",
                f"- Collected at: `{bundle.collected_at.isoformat()}`",
                "",
            ]
        )
    for result in results:
        lines.extend(
            [
                f"## {result.sensor_id}",
                "",
                f"- Status: `{result.status}`",
                f"- Confidence: `{result.confidence:.2f}`",
                f"- Summary: {result.summary}",
                "",
            ]
        )
        if result.findings:
            lines.extend(["### Findings", ""])
            for finding in result.findings:
                lines.append(f"- **{finding.severity}**: {finding.claim}")
                for evidence in finding.evidence:
                    location = evidence.path or "evidence bundle"
                    if evidence.lines:
                        location = f"{location}:{evidence.lines}"
                    lines.append(f"  - Evidence: `{location}` - {evidence.detail}")
                lines.append(f"  - Repair: {finding.repair}")
            lines.append("")
        if result.missing_evidence:
            lines.extend(["### Missing Evidence", ""])
            lines.extend(f"- {item}" for item in result.missing_evidence)
            lines.append("")
        if result.next_actions:
            lines.extend(["### Next Actions", ""])
            lines.extend(f"- {item}" for item in result.next_actions)
            lines.append("")
    return "\n".join(lines).rstrip() + "\n"
