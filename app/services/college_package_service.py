from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.college_package import CollegePackage
from app.repositories.college_package_repository import (
    CollegePackageRepository,
)
from app.repositories.college_repository import (
    CollegeRepository,
)
from app.repositories.course_repository import (
    CourseRepository,
)


class CollegePackageService:

    def __init__(
        self,
        session: AsyncSession,
    ):
        self.session = session

        self.repository = (
            CollegePackageRepository(
                session
            )
        )

        self.college_repository = (
            CollegeRepository(session)
        )

        self.course_repository = (
            CourseRepository(session)
        )

    # ========================================================
    # VALIDATE COLLEGE
    # ========================================================

    async def validate_college(
        self,
        college_id: UUID,
    ):

        college = (
            await self.college_repository.get_by_id(
                college_id
            )
        )

        if college is None:

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="College not found.",
            )

        return college

    # ========================================================
    # VALIDATE COURSES
    # ========================================================

    async def validate_courses(
        self,
        course_ids: list[UUID],
    ) -> list:

        # Remove duplicate IDs
        unique_ids = list(
            dict.fromkeys(course_ids)
        )

        if not unique_ids:

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "At least one course "
                    "must be selected."
                ),
            )

        courses = (
            await self.course_repository.get_course_by_ids(
                unique_ids
            )
        )

        found_ids = {
            course.id
            for course in courses
        }

        missing_ids = [
            course_id
            for course_id in unique_ids
            if course_id not in found_ids
        ]

        if missing_ids:

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "One or more selected "
                    "courses were not found."
                ),
            )

        return courses

    # ========================================================
    # CREATE
    # ========================================================

    async def create_package(
        self,
        *,
        college_id: UUID,
        package_name: str,
        description: str | None,
        course_ids: list[UUID],
    ):

        await self.validate_college(
            college_id
        )

        courses = await self.validate_courses(
            course_ids
        )

        existing = (
            await self.repository
            .get_by_college_and_name(
                college_id,
                package_name.strip(),
            )
        )

        if existing:

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "A package with this name "
                    "already exists for this college."
                ),
            )

        package = CollegePackage(
            college_id=college_id,
            package_name=package_name.strip(),
            description=description,
        )

        self.session.add(package)

        await self.session.flush()

        await self.repository.add_courses(
            package.id,
            [
                course.id
                for course in courses
            ],
        )

        await self.session.commit()

        return await self.repository.get_by_id_with_courses(
            package.id
        )

    # ========================================================
    # GET ONE
    # ========================================================

    async def get_package(
        self,
        package_id: UUID,
    ):

        result = (
            await self.repository
            .get_by_id_with_courses(
                package_id
            )
        )

        if result is None:

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="College package not found.",
            )

        return result

    # ========================================================
    # GET ALL
    # ========================================================

    async def get_packages(
        self,
        *,
        college_id: UUID | None = None,
        skip: int = 0,
        limit: int = 100,
    ):

        return await (
            self.repository
            .get_all_with_courses(
                college_id=college_id,
                skip=skip,
                limit=limit,
            )
        )

    # ========================================================
    # UPDATE
    # ========================================================

    async def update_package(
        self,
        package_id: UUID,
        *,
        package_name: str | None = None,
        description: str | None = None,
        course_ids: list[UUID] | None = None,
    ):

        package = (
            await self.repository.get_by_id(
                package_id
            )
        )

        if package is None:

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="College package not found.",
            )

        # ----------------------------------------------------
        # UPDATE NAME
        # ----------------------------------------------------

        if package_name is not None:

            package_name = (
                package_name.strip()
            )

            existing = (
                await self.repository
                .get_by_college_and_name(
                    package.college_id,
                    package_name,
                )
            )

            if (
                existing is not None
                and existing.id != package.id
            ):

                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=(
                        "A package with this name "
                        "already exists for this college."
                    ),
                )

            package.package_name = (
                package_name
            )

        # ----------------------------------------------------
        # UPDATE DESCRIPTION
        # ----------------------------------------------------

        if description is not None:

            package.description = description

        # ----------------------------------------------------
        # UPDATE COURSES
        # ----------------------------------------------------

        if course_ids is not None:

            courses = (
                await self.validate_courses(
                    course_ids
                )
            )

            await self.repository.remove_courses(
                package.id
            )

            await self.repository.add_courses(
                package.id,
                [
                    course.id
                    for course in courses
                ],
            )

        await self.session.commit()

        return await (
            self.repository
            .get_by_id_with_courses(
                package.id
            )
        )

    # ========================================================
    # DELETE
    # ========================================================

    async def delete_package(
        self,
        package_id: UUID,
    ):

        package = (
            await self.repository.get_by_id(
                package_id
            )
        )

        if package is None:

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="College package not found.",
            )

        await self.repository.delete(
            package
        )

        await self.session.commit()