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
