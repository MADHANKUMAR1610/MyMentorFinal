from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.level import Level
from app.repositories.level_repository import LevelRepository


class LevelService:

    def __init__(self, session: AsyncSession):
        self.repository = LevelRepository(session)

    async def get_by_id(
        self,
        level_id: UUID,
    ) -> Level | None:

        return await self.repository.get_by_id(level_id)

    async def get_by_course_id(
        self,
        course_id: UUID,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Level]:

        return await self.repository.get_by_course_id(
            course_id,
            skip=skip,
            limit=limit,
        )

    async def get_by_course_and_level_number(
        self,
        course_id: UUID,
        level_number: int,
    ) -> Level | None:

        return await self.repository.get_by_course_and_level_number(
            course_id,
            level_number,
        )

    async def get_by_stage(
        self,
        stage: str,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Level]:

        return await self.repository.get_by_stage(
            stage,
            skip=skip,
            limit=limit,
        )

    async def get_by_global_order(
        self,
        global_order: int,
    ) -> Level | None:

        return await self.repository.get_by_global_order(
            global_order
        )

    async def create_level(
        self,
        level: Level,
    ) -> Level:

        return await self.repository.create(level)

    async def update_level(
        self,
        level: Level,
    ) -> Level:

        return await self.repository.update(level)

    async def delete_level(
        self,
        level: Level,
    ) -> None:

        await self.repository.delete(level)