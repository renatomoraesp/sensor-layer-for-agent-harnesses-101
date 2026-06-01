from pydantic_settings import SettingsConfigDict
from pytest import MonkeyPatch

from sensor_layer_for_agent_harnesses_101.settings import Settings


class EnvlessSettings(Settings):
    model_config = SettingsConfigDict(env_prefix="SENSOR_LAYER_", extra="ignore")


def test_settings_defaults_to_development() -> None:
    settings = EnvlessSettings()

    assert settings.environment == "development"
    assert settings.log_level == "INFO"


def test_settings_reads_sensor_layer_env_vars(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setenv("SENSOR_LAYER_ENV", "test")
    monkeypatch.setenv("SENSOR_LAYER_LOG_LEVEL", "DEBUG")

    settings = EnvlessSettings()

    assert settings.environment == "test"
    assert settings.log_level == "DEBUG"
