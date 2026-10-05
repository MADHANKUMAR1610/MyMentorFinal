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

    # GET PROGRESS BY ID

    # ============================================================

    async def get_by_id(
        self,
        progress_id: UUID,
    ) -> Progress | None:

        return await self.repository.get_by_id(
            progress_id
        )

    # ============================================================
    # GET PROGRESS BY USER ID
    # ============================================================

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

    # GET PROGRESS BY COURSE ID

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

    # GET PROGRESS BY LEVEL ID

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

    # GET COMPLETED PROGRESS

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

    # GET INCOMPLETE PROGRESS

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

    # CREATE PROGRESS
    # ============================================================

    async def create_progress(
        self,
        progress: Progress,
    ) -> Progress:

        # Check whether progress already exists
        existing = await self.repository.get_user_level_progress(
            progress.user_id,
            progress.level_id,
        )

        if existing:

            existing.course_id = progress.course_id

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

        return await self.repository.create(
            progress
        )

    # ============================================================
    # UPDATE PROGRESS
    # ============================================================

    async def update_progress(
        self,
        progress_id: UUID,
        data,
    ) -> Progress:

        progress = await self.repository.get_by_id(
            progress_id
        )

        if progress is None:
            raise ValueError(
                "Progress not found"
            )

        # Update checkpoints
        if data.checkpoints_passed is not None:
            progress.checkpoints_passed = (
                data.checkpoints_passed
            )

        # Update MCQ answers
        if data.mcqs_answered is not None:
            progress.mcqs_answered = (
                data.mcqs_answered
            )

        # Update video status
        if data.video_completed is not None:
            progress.video_completed = (
                data.video_completed
            )

        # Update MCQ completion
        if data.mcqs_completed is not None:
            progress.mcqs_completed = (
                data.mcqs_completed
            )

        # Update level completion
        if data.completed is not None:
            progress.completed = (
                data.completed
            )

        return await self.repository.update(
            progress
        )
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.progress import Progress
from app.repositories.progress_repository import ProgressRepository


class ProgressService:

    def __init__(self, session: AsyncSession):
        self.repository = ProgressRepository(session)

    # ============================================================
    # GET PROGRESS BY ID
    # ============================================================

    async def get_by_id(
        self,
        progress_id: UUID,
    ) -> Progress | None:

        return await self.repository.get_by_id(
            progress_id
        )

    # ============================================================
    # GET PROGRESS BY USER ID
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
    # GET PROGRESS BY COURSE ID
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
    # GET PROGRESS BY LEVEL ID
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
    # GET COMPLETED PROGRESS
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
    # GET INCOMPLETE PROGRESS
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
    # CREATE PROGRESS

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


            existing.course_id = progress.course_id

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



        return await self.repository.create(
            progress
        )

    # ============================================================

    # UPDATE PROGRESS

    # ============================================================

    async def update_progress(
        self,
        progress_id: UUID,
        data,
    ) -> Progress:


        progress = await self.repository.get_by_id(
            progress_id
        )

        if progress is None:
            raise ValueError(
                "Progress not found"
            )

        if data.checkpoints_passed is not None:
            progress.checkpoints_passed = (
                data.checkpoints_passed
            )

        if data.mcqs_answered is not None:
            progress.mcqs_answered = (
                data.mcqs_answered
            )

        if data.video_completed is not None:
            progress.video_completed = (
                data.video_completed
            )

        if data.mcqs_completed is not None:
            progress.mcqs_completed = (
                data.mcqs_completed
            )

        if data.completed is not None:
            progress.completed = (
                data.completed
            )


        return await self.repository.update(
            progress
        )

    # ============================================================

    # DELETE PROGRESS

    # ============================================================

    async def delete_progress(
        self,
        progress: Progress,
    ) -> None:

        await self.repository.delete(
            progress

        )
    # ============================================================
    # DELETE PROGRESS
    # ============================================================

    async def delete_progress(
        self,
        progress: Progress,
    ) -> None:

        await self.repository.delete(
            progress

        )