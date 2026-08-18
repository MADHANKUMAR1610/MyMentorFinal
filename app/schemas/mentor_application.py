from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class MentorApplicationCreate(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=150,
    )

    email: str

    phone: str | None = Field(
        default=None,
        max_length=20,
    )

    role: str = Field(
        min_length=2,
        max_length=150,
    )

    company: str | None = Field(
        default=None,
        max_length=150,
    )

    industry: str = Field(
        min_length=1,
        max_length=100,
    )

    experience_years: int = Field(
        ge=0,
    )

    skills: str | None = None

    languages: str | None = None

    linkedin: str | None = None

    bio: str | None = None

    motivation: str | None = None

    status: str = Field(
        default="pending",
        max_length=30,
    )


class MentorApplicationUpdate(BaseModel):
    phone: str | None = Field(
        default=None,
        max_length=20,
    )

    role: str | None = Field(
        default=None,
        max_length=150,
    )

    company: str | None = Field(
        default=None,
        max_length=150,
    )

    industry: str | None = Field(
        default=None,
        max_length=100,
    )

    experience_years: int | None = Field(
        default=None,
        ge=0,
    )

    skills: str | None = None

    languages: str | None = None

    linkedin: str | None = None

    bio: str | None = None

    motivation: str | None = None

    status: str | None = Field(
        default=None,
        max_length=30,
    )


class MentorApplicationResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID
    name: str
    email: str
    phone: str | None
    role: str
    company: str | None
    industry: str
    experience_years: int
    skills: str | None
    languages: str | None
    linkedin: str | None
    bio: str | None
    motivation: str | None
    status: str
    created_at: datetime
    updated_at: datetime