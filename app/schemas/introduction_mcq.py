from uuid import UUID

from pydantic import BaseModel, Field


class IntroductionMCQSubmit(BaseModel):

    level_id: UUID

    question_index: int = Field(
        ge=0,
    )

    selected_option: str = Field(
        min_length=1,
        max_length=1,
    )


class IntroductionMCQResponse(BaseModel):

    correct: bool

    message: str

    question_index: int

    level_completed: bool

    next_level_unlocked: bool