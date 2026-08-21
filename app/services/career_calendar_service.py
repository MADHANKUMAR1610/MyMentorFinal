from uuid import UUID

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

        keywords: list[str] = []

        # ---------------------------------------------------------
        # 1. Get generated career from persona result
        # ---------------------------------------------------------

        if persona.result:

            career = persona.result.get("career")

            if career:
                keywords.append(career)

            primary_skill = (
                persona.result.get("primary_skill")
            )

            if primary_skill:
                keywords.append(primary_skill)

        # ---------------------------------------------------------
        # 2. Also use user's original goal
        # ---------------------------------------------------------

        if persona.goal:
            keywords.append(persona.goal)

        # ---------------------------------------------------------
        # 3. Add important words from goal
        # ---------------------------------------------------------

        goal_lower = (
            persona.goal.lower()
            if persona.goal
            else ""
        )

        if "python" in goal_lower:
            keywords.append("Python")

        if "java" in goal_lower:
            keywords.append("Java")

        if ".net" in goal_lower or "c#" in goal_lower:
            keywords.append(".NET")

        if "javascript" in goal_lower:
            keywords.append("JavaScript")

        if "react" in goal_lower:
            keywords.append("React")

        # Remove duplicates
        keywords = list(
            dict.fromkeys(
                keyword.strip()
                for keyword in keywords
                if keyword and keyword.strip()
            )
        )

        if not keywords:
            return []

        courses = (
           await self.course_repository.get_courses_for_career_goal(
    keywords=keywords,
    user_id=user_id,
    limit=20,
)
        )

        return courses