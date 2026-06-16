import asyncio

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlmodel import Session

from app.db.session import engine
from app.models import Game
from app.services.library import metadata_is_stale, refresh_game_metadata


async def refresh_stale_metadata(limit: int = 100) -> None:
    with Session(engine) as session:
        refreshed = 0
        for game in session.query(Game).all():
            if refreshed >= limit:
                break
            if metadata_is_stale(game):
                await refresh_game_metadata(session, game.app_id, game.name)
                refreshed += 1
        session.commit()


async def main() -> None:
    scheduler = AsyncIOScheduler()
    scheduler.add_job(refresh_stale_metadata, "interval", hours=6, id="refresh-stale-games")
    scheduler.start()
    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())
