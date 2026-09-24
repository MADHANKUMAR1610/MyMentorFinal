from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


# ============================================================
# CATEGORY
# ============================================================

class SkillAssessmentCategoryResponse(BaseModel):

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID
    name: str
    description: str | None
    max_questions: int
    question_count: int
    display_order: int
    is_active: bool


# ============================================================
# CREATE QUESTION
# ============================================================

class SkillAssessmentQuestionCreate(BaseModel):

    category_id: UUID

    title: str = Field(
        min_length=2,
        max_length=200,
    )

    problem: str = Field(
        min_length=1,
    )

    instructions: str | None = None

    language: str = Field(
        default="Java",
        min_length=1,
        max_length=30,
    )

    difficulty: str = Field(
        default="Beginner",
        min_length=1,
        max_length=30,
    )

    points: int = Field(
        default=10,
        ge=0,
    )

    starter_code: str | None = None

    expected_answer: str | None = None

    evaluation_criteria: str | None = None


# ============================================================
# UPDATE QUESTION
# ============================================================

class SkillAssessmentQuestionUpdate(BaseModel):

    title: str | None = Field(
        default=None,
        max_length=200,
    )

    problem: str | None = None

    instructions: str | None = None

    language: str | None = Field(
        default=None,
        max_length=30,
    )

    difficulty: str | None = Field(
        default=None,
        max_length=30,
    )

    points: int | None = Field(
        default=None,
        ge=0,
    )

    starter_code: str | None = None

    expected_answer: str | None = None

    evaluation_criteria: str | None = None

    is_active: bool | None = None


# ============================================================
# ADMIN QUESTION RESPONSE
# ============================================================

class SkillAssessmentQuestionResponse(BaseModel):

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID
    category_id: UUID
    question_order: int
    title: str
    problem: str
    instructions: str | None
    language: str
    difficulty: str
    points: int
    starter_code: str | None
    expected_answer: str | None
    evaluation_criteria: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime