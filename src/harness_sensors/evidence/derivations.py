"""Derived evidence that makes broad collector output sensor-aware."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from harness_sensors.models import (
    DiffSummary,
    EvidenceAvailability,
    EvidenceBundle,
    SensorCard,
    SensorEvidenceSummary,
    TaskEvidence,
)


def derive_task_evidence(feature_state: dict[str, Any]) -> TaskEvidence | None:
    """Derive active-task evidence from feature list and sprint contract files."""

    files = feature_state.get("files")
    if not isinstance(files, dict):
        return None
    feature_payload = files.get("feature_list.json")
    if not isinstance(feature_payload, dict):
        return None
    feature_json = feature_payload.get("json")
    if not isinstance(feature_json, dict):
        return None

    active_id = feature_json.get("active_feature")
    active_feature = _find_active_feature(feature_json, active_id)
    sprint_contract = _file_text(files.get("sprint_contract.md"))
    if not isinstance(active_feature, dict):
        return TaskEvidence(
            source="harness/feature_list.json",
            active_feature_id=str(active_id) if active_id is not None else None,
            sprint_contract=sprint_contract,
        )

    return TaskEvidence(
        source="harness/feature_list.json",
        active_feature_id=_optional_str(active_feature.get("id")),
        title=_optional_str(active_feature.get("title")),
        status=_optional_str(active_feature.get("status")),
        acceptance_criteria=_string_list(active_feature.get("acceptance_criteria")),
        verification=_list(active_feature.get("verification")),
        completion_claim=_optional_str(active_feature.get("completion_claim")),
        notes=_optional_str(active_feature.get("notes")),
        sprint_contract=sprint_contract,
    )


def derive_diff_summary(git: dict[str, Any]) -> DiffSummary:
    """Classify changed files into buckets that sensor cards ask for."""

    changed_files = [str(item) for item in _list(git.get("changed_files"))]
    changed_tests: list[str] = []
    changed_docs: list[str] = []
    changed_harness_state: list[str] = []
    changed_production_code: list[str] = []

    for file_path in changed_files:
        path = Path(file_path)
        parts = set(path.parts)
        suffix = path.suffix.lower()
        if "tests" in parts or path.name.startswith("test_") or path.name.endswith("_test.py"):
            changed_tests.append(file_path)
        elif "harness" in parts or file_path.startswith(".harness/"):
            changed_harness_state.append(file_path)
        elif suffix in {".md", ".rst", ".txt", ".adoc"} or "docs" in parts:
            changed_docs.append(file_path)
        else:
            changed_production_code.append(file_path)

    return DiffSummary(
        changed_files=changed_files,
        changed_tests=changed_tests,
        changed_production_code=changed_production_code,
        changed_docs=changed_docs,
        changed_harness_state=changed_harness_state,
    )


def derive_evidence_availability(bundle: EvidenceBundle) -> dict[str, EvidenceAvailability]:
    """Build a normalized availability map used by all sensor prompts."""

    availability: dict[str, EvidenceAvailability] = {
        "task": "present" if bundle.task else "missing",
        "active_feature": "present" if bundle.task and bundle.task.active_feature_id else "missing",
        "feature_list": _file_availability(bundle.feature_state, "feature_list.json"),
        "feature_state": "present" if bundle.feature_state else "missing",
        "progress": _file_availability(bundle.feature_state, "progress.md"),
        "decisions": _file_availability(bundle.feature_state, "decisions.md"),
        "sprint_contract": _file_availability(bundle.feature_state, "sprint_contract.md"),
        "quality_score": _file_availability(bundle.feature_state, "quality_score.md"),
        "diff": "present" if bundle.git.get("diff") or bundle.git.get("staged_diff") else "missing",
        "changed_files": "present" if bundle.diff_summary.changed_files else "missing",
        "changed_tests": "present" if bundle.diff_summary.changed_tests else "missing",
        "changed_production_code": (
            "present" if bundle.diff_summary.changed_production_code else "missing"
        ),
        "changed_docs": "present" if bundle.diff_summary.changed_docs else "missing",
        "changed_harness_state": (
            "present" if bundle.diff_summary.changed_harness_state else "missing"
        ),
        "test_results": _command_group_availability(bundle.test_results, "test_commands"),
        "build_results": _command_group_availability(bundle.test_results, "build_commands"),
        "lint_results": _command_group_availability(bundle.test_results, "lint_commands"),
        "runtime_logs": "present" if bundle.runtime.get("available") is True else "missing",
        "runtime_commands": _command_group_availability(bundle.runtime, "runtime_commands"),
        "health_checks": _command_group_availability(bundle.runtime, "health_check_commands"),
        "e2e_transcript": _runtime_signal_availability(bundle.runtime),
        "architecture_docs": _architecture_docs_availability(bundle.docs),
        "module_docs": "present" if bundle.docs.get("module_local_docs") else "missing",
        "workspace_state": "present" if bundle.workspace else "missing",
        "git_status": "present" if bundle.git.get("status_short") is not None else "missing",
        "todo_markers": "present" if bundle.workspace.get("todo_markers") else "missing",
        "untracked_artifacts": (
            "present"
            if bundle.git.get("untracked_files") or bundle.workspace.get("temporary_files")
            else "missing"
        ),
    }
    return availability


def summarize_evidence_for_sensor(
    card: SensorCard, bundle: EvidenceBundle
) -> SensorEvidenceSummary:
    """Summarize required and optional evidence availability for a card."""

    availability = bundle.evidence_availability or derive_evidence_availability(bundle)
    required = {
        name: _lookup_availability(name, availability) for name in card.metadata.evidence.required
    }
    optional = {
        name: _lookup_availability(name, availability) for name in card.metadata.evidence.optional
    }
    return SensorEvidenceSummary(
        sensor_id=card.id,
        required=required,
        optional=optional,
        notes=_summary_notes(required, optional),
    )


def _find_active_feature(feature_json: dict[str, Any], active_id: Any) -> dict[str, Any] | None:
    features = feature_json.get("features")
    if not isinstance(features, list):
        return None
    if active_id is not None:
        for feature in features:
            if isinstance(feature, dict) and str(feature.get("id")) == str(active_id):
                return feature
    active_features = [
        feature for feature in features if isinstance(feature, dict) and feature.get("active")
    ]
    if len(active_features) == 1:
        return active_features[0]
    return None


def _file_text(payload: Any) -> str | None:
    if isinstance(payload, dict) and isinstance(payload.get("text"), str):
        return str(payload["text"])
    return None


def _optional_str(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, str):
        return value
    return str(value)


def _string_list(value: Any) -> list[str]:
    return [str(item) for item in _list(value)]


def _list(value: Any) -> list[Any]:
    if isinstance(value, list):
        return value
    return []


def _file_availability(feature_state: dict[str, Any], filename: str) -> EvidenceAvailability:
    files = feature_state.get("files")
    if not isinstance(files, dict):
        return "missing"
    payload = files.get(filename)
    if isinstance(payload, dict) and payload.get("exists") is True:
        return "present"
    return "missing"


def _command_group_availability(container: dict[str, Any], key: str) -> EvidenceAvailability:
    commands = container.get(key)
    if not isinstance(commands, list) or not commands:
        return "not_configured"
    statuses = {item.get("status") for item in commands if isinstance(item, dict)}
    if not statuses:
        return "missing"
    if statuses == {"not_run"}:
        return "present_not_run"
    if "passed" in statuses or "failed" in statuses or "error" in statuses:
        return "present"
    return "partial"


def _runtime_signal_availability(runtime: dict[str, Any]) -> EvidenceAvailability:
    if runtime.get("available") is True:
        return "present"
    if runtime.get("configured"):
        return "configured_missing"
    return "missing"


def _architecture_docs_availability(docs: dict[str, Any]) -> EvidenceAvailability:
    documents = docs.get("documents")
    if not isinstance(documents, list):
        return "missing"
    existing = [
        item
        for item in documents
        if isinstance(item, dict)
        and (item.get("exists") is True or _any_doc_exists(item.get("documents")))
    ]
    if not existing:
        return "missing"
    if any("architecture" in str(item.get("path", "")).lower() for item in existing):
        return "present"
    return "partial"


def _any_doc_exists(value: Any) -> bool:
    return isinstance(value, list) and any(
        isinstance(item, dict) and item.get("exists") is True for item in value
    )


def _lookup_availability(
    evidence_name: str, availability: dict[str, EvidenceAvailability]
) -> EvidenceAvailability:
    aliases = {
        "diff": "diff",
        "changed_tests": "changed_tests",
        "changed_production_code": "changed_production_code",
        "changed_files": "changed_files",
        "feature_state": "feature_state",
        "feature_list": "feature_list",
        "active_feature": "active_feature",
        "progress": "progress",
        "decisions": "decisions",
        "test_results": "test_results",
        "coverage_output": "test_results",
        "runtime_logs": "runtime_logs",
        "runtime_transcript": "e2e_transcript",
        "e2e_transcript": "e2e_transcript",
        "command_output": "runtime_commands",
        "expected_runtime_behavior": "task",
        "architecture_docs": "architecture_docs",
        "module_docs": "module_docs",
        "neighboring_patterns": "changed_files",
        "git_status": "git_status",
        "workspace_state": "workspace_state",
        "todo_markers": "todo_markers",
        "untracked_artifacts": "untracked_artifacts",
        "agents_md": "architecture_docs",
        "harness_docs": "feature_state",
        "changed_documentation": "changed_docs",
        "recent_sensor_failures": "quality_score",
        "last_failure": "progress",
        "sprint_contract": "sprint_contract",
        "acceptance_criteria": "task",
        "completion_claim": "task",
    }
    return availability.get(aliases.get(evidence_name, evidence_name), "missing")


def _summary_notes(
    required: dict[str, EvidenceAvailability],
    optional: dict[str, EvidenceAvailability],
) -> list[str]:
    notes: list[str] = []
    weak_required = [
        name
        for name, status in required.items()
        if status in {"missing", "configured_missing", "not_configured", "present_not_run"}
    ]
    if weak_required:
        notes.append(
            "Required evidence needs attention: "
            + ", ".join(f"{name}={required[name]}" for name in weak_required)
        )
    missing_optional = [name for name, status in optional.items() if status == "missing"]
    if missing_optional:
        notes.append("Optional evidence is absent: " + ", ".join(missing_optional))
    if not notes:
        notes.append("Required evidence appears present in the bundle.")
    return notes
