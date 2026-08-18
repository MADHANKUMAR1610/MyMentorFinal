from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.course import Course
from app.repositories.base import BaseRepository


class CourseRepository(BaseRepository[Course]):
    """
    Repository responsible for Course database operations.

    Business rules belong in the service layer.
    """

    def __init__(self, session: AsyncSession):
        super().__init__(Course, session)

    async def get_by_title(
        self,
        title: str,
    ) -> Optional[Course]:
        """
        Get a course by title.
        """

        result = await self.session.execute(
            select(Course).where(
                Course.title == title
            )
        )

        return result.scalar_one_or_none()

    async def get_by_status(
        self,
        status: str,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Course]:
        """
        Get courses by status.
        """

        result = await self.session.execute(
            select(Course)
            .where(Course.status == status)
            .order_by(Course.created_at.desc())
            .offset(skip)
            .limit(limit)
        )

        return list(result.scalars().all())

    async def get_published(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Course]:
        """
        Get published courses.
        """

        result = await self.session.execute(
            select(Course)
            .where(Course.status == "published")
            .order_by(Course.created_at.desc())
            .offset(skip)
            .limit(limit)
        )

        return list(result.scalars().all())

    async def get_by_language(
        self,
        language: str,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Course]:
        """
        Get courses by language.
        """

        result = await self.session.execute(
            select(Course)
            .where(Course.language == language)
            .order_by(Course.created_at.desc())
            .offset(skip)
            .limit(limit)
        )

        return list(result.scalars().all())

    async def get_by_difficulty(
        self,
        difficulty: str,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Course]:
        """
        Get courses by difficulty.
        """

        result = await self.session.execute(
            select(Course)
            .where(Course.difficulty == difficulty)
            .order_by(Course.created_at.desc())
            .offset(skip)
            .limit(limit)
        )

        return list(result.scalars().all())