from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.company import Company
from app.models.job import Job
from app.models.job_application import JobApplication


class OrganizationDashboardRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_dashboard_data(
        self,
        company_id: UUID,
    ) -> dict:

        # --------------------------------------------
        # Total Jobs
        # --------------------------------------------

        total_jobs_result = await self.db.execute(
            select(func.count(Job.id))
            .where(Job.company_id == company_id)
        )

        total_jobs = total_jobs_result.scalar() or 0

        # --------------------------------------------
        # Active Jobs
        # --------------------------------------------

        active_jobs_result = await self.db.execute(
            select(func.count(Job.id))
            .where(
                Job.company_id == company_id,
                Job.status == "open",
            )
        )

        active_jobs = active_jobs_result.scalar() or 0

        # --------------------------------------------
        # Total Applications
        # --------------------------------------------

        total_applications_result = await self.db.execute(
            select(func.count(JobApplication.id))
            .join(
                Job,
                Job.id == JobApplication.job_id,
            )
            .where(
                Job.company_id == company_id
            )
        )

        total_applications = (
            total_applications_result.scalar() or 0
        )

        # --------------------------------------------
        # Shortlisted Candidates
        # --------------------------------------------

        shortlisted_result = await self.db.execute(
            select(func.count(JobApplication.id))
            .join(
                Job,
                Job.id == JobApplication.job_id,
            )
            .where(
                Job.company_id == company_id,
                JobApplication.status == "shortlisted",
            )
        )

        shortlisted_candidates = (
            shortlisted_result.scalar() or 0
        )

        return {
            "total_jobs": total_jobs,
            "active_jobs": active_jobs,
            "total_applications": total_applications,
            "shortlisted_candidates": shortlisted_candidates,
        }