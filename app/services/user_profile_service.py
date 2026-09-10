import uuid

from app.models.user_profile import UserProfile
from app.models.user import User
from app.repositories.user_profile_repository import (
    UserProfileRepository,
)
from datetime import date, timedelta
from sqlalchemy import select, func

from app.models.progress import Progress
from app.models.level import Level
from app.models.job_application import JobApplication

class UserProfileService:

    def __init__(self, db):

        self.db = db

        self.repository = UserProfileRepository(
            UserProfile,
            db,
        )

    # =========================================================
    # GET PROFILE BY USER ID
    # =========================================================

    async def get_by_user_id(
        self,
        user_id: uuid.UUID,
    ) -> UserProfile | None:

        return await self.repository.get_by_user_id(
            user_id
        )

    # =========================================================
    # GET PROFILE BY ID
    # =========================================================

    async def get_by_id(
        self,
        profile_id: uuid.UUID,
    ) -> UserProfile | None:

        return await self.repository.get_by_id(
            profile_id
        )

    # =========================================================
    # CREATE PROFILE
    # =========================================================

    async def create_profile(
        self,
        profile: UserProfile,
    ) -> UserProfile:

        return await self.repository.create(
            profile
        )

    # =========================================================
    # UPDATE PROFILE
    # =========================================================

    async def update_profile(
        self,
        profile: UserProfile,
    ) -> UserProfile:

        return await self.repository.update(
            profile
        )

    # =========================================================
    # DELETE PROFILE
    # =========================================================

    async def delete_profile(
        self,
        profile: UserProfile,
    ) -> None:

        await self.repository.delete(
            profile
        )

    # =========================================================
    # BUILD PROFILE RESPONSE
    # =========================================================

    def build_profile_response(
        self,
        profile: UserProfile,
    ) -> dict:

        # =====================================================
        # PROFILE PHOTO URL
        # =====================================================

        profile_photo_url = None

        if (
            profile.profile_photo
            and not profile.profile_photo.is_deleted
        ):
            profile_photo_url = (
                profile.profile_photo.public_url
            )

        # =====================================================
        # RESUME DETAILS
        # =====================================================

        resume_url = None
        resume_file_name = None

        if (
            profile.resume_file
            and not profile.resume_file.is_deleted
        ):
            resume_url = (
                profile.resume_file.public_url
            )

            resume_file_name = (
                profile.resume_file.original_filename
            )

        # =====================================================
        # RESPONSE
        # =====================================================

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

            # =================================================
            # PROFILE PHOTO
            # =================================================

            "profile_photo_file_id": (
                profile.profile_photo_file_id
            ),

            "profile_photo_url": (
                profile_photo_url
            ),

            # =================================================
            # RESUME
            # =================================================

            "resume_file_id": (
                profile.resume_file_id
            ),

            "resume_file_name": (
                resume_file_name
            ),

            "resume_url": (
                resume_url
            ),

            # =================================================
            # SKILLS
            # =================================================

            "skills": profile.skills or [],

            # =================================================
            # TIMESTAMPS
            # =================================================

            "created_at": profile.created_at,
            "updated_at": profile.updated_at,
        }

    # =========================================================
    # GET PROFILE SUMMARY
    # =========================================================

    async def get_profile_summary(
        self,
        user_id: uuid.UUID,
    ):
        """
        Calculate the user's profile summary dynamically.
        """

        # =========================================================
        # GET USER
        # =========================================================

        user_result = await self.db.execute(
            select(User).where(
                User.id == user_id
            )
        )

        user = user_result.scalar_one_or_none()

        if user is None:
            raise ValueError("User not found")

        # =========================================================
        # GET PROFILE
        # =========================================================

        profile_result = await self.db.execute(
            select(UserProfile).where(
                UserProfile.user_id == user_id
            )
        )

        profile = profile_result.scalar_one_or_none()

        # =========================================================
        # COMPLETED LEVELS
        # =========================================================

        completed_result = await self.db.execute(
            select(func.count(Progress.id))
            .where(
                Progress.user_id == user_id,
                Progress.completed.is_(True),
            )
        )

        completed_levels = completed_result.scalar_one() or 0

        # =========================================================
        # TOTAL LEVELS
        # =========================================================

        total_levels_result = await self.db.execute(
            select(func.count(Level.id))
        )

        total_levels = total_levels_result.scalar_one() or 0

        # =========================================================
        # XP
        # =========================================================

        xp_result = await self.db.execute(
            select(
                func.coalesce(
                    func.sum(Level.xp),
                    0
                )
            )
            .join(
                Progress,
                Progress.level_id == Level.id
            )
            .where(
                Progress.user_id == user_id,
                Progress.completed.is_(True),
            )
        )

        xp = xp_result.scalar_one() or 0

        # =========================================================
        # JOB APPLICATIONS
        # =========================================================

        applications_result = await self.db.execute(
            select(func.count(JobApplication.id))
            .where(
                JobApplication.applicant_user_id == user_id
            )
        )

        applications = applications_result.scalar_one() or 0

        # =========================================================
        # DAILY LOGIN STREAK
        # =========================================================
        #
        # Streak is based on USER LOGIN activity,
        # NOT Progress activity.
        #
        # User.streak      -> current consecutive login days
        # User.last_active -> last date the user was active
        #

        day_streak = int(user.streak or 0)

        # =========================================================
        # PROFILE SCORE
        # =========================================================

        profile_score = (
            self._calculate_profile_score(profile)
            if profile
            else 0
        )

        # =========================================================
        # BADGE
        # =========================================================

        badge = self._get_profile_badge(
            profile_score
        )

        # =========================================================
        # RETURN RESPONSE
        # =========================================================

        return {
            "id": user_id,
            "name": user.name or "",
            "score": profile_score,
            "badge": badge,
            "xp": int(xp),
            "day_streak": day_streak,
            "completed_levels": int(completed_levels),
            "total_levels": int(total_levels),
            "applications": int(applications),
        }

    # =========================================================
    # UPDATE DAILY LOGIN STREAK
    # =========================================================
