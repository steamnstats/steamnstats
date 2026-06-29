from fastapi import FastAPI, Query, Request
from fastapi.responses import PlainTextResponse, RedirectResponse, Response

MOCK_STEAM_ID = "76561198000000000"

MOCK_GAMES = [
    {
        "appid": 10,
        "name": "Counter-Strike",
        "playtime_forever": 1840,
        "playtime_2weeks": 45,
        "rtime_last_played": 1718064000,
    },
    {
        "appid": 70,
        "name": "Half-Life",
        "playtime_forever": 920,
        "playtime_2weeks": 0,
        "rtime_last_played": 1715472000,
    },
    {
        "appid": 620,
        "name": "Portal 2",
        "playtime_forever": 1320,
        "playtime_2weeks": 120,
        "rtime_last_played": 1718841600,
    },
]

MOCK_ACHIEVEMENTS = {
    10: [
        {
            "name": "ACH_HEADSHOT",
            "displayName": "Headshot",
            "description": "Get a headshot kill",
            "icon": "https://cdn.cloudflare.steamstatic.com/steamcommunity/public/images/apps/10/ach_headshot.jpg",
            "icongray": "https://cdn.cloudflare.steamstatic.com/steamcommunity/public/images/apps/10/ach_headshot_gray.jpg",
            "hidden": 0,
        },
        {
            "name": "ACH_MVP",
            "displayName": "Most Valuable Player",
            "description": "Be the MVP of a round",
            "icon": "https://cdn.cloudflare.steamstatic.com/steamcommunity/public/images/apps/10/ach_mvp.jpg",
            "icongray": "https://cdn.cloudflare.steamstatic.com/steamcommunity/public/images/apps/10/ach_mvp_gray.jpg",
            "hidden": 0,
        },
    ],
    70: [
        {
            "name": "ACH_CROWBAR",
            "displayName": "Trusty Crowbar",
            "description": "Defeat an enemy with the crowbar",
            "icon": "https://cdn.cloudflare.steamstatic.com/steamcommunity/public/images/apps/70/ach_crowbar.jpg",
            "icongray": "https://cdn.cloudflare.steamstatic.com/steamcommunity/public/images/apps/70/ach_crowbar_gray.jpg",
            "hidden": 0,
        },
    ],
    620: [
        {
            "name": "ACH_PORTAL",
            "displayName": "Portal Pioneering",
            "description": "Complete all test chambers",
            "icon": "https://cdn.cloudflare.steamstatic.com/steamcommunity/public/images/apps/620/ach_portal.jpg",
            "icongray": "https://cdn.cloudflare.steamstatic.com/steamcommunity/public/images/apps/620/ach_portal_gray.jpg",
            "hidden": 0,
        },
        {
            "name": "ACH_SECRET",
            "displayName": "Secret Achievement",
            "hidden": 1,
            "icon": "https://cdn.cloudflare.steamstatic.com/steamcommunity/public/images/apps/620/ach_secret.jpg",
            "icongray": "https://cdn.cloudflare.steamstatic.com/steamcommunity/public/images/apps/620/ach_secret_gray.jpg",
        },
    ],
}

MOCK_PLAYER_ACHIEVEMENTS = {
    10: [
        {"apiname": "ACH_HEADSHOT", "achieved": 1, "unlocktime": 1718064000},
        {"apiname": "ACH_MVP", "achieved": 0},
    ],
    70: [
        {"apiname": "ACH_CROWBAR", "achieved": 1, "unlocktime": 1715472000},
    ],
    620: [
        {"apiname": "ACH_PORTAL", "achieved": 1, "unlocktime": 1718841600},
        {"apiname": "ACH_SECRET", "achieved": 0},
    ],
}

