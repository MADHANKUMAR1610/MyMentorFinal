from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.checkpoint import Checkpoint
from app.repositories.base import BaseRepository


class CheckpointRepository(BaseRepository[Checkpoint]):
    """
    Repository responsible for Checkpoint database operations.

    Business rules belong in the service layer.
    """

    def __init__(self, session: AsyncSession):
        super().__init__(Checkpoint, session)

    async def get_by_level_id(
        self,
        level_id: UUID,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Checkpoint]:
        """
        Get checkpoints belonging to a level.
        """

        result = await self.session.execute(
            select(Checkpoint)
            .where(
                Checkpoint.level_id == level_id
            )
            .order_by(
                Checkpoint.checkpoint_order.asc()
            )
            .offset(skip)
            .limit(limit)
        )

        return list(result.scalars().all())

    async def get_by_level_and_order(
        self,
        level_id: UUID,
        checkpoint_order: int,
    ) -> Optional[Checkpoint]:
        """
        Get a specific checkpoint within a level.
        """

        result = await self.session.execute(
            select(Checkpoint).where(
                Checkpoint.level_id == level_id,
                Checkpoint.checkpoint_order == checkpoint_order,
            )
        )

        return result.scalar_one_or_none()

    async def get_by_difficulty(
        self,
        difficulty: str,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Checkpoint]:
        """
        Get checkpoints by difficulty.
        """

        result = await self.session.execute(
            select(Checkpoint)
            .where(
                Checkpoint.difficulty == difficulty
            )
            .offset(skip)
            .limit(limit)
        )

        return list(result.scalars().all())

    async def get_by_language(
        self,
        language: str,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Checkpoint]:
        """
        Get checkpoints by programming language.
        """

        result = await self.session.execute(
            select(Checkpoint)
            .where(
                Checkpoint.language == language
            )
            .offset(skip)
            .limit(limit)
        )

        return list(result.scalars().all())