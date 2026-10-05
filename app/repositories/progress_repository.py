from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.progress import Progress
from app.repositories.base import BaseRepository


class ProgressRepository(BaseRepository[Progress]):
    """
    Repository responsible for Progress database operations.

    Business rules belong in the service layer.
    """

    def __init__(self, session: AsyncSession):
        super().__init__(Progress, session)

    # ============================================================
    # GET BY USER ID
    # ============================================================

    async def get_by_user_id(
        self,
        user_id: UUID,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Progress]:

        result = await self.session.execute(
            select(Progress)
            .where(
                Progress.user_id == user_id
            )
            .order_by(
                Progress.created_at.desc()
            )
            .offset(skip)
            .limit(limit)
        )

        return list(result.scalars().all())

    # ============================================================
    # GET BY COURSE ID
    # ============================================================

    async def get_by_course_id(
        self,
        course_id: UUID,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Progress]:

        result = await self.session.execute(
            select(Progress)
            .where(
                Progress.course_id == course_id
            )
            .order_by(
                Progress.created_at.desc()
            )
            .offset(skip)
            .limit(limit)
        )

        return list(result.scalars().all())

    # ============================================================
    # GET BY LEVEL ID
    # ============================================================

    async def get_by_level_id(
        self,
        level_id: UUID,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Progress]:

        result = await self.session.execute(
            select(Progress)
            .where(
                Progress.level_id == level_id
            )
            .order_by(
                Progress.created_at.desc()
            )
            .offset(skip)
            .limit(limit)
        )

        return list(result.scalars().all())

    # ============================================================
    # GET USER LEVEL PROGRESS
    # ============================================================

    async def get_user_level_progress(
        self,
        user_id: UUID,
        level_id: UUID,
    ) -> Optional[Progress]:

        result = await self.session.execute(
            select(Progress).where(
                Progress.user_id == user_id,
                Progress.level_id == level_id,
            )
        )

        return result.scalar_one_or_none()

    # ============================================================
    # GET COMPLETED PROGRESS
    # ============================================================

    async def get_completed_for_user(
        self,
        user_id: UUID,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Progress]:

        result = await self.session.execute(
            select(Progress)
            .where(
                Progress.user_id == user_id,
                Progress.completed.is_(True),
            )
            .order_by(
                Progress.created_at.desc()
            )
            .offset(skip)
            .limit(limit)
        )

        return list(result.scalars().all())

    # ============================================================
    # GET INCOMPLETE PROGRESS
    # ============================================================

    async def get_incomplete_for_user(
        self,
        user_id: UUID,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Progress]:

        result = await self.session.execute(
            select(Progress)
            .where(
                Progress.user_id == user_id,
                Progress.completed.is_(False),
            )
            .order_by(
                Progress.created_at.asc()
            )
            .offset(skip)
            .limit(limit)
        )

        return list(result.scalars().all())