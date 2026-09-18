from fastapi import (
    APIRouter,
    Depends,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import (
    get_current_user,
)
from app.database.database import get_db
from app.models.user import User
from app.schemas.student_college import (
    StudentCollegeCodeRequest,
    StudentCollegeResponse,
)
from app.services.student_college_service import (
    StudentCollegeService,
)


router = APIRouter(
    prefix="/students",
    tags=["Student College"],
)


# ============================================================
# LINK STUDENT TO COLLEGE
# ============================================================

@router.post(
    "/college-code",
    response_model=StudentCollegeResponse,
)
async def link_student_college(
    data: StudentCollegeCodeRequest,
    current_user: User = Depends(
        get_current_user
    ),
    session: AsyncSession = Depends(
        get_db
    ),
):

    service = StudentCollegeService(
        session
    )

    college = await service.link_college(
        user=current_user,
        college_code=data.college_code,
    )

    return StudentCollegeResponse(
        id=college.id,
        name=college.name,
        code=college.code,
        college_type=college.college_type,
        city=college.city,
        state=college.state,
        country=college.country,
        status=college.status,
    )