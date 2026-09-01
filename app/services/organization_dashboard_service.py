from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.organization_repository import (
    OrganizationRepository,
)

from app.repositories.organization_dashboard_repository import (
    OrganizationDashboardRepository,
)


class OrganizationDashboardService:

    def __init__(
        self,
        db: AsyncSession,
    ):
        self.db = db

        self.organization_repository = (
            OrganizationRepository(db)
        )

        self.dashboard_repository = (
            OrganizationDashboardRepository(db)
        )

    # ============================================================
    # GET DASHBOARD
    # ============================================================

    async def get_dashboard(
        self,
        user_id: UUID,
    ):

        # --------------------------------------------------------
        # Find organization
        # --------------------------------------------------------

        organization = await (
            self.organization_repository
            .get_by_admin_user_id(user_id)
        )

        if organization is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found for this user.",
            )

        company_id = organization.id

        # --------------------------------------------------------
        # Organization statistics
        # --------------------------------------------------------

        user_counts = await (
            self.dashboard_repository
            .get_user_counts(company_id)
        )

        job_counts = await (
            self.dashboard_repository
            .get_job_counts(company_id)
        )

        # --------------------------------------------------------
        # Application statistics
        # --------------------------------------------------------

        application_counts = await (
            self.dashboard_repository
            .get_application_counts(company_id)
        )

        # --------------------------------------------------------
        # Active jobs
        # --------------------------------------------------------

        active_jobs = await (
            self.dashboard_repository
            .get_active_jobs(company_id)
        )

        active_job_data = []

        for job in active_jobs:

            application_counts_for_job = await (
                self.dashboard_repository
                .get_job_application_counts(job.id)
            )

            active_job_data.append(
                {
                    "id": job.id,
                    "title": job.title,
                    "department": getattr(
                        job,
                        "department",
                        None,
                    ),
                    "location": job.location,

                    "applications":
                        application_counts_for_job[
                            "applications"
                        ],

                    "matched":
                        application_counts_for_job[
                            "matched"
                        ],

                    "shortlisted":
                        application_counts_for_job[
                            "shortlisted"
                        ],

                    "interviews":
                        application_counts_for_job[
                            "interviews"
                        ],

                    "selected":
                        application_counts_for_job[
                            "selected"
                        ],

                    "status": job.status,
                }
            )

        # --------------------------------------------------------
        # Recruitment funnel
        # --------------------------------------------------------

        funnel = {
            "applications":
                application_counts[
                    "total_applications"
                ],

            "matched":
                application_counts[
                    "matched_profiles"
                ],

            "screening":
                0,

            "shortlisted":
                application_counts[
                    "shortlisted"
                ],

            "interview":
                application_counts[
                    "interviews"
                ],

            "finalist":
                0,

            "selected":
                application_counts[
                    "selected"
                ],
        }

        # --------------------------------------------------------
        # Final response
        # --------------------------------------------------------

        return {
            "organization": {
                **user_counts,
                **job_counts,
            },

            "candidates": application_counts,

            "recruitment_funnel": funnel,

            "active_jobs": active_job_data,

            "recent_activity": [],
        }