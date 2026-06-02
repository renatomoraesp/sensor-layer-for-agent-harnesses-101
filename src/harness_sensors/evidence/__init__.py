"""Evidence collection facade."""

from __future__ import annotations

from pathlib import Path

from harness_sensors.config import RuntimeConfig
from harness_sensors.evidence.derivations import (
    derive_diff_summary,
    derive_evidence_availability,
    derive_task_evidence,
)
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
    feature_state = collect_feature_state(repo, harness_dir=config.target.harness_dir)
    docs = collect_docs_evidence(
        repo,
        docs_paths=[*config.target.docs_paths, *config.target.architecture_doc_paths],
        changed_files=[str(path) for path in changed_files],
    )
    runtime = collect_runtime_evidence(
        repo,
        log_paths=config.target.log_paths,
        runtime_commands=config.target.runtime_commands,
        health_check_commands=config.target.health_check_commands,
        e2e_commands=config.target.e2e_commands,
        run_commands=run_checks,
    )

    bundle = EvidenceBundle(
        repo_path=str(repo),
        task=derive_task_evidence(feature_state),
        git=git_evidence,
        diff_summary=derive_diff_summary(git_evidence),
        test_results=collect_test_evidence(
            repo,
            test_commands=config.target.test_commands,
            build_commands=config.target.build_commands,
            lint_commands=config.target.lint_commands,
            run_commands=run_checks,
        ),
        docs=docs,
        feature_state=feature_state,
        runtime=runtime,
        workspace=collect_workspace_evidence(
            repo, status_short=[str(line) for line in status_short]
        ),
    )
    bundle.evidence_availability = derive_evidence_availability(bundle)
    return bundle
