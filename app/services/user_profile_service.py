import uuid

from app.models.user_profile import UserProfile
from app.repositories.user_profile_repository import (
    UserProfileRepository,
)


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
        # RESUME URL
        # =====================================================

        resume_url = None

        if (
            profile.resume_file
            and not profile.resume_file.is_deleted
        ):
            resume_url = (
                profile.resume_file.public_url
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

            "profile_photo_file_id": profile.profile_photo_file_id,
            "profile_photo_url": profile_photo_url,

            # =================================================
            # RESUME
            # =================================================

            "resume_file_id": profile.resume_file_id,
            "resume_url": resume_url,

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