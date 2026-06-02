import shutil
from pathlib import Path
from typing import Any

from harness_sensors.models import SensorStatus
from harness_sensors.runner import SensorRunner

ROOT = Path(__file__).resolve().parents[1]


def test_prompt_only_runner_writes_prompt_and_warn_result(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    shutil.copytree(ROOT / "tests" / "fixtures" / "sample_repo", repo)
    runner = SensorRunner(sensor_dir=ROOT / "sensors")

    result = runner.run_sensor(repo, sensor_id="completion-calibration")

    assert result.status == "WARN"
    prompt_path = Path(result.metadata["prompt_path"])
    assert prompt_path.exists()
    assert "Completion Calibration Sensor" in prompt_path.read_text(encoding="utf-8")


def test_run_all_defaults_to_core_sensors_only() -> None:
    runner = SensorRunner(sensor_dir=ROOT / "sensors")

    assert "instruction-ecology" not in runner.enabled_sensor_ids()


def test_render_prompt_includes_schema_and_evidence(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    shutil.copytree(ROOT / "tests" / "fixtures" / "sample_repo", repo)
    runner = SensorRunner(sensor_dir=ROOT / "sensors")
    bundle = runner.collect(repo)

    prompt = runner.render_prompt("test-adequacy", bundle)

    assert "Test Adequacy and Behavior Sensor" in prompt
    assert "sensor-result.v1 JSON Schema" in prompt
    assert '"schema_version": "evidence-bundle.v1"' in prompt


def test_runner_accepts_mock_provider_result(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    shutil.copytree(ROOT / "tests" / "fixtures" / "sample_repo", repo)
    runner = SensorRunner(sensor_dir=ROOT / "sensors", provider=_PassingProvider())

    result = runner.run_sensor(repo, sensor_id="test-adequacy")

    assert result.status is SensorStatus.PASS
    assert result.sensor_id == "test-adequacy"


def test_runner_turns_provider_failure_into_error_result(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    shutil.copytree(ROOT / "tests" / "fixtures" / "sample_repo", repo)
    runner = SensorRunner(sensor_dir=ROOT / "sensors", provider=_FailingProvider())

    result = runner.run_sensor(repo, sensor_id="test-adequacy")

    assert result.status is SensorStatus.ERROR
    assert "Provider failed" in result.summary


class _PassingProvider:
    def complete(self, prompt: str, *, schema: dict[str, Any] | None = None) -> str:
        return """{
  "schema_version": "sensor-result.v1",
  "sensor_id": "test-adequacy",
  "status": "PASS",
  "confidence": 0.8,
  "summary": "Mock provider accepted the evidence.",
  "findings": [],
  "missing_evidence": [],
  "next_actions": []
}"""


class _FailingProvider:
    def complete(self, prompt: str, *, schema: dict[str, Any] | None = None) -> str:
        raise RuntimeError("mock provider unavailable")
