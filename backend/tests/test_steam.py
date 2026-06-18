from app.services.steam import build_steam_login_url, extract_steam_id


def test_extract_steam_id_from_claimed_id() -> None:
    steam_id = extract_steam_id("https://steamcommunity.com/openid/id/76561198000000000")
    assert steam_id == "76561198000000000"


def test_steam_endpoint_url_overrides_login_endpoint(monkeypatch) -> None:
    monkeypatch.setenv("STEAM_ENDPOINT_URL", "http://localhost:8001")

    login_url = build_steam_login_url()

    assert login_url.startswith("http://localhost:8001/openid/login?")
