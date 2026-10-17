
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class SkillAssessmentCodeRequest(BaseModel):
    language: str = Field(min_length=1, max_length=30)
    code: str = Field(min_length=1)


class SkillAssessmentTestResult(BaseModel):
    test_case_number: int
    passed: bool
    input: str
    expected_output: str
    actual_output: str | None = None
    error: str | None = None


class SkillAssessmentCodeResponse(BaseModel):
    success: bool
    question_id: UUID
    passed_tests: int
    total_tests: int
    results: list[SkillAssessmentTestResult]
    score_data: dict[str, Any] | None = None
