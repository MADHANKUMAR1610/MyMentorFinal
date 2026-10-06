from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import func, select, distinct, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.college import College
from app.models.course import Course
from app.models.level import Level
from app.models.checkpoint import Checkpoint
from app.models.progress import Progress
from app.models.course_enrollment import CourseEnrollment
from app.models.college_package import CollegePackage
from app.models.college_package_course import CollegePackageCourse


class CollegeAdminRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    # ========================================================
    # ASSIGNED COURSE IDS
    # ========================================================

    def assigned_course_ids_query(
        self,
        college_id: UUID,
    ):
        return (
            select(
                CollegePackageCourse.course_id
            )
            .join(
                CollegePackage,
                CollegePackage.id
                == CollegePackageCourse.package_id,
            )
            .where(
                CollegePackage.college_id
                == college_id
            )
        )

    # ========================================================
    # DASHBOARD - STUDENTS
    # ========================================================

    async def get_total_students(
        self,
        college_id: UUID,
    ) -> int:

        result = await self.session.execute(
            select(
                func.count(User.id)
            )
            .where(
                User.college_id == college_id,
                User.role == "student",
            )
        )

        return result.scalar_one()

    async def get_active_students(
        self,
        college_id: UUID,
    ) -> int:

        result = await self.session.execute(
            select(
                func.count(User.id)
            )
            .where(
                User.college_id == college_id,
                User.role == "student",
                User.is_active.is_(True),
            )
        )

        return result.scalar_one()

    # ========================================================
    # ASSIGNED COURSES
    # ========================================================

    async def get_assigned_courses(
        self,
        college_id: UUID,
        search: str | None = None,
        skip: int = 0,
        limit: int = 100,
    ):

        level_count = (
            select(
                func.count(Level.id)
            )
            .where(
                Level.course_id == Course.id
            )
            .correlate(Course)
            .scalar_subquery()
        )

        enrollment_count = (
            select(
                func.count(
                    distinct(
                        CourseEnrollment.user_id
                    )
                )
            )
            .join(
                User,
                User.id
                == CourseEnrollment.user_id,
            )
            .where(
                CourseEnrollment.course_id
                == Course.id,
                User.college_id == college_id,
                User.role == "student",
            )
            .correlate(Course)
            .scalar_subquery()
        )

        completed_count = (
            select(
                func.count(Progress.id)
            )
            .join(
                User,
                User.id == Progress.user_id,
            )
            .where(
                Progress.course_id == Course.id,
                Progress.completed.is_(True),
                User.college_id == college_id,
                User.role == "student",
            )
            .correlate(Course)
            .scalar_subquery()
        )

        query = (
            select(
                Course,
                level_count.label(
                    "level_count"
                ),
                enrollment_count.label(
                    "enrollment_count"
                ),
                completed_count.label(
                    "completed_count"
                ),
            )
            .where(
                Course.id.in_(
                    self.assigned_course_ids_query(
                        college_id
                    )
                )
            )
        )

        if search:
            pattern = f"%{search.strip()}%"

            query = query.where(
                or_(
                    Course.title.ilike(pattern),
                    Course.category.ilike(pattern),
                    Course.language.ilike(pattern),
                )
            )

        query = (
            query
            .order_by(
                Course.created_at.desc()
            )
            .offset(skip)
            .limit(limit)
        )

        result = await self.session.execute(
            query
        )

        return result.all()

    # ========================================================
    # RECENTLY ACTIVE STUDENTS
    # ========================================================

    async def get_recently_active_students(
        self,
        college_id: UUID,
        limit: int = 10,
    ):

        completed_levels = (
            select(
                func.count(
                    distinct(
                        Progress.level_id
                    )
                )
            )
            .where(
                Progress.user_id == User.id,
                Progress.completed.is_(True),
            )
            .correlate(User)
            .scalar_subquery()
        )

        result = await self.session.execute(
            select(
                User.id,
                User.name,
                User.email,
                User.student_code,
                User.xp,
                User.streak,
                completed_levels.label(
                    "levels"
                ),
            )
            .where(
                User.college_id == college_id,
                User.role == "student",
            )
            .order_by(
                User.updated_at.desc()
            )
            .limit(limit)
        )

        return result.all()

    # ========================================================
    # STUDENTS LIST
    # ========================================================

    async def get_students(
        self,
        college_id: UUID,
        search: str | None = None,
        skip: int = 0,
        limit: int = 100,
    ):

        course_count = (
            select(
                func.count(
                    distinct(
                        CourseEnrollment.course_id
                    )
                )
            )
            .where(
                CourseEnrollment.user_id
                == User.id
            )
            .correlate(User)
            .scalar_subquery()
        )

        level_count = (
            select(
                func.count(
                    distinct(
                        Progress.level_id
                    )
                )
            )
            .where(
                Progress.user_id == User.id,
                Progress.completed.is_(True),
            )
            .correlate(User)
            .scalar_subquery()
        )

        total_levels = (
            select(
                func.count(Level.id)
            )
            .join(
                CourseEnrollment,
                CourseEnrollment.course_id
                == Level.course_id,
            )
            .where(
                CourseEnrollment.user_id
                == User.id
            )
            .correlate(User)
            .scalar_subquery()
        )

        query = select(
            User,
            course_count.label(
                "course_count"
            ),
            level_count.label(
                "level_count"
            ),
            total_levels.label(
                "total_levels"
            ),
        ).where(
            User.college_id == college_id,
            User.role == "student",
        )

        if search:

            pattern = (
                f"%{search.strip()}%"
            )

            query = query.where(
                or_(
                    User.name.ilike(pattern),
                    User.email.ilike(pattern),
                    User.student_code.ilike(
                        pattern
                    ),
                )
            )

        query = (
            query
            .order_by(
                User.created_at.desc()
            )
            .offset(skip)
            .limit(limit)
        )

        result = await self.session.execute(
            query
        )

        return result.all()

    # ========================================================
    # STUDENT COUNT
    # ========================================================

    async def count_students(
        self,
        college_id: UUID,
        search: str | None = None,
    ) -> int:

        query = select(
            func.count(User.id)
        ).where(
            User.college_id == college_id,
            User.role == "student",
        )

        if search:

            pattern = (
                f"%{search.strip()}%"
            )

            query = query.where(
                or_(
                    User.name.ilike(pattern),
                    User.email.ilike(pattern),
                    User.student_code.ilike(
                        pattern
                    ),
                )
            )

        result = await self.session.execute(
            query
        )

        return result.scalar_one()

    # ========================================================
    # STUDENT BY ID
    # ========================================================

    async def get_student_by_id(
        self,
        college_id: UUID,
        student_id: UUID,
    ) -> User | None:

        result = await self.session.execute(
            select(User)
            .where(
                User.id == student_id,
                User.college_id == college_id,
                User.role == "student",
            )
        )

        return result.scalar_one_or_none()

    # ========================================================
    # WEEKLY ACTIVE
    # ========================================================

    async def get_active_this_week(
        self,
        college_id: UUID,
    ) -> int:

        start_date = (
            datetime.now(timezone.utc)
            - timedelta(days=7)
        )

        result = await self.session.execute(
            select(
                func.count(
                    distinct(
                        Progress.user_id
                    )
                )
            )
            .join(
                User,
                User.id == Progress.user_id,
            )
            .where(
                User.college_id == college_id,
                User.role == "student",
                Progress.updated_at
                >= start_date,
            )
        )

        return result.scalar_one()

    # ========================================================
    # COMPLETED LEVELS
    # ========================================================

    async def get_completed_levels(
        self,
        college_id: UUID,
    ) -> int:

        result = await self.session.execute(
            select(
                func.count(Progress.id)
            )
            .join(
                User,
                User.id == Progress.user_id,
            )
            .where(
                User.college_id == college_id,
                User.role == "student",
                Progress.completed.is_(True),
            )
        )

        return result.scalar_one()

    # ========================================================
    # LEARNING VIDEOS
    # ========================================================

    async def get_learning_videos(
        self,
        college_id: UUID,
    ) -> int:

        result = await self.session.execute(
            select(
                func.count(Level.id)
            )
            .where(
                Level.course_id.in_(
                    self.assigned_course_ids_query(
                        college_id
                    )
                ),
                Level.video.is_not(None),
            )
        )

        return result.scalar_one()

    # ========================================================
    # CODING CHALLENGES
    # ========================================================

    async def get_coding_challenges(
        self,
        college_id: UUID,
    ) -> int:

        result = await self.session.execute(
            select(
                func.count(Checkpoint.id)
            )
            .join(
                Level,
                Level.id
                == Checkpoint.level_id,
            )
            .where(
                Level.course_id.in_(
                    self.assigned_course_ids_query(
                        college_id
                    )
                )
            )
        )

        return result.scalar_one()