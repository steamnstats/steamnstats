from datetime import UTC, datetime, timedelta

import pytest
from sqlmodel import Session, select

from app.core.security import hash_token
from app.models import RefreshSession, User
from app.services.auth import issue_tokens, revoke_refresh_token, rotate_refresh_token, upsert_user
from app.services.steam import SteamProfile


@pytest.fixture(autouse=True)
def _set_jwt_secrets(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("JWT_SECRET_KEY", "test-secret-key-long-enough-32b!")
    monkeypatch.setenv("JWT_REFRESH_SECRET_KEY", "test-refresh-key-long-enough-32!")


def test_upsert_user_creates_new_user(session: Session) -> None:
    profile = SteamProfile(
        steam_id="76561198000000001",
        persona_name="NewPlayer",
        avatar_url="https://example.com/avatar.jpg",
        profile_url="https://steamcommunity.com/id/newplayer",
    )
    user = upsert_user(session, profile)

    assert user.steam_id == "76561198000000001"
    assert user.persona_name == "NewPlayer"
    assert user.avatar_url == "https://example.com/avatar.jpg"
    assert user.profile_url == "https://steamcommunity.com/id/newplayer"


def test_upsert_user_updates_existing_user(session: Session) -> None:
    existing = User(steam_id="76561198000000002", persona_name="OldName")
    session.add(existing)
    session.commit()

    profile = SteamProfile(
        steam_id="76561198000000002",
        persona_name="UpdatedName",
        avatar_url="https://example.com/new_avatar.jpg",
        profile_url=None,
    )
    user = upsert_user(session, profile)

    assert user.steam_id == "76561198000000002"
    assert user.persona_name == "UpdatedName"
    assert user.avatar_url == "https://example.com/new_avatar.jpg"


def test_issue_tokens_returns_token_pair_and_stores_refresh(session: Session) -> None:
    user = User(steam_id="76561198000000003", persona_name="Tester")
    session.add(user)
    session.commit()

    tokens = issue_tokens(session, user)

    assert tokens.access_token
    assert tokens.refresh_token
    assert tokens.token_type == "bearer"

    stored = session.exec(select(RefreshSession)).first()
    assert stored is not None
    assert stored.user_steam_id == user.steam_id
    assert stored.token_hash == hash_token(tokens.refresh_token)


def test_rotate_refresh_token_issues_new_pair_and_revokes_old(session: Session) -> None:
    user = User(steam_id="76561198000000004", persona_name="Rotator")
    session.add(user)
    session.commit()

    tokens = issue_tokens(session, user)
    old_refresh = tokens.refresh_token

    # SQLite loses timezone; patch expires_at to be tz-aware for comparison
    rs = session.exec(
        select(RefreshSession).where(RefreshSession.token_hash == hash_token(old_refresh))
    ).first()
    assert rs is not None
    rs.expires_at = datetime.now(UTC) + timedelta(days=30)
    session.add(rs)
    session.commit()

    new_tokens = rotate_refresh_token(session, old_refresh)

    assert new_tokens.access_token != tokens.access_token
    assert new_tokens.refresh_token != old_refresh

    old_session = session.exec(
        select(RefreshSession).where(RefreshSession.token_hash == hash_token(old_refresh))
    ).first()
    assert old_session is not None
    assert old_session.revoked_at is not None


def test_rotate_refresh_token_rejects_revoked_token(session: Session) -> None:
    user = User(steam_id="76561198000000005", persona_name="Revoker")
    session.add(user)
    session.commit()

    tokens = issue_tokens(session, user)

    # SQLite loses timezone; patch expires_at to be tz-aware
    rs = session.exec(
        select(RefreshSession).where(RefreshSession.token_hash == hash_token(tokens.refresh_token))
    ).first()
    assert rs is not None
    rs.expires_at = datetime.now(UTC) + timedelta(days=30)
    session.add(rs)
    session.commit()

    rotate_refresh_token(session, tokens.refresh_token)

    with pytest.raises(ValueError, match="invalid"):
        rotate_refresh_token(session, tokens.refresh_token)


def test_rotate_refresh_token_rejects_expired_token(session: Session) -> None:
    user = User(steam_id="76561198000000006", persona_name="Expirer")
    session.add(user)
    session.commit()

    tokens = issue_tokens(session, user)

    rs = session.exec(
        select(RefreshSession).where(RefreshSession.token_hash == hash_token(tokens.refresh_token))
    ).first()
    assert rs is not None
    # Set to expired (tz-aware so comparison in rotate_refresh_token works)
    rs.expires_at = datetime.now(UTC) - timedelta(days=1)
    session.add(rs)
    session.commit()

    with pytest.raises(ValueError, match="invalid"):
        rotate_refresh_token(session, tokens.refresh_token)


def test_revoke_refresh_token_marks_session_revoked(session: Session) -> None:
    user = User(steam_id="76561198000000007", persona_name="Revoker2")
    session.add(user)
    session.commit()

    tokens = issue_tokens(session, user)
    revoke_refresh_token(session, tokens.refresh_token)

    rs = session.exec(
        select(RefreshSession).where(RefreshSession.token_hash == hash_token(tokens.refresh_token))
    ).first()
    assert rs is not None
    assert rs.revoked_at is not None


def test_revoke_refresh_token_noop_for_unknown_token(session: Session) -> None:
    revoke_refresh_token(session, "nonexistent-token")
