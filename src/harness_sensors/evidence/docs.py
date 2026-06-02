"""Documentation evidence collector."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from harness_sensors.evidence._utils import read_text_file, relative_path


def collect_docs_evidence(
    repo: Path,
    *,
    docs_paths: list[str],
    changed_files: list[str],
) -> dict[str, Any]:
    """Collect AGENTS, docs, harness docs, and local docs near changed files."""

    configured_docs = [_read_doc_path(repo, path) for path in docs_paths]
    local_docs = _collect_local_docs(repo, changed_files)
    return {
        "configured_paths": docs_paths,
        "documents": configured_docs,
        "module_local_docs": local_docs,
    }


def _read_doc_path(repo: Path, configured_path: str) -> dict[str, Any]:
    path = repo / configured_path
    if path.is_file():
        return read_text_file(path)
    if path.is_dir():
        docs: list[dict[str, Any]] = []
        for child in sorted(path.rglob("*.md"))[:20]:
            docs.append(read_text_file(child, max_chars=8_000))
        return {"path": str(path), "exists": True, "documents": docs}
    return {"path": str(path), "exists": False, "documents": []}


def _collect_local_docs(repo: Path, changed_files: list[str]) -> list[dict[str, Any]]:
    docs: list[dict[str, Any]] = []
    seen: set[Path] = set()
    for changed in changed_files[:30]:
        current = (repo / changed).parent
        for candidate_name in ["README.md", "AGENTS.md"]:
            candidate = current / candidate_name
            if candidate.exists() and candidate not in seen:
                seen.add(candidate)
                payload = read_text_file(candidate, max_chars=6_000)
                payload["relative_path"] = relative_path(repo, candidate)
                docs.append(payload)
    return docs
