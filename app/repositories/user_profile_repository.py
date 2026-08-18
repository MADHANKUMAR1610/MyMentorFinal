from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user_profile import UserProfile
from app.repositories.base import BaseRepository


class UserProfileRepository(BaseRepository[UserProfile]):
    """
    Repository responsible for UserProfile database operations.

    Business logic belongs in the service layer.
    """

    def __init__(self, session: AsyncSession):
        super().__init__(UserProfile, session)

    async def get_by_user_id(
        self,
        user_id: UUID,
    ) -> Optional[UserProfile]:
        result = await self.session.execute(
            select(UserProfile).where(
                UserProfile.user_id == user_id
            )
        )

        return result.scalar_one_or_none()

    async def get_by_career_goal(
        self,
        career_goal: str,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[UserProfile]:
        result = await self.session.execute(
            select(UserProfile)
            .where(
                UserProfile.career_goal == career_goal
            )
            .offset(skip)
            .limit(limit)
        )

        return list(result.scalars().all())

    async def get_by_profile_category(
        self,
        profile_category: str,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[UserProfile]:
        result = await self.session.execute(
            select(UserProfile)
            .where(
                UserProfile.profile_category == profile_category
            )
            .offset(skip)
            .limit(limit)
        )

        return list(result.scalars().all())