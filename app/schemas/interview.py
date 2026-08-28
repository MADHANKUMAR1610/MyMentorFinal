from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


# ============================================================
# CREATE INTERVIEW
# ============================================================

class InterviewCreate(BaseModel):

    application_id: UUID

    interviewer_id: UUID

    title: str = Field(
        min_length=2,
        max_length=200,
    )

    interview_type: str = Field(
        max_length=30,
    )

    scheduled_at: datetime

    duration_minutes: int = Field(
        default=30,
        ge=15,
        le=480,
    )

    mode: str = Field(
        max_length=30,
    )

    meeting_link: str | None = None

    location: str | None = Field(
        default=None,
        max_length=255,
    )

    notes: str | None = None


# ============================================================
# UPDATE INTERVIEW
# ============================================================

class InterviewUpdate(BaseModel):

    interviewer_id: UUID | None = None

    title: str | None = Field(
        default=None,
        min_length=2,
        max_length=200,
    )

    interview_type: str | None = Field(
        default=None,
        max_length=30,
    )

    scheduled_at: datetime | None = None

    duration_minutes: int | None = Field(
        default=None,
        ge=15,
        le=480,
    )

    mode: str | None = Field(
        default=None,
        max_length=30,
    )

    meeting_link: str | None = None

    location: str | None = Field(
        default=None,
        max_length=255,
    )

    notes: str | None = None


# ============================================================
# UPDATE INTERVIEW STATUS
# ============================================================

class InterviewStatusUpdate(BaseModel):

    status: str = Field(
        max_length=30,
    )


# ============================================================
# INTERVIEW FEEDBACK
# ============================================================

class InterviewFeedbackUpdate(BaseModel):

    rating: int | None = Field(
        default=None,
        ge=1,
        le=5,
    )

    feedback: str | None = None

    recommendation: str | None = Field(
        default=None,
        max_length=30,
    )

    notes: str | None = None


# ============================================================
# INTERVIEW RESPONSE
# ============================================================

class InterviewResponse(BaseModel):

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID

    company_id: UUID

    application_id: UUID

    interviewer_id: UUID

    title: str

    interview_type: str

    scheduled_at: datetime

    duration_minutes: int

    mode: str

    meeting_link: str | None

    location: str | None

    status: str

    rating: int | None

    feedback: str | None

    recommendation: str | None

    notes: str | None

    created_at: datetime

    updated_at: datetime