from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.career_persona_repository import (
    CareerPersonaRepository,
)
from app.repositories.course_enrollment_repository import (
    CourseEnrollmentRepository,
)
from app.repositories.job_application_repository import (
    JobApplicationRepository,
)


class JourneyService:
    """
    Service responsible for building the user's
    dynamic MyMentor journey.
    """

    def __init__(self, session: AsyncSession):
        self.career_persona_repository = (
            CareerPersonaRepository(session)
        )

        self.course_enrollment_repository = (
            CourseEnrollmentRepository(session)
        )

        self.job_application_repository = (
            JobApplicationRepository(session)
        )

    async def get_user_journey(
        self,
        user_id: UUID,
    ) -> dict:
        """
        Build the user's journey based on
        actual database records.
        """

        # =====================================================
        # 1. CAREER PERSONA
        # =====================================================

        career_persona = (
            await self.career_persona_repository
            .get_by_user_id(user_id)
        )

        career_path_done = career_persona is not None

        career_goal = (
            career_persona.goal
            if career_persona is not None
            else "Discover your career path"
        )

        # =====================================================
        # 2. COURSE ENROLLMENTS
        # =====================================================

        enrollments = (
            await self.course_enrollment_repository
            .get_user_enrollments(user_id)
        )

        learning_done = len(enrollments) > 0

        # =====================================================
        # 3. JOB APPLICATIONS
        # =====================================================

        applications = (
            await self.job_application_repository
            .get_by_applicant_user_id(
                user_id,
                skip=0,
                limit=1,
            )
        )

        job_done = len(applications) > 0

        # =====================================================
        # 4. BUILD JOURNEY
        # =====================================================

        return {
            "journey": [
                {
                    "key": "joined",
                    "title": "Joined MyMentor",
                    "description": (
                        "Your career journey began here."
                    ),
                    "done": True,
                    "icon": "sparkles",
                },
                {
                    "key": "career_path",
                    "title": "Discovered your career path",
                    "description": (
                        f"Goal: {career_goal}"
                    ),
                    "done": career_path_done,
                    "icon": "compass",
                },
                {
                    "key": "learning",
                    "title": "Start learning on SkillHub",
                    "description": (
                        "Complete your first level "
                        "to build skills."
                    ),
                    "done": learning_done,
                    "icon": "graduation-cap",
                },
                {
                    "key": "job",
                    "title": "Apply to your first job",
                    "description": (
                        "Explore partner companies and "
                        "apply on the job board."
                    ),
                    "done": job_done,
                    "icon": "briefcase",
                },
            ]
        }