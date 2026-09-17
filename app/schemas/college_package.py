from datetime import datetime
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)


# ============================================================
# CREATE PACKAGE
# ============================================================

class CollegePackageCreate(BaseModel):

    college_id: UUID

    package_name: str = Field(
        ...,
        min_length=2,
        max_length=255,
    )

    description: str | None = None

    course_ids: list[UUID] = Field(
        ...,
        min_length=1,
    )


# ============================================================
# UPDATE PACKAGE
# ============================================================

class CollegePackageUpdate(BaseModel):

    package_name: str | None = Field(
        default=None,
        min_length=2,
        max_length=255,
    )

    description: str | None = None

    course_ids: list[UUID] | None = None


# ============================================================
# COURSE INSIDE PACKAGE
# ============================================================

class CollegePackageCourseResponse(BaseModel):

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID
    title: str
    description: str | None
    language: str
    difficulty: str
    duration: str | None
    thumbnail: str | None
    status: str


# ============================================================
# PACKAGE RESPONSE
# ============================================================

class CollegePackageResponse(BaseModel):

    id: UUID

    college_id: UUID

    college_name: str

    package_name: str

    description: str | None

    course_ids: list[UUID]

    courses: list[
        CollegePackageCourseResponse
    ]

    created_at: datetime

    updated_at: datetime