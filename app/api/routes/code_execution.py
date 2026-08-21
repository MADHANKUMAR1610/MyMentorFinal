from uuid import UUID

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
from app.schemas.code_execution import (
    CodeExecutionRequest,
    CodeExecutionResponse,
)
from app.services.code_execution_service import (
    CodeExecutionService,
)


router = APIRouter(
    prefix="/code",
    tags=["Code Execution"],
)


# ============================================================
# RUN CODE
# ============================================================

@router.post(
    "/run",
    response_model=CodeExecutionResponse,
)
async def run_code(
    data: CodeExecutionRequest,
    current_user: User = Depends(
        get_current_user
    ),
    session: AsyncSession = Depends(
        get_db
    ),
):

    service = CodeExecutionService(
        session
    )

    return await service.run_code(
        user=current_user,
        checkpoint_id=data.checkpoint_id,
        language=data.language,
        code=data.code,
    )


# ============================================================
# SUBMIT CODE
# ============================================================

@router.post(
    "/submit",
    response_model=CodeExecutionResponse,
)
async def submit_code(
    data: CodeExecutionRequest,
    current_user: User = Depends(
        get_current_user
    ),
    session: AsyncSession = Depends(
        get_db
    ),
):

    service = CodeExecutionService(
        session
    )

    return await service.submit_code(
        user=current_user,
        checkpoint_id=data.checkpoint_id,
        language=data.language,
        code=data.code,
    )