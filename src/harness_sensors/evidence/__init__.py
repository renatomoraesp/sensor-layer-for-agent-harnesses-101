"""Evidence collection facade."""

from __future__ import annotations

from pathlib import Path

from harness_sensors.config import RuntimeConfig
from harness_sensors.evidence.docs import collect_docs_evidence
from harness_sensors.evidence.feature_state import collect_feature_state
from harness_sensors.evidence.git import collect_git_evidence
from harness_sensors.evidence.logs import collect_runtime_evidence
from harness_sensors.evidence.tests import collect_test_evidence
from harness_sensors.evidence.workspace import collect_workspace_evidence
from harness_sensors.models import EvidenceBundle


def collect_evidence(
    repo: Path, config: RuntimeConfig, *, run_checks: bool = False
) -> EvidenceBundle:
    """Collect a full evidence bundle from a target repository."""

    repo = repo.resolve()
    git_evidence = collect_git_evidence(repo)
    changed_files = git_evidence.get("changed_files", [])
    if not isinstance(changed_files, list):
        changed_files = []
    status_short = git_evidence.get("status_short", [])
    if not isinstance(status_short, list):
        status_short = []

    return EvidenceBundle(
        repo_path=str(repo),
        git=git_evidence,
        test_results=collect_test_evidence(
            repo,
            test_commands=config.target.test_commands,
            build_commands=config.target.build_commands,
            lint_commands=config.target.lint_commands,
            run_commands=run_checks,
        ),
        docs=collect_docs_evidence(
            repo,
            docs_paths=config.target.docs_paths,
            changed_files=[str(path) for path in changed_files],
        ),
        feature_state=collect_feature_state(repo, harness_dir=config.target.harness_dir),
        runtime=collect_runtime_evidence(repo, log_paths=config.target.log_paths),
        workspace=collect_workspace_evidence(
            repo, status_short=[str(line) for line in status_short]
        ),
    )
