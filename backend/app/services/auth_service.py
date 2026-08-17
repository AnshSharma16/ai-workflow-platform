from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import DuplicateEmailError
from app.core.jwt import create_access_token
from app.core.security import hash_password, verify_password
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserLogin


class AuthService:
    def __init__(self, session: AsyncSession) -> None:
        self.repository = UserRepository(session)

    async def register(self, data: UserCreate) -> User:
        existing_user = await self.repository.get_by_email(data.email)

        if existing_user:
            raise DuplicateEmailError(data.email)

        hashed_password = hash_password(data.password)

        user = User(
            email=data.email,
            username=data.username,
            hashed_password=hashed_password,
        )

        return await self.repository.create(user)

    async def login(self, data: UserLogin) -> str:
        user = await self.repository.get_by_email(data.email)

        if not user:
            raise ValueError("Invalid email or password")

        if not verify_password(
            data.password,
            user.hashed_password,
        ):
            raise ValueError("Invalid email or password")

        return create_access_token(str(user.id))