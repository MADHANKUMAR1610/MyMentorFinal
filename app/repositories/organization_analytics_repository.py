from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.job import Job
from app.models.job_application import JobApplication
from app.models.interview import Interview
from datetime import datetime


class OrganizationAnalyticsRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    # ============================================================
    # TOTAL USERS
    # ============================================================

    async def get_total_users(
        self,
        company_id: UUID,
    ) -> int:

        result = await self.db.execute(
            select(func.count(User.id))
            .where(
                User.company_id == company_id
            )
        )

        return result.scalar() or 0

    # ============================================================
    # ACTIVE USERS
    # ============================================================

    async def get_active_users(
        self,
        company_id: UUID,
    ) -> int:

        result = await self.db.execute(
            select(func.count(User.id))
            .where(
                User.company_id == company_id,
                User.is_active.is_(True),
            )
        )

        return result.scalar() or 0

    # ============================================================
    # TOTAL JOBS
    # ============================================================

    async def get_total_jobs(
        self,
        company_id: UUID,
    ) -> int:

        result = await self.db.execute(
            select(func.count(Job.id))
            .where(
                Job.company_id == company_id
            )
        )

        return result.scalar() or 0

    # ============================================================
    # ACTIVE JOBS
    # ============================================================

    async def get_active_jobs(
        self,
        company_id: UUID,
    ) -> int:

        result = await self.db.execute(
            select(func.count(Job.id))
            .where(
                Job.company_id == company_id,
                Job.status == "active",
            )
        )

        return result.scalar() or 0

    # ============================================================
    # TOTAL APPLICATIONS
    # ============================================================

    async def get_total_applications(
        self,
        company_id: UUID,
    ) -> int:

        result = await self.db.execute(
            select(func.count(JobApplication.id))
            .join(
                Job,
                Job.id == JobApplication.job_id,
            )
            .where(
                Job.company_id == company_id
            )
        )

        return result.scalar() or 0

    # ============================================================
    # APPLICATIONS BY STATUS
    # ============================================================

    async def get_applications_by_status(
        self,
        company_id: UUID,
    ) -> list[tuple[str, int]]:

        result = await self.db.execute(
            select(
                JobApplication.status,
                func.count(JobApplication.id),
            )
            .join(
                Job,
                Job.id == JobApplication.job_id,
            )
            .where(
                Job.company_id == company_id
            )
            .group_by(
                JobApplication.status
            )
        )

        return list(result.all())

    # ============================================================
    # TOTAL INTERVIEWS
    # ============================================================

    async def get_total_interviews(
        self,
        company_id: UUID,
    ) -> int:

        result = await self.db.execute(
            select(func.count(Interview.id))
            .where(
                Interview.company_id == company_id
            )
        )

        return result.scalar() or 0

    # ============================================================
    # INTERVIEWS BY STATUS
    # ============================================================

    async def get_interviews_by_status(
        self,
        company_id: UUID,
    ) -> list[tuple[str, int]]:

        result = await self.db.execute(
            select(
                Interview.status,
                func.count(Interview.id),
            )
            .where(
                Interview.company_id == company_id
            )
            .group_by(
                Interview.status
            )
        )

        return list(result.all())
