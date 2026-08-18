from datetime import datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.booking import Booking
from app.repositories.booking_repository import BookingRepository


class BookingService:

    def __init__(self, session: AsyncSession):
        self.repository = BookingRepository(session)

    async def get_by_id(
        self,
        booking_id: UUID,
    ) -> Booking | None:

        return await self.repository.get_by_id(booking_id)

    async def get_by_user_id(
        self,
        user_id: UUID,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Booking]:

        return await self.repository.get_by_user_id(
            user_id,
            skip=skip,
            limit=limit,
        )

    async def get_by_mentor_id(
        self,
        mentor_id: UUID,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Booking]:

        return await self.repository.get_by_mentor_id(
            mentor_id,
            skip=skip,
            limit=limit,
        )

    async def get_by_status(
        self,
        status: str,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Booking]:

        return await self.repository.get_by_status(
            status,
            skip=skip,
            limit=limit,
        )

    async def get_upcoming_for_user(
        self,
        user_id: UUID,
        *,
        from_time: datetime | None = None,
        limit: int = 100,
    ) -> list[Booking]:

        return await self.repository.get_upcoming_for_user(
            user_id,
            from_time=from_time,
            limit=limit,
        )

    async def get_upcoming_for_mentor(
        self,
        mentor_id: UUID,
        *,
        from_time: datetime | None = None,
        limit: int = 100,
    ) -> list[Booking]:

        return await self.repository.get_upcoming_for_mentor(
            mentor_id,
            from_time=from_time,
            limit=limit,
        )

    async def create_booking(
        self,
        booking: Booking,
    ) -> Booking:

        return await self.repository.create(booking)

    async def update_booking(
        self,
        booking: Booking,
    ) -> Booking:

        return await self.repository.update(booking)

    async def delete_booking(
        self,
        booking: Booking,
    ) -> None:

        await self.repository.delete(booking)