from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.career_calendar import CareerCalendar


class CareerCalendarService:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_user_id(
        self,
        user_id: UUID,
    ):
        result = await self.session.execute(
            select(CareerCalendar)
            .where(CareerCalendar.user_id == user_id)
        )

        return result.scalar_one_or_none()

    async def get_by_id(
        self,
        calendar_id: UUID,
    ):
        result = await self.session.execute(
            select(CareerCalendar)
            .where(CareerCalendar.id == calendar_id)
        )

        return result.scalar_one_or_none()

    async def create_calendar(
        self,
        calendar: CareerCalendar,
    ):
        self.session.add(calendar)

        await self.session.commit()

        await self.session.refresh(calendar)

        return calendar

    async def update_calendar(
        self,
        calendar: CareerCalendar,
    ):
        await self.session.commit()

        await self.session.refresh(calendar)

        return calendar

    async def delete_calendar(
        self,
        calendar: CareerCalendar,
    ):
        await self.session.delete(calendar)

        await self.session.commit()