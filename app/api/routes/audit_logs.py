from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.database.database import get_db
from app.models.user import User
from app.schemas.audit_log import AuditLogResponse
from app.services.audit_log_service import AuditLogService


router = APIRouter(
    prefix="/audit-logs",
    tags=["Audit Logs"],
)


# ============================================================
# GET ALL AUDIT LOGS
# ============================================================

@router.get(
    "",
    response_model=list[AuditLogResponse],
)
async def get_audit_logs(
    skip: int = Query(
        default=0,
        ge=0,
    ),
    limit: int = Query(
        default=100,
        ge=1,
        le=200,
    ),
    current_user: User = Depends(
        get_current_user
    ),
    session: AsyncSession = Depends(
        get_db
    ),
):

    if current_user.role != "organization_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Only organization admins "
                "can view audit logs."
            ),
        )

    if current_user.company_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not linked to a company.",
        )

    service = AuditLogService(
        session
    )

    return await service.get_by_company_id(
        current_user.company_id,
        skip=skip,
        limit=limit,
    )


# ============================================================
# GET USER AUDIT LOGS
# ============================================================

@router.get(
    "/users",
    response_model=list[AuditLogResponse],
)
async def get_user_audit_logs(
    skip: int = Query(
        default=0,
        ge=0,
    ),
    limit: int = Query(
        default=100,
        ge=1,
        le=200,
    ),
    current_user: User = Depends(
        get_current_user
    ),
    session: AsyncSession = Depends(
        get_db
    ),
):

    if current_user.role != "organization_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Only organization admins "
                "can view user audit logs."
            ),
        )

    if current_user.company_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not linked to a company.",
        )

    service = AuditLogService(
        session
    )

    return await service.get_user_audit_logs(
        current_user.company_id,
        skip=skip,
        limit=limit,
    )


# ============================================================
# GET SINGLE AUDIT LOG
# ============================================================

@router.get(
    "/{audit_log_id}",
    response_model=AuditLogResponse,
)
async def get_audit_log(
    audit_log_id: UUID,
    current_user: User = Depends(
        get_current_user
    ),
    session: AsyncSession = Depends(
        get_db
    ),
):

    if current_user.role != "organization_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Only organization admins "
                "can view audit logs."
            ),
        )

    if current_user.company_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not linked to a company.",
        )

    service = AuditLogService(
        session
    )

    audit_log = await service.get_by_id(
        audit_log_id
    )

    if audit_log is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audit log not found.",
        )

    if (
        audit_log.company_id
        != current_user.company_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied.",
        )

    return audit_log