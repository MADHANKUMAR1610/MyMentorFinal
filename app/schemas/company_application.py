from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CompanyApplicationCreate(BaseModel):
    company_name: str = Field(
        min_length=2,
        max_length=200,
    )

    website: str | None = None

    industry: str = Field(
        min_length=1,
        max_length=100,
    )

    contact_name: str = Field(
        min_length=2,
        max_length=150,
    )

    email: str

    size: str | None = Field(
        default=None,
        max_length=50,
    )

    location: str | None = Field(
        default=None,
        max_length=255,
    )

    about: str | None = None

    hiring_needs: str | None = None

    submitted_by: UUID | None = None

    status: str = Field(
        default="pending",
        max_length=30,
    )


class CompanyApplicationUpdate(BaseModel):
    company_name: str | None = Field(
        default=None,
        min_length=2,
        max_length=200,
    )

    website: str | None = None

    industry: str | None = Field(
        default=None,
        max_length=100,
    )

    contact_name: str | None = Field(
        default=None,
        min_length=2,
        max_length=150,
    )

    email: str | None = None

    size: str | None = Field(
        default=None,
        max_length=50,
    )

    location: str | None = Field(
        default=None,
        max_length=255,
    )

    about: str | None = None

    hiring_needs: str | None = None

    status: str | None = Field(
        default=None,
        max_length=30,
    )


class CompanyApplicationResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID
    company_name: str
    website: str | None
    industry: str
    contact_name: str
    email: str
    size: str | None
    location: str | None
    about: str | None
    hiring_needs: str | None
    submitted_by: UUID | None
    status: str
    created_at: datetime
    updated_at: datetime