from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import (
    get_current_system_admin,
)
from app.database.database import get_db
from app.models.college import College
from app.models.user import User
from app.schemas.college import (
    CollegeCreate,
    CollegeResponse,
    CollegeUpdate,
)
from app.services.college_service import (
    CollegeService,
)
from app.core.security import hash_password
from app.repositories.user_repository import UserRepository
from app.utils.password_encryption import encrypt_password
from app.utils.password_encryption import decrypt_password
router = APIRouter(
    prefix="/colleges",
    tags=["Colleges"],
)


# ============================================================
# CREATE COLLEGE
# ============================================================

@router.post(
    "",
    response_model=CollegeResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_college(
    data: CollegeCreate,
    current_user: User = Depends(
        get_current_system_admin
    ),
    session: AsyncSession = Depends(
        get_db
    ),
):
    """
    Create a new college.

    Admin only.
    """

    service = CollegeService(
        session
    )

    # --------------------------------------------------------
    # GENERATE UNIQUE COLLEGE CODE
    # --------------------------------------------------------

    code = await service.generate_unique_code(
        data.name.strip()
    )

    # --------------------------------------------------------
    # CREATE
    # --------------------------------------------------------

    college = College(
        name=data.name.strip(),
        code=code,
        college_type=data.college_type,
        established_year=data.established_year,
        university_affiliation=(
            data.university_affiliation
        ),
        accreditation=data.accreditation,
        email=data.email,
        phone=data.phone.strip(),
        website=data.website,
        principal_dean_name=(
            data.principal_dean_name
        ),
        contact_person=data.contact_person,
        address=data.address.strip(),
        city=data.city.strip(),
        state=data.state.strip(),
        country=data.country.strip(),
        pincode=data.pincode.strip(),
        description=data.description,
        status=data.status,
    )

    try:
        # --------------------------------------------------------
        # CREATE COLLEGE
        # --------------------------------------------------------

        created_college = await service.create(
            college
        )

        # --------------------------------------------------------
        # CHECK ADMIN EMAIL
        # --------------------------------------------------------

        user_repository = UserRepository(
            session
        )

        existing_admin = await user_repository.get_by_email(
            data.admin_email
        )

        if existing_admin is not None:
            await session.rollback()

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A user with this admin email already exists.",
            )

        # --------------------------------------------------------
        # CREATE COLLEGE ADMIN USER
        # --------------------------------------------------------

        college_admin = User(
          name=f"{created_college.name} Admin",
          email=data.admin_email,
          password_hash=hash_password(data.admin_password),

        # Store encrypted copy for admin management
          admin_password_encrypted=encrypt_password(
             data.admin_password
         ),

          role="college_admin",
          college_id=created_college.id,
          is_active=True,
          is_verified=True,
         )

        await user_repository.create(
            college_admin
        )

        # --------------------------------------------------------
        # COMMIT BOTH COLLEGE + ADMIN
        # --------------------------------------------------------

        await session.commit()

    except IntegrityError:
        await session.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="College or admin email already exists.",
        )

    return CollegeResponse.model_validate(
        created_college
    )


# ============================================================
# GET ALL COLLEGES
# ============================================================

@router.get(
    "",
    response_model=list[CollegeResponse],
)
async def get_colleges(
    search: str | None = Query(
        default=None,
    ),
    college_type: str | None = Query(
        default=None,
    ),
    college_status: str | None = Query(
        default=None,
        alias="status",
    ),
    city: str | None = Query(
        default=None,
    ),
    state: str | None = Query(
        default=None,
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
        get_current_system_admin
    ),
    session: AsyncSession = Depends(
        get_db
    ),
):
    """
    Get colleges with optional filters.

    Admin only.
    """

    service = CollegeService(
        session
    )

    colleges = await service.get_colleges(
    search=search,
    college_type=college_type,
    status=college_status,
    city=city,
    state=state,
    skip=skip,
    limit=limit,
)

    # --------------------------------------------------------
    # GET COLLEGE ADMIN EMAILS
    # --------------------------------------------------------

    # --------------------------------------------------------
    # GET COLLEGE ADMIN EMAIL + PASSWORD
    # --------------------------------------------------------

    college_ids = [
        college.id
        for college in colleges
    ]

    admin_result = await session.execute(
        select(
            User.college_id,
            User.email,
            User.admin_password_encrypted,
        )
        .where(
            User.college_id.in_(college_ids),
            User.role == "college_admin",
        )
    )

    admin_map = {
        row.college_id: {
            "email": row.email,
            "password": (
                decrypt_password(row.admin_password_encrypted)
                if row.admin_password_encrypted
                else None
            ),
        }
        for row in admin_result.all()
    }

    # --------------------------------------------------------
    # BUILD RESPONSE
    # --------------------------------------------------------

    responses = []

    for college in colleges:

        response = CollegeResponse.model_validate(
            college
        )

        admin = admin_map.get(college.id)

        if admin:
            response.admin_email = admin["email"]
            response.admin_password = admin["password"]

        responses.append(response)

    return responses


