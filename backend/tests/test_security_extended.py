from datetime import timedelta

import pytest
from fastapi import HTTPException

from app.core.security import create_token, decode_token


@pytest.fixture(autouse=True)
def _set_jwt_secrets(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("JWT_SECRET_KEY", "test-secret-key-long-enough-32b!")
    monkeypatch.setenv("JWT_REFRESH_SECRET_KEY", "test-refresh-key-long-enough-32!")


def test_decode_token_invalid_jwt_raises_401() -> None:
    with pytest.raises(HTTPException) as exc_info:
        decode_token("not.a.valid.jwt", "access")
    assert exc_info.value.status_code == 401
    assert "Invalid or expired" in str(exc_info.value.detail)


def test_decode_token_wrong_kind_raises_401() -> None:
    # Using different secrets for access/refresh, so decoding with wrong key raises
    token = create_token("76561198000000001", "refresh", timedelta(minutes=5))
    with pytest.raises(HTTPException) as exc_info:
        decode_token(token, "access")
    assert exc_info.value.status_code == 401


def test_decode_token_expired_raises_401(monkeypatch: pytest.MonkeyPatch) -> None:
    token = create_token("76561198000000001", "access", timedelta(seconds=-1))
    with pytest.raises(HTTPException) as exc_info:
        decode_token(token, "access")
    assert exc_info.value.status_code == 401


def test_create_token_includes_required_claims() -> None:
    token = create_token("76561198000000001", "access", timedelta(hours=1))
    payload = decode_token(token, "access")
    assert payload["sub"] == "76561198000000001"
    assert payload["typ"] == "access"
    assert "iat" in payload
    assert "exp" in payload
    assert "jti" in payload
