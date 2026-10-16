
from datetime import datetime, time
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


AvailabilityType = Literal["Weekdays", "Weekends", "Flexible"]


class MentorApplicationCreate(BaseModel):
    name: str = Field(min_length=2, max_length=150)
    email: str
    phone: str | None = Field(default=None, max_length=20)
    role: str = Field(min_length=2, max_length=150)
    company: str | None = Field(default=None, max_length=150)
    industry: str = Field(min_length=1, max_length=100)
    experience_years: int = Field(ge=0)

    skills: str | None = None
    languages: str | None = None
    linkedin: str | None = None
    bio: str | None = None
    motivation: str | None = None

    price_per_session: int = Field(gt=0, le=1000000)
    availability: AvailabilityType
    start_time: time
    end_time: time

    @model_validator(mode="after")
    def validate_time_range(self):
        if self.end_time <= self.start_time:
            raise ValueError("end_time must be later than start_time")
        return self


class MentorApplicationUpdate(BaseModel):
    phone: str | None = Field(default=None, max_length=20)
    role: str | None = Field(default=None, max_length=150)
    company: str | None = Field(default=None, max_length=150)
    industry: str | None = Field(default=None, max_length=100)
    experience_years: int | None = Field(default=None, ge=0)

    skills: str | None = None
    languages: str | None = None
    linkedin: str | None = None
    bio: str | None = None
    motivation: str | None = None

    price_per_session: int | None = Field(
        default=None, gt=0, le=1000000
    )
    availability: AvailabilityType | None = None
    start_time: time | None = None
    end_time: time | None = None

    status: str | None = Field(default=None, max_length=30)

    @model_validator(mode="after")
    def validate_time_range(self):
        if (
            self.start_time is not None
            and self.end_time is not None
            and self.end_time <= self.start_time
        ):
            raise ValueError("end_time must be later than start_time")
        return self


class MentorApplicationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    email: str
    phone: str | None
    role: str
    company: str | None
    industry: str
    experience_years: int
    skills: str | None
    languages: str | None
    linkedin: str | None
    bio: str | None
    motivation: str | None

    price_per_session: int
    availability: str
    start_time: time
    end_time: time

    status: str
    created_at: datetime
    updated_at: datetime
