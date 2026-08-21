from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.career_calendar import CareerCalendar
from app.repositories.base import BaseRepository


class CareerCalendarRepository(
    BaseRepository[CareerCalendar]
):

    def __init__(
        self,
        session: AsyncSession,
    ):
        super().__init__(
            CareerCalendar,
            session,
        )

    async def get_by_user_id(
        self,
        user_id: UUID,
    ) -> Optional[CareerCalendar]:

        result = await self.session.execute(
            select(CareerCalendar).where(
                CareerCalendar.user_id == user_id
            )
        )

        return result.scalar_one_or_none()

    async def get_by_user_and_persona(
        self,
        user_id: UUID,
        career_persona_id: UUID,
    ) -> Optional[CareerCalendar]:

        result = await self.session.execute(
            select(CareerCalendar).where(
                CareerCalendar.user_id == user_id,
                CareerCalendar.career_persona_id
                == career_persona_id,
            )
        )

        return result.scalar_one_or_none()

    async def create_calendar(
        self,
        calendar: CareerCalendar,
    ) -> CareerCalendar:

        self.session.add(calendar)

        await self.session.flush()

        await self.session.refresh(calendar)

        return calendar

    async def update_calendar(
        self,
        calendar: CareerCalendar,
    ) -> CareerCalendar:

        await self.session.flush()

        await self.session.refresh(calendar)

        return calendar