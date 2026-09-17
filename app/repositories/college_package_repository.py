from typing import Optional
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.college_package import CollegePackage
from app.models.college_package_course import (
    CollegePackageCourse,
)
from app.models.college import College
from app.models.course import Course
from app.repositories.base import BaseRepository


class CollegePackageRepository(
    BaseRepository[CollegePackage]
):

    def __init__(
        self,
        session: AsyncSession,
    ):
        super().__init__(
            CollegePackage,
            session,
        )

    # ========================================================
    # GET PACKAGE WITH COURSES
    # ========================================================

    async def get_by_id_with_courses(
        self,
        package_id: UUID,
    ) -> Optional[dict]:

        package_result = await self.session.execute(
            select(
                CollegePackage,
                College.name.label(
                    "college_name"
                ),
            )
            .join(
                College,
                College.id
                == CollegePackage.college_id,
            )
            .where(
                CollegePackage.id == package_id
            )
        )

        row = package_result.first()

        if row is None:
            return None

        package = row[0]
        college_name = row[1]

        course_result = await self.session.execute(
            select(Course)
            .join(
                CollegePackageCourse,
                CollegePackageCourse.course_id
                == Course.id,
            )
            .where(
                CollegePackageCourse.package_id
                == package_id
            )
            .order_by(
                Course.created_at.asc()
            )
        )

        courses = list(
            course_result.scalars().all()
        )

        return {
            "package": package,
            "college_name": college_name,
            "courses": courses,
        }

    # ========================================================
    # GET ALL PACKAGES
    # ========================================================

    async def get_all_with_courses(
        self,
        *,
        college_id: UUID | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[dict]:

        query = (
            select(
                CollegePackage,
                College.name.label(
                    "college_name"
                ),
            )
            .join(
                College,
                College.id
                == CollegePackage.college_id,
            )
        )

        if college_id is not None:
            query = query.where(
                CollegePackage.college_id
                == college_id
            )

        query = (
            query
            .order_by(
                CollegePackage.created_at.desc()
            )
            .offset(skip)
            .limit(limit)
        )

        result = await self.session.execute(
            query
        )

        rows = result.all()

        response = []

        for row in rows:

            package = row[0]
            college_name = row[1]

            course_result = (
                await self.session.execute(
                    select(Course)
                    .join(
                        CollegePackageCourse,
                        CollegePackageCourse.course_id
                        == Course.id,
                    )
                    .where(
                        CollegePackageCourse.package_id
                        == package.id
                    )
                    .order_by(
                        Course.created_at.asc()
                    )
                )
            )

            courses = list(
                course_result.scalars().all()
            )

            response.append(
                {
                    "package": package,
                    "college_name": college_name,
                    "courses": courses,
                }
            )

        return response

    # ========================================================
    # FIND PACKAGE BY COLLEGE + NAME
    # ========================================================

    async def get_by_college_and_name(
        self,
        college_id: UUID,
        package_name: str,
    ) -> Optional[CollegePackage]:

        result = await self.session.execute(
            select(CollegePackage).where(
                CollegePackage.college_id
                == college_id,
                CollegePackage.package_name
                == package_name,
            )
        )

        return result.scalar_one_or_none()

    # ========================================================
    # ADD COURSES
    # ========================================================

    async def add_courses(
        self,
        package_id: UUID,
        course_ids: list[UUID],
    ) -> None:

        for course_id in course_ids:

            self.session.add(
                CollegePackageCourse(
                    package_id=package_id,
                    course_id=course_id,
                )
            )

    # ========================================================
    # REMOVE ALL COURSES
    # ========================================================

    async def remove_courses(
        self,
        package_id: UUID,
    ) -> None:

        await self.session.execute(
            delete(
                CollegePackageCourse
            ).where(
                CollegePackageCourse.package_id
                == package_id
            )
        )