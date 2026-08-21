from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CheckpointCreate(BaseModel):
    level_id: UUID

    checkpoint_order: int = Field(
        ge=1,
    )

    at_seconds: int = Field(
        ge=0,
    )

    title: str = Field(
        min_length=2,
        max_length=200,
    )

    scenario: str | None = None

    problem_statement: str

    objective: str | None = None

    difficulty: str = Field(
        default="Easy",
        max_length=30,
    )

    marks: int = Field(
        default=25,
        ge=0,
    )

    xp: int = Field(
        default=25,
        ge=0,
    )

    retry_limit: int = Field(
        default=5,
        ge=0,
    )

    language: str = Field(
        default="python",
        max_length=30,
    )

    starter_code: dict = Field(
        default_factory=dict,
    )

    constraints: str | None = None

    hints: list = Field(
        default_factory=list,
    )

    solution: str | None = None

    explanation: str | None = None

    visible_test_cases: list = Field(
        default_factory=list,
    )

    hidden_test_cases: list = Field(
        default_factory=list,
    )


class CheckpointUpdate(BaseModel):
    checkpoint_order: int | None = Field(
        default=None,
        ge=1,
    )

    at_seconds: int | None = Field(
        default=None,
        ge=0,
    )

    title: str | None = Field(
        default=None,
        max_length=200,
    )

    scenario: str | None = None

    problem_statement: str | None = None

    objective: str | None = None

    difficulty: str | None = Field(
        default=None,
        max_length=30,
    )

    marks: int | None = Field(
        default=None,
        ge=0,
    )

    xp: int | None = Field(
        default=None,
        ge=0,
    )

    retry_limit: int | None = Field(
        default=None,
        ge=0,
    )

    language: str | None = Field(
        default=None,
        max_length=30,
    )

    starter_code: dict | None = None

    constraints: str | None = None

    hints: list | None = None

    solution: str | None = None

    explanation: str | None = None

    visible_test_cases: list | None = None

    hidden_test_cases: list | None = None


class CheckpointResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID
    level_id: UUID
    checkpoint_order: int
    at_seconds: int
    title: str
    scenario: str | None
    problem_statement: str
    objective: str | None
    difficulty: str
    marks: int
    xp: int
    retry_limit: int
    language: str
    starter_code: dict
    constraints: str | None
    hints: list
    explanation: str | None
    visible_test_cases: list
    created_at: datetime
    updated_at: datetime