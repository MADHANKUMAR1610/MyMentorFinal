from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.organization_repository import (
    OrganizationRepository,
)

from app.repositories.organization_dashboard_repository import (
    OrganizationDashboardRepository,
)
from app.repositories.audit_log_repository import (
    AuditLogRepository,
)

from app.repositories.organization_analytics_repository import (
    OrganizationAnalyticsRepository,
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

        self.audit_log_repository = (
            AuditLogRepository(db)
        )

        self.analytics_repository = (
            OrganizationAnalyticsRepository(db)
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
        # Candidate quality
        # --------------------------------------------------------

        candidate_quality = await (
            self.analytics_repository
            .get_candidate_quality(company_id)
        )
        # --------------------------------------------------------
        # Recent activity
        # --------------------------------------------------------

        audit_logs = await (
            self.audit_log_repository
            .get_by_company_id(
                company_id,
                skip=0,
                limit=10,
            )
        )

        recent_activity = []

        for log in audit_logs:

            activity = None

            if log.action == "login":
                activity = f"{log.user or 'User'} logged in"

            elif log.action == "logout":
                activity = f"{log.user or 'User'} logged out"

            elif log.action == "user_created":
                activity = f"{log.user or 'Admin'} created a user"

            elif log.action == "user_updated":
                activity = f"{log.user or 'Admin'} updated a user"

            elif log.action == "user_deleted":
                activity = f"{log.user or 'Admin'} deleted a user"

            elif log.action == "password_reset_requested":
                activity = (
                    f"{log.user or 'User'} requested a password reset"
                )

            else:
                activity = (
                    f"{log.user or 'User'} performed "
                    f"{log.action.replace('_', ' ')}"
                )

            recent_activity.append(
                {
                    "activity": activity,
                    "created_at": log.created_at,
                }
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

           "candidate_quality": {
              "average_ats_score":
                  candidate_quality["average_ats_score"],

              "average_match_score":
                  candidate_quality["average_match_score"],

              "score_distribution":
                  candidate_quality["score_distribution"],

              "above_90":
                  candidate_quality["above_90"],

              "below_60":
                  candidate_quality["below_60"],
            },

            "active_jobs": active_job_data,

            "recent_activity": recent_activity,
        }