"""Harness feature-state collector."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from harness_sensors.evidence._utils import read_text_file

HARNESS_FILES = [
    "feature_list.json",
    "progress.md",
    "decisions.md",
    "sprint_contract.md",
    "quality_score.md",
]


def collect_feature_state(repo: Path, *, harness_dir: str) -> dict[str, Any]:
    """Collect target-repo harness state files."""

    root = repo / harness_dir
    files: dict[str, Any] = {}
    for name in HARNESS_FILES:
        path = root / name
        payload = read_text_file(path, max_chars=14_000)
        if name.endswith(".json") and payload.get("exists"):
            text = payload.get("text", "")
            if isinstance(text, str):
                try:
                    payload["json"] = json.loads(text)
                except json.JSONDecodeError as exc:
                    payload["json_error"] = str(exc)
        files[name] = payload

    feature_json = files.get("feature_list.json", {}).get("json")
    active_feature = _active_feature(feature_json)
    return {
        "harness_dir": str(root),
        "files": files,
        "active_feature": active_feature,
    }


def _active_feature(feature_json: Any) -> Any:
    if not isinstance(feature_json, dict):
        return None
    if "active_feature" in feature_json:
        return feature_json["active_feature"]
    features = feature_json.get("features")
    if not isinstance(features, list):
        return None
    active = [
        feature for feature in features if isinstance(feature, dict) and feature.get("active")
    ]
    if len(active) == 1:
        return active[0]
    return active