# ============================================================
# GET COLLEGE BY ID
# ============================================================

@router.get(
    "/{college_id}",
    response_model=CollegeResponse,
)
async def get_college(
    college_id: UUID,
    current_user: User = Depends(
        get_current_system_admin
    ),
    session: AsyncSession = Depends(
        get_db
    ),
):
    """
    Get a college by UUID.
    """

    service = CollegeService(
        session
    )

    college = await service.get_by_id(
        college_id
    )

    if college is None:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="College not found.",
        )

    # --------------------------------------------------------
    # GET COLLEGE ADMIN
    # --------------------------------------------------------

    admin_result = await session.execute(
        select(
            User.email,
            User.password_hash,
            User.admin_password_encrypted,
        )
        .where(
            User.college_id == college.id,
            User.role == "college_admin",
        )
    )

    admin = admin_result.first()

    # --------------------------------------------------------
    # BUILD RESPONSE
    # --------------------------------------------------------

    response = CollegeResponse.model_validate(
        college
    )

    if admin:
        response.admin_email = admin.email
        response.admin_password = (
            decrypt_password(admin.admin_password_encrypted)
            if admin.admin_password_encrypted
            else None
        )

    return response


# ============================================================
# UPDATE COLLEGE
# ============================================================

@router.put(
    "/{college_id}",
    response_model=CollegeResponse,
)
async def update_college(
    college_id: UUID,
    data: CollegeUpdate,
    current_user: User = Depends(
        get_current_system_admin
    ),
    session: AsyncSession = Depends(
        get_db
    ),
):
    """
    Update an existing college.

    Admin only.
    """

    service = CollegeService(
        session
    )

    college = await service.get_by_id(
        college_id
    )

    if college is None:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="College not found.",
        )

    

    # --------------------------------------------------------
    # UPDATE BASIC
    # --------------------------------------------------------

    if data.name is not None:
        college.name = data.name.strip()

    if data.college_type is not None:
        college.college_type = (
            data.college_type
        )

    if data.established_year is not None:
        college.established_year = (
            data.established_year
        )

    if data.university_affiliation is not None:
        college.university_affiliation = (
            data.university_affiliation
        )

    if data.accreditation is not None:
        college.accreditation = (
            data.accreditation
        )

    # --------------------------------------------------------
    # CONTACT
    # --------------------------------------------------------

    if data.email is not None:
        college.email = data.email

    if data.phone is not None:
        college.phone = data.phone.strip()

    if data.website is not None:
        college.website = data.website

    if data.principal_dean_name is not None:
        college.principal_dean_name = (
            data.principal_dean_name
        )

    if data.contact_person is not None:
        college.contact_person = (
            data.contact_person
        )

    # --------------------------------------------------------
    # ADDRESS
    # --------------------------------------------------------

    if data.address is not None:
        college.address = data.address.strip()

    if data.city is not None:
        college.city = data.city.strip()

    if data.state is not None:
        college.state = data.state.strip()

    if data.country is not None:
        college.country = data.country.strip()

    if data.pincode is not None:
        college.pincode = data.pincode.strip()

    # --------------------------------------------------------
    # ADDITIONAL
    # --------------------------------------------------------

    if data.description is not None:
        college.description = data.description

    if data.status is not None:
        college.status = data.status

    try:

        updated_college = (
            await service.update(
                college
            )
        )

        await session.commit()

    except IntegrityError:

        await session.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="College update failed.",
        )

    return CollegeResponse.model_validate(
        updated_college
    )


# ============================================================
# DELETE COLLEGE
# ============================================================

@router.delete(
    "/{college_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_college(
    college_id: UUID,
    current_user: User = Depends(
        get_current_system_admin
    ),
    session: AsyncSession = Depends(
        get_db
    ),
):
    """
    Delete a college.

    Admin only.
    """

    service = CollegeService(
        session
    )

    college = await service.get_by_id(
        college_id
    )

    if college is None:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="College not found.",
        )

    await service.delete(
        college
    )

    await session.commit()

    return None