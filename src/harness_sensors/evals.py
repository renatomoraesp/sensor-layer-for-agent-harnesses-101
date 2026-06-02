"""Executable offline eval-case validation."""

from __future__ import annotations

import json
from pathlib import Path

from pydantic import BaseModel, Field

from harness_sensors.models import EvidenceBundle, SensorCard, SensorResult
from harness_sensors.prompt import render_sensor_prompt
from harness_sensors.schema_loader import load_schema
from harness_sensors.sensor_card import default_sensor_dir, load_sensor_index


class EvalCaseReport(BaseModel):
    """Structural validation report for one eval case."""

    case: str
    sensor_id: str
    expected_status: str
    ok: bool
    checks: dict[str, bool] = Field(default_factory=dict)
    issues: list[str] = Field(default_factory=list)
    prompt_preview: str | None = None


def default_evals_dir() -> Path:
    """Return the bundled evals directory for source checkouts or wheels."""

    package_path = Path(__file__).resolve()
    candidates = [
        Path.cwd() / "evals",
        package_path.parents[2] / "evals",
        package_path.parents[1] / "evals",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return candidates[1]


def discover_eval_cases(evals_dir: Path | None = None) -> list[str]:
    """Discover eval case names with evidence and expected result files."""

    root = evals_dir or default_evals_dir()
    cases_dir = root / "cases"
    expected_dir = root / "expected"
    cases: list[str] = []
    for evidence_path in sorted(cases_dir.glob("*/evidence.json")):
        case_name = evidence_path.parent.name
        if (expected_dir / f"{case_name}.json").exists():
            cases.append(case_name)
    return cases


def run_eval_case(
    case_name: str,
    *,
    evals_dir: Path | None = None,
    sensor_dir: Path | None = None,
) -> EvalCaseReport:
    """Validate one eval case structurally and render its prompt."""

    root = evals_dir or default_evals_dir()
    evidence_path = root / "cases" / case_name / "evidence.json"
    expected_path = root / "expected" / f"{case_name}.json"
    bundle = EvidenceBundle.model_validate(json.loads(evidence_path.read_text(encoding="utf-8")))
    expected = SensorResult.model_validate(json.loads(expected_path.read_text(encoding="utf-8")))
    cards = load_sensor_index(sensor_dir or default_sensor_dir())
    card = cards[expected.sensor_id]
    prompt = render_sensor_prompt(
        card,
        bundle,
        result_schema=load_schema("sensor-result.schema.json"),
    )
    checks = _structural_checks(expected, card, prompt)
    issues = [name for name, passed in checks.items() if not passed]
    return EvalCaseReport(
        case=case_name,
        sensor_id=expected.sensor_id,
        expected_status=expected.status.value,
        ok=not issues,
        checks=checks,
        issues=issues,
        prompt_preview=prompt[:500],
    )


def run_eval_cases(
    *,
    case_names: list[str] | None = None,
    evals_dir: Path | None = None,
    sensor_dir: Path | None = None,
) -> list[EvalCaseReport]:
    """Run several eval cases."""

    selected = case_names or discover_eval_cases(evals_dir)
    return [
        run_eval_case(case_name, evals_dir=evals_dir, sensor_dir=sensor_dir)
        for case_name in selected
    ]


def render_eval_report(reports: list[EvalCaseReport], *, as_json: bool = False) -> str:
    """Render eval reports for CLI output."""

    if as_json:
        return json.dumps([report.model_dump(mode="json") for report in reports], indent=2)
    lines = ["# Harness Sensor Evals", ""]
    for report in reports:
        status = "PASS" if report.ok else "FAIL"
        lines.extend(
            [
                f"## {report.case}",
                "",
                f"- Result: `{status}`",
                f"- Sensor: `{report.sensor_id}`",
                f"- Expected status: `{report.expected_status}`",
            ]
        )
        if report.issues:
            lines.append("- Issues: " + ", ".join(report.issues))
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _structural_checks(expected: SensorResult, card: SensorCard, prompt: str) -> dict[str, bool]:
    return {
        "expected_sensor_matches_card": expected.sensor_id == card.id,
        "expected_has_summary": bool(expected.summary.strip()),
        "expected_has_action_or_pass": bool(expected.next_actions)
        or expected.status.value == "PASS",
        "expected_findings_fit_status": bool(expected.findings)
        or expected.status.value in {"PASS", "WARN"},
        "prompt_rendered_sensor_card": card.metadata.name in prompt,
        "prompt_includes_evidence_summary": "Evidence Availability Summary" in prompt,
        "prompt_includes_result_schema": "sensor-result.v1 JSON Schema" in prompt,
    }
