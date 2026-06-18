from claim_pilot_core.core.config import BaseSettings, create_settings, get_settings, reload_settings


def test_default_settings():
    reload_settings(BaseSettings)
    s = get_settings()
    assert s.app_name == "claim-pilot"
    assert s.environment == "development"
    assert s.aws_region == "us-east-1"


def test_create_settings():
    class MySettings(BaseSettings):
        custom_field: str = "hello"

    settings = create_settings(MySettings)
    assert settings.custom_field == "hello"
    assert settings.app_name == "claim-pilot"
    reload_settings(BaseSettings)
