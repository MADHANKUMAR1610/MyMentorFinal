from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.level import Level
from app.models.progress import Progress

from app.repositories.level_repository import LevelRepository
from app.repositories.progress_repository import ProgressRepository
from app.repositories.checkpoint_repository import CheckpointRepository

class LevelService:

    def __init__(self, session: AsyncSession):

        self.repository = LevelRepository(session)

        self.level_repository = LevelRepository(session)
        self.progress_repository = ProgressRepository(session)
        self.checkpoint_repository = CheckpointRepository(session)

    # ============================================================
    # GET BY ID
    # ============================================================

    async def get_by_id(
        self,
        level_id: UUID,
    ) -> Level | None:

        return await self.repository.get_by_id(
            level_id
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
    ) -> list[Level]:

        return await self.repository.get_by_course_id(
            course_id,
            skip=skip,
            limit=limit,
        )

    # ============================================================
    # GET BY COURSE + LEVEL NUMBER
    # ============================================================

    async def get_by_course_and_level_number(
        self,
        course_id: UUID,
        level_number: int,
    ) -> Level | None:

        return await self.repository.get_by_course_and_level_number(
            course_id,
            level_number,
        )

    # ============================================================
    # GET BY STAGE
    # ============================================================

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

    # ============================================================
    # GET BY GLOBAL ORDER
    # ============================================================

    async def get_by_global_order(
        self,
        global_order: int,
    ) -> Level | None:

        return await self.repository.get_by_global_order(
            global_order
        )

    # ============================================================
    # CHECKPOINT COUNT
    # ============================================================

    async def get_levels_with_checkpoint_count(
        self,
        course_id: UUID,
        *,
        skip: int = 0,
        limit: int = 100,
    ):

        return await self.repository.get_levels_with_checkpoint_count(
            course_id,
            skip=skip,
            limit=limit,
        )

    # ============================================================
    # CREATE
    # ============================================================

    async def create_level(
        self,
        level: Level,
    ) -> Level:

        return await self.repository.create(
            level
        )

    # ============================================================
    # UPDATE
    # ============================================================

    async def update_level(
        self,
        level: Level,
    ) -> Level:

        return await self.repository.update(
            level
        )

    # ============================================================
    # DELETE
    # ============================================================

    async def delete_level(
        self,
        level: Level,
    ) -> None:

        await self.repository.delete(
            level
        )

    # ============================================================
    # COMPLETE LEVEL VIDEO
    # ============================================================

    async def complete_level_video(
        self,
        user_id: UUID,
        level_id: UUID,
    ):
        # --------------------------------------------------
        # 1. Get level
        # --------------------------------------------------

        level = await self.level_repository.get_by_id(level_id)

        if not level:
            raise HTTPException(
                status_code=404,
                detail="Level not found",
            )

        # --------------------------------------------------
        # 2. Get user's progress
        # --------------------------------------------------

        progress = await self.progress_repository.get_user_level_progress(
            user_id=user_id,
            level_id=level_id,
        )

        # --------------------------------------------------
        # 3. Create progress if it doesn't exist
        # --------------------------------------------------

        if not progress:

            progress = Progress(
                user_id=user_id,
                course_id=level.course_id,
                level_id=level_id,
                checkpoints_passed=[],
                video_completed=False,
                completed=False,
              
            )

            progress = await self.progress_repository.create(progress)

        # --------------------------------------------------
        # 4. Get all checkpoints
        # --------------------------------------------------

        checkpoints = await self.checkpoint_repository.get_by_level_id(
            level_id
        )

        checkpoint_ids = {
            str(checkpoint.id)
            for checkpoint in checkpoints
        }

        passed_checkpoint_ids = {
            str(checkpoint_id)
            for checkpoint_id in (progress.checkpoints_passed or [])
        }

        # --------------------------------------------------
        # 5. Check all checkpoints
        # --------------------------------------------------

        all_checkpoints_completed = checkpoint_ids.issubset(
            passed_checkpoint_ids
        )

        if not all_checkpoints_completed:

            raise HTTPException(
                status_code=400,
                detail="Complete all checkpoints before completing the level",
            )

        # --------------------------------------------------
        # 6. Complete video
        # --------------------------------------------------

        progress.video_completed = True

        # --------------------------------------------------
        # 7. Complete level
        # --------------------------------------------------

        progress.completed = True

        # XP
        progress.xp_earned = level.xp

        # --------------------------------------------------
        # 8. Save
        # --------------------------------------------------

        updated_progress = await self.progress_repository.update(
            progress
        )

        return {
            "success": True,
            "level_id": str(level_id),
            "video_completed": True,
            "level_completed": True,
            "xp_earned": level.xp,
            "message": "Level completed successfully",
        }