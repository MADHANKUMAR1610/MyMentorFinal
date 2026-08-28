from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.organization_repository import (
    OrganizationRepository,
)

from app.repositories.organization_analytics_repository import (
    OrganizationAnalyticsRepository,
)


class OrganizationAnalyticsService:

    def __init__(self, db: AsyncSession):

        self.organization_repository = (
            OrganizationRepository(db)
        )

        self.analytics_repository = (
            OrganizationAnalyticsRepository(db)
        )

    # ============================================================
    # GET RECRUITMENT ANALYTICS
    # ============================================================

    async def get_recruitment_analytics(
        self,
        user_id: UUID,
    ):

        # --------------------------------------------------------
        # Find organization of logged-in admin
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

        company_id = company.id

        # --------------------------------------------------------
        # USERS
        # --------------------------------------------------------

        total_users = await (
            self.analytics_repository
            .get_total_users(company_id)
        )

        active_users = await (
            self.analytics_repository
            .get_active_users(company_id)
        )

        # --------------------------------------------------------
        # JOBS
        # --------------------------------------------------------

        total_jobs = await (
            self.analytics_repository
            .get_total_jobs(company_id)
        )

        active_jobs = await (
            self.analytics_repository
            .get_active_jobs(company_id)
        )

        # --------------------------------------------------------
        # APPLICATIONS
        # --------------------------------------------------------

        total_applications = await (
            self.analytics_repository
            .get_total_applications(company_id)
        )

        application_statuses = await (
            self.analytics_repository
            .get_applications_by_status(
                company_id
            )
        )

        applications_by_status = {
            status_name: count
            for status_name, count
            in application_statuses
        }

        # --------------------------------------------------------
        # INTERVIEWS
        # --------------------------------------------------------

        total_interviews = await (
            self.analytics_repository
            .get_total_interviews(company_id)
        )

        interview_statuses = await (
            self.analytics_repository
            .get_interviews_by_status(
                company_id
            )
        )

        interviews_by_status = {
            status_name: count
            for status_name, count
            in interview_statuses
        }

        # --------------------------------------------------------
        # RETURN ANALYTICS
        # --------------------------------------------------------

        return {
            "company_id": company_id,

            "users": {
                "total": total_users,
                "active": active_users,
            },

            "jobs": {
                "total": total_jobs,
                "active": active_jobs,
            },

            "applications": {
                "total": total_applications,
                "by_status": applications_by_status,
            },

            "interviews": {
                "total": total_interviews,
                "by_status": interviews_by_status,
            },
        }
    # ============================================================
    # APPLICATION TREND
    # ============================================================

    async def get_application_trend(
        self,
        user_id: UUID,
    ):
        # --------------------------------------------------------
        # Find organization of logged-in admin
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
        # Get application trend
        # --------------------------------------------------------

        return await (
            self.analytics_repository
            .get_application_trend(
                company.id
            )
        )
    # ============================================================
    # RECRUITMENT FUNNEL
    # ============================================================

    async def get_recruitment_funnel(
        self,
        user_id: UUID,
    ):
        # --------------------------------------------------------
        # Find organization of logged-in admin
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
        # Get recruitment funnel
        # --------------------------------------------------------

        return await (
            self.analytics_repository
            .get_recruitment_funnel(
                company.id
            )
        )
    # ============================================================
    # INTERVIEW ANALYTICS
    # ============================================================

    async def get_interview_analytics(
        self,
        user_id: UUID,
    ):
        # --------------------------------------------------------
        # Find organization of logged-in admin
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
        # Get interview analytics
        # --------------------------------------------------------

        return await (
            self.analytics_repository
            .get_interview_analytics(
                company.id
            )
        )
    # ============================================================
    # JOB-WISE RECRUITMENT ANALYTICS
    # ============================================================

    async def get_job_wise_recruitment_analytics(
        self,
        user_id: UUID,
    ):
        # --------------------------------------------------------
        # Find organization of logged-in admin
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
        # Get job-wise recruitment analytics
        # --------------------------------------------------------

        return await (
            self.analytics_repository
            .get_job_wise_recruitment_analytics(
                company.id
            )
        )
    # ============================================================
    # HIRING RATE ANALYTICS
    # ============================================================

    async def get_hiring_rate(
        self,
        user_id: UUID,
    ):
        # --------------------------------------------------------
        # Find organization of logged-in admin
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
        # Get hiring rate
        # --------------------------------------------------------

        return await (
            self.analytics_repository
            .get_hiring_rate(
                company.id
            )
        )
    # ============================================================
    # AVERAGE TIME TO HIRE
    # ============================================================

    async def get_average_time_to_hire(
        self,
        user_id: UUID,
    ):
        # --------------------------------------------------------
        # Find organization of logged-in admin
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
        # Get average time to hire
        # --------------------------------------------------------

        return await (
            self.analytics_repository
            .get_average_time_to_hire(
                company.id
            )
        )
    # ============================================================
# RECRUITMENT DASHBOARD SUMMARY
# ============================================================

    async def get_recruitment_dashboard(
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

        if company is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found for this user.",
            )

        # --------------------------------------------------------
        # Get summary metrics
        # --------------------------------------------------------

        total_jobs = await (
            self.analytics_repository
            .get_total_jobs(company.id)
        )

        active_jobs = await (
            self.analytics_repository
            .get_active_jobs(company.id)
        )

        total_applications = await (
            self.analytics_repository
            .get_total_applications(company.id)
        )

        applications_by_status = await (
            self.analytics_repository
            .get_applications_by_status(company.id)
        )

        total_interviews = await (
            self.analytics_repository
            .get_total_interviews(company.id)
        )

        interviews_by_status = await (
            self.analytics_repository
            .get_interviews_by_status(company.id)
        )

        hiring_rate = await (
            self.analytics_repository
            .get_hiring_rate(company.id)
        )

        average_time_to_hire = await (
            self.analytics_repository
            .get_average_time_to_hire(company.id)
        )

        # --------------------------------------------------------
        # Return dashboard summary
        # --------------------------------------------------------

        return {
            "total_jobs": total_jobs,
            "active_jobs": active_jobs,
            "total_applications": total_applications,
            "applications_by_status": [
                {
                    "status": status,
                    "count": count,
                }
                for status, count in applications_by_status
            ],
            "total_interviews": total_interviews,
            "interviews_by_status": [
                {
                    "status": status,
                    "count": count,
                }
                for status, count in interviews_by_status
            ],
            "hired_applications": hiring_rate[
                "hired_applications"
            ],
            "hiring_rate": hiring_rate[
                "hiring_rate"
            ],
            "average_time_to_hire_days": (
                average_time_to_hire[
                    "average_time_to_hire_days"
                ]
            ),
        }