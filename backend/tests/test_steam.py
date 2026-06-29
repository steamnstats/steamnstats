import pytest
import respx
from fastapi import HTTPException
from httpx import Response

from app.services.steam import (
    build_steam_login_url,
    extract_steam_id,
    fetch_game_achievement_schema,
    fetch_owned_games,
    fetch_player_achievements,
    fetch_player_summary,
    fetch_store_metadata,
    fetch_store_metadata_batch,
    steam_api_base,
    steam_openid_endpoint,
    steam_store_base,
    verify_openid_response,
)


def test_extract_steam_id_from_claimed_id() -> None:
    steam_id = extract_steam_id("https://steamcommunity.com/openid/id/76561198000000000")
    assert steam_id == "76561198000000000"


def test_extract_steam_id_rejects_none() -> None:
    with pytest.raises(HTTPException) as exc_info:
        extract_steam_id(None)
    assert exc_info.value.status_code == 400


def test_extract_steam_id_rejects_invalid_prefix() -> None:
    with pytest.raises(HTTPException) as exc_info:
        extract_steam_id("https://evil.com/openid/id/76561198000000000")
    assert exc_info.value.status_code == 400


def test_steam_endpoint_url_overrides_login_endpoint(monkeypatch) -> None:
    monkeypatch.setenv("STEAM_ENDPOINT_URL", "http://localhost:8001")

    login_url = build_steam_login_url()

    assert login_url.startswith("http://localhost:8001/openid/login?")


def test_steam_endpoint_url_overrides_api_and_store_base(monkeypatch) -> None:
    monkeypatch.setenv("STEAM_ENDPOINT_URL", "http://localhost:8001")

    assert steam_api_base() == "http://localhost:8001"
    assert steam_store_base() == "http://localhost:8001"
    assert steam_openid_endpoint() == "http://localhost:8001/openid/login"


def test_default_steam_bases(monkeypatch) -> None:
    monkeypatch.setenv("STEAM_ENDPOINT_URL", "")

    assert steam_api_base() == "https://api.steampowered.com"
    assert steam_store_base() == "https://store.steampowered.com/api"
    assert steam_openid_endpoint() == "https://steamcommunity.com/openid/login"


@respx.mock
async def test_fetch_player_summary_without_api_key(monkeypatch) -> None:
    monkeypatch.delenv("STEAM_WEB_API_KEY", raising=False)
    monkeypatch.setenv("STEAM_WEB_API_KEY", "")

    profile = await fetch_player_summary("76561198000000000")

    assert profile.steam_id == "76561198000000000"
    assert profile.persona_name is None
    assert profile.avatar_url is None


@respx.mock
async def test_fetch_player_summary_with_api_key(monkeypatch) -> None:
    monkeypatch.setenv("STEAM_WEB_API_KEY", "test-key")
    url = f"{steam_api_base()}/ISteamUser/GetPlayerSummaries/v0002/"
    respx.get(url).mock(
        return_value=Response(
            200,
            json={
                "response": {
                    "players": [
                        {
                            "personaname": "Tester",
                            "avatarfull": "https://example.com/full.png",
                            "profileurl": "https://steamcommunity.com/id/tester",
                        }
                    ]
                }
            },
        )
    )

    profile = await fetch_player_summary("76561198000000000")

    assert profile.persona_name == "Tester"
    assert profile.avatar_url == "https://example.com/full.png"
    assert profile.profile_url == "https://steamcommunity.com/id/tester"


@respx.mock
async def test_fetch_player_summary_empty_players(monkeypatch) -> None:
    monkeypatch.setenv("STEAM_WEB_API_KEY", "test-key")
    url = f"{steam_api_base()}/ISteamUser/GetPlayerSummaries/v0002/"
    respx.get(url).mock(return_value=Response(200, json={"response": {"players": []}}))

    profile = await fetch_player_summary("76561198000000000")

    assert profile.persona_name is None
    assert profile.avatar_url is None


@respx.mock
async def test_fetch_owned_games_parses_response(monkeypatch) -> None:
    monkeypatch.setenv("STEAM_WEB_API_KEY", "test-key")
    url = f"{steam_api_base()}/IPlayerService/GetOwnedGames/v0001/"
    respx.get(url).mock(
        return_value=Response(
            200,
            json={
                "response": {
                    "games": [
                        {
                            "appid": 10,
                            "name": "CS",
                            "playtime_forever": 500,
                            "playtime_2weeks": 30,
                            "rtime_last_played": 1700000000,
                        },
                        {
                            "appid": 20,
                            "name": "Portal",
                            "playtime_forever": 100,
                            "playtime_2weeks": 0,
                            "rtime_last_played": 0,
                        },
                    ]
                }
            },
        )
    )

    games = await fetch_owned_games("76561198000000000")

    assert len(games) == 2
    assert games[0].app_id == 10
    assert games[0].name == "CS"
    assert games[0].playtime_forever_minutes == 500
    assert games[0].playtime_2weeks_minutes == 30
    assert games[0].last_played_at is not None
    assert games[1].app_id == 20
    assert games[1].last_played_at is None


