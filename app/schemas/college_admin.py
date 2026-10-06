from uuid import UUID
from pydantic import BaseModel


# ============================================================
# DASHBOARD
# ============================================================

class CollegeAdminStudentSummary(BaseModel):
    id: UUID
    name: str
    email: str | None = None
    student_code: str | None = None
    xp: int
    streak: int
    levels: int


class CollegeAdminCourseSummary(BaseModel):
    course_id: UUID
    title: str
    students: int
    levels: int
    progress_percentage: float


class CollegeAdminDashboardResponse(BaseModel):
    college_id: UUID
    college_name: str
    college_code: str

    total_students: int
    active_students: int
    assigned_courses: int
    average_progress: float

    completed_levels: int
    learning_videos: int
    coding_challenges: int
    active_this_week: int

    recently_active_students: list[
        CollegeAdminStudentSummary
    ]

    course_performance: list[
        CollegeAdminCourseSummary
    ]


# ============================================================
# STUDENTS
# ============================================================

class CollegeAdminStudentItem(BaseModel):
    id: UUID
    name: str
    email: str | None = None
    phone: str | None = None
    student_code: str | None = None
    department: str | None = None
    year: str | None = None

    xp: int
    streak: int

    courses: int
    levels: int
    progress_percentage: float


class CollegeAdminStudentsResponse(BaseModel):
    total: int
    students: list[CollegeAdminStudentItem]


# ============================================================
# COURSES
# ============================================================

class CollegeAdminCourseItem(BaseModel):
    course_id: UUID
    title: str
    description: str | None = None
    category: str
    language: str
    difficulty: str
    duration: str | None = None
    thumbnail: str | None = None

    students: int
    levels: int
    progress_percentage: float


class CollegeAdminCoursesResponse(BaseModel):
    total_courses: int
    total_enrollments: int
    total_levels: int
    average_progress: float

    courses: list[CollegeAdminCourseItem]