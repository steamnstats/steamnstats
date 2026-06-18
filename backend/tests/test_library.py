from datetime import UTC, datetime, timedelta

from app.models import Game, User, UserGame
from app.schemas import LibraryEntryRead
from app.services.library import build_summary, metadata_is_stale


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
