
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.skill_assessment_question import (
    SkillAssessmentQuestion,
)
from app.services.code_execution_service import (
    CodeExecutionService,
)
from app.services.skill_assessment_service import (
    SkillAssessmentService,
)


class SkillAssessmentExecutionService:

    def __init__(self, session: AsyncSession):
        self.session = session
        self.executor = CodeExecutionService(session)
        self.assessment_service = SkillAssessmentService(session)

    async def execute(
        self,
        *,
        user_id: UUID,
        question_id: UUID,
        language: str,
        code: str,
        submit: bool,
    ) -> dict:

        # 1. Get the active assessment question.
        result = await self.session.execute(
            select(SkillAssessmentQuestion).where(
                SkillAssessmentQuestion.id == question_id,
                SkillAssessmentQuestion.is_active.is_(True),
            )
        )
        question = result.scalar_one_or_none()

        if question is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Active assessment question not found.",
            )

        # 2. Validate the language.
        if language.strip().lower() != question.language.strip().lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"This question requires {question.language}.",
            )

        execution_type = self.executor.get_execution_type(language)

        if execution_type != "judge0":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This implementation supports Judge0 languages only.",
            )

        expected_output = (question.expected_answer or "").strip()

        if submit and not expected_output:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Configure expected_answer before submitting this question.",
            )

        # 3. Execute code.
        # Run does not save scores. Submit evaluates the output.
        try:
            _, actual_output, error = (
                await self.executor.execute_test_case(
                    code=code,
                    language=language,
                    test_input="",
                    expected_output=expected_output,
                )
            )
        except Exception:
            await self.session.rollback()
            raise

        actual_output = (
            actual_output.strip()
            if actual_output is not None
            else ""
        )

        # 4. Compare normalized output.
        passed = (
            error is None
            and bool(expected_output)
            and actual_output == expected_output
        )

        # 5. Save score only when Submit is used.
        score_data = None

        if submit:
            try:
                score_data = (
                    await self.assessment_service.record_assessment_score(
                        user_id=user_id,
                        question=question,
                        passed=passed,
                    )
                )
                await self.session.commit()
            except Exception:
                await self.session.rollback()
                raise

        # 6. Return the execution result.
        return {
            "success": error is None,
            "question_id": question.id,
            "passed_tests": int(passed),
            "total_tests": 1,
            "results": [
                {
                    "test_case_number": 1,
                    "passed": passed,
                    "input": "",
                    "expected_output": expected_output,
                    "actual_output": actual_output,
                    "error": error,
                }
            ],
            "score_data": score_data,
        }
