from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.level import Level
from app.repositories.base import BaseRepository


class LevelRepository(BaseRepository[Level]):
    """
    Repository responsible for Level database operations.

    Business rules belong in the service layer.
    """

    def __init__(self, session: AsyncSession):
        super().__init__(Level, session)

    async def get_by_course_id(
        self,
        course_id: UUID,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Level]:
        """
        Get levels belonging to a course.
        """

        result = await self.session.execute(
            select(Level)
            .where(Level.course_id == course_id)
            .order_by(Level.global_order.asc())
            .offset(skip)
            .limit(limit)
        )

        return list(result.scalars().all())

    async def get_by_course_and_level_number(
        self,
        course_id: UUID,
        level_number: int,
    ) -> Optional[Level]:
        """
        Get a specific level within a course.
        """

        result = await self.session.execute(
            select(Level).where(
                Level.course_id == course_id,
                Level.level_number == level_number,
            )
        )

        return result.scalar_one_or_none()

    async def get_by_stage(
        self,
        stage: str,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Level]:
        """
        Get levels belonging to a specific stage.
        """

        result = await self.session.execute(
            select(Level)
            .where(Level.stage == stage)
            .order_by(Level.global_order.asc())
            .offset(skip)
            .limit(limit)
        )

        return list(result.scalars().all())

    async def get_by_global_order(
        self,
        global_order: int,
    ) -> Optional[Level]:
        """
        Get a level using its global order.
        """

        result = await self.session.execute(
            select(Level).where(
                Level.global_order == global_order
            )
        )

        return result.scalar_one_or_none()