from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


# ============================================================
# ORGANIZATION SUMMARY
# ============================================================

class OrganizationDashboardSummary(BaseModel):

    total_users: int
    active_users: int

    total_jobs: int
    active_jobs: int


# ============================================================
# CANDIDATE SUMMARY
# ============================================================

class CandidateDashboardSummary(BaseModel):

    total_applications: int
    matched_profiles: int
    shortlisted: int
    interviews: int
    selected: int


# ============================================================
# RECRUITMENT FUNNEL
# ============================================================

class RecruitmentFunnelResponse(BaseModel):

    applications: int
    matched: int
    screening: int
    shortlisted: int
    interview: int
    finalist: int
    selected: int


# ============================================================
# ACTIVE JOB OVERVIEW
# ============================================================

class ActiveJobDashboardResponse(BaseModel):

    id: UUID
    title: str
    department: str | None
    location: str | None

    applications: int
    matched: int
    shortlisted: int
    interviews: int
    selected: int

    status: str


# ============================================================
# RECENT ACTIVITY
# ============================================================

class RecentActivityResponse(BaseModel):

    activity: str
    created_at: datetime
# ============================================================
# CANDIDATE QUALITY
# ============================================================

class CandidateQualityDashboardResponse(BaseModel):

    average_ats_score: float
    average_match_score: float

    score_distribution: dict[str, int]

    above_90: int
    below_60: int

# ============================================================
# COMPLETE DASHBOARD
# ============================================================

class OrganizationDashboardResponse(BaseModel):

    organization: OrganizationDashboardSummary

    candidates: CandidateDashboardSummary

    recruitment_funnel: RecruitmentFunnelResponse

    candidate_quality: CandidateQualityDashboardResponse

    active_jobs: list[ActiveJobDashboardResponse]

    recent_activity: list[RecentActivityResponse]