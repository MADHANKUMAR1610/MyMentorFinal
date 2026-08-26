from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.progress import Progress
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):

    def __init__(self, session: AsyncSession):
        super().__init__(User, session)

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
                func.count(
                    func.distinct(Progress.level_id)
                )
                .filter(
                    Progress.completed.is_(True)
                )
                .label("completed_levels"),
            )
            .outerjoin(
                Progress,
                Progress.user_id == User.id,
            )
            .where(
                User.role == "student"
            )
            .group_by(
                User.id
            )
            .order_by(
                User.created_at.desc()
            )
            .offset(skip)
            .limit(limit)
        )

        return result.all()

    async def get_student_streak(
        self,
        user_id: UUID,
    ) -> int:
        """
        Calculate the student's current learning streak
        based on Progress.updated_at.

        A day counts when the student has progress activity
        on that date.
        """

        result = await self.session.execute(
            select(
                func.date(Progress.updated_at).label("activity_date")
            )
            .where(
                Progress.user_id == user_id
            )
            .group_by(
                func.date(Progress.updated_at)
            )
            .order_by(
                func.date(Progress.updated_at).desc()
            )
        )

        activity_dates = [
            row.activity_date
            for row in result.all()
        ]

        if not activity_dates:
            return 0

        today = datetime.now(timezone.utc).date()

        # --------------------------------------------------------
        # If the student has no activity today, allow the streak
        # to start from yesterday.
        # --------------------------------------------------------

        latest_date = activity_dates[0]

        if latest_date == today:
            expected_date = today
        elif latest_date == today - timedelta(days=1):
            expected_date = today - timedelta(days=1)
        else:
            return 0

        streak = 0

        for activity_date in activity_dates:

            if activity_date == expected_date:
                streak += 1
                expected_date -= timedelta(days=1)

            elif activity_date < expected_date:
                break

        return streak