import json
from pathlib import Path

from harness_sensors.models import EvidenceBundle, SensorResult

ROOT = Path(__file__).resolve().parents[1]
CASES = [
    "premature-completion",
    "scope-creep",
    "weak-tests",
    "architecture-drift",
    "runtime-signal-missing",
    "dirty-handoff",
]


def test_seeded_eval_cases_have_evidence_and_expected_results() -> None:
    for case in CASES:
        evidence_path = ROOT / "evals" / "cases" / case / "evidence.json"
        expected_path = ROOT / "evals" / "expected" / f"{case}.json"

        evidence = EvidenceBundle.model_validate(json.loads(evidence_path.read_text()))
        expected = SensorResult.model_validate(json.loads(expected_path.read_text()))

        assert evidence.schema_version == "evidence-bundle.v1"
        assert expected.status == "FAIL"
