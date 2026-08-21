from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


# ============================================================
# CREATE LEVEL
# ============================================================

class LevelCreate(BaseModel):

    course_id: UUID

    stage: str = Field(
        min_length=1,
        max_length=50,
    )

    stage_order: int = Field(
        ge=1,
    )

    level_number: int = Field(
        ge=1,
    )

    global_order: int = Field(
        ge=1,
    )

    title: str = Field(
        min_length=2,
        max_length=200,
    )

    description: str | None = None

    objectives: list = Field(
        default_factory=list,
    )

    xp: int = Field(
        default=100,
        ge=0,
    )

    pass_percentage: int = Field(
        default=100,
        ge=0,
        le=100,
    )

    duration: str | None = Field(
        default=None,
        max_length=50,
    )

    video: dict = Field(
        default_factory=dict,
    )

    theory: dict = Field(
        default_factory=dict,
    )


# ============================================================
# UPDATE LEVEL
# ============================================================

class LevelUpdate(BaseModel):

    stage: str | None = Field(
        default=None,
        max_length=50,
    )

    stage_order: int | None = Field(
        default=None,
        ge=1,
    )

    level_number: int | None = Field(
        default=None,
        ge=1,
    )

    global_order: int | None = Field(
        default=None,
        ge=1,
    )

    title: str | None = Field(
        default=None,
        max_length=200,
    )

    description: str | None = None

    objectives: list | None = None

    xp: int | None = Field(
        default=None,
        ge=0,
    )

    pass_percentage: int | None = Field(
        default=None,
        ge=0,
        le=100,
    )

    duration: str | None = Field(
        default=None,
        max_length=50,
    )

    video: dict | None = None

    theory: dict | None = None


# ============================================================
# LEVEL RESPONSE
# ============================================================

class LevelResponse(BaseModel):

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID

    course_id: UUID

    stage: str

    stage_order: int

    level_number: int

    global_order: int

    title: str

    description: str | None

    objectives: list

    xp: int

    pass_percentage: int

    duration: str | None

    video: dict

    theory: dict

    created_at: datetime

    updated_at: datetime


# ============================================================
# LEVEL DROPDOWN RESPONSE
# ============================================================

# ============================================================
# LEVEL DROPDOWN RESPONSE
# ============================================================

class LevelDropdownResponse(BaseModel):

    id: UUID

    course_id: UUID

    stage: str

    stage_order: int

    level_number: int

    checkpoint_count: int