import uuid

from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.models.user_profile import UserProfile
from app.repositories.base import BaseRepository


class UserProfileRepository(
    BaseRepository[UserProfile]
):

    # =========================================================
    # GET BY USER ID
    # =========================================================

    async def get_by_user_id(
        self,
        user_id: uuid.UUID,
    ) -> UserProfile | None:

        result = await self.session.execute(
            select(UserProfile)
            .options(
                joinedload(
                    UserProfile.profile_photo
                ),
                joinedload(
                    UserProfile.resume_file
                ),
                joinedload(
                    UserProfile.work_experiences
                ),
            )
            .where(
                UserProfile.user_id == user_id
            )
        )

        return (
            result
            .unique()
            .scalar_one_or_none()
        )

    # =========================================================
    # GET BY PROFILE ID
    # =========================================================

    async def get_by_id(
        self,
        profile_id: uuid.UUID,
    ) -> UserProfile | None:

        result = await self.session.execute(
            select(UserProfile)
            .options(
                joinedload(
                    UserProfile.profile_photo
                ),
                joinedload(
                    UserProfile.resume_file
                ),
                joinedload(
                    UserProfile.work_experiences
                ),
            )
            .where(
                UserProfile.id == profile_id
            )
        )

        return (
            result
            .unique()
            .scalar_one_or_none()
        )

    # =========================================================
    # GET BY CAREER GOAL
    # =========================================================

    async def get_by_career_goal(
        self,
        career_goal: str,
    ) -> list[UserProfile]:

        result = await self.session.execute(
            select(UserProfile)
            .options(
                joinedload(
                    UserProfile.profile_photo
                ),
                joinedload(
                    UserProfile.resume_file
                ),
            )
            .where(
                UserProfile.career_goal == career_goal
            )
        )

        return (
            result
            .unique()
            .scalars()
            .all()
        )

    # =========================================================
    # GET BY PROFILE CATEGORY
    # =========================================================

    async def get_by_profile_category(
        self,
        profile_category: str,
    ) -> list[UserProfile]:

        result = await self.session.execute(
            select(UserProfile)
            .options(
                joinedload(
                    UserProfile.profile_photo
                ),
                joinedload(
                    UserProfile.resume_file
                ),
            )
            .where(
                UserProfile.profile_category
                == profile_category
            )
        )

        return (
            result
            .unique()
            .scalars()
            .all()
        )