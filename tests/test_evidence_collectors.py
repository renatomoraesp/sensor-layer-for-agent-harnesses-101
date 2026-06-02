import os
import shutil
import subprocess
from pathlib import Path

from harness_sensors.config import RuntimeConfig, TargetRepoConfig
from harness_sensors.evidence import collect_evidence

ROOT = Path(__file__).resolve().parents[1]


def test_collect_evidence_from_fixture_repo(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    shutil.copytree(ROOT / "tests" / "fixtures" / "sample_repo", repo)
    subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "add", "."], cwd=repo, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "initial"],
        cwd=repo,
        check=True,
        capture_output=True,
        env={
            **os.environ,
            "GIT_AUTHOR_NAME": "Test",
            "GIT_AUTHOR_EMAIL": "test@example.com",
            "GIT_COMMITTER_NAME": "Test",
            "GIT_COMMITTER_EMAIL": "test@example.com",
        },
    )
    (repo / "src" / "sample.py").write_text(
        "def greet(name: str) -> str:\n    return name\n", encoding="utf-8"
    )

    config = RuntimeConfig(
        target=TargetRepoConfig(
            docs_paths=["AGENTS.md", "docs", "harness"],
            test_commands=["python -m pytest"],
            lint_commands=["ruff check ."],
        )
    )

    bundle = collect_evidence(repo, config, run_checks=False)

    assert bundle.git["available"] is True
    assert "src/sample.py" in bundle.git["changed_files"]
    assert bundle.test_results["commands_were_run"] is False
    assert bundle.feature_state["active_feature"] == "F001"
    assert bundle.task is not None
    assert bundle.task.active_feature_id == "F001"
    assert "src/sample.py" in bundle.diff_summary.changed_production_code
    assert bundle.evidence_availability["changed_production_code"] == "present"
    assert bundle.workspace["dirty"] is True
    assert bundle.docs["documents"]


def test_missing_configured_runtime_logs_are_not_available(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    shutil.copytree(ROOT / "tests" / "fixtures" / "sample_repo", repo)
    config = RuntimeConfig(target=TargetRepoConfig(log_paths=[".harness/logs"]))

    bundle = collect_evidence(repo, config, run_checks=False)

    assert bundle.runtime["configured"] is True
    assert bundle.runtime["available"] is False
    assert bundle.runtime["missing_logs"] == [".harness/logs"]
