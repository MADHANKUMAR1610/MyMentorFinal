from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.checkpoint import Checkpoint
from app.models.course import Course
from app.models.course_enrollment import CourseEnrollment
from app.models.level import Level
from app.models.progress import Progress


class CourseJourneyRepository:
    """
    Repository for Course Journey database operations.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_course(
        self,
        course_id: UUID,
    ) -> Course | None:

        result = await self.session.execute(
            select(Course).where(
                Course.id == course_id
            )
        )

        return result.scalar_one_or_none()

    async def get_user_enrollment(
        self,
        user_id: UUID,
        course_id: UUID,
    ) -> CourseEnrollment | None:

        result = await self.session.execute(
            select(CourseEnrollment).where(
                CourseEnrollment.user_id == user_id,
                CourseEnrollment.course_id == course_id,
            )
        )

        return result.scalar_one_or_none()

    async def get_course_levels(
        self,
        course_id: UUID,
    ) -> list[Level]:

        result = await self.session.execute(
            select(Level)
            .where(
                Level.course_id == course_id
            )
            .order_by(
                Level.global_order.asc()
            )
        )

        return list(result.scalars().all())

    async def get_level_checkpoints(
        self,
        level_id: UUID,
    ) -> list[Checkpoint]:

        result = await self.session.execute(
            select(Checkpoint)
            .where(
                Checkpoint.level_id == level_id
            )
            .order_by(
                Checkpoint.checkpoint_order.asc()
            )
        )

        return list(result.scalars().all())

    async def get_user_progress(
        self,
        user_id: UUID,
        course_id: UUID,
    ) -> list[Progress]:

        result = await self.session.execute(
            select(Progress)
            .where(
                Progress.user_id == user_id,
                Progress.course_id == course_id,
            )
        )

        return list(result.scalars().all())