from uuid import UUID

from pydantic import BaseModel


class StudentCourseItem(BaseModel):
    course_id: UUID
    course_name: str
    description: str | None = None

    # True if the student already has CourseEnrollment
    enrolled: bool = False

    # True if this course came through the student's college package
    package_course: bool = False

    package_id: UUID | None = None
    package_name: str | None = None


class StudentCoursesResponse(BaseModel):
    college_id: UUID | None = None
    college_name: str | None = None
    college_code: str | None = None

    package_courses: list[StudentCourseItem] = []
    enrolled_courses: list[StudentCourseItem] = []

    # Combined list for frontend convenience
    courses: list[StudentCourseItem] = []