from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.course import Course
from app.models.course_enrollment import CourseEnrollment
from app.repositories.base import BaseRepository


class CourseEnrollmentRepository(
    BaseRepository[CourseEnrollment]
):
    """
    Repository responsible for course enrollment database operations.
    """

    def __init__(self, session: AsyncSession):
        super().__init__(
            CourseEnrollment,
            session,
        )

    async def get_user_course_enrollment(
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

    async def get_user_enrollments(
        self,
        user_id: UUID,
    ) -> list[CourseEnrollment]:

        result = await self.session.execute(
            select(CourseEnrollment)
            .where(
                CourseEnrollment.user_id == user_id
            )
            .order_by(
                CourseEnrollment.enrolled_at.desc()
            )
        )

        return list(result.scalars().all())

    async def get_user_enrollments_with_courses(
        self,
        user_id: UUID,
    ):
        result = await self.session.execute(
            select(
                CourseEnrollment,
                Course,
            )
            .join(
                Course,
                Course.id == CourseEnrollment.course_id,
            )
            .where(
                CourseEnrollment.user_id == user_id
            )
            .order_by(
                CourseEnrollment.enrolled_at.desc()
            )
        )

        return result.all()