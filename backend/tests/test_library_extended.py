from datetime import UTC, datetime

from sqlmodel import Session, select

from app.models import Game, User, UserGame
from app.services.library import upsert_library_entry
from app.services.steam import OwnedGame


def test_upsert_library_entry_creates_new_entry(session: Session) -> None:
    user = User(steam_id="76561198000000020", persona_name="Inserter")
    game = Game(app_id=400, name="Portal")
    session.add(user)
    session.add(game)
    session.commit()

    owned = OwnedGame(
        app_id=400,
        name="Portal",
        playtime_forever_minutes=300,
        playtime_2weeks_minutes=60,
        last_played_at=datetime(2024, 1, 15, tzinfo=UTC),
    )

    entry = upsert_library_entry(session, user, owned, game)
    session.commit()

    assert entry.user_steam_id == user.steam_id
    assert entry.game_app_id == 400
    assert entry.playtime_forever_minutes == 300
    assert entry.playtime_2weeks_minutes == 60
    # SQLite strips timezone; compare date components
    assert entry.last_played_at is not None
    assert entry.last_played_at.year == 2024
    assert entry.last_played_at.month == 1
    assert entry.last_played_at.day == 15


def test_upsert_library_entry_updates_existing(session: Session) -> None:
    user = User(steam_id="76561198000000021", persona_name="Updater")
    game = Game(app_id=401, name="Portal 2")
    session.add(user)
    session.add(game)
    session.add(
        UserGame(
            user_steam_id="76561198000000021",
            game_app_id=401,
            playtime_forever_minutes=100,
            playtime_2weeks_minutes=10,
        )
    )
    session.commit()

    owned = OwnedGame(
        app_id=401,
        name="Portal 2",
        playtime_forever_minutes=500,
        playtime_2weeks_minutes=80,
        last_played_at=datetime(2024, 6, 1, tzinfo=UTC),
    )

    entry = upsert_library_entry(session, user, owned, game)
    session.commit()

    assert entry.playtime_forever_minutes == 500
    assert entry.playtime_2weeks_minutes == 80
    assert entry.last_played_at is not None
    assert entry.last_played_at.year == 2024
    assert entry.last_played_at.month == 6

    all_entries = session.exec(
        select(UserGame).where(UserGame.user_steam_id == "76561198000000021")
    ).all()
    assert len(all_entries) == 1


def test_metadata_is_stale_when_never_fetched(session: Session) -> None:
    from app.services.library import metadata_is_stale

    game = Game(app_id=500, name="NeverFetched", metadata_fetched_at=None)
    assert metadata_is_stale(game) is True
