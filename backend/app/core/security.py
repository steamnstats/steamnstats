from datetime import UTC, datetime, timedelta
from hashlib import sha256
from secrets import token_urlsafe
from typing import Any, Literal

import jwt
from fastapi import HTTPException, status

from app.core.config import get_settings

TokenKind = Literal["access", "refresh"]


def create_token(subject: str, kind: TokenKind, expires_delta: timedelta) -> str:
    settings = get_settings()
    secret = settings.jwt_secret_key if kind == "access" else settings.jwt_refresh_secret_key
    now = datetime.now(UTC)
    payload: dict[str, Any] = {
        "sub": subject,
        "typ": kind,
        "iat": int(now.timestamp()),
        "exp": int((now + expires_delta).timestamp()),
        "jti": token_urlsafe(16),
    }
    return jwt.encode(payload, secret, algorithm="HS256")


def decode_token(token: str, kind: TokenKind) -> dict[str, Any]:
    settings = get_settings()
    secret = settings.jwt_secret_key if kind == "access" else settings.jwt_refresh_secret_key
    try:
        payload = jwt.decode(token, secret, algorithms=["HS256"])
    except jwt.PyJWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        ) from exc
    if payload.get("typ") != kind or not payload.get("sub"):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")
    return payload


def hash_token(token: str) -> str:
    return sha256(token.encode("utf-8")).hexdigest()


def access_token_for(steam_id: str) -> str:
    settings = get_settings()
    return create_token(
        steam_id,
        "access",
        timedelta(minutes=settings.access_token_expire_minutes),
    )


def refresh_token_for(steam_id: str) -> str:
    settings = get_settings()
    return create_token(
        steam_id,
        "refresh",
        timedelta(days=settings.refresh_token_expire_days),
    )
