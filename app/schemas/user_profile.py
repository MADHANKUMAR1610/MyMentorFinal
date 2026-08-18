from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class UserProfileCreate(BaseModel):
    """
    Create a user profile.
    """

    dob: date | None = None

    age: int | None = Field(
        default=None,
        ge=0,
        le=120,
    )

    profile_category: str | None = Field(
        default=None,
        max_length=50,
    )

    education: str | None = Field(
        default=None,
        max_length=255,
    )

    class_year: str | None = Field(
        default=None,
        max_length=50,
    )

    institution: str | None = Field(
        default=None,
        max_length=255,
    )

    career_goal: str | None = Field(
        default=None,
        max_length=255,
    )

    career_interests: str | None = None


class UserProfileUpdate(BaseModel):
    """
    Update a user profile.
    """

    dob: date | None = None

    age: int | None = Field(
        default=None,
        ge=0,
        le=120,
    )

    profile_category: str | None = Field(
        default=None,
        max_length=50,
    )

    education: str | None = Field(
        default=None,
        max_length=255,
    )

    class_year: str | None = Field(
        default=None,
        max_length=50,
    )

    institution: str | None = Field(
        default=None,
        max_length=255,
    )

    career_goal: str | None = Field(
        default=None,
        max_length=255,
    )

    career_interests: str | None = None


class UserProfileResponse(BaseModel):
    """
    User profile API response.
    """

    model_config = ConfigDict(
        from_attributes=True
    )

    id: UUID
    user_id: UUID
    dob: date | None
    age: int | None
    profile_category: str | None
    education: str | None
    class_year: str | None
    institution: str | None
    career_goal: str | None
    career_interests: str | None
    created_at: datetime
    updated_at: datetime