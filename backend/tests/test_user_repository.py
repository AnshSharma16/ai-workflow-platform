from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.user_repository import UserRepository


@pytest.mark.asyncio
async def test_create_and_get_user(db_session: AsyncSession):
    repository = UserRepository(db_session)

    user = User(
        email=f"test-{uuid4()}@example.com",
        username=f"test_{uuid4().hex[:8]}",
        hashed_password="fake-hash",
    )

    created_user = await repository.create(user)
    await db_session.commit()

    found_user = await repository.get_by_email(created_user.email)

    assert found_user is not None
    assert found_user.id == created_user.id
    assert found_user.email == created_user.email
    assert found_user.username == created_user.username