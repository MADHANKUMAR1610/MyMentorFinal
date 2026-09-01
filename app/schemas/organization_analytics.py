from uuid import UUID

from pydantic import BaseModel, ConfigDict


# ============================================================
# COMMON
# ============================================================

class AnalyticsBase(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )


# ============================================================
# 1. RECRUITMENT DASHBOARD OVERVIEW
# ============================================================

class RecruitmentOverviewResponse(AnalyticsBase):

    company_id: UUID

    total_jobs: int
    active_jobs: int

    applications: int
    matched: int
    shortlisted: int
    interviews: int
    finalists: int
    selected: int
    rejected: int

    conversion: float
    avg_ats: float
    time_to_hire: float


# ============================================================
# 2. JOB PERFORMANCE
# ============================================================

class JobPerformanceItem(AnalyticsBase):

    job_id: UUID
    job_title: str
    department: str | None

    applications: int
    matched: int
    match_rate: float

    shortlisted: int
    interviews: int
    selected: int

    avg_ats: float
    days_open: int
    conversion: float


class JobPerformanceResponse(AnalyticsBase):

    company_id: UUID

    jobs: list[JobPerformanceItem]


# ============================================================
# 3. RECRUITMENT FUNNEL
# ============================================================

class RecruitmentFunnelResponse(AnalyticsBase):

    company_id: UUID

    applications: int
    matched: int
    screened: int
    shortlisted: int
    interviewed: int
    finalists: int
    selected: int
    rejected: int


# ============================================================
# 4. CANDIDATE QUALITY
# ============================================================

class CandidateQualityResponse(AnalyticsBase):

    company_id: UUID

    total_candidates: int

    average_ats_score: float
    average_match_score: float

    score_distribution: dict[str, int]

    above_90: int
    below_60: int


# ============================================================
# 5. SOURCE ANALYTICS
# ============================================================

class SourceAnalyticsItem(AnalyticsBase):

    source: str

    applications: int
    shortlisted: int
    interviews: int
    hires: int

    conversion: float


class SourceAnalyticsResponse(AnalyticsBase):

    company_id: UUID

    sources: list[SourceAnalyticsItem]


# ============================================================
# 6. TIME TO HIRE
# ============================================================

class TimeToHireItem(AnalyticsBase):

    job_id: UUID
    job_title: str

    average_days: float
    hires: int


class TimeToHireResponse(AnalyticsBase):

    company_id: UUID

    average_time_to_hire: float

    jobs: list[TimeToHireItem]

    job_to_first_application: float
    application_to_screening: float
    screening_to_shortlist: float
    shortlist_to_interview: float
    interview_to_selection: float


# ============================================================
# 7. RECRUITER ANALYTICS
# ============================================================

class RecruiterAnalyticsItem(AnalyticsBase):

    recruiter_id: UUID
    recruiter_name: str

    jobs: int

    applications: int
    shortlisted: int
    interviews: int
    selected: int

    avg_days: float
    conversion: float


class RecruiterAnalyticsResponse(AnalyticsBase):

    company_id: UUID

    recruiters: list[RecruiterAnalyticsItem]
# ============================================================
# 8. SKILL GAP
# ============================================================

# ============================================================
# 8. SKILL GAP
# ============================================================

class SkillGapItem(AnalyticsBase):

    skill: str
    count: int


class SkillGapResponse(AnalyticsBase):

    company_id: UUID

    most_requested_skills: list[SkillGapItem]

    candidate_gaps: list[SkillGapItem]
# ============================================================
# 9. JOB HEALTH
# ============================================================

class JobHealthItem(AnalyticsBase):

    job_id: UUID
    job_title: str
    status: str

    applications: int
    qualified_matches: int
    average_score: float
    days_open: int

    health_status: str


class JobHealthResponse(AnalyticsBase):

    company_id: UUID

    jobs: list[JobHealthItem]


# ============================================================
# EXISTING GENERAL ANALYTICS
# ============================================================

class UserAnalytics(AnalyticsBase):

    total: int
    active: int


class JobAnalytics(AnalyticsBase):

    total: int
    active: int


class ApplicationAnalytics(AnalyticsBase):

    total: int
    by_status: dict[str, int]


class InterviewAnalytics(AnalyticsBase):

    total: int
    by_status: dict[str, int]


class OrganizationRecruitmentAnalyticsResponse(
    AnalyticsBase
):

    company_id: UUID

    users: UserAnalytics

    jobs: JobAnalytics

    applications: ApplicationAnalytics

    interviews: InterviewAnalytics


# ============================================================
# 10. COMPLETE RECRUITMENT DASHBOARD
# ============================================================

class RecruitmentDashboardResponse(AnalyticsBase):

    company_id: UUID

    overview: RecruitmentOverviewResponse

    job_performance: JobPerformanceResponse

    funnel: RecruitmentFunnelResponse

    candidate_quality: CandidateQualityResponse

    sources: SourceAnalyticsResponse

    time_to_hire: TimeToHireResponse

    recruiters: RecruiterAnalyticsResponse

    skill_gap: SkillGapResponse

    job_health: list[JobHealthItem]