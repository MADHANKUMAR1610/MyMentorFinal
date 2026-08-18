from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.mentor import Mentor
from app.repositories.base import BaseRepository


class MentorRepository(BaseRepository[Mentor]):
    """
    Repository responsible for Mentor database operations.

    Business rules belong in the service layer.
    """

    def __init__(self, session: AsyncSession):
        super().__init__(Mentor, session)

    async def get_by_id(
        self,
        mentor_id: UUID,
    ) -> Optional[Mentor]:
        """
        Get a mentor by ID.
        """

        result = await self.session.execute(
            select(Mentor).where(
                Mentor.id == mentor_id
            )
        )

        return result.scalar_one_or_none()

    async def get_by_industry(
        self,
        industry: str,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Mentor]:
        """
        Get mentors belonging to an industry.
        """

        result = await self.session.execute(
            select(Mentor)
            .where(
                Mentor.industry == industry
            )
            .offset(skip)
            .limit(limit)
        )

        return list(result.scalars().all())

    async def get_by_status(
        self,
        status: str,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Mentor]:
        """
        Get mentors by status.
        """

        result = await self.session.execute(
            select(Mentor)
            .where(
                Mentor.status == status
            )
            .offset(skip)
            .limit(limit)
        )

        return list(result.scalars().all())

    async def get_verified(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Mentor]:
        """
        Get verified mentors.
        """

        result = await self.session.execute(
            select(Mentor)
            .where(
                Mentor.verified.is_(True)
            )
            .offset(skip)
            .limit(limit)
        )

        return list(result.scalars().all())

    async def get_by_role(
        self,
        role: str,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Mentor]:
        """
        Get mentors by professional role.
        """

        result = await self.session.execute(
            select(Mentor)
            .where(
                Mentor.role == role
            )
            .offset(skip)
            .limit(limit)
        )

        return list(result.scalars().all())