async def test_fetch_owned_games_without_api_key_raises(monkeypatch) -> None:
    monkeypatch.setenv("STEAM_WEB_API_KEY", "")

    with pytest.raises(HTTPException) as exc_info:
        await fetch_owned_games("76561198000000000")
    assert exc_info.value.status_code == 503


@respx.mock
async def test_fetch_store_metadata_success(monkeypatch) -> None:
    url = f"{steam_store_base()}/appdetails"
    respx.get(url).mock(
        return_value=Response(
            200,
            json={
                "10": {
                    "success": True,
                    "data": {
                        "name": "Counter-Strike",
                        "header_image": "https://example.com/header.jpg",
                        "price_overview": {
                            "final": 999,
                            "initial": 999,
                            "discount_percent": 0,
                            "currency": "USD",
                        },
                        "is_free": False,
                    },
                }
            },
        )
    )

    metadata = await fetch_store_metadata(10)

    assert metadata is not None
    assert metadata.app_id == 10
    assert metadata.name == "Counter-Strike"
    assert metadata.current_price_cents == 999
    assert metadata.is_free is False
    assert metadata.currency == "USD"
    assert metadata.genres == {"english": [], "portuguese": []}


@respx.mock
async def test_fetch_store_metadata_with_genres(monkeypatch) -> None:
    url = f"{steam_store_base()}/appdetails"
    en_data = {
        "10": {
            "success": True,
            "data": {
                "name": "Counter-Strike",
                "is_free": False,
                "genres": [
                    {"id": "1", "description": "Action"},
                    {"id": "37", "description": "Free to Play"},
                ],
            },
        }
    }
    pt_data = {
        "10": {
            "success": True,
            "data": {
                "genres": [
                    {"id": "1", "description": "Ação"},
                    {"id": "37", "description": "Gratuito para Jogar"},
                ],
            },
        }
    }

    def appdetails_handler(request):
        if request.url.params.get("l") == "portuguese":
            return Response(200, json=pt_data)
        return Response(200, json=en_data)

    respx.get(url).mock(side_effect=appdetails_handler)

    metadata = await fetch_store_metadata(10)

    assert metadata is not None
    assert metadata.genres == {
        "english": ["Action", "Free to Play"],
        "portuguese": ["Ação", "Gratuito para Jogar"],
    }


@respx.mock
async def test_fetch_store_metadata_free_game(monkeypatch) -> None:
    url = f"{steam_store_base()}/appdetails"
    respx.get(url).mock(
        return_value=Response(
            200,
            json={
                "20": {
                    "success": True,
                    "data": {
                        "name": "Free Game",
                        "header_image": None,
                        "is_free": True,
                    },
                }
            },
        )
    )

    metadata = await fetch_store_metadata(20)

    assert metadata is not None
    assert metadata.is_free is True
    assert metadata.current_price_cents == 0
    assert metadata.initial_price_cents == 0
    assert metadata.genres == {"english": [], "portuguese": []}


@respx.mock
async def test_fetch_store_metadata_unsuccessful(monkeypatch) -> None:
    url = f"{steam_store_base()}/appdetails"
    respx.get(url).mock(
        return_value=Response(200, json={"10": {"success": False}})
    )

    metadata = await fetch_store_metadata(10)

    assert metadata is None


@respx.mock
async def test_fetch_store_metadata_batch_success(monkeypatch) -> None:
    url = f"{steam_store_base()}/appdetails"

    en_body = {
        "10": {
            "success": True,
            "data": {
                "name": "CS",
                "is_free": False,
                "price_overview": {"final": 999, "initial": 999, "discount_percent": 0, "currency": "USD"},
                "genres": [{"id": "1", "description": "Action"}],
            },
        },
        "20": {
            "success": True,
            "data": {
                "name": "Portal",
                "is_free": True,
            },
        },
        "30": {"success": False},
    }
    pt_body = {
        "10": {
            "success": True,
            "data": {
                "genres": [{"id": "1", "description": "Ação"}],
            },
        },
        "20": {
            "success": True,
            "data": {
                "genres": [{"id": "2", "description": "Estratégia"}],
            },
        },
    }

    def appdetails_handler(request):
        if request.url.params.get("l") == "portuguese":
            return Response(200, json=pt_body)
        return Response(200, json=en_body)

    respx.get(url).mock(side_effect=appdetails_handler)

    results = await fetch_store_metadata_batch([10, 20, 30])

    assert results[10] is not None
    assert results[10].name == "CS"
    assert results[10].genres == {"english": ["Action"], "portuguese": ["Ação"]}
    assert results[20] is not None
    assert results[20].is_free is True
    assert results[20].genres == {"english": [], "portuguese": ["Estratégia"]}
    assert results[30] is None


@respx.mock
async def test_fetch_store_metadata_batch_empty(monkeypatch) -> None:
    results = await fetch_store_metadata_batch([])
    assert results == {}


