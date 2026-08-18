from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    """
    Create a new user.
    """

    name: str = Field(
        min_length=2,
        max_length=150,
    )

    email: EmailStr

    password: str = Field(
        min_length=8,
        max_length=128,
    )


class UserUpdate(BaseModel):
    """
    Update user information.
    """

    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=150,
    )

    phone: str | None = Field(
        default=None,
        max_length=20,
    )


class UserResponse(BaseModel):
    """
    User API response.
    """

    model_config = ConfigDict(
        from_attributes=True
    )

    id: UUID
    email: str | None
    phone: str | None
    name: str
    role: str
    is_active: bool
    is_verified: bool
    xp: int
    streak: int
    last_active: str | None
    onboarded: bool
    created_at: datetime
    updated_at: datetime