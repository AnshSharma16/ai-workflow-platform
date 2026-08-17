import pytest
from fastapi import HTTPException
from jose import jwt

from app.core.config import settings
from app.core.jwt import create_access_token
from app.dependencies.auth import get_current_user


@pytest.mark.asyncio
async def test_valid_token_returns_user(db_session):
    # Create a token for a real user first.
    from app.models.user import User
    from app.repositories.user_repository import UserRepository

    user = User(
        email="dependency@example.com",
        username="dependencyuser",
        hashed_password="not-a-real-password-hash",
    )

    repository = UserRepository(db_session)
    await repository.create(user)
    await db_session.commit()

    token = create_access_token(str(user.id))

    credentials = type(
        "Credentials",
        (),
        {"credentials": token},
    )()

    current_user = await get_current_user(
        credentials=credentials,
        db=db_session,
    )

    assert current_user.id == user.id
    assert current_user.email == user.email


@pytest.mark.asyncio
async def test_invalid_token_rejected(db_session):
    credentials = type(
        "Credentials",
        (),
        {"credentials": "invalid.token.here"},
    )()

    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(
            credentials=credentials,
            db=db_session,
        )

    assert exc_info.value.status_code == 401


@pytest.mark.asyncio
async def test_token_without_subject_rejected(db_session):
    token = jwt.encode(
        {"exp": 9999999999},
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )

    credentials = type(
        "Credentials",
        (),
        {"credentials": token},
    )()

    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(
            credentials=credentials,
            db=db_session,
        )

    assert exc_info.value.status_code == 401