MOCK_STORE = {
    10: {
        "name": "Counter-Strike",
        "header_image": "https://cdn.cloudflare.steamstatic.com/steam/apps/10/header.jpg",
        "price_overview": {
            "currency": "USD",
            "initial": 999,
            "final": 999,
            "discount_percent": 0,
        },
        "is_free": False,
        "genres": [
            {"id": "1", "description": "Action"},
            {"id": "37", "description": "Free to Play"},
        ],
    },
    70: {
        "name": "Half-Life",
        "header_image": "https://cdn.cloudflare.steamstatic.com/steam/apps/70/header.jpg",
        "price_overview": {
            "currency": "USD",
            "initial": 999,
            "final": 249,
            "discount_percent": 75,
        },
        "is_free": False,
        "genres": [
            {"id": "1", "description": "Action"},
            {"id": "24", "description": "Classic"},
        ],
    },
    620: {
        "name": "Portal 2",
        "header_image": "https://cdn.cloudflare.steamstatic.com/steam/apps/620/header.jpg",
        "price_overview": {
            "currency": "USD",
            "initial": 999,
            "final": 99,
            "discount_percent": 90,
        },
        "is_free": False,
        "genres": [
            {"id": "1", "description": "Action"},
            {"id": "2", "description": "Strategy"},
            {"id": "5", "description": "Puzzle"},
        ],
    },
}

app = FastAPI(title="Mock Steam API")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.api_route("/openid/login", methods=["GET", "POST"], response_model=None)
async def openid_login(request: Request) -> Response:
    if request.method == "POST":
        return PlainTextResponse("ns:http://specs.openid.net/auth/2.0\nis_valid:true\n")

    return_to = request.query_params.get("openid.return_to")
    if not return_to:
        return PlainTextResponse("Missing openid.return_to", status_code=400)

    separator = "&" if "?" in return_to else "?"
    claimed_id = f"https://steamcommunity.com/openid/id/{MOCK_STEAM_ID}"
    return RedirectResponse(
        f"{return_to}{separator}"
        "openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0&"
        "openid.mode=id_res&"
        f"openid.claimed_id={claimed_id}&"
        f"openid.identity={claimed_id}",
    )


@app.get("/ISteamUser/GetPlayerSummaries/v0002/")
def get_player_summaries(steamids: str = Query(default=MOCK_STEAM_ID)) -> dict[str, object]:
    steam_id = steamids.split(",", 1)[0] or MOCK_STEAM_ID
    return {
        "response": {
            "players": [
                {
                    "steamid": steam_id,
                    "personaname": "Mock Steam Player",
                    "profileurl": f"https://steamcommunity.com/profiles/{steam_id}/",
                    "avatarfull": "https://avatars.cloudflare.steamstatic.com/mock_full.jpg",
                    "avatarmedium": "https://avatars.cloudflare.steamstatic.com/mock_medium.jpg",
                }
            ]
        }
    }


@app.get("/IPlayerService/GetOwnedGames/v0001/")
def get_owned_games() -> dict[str, object]:
    return {"response": {"game_count": len(MOCK_GAMES), "games": MOCK_GAMES}}


@app.get("/appdetails")
def appdetails(appids: str) -> dict[str, object]:
    response: dict[str, object] = {}
    for raw_app_id in appids.split(","):
        app_id = int(raw_app_id)
        data = MOCK_STORE.get(app_id)
        response[str(app_id)] = {"success": data is not None, "data": data or {}}
    return response


@app.get("/ISteamUserStats/GetSchemaForGame/v2/")
def get_schema_for_game(appid: int = Query(), l: str = Query(default="english")) -> dict[str, object]:
    achievements = MOCK_ACHIEVEMENTS.get(appid, [])
    return {
        "game": {
            "gameName": f"App {appid}",
            "gameVersion": 1,
            "availableGameStats": {"achievements": achievements} if achievements else {},
        }
    }


@app.get("/ISteamUserStats/GetPlayerAchievements/v1/")
def get_player_achievements(
    steamid: str = Query(),
    appid: int = Query(),
    l: str = Query(default="english"),
) -> dict[str, object]:
    achievements = MOCK_PLAYER_ACHIEVEMENTS.get(appid, [])
    return {
        "playerstats": {
            "steamID": steamid,
            "gameName": f"App {appid}",
            "achievements": achievements,
        }
    }
