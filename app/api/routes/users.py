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
    session: AsyncSession = Depends(
        get_db
    ),
):

    service = UserService(
        session
    )

    # --------------------------------------------------------
    # GET LEARNING STREAK
    # --------------------------------------------------------
    # Use the same streak calculation used by
    # Dashboard / SkillHub.
    #
    # This ensures:
    #
    # Dashboard  → same streak
    # Profile    → same streak
    # Leaderboard → same streak
    # --------------------------------------------------------

    learning_streak = await (
        service.get_student_streak(
            current_user.id
        )
    )

    # --------------------------------------------------------
    # CREATE PROFILE RESPONSE
    # --------------------------------------------------------

    response = UserResponse.model_validate(
        current_user
    )

    # --------------------------------------------------------
    # OVERRIDE LOGIN STREAK
    # WITH LEARNING STREAK
    # --------------------------------------------------------

    response.streak = learning_streak

    return response


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

    # --------------------------------------------------------
    # GET LEARNING STREAK
    # --------------------------------------------------------

    learning_streak = await (
        service.get_student_streak(
            updated_user.id
        )
    )

    # --------------------------------------------------------
    # CREATE RESPONSE
    # --------------------------------------------------------

    response = UserResponse.model_validate(
        updated_user
    )

    response.streak = learning_streak

    return response


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
        college_id,
        college_name,
        college_code,
        completed_levels,
        enrolled_courses,
    ) in rows:

        # ----------------------------------------------------
        # GET LEARNING STREAK
        # ----------------------------------------------------

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

                # ---------------------------------------------
                # STUDENT CODE
                # ---------------------------------------------

                "student_code": (
                    student.student_code
                ),

                # ---------------------------------------------
                # COLLEGE
                # ---------------------------------------------

                "college_id": college_id,

                "college_name": college_name,

                "college_code": college_code,
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

    # --------------------------------------------------------
    # GET LEARNING STREAK
    # --------------------------------------------------------

    learning_streak = await (
        service.get_student_streak(
            user.id
        )
    )

    # --------------------------------------------------------
    # CREATE RESPONSE
    # --------------------------------------------------------

    response = UserResponse.model_validate(
        user
    )

    response.streak = learning_streak

    return response