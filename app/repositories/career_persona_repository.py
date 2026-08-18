from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.career_persona import CareerPersona
from app.repositories.base import BaseRepository


class CareerPersonaRepository(BaseRepository[CareerPersona]):
    """
    Repository responsible for CareerPersona database operations.

    Business logic belongs in the service layer.
    """

    def __init__(self, session: AsyncSession):
        super().__init__(CareerPersona, session)

    async def get_by_user_id(
        self,
        user_id: UUID,
    ) -> Optional[CareerPersona]:
        """
        Get the career persona belonging to a user.
        """

        result = await self.session.execute(
            select(CareerPersona).where(
                CareerPersona.user_id == user_id
            )
        )

        return result.scalar_one_or_none()

    async def get_by_goal(
        self,
        goal: str,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[CareerPersona]:
        """
        Get career personas matching a career goal.
        """

        result = await self.session.execute(
            select(CareerPersona)
            .where(
                CareerPersona.goal == goal
            )
            .offset(skip)
            .limit(limit)
        )

        return list(result.scalars().all())