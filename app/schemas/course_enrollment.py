from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class CourseEnrollmentResponse(BaseModel):

    model_config = ConfigDict(
        from_attributes=True
    )

    id: UUID
    course_id: UUID

    title: str
    description: str | None = None
    language: str
    difficulty: str
    duration: str | None = None
    thumbnail: str | None = None

    enrolled_at: datetime