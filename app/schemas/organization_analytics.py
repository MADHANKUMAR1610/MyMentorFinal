from uuid import UUID

from pydantic import BaseModel, ConfigDict


# ============================================================
# USERS ANALYTICS
# ============================================================

class UserAnalytics(BaseModel):

    total: int
    active: int


# ============================================================
# JOB ANALYTICS
# ============================================================

class JobAnalytics(BaseModel):

    total: int
    active: int


# ============================================================
# APPLICATION ANALYTICS
# ============================================================

class ApplicationAnalytics(BaseModel):

    total: int
    by_status: dict[str, int]


# ============================================================
# INTERVIEW ANALYTICS
# ============================================================

class InterviewAnalytics(BaseModel):

    total: int
    by_status: dict[str, int]


# ============================================================
# ORGANIZATION RECRUITMENT ANALYTICS RESPONSE
# ============================================================

class OrganizationRecruitmentAnalyticsResponse(BaseModel):

    model_config = ConfigDict(
        from_attributes=True,
    )

    company_id: UUID

    users: UserAnalytics

    jobs: JobAnalytics

    applications: ApplicationAnalytics

    interviews: InterviewAnalytics