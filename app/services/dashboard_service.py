from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.dashboard_repository import (
    DashboardRepository,
)
from app.schemas.dashboard import (
    AdminSkillHubDashboardResponse,
    CourseDashboardItem,
)
from app.schemas.dashboard import (
    StudentCourseDashboardItem,
    StudentSkillHubDashboardResponse,
)

class DashboardService:

    def __init__(self, session: AsyncSession):
        self.repository = DashboardRepository(session)

    async def get_admin_skillhub_dashboard(
        self,
    ) -> AdminSkillHubDashboardResponse:

        total_courses = (
            await self.repository.get_total_courses()
        )

        published_courses = (
            await self.repository.get_published_courses()
        )

        draft_courses = (
            await self.repository.get_draft_courses()
        )

        total_levels = (
            await self.repository.get_total_levels()
        )

        total_checkpoints = (
            await self.repository.get_total_checkpoints()
        )

        total_students = (
            await self.repository.get_total_students()
        )

        completed_levels = (
            await self.repository.get_completed_levels()
        )

        course_rows = (
            await self.repository.get_course_statistics()
        )

        courses = [
            CourseDashboardItem(
                course_id=str(row.id),
                title=row.title,
                status=row.status,
                total_levels=row.total_levels,
                total_checkpoints=row.total_checkpoints,
            )
            for row in course_rows
        ]

        return AdminSkillHubDashboardResponse(
            total_courses=total_courses,
            published_courses=published_courses,
            draft_courses=draft_courses,
            total_levels=total_levels,
            total_checkpoints=total_checkpoints,
            total_students=total_students,
            completed_levels=completed_levels,
            courses=courses,
        )
    async def get_student_skillhub_dashboard(
        self,
        user_id,
    ) -> StudentSkillHubDashboardResponse:

        course_rows = (
            await self.repository.get_student_course_statistics(
                user_id
            )
        )

        completed_levels = (
            await self.repository.get_student_completed_levels(
                user_id
            )
        )

        courses = []

        completed_courses = 0

        for row in course_rows:

            total_levels = row.total_levels or 0
            completed = row.completed_levels or 0

            if total_levels > 0:
                percentage = (
                    completed / total_levels
                ) * 100
            else:
                percentage = 0

            if (
                total_levels > 0
                and completed == total_levels
            ):
                completed_courses += 1

            courses.append(
                StudentCourseDashboardItem(
                    course_id=str(row.id),
                    title=row.title,
                    total_levels=total_levels,
                    completed_levels=completed,
                    progress_percentage=round(
                        percentage,
                        2,
                    ),
                )
            )

        total_courses = len(courses)

        in_progress_courses = (
            total_courses - completed_courses
        )

        return StudentSkillHubDashboardResponse(
            total_courses=total_courses,
            completed_courses=completed_courses,
            in_progress_courses=in_progress_courses,
            total_levels_completed=completed_levels,
            total_xp=0,
            courses=courses,
        )