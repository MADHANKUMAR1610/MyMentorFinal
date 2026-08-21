from uuid import UUID

from pydantic import BaseModel, ConfigDict


class CourseJourneyCheckpointResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID
    checkpoint_order: int
    title: str
    xp: int
    completed: bool


class CourseJourneyLevelResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID
    level_number: int
    title: str
    description: str | None = None
    xp: int

    completed_checkpoints: int
    total_checkpoints: int

    completed: bool
    unlocked: bool

    checkpoints: list[CourseJourneyCheckpointResponse]


class CourseJourneyStageResponse(BaseModel):
    stage: str
    stage_order: int

    completed_levels: int
    total_levels: int

    levels: list[CourseJourneyLevelResponse]


class CourseJourneyCourseResponse(BaseModel):
    id: UUID
    title: str
    description: str | None = None
    language: str
    difficulty: str
    duration: str | None = None
    thumbnail: str | None = None


class CourseJourneyProgressResponse(BaseModel):
    completed_levels: int
    total_levels: int


class CourseJourneyResponse(BaseModel):
    course: CourseJourneyCourseResponse
    progress: CourseJourneyProgressResponse
    stages: list[CourseJourneyStageResponse]