from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)

from sqlalchemy.ext.asyncio import AsyncSession
from app.api.dependencies import (
    get_current_college_admin,
)
from app.database.database import get_db
from app.models.user import User
from app.schemas.college_admin import (
    CollegeAdminDashboardResponse,
    CollegeAdminStudentsResponse,
    CollegeAdminCoursesResponse,
)
from app.services.college_admin_service import (
    CollegeAdminService,
)
from app.services.auth_service import AuthService
from app.schemas.auth import LoginRequest
from app.models.college import College
from app.repositories.college_repository import CollegeRepository


router = APIRouter(
    prefix="/college-admin",
    tags=["College Admin"],
)
@router.post(
    "/login",
)
async def college_admin_login(
    data: LoginRequest,
    session: AsyncSession = Depends(get_db),
):
    service = AuthService(session)

    # --------------------------------------------------------
    # AUTHENTICATE EMAIL + PASSWORD
    # --------------------------------------------------------

    user = await service.authenticate(
        email=data.email,
        password=data.password,
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    # --------------------------------------------------------
    # CHECK ROLE
    # --------------------------------------------------------

    if user.role != "college_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="College admin access required.",
        )

    # --------------------------------------------------------
    # CHECK COLLEGE LINK
    # --------------------------------------------------------

    if user.college_id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="College admin is not linked to a college.",
        )

    # --------------------------------------------------------
    # GET COLLEGE
    # --------------------------------------------------------

    college_repository = CollegeRepository(
        session
    )

    college = await college_repository.get_by_id(
        user.college_id
    )

    if college is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="College not found.",
        )

    # --------------------------------------------------------
    # CREATE JWT
    # --------------------------------------------------------

    access_token = service.create_token(
        user
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id,
        "role": user.role,
        "college_id": college.id,
        "college_name": college.name,
        "college_code": college.code,
    }
@router.get(
    "/dashboard",
    response_model=CollegeAdminDashboardResponse,
)
async def get_college_admin_dashboard(
    current_user: User = Depends(
        get_current_college_admin
    ),
    session: AsyncSession = Depends(
        get_db
    ),
):

    service = CollegeAdminService(
        session
    )

    try:

        return await service.get_dashboard(
            current_user.college_id
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )


# ============================================================
# STUDENTS
# ============================================================

@router.get(
    "/students",
    response_model=CollegeAdminStudentsResponse,
)
async def get_college_admin_students(
    search: str | None = Query(
        default=None
    ),
    skip: int = Query(
        default=0,
        ge=0,
    ),
    limit: int = Query(
        default=100,
        ge=1,
        le=100,
    ),
    current_user: User = Depends(
        get_current_college_admin
    ),
    session: AsyncSession = Depends(
        get_db
    ),
):

    service = CollegeAdminService(
        session
    )

    return await service.get_students(
        college_id=current_user.college_id,
        search=search,
        skip=skip,
        limit=limit,
    )


# ============================================================
# COURSES
# ============================================================

@router.get(
    "/courses",
    response_model=CollegeAdminCoursesResponse,
)
async def get_college_admin_courses(
    search: str | None = Query(
        default=None
    ),
    skip: int = Query(
        default=0,
        ge=0,
    ),
    limit: int = Query(
        default=100,
        ge=1,
        le=100,
    ),
    current_user: User = Depends(
        get_current_college_admin
    ),
    session: AsyncSession = Depends(
        get_db
    ),
):

    service = CollegeAdminService(
        session
    )

    return await service.get_courses(
        college_id=current_user.college_id,
        search=search,
        skip=skip,
        limit=limit,
    )