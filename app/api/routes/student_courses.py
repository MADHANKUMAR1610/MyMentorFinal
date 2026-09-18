from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.database.database import get_db
from app.models.user import User
from app.schemas.student_courses import (
    StudentCoursesResponse,
)
from app.services.student_courses_service import (
    StudentCoursesService,
)


router = APIRouter(
    prefix="/students",
    tags=["Student Courses"],
)


@router.get(
    "/courses",
    response_model=StudentCoursesResponse,
)
async def get_student_courses(
    current_user: User = Depends(
        get_current_user
    ),
    session: AsyncSession = Depends(
        get_db
    ),
):

    service = StudentCoursesService(
        session
    )

    return await service.get_student_courses(
        current_user
    )