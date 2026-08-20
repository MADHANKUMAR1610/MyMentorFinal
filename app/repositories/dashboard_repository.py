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

    async def get_total_courses(self) -> int:
        result = await self.session.execute(
            select(func.count(Course.id))
        )

        return result.scalar_one()

    async def get_published_courses(self) -> int:
        result = await self.session.execute(
            select(func.count(Course.id))
            .where(Course.status == "published")
        )

        return result.scalar_one()

    async def get_draft_courses(self) -> int:
        result = await self.session.execute(
            select(func.count(Course.id))
            .where(Course.status == "draft")
        )

        return result.scalar_one()

    async def get_total_levels(self) -> int:
        result = await self.session.execute(
            select(func.count(Level.id))
        )

        return result.scalar_one()

    async def get_total_checkpoints(self) -> int:
        result = await self.session.execute(
            select(func.count(Checkpoint.id))
        )

        return result.scalar_one()

    async def get_total_students(self) -> int:
        result = await self.session.execute(
            select(func.count(User.id))
            .where(User.role == "student")
        )

        return result.scalar_one()

    async def get_completed_levels(self) -> int:
        result = await self.session.execute(
            select(func.count(Progress.id))
            .where(Progress.completed.is_(True))
        )

        return result.scalar_one()

    async def get_course_statistics(self):
        result = await self.session.execute(
            select(
                Course.id,
                Course.title,
                Course.status,
                func.count(
                    func.distinct(Level.id)
                ).label("total_levels"),
                func.count(
                    func.distinct(Checkpoint.id)
                ).label("total_checkpoints"),
            )
            .outerjoin(
                Level,
                Level.course_id == Course.id,
            )
            .outerjoin(
                Checkpoint,
                Checkpoint.level_id == Level.id,
            )
            .group_by(
                Course.id,
                Course.title,
                Course.status,
            )
            .order_by(
                Course.created_at.desc()
            )
        )

        return result.all()
    async def get_student_course_statistics(
        self,
        user_id,
    ):
        result = await self.session.execute(
            select(
                Course.id,
                Course.title,
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
            )
            .order_by(
                Course.title.asc()
            )
        )

        return result.all()
    async def get_student_completed_levels(
        self,
        user_id,
    ) -> int:

        result = await self.session.execute(
            select(func.count(Progress.id))
            .where(
                Progress.user_id == user_id,
                Progress.completed.is_(True),
            )
        )

        return result.scalar_one()