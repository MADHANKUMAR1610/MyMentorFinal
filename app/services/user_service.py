from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.user_repository import UserRepository


class UserService:

    def __init__(self, session: AsyncSession):
        self.repository = UserRepository(session)

    async def get_by_id(
        self,
        user_id: UUID,
    ) -> User | None:

        return await self.repository.get_by_id(user_id)

    async def get_by_email(
        self,
        email: str,
    ) -> User | None:

        return await self.repository.get_by_email(email)

    async def get_by_phone(
        self,
        phone: str,
    ) -> User | None:

        return await self.repository.get_by_phone(phone)

    async def create_user(
        self,
        user: User,
    ) -> User:

        return await self.repository.create(user)

    async def update_user(
        self,
        user: User,
    ) -> User:

        return await self.repository.update(user)

    async def delete_user(
        self,
        user: User,
    ) -> None:

        await self.repository.delete(user)