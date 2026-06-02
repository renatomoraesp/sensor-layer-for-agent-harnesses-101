import json

from harness_sensors.models import (
    EvidenceReference,
    SensorFinding,
    SensorResult,
    SensorStatus,
    Severity,
)
from harness_sensors.reporters import render_report


def _result() -> SensorResult:
    return SensorResult(
        sensor_id="test-adequacy",
        status=SensorStatus.FAIL,
        confidence=0.8,
        summary="Tests do not prove the behavior.",
        findings=[
            SensorFinding(
                severity=Severity.BLOCKER,
                claim="No behavior-level test exists.",
                evidence=[
                    EvidenceReference(
                        path="tests/test_example.py", lines="1-5", detail="Only imports."
                    )
                ],
                repair="Add a behavior-level test.",
            )
        ],
        missing_evidence=["No runtime transcript."],
        next_actions=["Add tests.", "Re-run sensor."],
    )


def test_markdown_report_contains_findings() -> None:
    report = render_report([_result()], output_format="markdown")

    assert "# Harness Sensor Report" in report
    assert "No behavior-level test exists" in report
    assert "No runtime transcript" in report


def test_jsonl_report_is_structured() -> None:
    report = render_report([_result()], output_format="jsonl")
    decoded = json.loads(report)

    assert decoded["sensor_id"] == "test-adequacy"
    assert decoded["status"] == "FAIL"
