
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.career_persona_history import (
    CareerPersonaHistory,
)

from app.repositories.career_persona_history_repository import (
    CareerPersonaHistoryRepository,
)


class CareerPersonaHistoryService:

    def __init__(
        self,
        session: AsyncSession,
    ):
        self.repository = (
            CareerPersonaHistoryRepository(
                session
            )
        )

    # ========================================================
    # CREATE HISTORY
    # ========================================================

    async def create_history(
        self,
        history: CareerPersonaHistory,
    ) -> CareerPersonaHistory:

        return await self.repository.create(
            history
        )

    # ========================================================
    # GET USER HISTORY
    # ========================================================

    async def get_user_history(
        self,
        user_id: UUID,
        *,
        skip: int = 0,
        limit: int = 20,
    ) -> list[CareerPersonaHistory]:

        return await self.repository.get_by_user_id(
            user_id,
            skip=skip,
            limit=limit,
        )

    # ========================================================
    # GET HISTORY BY ID
    # ========================================================

    async def get_by_id(
        self,
        history_id: UUID,
    ) -> CareerPersonaHistory | None:

        return await self.repository.get_by_id(
            history_id
        )

    # ========================================================
    # GET LATEST HISTORY
    # ========================================================

    async def get_latest_by_user_id(
        self,
        user_id: UUID,
    ) -> CareerPersonaHistory | None:

        return await self.repository.get_latest_by_user_id(
            user_id
        )

    # ========================================================
    # COUNT USER HISTORY
    # ========================================================

    async def count_user_history(
        self,
        user_id: UUID,
    ) -> int:

        return await self.repository.count_by_user_id(
            user_id
        )

