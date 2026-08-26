from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class WorkExperienceCreate(BaseModel):
    company_name: str = Field(
        min_length=1,
        max_length=255,
    )

    job_title: str = Field(
        min_length=1,
        max_length=255,
    )

    employment_type: str | None = Field(
        default=None,
        max_length=100,
    )

    location: str | None = Field(
        default=None,
        max_length=255,
    )

    start_date: date | None = None

    end_date: date | None = None

    currently_working: bool = False

    description: str | None = None

    skills: str | None = None


class WorkExperienceUpdate(BaseModel):
    company_name: str | None = Field(
        default=None,
        max_length=255,
    )

    job_title: str | None = Field(
        default=None,
        max_length=255,
    )

    employment_type: str | None = Field(
        default=None,
        max_length=100,
    )

    location: str | None = Field(
        default=None,
        max_length=255,
    )

    start_date: date | None = None

    end_date: date | None = None

    currently_working: bool | None = None

    description: str | None = None

    skills: str | None = None


class WorkExperienceResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID
    user_profile_id: UUID

    company_name: str
    job_title: str
    employment_type: str | None
    location: str | None

    start_date: date | None
    end_date: date | None
    currently_working: bool

    description: str | None
    skills: str | None

    created_at: datetime
    updated_at: datetime