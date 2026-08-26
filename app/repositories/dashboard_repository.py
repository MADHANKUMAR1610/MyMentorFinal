from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.checkpoint import Checkpoint
from app.models.course import Course
from app.models.level import Level
from app.models.progress import Progress
from app.models.user import User


class DashboardRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    # ========================================================
    # ADMIN DASHBOARD
    # ========================================================

    async def get_total_students(self) -> int:

        result = await self.session.execute(
            select(func.count(User.id))
            .where(User.role == "student")
        )

        return result.scalar_one()

    async def get_active_students(self) -> int:

        result = await self.session.execute(
            select(func.count(User.id))
            .where(
                User.role == "student",
                User.is_active.is_(True),
            )
        )

        return result.scalar_one()

    async def get_total_courses(self) -> int:

        result = await self.session.execute(
            select(func.count(Course.id))
        )

        return result.scalar_one()

    async def get_total_levels(self) -> int:

        result = await self.session.execute(
            select(func.count(Level.id))
        )

        return result.scalar_one()

    async def get_total_videos(self) -> int:

        # Each level contains its video information
        # inside the Level.video JSONB column.
        #
        # Count levels where video is not empty.

        result = await self.session.execute(
            select(func.count(Level.id))
            .where(
                Level.video.is_not(None)
            )
        )

        return result.scalar_one()

    async def get_total_coding_challenges(self) -> int:

        result = await self.session.execute(
            select(func.count(Checkpoint.id))
        )

        return result.scalar_one()

    async def get_completed_levels(self) -> int:

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

    async def get_daily_active_students(self) -> int:

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
                    func.distinct(Progress.user_id)
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

    async def get_monthly_active_students(self) -> int:

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
                    func.distinct(Progress.user_id)
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

    async def get_learning_hours(self) -> float:

        # There is currently no learning-duration column
        # in the models provided.
        #
        # Therefore we return 0 until a learning-session/
        # duration model is available.

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
                User.streak,
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
                User.streak,
            )
            .order_by(
                User.updated_at.desc()
            )
            .limit(limit)
        )

        return result.all()

    # ========================================================
    # STUDENT DASHBOARD
    # ========================================================

    async def get_student_courses(
        self,
        user_id,
    ):
        result = await self.session.execute(
            select(
                Course.id,
                Course.title,
                Course.difficulty,

                func.min(Level.stage).label("stage"),

                func.count(
                    func.distinct(Level.id)
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

    async def get_student_user(
        self,
        user_id,
    ):

        result = await self.session.execute(
            select(User)
            .where(User.id == user_id)
        )

        return result.scalar_one_or_none()

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
                    func.distinct(Level.id)
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