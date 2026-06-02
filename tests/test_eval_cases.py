import json
from collections import defaultdict
from pathlib import Path

from harness_sensors.evals import discover_eval_cases, run_eval_cases
from harness_sensors.models import EvidenceBundle, SensorResult

ROOT = Path(__file__).resolve().parents[1]


def test_seeded_eval_cases_have_evidence_and_expected_results() -> None:
    cases = discover_eval_cases(ROOT / "evals")
    assert len(cases) >= 12

    statuses_by_sensor: dict[str, set[str]] = defaultdict(set)
    for case in cases:
        evidence_path = ROOT / "evals" / "cases" / case / "evidence.json"
        expected_path = ROOT / "evals" / "expected" / f"{case}.json"

        evidence = EvidenceBundle.model_validate(json.loads(evidence_path.read_text()))
        expected = SensorResult.model_validate(json.loads(expected_path.read_text()))

        assert evidence.schema_version == "evidence-bundle.v1"
        statuses_by_sensor[expected.sensor_id].add(expected.status.value)

    for sensor_id in [
        "completion-calibration",
        "feature-wip-boundary",
        "test-adequacy",
        "architecture-drift",
        "runtime-observability",
        "clean-handoff",
    ]:
        assert "FAIL" in statuses_by_sensor[sensor_id]
        assert statuses_by_sensor[sensor_id] & {"PASS", "WARN"}


def test_eval_cases_render_structural_reports() -> None:
    reports = run_eval_cases(evals_dir=ROOT / "evals", sensor_dir=ROOT / "sensors")

    assert reports
    assert all(report.ok for report in reports)
