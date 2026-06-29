from app.core.config import Settings


def test_default_settings() -> None:
    settings = Settings()
    assert settings.project_name == "SteamNStats"
    assert settings.environment == "development"
    assert settings.access_token_expire_minutes == 15
    assert settings.refresh_token_expire_days == 30
    assert settings.game_metadata_ttl_hours == 24


def test_parse_cors_origins_from_string() -> None:
    settings = Settings(backend_cors_origins="http://a.com, http://b.com")
    assert settings.backend_cors_origins == ["http://a.com", "http://b.com"]


def test_parse_cors_origins_from_list() -> None:
    origins = ["http://a.com", "http://b.com"]
    settings = Settings(backend_cors_origins=origins)
    assert settings.backend_cors_origins == origins


def test_parse_cors_origins_empty_string_filtered() -> None:
    settings = Settings(backend_cors_origins="http://a.com, , http://b.com")
    assert settings.backend_cors_origins == ["http://a.com", "http://b.com"]


def test_parse_optional_url_empty_string_becomes_none() -> None:
    settings = Settings(steam_endpoint_url="")
    assert settings.steam_endpoint_url is None


def test_parse_optional_url_value_preserved() -> None:
    settings = Settings(steam_endpoint_url="http://localhost:8001")
    assert str(settings.steam_endpoint_url).rstrip("/") == "http://localhost:8001"
