from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.database.database import get_db
from app.models.checkpoint import Checkpoint
from app.models.level import Level
from app.models.user import User
from app.schemas.checkpoint import (
    CheckpointCreate,
    CheckpointResponse,
    CheckpointUpdate,
)
from app.services.checkpoint_service import CheckpointService


router = APIRouter(
    prefix="/checkpoints",
    tags=["Checkpoints"],
)


# ============================================================
# CREATE CHECKPOINT
# ============================================================

@router.post(
    "",
    response_model=CheckpointResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_checkpoint(
    data: CheckpointCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """
    Create a checkpoint for a level.
    """

    level = await session.get(
        Level,
        data.level_id,
    )

    if level is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Level not found.",
        )

    service = CheckpointService(session)

    existing_checkpoint = (
        await service.get_by_level_and_order(
            data.level_id,
            data.checkpoint_order,
        )
    )

    if existing_checkpoint is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This checkpoint order already exists for this level.",
        )

    checkpoint = Checkpoint(
        level_id=data.level_id,
        checkpoint_order=data.checkpoint_order,
        at_seconds=data.at_seconds,
        title=data.title,
        scenario=data.scenario,
        problem_statement=data.problem_statement,
        objective=data.objective,
        difficulty=data.difficulty,
        marks=data.marks,
        xp=data.xp,
        retry_limit=data.retry_limit,
        language=data.language,
        starter_code=data.starter_code,
        constraints=data.constraints,
        hints=data.hints,
        solution=data.solution,
        explanation=data.explanation,
        visible_test_cases=data.visible_test_cases,
        hidden_test_cases=data.hidden_test_cases,
    )

    created_checkpoint = (
        await service.create_checkpoint(checkpoint)
    )

    return CheckpointResponse.model_validate(
        created_checkpoint
    )


# ============================================================
# GET CHECKPOINTS
# ============================================================

@router.get(
    "",
    response_model=list[CheckpointResponse],
)
async def get_checkpoints(
    level_id: UUID | None = Query(default=None),
    difficulty: str | None = Query(default=None),
    language: str | None = Query(default=None),
    skip: int = Query(
        default=0,
        ge=0,
    ),
    limit: int = Query(
        default=100,
        ge=1,
        le=100,
    ),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """
    Get checkpoints using optional filters.
    """

    service = CheckpointService(session)

    if level_id is not None:
        checkpoints = await service.get_by_level_id(
            level_id,
            skip=skip,
            limit=limit,
        )

    elif difficulty is not None:
        checkpoints = await service.get_by_difficulty(
            difficulty,
            skip=skip,
            limit=limit,
        )

    elif language is not None:
        checkpoints = await service.get_by_language(
            language,
            skip=skip,
            limit=limit,
        )

    else:
        checkpoints = await service.repository.get_all(
            skip=skip,
            limit=limit,
        )

    return [
        CheckpointResponse.model_validate(checkpoint)
        for checkpoint in checkpoints
    ]


# ============================================================
# GET CHECKPOINT BY LEVEL + ORDER
# ============================================================

@router.get(
    "/level/{level_id}/order/{checkpoint_order}",
    response_model=CheckpointResponse,
)
async def get_checkpoint_by_level_and_order(
    level_id: UUID,
    checkpoint_order: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """
    Get a specific checkpoint within a level.
    """

    service = CheckpointService(session)

    checkpoint = (
        await service.get_by_level_and_order(
            level_id,
            checkpoint_order,
        )
    )

    if checkpoint is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Checkpoint not found.",
        )

    return CheckpointResponse.model_validate(
        checkpoint
    )


# ============================================================
# GET CHECKPOINT BY ID
# ============================================================

@router.get(
    "/{checkpoint_id}",
    response_model=CheckpointResponse,
)
async def get_checkpoint_by_id(
    checkpoint_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """
    Get a checkpoint by UUID.
    """

    service = CheckpointService(session)

    checkpoint = await service.get_by_id(
        checkpoint_id
    )

    if checkpoint is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Checkpoint not found.",
        )

    return CheckpointResponse.model_validate(
        checkpoint
    )


# ============================================================
# UPDATE CHECKPOINT
# ============================================================

@router.put(
    "/{checkpoint_id}",
    response_model=CheckpointResponse,
)
async def update_checkpoint(
    checkpoint_id: UUID,
    data: CheckpointUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """
    Update a checkpoint.
    """

    service = CheckpointService(session)

    checkpoint = await service.get_by_id(
        checkpoint_id
    )

    if checkpoint is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Checkpoint not found.",
        )

    if data.checkpoint_order is not None:

        existing_checkpoint = (
            await service.get_by_level_and_order(
                checkpoint.level_id,
                data.checkpoint_order,
            )
        )

        if (
            existing_checkpoint is not None
            and existing_checkpoint.id != checkpoint.id
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This checkpoint order already exists for this level.",
            )

        checkpoint.checkpoint_order = (
            data.checkpoint_order
        )

    if data.at_seconds is not None:
        checkpoint.at_seconds = data.at_seconds

    if data.title is not None:
        checkpoint.title = data.title

    if data.scenario is not None:
        checkpoint.scenario = data.scenario

    if data.problem_statement is not None:
        checkpoint.problem_statement = (
            data.problem_statement
        )

    if data.objective is not None:
        checkpoint.objective = data.objective

    if data.difficulty is not None:
        checkpoint.difficulty = data.difficulty

    if data.marks is not None:
        checkpoint.marks = data.marks

    if data.xp is not None:
        checkpoint.xp = data.xp

    if data.retry_limit is not None:
        checkpoint.retry_limit = data.retry_limit

    if data.language is not None:
        checkpoint.language = data.language

    if data.starter_code is not None:
        checkpoint.starter_code = data.starter_code

    if data.constraints is not None:
        checkpoint.constraints = data.constraints

    if data.hints is not None:
        checkpoint.hints = data.hints

    if data.solution is not None:
        checkpoint.solution = data.solution

    if data.explanation is not None:
        checkpoint.explanation = data.explanation

    if data.visible_test_cases is not None:
        checkpoint.visible_test_cases = (
            data.visible_test_cases
        )

    if data.hidden_test_cases is not None:
        checkpoint.hidden_test_cases = (
            data.hidden_test_cases
        )

    updated_checkpoint = (
        await service.update_checkpoint(
            checkpoint
        )
    )

    return CheckpointResponse.model_validate(
        updated_checkpoint
    )


# ============================================================
# DELETE CHECKPOINT
# ============================================================

@router.delete(
    "/{checkpoint_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_checkpoint(
    checkpoint_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """
    Delete a checkpoint.
    """

    service = CheckpointService(session)

    checkpoint = await service.get_by_id(
        checkpoint_id
    )

    if checkpoint is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Checkpoint not found.",
        )

    await service.delete_checkpoint(
        checkpoint
    )

    return None