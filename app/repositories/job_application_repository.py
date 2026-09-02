from typing import Optional
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.job import Job
from app.models.job_application import JobApplication
from app.repositories.base import BaseRepository


class JobApplicationRepository(
    BaseRepository[JobApplication]
):
    """
    Repository responsible for JobApplication
    database operations.

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
        """
        Get applications submitted for a specific job.
        """

        result = await self.session.execute(
            select(JobApplication)
            .where(
                JobApplication.job_id == job_id
            )
            .order_by(
                JobApplication.created_at.desc()
            )
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
        """
        Get applications submitted by a specific user.
        """

        result = await self.session.execute(
            select(JobApplication)
            .where(
                JobApplication.applicant_user_id == user_id
            )
            .order_by(
                JobApplication.created_at.desc()
            )
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
        """
        Get applications using applicant email.
        """

        result = await self.session.execute(
            select(JobApplication)
            .where(
                JobApplication.email == email
            )
            .order_by(
                JobApplication.created_at.desc()
            )
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
        """
        Get applications by status.
        """

        result = await self.session.execute(
            select(JobApplication)
            .where(
                JobApplication.status == status
            )
            .order_by(
                JobApplication.created_at.desc()
            )
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
        """
        Get a user's application for a specific job.
        """

        result = await self.session.execute(
            select(JobApplication)
            .where(
                JobApplication.job_id == job_id,
                JobApplication.applicant_user_id == user_id,
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
            .join(
                Job,
                JobApplication.job_id == Job.id,
            )
            .where(
                Job.company_id == company_id
            )
        )

    # --------------------------------------------------------
    # Filter by application status
    # --------------------------------------------------------

        if status is not None:
            query = query.where(
                JobApplication.status == status
            )

    # --------------------------------------------------------
    # Filter by applicant name
    # --------------------------------------------------------

        if name is not None:
            query = query.where(
                JobApplication.name.ilike(
                    f"%{name}%"
                )
            )

    # --------------------------------------------------------
    # Filter by applicant email
    # --------------------------------------------------------

        if email is not None:
            query = query.where(
                JobApplication.email.ilike(
                    f"%{email}%"
                )
            )

    # --------------------------------------------------------
    # Filter by job
    # --------------------------------------------------------

        if job_id is not None:
            query = query.where(
                JobApplication.job_id == job_id
            )

    # --------------------------------------------------------
    # Pagination + ordering
    # --------------------------------------------------------

        query = (
            query
            .order_by(
                JobApplication.created_at.desc()
            )
            .offset(skip)
            .limit(limit)
        )

        result = await self.session.execute(query)

        return list(
            result.scalars().all()
        )

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
        """
        Get applications for a specific job
        only when the job belongs to the organization.
        """

        result = await self.session.execute(
            select(JobApplication)
            .join(
                Job,
                JobApplication.job_id == Job.id,
            )
            .where(
                JobApplication.job_id == job_id,
                Job.company_id == company_id,
            )
            .order_by(
                JobApplication.created_at.desc()
            )
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
        """
        Get a specific application only when
        its job belongs to the organization.
        """

        result = await self.session.execute(
            select(JobApplication)
            .join(
                Job,
                JobApplication.job_id == Job.id,
            )
            .where(
                JobApplication.id == application_id,
                Job.company_id == company_id,
            )
        )

        return result.scalar_one_or_none()

    async def get_company_application_stats(
        self,
        company_id: UUID,
    ) -> dict[str, int]:
        result = await self.session.execute(
            select(
                JobApplication.status,
            )
            .join(
                Job,
                JobApplication.job_id == Job.id,
            )
            .where(
                Job.company_id == company_id
            )
        )

        applications = result.all()

        stats = {
            "total": 0,
            "submitted": 0,
            "reviewing": 0,
            "shortlisted": 0,
            "interview": 0,
            "selected": 0,
            "rejected": 0,
        }

        for row in applications:
            application_status = row.status

            stats["total"] += 1

            if application_status in stats:
                stats[application_status] += 1

        return stats

    async def update_organization_application_status(
        self,
        application_id: UUID,
        company_id: UUID,
        new_status: str,
    ) -> JobApplication | None:
        application = (
            await self.get_organization_application(
                application_id=application_id,
                company_id=company_id,
            )
        )

        if application is None:
            return None

        application.status = new_status

        await self.session.commit()

        await self.session.refresh(application)

        return application

    async def get_status_counts_by_company_id(
        self,
        company_id: UUID,
    ) -> dict[str, int]:
        result = await self.session.execute(
            select(
                JobApplication.status,
                func.count(JobApplication.id),
            )
            .join(
                Job,
                JobApplication.job_id == Job.id,
            )
            .where(
                Job.company_id == company_id
            )
            .group_by(
                JobApplication.status
            )
        )

        counts = {
            "submitted": 0,
            "reviewing": 0,
            "shortlisted": 0,
            "interview": 0,
            "selected": 0,
            "rejected": 0,
        }

        for application_status, count in result.all():
            if application_status in counts:
                counts[application_status] = count

        counts["total"] = sum(counts.values())

        return counts