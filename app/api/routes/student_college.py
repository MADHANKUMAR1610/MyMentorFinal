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
    StudentCodeRequest,
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
    "/student-code",
    response_model=StudentCollegeResponse,
)
async def link_college_by_student_code(
    data: StudentCodeRequest,
    current_user: User = Depends(
        get_current_user
    ),
    session: AsyncSession = Depends(
        get_db
    ),
):

    service = StudentCollegeService(session)

    college = await service.link_college_by_student_code(
        current_user=current_user,
        student_code=data.student_code,
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