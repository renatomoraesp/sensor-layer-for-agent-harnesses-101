import json
from pathlib import Path

from harness_sensors.providers.anthropic import extract_anthropic_messages_text
from harness_sensors.providers.openai import (
    extract_openai_chat_completions_text,
    extract_openai_responses_text,
)

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures" / "provider_responses"


def test_extract_openai_responses_text() -> None:
    raw = json.loads((FIXTURES / "openai_responses.json").read_text(encoding="utf-8"))

    extracted = extract_openai_responses_text(raw)

    assert json.loads(extracted)["sensor_id"] == "test-adequacy"


def test_extract_anthropic_messages_text() -> None:
    raw = json.loads((FIXTURES / "anthropic_messages.json").read_text(encoding="utf-8"))

    extracted = extract_anthropic_messages_text(raw)

    assert json.loads(extracted)["status"] == "PASS"


def test_extract_openai_chat_completions_text() -> None:
    raw = json.loads((FIXTURES / "openai_chat_completions.json").read_text(encoding="utf-8"))

    extracted = extract_openai_chat_completions_text(raw)

    assert json.loads(extracted)["summary"] == "ok"
