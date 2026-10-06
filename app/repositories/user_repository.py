from typing import Optional
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.progress import Progress
from app.models.course_enrollment import CourseEnrollment
from app.models.college import College

from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):

    def __init__(
        self,
        session: AsyncSession,
    ):
        super().__init__(
            User,
            session
        )

    # =========================================================
    # GET USER BY EMAIL
    # =========================================================

    async def get_by_email(
        self,
        email: str,
    ) -> Optional[User]:

        result = await self.session.execute(
            select(User).where(
                User.email == email
            )
        )

        return result.scalar_one_or_none()

    # =========================================================
    # GET USER BY PHONE
    # =========================================================

    async def get_by_phone(
        self,
        phone: str,
    ) -> Optional[User]:

        result = await self.session.execute(
            select(User).where(
                User.phone == phone
            )
        )

        return result.scalar_one_or_none()

    # =========================================================
    # GET USER BY GOOGLE ID
    # =========================================================

    async def get_by_google_id(
        self,
        google_id: str,
    ) -> Optional[User]:

        result = await self.session.execute(
            select(User).where(
                User.google_id == google_id
            )
        )

        return result.scalar_one_or_none()

    # =========================================================
    # GET STUDENTS WITH PROGRESS
    # =========================================================

    async def get_students_with_progress(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
    ):

        result = await self.session.execute(
            select(
                User,

                # ---------------------------------------------
                # COLLEGE DETAILS
                # ---------------------------------------------

                College.id.label(
                    "college_id"
                ),

                College.name.label(
                    "college_name"
                ),

                College.code.label(
                    "college_code"
                ),

                # ---------------------------------------------
                # COMPLETED LEVELS
                # ---------------------------------------------

                func.count(
                    func.distinct(
                        Progress.level_id
                    )
                )
                .filter(
                    Progress.completed.is_(True)
                )
                .label(
                    "completed_levels"
                ),

                # ---------------------------------------------
                # ENROLLED COURSES
                # ---------------------------------------------

                func.count(
                    func.distinct(
                        CourseEnrollment.course_id
                    )
                )
                .label(
                    "enrolled_courses"
                ),
            )

            # ---------------------------------------------
            # PROGRESS
            # ---------------------------------------------

            .outerjoin(
                Progress,
                Progress.user_id == User.id,
            )

            # ---------------------------------------------
            # COURSE ENROLLMENTS
            # ---------------------------------------------

            .outerjoin(
                CourseEnrollment,
                CourseEnrollment.user_id == User.id,
            )

            # ---------------------------------------------
            # COLLEGE
            # ---------------------------------------------

            .outerjoin(
                College,
                College.id == User.college_id,
            )

            .where(
                User.role == "student"
            )

            .group_by(
                User.id,
                College.id,
                College.name,
                College.code,
            )

            .order_by(
                User.created_at.desc()
            )

            .offset(skip)
            .limit(limit)
        )

        return result.all()

    # =========================================================
    # GET STUDENT STREAK
    # =========================================================

    async def get_student_streak(
        self,
        user_id: UUID,
    ) -> int:
        """
        Get the student's current learning streak.

        The streak is stored directly on the User model.

        User.streak:
            Current consecutive learning days.

        User.last_active:
            Last successful learning activity date.

        The streak is updated by:
            - Successful checkpoint completion
            - Complete MCQ level
            - Video completion

        Login does NOT update the learning streak.
        """

        result = await self.session.execute(
            select(
                User.streak
            )
            .where(
                User.id == user_id
            )
        )

        streak = result.scalar_one_or_none()

        if streak is None:
            return 0

        return int(
            streak or 0
        )

    # =========================================================
    # GET USER BY STUDENT CODE
    # =========================================================

    async def get_by_student_code(
        self,
        student_code: str,
    ) -> User | None:

        result = await self.session.execute(
            select(User).where(
                User.student_code == student_code
            )
        )

        return result.scalar_one_or_none()

    # =========================================================
    # GET STUDENTS BY COLLEGE
    # =========================================================

    async def get_students_by_college(
        self,
        college_id: UUID,
    ) -> list[User]:

        result = await self.session.execute(
            select(User)
            .where(
                User.college_id == college_id,
                User.role == "student",
            )
            .order_by(
                User.created_at.asc()
            )
        )

        return list(
            result.scalars().all()
        )