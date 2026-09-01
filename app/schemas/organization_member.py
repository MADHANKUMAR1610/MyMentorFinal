from datetime import datetime
from uuid import UUID
from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
)


# ============================================================
# ORGANIZATION MEMBER ROLES
# ============================================================

OrganizationMemberRole = Literal[
    "organization_admin",
    "hr_admin",
    "recruiter",
    "hiring_manager",
    "interviewer",
    "viewer",
]


# ============================================================
# CREATE ORGANIZATION MEMBER
# ============================================================

class OrganizationMemberCreate(BaseModel):

    name: str = Field(
        min_length=2,
        max_length=150,
    )

    email: EmailStr

    phone: str | None = Field(
        default=None,
        max_length=20,
    )

    department: str | None = Field(
        default=None,
        max_length=150,
    )

    designation: str | None = Field(
        default=None,
        max_length=150,
    )

    role: OrganizationMemberRole

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

    email: EmailStr | None = None

    phone: str | None = Field(
        default=None,
        max_length=20,
    )

    department: str | None = Field(
        default=None,
        max_length=150,
    )

    designation: str | None = Field(
        default=None,
        max_length=150,
    )

    role: OrganizationMemberRole | None = None


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

    department: str | None

    designation: str | None

    role: str

    company_id: UUID | None

    is_active: bool

    is_verified: bool

    created_at: datetime

    updated_at: datetime
class OrganizationMemberPasswordReset(BaseModel):

    password: str = Field(
        min_length=6,
        max_length=100,
    )