import json
from uuid import UUID

import httpx
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.checkpoint import Checkpoint
from app.models.course import Course
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

    # ============================================================
    # JUDGE0 LANGUAGE IDS
    # ============================================================

    LANGUAGE_IDS = {

        # Python
        "python": 71,
        "python3": 71,

        # Java
        "java": 62,

        # JavaScript
        "javascript": 63,
        "js": 63,

        # C
        "c": 50,

        # C++
        "c++": 54,
        "cpp": 54,

        # C#
        "c#": 51,
        "csharp": 51,

        # Go
        "go": 60,

        # PHP
        "php": 68,

        # Kotlin
        "kotlin": 78,

        # Rust
        "rust": 73,
    }

    # ============================================================
    # EXECUTION TYPES
    # ============================================================

    EXECUTION_TYPES = {

        # Judge0
        "python": "judge0",
        "java": "judge0",
        "javascript": "judge0",
        "c": "judge0",
        "cpp": "judge0",
        "csharp": "judge0",
        "go": "judge0",
        "php": "judge0",
        "kotlin": "judge0",
        "rust": "judge0",

        # Separate execution engines
        "sql": "sql",
        "react": "react",
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
    # GET COURSE
    # ============================================================

    async def get_course(
        self,
        course_id: UUID,
    ) -> Course:

        result = await self.session.execute(
            select(Course).where(
                Course.id == course_id
            )
        )

        course = result.scalar_one_or_none()

        if course is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found.",
            )

        return course

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
    # EXECUTION TYPE
    # ============================================================

    def get_execution_type(
        self,
        language: str,
    ) -> str:

        execution_type = self.EXECUTION_TYPES.get(
            language.lower().strip()
        )

        if execution_type is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Unsupported execution language: "
                    f"{language}"
                ),
            )

        return execution_type

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
    # EXECUTE ONE JUDGE0 TEST CASE
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
    # SQL
    # ============================================================

    async def execute_sql(
        self,
        *,
        code: str,
        checkpoint: Checkpoint,
        test_input: str = "",
        expected_output: str = "",
    ) -> tuple[bool, str | None, str | None]:

        from app.database.sql_sandbox import SQLSandboxSessionLocal

        sql = code.strip()

        if not sql:
            return (
                False,
                None,
                "SQL code cannot be empty.",
            )

        # ------------------------------------------------------------
        # BASIC SAFETY CHECK
        # ------------------------------------------------------------

        forbidden_keywords = [
            "drop database",
            "drop schema",
            "create extension",
            "alter system",
            "copy ",
            "pg_read_file",
            "pg_write_file",
            "lo_import",
            "lo_export",
            "dblink",
        ]

        normalized_sql = sql.lower()

        for keyword in forbidden_keywords:
            if keyword in normalized_sql:
                return (
                    False,
                    None,
                    f"SQL operation is not allowed: {keyword.strip()}",
                )

        # ------------------------------------------------------------
        # OPEN SANDBOX SESSION
        # ------------------------------------------------------------

        async with SQLSandboxSessionLocal() as session:
            try:
                # ----------------------------------------------------
                # START TRANSACTION
                # ----------------------------------------------------

                await session.begin()

                # ----------------------------------------------------
                # LIMIT EXECUTION TIME
                # ----------------------------------------------------

                await session.execute(
                    text(
                        "SET LOCAL statement_timeout = '3000ms'"
                    )
                )

                await session.execute(
                    text(
                        "SET LOCAL lock_timeout = '1000ms'"
                    )
                )

                # ----------------------------------------------------
                # OPTIONAL SETUP SQL
                # ----------------------------------------------------

                setup_sql = (
                    test_input.strip()
                    if test_input
                    else ""
                )

                if setup_sql:
                    await session.execute(
                        text(setup_sql)
                    )

                # ----------------------------------------------------
                # EXECUTE STUDENT SQL
                # ----------------------------------------------------

                result = await session.execute(
                    text(sql)
                )

                # ----------------------------------------------------
                # GET RESULT
                # ----------------------------------------------------

                if result.returns_rows:
                    rows = result.fetchall()

                    actual_data = [
                        list(row)
                        for row in rows
                    ]

                    actual_output = json.dumps(
                        actual_data,
                        ensure_ascii=False,
                    )

                else:
                    actual_output = str(
                        result.rowcount
                    )

                # ----------------------------------------------------
                # ROLLBACK STUDENT CHANGES
                # ----------------------------------------------------
                # Never permanently save student SQL changes.
                # ----------------------------------------------------

                await session.rollback()

                normalized_actual = actual_output.strip()
                normalized_expected = expected_output.strip()

                passed = (
                    normalized_actual
                    == normalized_expected
                )

                return (
                    passed,
                    actual_output,
                    None,
                )

            except Exception as exc:
                await session.rollback()

                return (
                    False,
                    None,
                    str(exc),
                )

    # ============================================================
    # REACT
    # ============================================================

    async def execute_react(
        self,
        *,
        code: str,
        checkpoint: Checkpoint,
    ) -> tuple[bool, str | None, str | None]:

        if not code or not code.strip():
            return (
                False,
                None,
                "React code cannot be empty.",
            )

        code = code.strip()

        react_indicators = [
            "import React",
            "from 'react'",
            'from "react"',
            "useState",
            "useEffect",
            "useContext",
            "useReducer",
            "useRef",
            "export default",
            "function App",
            "const App",
            "class App",
            "ReactDOM",
            "createRoot",
        ]

        if not any(
            indicator in code
            for indicator in react_indicators
        ):
            return (
                False,
                None,
                (
                    "Invalid React code. "
                    "Please create a valid React component."
                ),
            )

        jsx_indicators = [
            "<div",
            "<h1",
            "<h2",
            "<p",
            "<button",
            "<input",
            "<form",
            "<section",
            "<main",
            "<header",
            "<footer",
            "<App",
        ]

        if not any(
            indicator in code
            for indicator in jsx_indicators
        ):
            return (
                False,
                None,
                (
                    "React component detected, "
                    "but JSX markup was not found."
                ),
            )

        has_app_component = (
            "function App" in code
            or "const App" in code
            or "class App" in code
            or "export default App" in code
        )

        if not has_app_component:
            return (
                False,
                None,
                (
                    "React App component not found. "
                    "Create an App component."
                ),
            )

        # The frontend React sandbox is responsible for:
        # 1. React runtime
        # 2. JSX compilation
        # 3. Live preview
        # 4. Compile/runtime errors

        return (
            True,
            code,
            None,
        )

    # ============================================================
    # EXECUTION ROUTER
    # ============================================================

    async def execute_by_language(
        self,
        *,
        language: str,
        code: str,
        checkpoint: Checkpoint,
        test_input: str = "",
        expected_output: str = "",
    ) -> tuple[bool, str | None, str | None]:

        normalized_language = (
            language.lower().strip()
        )

        execution_type = self.get_execution_type(
            normalized_language
        )

        if execution_type == "judge0":

            return await self.execute_test_case(
                code=code,
                language=normalized_language,
                test_input=test_input,
                expected_output=expected_output,
            )

        if execution_type == "sql":

            return await self.execute_sql(
                code=code,
                checkpoint=checkpoint,
                test_input=test_input,
                expected_output=expected_output,
            )

        if execution_type == "react":

            return await self.execute_react(
                code=code,
                checkpoint=checkpoint,
            )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Unsupported execution type: "
                f"{execution_type}"
            ),
        )

    # VALIDATE CHECKPOINT LANGUAGE
    # ============================================================

    def validate_checkpoint_language(
        self,
        *,
        checkpoint: Checkpoint,
        language: str,
    ) -> None:

        expected_language = (
            checkpoint.language
            .lower()
            .strip()
        )

        submitted_language = (
            language
            .lower()
            .strip()
        )

        if expected_language != submitted_language:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"This checkpoint requires "
                    f"{checkpoint.language}."
                ),
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

        course = await self.get_course(
            level.course_id
        )

        await self.check_enrollment(
            user.id,
            course.id,
        )

        self.validate_checkpoint_language(
            checkpoint=checkpoint,
            language=language,
        )

        # --------------------------------------------------------
        # REACT
        # --------------------------------------------------------

        if language.lower().strip() == "react":

            passed, actual_output, error = (
                await self.execute_react(
                    code=code,
                    checkpoint=checkpoint,
                )
            )

            result = TestCaseResult(
                test_case_number=1,
                passed=passed,
                input="",
                expected_output="React component",
                actual_output=actual_output,
                error=error,
            )

            return CodeExecutionResponse(
                success=passed,
                checkpoint_id=checkpoint.id,
                passed_tests=1 if passed else 0,
                total_tests=1,
                results=[result],
            )

        # --------------------------------------------------------
        # NORMAL LANGUAGES
        # --------------------------------------------------------

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
            ) = await self.execute_by_language(
                code=code,
                language=language,
                checkpoint=checkpoint,
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

        course = await self.get_course(
            level.course_id
        )

        await self.check_enrollment(
            user.id,
            course.id,
        )

        self.validate_checkpoint_language(
            checkpoint=checkpoint,
            language=language,
        )

        # --------------------------------------------------------
        # REACT
        # --------------------------------------------------------

        if language.lower().strip() == "react":

            passed, actual_output, error = (
                await self.execute_react(
                    code=code,
                    checkpoint=checkpoint,
                )
            )

            results = [
                TestCaseResult(
                    test_case_number=1,
                    passed=passed,
                    input="",
                    expected_output="React component",
                    actual_output=actual_output,
                    error=error,
                )
            ]

            passed_count = 1 if passed else 0
            total_tests = 1

        else:

            # ----------------------------------------------------
            # GET ALL TEST CASES
            # ----------------------------------------------------

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
                ) = await self.execute_by_language(
                    code=code,
                    language=language,
                    checkpoint=checkpoint,
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

            total_tests = len(test_cases)

        all_passed = (
            passed_count
            == total_tests
        )

        # --------------------------------------------------------
        # NOT PASSED
        # --------------------------------------------------------

        if not all_passed:

            return CodeExecutionResponse(
                success=False,
                checkpoint_id=checkpoint.id,
                passed_tests=passed_count,
                total_tests=total_tests,
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
            str(item)
            for item in (
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
            total_tests=total_tests,
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

