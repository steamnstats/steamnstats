from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models import SyncStatus


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    steam_id: str
    persona_name: str | None = None
    avatar_url: str | None = None
    profile_url: str | None = None
    last_login_at: datetime


class GameRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    app_id: int
    name: str
    header_image: str | None = None
    current_price_cents: int | None = None
    initial_price_cents: int | None = None
    discount_percent: int | None = None
    currency: str | None = None
    is_free: bool
    lowest_price_cents: int | None = None
    metadata_fetched_at: datetime | None = None


class LibraryEntryRead(BaseModel):
    game: GameRead
    playtime_forever_minutes: int
    playtime_2weeks_minutes: int
    last_played_at: datetime | None = None
    last_synced_at: datetime


class LibraryResponse(BaseModel):
    items: list[LibraryEntryRead]


class TopGameRead(BaseModel):
    app_id: int
    name: str
    playtime_forever_minutes: int
    header_image: str | None = None


class SummaryResponse(BaseModel):
    estimated_value_cents: int
    currency: str | None
    owned_games: int
    priced_games: int
    unavailable_prices: int
    free_games: int
    total_playtime_minutes: int
    most_played: list[TopGameRead]
    last_synced_at: datetime | None


class SyncJobRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    status: SyncStatus
    games_seen: int
    games_priced: int
    unavailable_prices: int
    error: str | None = None
    created_at: datetime
    started_at: datetime | None = None
    finished_at: datetime | None = None
