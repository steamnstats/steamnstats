import httpx
import pytest
import respx
from fastapi import HTTPException

from app.services.steam import (
    extract_steam_id,
    fetch_owned_games,
    fetch_player_summary,
    fetch_store_metadata,
    steam_api_base,
    steam_openid_endpoint,
    steam_store_base,
    verify_openid_response,
)


@pytest.fixture(autouse=True)
def _set_steam_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("STEAM_WEB_API_KEY", "test-api-key")


def test_extract_steam_id_invalid_url_raises() -> None:
    with pytest.raises(HTTPException) as exc_info:
        extract_steam_id("https://example.com/not-steam")
    assert exc_info.value.status_code == 400


def test_extract_steam_id_none_raises() -> None:
    with pytest.raises(HTTPException) as exc_info:
        extract_steam_id(None)
    assert exc_info.value.status_code == 400


def test_steam_openid_endpoint_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("STEAM_ENDPOINT_URL", raising=False)
    monkeypatch.setenv("STEAM_ENDPOINT_URL", "")
    endpoint = steam_openid_endpoint()
    assert endpoint == "https://steamcommunity.com/openid/login"


def test_steam_openid_endpoint_custom(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("STEAM_ENDPOINT_URL", "http://localhost:8001")
    endpoint = steam_openid_endpoint()
    assert endpoint == "http://localhost:8001/openid/login"


def test_steam_api_base_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("STEAM_ENDPOINT_URL", "")
    assert steam_api_base() == "https://api.steampowered.com"


def test_steam_api_base_custom(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("STEAM_ENDPOINT_URL", "http://localhost:8001")
    assert steam_api_base() == "http://localhost:8001"


def test_steam_store_base_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("STEAM_ENDPOINT_URL", "")
    assert steam_store_base() == "https://store.steampowered.com/api"


def test_steam_store_base_custom(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("STEAM_ENDPOINT_URL", "http://localhost:8001")
    assert steam_store_base() == "http://localhost:8001"


@respx.mock
async def test_fetch_player_summary_success(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("STEAM_ENDPOINT_URL", "")
    respx.get("https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/").mock(
        return_value=httpx.Response(
            200,
            json={
                "response": {
                    "players": [
                        {
                            "steamid": "76561198000000001",
                            "personaname": "TestPlayer",
                            "avatarfull": "https://cdn.example.com/avatar.jpg",
                            "profileurl": "https://steamcommunity.com/id/test/",
                        }
                    ]
                }
            },
        )
    )

    profile = await fetch_player_summary("76561198000000001")
    assert profile.steam_id == "76561198000000001"
    assert profile.persona_name == "TestPlayer"
    assert profile.avatar_url == "https://cdn.example.com/avatar.jpg"
    assert profile.profile_url == "https://steamcommunity.com/id/test/"


@respx.mock
async def test_fetch_player_summary_no_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("STEAM_WEB_API_KEY", "")
    profile = await fetch_player_summary("76561198000000001")
    assert profile.steam_id == "76561198000000001"
    assert profile.persona_name is None


@respx.mock
async def test_fetch_owned_games_success(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("STEAM_ENDPOINT_URL", "")
    respx.get("https://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/").mock(
        return_value=httpx.Response(
            200,
            json={
                "response": {
                    "games": [
                        {
                            "appid": 730,
                            "name": "Counter-Strike 2",
                            "playtime_forever": 5000,
                            "playtime_2weeks": 120,
                            "rtime_last_played": 1700000000,
                        },
                        {
                            "appid": 570,
                            "name": "Dota 2",
                            "playtime_forever": 10000,
                            "playtime_2weeks": 0,
                        },
                    ]
                }
            },
        )
    )

    games = await fetch_owned_games("76561198000000001")
    assert len(games) == 2
    assert games[0].app_id == 730
    assert games[0].name == "Counter-Strike 2"
    assert games[0].playtime_forever_minutes == 5000
    assert games[0].playtime_2weeks_minutes == 120
    assert games[0].last_played_at is not None
    assert games[1].app_id == 570
    assert games[1].last_played_at is None


@respx.mock
async def test_fetch_owned_games_no_api_key_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("STEAM_WEB_API_KEY", "")
    with pytest.raises(HTTPException) as exc_info:
        await fetch_owned_games("76561198000000001")
    assert exc_info.value.status_code == 503


@respx.mock
async def test_fetch_store_metadata_success(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("STEAM_ENDPOINT_URL", "")
    respx.get("https://store.steampowered.com/api/appdetails").mock(
        return_value=httpx.Response(
            200,
            json={
                "730": {
                    "success": True,
                    "data": {
                        "name": "Counter-Strike 2",
                        "header_image": "https://cdn.example.com/header.jpg",
                        "is_free": False,
                        "price_overview": {
                            "final": 0,
                            "initial": 1499,
                            "discount_percent": 100,
                            "currency": "USD",
                        },
                    },
                }
            },
        )
    )

    metadata = await fetch_store_metadata(730)
    assert metadata is not None
    assert metadata.app_id == 730
    assert metadata.name == "Counter-Strike 2"
    assert metadata.current_price_cents == 0
    assert metadata.initial_price_cents == 1499
    assert metadata.discount_percent == 100
    assert metadata.currency == "USD"
    assert metadata.is_free is False


@respx.mock
async def test_fetch_store_metadata_free_game(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("STEAM_ENDPOINT_URL", "")
    respx.get("https://store.steampowered.com/api/appdetails").mock(
        return_value=httpx.Response(
            200,
            json={
                "570": {
                    "success": True,
                    "data": {
                        "name": "Dota 2",
                        "header_image": "https://cdn.example.com/dota.jpg",
                        "is_free": True,
                    },
                }
            },
        )
    )

    metadata = await fetch_store_metadata(570)
    assert metadata is not None
    assert metadata.is_free is True
    assert metadata.current_price_cents == 0


@respx.mock
async def test_fetch_store_metadata_not_found(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("STEAM_ENDPOINT_URL", "")
    respx.get("https://store.steampowered.com/api/appdetails").mock(
        return_value=httpx.Response(
            200,
            json={"99999": {"success": False}},
        )
    )

    metadata = await fetch_store_metadata(99999)
    assert metadata is None


@respx.mock
async def test_verify_openid_response_without_verification(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("STEAM_OPENID_VERIFY", "false")

    class FakeRequest:
        query_params = {
            "openid.claimed_id": "https://steamcommunity.com/openid/id/76561198000000001",
            "openid.mode": "id_res",
        }

        class url:
            query = "openid.claimed_id=https://steamcommunity.com/openid/id/76561198000000001&openid.mode=id_res"

    steam_id = await verify_openid_response(FakeRequest())  # type: ignore[arg-type]
    assert steam_id == "76561198000000001"
