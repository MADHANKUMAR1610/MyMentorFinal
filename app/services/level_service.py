from datetime import datetime, timedelta
from uuid import UUID
from zoneinfo import ZoneInfo

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.level import Level
from app.models.progress import Progress
from app.models.user import User

from app.repositories.level_repository import LevelRepository
from app.repositories.progress_repository import ProgressRepository
from app.repositories.checkpoint_repository import CheckpointRepository


class LevelService:

    def __init__(self, session: AsyncSession):

        # IMPORTANT:
        # Some methods in this service directly use the session.
        self.session = session

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
    # RECORD LEARNING ACTIVITY
    # ============================================================

    async def record_learning_activity(
        self,
        user_id: UUID,
    ) -> int:
        """
        Record a successful learning action.

        Learning actions:
            - Successful checkpoint
            - All MCQs completed
            - Video completed

        Rules:
            - Same day = streak does not increase twice
            - Yesterday = streak increases by 1
            - Gap = streak resets to 1
            - Login does not affect learning streak
        """

        # --------------------------------------------------------
        # INDIA TIMEZONE
        # --------------------------------------------------------

        today = datetime.now(
            ZoneInfo("Asia/Kolkata")
        ).date()

        today_str = today.isoformat()

        yesterday_str = (
            today - timedelta(days=1)
        ).isoformat()

        # --------------------------------------------------------
        # GET USER
        # --------------------------------------------------------

        result = await self.session.execute(
            select(User)
            .where(
                User.id == user_id
            )
        )

        user = result.scalar_one_or_none()

        if user is None:
            raise HTTPException(
                status_code=404,
                detail="User not found",
            )

        # --------------------------------------------------------
        # LAST LEARNING ACTIVITY
        # --------------------------------------------------------

        last_active = (
            str(user.last_active)
            if user.last_active
            else None
        )

        # --------------------------------------------------------
        # SAME DAY
        # --------------------------------------------------------

        if last_active == today_str:

            return int(
                user.streak or 0
            )

        # --------------------------------------------------------
        # CONSECUTIVE DAY
        # --------------------------------------------------------

        if last_active == yesterday_str:

            user.streak = (
                int(user.streak or 0) + 1
            )

        # --------------------------------------------------------
        # FIRST ACTIVITY / STREAK BROKEN
        # --------------------------------------------------------

        else:

            user.streak = 1

        # --------------------------------------------------------
        # SAVE LAST LEARNING DATE
        # --------------------------------------------------------

        user.last_active = today_str

        await self.session.flush()

        return int(
            user.streak or 0
        )

    # ============================================================
    # CHECK AND COMPLETE LEVEL
    # ============================================================

    async def check_and_complete_level(
        self,
        user_id: UUID,
        level_id: UUID,
    ):
        """
        Level completion rules.

        TYPE 1 - CODING LEVEL
            Video + Checkpoints

            Requirements:
                video_completed == True
                AND
                all checkpoints completed

            Reward:
                100 XP

        TYPE 2 - MCQ LEVEL
            Theory + MCQs

            Requirements:
                mcqs_completed == True

            Reward:
                100 XP

        TYPE 3 - VIDEO ONLY LEVEL
            Video only

            Requirements:
                video_completed == True
                AND
                no checkpoints
                AND
                MCQs not required

            Reward:
                100 XP

        XP is awarded only once.
        """

        # --------------------------------------------------------
        # 1. GET LEVEL
        # --------------------------------------------------------

        level = await self.level_repository.get_by_id(
            level_id
        )

        if not level:

            raise HTTPException(
                status_code=404,
                detail="Level not found",
            )

        # --------------------------------------------------------
        # 2. GET USER
        # --------------------------------------------------------

        user = await self.session.get(
            User,
            user_id,
        )

        if not user:

            raise HTTPException(
                status_code=404,
                detail="User not found",
            )

        # --------------------------------------------------------
        # 3. GET PROGRESS
        # --------------------------------------------------------

        progress = (
            await self.progress_repository
            .get_user_level_progress(
                user_id=user_id,
                level_id=level_id,
            )
        )

        # --------------------------------------------------------
        # 4. CREATE PROGRESS IF MISSING
        # --------------------------------------------------------

        if progress is None:

            progress = Progress(
                user_id=user_id,
                course_id=level.course_id,
                level_id=level_id,
                checkpoints_passed=[],
                mcqs_answered=[],
                video_completed=False,
                mcqs_completed=False,
                completed=False,
            )

            progress = (
                await self.progress_repository
                .create(progress)
            )

        # --------------------------------------------------------
        # 5. ALREADY COMPLETED
        # --------------------------------------------------------

        if progress.completed:

            return {
                "success": True,
                "level_id": str(level_id),
                "level_completed": True,
                "xp_earned": 0,
                "message": "Level already completed",
            }

        # --------------------------------------------------------
        # 6. GET CHECKPOINTS
        # --------------------------------------------------------

        checkpoints = (
            await self.checkpoint_repository
            .get_by_level_id(level_id)
        )

        has_checkpoints = bool(
            checkpoints
        )

        # --------------------------------------------------------
        # 7. CHECK PASSED CHECKPOINTS
        # --------------------------------------------------------

        checkpoint_ids = {
            str(checkpoint.id)
            for checkpoint in checkpoints
        }

        passed_checkpoint_ids = {
            str(checkpoint_id)
            for checkpoint_id in (
                progress.checkpoints_passed
                or []
            )
        }

        all_checkpoints_completed = (
            checkpoint_ids.issubset(
                passed_checkpoint_ids
            )
        )

        # --------------------------------------------------------
        # 8. TYPE 1 - CODING LEVEL
        # --------------------------------------------------------

        video_checkpoint_completed = (
            has_checkpoints
            and progress.video_completed
            and all_checkpoints_completed
        )

        # --------------------------------------------------------
        # 9. TYPE 2 - MCQ LEVEL
        # --------------------------------------------------------

        mcq_level_completed = (
            progress.mcqs_completed is True
        )

        # --------------------------------------------------------
        # 10. TYPE 3 - VIDEO ONLY LEVEL
        # --------------------------------------------------------

        video_only_completed = (
            not has_checkpoints
            and not progress.mcqs_completed
            and progress.video_completed
        )

        # --------------------------------------------------------
        # 11. FINAL LEVEL COMPLETION
        # --------------------------------------------------------

        level_completed = (
            video_checkpoint_completed
            or mcq_level_completed
            or video_only_completed
        )

        # --------------------------------------------------------
        # 12. NOT COMPLETED YET
        # --------------------------------------------------------

        if not level_completed:

            return {
                "success": True,
                "level_id": str(level_id),
                "level_completed": False,
                "xp_earned": 0,
                "message": "Level is not completed yet",
            }

        # --------------------------------------------------------
        # 13. COMPLETE LEVEL
        # --------------------------------------------------------

        progress.completed = True

        # --------------------------------------------------------
        # 14. AWARD EXACTLY 100 XP
        # --------------------------------------------------------

        XP_REWARD = 100

        user.xp = (
            user.xp or 0
        ) + XP_REWARD

        # --------------------------------------------------------
        # 15. SAVE
        # --------------------------------------------------------

        await self.progress_repository.update(
            progress
        )

        await self.session.flush()

        # --------------------------------------------------------
        # 16. RESPONSE
        # --------------------------------------------------------

        return {
            "success": True,
            "level_id": str(level_id),
            "level_completed": True,
            "xp_earned": XP_REWARD,
            "message": "Level completed successfully",
        }

    # ============================================================
    # COMPLETE LEVEL VIDEO
    # ============================================================

    async def complete_level_video(
        self,
        user_id: UUID,
        level_id: UUID,
    ):
        """
        Mark the video as completed.

        IMPORTANT:

        Video completion itself does NOT automatically mean
        the whole level is completed when checkpoints exist.

        Coding level:
            Video + all checkpoints = complete

        Video-only level:
            Video = complete

        MCQ level:
            MCQ completion controls completion
        """

        # --------------------------------------------------------
        # 1. GET LEVEL
        # --------------------------------------------------------

        level = await self.level_repository.get_by_id(
            level_id
        )

        if not level:

            raise HTTPException(
                status_code=404,
                detail="Level not found",
            )

        # --------------------------------------------------------
        # 2. GET USER
        # --------------------------------------------------------

        user = await self.session.get(
            User,
            user_id,
        )

        if not user:

            raise HTTPException(
                status_code=404,
                detail="User not found",
            )

        # --------------------------------------------------------
        # 3. GET PROGRESS
        # --------------------------------------------------------

        progress = (
            await self.progress_repository
            .get_user_level_progress(
                user_id=user_id,
                level_id=level_id,
            )
        )

        # --------------------------------------------------------
        # 4. CREATE PROGRESS IF MISSING
        # --------------------------------------------------------

        if progress is None:

            progress = Progress(
                user_id=user_id,
                course_id=level.course_id,
                level_id=level_id,
                checkpoints_passed=[],
                mcqs_answered=[],
                video_completed=False,
                mcqs_completed=False,
                completed=False,
            )

            progress = (
                await self.progress_repository
                .create(progress)
            )

        # --------------------------------------------------------
        # 5. ALREADY COMPLETED
        # --------------------------------------------------------

        if progress.completed:

            return {
                "success": True,
                "level_id": str(level_id),
                "video_completed": True,
                "level_completed": True,
                "xp_earned": 0,
                "message": "Level already completed",
            }

        # --------------------------------------------------------
        # 6. CHECK WHETHER VIDEO WAS ALREADY COMPLETED
        # --------------------------------------------------------

        was_video_completed = bool(
            progress.video_completed
        )

        # --------------------------------------------------------
        # 7. MARK VIDEO COMPLETED
        # --------------------------------------------------------

        progress.video_completed = True

        # --------------------------------------------------------
        # 8. RECORD LEARNING STREAK
        # --------------------------------------------------------

        # Only the first successful video completion
        # counts as a learning activity.

        if not was_video_completed:

            await self.record_learning_activity(
                user_id
            )

        # --------------------------------------------------------
        # 9. SAVE VIDEO PROGRESS
        # --------------------------------------------------------

        await self.progress_repository.update(
            progress
        )

        await self.session.flush()

        # --------------------------------------------------------
        # 10. CHECK WHETHER LEVEL IS NOW COMPLETED
        # --------------------------------------------------------

        completion_result = (
            await self.check_and_complete_level(
                user_id=user_id,
                level_id=level_id,
            )
        )

        # --------------------------------------------------------
        # 11. RESPONSE
        # --------------------------------------------------------

        return {
            "success": True,
            "level_id": str(level_id),
            "video_completed": True,
            "level_completed": completion_result[
                "level_completed"
            ],
            "xp_earned": completion_result[
                "xp_earned"
            ],
            "message": (
                "Level completed successfully"
                if completion_result["level_completed"]
                else "Video completed successfully"
            ),
        }

    # ============================================================
    # COUNT BY COURSE
    # ============================================================

    async def count_by_course_id(
        self,
        course_id: UUID,
    ) -> int:

        return await self.repository.count_by_course_id(
            course_id
        )