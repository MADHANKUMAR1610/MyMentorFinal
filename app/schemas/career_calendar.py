from uuid import UUID

from pydantic import BaseModel, ConfigDict


class CareerCalendarCreate(BaseModel):
    career_persona_id: UUID
    add_to_calendar: bool


class CareerCalendarResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID
    user_id: UUID
    career_persona_id: UUID
    added_to_calendar: bool


class CourseSuggestionResponse(BaseModel):
    id: UUID
    title: str
    description: str | None = None
    language: str
    difficulty: str
    duration: str | None = None
    thumbnail: str | None = None
    enrolled: bool = False