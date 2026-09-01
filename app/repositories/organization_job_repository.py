from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.job import Job


class OrganizationJobRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    # ============================================================
    # GET ALL JOBS
    # ============================================================

    async def get_jobs_by_company_id(
        self,
        company_id: UUID,
    ) -> list[Job]:

        result = await self.db.execute(
            select(Job)
            .where(
                Job.company_id == company_id
            )
            .order_by(
                Job.created_at.desc()
            )
        )

        return list(result.scalars().all())

    # ============================================================
    # GET JOB BY ID
    # ============================================================

    async def get_by_id(
        self,
        job_id: UUID,
        company_id: UUID,
    ) -> Job | None:

        result = await self.db.execute(
            select(Job).where(
                Job.id == job_id,
                Job.company_id == company_id,
            )
        )

        return result.scalar_one_or_none()

    # ============================================================
    # CREATE JOB
    # ============================================================

    async def create(
        self,
        company_id: UUID,
        posted_by: UUID,
        data: dict,
    ) -> Job:

        job = Job(
            company_id=company_id,
            posted_by=posted_by,

            # Basic Information
            company_name=data["company_name"],
            title=data["title"],
            department=data.get("department"),
            location=data.get("location"),
            job_type=data.get(
                "job_type",
                "Full-time",
            ),
            work_mode=data.get(
                "work_mode",
                "On-site",
            ),

            min_experience=data.get(
                "min_experience"
            ),
            max_experience=data.get(
                "max_experience"
            ),

            openings=data.get(
                "openings",
                1,
            ),

            salary_min=data.get(
                "salary_min"
            ),
            salary_max=data.get(
                "salary_max"
            ),

            recruiter_id=data.get(
                "recruiter_id"
            ),
            hiring_manager_id=data.get(
                "hiring_manager_id"
            ),

            # Job Description
            summary=data.get(
                "summary"
            ),

            description=data.get(
                "description"
            ),

            responsibilities=data.get(
                "responsibilities",
                [],
            ),

            required_skills=data.get(
                "required_skills",
                [],
            ),

            preferred_skills=data.get(
                "preferred_skills",
                [],
            ),

            education=data.get(
                "education"
            ),

            # Requirements
            mandatory_requirements=data.get(
                "mandatory_requirements",
                [],
            ),

            preferred_requirements=data.get(
                "preferred_requirements",
                [],
            ),

            # Screening Questions
            screening_questions=data.get(
                "screening_questions",
                [],
            ),

            # ATS
            ats_configuration=data.get(
                "ats_configuration",
                {
                    "skills": 30,
                    "experience": 20,
                    "education": 15,
                    "role_relevance": 20,
                    "screening_questions": 10,
                    "certifications": 5,
                },
            ),

            # Existing fields
            skills=data.get(
                "skills",
                [],
            ),

            apply_email=data.get(
                "apply_email"
            ),

            applicants=0,

            status=data.get(
                "status",
                "draft",
            ),
        )

        self.db.add(job)

        await self.db.commit()
        await self.db.refresh(job)

        return job

    # ============================================================
    # UPDATE JOB
    # ============================================================

    async def update(
        self,
        job: Job,
        data: dict,
    ) -> Job:

        for field, value in data.items():

            if value is not None:
                setattr(
                    job,
                    field,
                    value,
                )

        await self.db.commit()
        await self.db.refresh(job)

        return job

    # ============================================================
    # DELETE JOB
    # ============================================================

    async def delete(
        self,
        job: Job,
    ) -> None:

        await self.db.delete(job)

        await self.db.commit()

    # ============================================================
    # UPDATE STATUS
    # ============================================================

    async def update_status(
        self,
        job: Job,
        status: str,
    ) -> Job:

        job.status = status

        await self.db.commit()
        await self.db.refresh(job)

        return job

    # ============================================================
    # DUPLICATE JOB
    # ============================================================

    async def duplicate(
        self,
        job: Job,
        posted_by: UUID,
    ) -> Job:

        duplicated_job = Job(
            company_id=job.company_id,
            posted_by=posted_by,

            company_name=job.company_name,

            title=f"{job.title} - Copy",

            department=job.department,
            location=job.location,
            job_type=job.job_type,
            work_mode=job.work_mode,

            min_experience=job.min_experience,
            max_experience=job.max_experience,

            openings=job.openings,

            salary_min=job.salary_min,
            salary_max=job.salary_max,

            recruiter_id=job.recruiter_id,
            hiring_manager_id=job.hiring_manager_id,

            summary=job.summary,
            description=job.description,

            responsibilities=job.responsibilities,
            required_skills=job.required_skills,
            preferred_skills=job.preferred_skills,

            education=job.education,

            mandatory_requirements=job.mandatory_requirements,
            preferred_requirements=job.preferred_requirements,

            screening_questions=job.screening_questions,
            ats_configuration=job.ats_configuration,

            skills=job.skills,

            apply_email=job.apply_email,

            applicants=0,

            status="draft",
        )

        self.db.add(duplicated_job)

        await self.db.commit()
        await self.db.refresh(duplicated_job)

        return duplicated_job
        # ============================================================
    # GET JOB SUMMARY
    # ============================================================

    async def get_job_summary(
        self,
        company_id: UUID,
    ) -> dict:

        result = await self.db.execute(
            select(
                func.count(Job.id).label("total_jobs"),

                func.count(Job.id)
                .filter(
                    Job.status == "draft"
                )
                .label("draft"),

                func.count(Job.id)
                .filter(
                    Job.status == "open"
                )
                .label("active"),

                func.count(Job.id)
                .filter(
                    Job.status == "paused"
                )
                .label("paused"),

                func.count(Job.id)
                .filter(
                    Job.status == "closed"
                )
                .label("closed"),

                func.count(Job.id)
                .filter(
                    Job.status == "filled"
                )
                .label("filled"),
            )
            .where(
                Job.company_id == company_id
            )
        )

        row = result.one()

        return {
            "total_jobs": row.total_jobs or 0,
            "draft": row.draft or 0,
            "active": row.active or 0,
            "paused": row.paused or 0,
            "closed": row.closed or 0,
            "filled": row.filled or 0,
        }