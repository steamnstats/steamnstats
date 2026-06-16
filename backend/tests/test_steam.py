from app.services.steam import extract_steam_id


def test_extract_steam_id_from_claimed_id() -> None:
    steam_id = extract_steam_id("https://steamcommunity.com/openid/id/76561198000000000")
    assert steam_id == "76561198000000000"
