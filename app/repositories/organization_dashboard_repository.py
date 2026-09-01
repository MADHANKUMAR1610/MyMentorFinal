from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.job import Job
from app.models.job_application import JobApplication


class OrganizationDashboardRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    # ============================================================
    # USER COUNTS
    # ============================================================

    async def get_user_counts(
        self,
        company_id: UUID,
    ) -> dict[str, int]:

        result = await self.db.execute(
            select(
                func.count(User.id),
                func.count(User.id).filter(
                    User.is_active.is_(True)
                ),
            )
            .where(
                User.company_id == company_id
            )
        )

        total_users, active_users = result.one()

        return {
            "total_users": total_users or 0,
            "active_users": active_users or 0,
        }

    # ============================================================
    # JOB COUNTS
    # ============================================================

    async def get_job_counts(
        self,
        company_id: UUID,
    ) -> dict[str, int]:

        result = await self.db.execute(
            select(
                func.count(Job.id),
                func.count(Job.id).filter(
                    Job.status == "active"
                ),
            )
            .where(
                Job.company_id == company_id
            )
        )

        total_jobs, active_jobs = result.one()

        return {
            "total_jobs": total_jobs or 0,
            "active_jobs": active_jobs or 0,
        }

    # ============================================================
    # APPLICATION COUNTS
    # ============================================================

    async def get_application_counts(
        self,
        company_id: UUID,
    ) -> dict[str, int]:

        result = await self.db.execute(
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
            "total_applications": 0,
            "matched_profiles": 0,
            "shortlisted": 0,
            "interviews": 0,
            "selected": 0,
        }

        for application_status, count in result.all():

            counts["total_applications"] += count

            if application_status == "shortlisted":
                counts["shortlisted"] = count

            elif application_status == "interview":
                counts["interviews"] = count

            elif application_status == "selected":
                counts["selected"] = count

        return counts

    # ============================================================
    # ACTIVE JOBS
    # ============================================================

    async def get_active_jobs(
        self,
        company_id: UUID,
    ) -> list[Job]:

        result = await self.db.execute(
            select(Job)
            .where(
                Job.company_id == company_id,
                Job.status == "active",
            )
            .order_by(
                Job.created_at.desc()
            )
        )

        return list(
            result.scalars().all()
        )

    # ============================================================
    # APPLICATION COUNTS FOR EACH JOB
    # ============================================================

    async def get_job_application_counts(
        self,
        job_id: UUID,
    ) -> dict[str, int]:

        result = await self.db.execute(
            select(
                JobApplication.status,
                func.count(JobApplication.id),
            )
            .where(
                JobApplication.job_id == job_id
            )
            .group_by(
                JobApplication.status
            )
        )

        counts = {
            "applications": 0,
            "matched": 0,
            "shortlisted": 0,
            "interviews": 0,
            "selected": 0,
        }

        for application_status, count in result.all():

            counts["applications"] += count

            if application_status == "shortlisted":
                counts["shortlisted"] = count

            elif application_status == "interview":
                counts["interviews"] = count

            elif application_status == "selected":
                counts["selected"] = count

        return counts