from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)

from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from app.api.dependencies import (
    get_current_user,
)

from app.database.database import (
    get_db,
)

from app.models.user import User

from app.schemas.user import (
    UserResponse,
    UserUpdate,
)

from app.services.user_service import (
    UserService,
)


router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


# ============================================================
# GET MY PROFILE
# ============================================================

@router.get(
    "/me",
    response_model=UserResponse,
)
async def get_my_profile(
    current_user: User = Depends(
        get_current_user
    ),
):

    return UserResponse.model_validate(
        current_user
    )


# ============================================================
# UPDATE MY PROFILE
# ============================================================

@router.put(
    "/me",
    response_model=UserResponse,
)
async def update_my_profile(
    data: UserUpdate,
    current_user: User = Depends(
        get_current_user
    ),
    session: AsyncSession = Depends(
        get_db
    ),
):

    service = UserService(
        session
    )

    changed_fields = {}

    # --------------------------------------------------------
    # NAME
    # --------------------------------------------------------

    if (
        data.name is not None
        and data.name != current_user.name
    ):

        changed_fields["name"] = {
            "from": current_user.name,
            "to": data.name,
        }

        current_user.name = data.name

    # --------------------------------------------------------
    # PHONE
    # --------------------------------------------------------

    if (
        data.phone is not None
        and data.phone != current_user.phone
    ):

        existing_phone = await (
            service.get_by_phone(
                data.phone
            )
        )

        if (
            existing_phone is not None
            and existing_phone.id
            != current_user.id
        ):

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "A user with this phone "
                    "number already exists."
                ),
            )

        changed_fields["phone"] = {
            "from": current_user.phone,
            "to": data.phone,
        }

        current_user.phone = data.phone

    # --------------------------------------------------------
    # UPDATE
    # --------------------------------------------------------

    updated_user = await service.update_user(
        current_user,
        changed_fields=changed_fields,
        performed_by_user_id=current_user.id,
        performed_by_name=current_user.name,
    )

    return UserResponse.model_validate(
        updated_user
    )


# ============================================================
# GET ALL STUDENTS
# ============================================================

@router.get(
    "/students",
)
async def get_all_students(
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
        get_current_user
    ),
    session: AsyncSession = Depends(
        get_db
    ),
):

    service = UserService(
        session
    )

    rows = await (
        service.get_students_with_progress(
            skip=skip,
            limit=limit,
        )
    )

    students = []

    for (
        student,
        completed_levels,
        enrolled_courses,
    ) in rows:

        streak = await (
            service.get_student_streak(
                student.id
            )
        )

        students.append(
            {
                "id": student.id,
                "name": student.name,
                "email": student.email,
                "xp": student.xp or 0,
                "streak": streak,
                "levels": (
                    completed_levels
                    or 0
                ),
                "courses": (
                    enrolled_courses
                    or 0
                ),
            }
        )

    return students


# ============================================================
# GET USER BY ID
# ============================================================

@router.get(
    "/{user_id}",
    response_model=UserResponse,
)
async def get_user_by_id(
    user_id: UUID,
    current_user: User = Depends(
        get_current_user
    ),
    session: AsyncSession = Depends(
        get_db
    ),
):

    service = UserService(
        session
    )

    user = await service.get_by_id(
        user_id
    )

    if user is None:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )

    return UserResponse.model_validate(
        user
    )