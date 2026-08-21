from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user_profile import UserProfile
from app.repositories.user_profile_repository import UserProfileRepository


class UserProfileService:

    def __init__(self, session: AsyncSession):
        self.repository = UserProfileRepository(session)

    async def get_by_id(
        self,
        profile_id: UUID,
    ) -> UserProfile | None:

        return await self.repository.get_by_id(profile_id)

    async def get_by_user_id(
        self,
        user_id: UUID,
    ) -> UserProfile | None:

        return await self.repository.get_by_user_id(user_id)

    async def get_by_profile_category(
        self,
        profile_category: str,
    ) -> list[UserProfile]:

        return await self.repository.get_by_profile_category(
            profile_category
        )

    async def create_profile(
        self,
        profile: UserProfile,
    ) -> UserProfile:

        return await self.repository.create(profile)

    async def update_profile(
        self,
        profile: UserProfile,
    ) -> UserProfile:

        return await self.repository.update(profile)

    async def delete_profile(
        self,
        profile: UserProfile,
    ) -> None:

        await self.repository.delete(profile)