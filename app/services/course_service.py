from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.course import Course
from app.repositories.course_repository import CourseRepository


class CourseService:

    def __init__(self, session: AsyncSession):
        self.repository = CourseRepository(session)

    async def get_by_id(
        self,
        course_id: UUID,
    ) -> Course | None:

        return await self.repository.get_by_id(course_id)

    async def get_by_title(
        self,
        title: str,
    ) -> Course | None:

        return await self.repository.get_by_title(title)

    async def get_by_status(
        self,
        status: str,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Course]:

        return await self.repository.get_by_status(
            status,
            skip=skip,
            limit=limit,
        )

    async def get_published(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Course]:

        return await self.repository.get_published(
            skip=skip,
            limit=limit,
        )

    async def get_by_language(
        self,
        language: str,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Course]:

        return await self.repository.get_by_language(
            language,
            skip=skip,
            limit=limit,
        )

    async def get_by_difficulty(
        self,
        difficulty: str,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Course]:

        return await self.repository.get_by_difficulty(
            difficulty,
            skip=skip,
            limit=limit,
        )

    async def create_course(
        self,
        course: Course,
    ) -> Course:

        return await self.repository.create(course)

    async def update_course(
        self,
        course: Course,
    ) -> Course:

        return await self.repository.update(course)

    async def delete_course(
        self,
        course: Course,
    ) -> None:

        await self.repository.delete(course)

    async def get_courses_with_level_count(
        self,
        *,
        course_status: str | None = None,
        language: str | None = None,
        difficulty: str | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[tuple[Course, int]]:

        return await self.repository.get_courses_with_level_count(
            course_status=course_status,
            language=language,
            difficulty=difficulty,
            skip=skip,
            limit=limit,
        )