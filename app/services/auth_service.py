from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate


class AuthService:
    """
    Service responsible for authentication operations.

    Business logic belongs here.
    Database operations belong in the repository layer.
    """

    def __init__(self, session: AsyncSession):
        self.repository = UserRepository(session)

    async def register(
        self,
        data: UserCreate,
    ) -> User:

        existing_email = await self.repository.get_by_email(
            data.email
        )

        if existing_email is not None:
            raise ValueError(
                "A user with this email already exists."
            )

        user = User(
            name=data.name,
            email=data.email,
            password_hash=hash_password(data.password),
        )

        return await self.repository.create(user)

    async def authenticate(
        self,
        email: str,
        password: str,
    ) -> User | None:

        user = await self.repository.get_by_email(email)

        if user is None:
            return None

        if not user.password_hash:
            return None

        if not verify_password(
            password,
            user.password_hash,
        ):
            return None

        if not user.is_active:
            return None

        return user

    def create_token(
        self,
        user: User,
    ) -> str:

        return create_access_token(user.id)