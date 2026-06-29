from datetime import UTC, datetime, timedelta

import pytest
import respx
from httpx import Response
from sqlmodel import select

from app.models import Game, GameAchievement, User, UserGame
from app.schemas import LibraryEntryRead
from app.services.library import (
    achievement_schema_is_stale,
    build_summary,
    metadata_is_stale,
    refresh_game_achievement_schema,
    refresh_game_metadata,
    upsert_library_entry,
)
from app.services.steam import OwnedGame, steam_api_base, steam_store_base


def test_metadata_staleness() -> None:
    fresh = Game(
        app_id=10,
        name="Fresh",
        metadata_fetched_at=datetime.now(UTC),
        metadata_ttl_seconds=3600,
    )
    stale = Game(
        app_id=20,
        name="Stale",
        metadata_fetched_at=datetime.now(UTC) - timedelta(hours=2),
        metadata_ttl_seconds=3600,
    )
    assert metadata_is_stale(fresh) is False
    assert metadata_is_stale(stale) is True


def test_summary_uses_current_prices_and_tracks_unavailable(session) -> None:
    user = User(steam_id="76561198000000000", persona_name="Tester")
    paid = Game(app_id=1, name="Paid", current_price_cents=1999, currency="USD")
    free = Game(app_id=2, name="Free", current_price_cents=0, currency="USD", is_free=True)
    unknown = Game(app_id=3, name="Unknown")
    session.add(user)
    session.add(paid)
    session.add(free)
    session.add(unknown)
    session.add(UserGame(user_steam_id=user.steam_id, game_app_id=1, playtime_forever_minutes=120))
    session.add(UserGame(user_steam_id=user.steam_id, game_app_id=2, playtime_forever_minutes=240))
    session.add(UserGame(user_steam_id=user.steam_id, game_app_id=3, playtime_forever_minutes=60))
    session.commit()

    summary = build_summary(session, user)

    assert summary.estimated_value_cents == 1999
    assert summary.owned_games == 3
    assert summary.priced_games == 2
    assert summary.free_games == 1
    assert summary.unavailable_prices == 1
    assert summary.total_playtime_minutes == 420
    assert summary.most_played[0].name == "Free"


def test_library_entry_read_accepts_game_model() -> None:
    entry = LibraryEntryRead(
        game=Game(app_id=10, name="Counter-Strike", current_price_cents=999),
        playtime_forever_minutes=1840,
        playtime_2weeks_minutes=45,
        last_synced_at=datetime.now(UTC),
    )

    assert entry.game.app_id == 10
    assert entry.game.name == "Counter-Strike"


def test_metadata_is_stale_when_never_fetched() -> None:
    game = Game(app_id=30, name="Never", metadata_fetched_at=None)
    assert metadata_is_stale(game) is True


def test_upsert_library_entry_creates_new(session) -> None:
    user = User(steam_id="76561198000000000", persona_name="Tester")
    game = Game(app_id=10, name="CS")
    session.add(user)
    session.add(game)
    session.commit()

    owned = OwnedGame(
        app_id=10,
        name="CS",
        playtime_forever_minutes=500,
        playtime_2weeks_minutes=30,
        last_played_at=datetime.now(UTC),
    )
    entry = upsert_library_entry(session, user, owned, game)
    session.commit()

    assert entry.user_steam_id == "76561198000000000"
    assert entry.game_app_id == 10
    assert entry.playtime_forever_minutes == 500
    assert entry.playtime_2weeks_minutes == 30
    assert entry.last_played_at is not None


def test_upsert_library_entry_updates_existing(session) -> None:
    user = User(steam_id="76561198000000000", persona_name="Tester")
    game = Game(app_id=10, name="CS")
    session.add(user)
    session.add(game)
    session.add(UserGame(user_steam_id=user.steam_id, game_app_id=10, playtime_forever_minutes=100))
    session.commit()

    owned = OwnedGame(
        app_id=10,
        name="CS",
        playtime_forever_minutes=999,
        playtime_2weeks_minutes=50,
        last_played_at=None,
    )
    entry = upsert_library_entry(session, user, owned, game)
    session.commit()

    assert entry.playtime_forever_minutes == 999
    assert entry.playtime_2weeks_minutes == 50


@respx.mock
async def test_refresh_game_metadata_fetches_and_updates(session, monkeypatch) -> None:
    monkeypatch.setenv("GAME_METADATA_TTL_HOURS", "24")
    url = f"{steam_store_base()}/appdetails"
    respx.get(url).mock(
        return_value=Response(
            200,
            json={
                "10": {
                    "success": True,
                    "data": {
                        "name": "Counter-Strike 2",
                        "header_image": "https://example.com/header.jpg",
                        "price_overview": {
                            "final": 0,
                            "initial": 0,
                            "discount_percent": 100,
                            "currency": "USD",
                        },
                        "is_free": False,
                    },
                }
            },
        )
    )

    game = await refresh_game_metadata(session, 10, fallback_name="App 10")
    session.commit()

    assert game.app_id == 10
    assert game.name == "Counter-Strike 2"
    assert game.header_image == "https://example.com/header.jpg"
    assert game.metadata_fetched_at is not None


