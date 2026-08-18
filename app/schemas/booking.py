from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class BookingCreate(BaseModel):
    mentor_id: UUID

    scheduled_at: datetime

    topic: str | None = None

    mode: str = Field(
        default="Google Meet",
        max_length=30,
    )

    meeting_link: str | None = None

    status: str = Field(
        default="upcoming",
        max_length=30,
    )

    report: dict | None = None


class BookingUpdate(BaseModel):
    scheduled_at: datetime | None = None

    topic: str | None = None

    mode: str | None = Field(
        default=None,
        max_length=30,
    )

    meeting_link: str | None = None

    status: str | None = Field(
        default=None,
        max_length=30,
    )

    report: dict | None = None


class BookingResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID
    mentor_id: UUID
    user_id: UUID
    scheduled_at: datetime
    topic: str | None
    mode: str
    meeting_link: str | None
    status: str
    report: dict | None
    created_at: datetime
    updated_at: datetime