from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.booking import Booking
from app.repositories.base import BaseRepository


class BookingRepository(BaseRepository[Booking]):
    """
    Repository responsible for Booking database operations.

    Business rules belong in the service layer.
    """

    def __init__(self, session: AsyncSession):
        super().__init__(Booking, session)

    async def get_by_user_id(
        self,
        user_id: UUID,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Booking]:
        """
        Get bookings belonging to a user.
        """

        result = await self.session.execute(
            select(Booking)
            .where(Booking.user_id == user_id)
            .order_by(Booking.scheduled_at.desc())
            .offset(skip)
            .limit(limit)
        )

        return list(result.scalars().all())

    async def get_by_mentor_id(
        self,
        mentor_id: UUID,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Booking]:
        """
        Get bookings belonging to a mentor.
        """

        result = await self.session.execute(
            select(Booking)
            .where(Booking.mentor_id == mentor_id)
            .order_by(Booking.scheduled_at.desc())
            .offset(skip)
            .limit(limit)
        )

        return list(result.scalars().all())

    async def get_by_status(
        self,
        status: str,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Booking]:
        """
        Get bookings by status.
        """

        result = await self.session.execute(
            select(Booking)
            .where(Booking.status == status)
            .order_by(Booking.scheduled_at.asc())
            .offset(skip)
            .limit(limit)
        )

        return list(result.scalars().all())

    async def get_upcoming_for_user(
        self,
        user_id: UUID,
        *,
        from_time: Optional[datetime] = None,
        limit: int = 100,
    ) -> list[Booking]:
        """
        Get upcoming bookings for a user.
        """

        if from_time is None:
            from_time = datetime.now().astimezone()

        result = await self.session.execute(
            select(Booking)
            .where(
                Booking.user_id == user_id,
                Booking.scheduled_at >= from_time,
                Booking.status == "upcoming",
            )
            .order_by(Booking.scheduled_at.asc())
            .limit(limit)
        )

        return list(result.scalars().all())

    async def get_upcoming_for_mentor(
        self,
        mentor_id: UUID,
        *,
        from_time: Optional[datetime] = None,
        limit: int = 100,
    ) -> list[Booking]:
        """
        Get upcoming bookings for a mentor.
        """

        if from_time is None:
            from_time = datetime.now().astimezone()

        result = await self.session.execute(
            select(Booking)
            .where(
                Booking.mentor_id == mentor_id,
                Booking.scheduled_at >= from_time,
                Booking.status == "upcoming",
            )
            .order_by(Booking.scheduled_at.asc())
            .limit(limit)
        )

        return list(result.scalars().all())