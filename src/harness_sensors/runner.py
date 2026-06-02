"""Offline-first sensor runner."""

from __future__ import annotations

import json
from pathlib import Path

from pydantic import ValidationError

from harness_sensors.config import RuntimeConfig, default_config
from harness_sensors.evidence import collect_evidence
from harness_sensors.models import EvidenceBundle, SensorCard, SensorResult
from harness_sensors.prompt import render_sensor_prompt
from harness_sensors.providers import build_provider
from harness_sensors.providers.base import Provider
from harness_sensors.providers.prompt_only import PromptOnlyProvider
from harness_sensors.reporters import ReportFormat, render_report
from harness_sensors.schema_loader import load_schema
from harness_sensors.sensor_card import default_sensor_dir, load_sensor_index


class SensorRunner:
    """Coordinate card loading, evidence collection, prompting, and reporting."""

    def __init__(
        self,
        *,
        sensor_dir: Path | None = None,
        config: RuntimeConfig | None = None,
        provider: Provider | None = None,
    ) -> None:
        self.sensor_dir = sensor_dir or default_sensor_dir()
        self.config = config or default_config()
        self.cards = load_sensor_index(self.sensor_dir)
        self._provider = provider
        self.result_schema = load_schema("sensor-result.schema.json")

    def collect(self, repo: Path, *, run_checks: bool = False) -> EvidenceBundle:
        """Collect evidence from the target repository."""

        return collect_evidence(repo, self.config, run_checks=run_checks)

    def render_prompt(self, sensor_id: str, bundle: EvidenceBundle) -> str:
        """Render a prompt for one sensor id."""

        card = self.cards[sensor_id]
        return render_sensor_prompt(card, bundle, result_schema=self.result_schema)

    def run_sensor(
        self,
        repo: Path,
        *,
        sensor_id: str,
        bundle: EvidenceBundle | None = None,
        run_checks: bool = False,
    ) -> SensorResult:
        """Run one sensor in the configured provider mode."""

        card = self.cards[sensor_id]
        evidence_bundle = bundle or self.collect(repo, run_checks=run_checks)
        prompt = render_sensor_prompt(card, evidence_bundle, result_schema=self.result_schema)
        provider = self._provider or self._build_provider(repo)
        if isinstance(provider, PromptOnlyProvider):
            prompt_path = provider.write_prompt(card.id, prompt)
            return SensorResult.prompt_only(card.id, prompt_path)

        try:
            raw = provider.complete(prompt, schema=self.result_schema)
        except Exception as exc:
            return SensorResult.error(
                card.id, "Provider failed while executing sensor.", detail=str(exc)
            )
        return self._parse_provider_result(card, raw)

    def run_many(
        self,
        repo: Path,
        *,
        sensor_ids: list[str],
        run_checks: bool = False,
    ) -> tuple[EvidenceBundle, list[SensorResult]]:
        """Collect evidence once and run several sensors against it."""

        bundle = self.collect(repo, run_checks=run_checks)
        results = [
            self.run_sensor(repo, sensor_id=sensor_id, bundle=bundle, run_checks=run_checks)
            for sensor_id in sensor_ids
        ]
        return bundle, results

    def enabled_sensor_ids(self) -> list[str]:
        """Return enabled sensors.

        Core sensors run by default. Maturity and experimental sensors require
        explicit enabling in config.
        """

        if not self.config.sensors:
            return [card.id for card in self.cards.values() if card.metadata.maturity == "core"]
        enabled: list[str] = []
        for sensor_id, card in self.cards.items():
            toggle = self.config.sensors.get(sensor_id)
            if toggle is None:
                if card.metadata.maturity == "core":
                    enabled.append(card.id)
            elif toggle.enabled:
                enabled.append(card.id)
        return enabled

    def write_report(
        self,
        results: list[SensorResult],
        *,
        output_path: Path,
        output_format: ReportFormat,
        bundle: EvidenceBundle | None = None,
    ) -> Path:
        """Write a rendered report to disk."""

        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            render_report(results, output_format=output_format, bundle=bundle),
            encoding="utf-8",
        )
        return output_path

    def _build_provider(self, repo: Path) -> Provider:
        prompt_dir = repo / self.config.target.prompt_dir
        return build_provider(self.config.provider, prompt_dir=prompt_dir)

    def _parse_provider_result(self, card: SensorCard, raw: str) -> SensorResult:
        try:
            decoded = json.loads(_extract_json_object(raw))
        except json.JSONDecodeError as exc:
            return SensorResult.error(
                card.id,
                "Provider output was not valid JSON.",
                detail=f"{exc}: {raw[:500]}",
            )
        if isinstance(decoded, dict) and "sensor_id" not in decoded:
            decoded["sensor_id"] = card.id
        try:
            result = SensorResult.model_validate(decoded)
        except ValidationError as exc:
            return SensorResult.error(
                card.id, "Provider JSON did not match sensor-result.v1.", detail=str(exc)
            )
        if result.sensor_id != card.id:
            return SensorResult.error(
                card.id,
                "Provider returned a result for a different sensor id.",
                detail=f"expected {card.id}, got {result.sensor_id}",
            )
        return result


def _extract_json_object(text: str) -> str:
    stripped = text.strip()
    if stripped.startswith("{") and stripped.endswith("}"):
        return stripped
    start = stripped.find("{")
    end = stripped.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return stripped
    return stripped[start : end + 1]
