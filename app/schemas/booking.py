
from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


BookingMode = Literal["Google Meet", "Zoom", "Phone"]


class BookingCreate(BaseModel):
    mentor_id: UUID
    scheduled_at: datetime
    topic: str = Field(min_length=1, max_length=500)
    mode: BookingMode = "Google Meet"

    @field_validator("scheduled_at")
    @classmethod
    def validate_scheduled_at(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError(
                "scheduled_at must include a timezone"
            )

        if value <= datetime.now(value.tzinfo):
            raise ValueError(
                "Booking must be scheduled in the future"
            )

        return value

    @field_validator("topic")
    @classmethod
    def validate_topic(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Topic cannot be empty")
        return value


class BookingUpdate(BaseModel):
    scheduled_at: datetime | None = None
    topic: str | None = Field(default=None, max_length=500)
    mode: BookingMode | None = None


class BookingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

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
