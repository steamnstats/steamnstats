from dataclasses import dataclass
from datetime import UTC, datetime
from urllib.parse import parse_qsl, urlencode

import httpx
from fastapi import HTTPException, Request, status

from app.core.config import get_settings

STEAM_OPENID_ENDPOINT = "https://steamcommunity.com/openid/login"
STEAM_API_BASE = "https://api.steampowered.com"
STEAM_STORE_BASE = "https://store.steampowered.com/api"
type QueryParams = dict[str, str | int | float | bool | None]


@dataclass(frozen=True)
class SteamProfile:
    steam_id: str
    persona_name: str | None
    avatar_url: str | None
    profile_url: str | None


@dataclass(frozen=True)
class OwnedGame:
    app_id: int
    name: str
    playtime_forever_minutes: int
    playtime_2weeks_minutes: int
    last_played_at: datetime | None


GENRE_LANGUAGES = ("english", "portuguese")


@dataclass(frozen=True)
class StoreMetadata:
    app_id: int
    name: str
    header_image: str | None
    current_price_cents: int | None
    initial_price_cents: int | None
    discount_percent: int | None
    currency: str | None
    is_free: bool
    genres: dict[str, list[str]]


def steam_openid_endpoint() -> str:
    settings = get_settings()
    if settings.steam_endpoint_url:
        return f"{str(settings.steam_endpoint_url).rstrip('/')}/openid/login"
    return STEAM_OPENID_ENDPOINT


def steam_endpoint_base() -> str | None:
    settings = get_settings()
    return str(settings.steam_endpoint_url).rstrip("/") if settings.steam_endpoint_url else None


def steam_api_base() -> str:
    if endpoint_url := steam_endpoint_base():
        return endpoint_url
    return STEAM_API_BASE


def steam_store_base() -> str:
    if endpoint_url := steam_endpoint_base():
        return endpoint_url
    return STEAM_STORE_BASE


def build_steam_login_url() -> str:
    settings = get_settings()
    params = {
        "openid.ns": "http://specs.openid.net/auth/2.0",
        "openid.mode": "checkid_setup",
        "openid.return_to": settings.steam_openid_return_url,
        "openid.realm": settings.steam_openid_realm,
        "openid.identity": "http://specs.openid.net/auth/2.0/identifier_select",
        "openid.claimed_id": "http://specs.openid.net/auth/2.0/identifier_select",
    }
    return f"{steam_openid_endpoint()}?{urlencode(params)}"


def extract_steam_id(claimed_id: str | None) -> str:
    if not claimed_id or not claimed_id.startswith("https://steamcommunity.com/openid/id/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Steam identity",
        )
    return claimed_id.rstrip("/").rsplit("/", 1)[-1]


async def verify_openid_response(request: Request) -> str:
    settings = get_settings()
    query = dict(request.query_params)
    steam_id = extract_steam_id(query.get("openid.claimed_id"))
    if not settings.steam_openid_verify:
        return steam_id

    verification_payload = dict(parse_qsl(request.url.query))
    verification_payload["openid.mode"] = "check_authentication"
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.post(steam_openid_endpoint(), data=verification_payload)
    response.raise_for_status()
    if "is_valid:true" not in response.text:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Steam login failed")
    return steam_id


async def fetch_player_summary(steam_id: str) -> SteamProfile:
    settings = get_settings()
    if not settings.steam_web_api_key:
        return SteamProfile(steam_id=steam_id, persona_name=None, avatar_url=None, profile_url=None)
    params = {"key": settings.steam_web_api_key, "steamids": steam_id}
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.get(
            f"{steam_api_base()}/ISteamUser/GetPlayerSummaries/v0002/",
            params=params,
        )
    response.raise_for_status()
    players = response.json().get("response", {}).get("players", [])
    player = players[0] if players else {}
    return SteamProfile(
        steam_id=steam_id,
        persona_name=player.get("personaname"),
        avatar_url=player.get("avatarfull") or player.get("avatarmedium"),
        profile_url=player.get("profileurl"),
    )


async def fetch_owned_games(steam_id: str) -> list[OwnedGame]:
    settings = get_settings()
    if not settings.steam_web_api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Steam API key missing",
        )
    params: QueryParams = {
        "key": settings.steam_web_api_key,
        "steamid": steam_id,
        "include_appinfo": 1,
        "include_played_free_games": 1,
    }
    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.get(
            f"{steam_api_base()}/IPlayerService/GetOwnedGames/v0001/",
            params=params,
        )
    response.raise_for_status()
    games = response.json().get("response", {}).get("games", [])
    parsed: list[OwnedGame] = []
    for game in games:
        last_played = game.get("rtime_last_played")
        parsed.append(
            OwnedGame(
                app_id=int(game["appid"]),
                name=game.get("name") or f"App {game['appid']}",
                playtime_forever_minutes=int(game.get("playtime_forever", 0)),
                playtime_2weeks_minutes=int(game.get("playtime_2weeks", 0)),
                last_played_at=datetime.fromtimestamp(last_played, UTC) if last_played else None,
            )
        )
    return parsed


def _extract_genres(data: dict) -> list[str]:
    return [g.get("description", "") for g in data.get("genres", []) if g.get("description")]


