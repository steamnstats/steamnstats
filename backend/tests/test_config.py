from app.core.config import Settings


def test_parse_cors_origins_from_comma_separated_string() -> None:
    settings = Settings(
        backend_cors_origins="http://localhost:5173,http://localhost:3000",  # type: ignore[call-arg]
        _env_file=None,  # type: ignore[call-arg]
    )
    assert settings.backend_cors_origins == ["http://localhost:5173", "http://localhost:3000"]


def test_parse_cors_origins_from_list() -> None:
    settings = Settings(
        backend_cors_origins=["http://a.com", "http://b.com"],  # type: ignore[call-arg]
        _env_file=None,  # type: ignore[call-arg]
    )
    assert settings.backend_cors_origins == ["http://a.com", "http://b.com"]


def test_parse_cors_origins_strips_whitespace() -> None:
    settings = Settings(
        backend_cors_origins=" http://a.com , http://b.com ",  # type: ignore[call-arg]
        _env_file=None,  # type: ignore[call-arg]
    )
    assert settings.backend_cors_origins == ["http://a.com", "http://b.com"]


def test_parse_optional_url_empty_string_becomes_none() -> None:
    settings = Settings(
        steam_endpoint_url="",  # type: ignore[call-arg]
        _env_file=None,  # type: ignore[call-arg]
    )
    assert settings.steam_endpoint_url is None


def test_parse_optional_url_valid_url_preserved() -> None:
    settings = Settings(
        steam_endpoint_url="http://localhost:8001",  # type: ignore[call-arg]
        _env_file=None,  # type: ignore[call-arg]
    )
    assert str(settings.steam_endpoint_url) == "http://localhost:8001/"


def test_default_settings_have_sane_values() -> None:
    settings = Settings(_env_file=None)  # type: ignore[call-arg]
    assert settings.project_name == "SteamNStats"
    assert settings.access_token_expire_minutes == 15
    assert settings.refresh_token_expire_days == 30
    assert settings.game_metadata_ttl_hours == 24
    assert settings.steam_openid_verify is True
