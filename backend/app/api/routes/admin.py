from fastapi import APIRouter
from sqlmodel import select

from app.api.deps import SessionDep
from app.models import Game
from app.services.library import metadata_is_stale, refresh_game_metadata

router = APIRouter(prefix="/internal", tags=["internal"])


@router.post("/refresh-stale-games")
async def refresh_stale_games(session: SessionDep, limit: int = 50) -> dict[str, int]:
    games = session.exec(select(Game)).all()
    refreshed = 0
    for game in games:
        if refreshed >= limit:
            break
        if metadata_is_stale(game):
            await refresh_game_metadata(session, game.app_id, game.name)
            refreshed += 1
    session.commit()
    return {"refreshed": refreshed}
