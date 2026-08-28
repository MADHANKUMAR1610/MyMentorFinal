from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


# ============================================================
# CREATE ORGANIZATION MEMBER
# ============================================================
class OrganizationMemberCreate(BaseModel):

    name: str = Field(
        min_length=2,
        max_length=150,
    )

    email: str

    phone: str | None = Field(
        default=None,
        max_length=20,
    )

    password: str = Field(
        min_length=6,
        max_length=100,
    )


# ============================================================
# UPDATE MEMBER
# ============================================================

class OrganizationMemberUpdate(BaseModel):

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

    role: str | None = Field(
        default=None,
        max_length=30,
    )


# ============================================================
# UPDATE MEMBER STATUS
# ============================================================

class OrganizationMemberStatusUpdate(BaseModel):

    is_active: bool


# ============================================================
# MEMBER RESPONSE
# ============================================================

class OrganizationMemberResponse(BaseModel):

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID

    name: str

    email: str | None

    phone: str | None

    role: str

    company_id: UUID | None

    is_active: bool

    is_verified: bool

    created_at: datetime

    updated_at: datetime