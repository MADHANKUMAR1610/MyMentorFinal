from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    HttpUrl,
)


ApplicationStatus = Literal[
    "submitted",
    "screening",
    "shortlisted",
    "interview",
    "technical_round",
    "hr_round",
    "finalist",
    "selected",
    "rejected",
    "withdrawn",
]

ResumeSource = Literal[
    "profile",
    "new_upload",
    "external_link",
]
class JobApplicationCreate(BaseModel):
    job_id: UUID

    # Usually taken from the authenticated user.
    # Do not trust this value from the frontend.
    applicant_user_id: UUID | None = None

    name: str = Field(
        min_length=2,
        max_length=150,
    )

    email: EmailStr

    phone: str | None = Field(
        default=None,
        max_length=20,
    )

    experience: str | None = Field(
        default=None,
        max_length=100,
    )

    cover_note: str | None = None

    resume_file_id: UUID | None = None

    resume_source: ResumeSource = "profile"

    resume_link: HttpUrl | None = None
class JobApplicationUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=150,
    )

    email: EmailStr | None = None

    phone: str | None = Field(
        default=None,
        max_length=20,
    )

    experience: str | None = Field(
        default=None,
        max_length=100,
    )

    cover_note: str | None = None

    resume_link: HttpUrl | None = None

    resume_file_id: UUID | None = None

    resume_source: ResumeSource | None = None
class JobApplicationStatusUpdate(BaseModel):
    status: ApplicationStatus
class JobApplicationResponse(BaseModel):
    id: UUID
    job_id: UUID
    applicant_user_id: UUID | None = None
    recruiter_id: UUID | None = None

    name: str
    email: str
    phone: str | None = None
    experience: str | None = None
    cover_note: str | None = None

    resume_file_id: UUID | None = None
    resume_source: str | None = None
    resume_link: str | None = None
    resume_url: str | None = None

    source: str | None = None
    ats_score: float | None = None
    match_score: float | None = None

    status: str

    screened_at: datetime | None = None
    shortlisted_at: datetime | None = None
    interviewed_at: datetime | None = None
    finalist_at: datetime | None = None
    selected_at: datetime | None = None
    rejected_at: datetime | None = None

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )
class JobApplicationStatsResponse(BaseModel):
    total: int
    submitted: int
    screening: int
    shortlisted: int
    interview: int
    technical_round: int
    hr_round: int
    finalist: int
    selected: int
    rejected: int
    withdrawn: int
class OrganizationApplicationStatsResponse(BaseModel):
    total: int
    submitted: int
    screening: int
    shortlisted: int
    interview: int
    technical_round: int
    hr_round: int
    finalist: int
    selected: int
    rejected: int
    withdrawn: int
