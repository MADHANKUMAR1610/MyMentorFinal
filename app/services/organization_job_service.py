from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.organization_repository import (
    OrganizationRepository,
)

from app.repositories.organization_job_repository import (
    OrganizationJobRepository,
)

from app.schemas.organization_job import (
    OrganizationJobCreate,
    OrganizationJobDraftCreate,
    OrganizationJobUpdate,
)


class OrganizationJobService:

    def __init__(self, db: AsyncSession):

        self.organization_repository = (
            OrganizationRepository(db)
        )

        self.job_repository = (
            OrganizationJobRepository(db)
        )

    # ============================================================
    # GET MY JOBS
    # ============================================================

    async def get_my_jobs(
        self,
        user_id: UUID,
    ):

        # --------------------------------------------------------
        # Find organization
        # --------------------------------------------------------

        company = await (
            self.organization_repository
            .get_by_admin_user_id(user_id)
        )

        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found for this user",
            )

        # --------------------------------------------------------
        # Get organization's jobs
        # --------------------------------------------------------

        return await (
            self.job_repository
            .get_jobs_by_company_id(company.id)
        )

    # ============================================================
    # CREATE JOB
    # ============================================================

    async def create_job(
        self,
        user_id: UUID,
        data: OrganizationJobCreate,
    ):

        # --------------------------------------------------------
        # Find organization
        # --------------------------------------------------------

        company = await (
            self.organization_repository
            .get_by_admin_user_id(user_id)
        )

        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found for this user",
            )

        # --------------------------------------------------------
        # Prepare job data
        # --------------------------------------------------------

        job_data = data.model_dump()

        # --------------------------------------------------------
        # Company information
        # --------------------------------------------------------

        job_data["company_name"] = company.name

        # --------------------------------------------------------
        # Screening questions
        #
        # Pydantic objects -> dictionaries
        # --------------------------------------------------------

        job_data["screening_questions"] = [
            question.model_dump()
            for question in data.screening_questions
        ]

        # --------------------------------------------------------
        # ATS configuration
        #
        # Pydantic object -> dictionary
        # --------------------------------------------------------

        job_data["ats_configuration"] = (
            data.ats_configuration.model_dump()
        )

        # --------------------------------------------------------
        # Compatibility with existing Job.skills field
        #
        # Existing APIs already use "skills".
        # Use required_skills for that field.
        # --------------------------------------------------------

        job_data["skills"] = data.required_skills

        # --------------------------------------------------------
        # Create job
        # --------------------------------------------------------

        return await self.job_repository.create(
            company_id=company.id,
            posted_by=user_id,
            data=job_data,
        )

    # ============================================================
    # SAVE JOB DRAFT
    # ============================================================

    async def save_draft(
        self,
        user_id: UUID,
        data: OrganizationJobDraftCreate,
    ):
        # --------------------------------------------------------
        # Find organization
        # --------------------------------------------------------

        company = await (
            self.organization_repository
            .get_by_admin_user_id(user_id)
        )

        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found for this user",
            )

        # --------------------------------------------------------
        # Prepare draft data
        # --------------------------------------------------------

        job_data = data.model_dump()

        # --------------------------------------------------------
        # Company information
        # --------------------------------------------------------

        job_data["company_name"] = company.name

        # --------------------------------------------------------
        # Screening questions
        # --------------------------------------------------------

        job_data["screening_questions"] = [
            question.model_dump()
            for question in data.screening_questions
        ]

        # --------------------------------------------------------
        # ATS configuration
        # --------------------------------------------------------

        job_data["ats_configuration"] = (
            data.ats_configuration.model_dump()
        )

        # --------------------------------------------------------
        # Keep old skills field synchronized
        # --------------------------------------------------------

        job_data["skills"] = data.required_skills

        # --------------------------------------------------------
        # Draft status
        # --------------------------------------------------------

        job_data["status"] = "draft"

        # --------------------------------------------------------
        # Create draft
        # --------------------------------------------------------

        return await self.job_repository.create(
            company_id=company.id,
            posted_by=user_id,
            data=job_data,
        )
    # ============================================================
    # GET JOB
    # ============================================================

    async def get_job(
        self,
        user_id: UUID,
        job_id: UUID,
    ):

        # --------------------------------------------------------
        # Find organization
        # --------------------------------------------------------

        company = await (
            self.organization_repository
            .get_by_admin_user_id(user_id)
        )

        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found for this user",
            )

        # --------------------------------------------------------
        # Find job belonging to organization
        # --------------------------------------------------------

        job = await self.job_repository.get_by_id(
            job_id=job_id,
            company_id=company.id,
        )

        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found",
            )

        return job

    # ============================================================
    # UPDATE JOB
    # ============================================================

    async def update_job(
        self,
        user_id: UUID,
        job_id: UUID,
        data: OrganizationJobUpdate,
    ):

        # --------------------------------------------------------
        # Find organization
        # --------------------------------------------------------

        company = await (
            self.organization_repository
            .get_by_admin_user_id(user_id)
        )

        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found for this user",
            )

        # --------------------------------------------------------
        # Find organization's job
        # --------------------------------------------------------

        job = await self.job_repository.get_by_id(
            job_id=job_id,
            company_id=company.id,
        )

        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found",
            )

        # --------------------------------------------------------
        # Prepare update data
        # --------------------------------------------------------

        update_data = data.model_dump(
            exclude_unset=True
        )

        # --------------------------------------------------------
        # Screening questions
        #
        # Convert Pydantic objects to dictionaries
        # --------------------------------------------------------

        if data.screening_questions is not None:

            update_data["screening_questions"] = [
                question.model_dump()
                for question in data.screening_questions
            ]

        # --------------------------------------------------------
        # ATS configuration
        #
        # Convert Pydantic object to dictionary
        # --------------------------------------------------------

        if data.ats_configuration is not None:

            update_data["ats_configuration"] = (
                data.ats_configuration.model_dump()
            )

        # --------------------------------------------------------
        # Keep old "skills" field synchronized
        # --------------------------------------------------------

        if data.required_skills is not None:

            update_data["skills"] = (
                data.required_skills
            )

        # --------------------------------------------------------
        # Update
        # --------------------------------------------------------

        return await self.job_repository.update(
            job,
            update_data,
        )

    # ============================================================
    # DELETE JOB
    # ============================================================

    async def delete_job(
        self,
        user_id: UUID,
        job_id: UUID,
    ):

        # --------------------------------------------------------
        # Find organization
        # --------------------------------------------------------

        company = await (
            self.organization_repository
            .get_by_admin_user_id(user_id)
        )

        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found for this user",
            )

        # --------------------------------------------------------
        # Find organization's job
        # --------------------------------------------------------

        job = await self.job_repository.get_by_id(
            job_id=job_id,
            company_id=company.id,
        )

        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found",
            )

        # --------------------------------------------------------
        # Delete job
        # --------------------------------------------------------

        await self.job_repository.delete(job)

    # ============================================================
    # UPDATE JOB STATUS
    # ============================================================

    async def update_job_status(
        self,
        user_id: UUID,
        job_id: UUID,
        new_status: str,
    ):

        # --------------------------------------------------------
        # Find organization
        # --------------------------------------------------------

        company = await (
            self.organization_repository
            .get_by_admin_user_id(user_id)
        )

        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found for this user",
            )

        # --------------------------------------------------------
        # Find organization's job
        # --------------------------------------------------------

        job = await self.job_repository.get_by_id(
            job_id=job_id,
            company_id=company.id,
        )

        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found",
            )

        # --------------------------------------------------------
        # Update status
        # --------------------------------------------------------

        return await self.job_repository.update_status(
            job,
            new_status,
        )

    # ============================================================
    # DUPLICATE JOB
    # ============================================================

    async def duplicate_job(
        self,
        user_id: UUID,
        job_id: UUID,
    ):

        # --------------------------------------------------------
        # Find organization of logged-in user
        # --------------------------------------------------------

        company = await (
            self.organization_repository
            .get_by_admin_user_id(user_id)
        )

        if company is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found for this user.",
            )

        # --------------------------------------------------------
        # Get existing job
        # --------------------------------------------------------

        job = await (
            self.job_repository
            .get_by_id(
                job_id=job_id,
                company_id=company.id,
            )
        )

        if job is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found.",
            )

        # --------------------------------------------------------
        # Duplicate job
        # --------------------------------------------------------

        return await (
            self.job_repository
            .duplicate(
                job=job,
                posted_by=user_id,
            )
        )