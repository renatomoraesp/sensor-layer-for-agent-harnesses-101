from pathlib import Path

import pytest

from harness_sensors.sensor_card import SensorCardError, discover_sensor_cards, load_sensor_card

ROOT = Path(__file__).resolve().parents[1]


def test_all_canonical_sensor_cards_validate() -> None:
    cards = discover_sensor_cards(ROOT / "sensors")

    assert {card.id for card in cards} == {
        "completion-calibration",
        "feature-wip-boundary",
        "test-adequacy",
        "architecture-drift",
        "runtime-observability",
        "clean-handoff",
        "instruction-ecology",
    }
    assert all(card.metadata.output_schema == "sensor-result.v1" for card in cards)


def test_sensor_card_requires_rubric_and_output_contract(tmp_path: Path) -> None:
    card = tmp_path / "bad.md"
    card.write_text(
        """---
id: bad-card
name: Bad Card
version: 0.1.0
trigger:
  - before_done
sensor_type: inferential_feedback_control
output_schema: sensor-result.v1
evidence:
  required:
    - diff
  optional: []
non_goals: []
---

# Bad Card
""",
        encoding="utf-8",
    )

    with pytest.raises(SensorCardError):
        load_sensor_card(card)
