from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.work_experience import WorkExperience
from app.schemas.work_experience import (
    WorkExperienceCreate,
    WorkExperienceUpdate,
)


class WorkExperienceService:

    def __init__(self, session: AsyncSession):
        self.session = session

    # =========================================================
    # CREATE
    # =========================================================

    async def create(
        self,
        user_profile_id: UUID,
        data: WorkExperienceCreate,
    ) -> WorkExperience:

        work_experience = WorkExperience(
            user_profile_id=user_profile_id,
            company_name=data.company_name,
            job_title=data.job_title,
            employment_type=data.employment_type,
            location=data.location,
            start_date=data.start_date,
            end_date=data.end_date,
            currently_working=data.currently_working,
            description=data.description,
            skills=data.skills,
        )

        self.session.add(work_experience)

        await self.session.commit()

        await self.session.refresh(work_experience)

        return work_experience

    # =========================================================
    # GET ALL
    # =========================================================

    async def get_all(
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

        return list(result.scalars().all())

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
                WorkExperience.id == work_experience_id,
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
        data: WorkExperienceUpdate,
    ) -> WorkExperience:

        if data.company_name is not None:
            work_experience.company_name = (
                data.company_name
            )

        if data.job_title is not None:
            work_experience.job_title = (
                data.job_title
            )

        if data.employment_type is not None:
            work_experience.employment_type = (
                data.employment_type
            )

        if data.location is not None:
            work_experience.location = (
                data.location
            )

        if data.start_date is not None:
            work_experience.start_date = (
                data.start_date
            )

        if data.end_date is not None:
            work_experience.end_date = (
                data.end_date
            )

        if data.currently_working is not None:
            work_experience.currently_working = (
                data.currently_working
            )

        if data.description is not None:
            work_experience.description = (
                data.description
            )

        if data.skills is not None:
            work_experience.skills = (
                data.skills
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