def _parse_store_metadata(app_id: int, data: dict, genres_by_lang: dict[str, list[str]] | None = None) -> StoreMetadata:
    price = data.get("price_overview") or {}
    is_free = bool(data.get("is_free", False))
    return StoreMetadata(
        app_id=app_id,
        name=data.get("name") or f"App {app_id}",
        header_image=data.get("header_image"),
        current_price_cents=0 if is_free else price.get("final"),
        initial_price_cents=0 if is_free else price.get("initial"),
        discount_percent=price.get("discount_percent"),
        currency=price.get("currency"),
        is_free=is_free,
        genres=genres_by_lang or {},
    )


async def fetch_store_metadata(app_id: int) -> StoreMetadata | None:
    base_params: QueryParams = {"appids": app_id, "filters": "basic,price_overview,genres"}
    async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
        response = await client.get(f"{steam_store_base()}/appdetails", params=base_params)
    response.raise_for_status()
    payload = response.json().get(str(app_id), {})
    if not payload.get("success"):
        return None
    data = payload.get("data", {})
    genres_by_lang: dict[str, list[str]] = {"english": _extract_genres(data)}

    pt_params: QueryParams = {"appids": app_id, "filters": "genres", "l": "portuguese"}
    async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
        pt_response = await client.get(f"{steam_store_base()}/appdetails", params=pt_params)
    if pt_response.status_code == 200:
        pt_data = pt_response.json().get(str(app_id), {}).get("data", {})
        genres_by_lang["portuguese"] = _extract_genres(pt_data)

    return _parse_store_metadata(app_id, data, genres_by_lang)


async def fetch_store_metadata_batch(
    app_ids: list[int], chunk_size: int = 20
) -> dict[int, StoreMetadata | None]:
    results: dict[int, StoreMetadata | None] = {}
    if not app_ids:
        return results

    async with httpx.AsyncClient(timeout=20, follow_redirects=True) as client:
        for i in range(0, len(app_ids), chunk_size):
            chunk = app_ids[i : i + chunk_size]
            appids_csv = ",".join(str(a) for a in chunk)

            en_params: QueryParams = {"appids": appids_csv, "filters": "basic,price_overview,genres"}
            en_response = await client.get(f"{steam_store_base()}/appdetails", params=en_params)
            en_response.raise_for_status()
            en_body = en_response.json()

            pt_params: QueryParams = {"appids": appids_csv, "filters": "genres", "l": "portuguese"}
            pt_response = await client.get(f"{steam_store_base()}/appdetails", params=pt_params)
            pt_body = pt_response.json() if pt_response.status_code == 200 else {}

            for app_id in chunk:
                en_payload = en_body.get(str(app_id), {})
                if en_payload.get("success"):
                    en_data = en_payload.get("data", {})
                    pt_data = pt_body.get(str(app_id), {}).get("data", {})
                    genres_by_lang = {
                        "english": _extract_genres(en_data),
                        "portuguese": _extract_genres(pt_data),
                    }
                    results[app_id] = _parse_store_metadata(app_id, en_data, genres_by_lang)
                else:
                    results[app_id] = None
    return results


@dataclass(frozen=True)
class AchievementSchema:
    api_name: str
    display_name: str | None
    description: str | None
    icon_url: str | None
    icon_gray_url: str | None
    hidden: bool


@dataclass(frozen=True)
class PlayerAchievement:
    api_name: str
    achieved: bool
    unlock_time: datetime | None


async def fetch_game_achievement_schema(app_id: int, language: str = "english") -> list[AchievementSchema]:
    settings = get_settings()
    if not settings.steam_web_api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Steam API key missing",
        )
    params: QueryParams = {
        "key": settings.steam_web_api_key,
        "appid": app_id,
        "l": language,
    }
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.get(
            f"{steam_api_base()}/ISteamUserStats/GetSchemaForGame/v2/",
            params=params,
        )
    response.raise_for_status()
    achievements = (
        response.json()
        .get("game", {})
        .get("availableGameStats", {})
        .get("achievements", [])
    )
    return [
        AchievementSchema(
            api_name=a.get("name", ""),
            display_name=a.get("displayName"),
            description=a.get("description"),
            icon_url=a.get("icon"),
            icon_gray_url=a.get("icongray"),
            hidden=bool(a.get("hidden", 0)),
        )
        for a in achievements
    ]


async def fetch_player_achievements(steam_id: str, app_id: int, language: str = "english") -> list[PlayerAchievement]:
    settings = get_settings()
    if not settings.steam_web_api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Steam API key missing",
        )
    params: QueryParams = {
        "key": settings.steam_web_api_key,
        "steamid": steam_id,
        "appid": app_id,
        "l": language,
    }
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.get(
            f"{steam_api_base()}/ISteamUserStats/GetPlayerAchievements/v1/",
            params=params,
        )
    response.raise_for_status()
    achievements = response.json().get("playerstats", {}).get("achievements", [])
    parsed: list[PlayerAchievement] = []
    for a in achievements:
        unlock_time = a.get("unlocktime")
        parsed.append(
            PlayerAchievement(
                api_name=a.get("apiname", ""),
                achieved=bool(a.get("achieved", 0)),
                unlock_time=datetime.fromtimestamp(unlock_time, UTC) if unlock_time else None,
            )
        )
    return parsed
