from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class JobApplicationCreate(BaseModel):
    job_id: UUID

    applicant_user_id: UUID | None = None

    name: str = Field(
        min_length=2,
        max_length=150,
    )

    email: str

    phone: str | None = Field(
        default=None,
        max_length=20,
    )

    experience: str | None = Field(
        default=None,
        max_length=100,
    )

    cover_note: str | None = None

    resume_link: str | None = None

    status: str = Field(
        default="submitted",
        max_length=30,
    )


class JobApplicationUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=150,
    )

    email: str | None = None

    phone: str | None = Field(
        default=None,
        max_length=20,
    )

    experience: str | None = Field(
        default=None,
        max_length=100,
    )

    cover_note: str | None = None

    resume_link: str | None = None

    status: str | None = Field(
        default=None,
        max_length=30,
    )


class JobApplicationResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID
    job_id: UUID
    applicant_user_id: UUID | None
    name: str
    email: str
    phone: str | None
    experience: str | None
    cover_note: str | None
    resume_link: str | None
    status: str
    created_at: datetime
    updated_at: datetime