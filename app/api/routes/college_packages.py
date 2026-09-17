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
    get_current_user,
)
from app.database.database import get_db
from app.models.user import User
from app.schemas.college_package import (
    CollegePackageCreate,
    CollegePackageUpdate,
    CollegePackageResponse,
    CollegePackageCourseResponse,
)
from app.services.college_package_service import (
    CollegePackageService,
)


router = APIRouter(
    prefix="/college-packages",
    tags=["College Packages"],
)


# ============================================================
# RESPONSE BUILDER
# ============================================================

def build_response(
    result: dict,
) -> CollegePackageResponse:

    package = result["package"]

    courses = result["courses"]

    return CollegePackageResponse(
        id=package.id,
        college_id=package.college_id,
        college_name=result["college_name"],
        package_name=package.package_name,
        description=package.description,
        course_ids=[
            course.id
            for course in courses
        ],
        courses=[
            CollegePackageCourseResponse.model_validate(
                course
            )
            for course in courses
        ],
        created_at=package.created_at,
        updated_at=package.updated_at,
    )


# ============================================================
# CREATE COLLEGE PACKAGE
# ============================================================

@router.post(
    "",
    response_model=CollegePackageResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_college_package(
    data: CollegePackageCreate,
    current_user: User = Depends(
        get_current_user
    ),
    session: AsyncSession = Depends(
        get_db
    ),
):

    service = CollegePackageService(
        session
    )

    result = await service.create_package(
        college_id=data.college_id,
        package_name=data.package_name,
        description=data.description,
        course_ids=data.course_ids,
    )

    return build_response(result)


# ============================================================
# GET ALL PACKAGES
# ============================================================

@router.get(
    "",
    response_model=list[CollegePackageResponse],
)
async def get_college_packages(
    college_id: UUID | None = Query(
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
        get_current_user
    ),
    session: AsyncSession = Depends(
        get_db
    ),
):

    service = CollegePackageService(
        session
    )

    results = await service.get_packages(
        college_id=college_id,
        skip=skip,
        limit=limit,
    )

    return [
        build_response(result)
        for result in results
    ]


# ============================================================
# GET PACKAGE BY ID
# ============================================================

@router.get(
    "/{package_id}",
    response_model=CollegePackageResponse,
)
async def get_college_package(
    package_id: UUID,
    current_user: User = Depends(
        get_current_user
    ),
    session: AsyncSession = Depends(
        get_db
    ),
):

    service = CollegePackageService(
        session
    )

    result = await service.get_package(
        package_id
    )

    return build_response(result)


# ============================================================
# UPDATE PACKAGE
# ============================================================

@router.put(
    "/{package_id}",
    response_model=CollegePackageResponse,
)
async def update_college_package(
    package_id: UUID,
    data: CollegePackageUpdate,
    current_user: User = Depends(
        get_current_user
    ),
    session: AsyncSession = Depends(
        get_db
    ),
):

    service = CollegePackageService(
        session
    )

    result = await service.update_package(
        package_id,
        package_name=data.package_name,
        description=data.description,
        course_ids=data.course_ids,
    )

    return build_response(result)


# ============================================================
# DELETE PACKAGE
# ============================================================

@router.delete(
    "/{package_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_college_package(
    package_id: UUID,
    current_user: User = Depends(
        get_current_user
    ),
    session: AsyncSession = Depends(
        get_db
    ),
):

    service = CollegePackageService(
        session
    )

    await service.delete_package(
        package_id
    )

    return None