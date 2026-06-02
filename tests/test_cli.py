import json
import shutil
from pathlib import Path

from pytest import CaptureFixture

from harness_sensors.cli import main

ROOT = Path(__file__).resolve().parents[1]


def test_doctor_non_strict_allows_missing_harness_files(tmp_path: Path) -> None:
    assert main(["doctor", "--repo", str(tmp_path)]) == 0


def test_doctor_strict_json_reports_missing_harness_files(
    tmp_path: Path, capsys: CaptureFixture[str]
) -> None:
    exit_code = main(["doctor", "--repo", str(tmp_path), "--strict", "--json"])

    captured = capsys.readouterr()
    report = json.loads(captured.out)
    assert exit_code == 1
    assert report["ok"] is False
    assert report["issues"]


def test_collect_render_run_install_and_export_continue(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    shutil.copytree(ROOT / "tests" / "fixtures" / "sample_repo", repo)

    evidence_path = tmp_path / "evidence.json"
    prompt_path = tmp_path / "prompt.md"
    report_path = tmp_path / "report.md"

    assert main(["collect", "--repo", str(repo), "--out", str(evidence_path)]) == 0
    assert evidence_path.exists()

    assert (
        main(
            [
                "render",
                "--repo",
                str(repo),
                "--sensor",
                "completion-calibration",
                "--out",
                str(prompt_path),
            ]
        )
        == 0
    )
    assert "Evidence Availability Summary" in prompt_path.read_text(encoding="utf-8")

    assert (
        main(
            [
                "run",
                "--repo",
                str(repo),
                "--sensor",
                "completion-calibration",
                "--out",
                str(report_path),
            ]
        )
        == 0
    )
    assert "Prompt-only mode" in report_path.read_text(encoding="utf-8")

    install_repo = tmp_path / "install-target"
    assert main(["install", "--repo", str(install_repo), "--profile", "minimal"]) == 0
    assert (install_repo / "harness" / "feature_list.json").exists()

    export_repo = tmp_path / "export-target"
    assert main(["export", "continue", "--repo", str(export_repo)]) == 0
    assert (export_repo / ".continue" / "checks" / "test-adequacy.md").exists()


def test_eval_cli_runs_all_cases(tmp_path: Path) -> None:
    out = tmp_path / "evals.json"

    exit_code = main(["eval", "--all", "--json", "--out", str(out)])

    assert exit_code == 0
    reports = json.loads(out.read_text(encoding="utf-8"))
    assert reports
    assert all(report["ok"] for report in reports)
