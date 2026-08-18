from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.checkpoint import Checkpoint
from app.repositories.checkpoint_repository import CheckpointRepository


class CheckpointService:

    def __init__(self, session: AsyncSession):
        self.repository = CheckpointRepository(session)

    async def get_by_id(
        self,
        checkpoint_id: UUID,
    ) -> Checkpoint | None:

        return await self.repository.get_by_id(checkpoint_id)

    async def get_by_level_id(
        self,
        level_id: UUID,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Checkpoint]:

        return await self.repository.get_by_level_id(
            level_id,
            skip=skip,
            limit=limit,
        )

    async def get_by_level_and_order(
        self,
        level_id: UUID,
        checkpoint_order: int,
    ) -> Checkpoint | None:

        return await self.repository.get_by_level_and_order(
            level_id,
            checkpoint_order,
        )

    async def get_by_difficulty(
        self,
        difficulty: str,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Checkpoint]:

        return await self.repository.get_by_difficulty(
            difficulty,
            skip=skip,
            limit=limit,
        )

    async def get_by_language(
        self,
        language: str,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Checkpoint]:

        return await self.repository.get_by_language(
            language,
            skip=skip,
            limit=limit,
        )

    async def create_checkpoint(
        self,
        checkpoint: Checkpoint,
    ) -> Checkpoint:

        return await self.repository.create(checkpoint)

    async def update_checkpoint(
        self,
        checkpoint: Checkpoint,
    ) -> Checkpoint:

        return await self.repository.update(checkpoint)

    async def delete_checkpoint(
        self,
        checkpoint: Checkpoint,
    ) -> None:

        await self.repository.delete(checkpoint)