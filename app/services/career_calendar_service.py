from uuid import UUID
import re

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.course import Course
from app.models.career_calendar import CareerCalendar

from app.repositories.career_calendar_repository import (
    CareerCalendarRepository,
)

from app.repositories.career_persona_repository import (
    CareerPersonaRepository,
)

from app.repositories.course_repository import (
    CourseRepository,
)


class CareerCalendarService:

    def __init__(
        self,
        session: AsyncSession,
    ):
        self.session = session

        self.calendar_repository = (
            CareerCalendarRepository(session)
        )

        self.persona_repository = (
            CareerPersonaRepository(session)
        )

        self.course_repository = (
            CourseRepository(session)
        )

    # =========================================================
    # EXTRACT KEYWORDS FROM CAREER PERSONA
    # =========================================================

    def extract_keywords(
        self,
        persona,
    ) -> list[str]:

        result = persona.result or {}

        text_parts: list[str] = []

        # -----------------------------------------------------
        # Career
        # -----------------------------------------------------

        if result.get("career"):
            text_parts.append(
                result["career"]
            )

        # -----------------------------------------------------
        # Primary skill
        # -----------------------------------------------------

        if result.get("primary_skill"):
            text_parts.append(
                result["primary_skill"]
            )

        # -----------------------------------------------------
        # Career overview
        # -----------------------------------------------------

        if result.get("career_overview"):
            text_parts.append(
                result["career_overview"]
            )

        # -----------------------------------------------------
        # Recommended next step
        # -----------------------------------------------------

        if result.get("recommended_next_step"):
            text_parts.append(
                result["recommended_next_step"]
            )

        # -----------------------------------------------------
        # Roadmap
        # -----------------------------------------------------

        for step in result.get("roadmap", []):

            if step.get("title"):
                text_parts.append(
                    step["title"]
                )

            if step.get("description"):
                text_parts.append(
                    step["description"]
                )

        # -----------------------------------------------------
        # Original goal
        # -----------------------------------------------------

        if persona.goal:
            text_parts.append(
                persona.goal
            )

        # -----------------------------------------------------
        # Combine everything
        # -----------------------------------------------------

        text = " ".join(
            text_parts
        ).lower()

        # -----------------------------------------------------
        # Normalize text
        # -----------------------------------------------------

        text = re.sub(
            r"[^a-zA-Z0-9+#.]+",
            " ",
            text,
        )

        words = text.split()

        # -----------------------------------------------------
        # Stop words
        # -----------------------------------------------------

        stop_words = {
            "the",
            "and",
            "or",
            "to",
            "a",
            "an",
            "in",
            "of",
            "for",
            "with",
            "on",
            "as",
            "is",
            "are",
            "be",
            "this",
            "that",
            "from",
            "into",
            "your",
            "their",
            "you",
            "learn",
            "learning",
            "complete",
            "master",
            "focus",
            "build",
            "gain",
            "develop",
            "working",
            "work",
            "skills",
            "skill",
        }

        # -----------------------------------------------------
        # Extract keywords
        # -----------------------------------------------------

        keywords = [
            word
            for word in words
            if word not in stop_words
            and len(word) >= 3
        ]

        # -----------------------------------------------------
        # Remove duplicates
        # -----------------------------------------------------

        keywords = list(
            dict.fromkeys(
                keywords
            )
        )

        return keywords

    # =========================================================
    # ADD TO CAREER CALENDAR
    # =========================================================

    async def add_to_calendar(
        self,
        user_id: UUID,
        career_persona_id: UUID,
        add_to_calendar: bool,
    ) -> CareerCalendar:

        persona = (
            await self.persona_repository
            .get_by_user_id(user_id)
        )

        if persona is None:
            raise ValueError(
                "Career persona not found."
            )

        if persona.id != career_persona_id:
            raise PermissionError(
                "This career persona does not belong to you."
            )

        calendar = (
            await self.calendar_repository
            .get_by_user_and_persona(
                user_id=user_id,
                career_persona_id=career_persona_id,
            )
        )

        if calendar is None:

            calendar = CareerCalendar(
                user_id=user_id,
                career_persona_id=career_persona_id,
                added_to_calendar=add_to_calendar,
            )

            calendar = (
                await self.calendar_repository
                .create_calendar(calendar)
            )

        else:

            calendar.added_to_calendar = (
                add_to_calendar
            )

            calendar = (
                await self.calendar_repository
                .update_calendar(calendar)
            )

        await self.session.commit()

        return calendar

    # =========================================================
    # COURSE SUGGESTIONS
    # =========================================================

    async def get_course_suggestions(
        self,
        user_id: UUID,
    ) -> list[Course]:

        persona = (
            await self.persona_repository
            .get_by_user_id(user_id)
        )

        if persona is None:
            raise ValueError(
                "Career persona not found."
            )

        # -----------------------------------------------------
        # Extract keywords directly from career persona
        # -----------------------------------------------------

        keywords = self.extract_keywords(
            persona
        )

        if not keywords:
            return []

        # -----------------------------------------------------
        # Search courses using those keywords
        # -----------------------------------------------------

        courses = (
            await self.course_repository
            .get_courses_for_career_goal(
                keywords=keywords,
                user_id=user_id,
                limit=20,
            )
        )

        return courses