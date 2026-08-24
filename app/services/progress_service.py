from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.progress import Progress
from app.repositories.progress_repository import ProgressRepository


class ProgressService:

    def __init__(self, session: AsyncSession):
        self.repository = ProgressRepository(session)

    async def get_by_id(
        self,
        progress_id: UUID,
    ) -> Progress | None:

        return await self.repository.get_by_id(progress_id)

    async def get_by_user_id(
        self,
        user_id: UUID,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Progress]:

        return await self.repository.get_by_user_id(
            user_id,
            skip=skip,
            limit=limit,
        )

    async def get_by_course_id(
        self,
        course_id: UUID,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Progress]:

        return await self.repository.get_by_course_id(
            course_id,
            skip=skip,
            limit=limit,
        )

    async def get_by_level_id(
        self,
        level_id: UUID,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Progress]:

        return await self.repository.get_by_level_id(
            level_id,
            skip=skip,
            limit=limit,
        )

    async def get_user_level_progress(
        self,
        user_id: UUID,
        level_id: UUID,
    ) -> Progress | None:

        return await self.repository.get_user_level_progress(
            user_id,
            level_id,
        )

    async def get_completed_for_user(
        self,
        user_id: UUID,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Progress]:

        return await self.repository.get_completed_for_user(
            user_id,
            skip=skip,
            limit=limit,
        )

    async def get_incomplete_for_user(
        self,
        user_id: UUID,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Progress]:

        return await self.repository.get_incomplete_for_user(
            user_id,
            skip=skip,
            limit=limit,
        )

    async def create_progress(
        self,
        progress: Progress,
    ) -> Progress:

        existing = await self.repository.get_user_level_progress(
            progress.user_id,
            progress.level_id,
        )

        if existing:
            existing.course_id = progress.course_id
            existing.checkpoints_passed = progress.checkpoints_passed
            existing.video_completed = progress.video_completed
            existing.completed = progress.completed

            return await self.repository.update(existing)

        return await self.repository.create(progress)

    async def update_progress(
        self,
        progress: Progress,
    ) -> Progress:

        return await self.repository.update(progress)

    async def delete_progress(
        self,
        progress: Progress,
    ) -> None:

        await self.repository.delete(progress)