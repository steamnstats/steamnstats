import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from app.api.deps import get_current_user
from app.core.security import access_token_for
from app.models import User


@pytest.fixture(autouse=True)
def _set_jwt_secrets(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("JWT_SECRET_KEY", "test-secret-key-long-enough-32b!")
    monkeypatch.setenv("JWT_REFRESH_SECRET_KEY", "test-refresh-key-long-enough-32!")


def test_get_current_user_valid_token(session) -> None:
    user = User(steam_id="76561198000000010", persona_name="AuthTest")
    session.add(user)
    session.commit()

    token = access_token_for("76561198000000010")
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
    result = get_current_user(session, credentials)

    assert result.steam_id == "76561198000000010"
    assert result.persona_name == "AuthTest"


def test_get_current_user_missing_credentials(session) -> None:
    with pytest.raises(HTTPException) as exc_info:
        get_current_user(session, None)
    assert exc_info.value.status_code == 401
    assert "Missing token" in str(exc_info.value.detail)


def test_get_current_user_invalid_token(session) -> None:
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="invalid.jwt.token")
    with pytest.raises(HTTPException) as exc_info:
        get_current_user(session, credentials)
    assert exc_info.value.status_code == 401


def test_get_current_user_unknown_user(session) -> None:
    token = access_token_for("76561198099999999")
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
    with pytest.raises(HTTPException) as exc_info:
        get_current_user(session, credentials)
    assert exc_info.value.status_code == 401
    assert "Unknown user" in str(exc_info.value.detail)
