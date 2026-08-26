from datetime import datetime
from uuid import UUID
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


CourseCategory = Literal[
    "Programming",
    "Artificial Intelligence",
    "Communication",
    "Leadership",
    "Interview Preparation",
    "Cloud",
    "Cyber Security",
    "Data Science",
]


class CourseCreate(BaseModel):

    title: str = Field(
        min_length=2,
        max_length=200,
    )

    description: str | None = None

    category: CourseCategory

    language: str = Field(
        default="Python",
        max_length=50,
    )

    difficulty: str = Field(
        default="Beginner",
        max_length=50,
    )

    duration: str | None = Field(
        default=None,
        max_length=50,
    )

    thumbnail: str | None = None

    status: str = Field(
        default="draft",
        max_length=30,
    )

    certificate_template: str | None = Field(
        default=None,
        max_length=100,
    )


class CourseUpdate(BaseModel):

    title: str | None = Field(
        default=None,
        min_length=2,
        max_length=200,
    )

    description: str | None = None

    category: CourseCategory | None = None

    language: str | None = Field(
        default=None,
        max_length=50,
    )

    difficulty: str | None = Field(
        default=None,
        max_length=50,
    )

    duration: str | None = Field(
        default=None,
        max_length=50,
    )

    thumbnail: str | None = None

    status: str | None = Field(
        default=None,
        max_length=30,
    )

    certificate_template: str | None = Field(
        default=None,
        max_length=100,
    )


class CourseResponse(BaseModel):

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID

    title: str

    description: str | None

    category: CourseCategory

    language: str

    difficulty: str

    duration: str | None

    thumbnail: str | None

    status: str

    certificate_template: str | None

    created_at: datetime

    updated_at: datetime

    level_count: int = 0

    enrollment_count: int = 0