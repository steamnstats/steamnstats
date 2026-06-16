from app.core.security import access_token_for, decode_token, hash_token, refresh_token_for


def test_access_token_round_trip(monkeypatch) -> None:
    monkeypatch.setenv("JWT_SECRET_KEY", "test-access-secret")
    token = access_token_for("76561198000000000")
    payload = decode_token(token, "access")
    assert payload["sub"] == "76561198000000000"
    assert payload["typ"] == "access"


def test_refresh_tokens_are_hashable_and_not_plaintext(monkeypatch) -> None:
    monkeypatch.setenv("JWT_REFRESH_SECRET_KEY", "test-refresh-secret")
    token = refresh_token_for("76561198000000000")
    digest = hash_token(token)
    assert digest != token
    assert len(digest) == 64
