from datetime import datetime, timezone

from jose import jwt

from app.core.config import settings
from app.core.jwt import create_access_token


def test_create_access_token():
    user_id = "test-user-id"

    token = create_access_token(user_id)

    payload = jwt.decode(
        token,
        settings.SECRET_KEY,
        algorithms=[settings.ALGORITHM],
    )

    assert payload["sub"] == user_id
    assert "exp" in payload


def test_access_token_has_future_expiration():
    token = create_access_token("test-user-id")

    payload = jwt.decode(
        token,
        settings.SECRET_KEY,
        algorithms=[settings.ALGORITHM],
    )

    expiration = datetime.fromtimestamp(
        payload["exp"],
        tz=timezone.utc,
    )

    assert expiration > datetime.now(timezone.utc)