from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.mentor_application import MentorApplication
from app.repositories.base import BaseRepository


class MentorApplicationRepository(BaseRepository[MentorApplication]):
    """
    Repository responsible for MentorApplication database operations.

    Business rules belong in the service layer.
    """

    def __init__(self, session: AsyncSession):
        super().__init__(MentorApplication, session)

    async def get_by_email(
        self,
        email: str,
    ) -> Optional[MentorApplication]:
        """
        Get a mentor application by email.
        """

        result = await self.session.execute(
            select(MentorApplication).where(
                MentorApplication.email == email
            )
        )

        return result.scalar_one_or_none()

    async def get_by_status(
        self,
        status: str,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[MentorApplication]:
        """
        Get mentor applications by status.
        """

        result = await self.session.execute(
            select(MentorApplication)
            .where(
                MentorApplication.status == status
            )
            .offset(skip)
            .limit(limit)
        )

        return list(result.scalars().all())

    async def get_by_industry(
        self,
        industry: str,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[MentorApplication]:
        """
        Get mentor applications by industry.
        """

        result = await self.session.execute(
            select(MentorApplication)
            .where(
                MentorApplication.industry == industry
            )
            .offset(skip)
            .limit(limit)
        )

        return list(result.scalars().all())

    async def get_pending(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[MentorApplication]:
        """
        Get applications waiting for review.
        """

        result = await self.session.execute(
            select(MentorApplication)
            .where(
                MentorApplication.status == "pending"
            )
            .offset(skip)
            .limit(limit)
        )

        return list(result.scalars().all())