from typing import Optional
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.career_persona_history import (
    CareerPersonaHistory,
)

from app.repositories.base import BaseRepository


class CareerPersonaHistoryRepository(
    BaseRepository[CareerPersonaHistory]
):

    def __init__(
        self,
        session: AsyncSession,
    ):
        super().__init__(
            CareerPersonaHistory,
            session,
        )

    # ========================================================
    # GET USER HISTORY
    # ========================================================

    async def get_by_user_id(
        self,
        user_id: UUID,
        *,
        skip: int = 0,
        limit: int = 20,
    ) -> list[CareerPersonaHistory]:

        result = await self.session.execute(
            select(CareerPersonaHistory)
            .where(
                CareerPersonaHistory.user_id == user_id
            )
            .order_by(
                CareerPersonaHistory.created_at.desc()
            )
            .offset(skip)
            .limit(limit)
        )

        return list(
            result.scalars().all()
        )

    # ========================================================
    # GET ONE HISTORY RECORD
    # ========================================================

    async def get_by_id(
        self,
        history_id: UUID,
    ) -> Optional[CareerPersonaHistory]:

        result = await self.session.execute(
            select(CareerPersonaHistory)
            .where(
                CareerPersonaHistory.id == history_id
            )
        )

        return result.scalar_one_or_none()

    # ========================================================
    # GET LATEST HISTORY
    # ========================================================

    async def get_latest_by_user_id(
        self,
        user_id: UUID,
    ) -> Optional[CareerPersonaHistory]:

        result = await self.session.execute(
            select(CareerPersonaHistory)
            .where(
                CareerPersonaHistory.user_id == user_id
            )
            .order_by(
                CareerPersonaHistory.created_at.desc()
            )
            .limit(1)
        )

        return result.scalar_one_or_none()

    # ========================================================
    # COUNT USER HISTORY
    # ========================================================

    async def count_by_user_id(
        self,
        user_id: UUID,
    ) -> int:

        result = await self.session.execute(
            select(
                func.count(
                    CareerPersonaHistory.id
                )
            )
            .where(
                CareerPersonaHistory.user_id == user_id
            )
        )

        return result.scalar_one() or 0
