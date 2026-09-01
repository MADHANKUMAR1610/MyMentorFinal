from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.organization_analytics_repository import (
    OrganizationAnalyticsRepository,
)


class OrganizationAnalyticsService:

    def __init__(self, db: AsyncSession):

        self.analytics_repository = (
            OrganizationAnalyticsRepository(db)
        )

    # ============================================================
    # 1. EXISTING RECRUITMENT ANALYTICS
    # ============================================================

    async def get_recruitment_analytics(
        self,
        company_id: UUID,
    ):

        total_users = await (
            self.analytics_repository
            .get_total_users(company_id)
        )

        active_users = await (
            self.analytics_repository
            .get_active_users(company_id)
        )

        total_jobs = await (
            self.analytics_repository
            .get_total_jobs(company_id)
        )

        active_jobs = await (
            self.analytics_repository
            .get_active_jobs(company_id)
        )

        total_applications = await (
            self.analytics_repository
            .get_total_applications(company_id)
        )

        application_statuses = await (
            self.analytics_repository
            .get_applications_by_status(company_id)
        )

        applications_by_status = {
            status_name: count
            for status_name, count in application_statuses
        }

        total_interviews = await (
            self.analytics_repository
            .get_total_interviews(company_id)
        )

        interview_statuses = await (
            self.analytics_repository
            .get_interviews_by_status(company_id)
        )

        interviews_by_status = {
            status_name: count
            for status_name, count in interview_statuses
        }

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
    # 2. APPLICATION TREND
    # ============================================================

    async def get_application_trend(
        self,
        company_id: UUID,
    ):

        return await (
            self.analytics_repository
            .get_application_trend(company_id)
        )

    # ============================================================
    # 3. RECRUITMENT FUNNEL
    # ============================================================

    async def get_recruitment_funnel(
        self,
        company_id: UUID,
    ):

        return await (
            self.analytics_repository
            .get_recruitment_funnel(company_id)
        )

    # ============================================================
    # 4. INTERVIEW ANALYTICS
    # ============================================================

    async def get_interview_analytics(
        self,
        company_id: UUID,
    ):

        return await (
            self.analytics_repository
            .get_interview_analytics(company_id)
        )

    # ============================================================
    # 5. JOB-WISE RECRUITMENT ANALYTICS
    # ============================================================

    async def get_job_wise_recruitment_analytics(
        self,
        company_id: UUID,
    ):

        return await (
            self.analytics_repository
            .get_job_wise_recruitment_analytics(
                company_id
            )
        )

    # ============================================================
    # 6. HIRING RATE
    # ============================================================

    async def get_hiring_rate(
        self,
        company_id: UUID,
    ):

        return await (
            self.analytics_repository
            .get_hiring_rate(company_id)
        )

    # ============================================================
    # 7. AVERAGE TIME TO HIRE
    # ============================================================

    async def get_average_time_to_hire(
        self,
        company_id: UUID,
    ):

        return await (
            self.analytics_repository
            .get_average_time_to_hire(
                company_id
            )
        )

    # ============================================================
    # 8. COMPLETE RECRUITMENT DASHBOARD
    # ============================================================

    async def get_recruitment_dashboard(
        self,
        company_id: UUID,
    ):

        # --------------------------------------------------------
        # OVERVIEW
        # --------------------------------------------------------

        overview = await (
            self.analytics_repository
            .get_overview(company_id)
        )

        # --------------------------------------------------------
        # JOB PERFORMANCE
        # --------------------------------------------------------

        job_performance = await (
            self.analytics_repository
            .get_job_performance(company_id)
        )

        # --------------------------------------------------------
        # RECRUITMENT FUNNEL
        # --------------------------------------------------------

        funnel = await (
            self.analytics_repository
            .get_recruitment_funnel(company_id)
        )

        # --------------------------------------------------------
        # CANDIDATE QUALITY
        # --------------------------------------------------------

        candidate_quality = await (
            self.analytics_repository
            .get_candidate_quality(company_id)
        )

        # --------------------------------------------------------
        # SOURCE ANALYTICS
        # --------------------------------------------------------

        sources = await (
            self.analytics_repository
            .get_source_analytics(company_id)
        )

        # --------------------------------------------------------
        # TIME TO HIRE
        # --------------------------------------------------------

        time_to_hire = await (
            self.analytics_repository
            .get_time_to_hire(company_id)
        )

        # --------------------------------------------------------
        # RECRUITER ANALYTICS
        # --------------------------------------------------------

        recruiters = await (
            self.analytics_repository
            .get_recruiter_analytics(company_id)
        )

        # --------------------------------------------------------
        # SKILL GAP
        # --------------------------------------------------------

        skill_gap = await (
            self.analytics_repository
            .get_skill_gap(company_id)
        )

        # --------------------------------------------------------
        # JOB HEALTH
        # --------------------------------------------------------

        job_health = await (
            self.analytics_repository
            .get_job_health(company_id)
        )

        # --------------------------------------------------------
        # FINAL DASHBOARD RESPONSE
        # --------------------------------------------------------

        return {
            "company_id": company_id,

            "overview": overview,

            "job_performance": job_performance,

            "funnel": funnel,

            "candidate_quality": candidate_quality,

            "sources": sources,

            "time_to_hire": time_to_hire,

            "recruiters": recruiters,

            "skill_gap": skill_gap,

            "job_health": job_health,
        }

    # ============================================================
    # 9. JOB HEALTH
    # ============================================================

    async def get_job_health(
        self,
        company_id: UUID,
    ):

        return await (
            self.analytics_repository
            .get_job_health(company_id)
        )