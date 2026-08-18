from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ProgressCreate(BaseModel):
    user_id: UUID
    course_id: UUID
    level_id: UUID

    checkpoints_passed: list = Field(
        default_factory=list,
    )

    video_completed: bool = False

    completed: bool = False


class ProgressUpdate(BaseModel):
    checkpoints_passed: list | None = None

    video_completed: bool | None = None

    completed: bool | None = None


class ProgressResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID
    user_id: UUID
    course_id: UUID
    level_id: UUID
    checkpoints_passed: list
    video_completed: bool
    completed: bool
    created_at: datetime
    updated_at: datetime