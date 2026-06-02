"""Prompt rendering for inferential sensor runs."""

from __future__ import annotations

import json
from typing import Any

from harness_sensors.evidence.derivations import summarize_evidence_for_sensor
from harness_sensors.models import EvidenceBundle, SensorCard


def render_sensor_prompt(
    card: SensorCard,
    bundle: EvidenceBundle,
    *,
    result_schema: dict[str, Any],
) -> str:
    """Render a provider-neutral prompt for one sensor and evidence bundle."""

    evidence_json = json.dumps(bundle.model_dump(mode="json"), indent=2, sort_keys=True)
    schema_json = json.dumps(result_schema, indent=2, sort_keys=True)
    summary_json = json.dumps(
        summarize_evidence_for_sensor(card, bundle).model_dump(mode="json"),
        indent=2,
        sort_keys=True,
    )
    required = ", ".join(card.metadata.evidence.required) or "none"
    optional = ", ".join(card.metadata.evidence.optional) or "none"

    return f"""You are executing an inferential feedback control for a coding-agent harness.

Sensor id: {card.metadata.id}
Sensor name: {card.metadata.name}
Required evidence: {required}
Optional evidence: {optional}

Use the sensor card below as the authoritative rubric. Judge only the evidence
provided. Do not invent repository facts. If required evidence is missing,
return WARN or FAIL when the missing evidence weakens the claim, or ERROR when
the sensor cannot run.

Return exactly one JSON object that validates against sensor-result.v1. Do not
wrap it in markdown.

## Evidence Availability Summary

```json
{summary_json}
```

## Sensor Card

{card.body}

## Evidence Bundle

```json
{evidence_json}
```

## sensor-result.v1 JSON Schema

```json
{schema_json}
```
"""
