"""initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-06-16
"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
import sqlmodel

revision: str = "0001_initial"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "user",
        sa.Column("steam_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("persona_name", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("avatar_url", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("profile_url", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("steam_id"),
    )
    op.create_index(op.f("ix_user_steam_id"), "user", ["steam_id"], unique=False)
    op.create_table(
        "game",
        sa.Column("app_id", sa.Integer(), nullable=False),
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("header_image", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("current_price_cents", sa.Integer(), nullable=True),
        sa.Column("initial_price_cents", sa.Integer(), nullable=True),
        sa.Column("discount_percent", sa.Integer(), nullable=True),
        sa.Column("currency", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("is_free", sa.Boolean(), nullable=False),
        sa.Column("lowest_price_cents", sa.Integer(), nullable=True),
        sa.Column("metadata_source", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("metadata_fetched_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("metadata_ttl_seconds", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("app_id"),
    )
    op.create_index(op.f("ix_game_app_id"), "game", ["app_id"], unique=False)
    op.create_table(
        "refreshsession",
        sa.Column("id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("user_steam_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("token_hash", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_steam_id"], ["user.steam_id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_refreshsession_token_hash"), "refreshsession", ["token_hash"], unique=True)
    op.create_index(op.f("ix_refreshsession_user_steam_id"), "refreshsession", ["user_steam_id"], unique=False)
    op.create_table(
        "syncjob",
        sa.Column("id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("user_steam_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("status", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("games_seen", sa.Integer(), nullable=False),
        sa.Column("games_priced", sa.Integer(), nullable=False),
        sa.Column("unavailable_prices", sa.Integer(), nullable=False),
        sa.Column("error", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_steam_id"], ["user.steam_id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_syncjob_status"), "syncjob", ["status"], unique=False)
    op.create_index(op.f("ix_syncjob_user_steam_id"), "syncjob", ["user_steam_id"], unique=False)
    op.create_table(
        "usergame",
        sa.Column("user_steam_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("game_app_id", sa.Integer(), nullable=False),
        sa.Column("playtime_forever_minutes", sa.Integer(), nullable=False),
        sa.Column("playtime_2weeks_minutes", sa.Integer(), nullable=False),
        sa.Column("last_played_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("owned_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_synced_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["game_app_id"], ["game.app_id"]),
        sa.ForeignKeyConstraint(["user_steam_id"], ["user.steam_id"]),
        sa.PrimaryKeyConstraint("user_steam_id", "game_app_id"),
        sa.UniqueConstraint("user_steam_id", "game_app_id"),
    )


def downgrade() -> None:
    op.drop_table("usergame")
    op.drop_index(op.f("ix_syncjob_user_steam_id"), table_name="syncjob")
    op.drop_index(op.f("ix_syncjob_status"), table_name="syncjob")
    op.drop_table("syncjob")
    op.drop_index(op.f("ix_refreshsession_user_steam_id"), table_name="refreshsession")
    op.drop_index(op.f("ix_refreshsession_token_hash"), table_name="refreshsession")
    op.drop_table("refreshsession")
    op.drop_index(op.f("ix_game_app_id"), table_name="game")
    op.drop_table("game")
    op.drop_index(op.f("ix_user_steam_id"), table_name="user")
    op.drop_table("user")
