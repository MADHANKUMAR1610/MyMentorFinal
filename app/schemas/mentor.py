from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class MentorCreate(BaseModel):
    name: str = Field(min_length=2, max_length=150)

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

    image_url: str | None = None

    experience_years: int = Field(
        ge=0,
    )

    languages: str | None = Field(
        default=None,
        max_length=255,
    )

    skills: list[str] = Field(
        default_factory=list,
    )

    rating: Decimal = Field(
        default=Decimal("0"),
        ge=0,
        le=5,
    )

    price: int = Field(
        default=0,
        ge=0,
    )

    availability: str | None = Field(
        default=None,
        max_length=100,
    )

    status: str = Field(
        default="pending",
        max_length=30,
    )

    verified: bool = False


class MentorUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=150,
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

    image_url: str | None = None

    experience_years: int | None = Field(
        default=None,
        ge=0,
    )

    languages: str | None = Field(
        default=None,
        max_length=255,
    )

    skills: list[str] | None = None

    rating: Decimal | None = Field(
        default=None,
        ge=0,
        le=5,
    )

    price: int | None = Field(
        default=None,
        ge=0,
    )

    availability: str | None = Field(
        default=None,
        max_length=100,
    )

    status: str | None = Field(
        default=None,
        max_length=30,
    )

    verified: bool | None = None


class MentorResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID
    name: str
    role: str
    company: str | None
    industry: str
    image_url: str | None
    experience_years: int
    languages: str | None
    skills: list[str]
    rating: Decimal
    price: int
    availability: str | None
    status: str
    verified: bool
    created_at: datetime
    updated_at: datetime