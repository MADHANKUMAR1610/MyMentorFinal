from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


# ============================================================
# CREATE JOB
# ============================================================

class JobCreate(BaseModel):

    company_id: UUID | None = None

    title: str = Field(
        min_length=2,
        max_length=200,
    )

    company_name: str = Field(
        min_length=2,
        max_length=200,
    )

    location: str | None = Field(
        default=None,
        max_length=255,
    )

    job_type: str = Field(
        default="Full-time",
        max_length=50,
    )

    experience: str | None = Field(
        default=None,
        max_length=100,
    )

    salary: str | None = Field(
        default=None,
        max_length=100,
    )

    skills: list[str] = Field(
        default_factory=list,
    )

    description: str = Field(
        min_length=1,
    )

    apply_email: str | None = None

    status: str = Field(
        default="active",
        max_length=30,
    )


# ============================================================
# UPDATE JOB
# ============================================================

class JobUpdate(BaseModel):

    company_id: UUID | None = None

    title: str | None = Field(
        default=None,
        min_length=2,
        max_length=200,
    )

    company_name: str | None = Field(
        default=None,
        max_length=200,
    )

    location: str | None = Field(
        default=None,
        max_length=255,
    )

    job_type: str | None = Field(
        default=None,
        max_length=50,
    )

    experience: str | None = Field(
        default=None,
        max_length=100,
    )

    salary: str | None = Field(
        default=None,
        max_length=100,
    )

    skills: list[str] | None = None

    description: str | None = None

    apply_email: str | None = None

    status: str | None = Field(
        default=None,
        max_length=30,
    )


# ============================================================
# RESPONSE
# ============================================================

class JobResponse(BaseModel):

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID

    job_code: str

    company_id: UUID | None

    posted_by: UUID | None

    title: str

    company_name: str

    location: str | None

    job_type: str

    experience: str | None

    salary: str | None

    skills: list[str]

    description: str

    apply_email: str | None

    applicants: int

    status: str

    created_at: datetime

    updated_at: datetime