@respx.mock
async def test_fetch_game_achievement_schema_success(monkeypatch) -> None:
    monkeypatch.setenv("STEAM_WEB_API_KEY", "test-key")
    url = f"{steam_api_base()}/ISteamUserStats/GetSchemaForGame/v2/"
    respx.get(url).mock(
        return_value=Response(
            200,
            json={
                "game": {
                    "gameName": "Test Game",
                    "availableGameStats": {
                        "achievements": [
                            {
                                "name": "ACH_TEST_1",
                                "displayName": "Test Achievement",
                                "description": "Do a thing",
                                "icon": "https://example.com/icon.png",
                                "icongray": "https://example.com/gray.png",
                                "hidden": 0,
                            },
                            {
                                "name": "ACH_HIDDEN",
                                "displayName": "Hidden One",
                                "hidden": 1,
                            },
                        ]
                    },
                }
            },
        )
    )

    schema = await fetch_game_achievement_schema(10)

    assert len(schema) == 2
    assert schema[0].api_name == "ACH_TEST_1"
    assert schema[0].display_name == "Test Achievement"
    assert schema[0].icon_url == "https://example.com/icon.png"
    assert schema[0].hidden is False
    assert schema[1].api_name == "ACH_HIDDEN"
    assert schema[1].hidden is True


@respx.mock
async def test_fetch_game_achievement_schema_empty(monkeypatch) -> None:
    monkeypatch.setenv("STEAM_WEB_API_KEY", "test-key")
    url = f"{steam_api_base()}/ISteamUserStats/GetSchemaForGame/v2/"
    respx.get(url).mock(return_value=Response(200, json={"game": {}}))

    schema = await fetch_game_achievement_schema(10)
    assert schema == []


async def test_fetch_game_achievement_schema_without_api_key_raises(monkeypatch) -> None:
    monkeypatch.setenv("STEAM_WEB_API_KEY", "")
    with pytest.raises(HTTPException) as exc_info:
        await fetch_game_achievement_schema(10)
    assert exc_info.value.status_code == 503


@respx.mock
async def test_fetch_player_achievements_success(monkeypatch) -> None:
    monkeypatch.setenv("STEAM_WEB_API_KEY", "test-key")
    url = f"{steam_api_base()}/ISteamUserStats/GetPlayerAchievements/v1/"
    respx.get(url).mock(
        return_value=Response(
            200,
            json={
                "playerstats": {
                    "steamID": "76561198000000000",
                    "achievements": [
                        {"apiname": "ACH_TEST_1", "achieved": 1, "unlocktime": 1700000000},
                        {"apiname": "ACH_TEST_2", "achieved": 0},
                    ],
                }
            },
        )
    )

    achievements = await fetch_player_achievements("76561198000000000", 10)

    assert len(achievements) == 2
    assert achievements[0].api_name == "ACH_TEST_1"
    assert achievements[0].achieved is True
    assert achievements[0].unlock_time is not None
    assert achievements[1].api_name == "ACH_TEST_2"
    assert achievements[1].achieved is False
    assert achievements[1].unlock_time is None


async def test_fetch_player_achievements_without_api_key_raises(monkeypatch) -> None:
    monkeypatch.setenv("STEAM_WEB_API_KEY", "")
    with pytest.raises(HTTPException) as exc_info:
        await fetch_player_achievements("76561198000000000", 10)
    assert exc_info.value.status_code == 503


async def test_verify_openid_response_skips_verification(monkeypatch) -> None:
    monkeypatch.setenv("STEAM_OPENID_VERIFY", "false")

    class FakeRequest:
        query_params = {"openid.claimed_id": "https://steamcommunity.com/openid/id/76561198000000000"}
        url = type("U", (), {"query": "openid.claimed_id=https://steamcommunity.com/openid/id/76561198000000000"})()

    steam_id = await verify_openid_response(FakeRequest())
    assert steam_id == "76561198000000000"


@respx.mock
async def test_verify_openid_response_valid(monkeypatch) -> None:
    monkeypatch.setenv("STEAM_OPENID_VERIFY", "true")
    endpoint = steam_openid_endpoint()
    respx.post(endpoint).mock(return_value=Response(200, text="is_valid:true\nns:http://specs.openid.net/auth/2.0"))

    class FakeRequest:
        query_params = {"openid.claimed_id": "https://steamcommunity.com/openid/id/76561198000000000"}
        url = type("U", (), {"query": "openid.claimed_id=https://steamcommunity.com/openid/id/76561198000000000&openid.mode=id_res"})()

    steam_id = await verify_openid_response(FakeRequest())
    assert steam_id == "76561198000000000"


@respx.mock
async def test_verify_openid_response_invalid(monkeypatch) -> None:
    monkeypatch.setenv("STEAM_OPENID_VERIFY", "true")
    endpoint = steam_openid_endpoint()
    respx.post(endpoint).mock(return_value=Response(200, text="is_valid:false"))

    class FakeRequest:
        query_params = {"openid.claimed_id": "https://steamcommunity.com/openid/id/76561198000000000"}
        url = type("U", (), {"query": "openid.claimed_id=https://steamcommunity.com/openid/id/76561198000000000&openid.mode=id_res"})()

    with pytest.raises(HTTPException) as exc_info:
        await verify_openid_response(FakeRequest())
    assert exc_info.value.status_code == 401
