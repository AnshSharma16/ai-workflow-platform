from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import verify_password
from app.schemas.user import UserCreate
from app.services.auth_service import AuthService
from app.core.exceptions import DuplicateEmailError

@pytest.mark.asyncio
async def test_register_user(db_session: AsyncSession):
    service = AuthService(db_session)

    data = UserCreate(
        email=f"newuser-{uuid4()}@example.com",
        username=f"newuser-{uuid4().hex[:8]}",
        password="StrongPassword123",
    )

    user = await service.register(data)

    await db_session.commit()

    assert user.email == data.email
    assert user.username == data.username
    assert user.hashed_password != data.password
    assert verify_password(
        data.password,
        user.hashed_password,
    )


@pytest.mark.asyncio
async def test_duplicate_email_rejected(
    db_session: AsyncSession,
):
    service = AuthService(db_session)

    unique_email = f"duplicate-{uuid4()}@example.com"

    data = UserCreate(
        email=unique_email,
        username=f"user-{uuid4().hex[:8]}",
        password="StrongPassword123",
    )

    # First registration must succeed.
    await service.register(data)
    await db_session.commit()

    duplicate = UserCreate(
        email=unique_email,
        username=f"user-{uuid4().hex[:8]}",
        password="AnotherPassword123",
    )

    # Second registration with the same email must fail.
    with pytest.raises(
        DuplicateEmailError,
        match="Email already registered",
    ):
        await service.register(duplicate)