@respx.mock
async def test_refresh_game_metadata_returns_cached_when_fresh(session, monkeypatch) -> None:
    monkeypatch.setenv("GAME_METADATA_TTL_HOURS", "24")
    game = Game(
        app_id=10,
        name="Cached",
        metadata_fetched_at=datetime.now(UTC),
        metadata_ttl_seconds=86400,
    )
    session.add(game)
    session.commit()

    result = await refresh_game_metadata(session, 10, fallback_name="App 10")

    assert result.name == "Cached"


@respx.mock
async def test_refresh_game_metadata_handles_unsuccessful_fetch(session, monkeypatch) -> None:
    monkeypatch.setenv("GAME_METADATA_TTL_HOURS", "24")
    url = f"{steam_store_base()}/appdetails"
    respx.get(url).mock(return_value=Response(200, json={"10": {"success": False}}))

    game = await refresh_game_metadata(session, 10, fallback_name="My Game")
    session.commit()

    assert game.name == "My Game"
    assert game.metadata_fetched_at is not None


def test_build_summary_empty_library(session) -> None:
    user = User(steam_id="76561198000000000", persona_name="Tester")
    session.add(user)
    session.commit()

    summary = build_summary(session, user)

    assert summary.estimated_value_cents == 0
    assert summary.owned_games == 0
    assert summary.priced_games == 0
    assert summary.free_games == 0
    assert summary.unavailable_prices == 0
    assert summary.total_playtime_minutes == 0
    assert summary.most_played == []
    assert summary.last_synced_at is None


def test_build_summary_top_games_capped_at_five(session) -> None:
    user = User(steam_id="76561198000000000", persona_name="Tester")
    session.add(user)
    for i in range(7):
        game = Game(app_id=i, name=f"Game {i}", current_price_cents=100, currency="USD")
        session.add(game)
        session.add(UserGame(
            user_steam_id=user.steam_id,
            game_app_id=i,
            playtime_forever_minutes=(7 - i) * 100,
        ))
    session.commit()

    summary = build_summary(session, user)

    assert len(summary.most_played) == 5
    assert summary.most_played[0].name == "Game 0"
    assert summary.most_played[0].playtime_forever_minutes == 700


def test_achievement_schema_staleness() -> None:
    fresh = Game(
        app_id=10,
        name="Fresh",
        achievements_fetched_at=datetime.now(UTC),
        achievements_ttl_seconds=3600,
    )
    stale = Game(
        app_id=20,
        name="Stale",
        achievements_fetched_at=datetime.now(UTC) - timedelta(hours=2),
        achievements_ttl_seconds=3600,
    )
    never = Game(app_id=30, name="Never", achievements_fetched_at=None)
    assert achievement_schema_is_stale(fresh) is False
    assert achievement_schema_is_stale(stale) is True
    assert achievement_schema_is_stale(never) is True


@respx.mock
async def test_refresh_game_achievement_schema_fetches_and_stores(session, monkeypatch) -> None:
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
                                "name": "ACH_1",
                                "displayName": "First",
                                "description": "Do something",
                                "icon": "https://example.com/icon.png",
                                "icongray": "https://example.com/gray.png",
                                "hidden": 0,
                            },
                        ]
                    },
                }
            },
        )
    )

    game = Game(app_id=10, name="Test Game")
    session.add(game)
    session.commit()

    achievements = await refresh_game_achievement_schema(session, 10)
    session.commit()

    assert len(achievements) == 1
    assert achievements[0].api_name == "ACH_1"
    assert achievements[0].display_name == "First"
    assert achievements[0].game_app_id == 10

    refreshed_game = session.get(Game, 10)
    assert refreshed_game.achievements_fetched_at is not None

    db_achievements = session.exec(
        select(GameAchievement).where(GameAchievement.game_app_id == 10)
    ).all()
    assert len(db_achievements) == 1


@respx.mock
async def test_refresh_game_achievement_schema_returns_cached_when_fresh(session, monkeypatch) -> None:
    game = Game(
        app_id=10,
        name="Cached",
        achievements_fetched_at=datetime.now(UTC),
        achievements_ttl_seconds=604800,
    )
    session.add(game)
    session.add(GameAchievement(game_app_id=10, api_name="ACH_CACHED", display_name="Cached Ach"))
    session.commit()

    result = await refresh_game_achievement_schema(session, 10)

    assert len(result) == 1
    assert result[0].api_name == "ACH_CACHED"
