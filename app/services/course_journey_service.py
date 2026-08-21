from collections import defaultdict
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.course_journey_repository import (
    CourseJourneyRepository,
)


class CourseJourneyService:
    """
    Service responsible for building the Course Journey
    shown in the student's My Journey page.
    """

    def __init__(
        self,
        session: AsyncSession,
    ):
        self.repository = CourseJourneyRepository(
            session
        )

    async def get_course_journey(
        self,
        user_id: UUID,
        course_id: UUID,
    ) -> dict:

        # =====================================================
        # 1. GET COURSE
        # =====================================================

        course = await self.repository.get_course(
            course_id
        )

        if course is None:
            raise ValueError(
                "Course not found."
            )

        # =====================================================
        # 2. CHECK ENROLLMENT
        # =====================================================

        enrollment = (
            await self.repository.get_user_enrollment(
                user_id=user_id,
                course_id=course_id,
            )
        )

        if enrollment is None:
            raise PermissionError(
                "You are not enrolled in this course."
            )

        # =====================================================
        # 3. GET LEVELS
        # =====================================================

        levels = await self.repository.get_course_levels(
            course_id
        )

        # =====================================================
        # 4. GET USER PROGRESS
        # =====================================================

        progress_records = (
            await self.repository.get_user_progress(
                user_id=user_id,
                course_id=course_id,
            )
        )

        progress_by_level = {
            progress.level_id: progress
            for progress in progress_records
        }

        # =====================================================
        # 5. BUILD LEVEL DATA
        # =====================================================

        level_data = []

        for level in levels:

            checkpoints = (
                await self.repository
                .get_level_checkpoints(
                    level.id
                )
            )

            progress = progress_by_level.get(
                level.id
            )

            passed_checkpoints = set()

            if progress is not None:
                for checkpoint_id in (
                    progress.checkpoints_passed or []
                ):
                    passed_checkpoints.add(
                        str(checkpoint_id)
                    )

            checkpoint_data = []

            completed_checkpoint_count = 0

            for checkpoint in checkpoints:

                is_completed = (
                    str(checkpoint.id)
                    in passed_checkpoints
                )

                if is_completed:
                    completed_checkpoint_count += 1

                checkpoint_data.append(
                    {
                        "id": checkpoint.id,
                        "checkpoint_order": (
                            checkpoint.checkpoint_order
                        ),
                        "title": checkpoint.title,
                        "xp": checkpoint.xp,
                        "completed": is_completed,
                    }
                )

            level_completed = (
                progress.completed
                if progress is not None
                else False
            )

            level_data.append(
                {
                    "level": level,
                    "checkpoints": checkpoint_data,
                    "completed_checkpoints": (
                        completed_checkpoint_count
                    ),
                    "total_checkpoints": len(
                        checkpoints
                    ),
                    "completed": level_completed,
                    "unlocked": False,
                }
            )

        # =====================================================
        # 6. CALCULATE UNLOCK STATUS
        # =====================================================

        previous_level_completed = True

        for item in level_data:

            item["unlocked"] = (
                previous_level_completed
            )

            previous_level_completed = (
                item["completed"]
            )

        # =====================================================
        # 7. GROUP BY STAGE
        # =====================================================

        stages = defaultdict(list)

        for item in level_data:

            stages[
                (
                    item["level"].stage,
                    item["level"].stage_order,
                )
            ].append(item)

        stage_data = []

        for (
            stage_name,
            stage_order,
        ), stage_levels in sorted(
            stages.items(),
            key=lambda item: item[0][1],
        ):

            completed_levels = sum(
                1
                for item in stage_levels
                if item["completed"]
            )

            levels_response = []

            for item in stage_levels:

                level = item["level"]

                levels_response.append(
                    {
                        "id": level.id,
                        "level_number": (
                            level.level_number
                        ),
                        "title": level.title,
                        "description": (
                            level.description
                        ),
                        "xp": level.xp,
                        "completed_checkpoints": (
                            item[
                                "completed_checkpoints"
                            ]
                        ),
                        "total_checkpoints": (
                            item[
                                "total_checkpoints"
                            ]
                        ),
                        "completed": (
                            item["completed"]
                        ),
                        "unlocked": (
                            item["unlocked"]
                        ),
                        "checkpoints": (
                            item["checkpoints"]
                        ),
                    }
                )

            stage_data.append(
                {
                    "stage": stage_name,
                    "stage_order": stage_order,
                    "completed_levels": (
                        completed_levels
                    ),
                    "total_levels": len(
                        stage_levels
                    ),
                    "levels": levels_response,
                }
            )

        # =====================================================
        # 8. OVERALL PROGRESS
        # =====================================================

        completed_levels = sum(
            1
            for item in level_data
            if item["completed"]
        )

        total_levels = len(level_data)

        # =====================================================
        # 9. FINAL RESPONSE
        # =====================================================

        return {
            "course": {
                "id": course.id,
                "title": course.title,
                "description": course.description,
                "language": course.language,
                "difficulty": course.difficulty,
                "duration": course.duration,
                "thumbnail": course.thumbnail,
            },
            "progress": {
                "completed_levels": completed_levels,
                "total_levels": total_levels,
            },
            "stages": stage_data,
        }