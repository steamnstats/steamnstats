from fastapi import APIRouter
from sqlmodel import select

from app.api.deps import CurrentUser, SessionDep
from app.models import UserGame
from app.schemas import LibraryEntryRead, LibraryResponse, SummaryResponse, SyncJobRead, UserRead
from app.services.library import build_summary, sync_user_library

router = APIRouter(prefix="/me", tags=["me"])


@router.get("", response_model=UserRead)
def read_me(user: CurrentUser) -> UserRead:
    return UserRead.model_validate(user)


@router.get("/library", response_model=LibraryResponse)
def read_library(session: SessionDep, user: CurrentUser) -> LibraryResponse:
    entries = session.exec(select(UserGame).where(UserGame.user_steam_id == user.steam_id)).all()
    items = [
        LibraryEntryRead(
            game=entry.game,
            playtime_forever_minutes=entry.playtime_forever_minutes,
            playtime_2weeks_minutes=entry.playtime_2weeks_minutes,
            last_played_at=entry.last_played_at,
            last_synced_at=entry.last_synced_at,
        )
        for entry in entries
    ]
    return LibraryResponse(items=items)


@router.get("/summary", response_model=SummaryResponse)
def read_summary(session: SessionDep, user: CurrentUser) -> SummaryResponse:
    return build_summary(session, user)


@router.post("/sync", response_model=SyncJobRead)
async def sync_library(session: SessionDep, user: CurrentUser) -> SyncJobRead:
    return SyncJobRead.model_validate(await sync_user_library(session, user))
