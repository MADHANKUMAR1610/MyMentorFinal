from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.job_application import JobApplication
from app.repositories.job_application_repository import (
    JobApplicationRepository,
)


class JobApplicationService:

    def __init__(self, session: AsyncSession):
        self.repository = JobApplicationRepository(session)

    # ============================================================
    # GET APPLICATION BY ID
    # ============================================================

    async def get_by_id(
        self,
        application_id: UUID,
    ) -> JobApplication | None:

        return await self.repository.get_by_id(
            application_id
        )

    # ============================================================
    # GET APPLICATIONS BY JOB
    # ============================================================

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

    # ============================================================
    # GET APPLICATIONS BY APPLICANT
    # ============================================================

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

    # ============================================================
    # GET APPLICATIONS BY EMAIL
    # ============================================================

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

    # ============================================================
    # GET APPLICATIONS BY STATUS
    # ============================================================

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

    # ============================================================
    # GET APPLICATION BY JOB AND USER
    # ============================================================

    async def get_by_job_and_user(
        self,
        job_id: UUID,
        user_id: UUID,
    ) -> JobApplication | None:

        return await self.repository.get_by_job_and_user(
            job_id,
            user_id,
        )

    # ============================================================
    # CREATE APPLICATION
    # ============================================================

    async def create_application(
        self,
        application: JobApplication,
    ) -> JobApplication:

        return await self.repository.create(
            application
        )

    # ============================================================
    # UPDATE APPLICATION
    # ============================================================

    async def update_application(
        self,
        application: JobApplication,
    ) -> JobApplication:

        return await self.repository.update(
            application
        )

    # ============================================================
    # DELETE APPLICATION
    # ============================================================

    async def delete_application(
        self,
        application: JobApplication,
    ) -> None:

        await self.repository.delete(
            application
        )
    async def update_organization_application_status(
        self,
        application_id: UUID,
        company_id: UUID,
        new_status: str,
    ) -> JobApplication | None:

        return await (
        self.repository
        .update_organization_application_status(
            application_id=application_id,
            company_id=company_id,
            new_status=new_status,
        )
        )
    # ============================================================
    # ORGANIZATION - GET ALL APPLICATIONS
    # ============================================================

    async def get_by_company_id(
        self,
        company_id: UUID,
        *,
        skip: int = 0,
        limit: int = 100,
        status: str | None = None,
        name: str | None = None,
        email: str | None = None,
        job_id: UUID | None = None,
    ) -> list[JobApplication]:

        return await self.repository.get_by_company_id(
            company_id,
            skip=skip,
            limit=limit,
            status=status,
            name=name,
            email=email,
            job_id=job_id,
        )

    # ============================================================
    # ORGANIZATION - GET APPLICATIONS FOR A JOB
    # ============================================================

    async def get_by_organization_job(
        self,
        job_id: UUID,
        company_id: UUID,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[JobApplication]:

        return await self.repository.get_by_organization_job(
            job_id=job_id,
            company_id=company_id,
            skip=skip,
            limit=limit,
        )

    # ============================================================
    # ORGANIZATION - GET SINGLE APPLICATION
    # ============================================================

    async def get_organization_application(
        self,
        application_id: UUID,
        company_id: UUID,
    ) -> JobApplication | None:

        return await self.repository.get_organization_application(
            application_id=application_id,
            company_id=company_id,
        )
    async def update_organization_application_status(
        self,
        application_id: UUID,
        company_id: UUID,
        new_status: str,
    ) -> JobApplication | None:

        application = (
            await self.repository.get_organization_application(
                application_id,
                company_id,
            )
        )

        if application is None:
            return None

        application.status = new_status

        return await self.repository.update(
            application
        )

    async def get_company_application_stats(
        self,
        company_id: UUID,
    ) -> dict[str, int]:

        return await self.repository.get_company_application_stats(
            company_id
        )
    async def get_organization_application_stats(
        self,
        company_id: UUID,
    ) -> dict[str, int]:

        return await self.repository.get_status_counts_by_company_id(
            company_id
        )