from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from app.api.dependencies import (
    get_current_admin,
    get_current_user,
)

from app.database.database import (
    get_db,
)

from app.models.user import User

from app.schemas.dashboard import (
    AdminDashboardResponse,
    StudentDashboardResponse,
)

from app.services.dashboard_service import (
    DashboardService,
)


router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
)


# ============================================================
# ADMIN DASHBOARD
# ============================================================

@router.get(
    "/admin/skillhub",
    response_model=AdminDashboardResponse,
)
async def get_admin_skillhub_dashboard(
    current_user: User = Depends(
        get_current_admin
    ),
    session: AsyncSession = Depends(
        get_db
    ),
):

    service = DashboardService(
        session
    )

    return await (
        service.get_admin_dashboard()
    )


# ============================================================
# NORMAL STUDENT DASHBOARD
# ============================================================

@router.get(
    "/student/skillhub",
    response_model=StudentDashboardResponse,
    response_model_exclude_none=True,
)
async def get_student_skillhub_dashboard(
    current_user: User = Depends(
        get_current_user
    ),
    session: AsyncSession = Depends(
        get_db
    ),
):

    service = DashboardService(
        session
    )

    try:

        return await (
            service.get_student_dashboard(
                current_user.id
            )
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )


# ============================================================
# ADMIN / COLLEGE ADMIN
# STUDENT DASHBOARD BY STUDENT ID
# ============================================================

@router.get(
    "/student/skillhub/{student_id}",
    response_model=StudentDashboardResponse,
    response_model_exclude_none=True,
)
async def get_student_skillhub_dashboard_by_id(
    student_id: UUID,
    current_user: User = Depends(
        get_current_user
    ),
    session: AsyncSession = Depends(
        get_db
    ),
):

    service = DashboardService(
        session
    )

    # ========================================================
    # NORMAL ADMIN
    # ========================================================
    #
    # Admin can view ANY student.
    #
    # College package is NOT returned.
    #

    if current_user.role == "admin":

        try:

            return await (
                service.get_student_dashboard_by_id(
                    user_id=student_id,

                    include_college_package=False,
                )
            )

        except ValueError as exc:

            raise HTTPException(
                status_code=404,
                detail=str(exc),
            )

    # ========================================================
    # COLLEGE ADMIN
    # ========================================================
    #
    # College admin can only view students
    # from their own college.
    #
    # College package IS returned.
    #

    if current_user.role == "college_admin":

        student = await session.get(
            User,
            student_id,
        )

        if student is None:

            raise HTTPException(
                status_code=404,
                detail="Student not found.",
            )

        if student.role != "student":

            raise HTTPException(
                status_code=404,
                detail="Student not found.",
            )

        if (
            student.college_id
            != current_user.college_id
        ):

            raise HTTPException(
                status_code=403,
                detail=(
                    "You are not authorized "
                    "to view this student."
                ),
            )

        try:

            return await (
                service.get_student_dashboard_by_id(
                    user_id=student_id,

                    include_college_package=True,
                )
            )

        except ValueError as exc:

            raise HTTPException(
                status_code=404,
                detail=str(exc),
            )

    # ========================================================
    # OTHER ROLES
    # ========================================================

    raise HTTPException(
        status_code=403,
        detail=(
            "You are not authorized "
            "to view student dashboards."
        ),
    )