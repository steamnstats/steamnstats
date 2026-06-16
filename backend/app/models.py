from datetime import UTC, datetime
from enum import StrEnum
from uuid import uuid4

from sqlalchemy import Column, DateTime, UniqueConstraint
from sqlmodel import Field, Relationship, SQLModel


def utc_now() -> datetime:
    return datetime.now(UTC)


class SyncStatus(StrEnum):
    queued = "queued"
    running = "running"
    succeeded = "succeeded"
    failed = "failed"


class User(SQLModel, table=True):
    steam_id: str = Field(primary_key=True, index=True)
    persona_name: str | None = None
    avatar_url: str | None = None
    profile_url: str | None = None
    last_login_at: datetime = Field(
        default_factory=utc_now,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    created_at: datetime = Field(
        default_factory=utc_now,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    updated_at: datetime = Field(
        default_factory=utc_now,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )

    library_entries: list["UserGame"] = Relationship(back_populates="user")
    refresh_sessions: list["RefreshSession"] = Relationship(back_populates="user")
    sync_jobs: list["SyncJob"] = Relationship(back_populates="user")


class Game(SQLModel, table=True):
    app_id: int = Field(primary_key=True, index=True)
    name: str
    header_image: str | None = None
    current_price_cents: int | None = None
    initial_price_cents: int | None = None
    discount_percent: int | None = None
    currency: str | None = None
    is_free: bool = False
    lowest_price_cents: int | None = None
    metadata_source: str = "steam_store"
    metadata_fetched_at: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
    )
    metadata_ttl_seconds: int = 86_400
    created_at: datetime = Field(
        default_factory=utc_now,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    updated_at: datetime = Field(
        default_factory=utc_now,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )

    owners: list["UserGame"] = Relationship(back_populates="game")


class UserGame(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("user_steam_id", "game_app_id"),)

    user_steam_id: str = Field(foreign_key="user.steam_id", primary_key=True)
    game_app_id: int = Field(foreign_key="game.app_id", primary_key=True)
    playtime_forever_minutes: int = 0
    playtime_2weeks_minutes: int = 0
    last_played_at: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
    )
    owned_at: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
    )
    last_synced_at: datetime = Field(
        default_factory=utc_now,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )

    user: User = Relationship(back_populates="library_entries")
    game: Game = Relationship(back_populates="owners")


class RefreshSession(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    user_steam_id: str = Field(foreign_key="user.steam_id", index=True)
    token_hash: str = Field(index=True, unique=True)
    expires_at: datetime = Field(sa_column=Column(DateTime(timezone=True), nullable=False))
    revoked_at: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
    )
    created_at: datetime = Field(
        default_factory=utc_now,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )

    user: User = Relationship(back_populates="refresh_sessions")


class SyncJob(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    user_steam_id: str = Field(foreign_key="user.steam_id", index=True)
    status: SyncStatus = Field(default=SyncStatus.queued, index=True)
    games_seen: int = 0
    games_priced: int = 0
    unavailable_prices: int = 0
    error: str | None = None
    started_at: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
    )
    finished_at: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
    )
    created_at: datetime = Field(
        default_factory=utc_now,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )

    user: User = Relationship(back_populates="sync_jobs")
