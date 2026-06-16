from datetime import UTC, datetime, timedelta

from sqlmodel import Session, select

from app.core.config import get_settings
from app.core.security import access_token_for, decode_token, hash_token, refresh_token_for
from app.models import RefreshSession, User, utc_now
from app.schemas import TokenResponse
from app.services.steam import SteamProfile


def upsert_user(session: Session, profile: SteamProfile) -> User:
    user = session.get(User, profile.steam_id)
    if user is None:
        user = User(steam_id=profile.steam_id)
        session.add(user)
    user.persona_name = profile.persona_name
    user.avatar_url = profile.avatar_url
    user.profile_url = profile.profile_url
    user.last_login_at = utc_now()
    user.updated_at = utc_now()
    session.commit()
    session.refresh(user)
    return user


def issue_tokens(session: Session, user: User) -> TokenResponse:
    settings = get_settings()
    access_token = access_token_for(user.steam_id)
    refresh_token = refresh_token_for(user.steam_id)
    refresh_session = RefreshSession(
        user_steam_id=user.steam_id,
        token_hash=hash_token(refresh_token),
        expires_at=datetime.now(UTC) + timedelta(days=settings.refresh_token_expire_days),
    )
    session.add(refresh_session)
    session.commit()
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


def rotate_refresh_token(session: Session, token: str) -> TokenResponse:
    payload = decode_token(token, "refresh")
    token_hash = hash_token(token)
    refresh_session = session.exec(
        select(RefreshSession).where(RefreshSession.token_hash == token_hash)
    ).first()
    if (
        refresh_session is None
        or refresh_session.revoked_at is not None
        or refresh_session.expires_at <= datetime.now(UTC)
    ):
        raise ValueError("Refresh session is invalid")
    refresh_session.revoked_at = utc_now()
    user = session.get(User, payload["sub"])
    if user is None:
        raise ValueError("User does not exist")
    session.add(refresh_session)
    return issue_tokens(session, user)


def revoke_refresh_token(session: Session, token: str) -> None:
    refresh_session = session.exec(
        select(RefreshSession).where(RefreshSession.token_hash == hash_token(token))
    ).first()
    if refresh_session is not None and refresh_session.revoked_at is None:
        refresh_session.revoked_at = utc_now()
        session.add(refresh_session)
        session.commit()