# ============================================================
# UPDATE DAILY LOGIN STREAK
# ============================================================

    async def update_login_streak(
    self,
    user_id: uuid.UUID,
):
        """
        Update the user's daily login streak.

        Rules:
        - First login                 -> streak = 1
        - Login again same day        -> streak unchanged
        - Login next consecutive day  -> streak + 1
        - Miss one or more days       -> streak = 1
        """

        # ========================================================
        # GET USER
        # ========================================================

        user_result = await self.db.execute(
            select(User).where(
                User.id == user_id
            )
        )

        user = user_result.scalar_one_or_none()

        if user is None:
            raise ValueError("User not found")

        # ========================================================
        # TODAY
        # ========================================================

        today = date.today()
        today_str = today.isoformat()

        yesterday_str = (
            today - timedelta(days=1)
        ).isoformat()

        # ========================================================
        # FIRST LOGIN
        # ========================================================

        if not user.last_active:

            user.streak = 1
            user.last_active = today_str

        else:

            last_active = str(
                user.last_active
            )

            # ====================================================
            # ALREADY LOGGED IN TODAY
            # ====================================================

            if last_active == today_str:

                # Do nothing.
                # Multiple logins on the same day
                # do not increase the streak.

                pass

            # ====================================================
            # LOGGED IN YESTERDAY
            # ====================================================

            elif last_active == yesterday_str:

                user.streak = (
                    user.streak or 0
                ) + 1

                user.last_active = today_str

            # ====================================================
            # MISSED ONE OR MORE DAYS
            # ====================================================

            else:

                user.streak = 1
                user.last_active = today_str

        # ========================================================
        # SAVE
        # ========================================================

        await self.db.commit()

        await self.db.refresh(user)

        return int(user.streak or 0)

    # =========================================================
    # CALCULATE PROFILE SCORE
    # =========================================================

    def _calculate_profile_score(
        self,
        profile,
    ) -> int:

        total_fields = 8
        completed_fields = 0

        if profile.dob:
            completed_fields += 1

        if profile.profile_category:
            completed_fields += 1

        if profile.education:
            completed_fields += 1

        if profile.class_year:
            completed_fields += 1

        if profile.institution:
            completed_fields += 1

        if profile.career_goal:
            completed_fields += 1

        if profile.career_interests:
            completed_fields += 1

        if profile.resume_file_id:
            completed_fields += 1

        return round(
            (
                completed_fields
                / total_fields
            )
            * 100
        )

    # =========================================================
    # GET PROFILE BADGE
    # =========================================================

    def _get_profile_badge(
        self,
        score: int,
    ) -> str:

        if score >= 90:
            return "Expert"

        if score >= 70:
            return "Advanced"

        if score >= 40:
            return "Intermediate"

        return "Beginner"

    # =========================================================
    # GET SCORE BREAKDOWN
    # =========================================================

    async def get_score_breakdown(
        self,
        user_id: uuid.UUID,
    ) -> dict:

        profile = await self.repository.get_by_user_id(
            user_id
        )

        if not profile:
            return {
                "total_score": 0,
                "max_score": 100,

                "career_clarity": 0,
                "career_clarity_max": 25,

                "learning_progress": 0,
                "learning_progress_max": 25,

                "profile_completeness": 0,
                "profile_completeness_max": 25,

                "consistency": 0,
                "consistency_max": 25,

                "job_readiness": 0,
                "job_readiness_max": 25,
            }

        # =====================================================
        # PROFILE COMPLETENESS
        # =====================================================

        profile_score = (
            self._calculate_profile_score(
                profile
            )
        )

        # =====================================================
        # CAREER CLARITY
        # =====================================================

        career_clarity = 0

        if profile.career_goal:
            career_clarity += 15

        if profile.career_interests:
            career_clarity += 10

        # =====================================================
        # LEARNING PROGRESS
        # =====================================================

        # Currently no learning-progress data
        # is connected
        learning_progress = 0

        # =====================================================
        # CONSISTENCY
        # =====================================================

        # Currently no activity/streak data
        # is connected
        consistency = 0

        # =====================================================
        # JOB READINESS
        # =====================================================

        job_readiness = 0

        if profile.resume_file_id:
            job_readiness += 15

        if profile.skills:
            job_readiness += 10

        # =====================================================
        # TOTAL SCORE
        # =====================================================

        total_score = (
            career_clarity
            + learning_progress
            + profile_score
            + consistency
            + job_readiness
        )

        # =====================================================
        # RESPONSE
        # =====================================================

        return {
            "total_score": total_score,
            "max_score": 125,

            "career_clarity": career_clarity,
            "career_clarity_max": 25,

            "learning_progress": learning_progress,
            "learning_progress_max": 25,

            "profile_completeness": profile_score,
            "profile_completeness_max": 100,

            "consistency": consistency,
            "consistency_max": 25,

            "job_readiness": job_readiness,
            "job_readiness_max": 25,
        }