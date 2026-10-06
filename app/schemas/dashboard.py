from pydantic import BaseModel


# ============================================================
# ADMIN DASHBOARD
# ============================================================


class RecentlyActiveStudent(BaseModel):
    name: str
    email: str | None = None
    xp: int
    streak: int
    levels: int


class AdminDashboardResponse(BaseModel):
    total_students: int
    active_students: int

    total_courses: int
    total_levels: int
    total_videos: int
    total_coding_challenges: int

    completed_levels: int
    learning_hours: float

    daily_active: int
    monthly_active: int

    recently_active_students: list[RecentlyActiveStudent]


# ============================================================
# COLLEGE PACKAGE
# ============================================================


class StudentCollegePackage(BaseModel):
    id: str
    package_name: str
    description: str | None = None


# ============================================================
# STUDENT DASHBOARD
# ============================================================


class StudentCourseDashboardItem(BaseModel):
    course_id: str
    title: str
    difficulty: str
    stage: str | None = None

    total_levels: int
    completed_levels: int
    progress_percentage: float


class StudentDashboardResponse(BaseModel):
    name: str

    xp: int
    streak: int

    # COLLEGE PACKAGE
    college_packages: list[StudentCollegePackage]

    # ALL COURSES ENROLLED BY THE STUDENT
    continue_courses: list[StudentCourseDashboardItem]

    achievements: list[str]
    recently_completed: list[str]
    certificates: list[str]