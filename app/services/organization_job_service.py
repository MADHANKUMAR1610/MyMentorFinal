import math
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

from app.repositories.organization_ats_config_repository import (
    OrganizationATSConfigRepository,
)


class OrganizationJobService:

    def __init__(self, db: AsyncSession):

        self.organization_repository = (
            OrganizationRepository(db)
        )

        self.job_repository = (
            OrganizationJobRepository(db)
        )

        self.ats_repository = (
            OrganizationATSConfigRepository(db)
        )

    # ============================================================
    # GET MY JOBS - FULL DETAILS
    # ============================================================

    async def get_my_jobs_full(
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
        # Get organization's full jobs
        # --------------------------------------------------------

        return await (
            self.job_repository
            .get_all_jobs_by_company_id(company.id)
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

        ats_config = await self.ats_repository.get_by_company_id(
            company.id
        )

        if not ats_config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="ATS configuration not found for this organization",
            )

        job_data["ats_configuration"] = {
            "skills": ats_config.skills,
            "experience": ats_config.experience,
            "education": ats_config.education,
            "role_relevance": ats_config.role_relevance,
            "screening_questions": ats_config.screening_questions,
            "certifications": ats_config.certifications,
        }

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

        ats_config = await self.ats_repository.get_by_company_id(
            company.id
        )

        if not ats_config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="ATS configuration not found for this organization",
            )

        job_data["ats_configuration"] = {
            "skills": ats_config.skills,
            "experience": ats_config.experience,
            "education": ats_config.education,
            "role_relevance": ats_config.role_relevance,
            "screening_questions": ats_config.screening_questions,
            "certifications": ats_config.certifications,
        }

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

    # ============================================================
    # GET MY JOBS - PAGINATED JOB LIST
    # ============================================================

    async def get_my_jobs_list(
        self,
        user_id: UUID,
        page: int = 1,
        page_size: int = 20,
        search: str | None = None,
        status: str | None = None,
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
        # Get paginated jobs
        # --------------------------------------------------------

        jobs, total = await (
            self.job_repository
            .get_jobs_by_company_id(
                company_id=company.id,
                page=page,
                page_size=page_size,
                search=search,
                status=status,
            )
        )

        # --------------------------------------------------------
        # Prepare Job List response
        # --------------------------------------------------------

        items = []

        for job in jobs:

            items.append(
                {
                    "id": job.id,
                    "job_id": str(job.id),
                    "title": job.title,
                    "department": job.department,
                    "location": job.location,
                    "employment_type": job.job_type,
                    "experience_min": job.min_experience,
                    "experience_max": job.max_experience,
                    "applications_count": job.applicants or 0,
                    "matched_count": 0,
                    "shortlisted_count": 0,
                    "interviews_count": 0,
                    "selected_count": 0,
                    "status": job.status,
                }
            )

        # --------------------------------------------------------
        # Return paginated response
        # --------------------------------------------------------

        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (
                math.ceil(total / page_size)
                if total
                else 0
            ),
        }

    # ============================================================
    # GET JOB SUMMARY
    # ============================================================

    async def get_job_summary(
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
        # Get job summary
        # --------------------------------------------------------

        return await (
            self.job_repository
            .get_job_summary(company.id)
        )