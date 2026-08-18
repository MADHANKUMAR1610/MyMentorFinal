from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.job_application import JobApplication
from app.repositories.job_application_repository import (
    JobApplicationRepository,
)


class JobApplicationService:

    def __init__(self, session: AsyncSession):
        self.repository = JobApplicationRepository(session)

    async def get_by_id(
        self,
        application_id: UUID,
    ) -> JobApplication | None:

        return await self.repository.get_by_id(application_id)

    async def get_by_job_id(
        self,
        job_id: UUID,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[JobApplication]:

        return await self.repository.get_by_job_id(
            job_id,
            skip=skip,
            limit=limit,
        )

    async def get_by_applicant_user_id(
        self,
        user_id: UUID,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[JobApplication]:

        return await self.repository.get_by_applicant_user_id(
            user_id,
            skip=skip,
            limit=limit,
        )

    async def get_by_email(
        self,
        email: str,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[JobApplication]:

        return await self.repository.get_by_email(
            email,
            skip=skip,
            limit=limit,
        )

    async def get_by_status(
        self,
        status: str,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[JobApplication]:

        return await self.repository.get_by_status(
            status,
            skip=skip,
            limit=limit,
        )

    async def get_by_job_and_user(
        self,
        job_id: UUID,
        user_id: UUID,
    ) -> JobApplication | None:

        return await self.repository.get_by_job_and_user(
            job_id,
            user_id,
        )

    async def create_application(
        self,
        application: JobApplication,
    ) -> JobApplication:

        return await self.repository.create(application)

    async def update_application(
        self,
        application: JobApplication,
    ) -> JobApplication:

        return await self.repository.update(application)

    async def delete_application(
        self,
        application: JobApplication,
    ) -> None:

        await self.repository.delete(application)