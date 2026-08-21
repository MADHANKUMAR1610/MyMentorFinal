from uuid import UUID

from pydantic import BaseModel


class CourseSuggestionResponse(BaseModel):
    id: UUID
    title: str
    description: str | None = None
    language: str
    difficulty: str
    duration: str | None = None
    thumbnail: str | None = None
    stream: str | None = None

    enrolled: bool = False
    enroll_endpoint: str
    skillhub_url: str


class CourseSuggestionListResponse(BaseModel):
    success: bool
    career_persona_id: UUID
    stream: str
    courses: list[CourseSuggestionResponse]