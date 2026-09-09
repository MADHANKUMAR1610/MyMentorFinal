from typing import Optional
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.job import Job
from app.models.job_application import JobApplication
from app.repositories.base import BaseRepository


class JobApplicationRepository(BaseRepository[JobApplication]):
    """
    Repository responsible for JobApplication database operations.

    Business rules belong in the service layer.
    """

    def __init__(self, session: AsyncSession):
        super().__init__(JobApplication, session)

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
        result = await self.session.execute(
            select(JobApplication)
            .options(selectinload(JobApplication.resume_file))
            .where(JobApplication.job_id == job_id)
            .order_by(JobApplication.created_at.desc())
            .offset(skip)
            .limit(limit)
        )

        return list(result.scalars().all())

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
        result = await self.session.execute(
            select(JobApplication)
            .options(selectinload(JobApplication.resume_file))
            .where(JobApplication.applicant_user_id == user_id)
            .order_by(JobApplication.created_at.desc())
            .offset(skip)
            .limit(limit)
        )

        return list(result.scalars().all())

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
        result = await self.session.execute(
            select(JobApplication)
            .options(selectinload(JobApplication.resume_file))
            .where(JobApplication.email == email.strip().lower())
            .order_by(JobApplication.created_at.desc())
            .offset(skip)
            .limit(limit)
        )

        return list(result.scalars().all())

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
        result = await self.session.execute(
            select(JobApplication)
            .options(selectinload(JobApplication.resume_file))
            .where(JobApplication.status == status)
            .order_by(JobApplication.created_at.desc())
            .offset(skip)
            .limit(limit)
        )

        return list(result.scalars().all())

    # ============================================================
    # GET APPLICATION BY JOB AND USER
    # ============================================================

    async def get_by_job_and_user(
        self,
        job_id: UUID,
        user_id: UUID,
    ) -> Optional[JobApplication]:
        result = await self.session.execute(
            select(JobApplication)
            .options(selectinload(JobApplication.resume_file))
            .where(
                JobApplication.job_id == job_id,
                JobApplication.applicant_user_id == user_id,
            )
        )

        return result.scalar_one_or_none()

    # ============================================================
    # GET APPLICATION BY JOB AND EMAIL
    # ============================================================

    async def get_by_job_and_email(
        self,
        job_id: UUID,
        email: str,
    ) -> Optional[JobApplication]:
        result = await self.session.execute(
            select(JobApplication)
            .options(selectinload(JobApplication.resume_file))
            .where(
                JobApplication.job_id == job_id,
                JobApplication.email == email.strip().lower(),
            )
        )

        return result.scalar_one_or_none()

    # ============================================================
    # GET ALL APPLICATIONS BY COMPANY
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
        query = (
            select(JobApplication)
            .options(selectinload(JobApplication.resume_file))
            .join(Job, JobApplication.job_id == Job.id)
            .where(Job.company_id == company_id)
        )

        if status is not None:
            query = query.where(JobApplication.status == status)

        if name is not None:
            query = query.where(
                JobApplication.name.ilike(f"%{name.strip()}%")
            )

        if email is not None:
            query = query.where(
                JobApplication.email.ilike(f"%{email.strip()}%")
            )

        if job_id is not None:
            query = query.where(JobApplication.job_id == job_id)

        query = (
            query
            .order_by(JobApplication.created_at.desc())
            .offset(skip)
            .limit(limit)
        )

        result = await self.session.execute(query)

        return list(result.scalars().all())

    # ============================================================
    # GET APPLICATIONS FOR ORGANIZATION JOB
    # ============================================================

    async def get_by_organization_job(
        self,
        job_id: UUID,
        company_id: UUID,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[JobApplication]:
        result = await self.session.execute(
            select(JobApplication)
            .options(selectinload(JobApplication.resume_file))
            .join(Job, JobApplication.job_id == Job.id)
            .where(
                JobApplication.job_id == job_id,
                Job.company_id == company_id,
            )
            .order_by(JobApplication.created_at.desc())
            .offset(skip)
            .limit(limit)
        )

        return list(result.scalars().all())

    # ============================================================
    # GET SINGLE ORGANIZATION APPLICATION
    # ============================================================

    async def get_organization_application(
        self,
        application_id: UUID,
        company_id: UUID,
    ) -> Optional[JobApplication]:
        result = await self.session.execute(
            select(JobApplication)
            .options(selectinload(JobApplication.resume_file))
            .join(Job, JobApplication.job_id == Job.id)
            .where(
                JobApplication.id == application_id,
                Job.company_id == company_id,
            )
        )

        return result.scalar_one_or_none()

    # ============================================================
    # GET COMPANY APPLICATION STATS
    # ============================================================

    async def get_company_application_stats(
        self,
        company_id: UUID,
    ) -> dict[str, int]:
        result = await self.session.execute(
            select(
                JobApplication.status,
                func.count(JobApplication.id),
            )
            .join(Job, JobApplication.job_id == Job.id)
            .where(Job.company_id == company_id)
            .group_by(JobApplication.status)
        )

        stats = {
            "total": 0,
            "submitted": 0,
            "screening": 0,
            "shortlisted": 0,
            "interview": 0,
            "technical_round": 0,
            "hr_round": 0,
            "finalist": 0,
            "selected": 0,
            "rejected": 0,
        }

        for application_status, count in result.all():
            if application_status in stats:
                stats[application_status] = count

            stats["total"] += count

        return stats

    # ============================================================
    # GET STATUS COUNTS BY COMPANY
    # ============================================================

    async def get_status_counts_by_company_id(
        self,
        company_id: UUID,
    ) -> dict[str, int]:
        result = await self.session.execute(
            select(
                JobApplication.status,
                func.count(JobApplication.id),
            )
            .join(Job, JobApplication.job_id == Job.id)
            .where(Job.company_id == company_id)
            .group_by(JobApplication.status)
        )

        counts = {
            "submitted": 0,
            "screening": 0,
            "shortlisted": 0,
            "interview": 0,
            "technical_round": 0,
            "hr_round": 0,
            "finalist": 0,
            "selected": 0,
            "rejected": 0,
        }

        for application_status, count in result.all():
            if application_status in counts:
                counts[application_status] = count

        counts["total"] = sum(counts.values())

        return counts