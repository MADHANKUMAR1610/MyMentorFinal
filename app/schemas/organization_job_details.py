from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel


# ============================================================
# JOB
# ============================================================

class JobDetailsJobResponse(BaseModel):

    id: UUID
    job_id: str

    title: str
    department: str | None = None
    location: str | None = None

    work_mode: str | None = None
    employment_type: str

    experience_min: int | None = None
    experience_max: int | None = None

    openings: int
    status: str

    created_at: datetime

    summary: str | None = None

    responsibilities: list[str] = []

    required_skills: list[str] = []

    preferred_skills: list[str] = []

    ats_weights: dict


# ============================================================
# OVERVIEW
# ============================================================

class JobDetailsOverviewResponse(BaseModel):

    applications: int
    matched: int
    shortlisted: int
    interviews: int
    finalists: int
    selected: int

    avg_ats_score: float


# ============================================================
# APPLICATION
# ============================================================

class JobDetailsApplicationResponse(BaseModel):

    application_id: UUID
    candidate_id: UUID | None

    candidate_name: str

    applied_at: datetime

    ats_score: float | None
    match_score: float | None

    experience: str | None

    stage: str

    recruiter: str | None


# ============================================================
# MATCHED PROFILE
# ============================================================

class JobDetailsMatchedProfileResponse(BaseModel):

    candidate_id: UUID | None

    candidate_name: str

    designation: str | None

    ats_score: float | None
    match_score: float | None

    relevant_skills: list[str]
    missing_skills: list[str]

    match_reason: str


# ============================================================
# PIPELINE
# ============================================================

class JobDetailsPipelineResponse(BaseModel):

    applied: list[JobDetailsApplicationResponse]
    screening: list[JobDetailsApplicationResponse]
    shortlisted: list[JobDetailsApplicationResponse]
    interview: list[JobDetailsApplicationResponse]
    technical_round: list[JobDetailsApplicationResponse]
    hr_round: list[JobDetailsApplicationResponse]
    finalist: list[JobDetailsApplicationResponse]
    selected: list[JobDetailsApplicationResponse]
    rejected: list[JobDetailsApplicationResponse]


# ============================================================
# INTERVIEW
# ============================================================

class JobDetailsInterviewResponse(BaseModel):

    interview_id: UUID

    candidate_id: UUID | None

    candidate_name: str

    type: str

    interviewer: str | None

    scheduled_at: datetime

    status: str


# ============================================================
# ANALYTICS
# ============================================================

class JobDetailsAnalyticsResponse(BaseModel):

    avg_ats_score: float
    avg_match_score: float

    match_rate: float
    conversion: float


# ============================================================
# COMPLETE RESPONSE
# ============================================================

class OrganizationJobDetailsResponse(BaseModel):

    job: JobDetailsJobResponse

    overview: JobDetailsOverviewResponse

    applications: list[JobDetailsApplicationResponse]

    matched_profiles: list[JobDetailsMatchedProfileResponse]

    pipeline: JobDetailsPipelineResponse

    interviews: list[JobDetailsInterviewResponse]

    analytics: JobDetailsAnalyticsResponse