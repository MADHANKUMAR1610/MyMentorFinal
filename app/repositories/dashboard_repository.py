from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.college_package import CollegePackage
from app.models.college_package_course import CollegePackageCourse
from app.models.checkpoint import Checkpoint
from app.models.course import Course
from app.models.level import Level
from app.models.progress import Progress
from app.models.user import User
from app.models.course_enrollment import CourseEnrollment


class DashboardRepository:

    def __init__(
        self,
        session: AsyncSession,
    ):
        self.session = session

    # ========================================================
    # ADMIN DASHBOARD
    # ========================================================

    async def get_total_students(
        self,
    ) -> int:

        result = await self.session.execute(
            select(func.count(User.id))
            .where(
                User.role == "student"
            )
        )

        return result.scalar_one()

    # ========================================================

    async def get_active_students(
        self,
    ) -> int:

        result = await self.session.execute(
            select(func.count(User.id))
            .where(
                User.role == "student",
                User.is_active.is_(True),
            )
        )

        return result.scalar_one()

    # ========================================================

    async def get_total_courses(
        self,
    ) -> int:

        result = await self.session.execute(
            select(func.count(Course.id))
        )

        return result.scalar_one()

    # ========================================================

    async def get_total_levels(
        self,
    ) -> int:

        result = await self.session.execute(
            select(func.count(Level.id))
        )

        return result.scalar_one()

    # ========================================================

    async def get_total_videos(
        self,
    ) -> int:

        result = await self.session.execute(
            select(func.count(Level.id))
            .where(
                Level.video.is_not(None)
            )
        )

        return result.scalar_one()

    # ========================================================

    async def get_total_coding_challenges(
        self,
    ) -> int:

        result = await self.session.execute(
            select(func.count(Checkpoint.id))
        )

        return result.scalar_one()

    # ========================================================

    async def get_completed_levels(
        self,
    ) -> int:

        result = await self.session.execute(
            select(func.count(Progress.id))
            .where(
                Progress.completed.is_(True)
            )
        )

        return result.scalar_one()

    # ========================================================
    # DAILY ACTIVE
    # ========================================================

    async def get_daily_active_students(
        self,
    ) -> int:

        now = datetime.now(timezone.utc)

        start_of_day = now.replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
        )

        result = await self.session.execute(
            select(
                func.count(
                    func.distinct(
                        Progress.user_id
                    )
                )
            )
            .where(
                Progress.updated_at >= start_of_day
            )
        )

        return result.scalar_one()

    # ========================================================
    # MONTHLY ACTIVE
    # ========================================================

    async def get_monthly_active_students(
        self,
    ) -> int:

        now = datetime.now(timezone.utc)

        start_of_month = now.replace(
            day=1,
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
        )

        result = await self.session.execute(
            select(
                func.count(
                    func.distinct(
                        Progress.user_id
                    )
                )
            )
            .where(
                Progress.updated_at >= start_of_month
            )
        )

        return result.scalar_one()

    # ========================================================
    # LEARNING HOURS
    # ========================================================

    async def get_learning_hours(
        self,
    ) -> float:

        return 0.0

    # ========================================================
    # RECENTLY ACTIVE STUDENTS
    # ========================================================

    async def get_recently_active_students(
        self,
        limit: int = 10,
    ):

        result = await self.session.execute(
            select(
                User.id,
                User.name,
                User.email,
                User.xp,

                func.count(
                    func.distinct(
                        Progress.level_id
                    )
                )
                .filter(
                    Progress.completed.is_(True)
                )
                .label("levels"),
            )
            .outerjoin(
                Progress,
                Progress.user_id == User.id,
            )
            .where(
                User.role == "student"
            )
            .group_by(
                User.id,
                User.name,
                User.email,
                User.xp,
            )
            .order_by(
                User.updated_at.desc()
            )
            .limit(limit)
        )

        rows = result.all()

        students = []

        for row in rows:

            streak = await self.get_student_streak(
                row.id
            )

            students.append(
                {
                    "id": row.id,
                    "name": row.name,
                    "email": row.email,
                    "xp": row.xp or 0,
                    "streak": streak,
                    "levels": row.levels or 0,
                }
            )

        return students

    # ========================================================
    # STUDENT DASHBOARD
    # ========================================================

    async def get_student_courses(
        self,
        user_id,
    ):
        """
        Get all courses enrolled by the student
        with real-time level progress.
        """

        result = await self.session.execute(
            select(
                Course.id,
                Course.title,
                Course.difficulty,

                func.min(
                    Level.stage
                ).label("stage"),

                func.count(
                    func.distinct(
                        Level.id
                    )
                ).label("total_levels"),

                func.count(
                    func.distinct(
                        Progress.level_id
                    )
                )
                .filter(
                    Progress.completed.is_(True)
                )
                .label("completed_levels"),
            )
            .join(
                CourseEnrollment,
                CourseEnrollment.course_id
                == Course.id,
            )
            .outerjoin(
                Level,
                Level.course_id == Course.id,
            )
            .outerjoin(
                Progress,
                (
                    Progress.level_id == Level.id
                )
                & (
                    Progress.user_id == user_id
                ),
            )
            .where(
                CourseEnrollment.user_id
                == user_id,
            )
            .group_by(
                Course.id,
                Course.title,
                Course.difficulty,
            )
            .order_by(
                Course.created_at.desc()
            )
        )

        return result.all()

    # ========================================================
    # STUDENT USER
    # ========================================================

    async def get_student_user(
        self,
        user_id,
    ):

        result = await self.session.execute(
            select(User)
            .where(
                User.id == user_id
            )
        )

        return result.scalar_one_or_none()

    # ========================================================
    # STUDENT COMPLETED COURSES
    # ========================================================

    async def get_student_completed_courses(
        self,
        user_id,
    ):

        result = await self.session.execute(
            select(
                Course.title
            )
            .join(
                Level,
                Level.course_id == Course.id,
            )
            .join(
                Progress,
                Progress.level_id == Level.id,
            )
            .where(
                Progress.user_id == user_id,
                Progress.completed.is_(True),
            )
            .group_by(
                Course.id,
                Course.title,
            )
            .having(
                func.count(
                    func.distinct(
                        Level.id
                    )
                )
                ==
                func.count(
                    func.distinct(
                        Progress.level_id
                    )
                )
            )
        )

        return [
            row[0]
            for row in result.all()
        ]

    # ========================================================
    # STUDENT STREAK
    # ========================================================

    async def get_student_streak(
        self,
        user_id,
    ) -> int:
        """
        Get the user's current learning streak.

        The streak is maintained on User.streak.

        Login does NOT update the streak.
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

    # ========================================================
    # COLLEGE PACKAGES WITH COURSES
    # ========================================================

    async def get_student_college_packages(
        self,
        user_id,
    ):
        """
        Get college packages for the student's college,
        including all courses assigned to each package.
        """

        result = await self.session.execute(
            select(
                CollegePackage.id.label(
                    "package_id"
                ),

                CollegePackage.package_name.label(
                    "package_name"
                ),

                CollegePackage.description.label(
                    "package_description"
                ),

                Course.id.label(
                    "course_id"
                ),

                Course.title.label(
                    "course_title"
                ),

                Course.description.label(
                    "course_description"
                ),

                Course.language.label(
                    "course_language"
                ),

                Course.difficulty.label(
                    "course_difficulty"
                ),

                Course.duration.label(
                    "course_duration"
                ),

                Course.thumbnail.label(
                    "course_thumbnail"
                ),

                Course.status.label(
                    "course_status"
                ),
            )
            .join(
                User,
                User.college_id
                == CollegePackage.college_id,
            )
            .join(
                CollegePackageCourse,
                CollegePackageCourse.package_id
                == CollegePackage.id,
            )
            .join(
                Course,
                Course.id
                == CollegePackageCourse.course_id,
            )
            .where(
                User.id == user_id
            )
            .order_by(
                CollegePackage.created_at.desc(),
                Course.created_at.asc(),
            )
        )

        return result.mappings().all()