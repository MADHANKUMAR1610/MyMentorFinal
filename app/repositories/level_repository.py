from typing import Optional
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.level import Level
from app.models.checkpoint import Checkpoint
from app.repositories.base import BaseRepository


class LevelRepository(BaseRepository[Level]):

    def __init__(self, session: AsyncSession):
        super().__init__(Level, session)

    async def get_by_course_id(
        self,
        course_id: UUID,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Level]:

        result = await self.session.execute(
            select(Level)
            .where(
                Level.course_id == course_id
            )
            .order_by(
                Level.global_order.asc()
            )
            .offset(skip)
            .limit(limit)
        )

        return list(
            result.scalars().all()
        )

    async def get_by_course_and_level_number(
        self,
        course_id: UUID,
        level_number: int,
    ) -> Optional[Level]:

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

        result = await self.session.execute(
            select(Level)
            .where(
                Level.stage == stage
            )
            .order_by(
                Level.global_order.asc()
            )
            .offset(skip)
            .limit(limit)
        )

        return list(
            result.scalars().all()
        )

    async def get_by_global_order(
        self,
        global_order: int,
    ) -> Optional[Level]:

        result = await self.session.execute(
            select(Level).where(
                Level.global_order == global_order
            )
        )

        return result.scalar_one_or_none()

    async def get_levels_with_checkpoint_count(
        self,
        course_id: UUID,
        *,
        skip: int = 0,
        limit: int = 100,
    ):

        result = await self.session.execute(
            select(
                Level.id,
                Level.course_id,
                Level.stage,
                Level.stage_order,
                Level.level_number,
                func.count(
                    Checkpoint.id
                ).label(
                    "checkpoint_count"
                ),
            )
            .outerjoin(
                Checkpoint,
                Checkpoint.level_id == Level.id,
            )
            .where(
                Level.course_id == course_id
            )
            .group_by(
                Level.id,
                Level.course_id,
                Level.stage,
                Level.stage_order,
                Level.level_number,
            )
            .order_by(
                Level.stage_order.asc(),
                Level.level_number.asc(),
            )
            .offset(skip)
            .limit(limit)
        )

        return result.all()