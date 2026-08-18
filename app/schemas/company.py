from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CompanyCreate(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=200,
    )

    industry: str = Field(
        min_length=1,
        max_length=100,
    )

    logo: str | None = None

    location: str | None = Field(
        default=None,
        max_length=255,
    )

    size: str | None = Field(
        default=None,
        max_length=50,
    )

    open_roles: int = Field(
        default=0,
        ge=0,
    )

    about: str | None = None

    website: str | None = None

    status: str = Field(
        default="pending",
        max_length=30,
    )

    verified: bool = False


class CompanyUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=200,
    )

    industry: str | None = Field(
        default=None,
        max_length=100,
    )

    logo: str | None = None

    location: str | None = Field(
        default=None,
        max_length=255,
    )

    size: str | None = Field(
        default=None,
        max_length=50,
    )

    open_roles: int | None = Field(
        default=None,
        ge=0,
    )

    about: str | None = None

    website: str | None = None

    status: str | None = Field(
        default=None,
        max_length=30,
    )

    verified: bool | None = None


class CompanyResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID
    name: str
    industry: str
    logo: str | None
    location: str | None
    size: str | None
    open_roles: int
    about: str | None
    website: str | None
    status: str
    verified: bool
    created_at: datetime
    updated_at: datetime