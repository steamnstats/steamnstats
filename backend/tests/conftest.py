from collections.abc import Generator
from datetime import datetime, timezone

import pytest
from sqlalchemy import event
from sqlalchemy.types import DateTime
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.core.config import get_settings
from app.models import Game, GameAchievement, RefreshSession, SyncJob, User, UserGame

_MODELS = [User, Game, GameAchievement, UserGame, RefreshSession, SyncJob]


@pytest.fixture(autouse=True)
def reset_settings_cache() -> Generator[None, None, None]:
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def _make_datetimes_aware(target, *args):
    for key, value in list(vars(target).items()):
        if isinstance(value, datetime) and value.tzinfo is None:
            setattr(target, key, value.replace(tzinfo=timezone.utc))


@pytest.fixture
def session() -> Generator[Session, None, None]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)

    for model in _MODELS:
        event.listen(model, "load", _make_datetimes_aware)
        event.listen(model, "refresh", _make_datetimes_aware)

    with Session(engine) as db:
        yield db

    for model in _MODELS:
        event.remove(model, "load", _make_datetimes_aware)
        event.remove(model, "refresh", _make_datetimes_aware)
