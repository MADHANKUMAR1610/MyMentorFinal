from uuid import UUID

from pydantic import BaseModel, Field


class CodeExecutionRequest(BaseModel):
    checkpoint_id: UUID

    language: str = Field(
        min_length=1,
        max_length=30,
    )

    code: str = Field(
        min_length=1,
    )


class TestCaseResult(BaseModel):
    test_case_number: int
    passed: bool
    input: str
    expected_output: str
    actual_output: str | None = None
    error: str | None = None


class CodeExecutionResponse(BaseModel):
    success: bool

    checkpoint_id: UUID

    passed_tests: int
    total_tests: int

    results: list[TestCaseResult]

    checkpoint_completed: bool = False
    level_completed: bool = False

    xp_earned: int = 0

    next_checkpoint_id: UUID | None = None