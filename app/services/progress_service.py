from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.progress import Progress
from app.models.level import Level
from app.repositories.progress_repository import ProgressRepository


class ProgressService:

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = ProgressRepository(session)

    # ============================================================
    # GET BY ID
    # ============================================================

    async def get_by_id(
        self,
        progress_id: UUID,
    ) -> Progress | None:

        return await self.repository.get_by_id(progress_id)

    # ============================================================
    # GET BY USER
    # ============================================================

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

    # ============================================================
    # GET BY COURSE
    # ============================================================

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

    # ============================================================
    # GET BY LEVEL
    # ============================================================

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

    # ============================================================
    # GET USER LEVEL PROGRESS
    # ============================================================

    async def get_user_level_progress(
        self,
        user_id: UUID,
        level_id: UUID,
    ) -> Progress | None:

        return await self.repository.get_user_level_progress(
            user_id,
            level_id,
        )

    # ============================================================
    # GET COMPLETED
    # ============================================================

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

    # ============================================================
    # GET INCOMPLETE
    # ============================================================

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

    # ============================================================
    # CREATE / GET EXISTING PROGRESS
    # ============================================================

    async def create_progress(
        self,
        progress: Progress,
    ) -> Progress:

        # --------------------------------------------------------
        # 1. Get level
        # --------------------------------------------------------

        result = await self.session.execute(
            select(Level).where(
                Level.id == progress.level_id
            )
        )

        level = result.scalar_one_or_none()

        if level is None:
            raise HTTPException(
                status_code=404,
                detail="Level not found",
            )

        # --------------------------------------------------------
        # 2. ALWAYS derive course_id from level
        #
        # Never trust frontend course_id
        # --------------------------------------------------------

        progress.course_id = level.course_id

        # --------------------------------------------------------
        # 3. Check existing progress
        # --------------------------------------------------------

        existing = await self.repository.get_user_level_progress(
            progress.user_id,
            progress.level_id,
        )

        if existing:

            # IMPORTANT:
            # Keep course_id from the actual level
            existing.course_id = level.course_id

            existing.checkpoints_passed = (
                progress.checkpoints_passed
            )

            existing.mcqs_answered = (
                progress.mcqs_answered
            )

            existing.video_completed = (
                progress.video_completed
            )

            existing.mcqs_completed = (
                progress.mcqs_completed
            )

            existing.completed = (
                progress.completed
            )

            return await self.repository.update(
                existing
            )

        # --------------------------------------------------------
        # 4. Create new progress
        # --------------------------------------------------------

        return await self.repository.create(
            progress
        )

    # ============================================================
    # UPDATE
    # ============================================================

    async def update_progress(
        self,
        progress: Progress,
    ) -> Progress:

        return await self.repository.update(
            progress
        )

    # ============================================================
    # DELETE
    # ============================================================

    async def delete_progress(
        self,
        progress: Progress,
    ) -> None:

        await self.repository.delete(
            progress
        )