from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.database.database import get_db
from app.models.master_data import MasterData
from app.models.user import User
from app.schemas.master_data import (
    MasterDataCreate,
    MasterDataResponse,
    MasterDataUpdate,
)
from app.services.master_data_service import MasterDataService


router = APIRouter(
    prefix="/master-data",
    tags=["Master Data"],
)


# ============================================================
# GET BY TYPE
# ============================================================

@router.get(
    "/",
    response_model=list[MasterDataResponse],
)
async def get_master_data_by_type(
    type: str = Query(
        ...,
        min_length=1,
        max_length=50,
    ),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """
    Get active master data by type.
    """

    service = MasterDataService(session)

    return await service.get_by_type(
        type,
        skip=skip,
        limit=limit,
    )


# ============================================================
# GET BY YEAR
# ============================================================

@router.get(
    "/year/{year}",
    response_model=list[MasterDataResponse],
)
async def get_master_data_by_year(
    year: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """
    Get all active master data for a specific year.
    """

    service = MasterDataService(session)

    return await service.get_by_year(
        year,
        skip=skip,
        limit=limit,
    )


# ============================================================
# GET BY TYPE AND YEAR
# ============================================================

@router.get(
    "/type/{type}/year/{year}",
    response_model=list[MasterDataResponse],
)
async def get_master_data_by_type_and_year(
    type: str,
    year: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """
    Get active master data for a specific type and year.
    """

    service = MasterDataService(session)

    return await service.get_by_type_and_year(
        type,
        year,
        skip=skip,
        limit=limit,
    )


# ============================================================
# GET BY ID
# ============================================================

@router.get(
    "/{master_data_id}",
    response_model=MasterDataResponse,
)
async def get_master_data(
    master_data_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """
    Get a master data record by UUID.
    """

    service = MasterDataService(session)

    master_data = await service.get_by_id(
        master_data_id
    )

    if master_data is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Master data not found.",
        )

    return master_data


# ============================================================
# CREATE
# ============================================================

@router.post(
    "/",
    response_model=MasterDataResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_master_data(
    data: MasterDataCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """
    Create a new master data record.
    """

    service = MasterDataService(session)

    existing = await service.get_by_name_type_year(
        data.type,
        data.name,
        data.year,
    )

    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Master data already exists "
                "for this type and year."
            ),
        )

    master_data = MasterData(
        type=data.type,
        name=data.name,
        year=data.year,
        is_active=data.is_active,
    )

    return await service.create(master_data)


# ============================================================
# UPDATE
# ============================================================

@router.put(
    "/{master_data_id}",
    response_model=MasterDataResponse,
)
async def update_master_data(
    master_data_id: UUID,
    data: MasterDataUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """
    Update an existing master data record.
    """

    service = MasterDataService(session)

    master_data = await service.get_by_id(
        master_data_id
    )

    if master_data is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Master data not found.",
        )

    if data.name is not None:
        master_data.name = data.name

    if data.year is not None:
        master_data.year = data.year

    if data.is_active is not None:
        master_data.is_active = data.is_active

    return await service.update(master_data)


# ============================================================
# DELETE
# ============================================================

@router.delete(
    "/{master_data_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_master_data(
    master_data_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """
    Delete a master data record.
    """

    service = MasterDataService(session)

    master_data = await service.get_by_id(
        master_data_id
    )

    if master_data is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Master data not found.",
        )

    await service.delete(master_data)

    return None