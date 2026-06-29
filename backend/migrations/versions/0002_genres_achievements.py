"""add genres column and gameachievement table

Revision ID: 0002_genres_achievements
Revises: 0001_initial
Create Date: 2026-06-29
"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
import sqlmodel

revision: str = "0002_genres_achievements"
down_revision: str | None = "0001_initial"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("game", sa.Column("genres", sa.JSON(), nullable=False, server_default="[]"))
    op.add_column("game", sa.Column("achievements_fetched_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("game", sa.Column("achievements_ttl_seconds", sa.Integer(), nullable=False, server_default="604800"))

    op.create_table(
        "gameachievement",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("game_app_id", sa.Integer(), nullable=False),
        sa.Column("api_name", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("display_name", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("description", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("icon_url", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("icon_gray_url", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("hidden", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["game_app_id"], ["game.app_id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_gameachievement_game_app_id"), "gameachievement", ["game_app_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_gameachievement_game_app_id"), table_name="gameachievement")
    op.drop_table("gameachievement")
    op.drop_column("game", "achievements_ttl_seconds")
    op.drop_column("game", "achievements_fetched_at")
    op.drop_column("game", "genres")
