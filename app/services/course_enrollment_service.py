from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.course_enrollment import CourseEnrollment
from app.repositories.course_enrollment_repository import (
    CourseEnrollmentRepository,
)
from app.repositories.course_repository import CourseRepository


class CourseEnrollmentService:
    """
    Service responsible for course enrollment business logic.
    """

    def __init__(self, session: AsyncSession):

        self.enrollment_repository = (
            CourseEnrollmentRepository(session)
        )

        self.course_repository = CourseRepository(
            session
        )

    async def enroll_user(
        self,
        user_id: UUID,
        course_id: UUID,
    ) -> CourseEnrollment:

        # Check course
        course = await self.course_repository.get_by_id(
            course_id
        )

        if course is None:
            raise ValueError(
                "Course not found."
            )

        # Only published courses can be enrolled
        if course.status != "published":
            raise ValueError(
                "This course is not available for enrollment."
            )

        # Check existing enrollment
        existing = (
            await self.enrollment_repository
            .get_user_course_enrollment(
                user_id,
                course_id,
            )
        )

        if existing is not None:
            raise ValueError(
                "You are already enrolled in this course."
            )

        enrollment = CourseEnrollment(
            user_id=user_id,
            course_id=course_id,
            enrolled_at=datetime.now(timezone.utc),
        )

        return await self.enrollment_repository.create(
            enrollment
        )

    async def get_my_enrollments(
        self,
        user_id: UUID,
    ):

        return await (
            self.enrollment_repository
            .get_user_enrollments_with_courses(
                user_id
            )
        )