from uuid import UUID

import httpx
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.checkpoint import Checkpoint
from app.models.course_enrollment import CourseEnrollment
from app.models.level import Level
from app.models.progress import Progress
from app.models.user import User
from app.schemas.code_execution import (
    CodeExecutionResponse,
    TestCaseResult,
)


class CodeExecutionService:
    """
    Handles student code execution and checkpoint submission.
    """

    LANGUAGE_IDS = {
        "python": 71,
        "python3": 71,
        "java": 62,
        "javascript": 63,
        "js": 63,
        "c++": 54,
        "cpp": 54,
        "c#": 51,
        "csharp": 51,
    }

    def __init__(
        self,
        session: AsyncSession,
    ):
        self.session = session

    # ============================================================
    # GET CHECKPOINT
    # ============================================================

    async def get_checkpoint(
        self,
        checkpoint_id: UUID,
    ) -> Checkpoint:

        result = await self.session.execute(
            select(Checkpoint).where(
                Checkpoint.id == checkpoint_id
            )
        )

        checkpoint = result.scalar_one_or_none()

        if checkpoint is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Checkpoint not found.",
            )

        return checkpoint

    # ============================================================
    # GET LEVEL
    # ============================================================

    async def get_level(
        self,
        level_id: UUID,
    ) -> Level:

        result = await self.session.execute(
            select(Level).where(
                Level.id == level_id
            )
        )

        level = result.scalar_one_or_none()

        if level is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Level not found.",
            )

        return level

    # ============================================================
    # CHECK ENROLLMENT
    # ============================================================

    async def check_enrollment(
        self,
        user_id: UUID,
        course_id: UUID,
    ) -> None:

        result = await self.session.execute(
            select(CourseEnrollment).where(
                CourseEnrollment.user_id == user_id,
                CourseEnrollment.course_id == course_id,
            )
        )

        enrollment = result.scalar_one_or_none()

        if enrollment is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "You are not enrolled in this course."
                ),
            )

    # ============================================================
    # LANGUAGE
    # ============================================================

    def get_language_id(
        self,
        language: str,
    ) -> int:

        language_id = self.LANGUAGE_IDS.get(
            language.lower().strip()
        )

        if language_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Unsupported programming language: "
                    f"{language}"
                ),
            )

        return language_id

    # ============================================================
    # TEST CASE VALUE
    # ============================================================

    @staticmethod
    def get_test_input(
        test_case: dict,
    ) -> str:

        value = test_case.get(
            "input",
            test_case.get(
                "stdin",
                "",
            ),
        )

        if value is None:
            return ""

        return str(value)

    # ============================================================
    # EXPECTED OUTPUT
    # ============================================================

    @staticmethod
    def get_expected_output(
        test_case: dict,
    ) -> str:

        value = test_case.get(
            "expected_output",
            test_case.get(
                "output",
                test_case.get(
                    "expected",
                    "",
                ),
            ),
        )

        if value is None:
            return ""

        return str(value)

    # ============================================================
    # NORMALIZE OUTPUT
    # ============================================================

    @staticmethod
    def normalize_output(
        value: str | None,
    ) -> str:

        if value is None:
            return ""

        return value.strip().replace(
            "\r\n",
            "\n",
        )

    # ============================================================
    # EXECUTE ONE TEST CASE
    # ============================================================

    async def execute_test_case(
        self,
        *,
        code: str,
        language: str,
        test_input: str,
        expected_output: str,
    ) -> tuple[bool, str | None, str | None]:

        language_id = self.get_language_id(
            language
        )

        url = (
            settings.CODE_EXECUTION_URL.rstrip("/")
            + "/submissions"
        )

        payload = {
            "source_code": code,
            "language_id": language_id,
            "stdin": test_input,
            "expected_output": expected_output,
            "cpu_time_limit": 3,
            "wall_time_limit": 5,
            "memory_limit": 128000,
            "enable_network": False,
        }

        headers = {
            "Content-Type": "application/json",
        }

        if settings.CODE_EXECUTION_API_KEY:
            headers["X-Auth-Token"] = (
                settings.CODE_EXECUTION_API_KEY
            )

        async with httpx.AsyncClient(
            timeout=15.0
        ) as client:

            response = await client.post(
                url,
                json=payload,
                headers=headers,
                params={
                    "base64_encoded": "false",
                    "wait": "true",
                },
            )

        if response.status_code not in (
            200,
            201,
        ):
            raise HTTPException(
                status_code=502,
                detail=(
                    "Code execution service "
                    "is unavailable."
                ),
            )

        data = response.json()

        status_data = data.get(
            "status",
            {},
        )

        status_id = status_data.get(
            "id"
        )

        actual_output = (
            data.get("stdout")
            or ""
        )

        stderr = (
            data.get("stderr")
            or ""
        )

        compile_output = (
            data.get("compile_output")
            or ""
        )

        error = (
            stderr
            or compile_output
            or data.get("message")
        )

        passed = (
            status_id == 3
            and self.normalize_output(
                actual_output
            )
            == self.normalize_output(
                expected_output
            )
        )

        return (
            passed,
            actual_output,
            error,
        )

    # ============================================================
    # RUN
    # ============================================================

    async def run_code(
        self,
        *,
        user: User,
        checkpoint_id: UUID,
        language: str,
        code: str,
    ) -> CodeExecutionResponse:

        checkpoint = await self.get_checkpoint(
            checkpoint_id
        )

        level = await self.get_level(
            checkpoint.level_id
        )

        await self.check_enrollment(
            user.id,
            level.course_id,
        )

        test_cases = (
            checkpoint.visible_test_cases
            or []
        )

        if not test_cases:
            raise HTTPException(
                status_code=400,
                detail=(
                    "No visible test cases are "
                    "configured for this checkpoint."
                ),
            )

        results = []

        passed_count = 0

        for index, test_case in enumerate(
            test_cases,
            start=1,
        ):

            test_input = (
                self.get_test_input(
                    test_case
                )
            )

            expected_output = (
                self.get_expected_output(
                    test_case
                )
            )

            (
                passed,
                actual_output,
                error,
            ) = await self.execute_test_case(
                code=code,
                language=language,
                test_input=test_input,
                expected_output=expected_output,
            )

            if passed:
                passed_count += 1

            results.append(
                TestCaseResult(
                    test_case_number=index,
                    passed=passed,
                    input=test_input,
                    expected_output=expected_output,
                    actual_output=actual_output,
                    error=error,
                )
            )

        return CodeExecutionResponse(
            success=(
                passed_count
                == len(test_cases)
            ),
            checkpoint_id=checkpoint.id,
            passed_tests=passed_count,
            total_tests=len(test_cases),
            results=results,
        )

    # ============================================================
    # SUBMIT
    # ============================================================

    async def submit_code(
        self,
        *,
        user: User,
        checkpoint_id: UUID,
        language: str,
        code: str,
    ) -> CodeExecutionResponse:

        checkpoint = await self.get_checkpoint(
            checkpoint_id
        )

        level = await self.get_level(
            checkpoint.level_id
        )

        await self.check_enrollment(
            user.id,
            level.course_id,
        )

        # --------------------------------------------------------
        # GET ALL TEST CASES
        # --------------------------------------------------------

        visible_tests = (
            checkpoint.visible_test_cases
            or []
        )

        hidden_tests = (
            checkpoint.hidden_test_cases
            or []
        )

        test_cases = (
            visible_tests
            + hidden_tests
        )

        if not test_cases:
            raise HTTPException(
                status_code=400,
                detail=(
                    "No test cases are configured "
                    "for this checkpoint."
                ),
            )

        results = []

        passed_count = 0

        for index, test_case in enumerate(
            test_cases,
            start=1,
        ):

            test_input = (
                self.get_test_input(
                    test_case
                )
            )

            expected_output = (
                self.get_expected_output(
                    test_case
                )
            )

            (
                passed,
                actual_output,
                error,
            ) = await self.execute_test_case(
                code=code,
                language=language,
                test_input=test_input,
                expected_output=expected_output,
            )

            if passed:
                passed_count += 1

            results.append(
                TestCaseResult(
                    test_case_number=index,
                    passed=passed,
                    input=test_input,
                    expected_output=expected_output,
                    actual_output=actual_output,
                    error=error,
                )
            )

        all_passed = (
            passed_count
            == len(test_cases)
        )

        # --------------------------------------------------------
        # NOT PASSED
        # --------------------------------------------------------

        if not all_passed:

            return CodeExecutionResponse(
                success=False,
                checkpoint_id=checkpoint.id,
                passed_tests=passed_count,
                total_tests=len(test_cases),
                results=results,
            )

        # --------------------------------------------------------
        # GET PROGRESS
        # --------------------------------------------------------

        result = await self.session.execute(
            select(Progress).where(
                Progress.user_id == user.id,
                Progress.level_id == level.id,
            )
        )

        progress = result.scalar_one_or_none()

        if progress is None:

            progress = Progress(
                user_id=user.id,
                course_id=level.course_id,
                level_id=level.id,
                checkpoints_passed=[],
                video_completed=False,
                completed=False,
            )

            self.session.add(progress)

            await self.session.flush()

        passed_checkpoints = [
            str(checkpoint)
            for checkpoint in (
                progress.checkpoints_passed
                or []
            )
        ]

        checkpoint_id_string = str(
            checkpoint.id
        )

        already_completed = (
            checkpoint_id_string
            in passed_checkpoints
        )

        xp_earned = 0

        if not already_completed:

            passed_checkpoints.append(
                checkpoint_id_string
            )

            progress.checkpoints_passed = (
                passed_checkpoints
            )

            xp_earned = checkpoint.xp or 0

            user.xp = (
                user.xp or 0
            ) + xp_earned

        # --------------------------------------------------------
        # CHECK LEVEL COMPLETION
        # --------------------------------------------------------

        result = await self.session.execute(
            select(Checkpoint)
            .where(
                Checkpoint.level_id == level.id
            )
        )

        level_checkpoints = list(
            result.scalars().all()
        )

        all_checkpoint_ids = {
            str(item.id)
            for item in level_checkpoints
        }

        current_passed_ids = {
            str(item)
            for item in (
                progress.checkpoints_passed
                or []
            )
        }

        all_checkpoints_completed = (
            all_checkpoint_ids
            .issubset(
                current_passed_ids
            )
        )

        level_completed = (
            all_checkpoints_completed
            and progress.video_completed
        )

        progress.completed = (
            level_completed
        )

        # --------------------------------------------------------
        # FIND NEXT CHECKPOINT
        # --------------------------------------------------------

        result = await self.session.execute(
            select(Checkpoint)
            .where(
                Checkpoint.level_id == level.id,
                Checkpoint.checkpoint_order
                > checkpoint.checkpoint_order,
            )
            .order_by(
                Checkpoint.checkpoint_order.asc()
            )
        )

        next_checkpoint = (
            result.scalars().first()
        )

        await self.session.flush()

        return CodeExecutionResponse(
            success=True,
            checkpoint_id=checkpoint.id,
            passed_tests=passed_count,
            total_tests=len(test_cases),
            results=results,
            checkpoint_completed=True,
            level_completed=level_completed,
            xp_earned=xp_earned,
            next_checkpoint_id=(
                next_checkpoint.id
                if next_checkpoint
                else None
            ),
        )