from typing import Optional
from uuid import UUID

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.course import Course
from app.models.course_enrollment import CourseEnrollment
from app.repositories.base import BaseRepository


class CourseRepository(BaseRepository[Course]):
    """
    Repository responsible for Course database operations.

    Business rules belong in the service layer.
    """

    def __init__(self, session: AsyncSession):
        super().__init__(Course, session)

    # =========================================================
    # GET BY TITLE
    # =========================================================

    async def get_by_title(
        self,
        title: str,
    ) -> Optional[Course]:

        result = await self.session.execute(
            select(Course).where(
                Course.title == title
            )
        )

        return result.scalar_one_or_none()

    # =========================================================
    # GET BY STATUS
    # =========================================================

    async def get_by_status(
        self,
        status: str,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Course]:

        result = await self.session.execute(
            select(Course)
            .where(
                Course.status == status
            )
            .order_by(
                Course.created_at.desc()
            )
            .offset(skip)
            .limit(limit)
        )

        return list(
            result.scalars().all()
        )

    # =========================================================
    # GET PUBLISHED COURSES
    # =========================================================

    async def get_published(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Course]:

        result = await self.session.execute(
            select(Course)
            .where(
                Course.status == "published"
            )
            .order_by(
                Course.created_at.desc()
            )
            .offset(skip)
            .limit(limit)
        )

        return list(
            result.scalars().all()
        )

    # =========================================================
    # GET BY LANGUAGE
    # =========================================================

    async def get_by_language(
        self,
        language: str,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Course]:

        result = await self.session.execute(
            select(Course)
            .where(
                Course.language == language
            )
            .order_by(
                Course.created_at.desc()
            )
            .offset(skip)
            .limit(limit)
        )

        return list(
            result.scalars().all()
        )

    # =========================================================
    # GET BY DIFFICULTY
    # =========================================================

    async def get_courses_for_career_goal(
        self,
        keywords: list[str],
        user_id: UUID,
        *,
        limit: int = 20,
    ) -> list[tuple[Course, bool]]:
        """
        Get published courses matching career keywords.

        Returns:
            (Course, already_enrolled)
        """

        conditions = []

        for keyword in keywords:
            keyword = keyword.strip().lower()

            if not keyword:
                continue

            pattern = f"%{keyword}%"

            conditions.extend(
                [
                    Course.title.ilike(pattern),
                    Course.description.ilike(pattern),
                    Course.language.ilike(pattern),
                ]
            )

        if not conditions:
            return []

        result = await self.session.execute(
            select(
                Course,
                CourseEnrollment.id.is_not(None),
            )
            .outerjoin(
                CourseEnrollment,
                (
                    CourseEnrollment.course_id == Course.id
                )
                & (
                    CourseEnrollment.user_id == user_id
                ),
            )
            .where(
                Course.status == "published",
                or_(*conditions),
            )
            .order_by(
                Course.created_at.desc()
            )
            .limit(limit)
        )

        return list(result.all())
    # =========================================================
    # GENERIC COURSE SUGGESTIONS
    # =========================================================

    async def get_suggestions(
        self,
        keywords: list[str],
        *,
        skip: int = 0,
        limit: int = 20,
    ) -> list[Course]:
        """
        Get published courses matching
        one or more keywords.
        """

        conditions = []

        for keyword in keywords:

            keyword = keyword.strip().lower()

            if not keyword:
                continue

            pattern = f"%{keyword}%"

            conditions.extend(
                [
                    Course.title.ilike(pattern),
                    Course.description.ilike(pattern),
                    Course.language.ilike(pattern),
                ]
            )

        if not conditions:
            return []

        result = await self.session.execute(
            select(Course)
            .where(
                Course.status == "published",
                or_(*conditions),
            )
            .order_by(
                Course.created_at.desc()
            )
            .offset(skip)
            .limit(limit)
        )

        return list(
            result.scalars().all()
        )