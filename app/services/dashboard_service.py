from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.dashboard_repository import (
    DashboardRepository,
)

from app.schemas.dashboard import (
    AdminDashboardResponse,
    RecentlyActiveStudent,
    StudentCourseDashboardItem,
    StudentDashboardResponse,
)


class DashboardService:

    def __init__(
        self,
        session: AsyncSession,
    ):
        self.repository = DashboardRepository(
            session
        )

    # ========================================================
    # ADMIN DASHBOARD
    # ========================================================

    async def get_admin_dashboard(
        self,
    ) -> AdminDashboardResponse:

        total_students = (
            await self.repository.get_total_students()
        )

        active_students = (
            await self.repository.get_active_students()
        )

        total_courses = (
            await self.repository.get_total_courses()
        )

        total_levels = (
            await self.repository.get_total_levels()
        )

        total_videos = (
            await self.repository.get_total_videos()
        )

        total_coding_challenges = (
            await self.repository.get_total_coding_challenges()
        )

        completed_levels = (
            await self.repository.get_completed_levels()
        )

        learning_hours = (
            await self.repository.get_learning_hours()
        )

        daily_active = (
            await self.repository.get_daily_active_students()
        )

        monthly_active = (
            await self.repository.get_monthly_active_students()
        )

        student_rows = (
            await self.repository.get_recently_active_students()
        )

        recently_active_students = [
    RecentlyActiveStudent(
        name=row["name"],
        email=row["email"],
        xp=row["xp"],
        streak=row["streak"],
        levels=row["levels"],
    )
    for row in student_rows
]

        return AdminDashboardResponse(
            total_students=total_students,
            active_students=active_students,

            total_courses=total_courses,
            total_levels=total_levels,
            total_videos=total_videos,
            total_coding_challenges=total_coding_challenges,

            completed_levels=completed_levels,
            learning_hours=learning_hours,

            daily_active=daily_active,
            monthly_active=monthly_active,

            recently_active_students=(
                recently_active_students
            ),
        )

        # ========================================================
    # STUDENT DASHBOARD
    # ========================================================

    async def get_student_dashboard(
        self,
        user_id,
    ) -> StudentDashboardResponse:

        user = (
            await self.repository.get_student_user(
                user_id
            )
        )

        if user is None:
            raise ValueError(
                "Student not found."
            )

        # ----------------------------------------------------
        # Get ALL courses enrolled by this student
        # ----------------------------------------------------

        course_rows = (
            await self.repository.get_student_courses(
                user_id
            )
        )

        courses = []

        for row in course_rows:

            total_levels = (
                row.total_levels or 0
            )

            completed_levels = (
                row.completed_levels or 0
            )

            # ------------------------------------------------
            # Real-time progress percentage
            # ------------------------------------------------

            if total_levels > 0:
                percentage = (
                    completed_levels
                    / total_levels
                ) * 100
            else:
                percentage = 0.0

            courses.append(
                StudentCourseDashboardItem(
                    course_id=str(row.id),
                    title=row.title,
                    difficulty=row.difficulty,
                    stage=row.stage,

                    total_levels=total_levels,

                    completed_levels=completed_levels,

                    progress_percentage=round(
                        percentage,
                        2,
                    ),
                )
            )

        # ----------------------------------------------------
        # Calculate REAL-TIME student streak
        # from Progress.updated_at
        # ----------------------------------------------------

        streak = (
            await self.repository.get_student_streak(
                user_id
            )
        )

        # ----------------------------------------------------
        # Completed courses
        # ----------------------------------------------------

        recently_completed = (
            await self.repository
            .get_student_completed_courses(
                user_id
            )
        )

        # ----------------------------------------------------
        # Student dashboard response
        # ----------------------------------------------------

        return StudentDashboardResponse(
            name=user.name,

            xp=user.xp or 0,

            # IMPORTANT:
            # Do NOT use user.streak here.
            # This is calculated from Progress.
            streak=streak,

            # ALL ENROLLED COURSES
            continue_courses=courses,

            achievements=[],

            recently_completed=recently_completed,

            certificates=[],
        )