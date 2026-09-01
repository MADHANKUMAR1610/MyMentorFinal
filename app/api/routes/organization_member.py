from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    Query,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.database.database import get_db

from app.schemas.organization_member import (
    OrganizationMemberCreate,
    OrganizationMemberResponse,
    OrganizationMemberUpdate,
    OrganizationMemberStatusUpdate,
    OrganizationMemberPasswordReset,
)

from app.services.organization_member_service import (
    OrganizationMemberService,
)


router = APIRouter(
    prefix="/organizations/me/members",
    tags=["Organization Members"],
)


# ============================================================
# GET ALL ORGANIZATION MEMBERS
# ============================================================

@router.get(
    "",
    response_model=list[OrganizationMemberResponse],
)
async def get_my_members(
    skip: int = Query(
        default=0,
        ge=0,
    ),
    limit: int = Query(
        default=100,
        ge=1,
        le=100,
    ),
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get all members belonging to the current user's organization.
    """

    service = OrganizationMemberService(db)

    members = await service.get_my_members(
        current_user.id,
        skip=skip,
        limit=limit,
    )

    return [
        OrganizationMemberResponse.model_validate(member)
        for member in members
    ]


# ============================================================
# GET SINGLE ORGANIZATION MEMBER
# ============================================================

@router.get(
    "/{member_id}",
    response_model=OrganizationMemberResponse,
)
async def get_my_member(
    member_id: UUID,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get a specific member belonging to the current user's organization.
    """

    service = OrganizationMemberService(db)

    member = await service.get_member(
        current_user.id,
        member_id,
    )

    return OrganizationMemberResponse.model_validate(
        member
    )


# ============================================================
# ADD EXISTING USER TO ORGANIZATION
# ============================================================
# ============================================================
# REGISTER ORGANIZATION MEMBER
# ============================================================
@router.post(
    "",
    response_model=OrganizationMemberResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_organization_member(
    data: OrganizationMemberCreate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new organization member.
    """

    service = OrganizationMemberService(db)

    member = await service.create_member(
        user_id=current_user.id,
        name=data.name,
        email=data.email,
        phone=data.phone,
        department=data.department,
        designation=data.designation,
        role=data.role,
        password=data.password,
    )

    return OrganizationMemberResponse.model_validate(
        member
    )
# ============================================================
# UPDATE ORGANIZATION MEMBER
# ============================================================

@router.put(
    "/{member_id}",
    response_model=OrganizationMemberResponse,
)
async def update_organization_member(
    member_id: UUID,
    data: OrganizationMemberUpdate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update organization member information.
    """

    service = OrganizationMemberService(db)

    update_data = data.model_dump(
        exclude_unset=True
    )

    member = await service.update_member(
        current_user.id,
        member_id,
        update_data,
    )

    return OrganizationMemberResponse.model_validate(
        member
    )


# ============================================================
# REMOVE ORGANIZATION MEMBER
# ============================================================

@router.delete(
    "/{member_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def remove_organization_member(
    member_id: UUID,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Remove a member from the current user's organization.
    """

    service = OrganizationMemberService(db)

    await service.remove_member(
        current_user.id,
        member_id,
    )

    return None


# ============================================================
# UPDATE MEMBER ACTIVE STATUS
# ============================================================

@router.put(
    "/{member_id}/status",
    response_model=OrganizationMemberResponse,
)
async def update_member_status(
    member_id: UUID,
    data: OrganizationMemberStatusUpdate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Activate or deactivate an organization member.
    """

    service = OrganizationMemberService(db)

    member = await service.update_member_status(
        current_user.id,
        member_id,
        data.is_active,
    )

    return OrganizationMemberResponse.model_validate(
        member
    )
# ============================================================
# RESET MEMBER PASSWORD
# ============================================================

@router.put(
    "/{member_id}/password",
    response_model=OrganizationMemberResponse,
)
async def reset_organization_member_password(
    member_id: UUID,
    data: OrganizationMemberPasswordReset,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Reset password for an organization member.
    """

    service = OrganizationMemberService(db)

    member = await service.reset_member_password(
        user_id=current_user.id,
        member_id=member_id,
        new_password=data.password,
    )

    return OrganizationMemberResponse.model_validate(
        member
    )