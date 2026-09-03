import math
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.organization_repository import (
    OrganizationRepository,
)

from app.repositories.organization_job_repository import (
    OrganizationJobRepository,
)
from app.repositories.job_application_repository import (
    JobApplicationRepository,
)

from app.repositories.interview_repository import (
    InterviewRepository,
)

from app.models.user import User
from app.models.user_profile import UserProfile
from app.models.job_application import JobApplication
from app.models.interview import Interview
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
        self.db = db
        self.organization_repository = (
            OrganizationRepository(db)
        )
      
        self.job_repository = (
            OrganizationJobRepository(db)
        )

        self.ats_repository = (
            OrganizationATSConfigRepository(db)
        )
        self.application_repository = (
             JobApplicationRepository(db)
        )

        self.interview_repository = (
             InterviewRepository(db)
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
        "job_id": job.job_code,
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
    # GET COMPLETE JOB DETAILS
    # ============================================================

    async def get_job_details(
        self,
        user_id: UUID,
        job_id: UUID,
    ):

        # --------------------------------------------------------
        # Find organization
        # --------------------------------------------------------

        company = await self.organization_repository.get_by_admin_user_id(user_id)

        if company is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found for this user.",
            )

        # --------------------------------------------------------
        # Get job
        # --------------------------------------------------------

        job = await self.job_repository.get_by_id(
            job_id=job_id,
            company_id=company.id,
        )

        if job is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found.",
            )

        # --------------------------------------------------------
        # Get applications
        # --------------------------------------------------------

        applications = await self.application_repository.get_by_organization_job(
            job_id=job.id,
            company_id=company.id,
            skip=0,
            limit=1000,
        )

        # --------------------------------------------------------
        # Convert applications
        # --------------------------------------------------------

        application_items = []

        for application in applications:

            recruiter_name = None

            if application.recruiter_id:

                recruiter = await self.db.get(
                    User,
                    application.recruiter_id,
                )

                if recruiter:
                    recruiter_name = recruiter.name

            application_items.append(
                {
                    "application_id": application.id,

                    "candidate_id":
                        application.applicant_user_id,

                    "candidate_name":
                        application.name,

                    "applied_at":
                        application.created_at,

                    "ats_score":
                        application.ats_score,

                    "match_score":
                        application.match_score,

                    "experience":
                        application.experience,

                    "stage":
                        application.status,

                    "recruiter":
                        recruiter_name,
                }
            )

        # --------------------------------------------------------
        # Overview counts
        # --------------------------------------------------------

        total_applications = len(applications)

        matched = sum(
            1
            for application in applications
            if application.match_score is not None
            and application.match_score >= 70
        )

        shortlisted = sum(
            1
            for application in applications
            if application.status == "shortlisted"
        )

        interview_stages = {
            "interview",
            "technical_round",
            "hr_round",
            "finalist",
        }

        interviews = sum(
            1
            for application in applications
            if application.status in interview_stages
        )

        finalists = sum(
            1
            for application in applications
            if application.status == "finalist"
        )

        selected = sum(
            1
            for application in applications
            if application.status == "selected"
        )

        ats_scores = [
            application.ats_score
            for application in applications
            if application.ats_score is not None
        ]

        match_scores = [
            application.match_score
            for application in applications
            if application.match_score is not None
        ]

        avg_ats_score = (
            round(
                sum(ats_scores) / len(ats_scores),
                2,
            )
            if ats_scores
            else 0
        )

        avg_match_score = (
            round(
                sum(match_scores) / len(match_scores),
                2,
            )
            if match_scores
            else 0
        )

        # --------------------------------------------------------
        # Pipeline
        # --------------------------------------------------------

        pipeline = {
            "applied": [],
            "screening": [],
            "shortlisted": [],
            "interview": [],
            "technical_round": [],
            "hr_round": [],
            "finalist": [],
            "selected": [],
            "rejected": [],
        }

        for item in application_items:

            stage = item["stage"]

            if stage == "submitted":
                pipeline["applied"].append(item)

            elif stage in pipeline:
                pipeline[stage].append(item)

        # --------------------------------------------------------
        # Matched profiles
        #
        # Current database does not have a separate
        # matched-profile table.
        #
        # Therefore derive matched profiles from
        # applications having match_score >= 70.
        # --------------------------------------------------------

        matched_profiles = []

        required_skills = [
            skill.lower()
            for skill in (
                job.required_skills or []
            )
        ]

        for application in applications:

            if (
                application.match_score is None
                or application.match_score < 70
            ):
                continue

            designation = None
            candidate_skills = []

            if application.applicant_user_id:

                user = await self.db.get(
                    User,
                    application.applicant_user_id,
                )

                if user:

                    designation = user.designation

                    profile_result = await self.db.execute(
                        select(UserProfile).where(
                            UserProfile.user_id
                            == application.applicant_user_id
                        )
                    )

                    profile = (
                        profile_result
                        .scalar_one_or_none()
                    )

                    if profile:
                        candidate_skills = [
                            skill.lower()
                            for skill in (
                                profile.skills or []
                            )
                        ]

            relevant_skills = [
                skill
                for skill in candidate_skills
                if skill in required_skills
            ]

            missing_skills = [
                skill
                for skill in required_skills
                if skill not in candidate_skills
            ]

            matched_profiles.append(
                {
                    "candidate_id":
                        application.applicant_user_id,

                    "candidate_name":
                        application.name,

                    "designation":
                        designation,

                    "ats_score":
                        application.ats_score,

                    "match_score":
                        application.match_score,

                    "relevant_skills":
                        relevant_skills,

                    "missing_skills":
                        missing_skills,

                    "match_reason":
                        (
                            f"{len(relevant_skills)} relevant "
                            f"required skill(s) matched"
                        ),
                }
            )

        # --------------------------------------------------------
        # Interviews
        # --------------------------------------------------------

        interview_result = await self.db.execute(
            select(
                Interview,
                JobApplication,
                User,
            )
            .join(
                JobApplication,
                Interview.application_id
                == JobApplication.id,
            )
            .outerjoin(
                User,
                Interview.interviewer_id
                == User.id,
            )
            .where(
                Interview.company_id == company.id,
                JobApplication.job_id == job.id,
            )
            .order_by(
                Interview.scheduled_at.desc()
            )
        )

        interview_rows = (
            interview_result.all()
        )

        interviews_data = []

        for interview, application, interviewer in (
            interview_rows
        ):

            interviews_data.append(
                {
                    "interview_id":
                        interview.id,

                    "candidate_id":
                        application.applicant_user_id,

                    "candidate_name":
                        application.name,

                    "type":
                        interview.interview_type,

                    "interviewer":
                        interviewer.name
                        if interviewer
                        else None,

                    "scheduled_at":
                        interview.scheduled_at,

                    "status":
                        interview.status,
                }
            )

        # --------------------------------------------------------
        # Analytics
        # --------------------------------------------------------

        match_rate = (
            round(
                matched
                / total_applications
                * 100,
                2,
            )
            if total_applications
            else 0
        )

        conversion = (
            round(
                selected
                / total_applications
                * 100,
                2,
            )
            if total_applications
            else 0
        )

        # --------------------------------------------------------
        # ATS weights
        # --------------------------------------------------------

        ats_configuration = (
            job.ats_configuration or {}
        )

        ats_weights = {
            "skills":
                ats_configuration.get(
                    "skills",
                    30,
                ),

            "experience":
                ats_configuration.get(
                    "experience",
                    20,
                ),

            "education":
                ats_configuration.get(
                    "education",
                    15,
                ),

            "role_relevance":
                ats_configuration.get(
                    "role_relevance",
                    20,
                ),

            "screening_questions":
                ats_configuration.get(
                    "screening_questions",
                    10,
                ),

            "certifications":
                ats_configuration.get(
                    "certifications",
                    5,
                ),
        }

        # --------------------------------------------------------
        # Final response
        # --------------------------------------------------------

        return {
            "job": {
                "id": job.id,
                "job_id": str(job.id),
                "title": job.title,
                "department": job.department,
                "location": job.location,
                "work_mode": job.work_mode,
                "employment_type": job.job_type,
                "experience_min": job.min_experience,
                "experience_max": job.max_experience,
                "openings": job.openings,
                "status": job.status,
                "created_at": job.created_at,
                "summary": job.summary,
                "responsibilities":
                    job.responsibilities or [],
                "required_skills":
                    job.required_skills or [],
                "preferred_skills":
                    job.preferred_skills or [],
                "ats_weights":
                    ats_weights,
            },

            "overview": {
                "applications":
                    total_applications,
                "matched":
                    matched,
                "shortlisted":
                    shortlisted,
                "interviews":
                    interviews,
                "finalists":
                    finalists,
                "selected":
                    selected,
                "avg_ats_score":
                    avg_ats_score,
            },

            "applications":
                application_items,

            "matched_profiles":
                matched_profiles,

            "pipeline":
                pipeline,

            "interviews":
                interviews_data,

            "analytics": {
                "avg_ats_score":
                    avg_ats_score,

                "avg_match_score":
                    avg_match_score,

                "match_rate":
                    match_rate,

                "conversion":
                    conversion,
            },
        }    # ============================================================
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