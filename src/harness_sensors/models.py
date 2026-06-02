"""Typed models shared by the sensor runtime."""

from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


def utc_now() -> datetime:
    """Return a timezone-aware UTC timestamp."""

    return datetime.now(UTC)


class SensorStatus(StrEnum):
    """Allowed sensor verdicts."""

    PASS = "PASS"
    WARN = "WARN"
    FAIL = "FAIL"
    ERROR = "ERROR"


class Severity(StrEnum):
    """Allowed finding severity levels."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    BLOCKER = "blocker"


class EvidenceRequirement(BaseModel):
    """Evidence names required or accepted by a sensor card."""

    model_config = ConfigDict(extra="forbid")

    required: list[str] = Field(default_factory=list)
    optional: list[str] = Field(default_factory=list)


class SensorCardMetadata(BaseModel):
    """Validated YAML frontmatter for a sensor card."""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(pattern=r"^[a-z0-9][a-z0-9-]*$")
    name: str
    version: str
    trigger: list[str] = Field(min_length=1)
    sensor_type: Literal["inferential_feedback_control"]
    output_schema: Literal["sensor-result.v1"]
    evidence: EvidenceRequirement
    non_goals: list[str] = Field(default_factory=list)
    maturity: Literal["core", "maturity", "experimental"] = "core"

    @field_validator("trigger", "non_goals")
    @classmethod
    def no_blank_items(cls, value: list[str]) -> list[str]:
        """Reject empty frontmatter list entries."""

        if any(not item.strip() for item in value):
            raise ValueError("list entries must be non-empty strings")
        return value


class SensorCard(BaseModel):
    """A markdown sensor card plus its validated metadata."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    metadata: SensorCardMetadata
    body: str
    source_path: Path

    @property
    def id(self) -> str:
        """Return the stable sensor id."""

        return self.metadata.id


class EvidenceReference(BaseModel):
    """Pointer to evidence used by a finding."""

    path: str | None = None
    lines: str | None = None
    detail: str


class SensorFinding(BaseModel):
    """One structured observation emitted by a sensor."""

    severity: Severity
    claim: str
    evidence: list[EvidenceReference] = Field(default_factory=list)
    repair: str


class SensorResult(BaseModel):
    """Common result shape for every sensor."""

    model_config = ConfigDict(extra="forbid")

    schema_version: Literal["sensor-result.v1"] = "sensor-result.v1"
    sensor_id: str
    status: SensorStatus
    confidence: float = Field(ge=0.0, le=1.0)
    summary: str
    findings: list[SensorFinding] = Field(default_factory=list)
    missing_evidence: list[str] = Field(default_factory=list)
    next_actions: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def error(cls, sensor_id: str, summary: str, *, detail: str | None = None) -> SensorResult:
        """Build an ERROR result for runtime failures."""

        missing = [detail] if detail else []
        return cls(
            sensor_id=sensor_id,
            status=SensorStatus.ERROR,
            confidence=1.0,
            summary=summary,
            missing_evidence=missing,
            next_actions=["Fix the runtime/configuration issue, then re-run the sensor."],
        )

    @classmethod
    def prompt_only(cls, sensor_id: str, prompt_path: Path) -> SensorResult:
        """Build the intentional prompt-only placeholder result."""

        return cls(
            sensor_id=sensor_id,
            status=SensorStatus.WARN,
            confidence=1.0,
            summary="Prompt-only mode rendered the sensor prompt; no model judgment was invoked.",
            findings=[
                SensorFinding(
                    severity=Severity.WARNING,
                    claim="The sensor has not produced an inferential verdict yet.",
                    evidence=[
                        EvidenceReference(
                            path=str(prompt_path),
                            detail="Rendered prompt ready for a human or external model.",
                        )
                    ],
                    repair=(
                        "Paste the prompt into a capable model, validate the JSON result, "
                        "or configure a provider adapter."
                    ),
                )
            ],
            missing_evidence=["Provider judgment was intentionally skipped in prompt-only mode."],
            next_actions=[
                f"Review or submit the rendered prompt at {prompt_path}.",
                "Record the resulting structured sensor verdict before claiming completion.",
            ],
            metadata={"prompt_path": str(prompt_path)},
        )


class CommandEvidence(BaseModel):
    """Captured command execution evidence."""

    command: str
    status: Literal["passed", "failed", "not_run", "error"]
    exit_code: int | None = None
    stdout: str = ""
    stderr: str = ""
    duration_seconds: float | None = None


class EvidenceBundle(BaseModel):
    """Serializable evidence object passed to sensor prompts."""

    schema_version: Literal["evidence-bundle.v1"] = "evidence-bundle.v1"
    repo_path: str
    collected_at: datetime = Field(default_factory=utc_now)
    task: str | None = None
    git: dict[str, Any] = Field(default_factory=dict)
    test_results: dict[str, Any] = Field(default_factory=dict)
    docs: dict[str, Any] = Field(default_factory=dict)
    feature_state: dict[str, Any] = Field(default_factory=dict)
    runtime: dict[str, Any] = Field(default_factory=dict)
    workspace: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)
