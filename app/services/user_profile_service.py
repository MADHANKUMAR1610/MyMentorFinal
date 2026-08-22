from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user_profile import UserProfile
from app.repositories.user_profile_repository import UserProfileRepository


class UserProfileService:

    def __init__(self, session: AsyncSession):
        self.repository = UserProfileRepository(session)

    async def get_by_id(
        self,
        profile_id: UUID,
    ) -> UserProfile | None:

        return await self.repository.get_by_id(profile_id)

    async def get_by_user_id(
        self,
        user_id: UUID,
    ) -> UserProfile | None:

        return await self.repository.get_by_user_id(user_id)

    async def get_by_profile_category(
        self,
        profile_category: str,
    ) -> list[UserProfile]:

        return await self.repository.get_by_profile_category(
            profile_category
        )

    async def create_profile(
        self,
        profile: UserProfile,
    ) -> UserProfile:

        return await self.repository.create(profile)

    async def update_profile(
        self,
        profile: UserProfile,
    ) -> UserProfile:

        return await self.repository.update(profile)

    async def delete_profile(
        self,
        profile: UserProfile,
    ) -> None:

        await self.repository.delete(profile)
    # ========================================================
    # PROFILE SUMMARY
    # ========================================================

    async def get_profile_summary(
        self,
        user: User,
        profile: UserProfile | None,
    ) -> dict:

        completed_levels = (
            await self.repository.get_completed_levels_count(
                user.id
            )
        )

        total_levels = (
            await self.repository.get_total_levels_count()
        )

        applications = (
            await self.repository.get_user_applications_count(
                user.id
            )
        )

        # ----------------------------------------------------
        # SCORE CALCULATION
        # ----------------------------------------------------

        career_clarity = 0

        if profile and profile.career_goal:
            career_clarity = 20

        # Learning Progress = 40 points
        if total_levels > 0:
            learning_progress = round(
                (completed_levels / total_levels) * 40
            )
        else:
            learning_progress = 0

        # Profile Completeness = 20 points
        profile_completeness = 0

        if profile:

            profile_fields = [
                profile.dob,
                profile.profile_category,
                profile.education,
                profile.class_year,
                profile.institution,
                profile.career_goal,
                profile.career_interests,
            ]

            completed_profile_fields = sum(
                1
                for field in profile_fields
                if field is not None
                and str(field).strip() != ""
            )

            profile_completeness = round(
                (
                    completed_profile_fields
                    / len(profile_fields)
                )
                * 20
            )

        # Consistency = 10 points
        consistency = min(
            max(user.streak, 0),
            10,
        )

        # Job Readiness = 10 points
        job_readiness = 10 if applications > 0 else 0

        total_score = (
            career_clarity
            + learning_progress
            + profile_completeness
            + consistency
            + job_readiness
        )

        badge = self._get_badge(total_score)

        return {
            "score": total_score,
            "badge": badge,
            "name": user.name,
            "career_goal": (
                profile.career_goal
                if profile
                else None
            ),
            "xp": user.xp,
            "day_streak": user.streak,
            "completed_levels": completed_levels,
            "total_levels": total_levels,
            "applications": applications,
        }

    # ========================================================
    # SCORE BREAKDOWN
    # ========================================================

    async def get_score_breakdown(
        self,
        user: User,
        profile: UserProfile | None,
    ) -> dict:

        completed_levels = (
            await self.repository.get_completed_levels_count(
                user.id
            )
        )

        total_levels = (
            await self.repository.get_total_levels_count()
        )

        applications = (
            await self.repository.get_user_applications_count(
                user.id
            )
        )

        # ----------------------------------------------------
        # Career Clarity - 20
        # ----------------------------------------------------

        career_clarity = 0

        if profile and profile.career_goal:
            career_clarity = 20

        # ----------------------------------------------------
        # Learning Progress - 40
        # ----------------------------------------------------

        if total_levels > 0:
            learning_progress = round(
                (completed_levels / total_levels) * 40
            )
        else:
            learning_progress = 0

        # ----------------------------------------------------
        # Profile Completeness - 20
        # ----------------------------------------------------

        profile_completeness = 0

        if profile:

            profile_fields = [
                profile.dob,
                profile.profile_category,
                profile.education,
                profile.class_year,
                profile.institution,
                profile.career_goal,
                profile.career_interests,
            ]

            completed_profile_fields = sum(
                1
                for field in profile_fields
                if field is not None
                and str(field).strip() != ""
            )

            profile_completeness = round(
                (
                    completed_profile_fields
                    / len(profile_fields)
                )
                * 20
            )

        # ----------------------------------------------------
        # Consistency - 10
        # ----------------------------------------------------

        consistency = min(
            max(user.streak, 0),
            10,
        )

        # ----------------------------------------------------
        # Job Readiness - 10
        # ----------------------------------------------------

        job_readiness = 10 if applications > 0 else 0

        total_score = (
            career_clarity
            + learning_progress
            + profile_completeness
            + consistency
            + job_readiness
        )

        return {
            "total_score": total_score,
            "max_score": 100,

            "career_clarity": career_clarity,
            "career_clarity_max": 20,

            "learning_progress": learning_progress,
            "learning_progress_max": 40,

            "profile_completeness": profile_completeness,
            "profile_completeness_max": 20,

            "consistency": consistency,
            "consistency_max": 10,

            "job_readiness": job_readiness,
            "job_readiness_max": 10,
        }

    # ========================================================
    # BADGE
    # ========================================================

    @staticmethod
    def _get_badge(score: int) -> str:

        if score >= 80:
            return "Career Champion"

        if score >= 60:
            return "Rising Star"

        if score >= 40:
            return "Rising Star"

        if score >= 20:
            return "Getting Started"

        return "New Explorer"