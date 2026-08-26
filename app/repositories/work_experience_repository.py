from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.work_experience import WorkExperience


class WorkExperienceRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    # =========================================================
    # CREATE
    # =========================================================

    async def create(
        self,
        work_experience: WorkExperience,
    ) -> WorkExperience:

        self.session.add(work_experience)

        await self.session.commit()

        await self.session.refresh(
            work_experience
        )

        return work_experience

    # =========================================================
    # GET ALL BY PROFILE
    # =========================================================

    async def get_all_by_profile(
        self,
        user_profile_id: UUID,
    ) -> list[WorkExperience]:

        result = await self.session.execute(
            select(WorkExperience)
            .where(
                WorkExperience.user_profile_id
                == user_profile_id
            )
            .order_by(
                WorkExperience.start_date.desc()
            )
        )

        return list(
            result.scalars().all()
        )

    # =========================================================
    # GET BY ID
    # =========================================================

    async def get_by_id(
        self,
        work_experience_id: UUID,
        user_profile_id: UUID,
    ) -> WorkExperience | None:

        result = await self.session.execute(
            select(WorkExperience).where(
                WorkExperience.id
                == work_experience_id,
                WorkExperience.user_profile_id
                == user_profile_id,
            )
        )

        return result.scalar_one_or_none()

    # =========================================================
    # UPDATE
    # =========================================================

    async def update(
        self,
        work_experience: WorkExperience,
    ) -> WorkExperience:

        self.session.add(
            work_experience
        )

        await self.session.commit()

        await self.session.refresh(
            work_experience
        )

        return work_experience

    # =========================================================
    # DELETE
    # =========================================================

    async def delete(
        self,
        work_experience: WorkExperience,
    ) -> None:

        await self.session.delete(
            work_experience
        )

        await self.session.commit()