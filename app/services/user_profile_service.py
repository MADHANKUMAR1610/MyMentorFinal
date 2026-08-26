from uuid import UUID

from app.models.user import User
from app.models.user_profile import UserProfile

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.user_profile_repository import (
    UserProfileRepository,
)


class UserProfileService:

    def __init__(self, session: AsyncSession):
        self.repository = UserProfileRepository(session)

    # ========================================================
    # GET BY ID
    # ========================================================

    async def get_by_id(
        self,
        profile_id: UUID,
    ) -> UserProfile | None:

        return await self.repository.get_by_id(
            profile_id
        )

    # ========================================================
    # GET BY USER ID
    # ========================================================

    async def get_by_user_id(
        self,
        user_id: UUID,
    ) -> UserProfile | None:

        return await self.repository.get_by_user_id(
            user_id
        )

    # ========================================================
    # GET BY PROFILE CATEGORY
    # ========================================================

    async def get_by_profile_category(
        self,
        profile_category: str,
    ) -> list[UserProfile]:

        return await self.repository.get_by_profile_category(
            profile_category
        )

    # ========================================================
    # CREATE PROFILE
    # ========================================================

    async def create_profile(
        self,
        profile: UserProfile,
    ) -> UserProfile:

        return await self.repository.create(
            profile
        )

    # ========================================================
    # UPDATE PROFILE
    # ========================================================

    async def update_profile(
        self,
        profile: UserProfile,
    ) -> UserProfile:

        return await self.repository.update(
            profile
        )

    # ========================================================
    # DELETE PROFILE
    # ========================================================

    async def delete_profile(
        self,
        profile: UserProfile,
    ) -> None:

        await self.repository.delete(
            profile
        )

    # ========================================================
    # PROFILE RESPONSE
    # ========================================================

    def build_profile_response(
        self,
        profile: UserProfile,
    ) -> dict:

        profile_photo_url = None

        if (
            profile.profile_photo_file is not None
            and not profile.profile_photo_file.is_deleted
        ):
            profile_photo_url = (
                profile.profile_photo_file.public_url
            )

        return {
            "id": profile.id,
            "user_id": profile.user_id,

            "dob": profile.dob,
            "age": profile.age,

            "profile_category": profile.profile_category,
            "education": profile.education,
            "class_year": profile.class_year,
            "institution": profile.institution,

            "career_goal": profile.career_goal,
            "career_interests": profile.career_interests,

            "profile_photo_file_id": (
                profile.profile_photo_file_id
            ),

            "profile_photo_url": profile_photo_url,

            "created_at": profile.created_at,
            "updated_at": profile.updated_at,
        }

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

        career_clarity = 0

        if profile and profile.career_goal:
            career_clarity = 20

        if total_levels > 0:
            learning_progress = round(
                (completed_levels / total_levels) * 40
            )
        else:
            learning_progress = 0

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

        consistency = min(
            max(user.streak, 0),
            10,
        )

        job_readiness = (
            10
            if applications > 0
            else 0
        )

        total_score = (
            career_clarity
            + learning_progress
            + profile_completeness
            + consistency
            + job_readiness
        )

        badge = self._get_badge(
            total_score
        )

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

        career_clarity = 0

        if profile and profile.career_goal:
            career_clarity = 20

        if total_levels > 0:
            learning_progress = round(
                (completed_levels / total_levels) * 40
            )
        else:
            learning_progress = 0

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

        consistency = min(
            max(user.streak, 0),
            10,
        )

        job_readiness = (
            10
            if applications > 0
            else 0
        )

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
    def _get_badge(
        score: int,
    ) -> str:

        if score >= 80:
            return "Career Champion"

        if score >= 60:
            return "Rising Star"

        if score >= 40:
            return "Rising Star"

        if score >= 20:
            return "Getting Started"

        return "New Explorer"