# ============================================================
# APPLICATION TREND
# ============================================================

    async def get_application_trend(
        self,
        company_id: UUID,
    ):
        result = await self.db.execute(
            select(
                func.date(JobApplication.created_at).label("date"),
                func.count(JobApplication.id).label("count"),
            )
            .join(
                Job,
                Job.id == JobApplication.job_id,
            )
            .where(
                Job.company_id == company_id
            )
            .group_by(
                func.date(JobApplication.created_at)
            )
            .order_by(
                func.date(JobApplication.created_at)
            )
        )

        return [
            {
                "date": row.date,
                "count": row.count,
            }
            for row in result.all()
        ]
    # ============================================================
    # RECRUITMENT FUNNEL
    # ============================================================

    async def get_recruitment_funnel(
        self,
        company_id: UUID,
    ):
        result = await self.db.execute(
            select(
                JobApplication.status,
                func.count(JobApplication.id).label("count"),
            )
            .join(
                Job,
                Job.id == JobApplication.job_id,
            )
            .where(
                Job.company_id == company_id
            )
            .group_by(
                JobApplication.status
            )
            .order_by(
                JobApplication.status
            )
        )

        return [
            {
                "status": row.status,
                "count": row.count,
            }
            for row in result.all()
        ]

    # ============================================================
    # INTERVIEW ANALYTICS
    # ============================================================

    async def get_interview_analytics(
        self,
        company_id: UUID,
    ):
        result = await self.db.execute(
            select(
                Interview.status,
                func.count(Interview.id).label("count"),
            )
            .where(
                Interview.company_id == company_id
            )
            .group_by(
                Interview.status
            )
            .order_by(
                Interview.status
            )
        )

        return [
            {
                "status": row.status,
                "count": row.count,
            }
            for row in result.all()
        ]

    # ============================================================
    # JOB-WISE RECRUITMENT ANALYTICS
    # ============================================================

    async def get_job_wise_recruitment_analytics(
        self,
        company_id: UUID,
    ):
        result = await self.db.execute(
            select(
                Job.id.label("job_id"),
                Job.title.label("job_title"),
                func.count(JobApplication.id).label(
                    "total_applications"
                ),
            )
            .outerjoin(
                JobApplication,
                JobApplication.job_id == Job.id,
            )
            .where(
                Job.company_id == company_id
            )
            .group_by(
                Job.id,
                Job.title,
            )
            .order_by(
                func.count(JobApplication.id).desc()
            )
        )

        return [
            {
                "job_id": row.job_id,
                "job_title": row.job_title,
                "total_applications": row.total_applications,
            }
            for row in result.all()
        ]
    # ============================================================
    # HIRING RATE ANALYTICS
    # ============================================================

    async def get_hiring_rate(
        self,
        company_id: UUID,
    ):
        # --------------------------------------------------------
        # Total applications
        # --------------------------------------------------------

        total_result = await self.db.execute(
            select(
                func.count(JobApplication.id)
            )
            .join(
                Job,
                Job.id == JobApplication.job_id,
            )
            .where(
                Job.company_id == company_id
            )
        )

        total_applications = total_result.scalar() or 0

        # --------------------------------------------------------
        # Total hired applications
        # --------------------------------------------------------

        hired_result = await self.db.execute(
            select(
                func.count(JobApplication.id)
            )
            .join(
                Job,
                Job.id == JobApplication.job_id,
            )
            .where(
                Job.company_id == company_id,
                JobApplication.status == "hired",
            )
        )

        hired_applications = hired_result.scalar() or 0

        # --------------------------------------------------------
        # Calculate hiring rate
        # --------------------------------------------------------

        hiring_rate = (
            (hired_applications / total_applications) * 100
            if total_applications > 0
            else 0
        )

        return {
            "total_applications": total_applications,
            "hired_applications": hired_applications,
            "hiring_rate": round(hiring_rate, 2),
        }
    # ============================================================
    # AVERAGE TIME TO HIRE
    # ============================================================

    async def get_average_time_to_hire(
        self,
        company_id: UUID,
    ):
        result = await self.db.execute(
            select(
                func.avg(
                    func.extract(
                        "epoch",
                        JobApplication.updated_at
                        - JobApplication.created_at,
                    )
                )
            )
            .join(
                Job,
                Job.id == JobApplication.job_id,
            )
            .where(
                Job.company_id == company_id,
                JobApplication.status == "hired",
            )
        )

        average_seconds = result.scalar()

        if average_seconds is None:
            return {
                "average_time_to_hire_days": 0
            }

        average_days = (
            float(average_seconds) / 86400
        )

        return {
            "average_time_to_hire_days": round(
                average_days,
                2,
            )
        }