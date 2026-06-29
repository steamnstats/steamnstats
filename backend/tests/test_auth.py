from datetime import UTC, datetime, timedelta

import pytest
from sqlmodel import select

from app.core.security import hash_token
from app.models import RefreshSession, User
from app.services.auth import (
    issue_tokens,
    revoke_refresh_token,
    rotate_refresh_token,
    upsert_user,
)
from app.services.steam import SteamProfile


def test_upsert_user_creates_new_user(session) -> None:
    profile = SteamProfile(
        steam_id="76561198000000000",
        persona_name="NewUser",
        avatar_url="https://example.com/avatar.png",
        profile_url="https://steamcommunity.com/id/newuser",
    )
    user = upsert_user(session, profile)

    assert user.steam_id == "76561198000000000"
    assert user.persona_name == "NewUser"
    assert user.avatar_url == "https://example.com/avatar.png"
    assert user.profile_url == "https://steamcommunity.com/id/newuser"


def test_upsert_user_updates_existing_user(session) -> None:
    session.add(User(steam_id="76561198000000000", persona_name="OldName"))
    session.commit()

    profile = SteamProfile(
        steam_id="76561198000000000",
        persona_name="NewName",
        avatar_url="https://example.com/new.png",
        profile_url=None,
    )
    user = upsert_user(session, profile)

    assert user.steam_id == "76561198000000000"
    assert user.persona_name == "NewName"
    assert user.avatar_url == "https://example.com/new.png"


def test_issue_tokens_returns_access_and_refresh(session, monkeypatch) -> None:
    monkeypatch.setenv("JWT_SECRET_KEY", "test-access-secret")
    monkeypatch.setenv("JWT_REFRESH_SECRET_KEY", "test-refresh-secret")
    user = User(steam_id="76561198000000000", persona_name="Tester")
    session.add(user)
    session.commit()

    tokens = issue_tokens(session, user)

    assert tokens.access_token != tokens.refresh_token
    assert tokens.token_type == "bearer"

    sessions = session.exec(
        select(RefreshSession).where(
            RefreshSession.user_steam_id == user.steam_id
        )
    ).all()
    assert len(sessions) == 1
    assert sessions[0].revoked_at is None


def test_rotate_refresh_token_issues_new_tokens(session, monkeypatch) -> None:
    monkeypatch.setenv("JWT_SECRET_KEY", "test-access-secret")
    monkeypatch.setenv("JWT_REFRESH_SECRET_KEY", "test-refresh-secret")
    user = User(steam_id="76561198000000000", persona_name="Tester")
    session.add(user)
    session.commit()

    tokens = issue_tokens(session, user)
    new_tokens = rotate_refresh_token(session, tokens.refresh_token)

    assert new_tokens.access_token != tokens.access_token
    assert new_tokens.refresh_token != tokens.refresh_token

    old_session = session.exec(
        select(RefreshSession).where(
            RefreshSession.token_hash == hash_token(tokens.refresh_token)
        )
    ).first()
    assert old_session is not None
    assert old_session.revoked_at is not None


def test_rotate_refresh_token_rejects_revoked(session, monkeypatch) -> None:
    monkeypatch.setenv("JWT_SECRET_KEY", "test-access-secret")
    monkeypatch.setenv("JWT_REFRESH_SECRET_KEY", "test-refresh-secret")
    user = User(steam_id="76561198000000000", persona_name="Tester")
    session.add(user)
    session.commit()

    tokens = issue_tokens(session, user)
    revoke_refresh_token(session, tokens.refresh_token)

    with pytest.raises(ValueError, match="invalid"):
        rotate_refresh_token(session, tokens.refresh_token)


def test_rotate_refresh_token_rejects_expired(session, monkeypatch) -> None:
    monkeypatch.setenv("JWT_SECRET_KEY", "test-access-secret")
    monkeypatch.setenv("JWT_REFRESH_SECRET_KEY", "test-refresh-secret")
    user = User(steam_id="76561198000000000", persona_name="Tester")
    session.add(user)
    session.commit()

    tokens = issue_tokens(session, user)

    refresh_session = session.exec(
        select(RefreshSession).where(
            RefreshSession.token_hash == hash_token(tokens.refresh_token)
        )
    ).first()
    assert refresh_session is not None
    refresh_session.expires_at = datetime.now(UTC) - timedelta(seconds=1)
    session.add(refresh_session)
    session.commit()

    with pytest.raises(ValueError, match="invalid"):
        rotate_refresh_token(session, tokens.refresh_token)


def test_revoke_refresh_token_is_idempotent(session, monkeypatch) -> None:
    monkeypatch.setenv("JWT_SECRET_KEY", "test-access-secret")
    monkeypatch.setenv("JWT_REFRESH_SECRET_KEY", "test-refresh-secret")
    user = User(steam_id="76561198000000000", persona_name="Tester")
    session.add(user)
    session.commit()

    tokens = issue_tokens(session, user)

    revoke_refresh_token(session, tokens.refresh_token)
    revoke_refresh_token(session, tokens.refresh_token)

    refresh_session = session.exec(
        select(RefreshSession).where(
            RefreshSession.token_hash == hash_token(tokens.refresh_token)
        )
    ).first()
    assert refresh_session is not None
    assert refresh_session.revoked_at is not None


def test_revoke_refresh_token_unknown_token_is_noop(session) -> None:
    revoke_refresh_token(session, "nonexistent-token")
