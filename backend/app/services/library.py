from datetime import UTC, datetime, timedelta

from sqlmodel import Session, col, select

from app.core.config import get_settings
from app.models import Game, SyncJob, SyncStatus, User, UserGame, utc_now
from app.schemas import SummaryResponse, TopGameRead
from app.services.steam import OwnedGame, fetch_owned_games, fetch_store_metadata


def metadata_is_stale(game: Game) -> bool:
    if game.metadata_fetched_at is None:
        return True
    expires_at = game.metadata_fetched_at + timedelta(seconds=game.metadata_ttl_seconds)
    return datetime.now(UTC) >= expires_at


async def refresh_game_metadata(
    session: Session,
    app_id: int,
    fallback_name: str | None = None,
) -> Game:
    settings = get_settings()
    game = session.get(Game, app_id)
    if game is not None and not metadata_is_stale(game):
        return game

    metadata = await fetch_store_metadata(app_id)
    if game is None:
        game = Game(app_id=app_id, name=fallback_name or f"App {app_id}")
        session.add(game)

    if metadata is not None:
        game.name = metadata.name
        game.header_image = metadata.header_image
        game.current_price_cents = metadata.current_price_cents
        game.initial_price_cents = metadata.initial_price_cents
        game.discount_percent = metadata.discount_percent
        game.currency = metadata.currency
        game.is_free = metadata.is_free
        game.metadata_fetched_at = utc_now()
        game.metadata_ttl_seconds = settings.game_metadata_ttl_hours * 3600
    else:
        game.name = fallback_name or game.name
        game.metadata_fetched_at = utc_now()
    game.updated_at = utc_now()
    session.add(game)
    return game


def upsert_library_entry(session: Session, user: User, owned: OwnedGame, game: Game) -> UserGame:
    entry = session.get(UserGame, (user.steam_id, owned.app_id))
    if entry is None:
        entry = UserGame(user_steam_id=user.steam_id, game_app_id=owned.app_id)
        session.add(entry)
    entry.playtime_forever_minutes = owned.playtime_forever_minutes
    entry.playtime_2weeks_minutes = owned.playtime_2weeks_minutes
    entry.last_played_at = owned.last_played_at
    entry.last_synced_at = utc_now()
    entry.game = game
    return entry


async def sync_user_library(session: Session, user: User) -> SyncJob:
    job = SyncJob(user_steam_id=user.steam_id, status=SyncStatus.running, started_at=utc_now())
    session.add(job)
    session.commit()
    session.refresh(job)

    try:
        owned_games = await fetch_owned_games(user.steam_id)
        job.games_seen = len(owned_games)
        for owned in owned_games:
            game = await refresh_game_metadata(session, owned.app_id, owned.name)
            upsert_library_entry(session, user, owned, game)
            if game.current_price_cents is None and not game.is_free:
                job.unavailable_prices += 1
            else:
                job.games_priced += 1
        job.status = SyncStatus.succeeded
    except Exception as exc:
        job.status = SyncStatus.failed
        job.error = str(exc)
        raise
    finally:
        job.finished_at = utc_now()
        session.add(job)
        session.commit()
        session.refresh(job)
    return job


def build_summary(session: Session, user: User) -> SummaryResponse:
    entries = session.exec(
        select(UserGame)
        .where(UserGame.user_steam_id == user.steam_id)
        .order_by(col(UserGame.playtime_forever_minutes).desc())
    ).all()
    estimated_value = 0
    priced_games = 0
    unavailable_prices = 0
    free_games = 0
    currency: str | None = None
    total_playtime = 0
    last_synced_at = None
    top_games: list[TopGameRead] = []

    for entry in entries:
        game = entry.game
        total_playtime += entry.playtime_forever_minutes
        last_synced_at = (
            max(last_synced_at, entry.last_synced_at)
            if last_synced_at
            else entry.last_synced_at
        )
        if game.is_free:
            free_games += 1
            priced_games += 1
        elif game.current_price_cents is None:
            unavailable_prices += 1
        else:
            estimated_value += game.current_price_cents
            priced_games += 1
            currency = currency or game.currency
        if len(top_games) < 5:
            top_games.append(
                TopGameRead(
                    app_id=game.app_id,
                    name=game.name,
                    playtime_forever_minutes=entry.playtime_forever_minutes,
                    header_image=game.header_image,
                )
            )

    return SummaryResponse(
        estimated_value_cents=estimated_value,
        currency=currency,
        owned_games=len(entries),
        priced_games=priced_games,
        unavailable_prices=unavailable_prices,
        free_games=free_games,
        total_playtime_minutes=total_playtime,
        most_played=top_games,
        last_synced_at=last_synced_at,
    )
