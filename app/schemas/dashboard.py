from pydantic import BaseModel


class CourseDashboardItem(BaseModel):
    course_id: str
    title: str
    status: str
    total_levels: int
    total_checkpoints: int


class AdminSkillHubDashboardResponse(BaseModel):
    total_courses: int
    published_courses: int
    draft_courses: int
    total_levels: int
    total_checkpoints: int
    total_students: int
    completed_levels: int
    courses: list[CourseDashboardItem]
class StudentCourseDashboardItem(BaseModel):
    course_id: str
    title: str
    total_levels: int
    completed_levels: int
    progress_percentage: float


class StudentSkillHubDashboardResponse(BaseModel):
    total_courses: int
    completed_courses: int
    in_progress_courses: int
    total_levels_completed: int
    total_xp: int
    courses: list[StudentCourseDashboardItem]