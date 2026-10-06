from uuid import UUID

from fastapi import HTTPException, status

from sqlalchemy import select

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.level import Level

from app.models.progress import Progress

from app.models.course_enrollment import CourseEnrollment

from app.services.level_service import LevelService

from app.schemas.introduction_mcq import (

    IntroductionMCQResponse,

)

class IntroductionMCQService:

    def __init__(

        self,

        session: AsyncSession,

    ):

        self.session = session

    # ============================================================

    # GET LEVEL

    # ============================================================

    async def get_level(

        self,

        level_id: UUID,

    ) -> Level:

        result = await self.session.execute(

            select(Level).where(

                Level.id == level_id

            )

        )

        level = result.scalar_one_or_none()

        if level is None:

            raise HTTPException(

                status_code=status.HTTP_404_NOT_FOUND,

                detail="Level not found.",

            )

        return level

    # ============================================================

    # CHECK ENROLLMENT

    # ============================================================

    async def check_enrollment(

        self,

        user_id: UUID,

        course_id: UUID,

    ) -> None:

        result = await self.session.execute(

            select(CourseEnrollment).where(

                CourseEnrollment.user_id == user_id,

                CourseEnrollment.course_id == course_id,

            )

        )

        enrollment = result.scalar_one_or_none()

        if enrollment is None:

            raise HTTPException(

                status_code=status.HTTP_403_FORBIDDEN,

                detail="You are not enrolled in this course.",

            )

    # ============================================================

    # CHECK PREVIOUS LEVEL

    # ============================================================

    async def check_level_unlocked(

        self,

        user_id: UUID,

        level: Level,

    ) -> None:

        # First level is always unlocked

        if level.global_order <= 1:

            return

        result = await self.session.execute(

            select(Level)

            .where(

                Level.course_id == level.course_id,

                Level.global_order < level.global_order,

            )

            .order_by(

                Level.global_order.desc()

            )

            .limit(1)

        )

        previous_level = result.scalar_one_or_none()

        if previous_level is None:

            return

        result = await self.session.execute(

            select(Progress).where(

                Progress.user_id == user_id,

                Progress.level_id == previous_level.id,

            )

        )

        previous_progress = result.scalar_one_or_none()

        if (

            previous_progress is None

            or not previous_progress.completed

        ):

            raise HTTPException(

                status_code=status.HTTP_403_FORBIDDEN,

                detail=(

                    "This level is locked. "

                    "Complete the previous level first."

                ),

            )

    # ============================================================

    # GET / CREATE PROGRESS

    # ============================================================

    async def get_or_create_progress(

        self,

        user_id: UUID,

        level: Level,

    ) -> Progress:

        result = await self.session.execute(

            select(Progress).where(

                Progress.user_id == user_id,

                Progress.level_id == level.id,

            )

        )

        progress = result.scalar_one_or_none()

        if progress is None:

            progress = Progress(

                user_id=user_id,

                course_id=level.course_id,

                level_id=level.id,

                checkpoints_passed=[],

                mcqs_answered=[],

                video_completed=False,

                mcqs_completed=False,

                completed=False,

            )

            self.session.add(progress)

            await self.session.flush()

        return progress

    # ============================================================

    # SUBMIT MCQ

    # ============================================================

    async def submit_mcq(

        self,

        *,

        user_id: UUID,

        level_id: UUID,

        question_index: int,

        selected_option: str,

    ) -> IntroductionMCQResponse:

        # --------------------------------------------------------

        # 1. GET LEVEL

        # --------------------------------------------------------

        level = await self.get_level(

            level_id

        )

        # --------------------------------------------------------

        # 2. CHECK ENROLLMENT

        # --------------------------------------------------------

        await self.check_enrollment(

            user_id,

            level.course_id,

        )

        # --------------------------------------------------------

        # 3. CHECK LEVEL UNLOCKED

        # --------------------------------------------------------

        await self.check_level_unlocked(

            user_id,

            level,

        )

        # --------------------------------------------------------

        # 4. GET MCQS

        # --------------------------------------------------------

        theory = level.theory or {}

        mcqs = (

            theory.get(

                "introduction_mcqs",

                [],

            )

            or []

        )

        if not mcqs:

            raise HTTPException(

                status_code=status.HTTP_400_BAD_REQUEST,

                detail=(

                    "No introduction MCQs "

                    "are configured for this level."

                ),

            )

        # --------------------------------------------------------

        # 5. VALIDATE QUESTION INDEX

        # --------------------------------------------------------

        if (

            question_index < 0

            or question_index >= len(mcqs)

        ):

            raise HTTPException(

                status_code=status.HTTP_400_BAD_REQUEST,

                detail="Invalid question index.",

            )

        # --------------------------------------------------------

        # 6. GET QUESTION

        # --------------------------------------------------------

        question = mcqs[question_index]

        correct_option = str(

            question.get(

                "correct_option",

                "",

            )

        ).strip().upper()

        selected_option = (

            selected_option.strip().upper()

        )

        # --------------------------------------------------------

        # 7. VALIDATE OPTIONS

        # --------------------------------------------------------

        options = question.get(

            "options",

            {},

        )

        if not isinstance(options, dict):

            raise HTTPException(

                status_code=status.HTTP_400_BAD_REQUEST,

                detail="Invalid MCQ options configuration.",

            )

        if selected_option not in options:

            raise HTTPException(

                status_code=status.HTTP_400_BAD_REQUEST,

                detail="Invalid option selected.",

            )

        if not correct_option:

            raise HTTPException(

                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,

                detail=(

                    "Correct option is not configured "

                    "for this question."

                ),

            )

        # --------------------------------------------------------

        # 8. GET PROGRESS

        # --------------------------------------------------------

        progress = await self.get_or_create_progress(

            user_id,

            level,

        )

        # --------------------------------------------------------

        # 9. ALREADY COMPLETED

        # --------------------------------------------------------

        if progress.completed:

            raise HTTPException(

                status_code=status.HTTP_400_BAD_REQUEST,

                detail=(

                    "Level already completed. "

                    "Move to the next level."

                ),

            )

        # --------------------------------------------------------

        # 10. WRONG ANSWER

        # --------------------------------------------------------

        if selected_option != correct_option:

            return IntroductionMCQResponse(

                correct=False,

                message="Wrong answer. Try again.",

                question_index=question_index,

                level_completed=False,

                next_level_unlocked=False,

            )

        # --------------------------------------------------------

        # 11. CORRECT ANSWER

        # --------------------------------------------------------

        answered_questions = [

            int(index)

            for index in (

                progress.mcqs_answered or []

            )

        ]

        if question_index not in answered_questions:

            answered_questions.append(

                question_index

            )

            answered_questions.sort()

            progress.mcqs_answered = (

                answered_questions

            )

        # --------------------------------------------------------

        # 12. CHECK ALL QUESTIONS

        # --------------------------------------------------------

        all_questions_answered = (

            len(answered_questions)

            == len(mcqs)

        )

        # --------------------------------------------------------

        # 13. NOT ALL MCQS COMPLETED

        # --------------------------------------------------------

        if not all_questions_answered:

            await self.session.flush()

            return IntroductionMCQResponse(

                correct=True,

                message=(

                    "Correct answer. "

                    "Continue to the next question."

                ),

                question_index=question_index,

                level_completed=False,

                next_level_unlocked=False,

            )

        # --------------------------------------------------------

    # --------------------------------------------------------

        # 14. ALL MCQS CORRECT

        # --------------------------------------------------------

        progress.mcqs_completed = True

        # Successful completion of all MCQs counts as learning activity.
        # LevelService handles the one-time 100 XP reward.
        await LevelService(self.session).record_learning_activity(
            user_id
        )

        # Centralize completion and the one-time 100 XP reward.

        level_service = LevelService(self.session)

        completion_result = await level_service.check_and_complete_level(

            user_id=user_id,

            level_id=level_id,

        )

        await self.session.flush()

        # --------------------------------------------------------

        # 15. LEVEL COMPLETED

        # --------------------------------------------------------

        return IntroductionMCQResponse(

            correct=True,

            message=(

                "All MCQs answered correctly. "

                "Level completed."

            ),

            question_index=question_index,

            level_completed=bool(

                completion_result.get("level_completed", True)

            ),

            next_level_unlocked=True,

        )
