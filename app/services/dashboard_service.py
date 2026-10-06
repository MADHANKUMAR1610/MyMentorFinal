from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.dashboard_repository import (
    DashboardRepository,
)

from app.schemas.dashboard import (
    AdminDashboardResponse,
    RecentlyActiveStudent,
    StudentCollegePackage,
    StudentCollegePackageCourse,
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
            await self.repository
            .get_total_coding_challenges()
        )

        completed_levels = (
            await self.repository
            .get_completed_levels()
        )

        learning_hours = (
            await self.repository
            .get_learning_hours()
        )

        daily_active = (
            await self.repository
            .get_daily_active_students()
        )

        monthly_active = (
            await self.repository
            .get_monthly_active_students()
        )

        student_rows = (
            await self.repository
            .get_recently_active_students()
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

            total_coding_challenges=(
                total_coding_challenges
            ),

            completed_levels=completed_levels,

            learning_hours=learning_hours,

            daily_active=daily_active,
            monthly_active=monthly_active,

            recently_active_students=(
                recently_active_students
            ),
        )

    # ========================================================
    # COMMON STUDENT DASHBOARD DATA
    # ========================================================

    async def _get_student_dashboard_data(
        self,
        user_id,
    ):

        user = (
            await self.repository
            .get_student_user(user_id)
        )

        if user is None:
            raise ValueError(
                "Student not found."
            )

        # ----------------------------------------------------
        # STUDENT COURSES
        # ----------------------------------------------------

        course_rows = (
            await self.repository
            .get_student_courses(user_id)
        )

        courses = []

        for row in course_rows:

            total_levels = (
                row.total_levels or 0
            )

            completed_levels = (
                row.completed_levels or 0
            )

            if total_levels > 0:

                percentage = (
                    completed_levels
                    / total_levels
                ) * 100

            else:

                percentage = 0.0

            courses.append(
                StudentCourseDashboardItem(
                    course_id=str(
                        row.id
                    ),

                    title=row.title,

                    difficulty=row.difficulty,

                    stage=row.stage,

                    total_levels=total_levels,

                    completed_levels=(
                        completed_levels
                    ),

                    progress_percentage=round(
                        percentage,
                        2,
                    ),
                )
            )

        # ----------------------------------------------------
        # STREAK
        # ----------------------------------------------------

        streak = (
            await self.repository
            .get_student_streak(user_id)
        )

        # ----------------------------------------------------
        # RECENTLY COMPLETED
        # ----------------------------------------------------

        recently_completed = (
            await self.repository
            .get_student_completed_courses(
                user_id
            )
        )

        return {
            "user": user,
            "courses": courses,
            "streak": streak,
            "recently_completed": (
                recently_completed
            ),
        }

    # ========================================================
    # NORMAL STUDENT DASHBOARD
    #
    # No college package
    # ========================================================

    async def get_student_dashboard(
        self,
        user_id,
    ) -> StudentDashboardResponse:

        data = (
            await self
            ._get_student_dashboard_data(
                user_id
            )
        )

        user = data["user"]

        return StudentDashboardResponse(
            name=user.name,

            xp=user.xp or 0,

            streak=data["streak"],

            continue_courses=data[
                "courses"
            ],

            achievements=[],

            recently_completed=data[
                "recently_completed"
            ],

            certificates=[],

            college_packages=None,
        )

    # ========================================================
    # STUDENT DASHBOARD BY ID
    #
    # Normal Admin:
    #     include_college_package=False
    #
    # College Admin:
    #     include_college_package=True
    # ========================================================

    async def get_student_dashboard_by_id(
        self,
        user_id,
        include_college_package: bool = False,
    ) -> StudentDashboardResponse:

        # ----------------------------------------------------
        # COMMON STUDENT DASHBOARD
        # ----------------------------------------------------

        data = (
            await self
            ._get_student_dashboard_data(
                user_id
            )
        )

        user = data["user"]

        # ----------------------------------------------------
        # DEFAULT
        # ----------------------------------------------------

        college_packages = None

        # ----------------------------------------------------
        # COLLEGE ADMIN ONLY
        # ----------------------------------------------------

        if include_college_package:

            rows = (
                await self.repository
                .get_student_college_packages(
                    user_id
                )
            )

            package_map = {}

            # ------------------------------------------------
            # PACKAGE + COURSES
            # ------------------------------------------------

            for row in rows:

                package_id = str(
                    row["package_id"]
                )

                # --------------------------------------------
                # CREATE PACKAGE
                # --------------------------------------------

                if package_id not in package_map:

                    package_map[
                        package_id
                    ] = {
                        "id": package_id,

                        "package_name": (
                            row["package_name"]
                        ),

                        "description": (
                            row[
                                "package_description"
                            ]
                        ),

                        "course_count": 0,

                        "courses": [],
                    }

                # --------------------------------------------
                # ADD COURSE
                # --------------------------------------------

                package_map[
                    package_id
                ][
                    "courses"
                ].append(
                    StudentCollegePackageCourse(
                        id=str(
                            row["course_id"]
                        ),

                        title=(
                            row["course_title"]
                        ),

                        description=(
                            row[
                                "course_description"
                            ]
                        ),

                        language=(
                            row["course_language"]
                        ),

                        difficulty=(
                            row[
                                "course_difficulty"
                            ]
                        ),

                        duration=(
                            row[
                                "course_duration"
                            ]
                        ),

                        thumbnail=(
                            row[
                                "course_thumbnail"
                            ]
                        ),

                        status=(
                            row["course_status"]
                        ),
                    )
                )

                # --------------------------------------------
                # INCREMENT COURSE COUNT
                # --------------------------------------------

                package_map[
                    package_id
                ][
                    "course_count"
                ] += 1

            # ------------------------------------------------
            # CONVERT PACKAGE MAP TO SCHEMA
            # ------------------------------------------------

            college_packages = [
                StudentCollegePackage(
                    **package_data
                )
                for package_data
                in package_map.values()
            ]

        # ----------------------------------------------------
        # FINAL RESPONSE
        # ----------------------------------------------------

        return StudentDashboardResponse(
            name=user.name,

            xp=user.xp or 0,

            streak=data["streak"],

            continue_courses=data[
                "courses"
            ],

            achievements=[],

            recently_completed=data[
                "recently_completed"
            ],

            certificates=[],

            college_packages=(
                college_packages
            ),
        )