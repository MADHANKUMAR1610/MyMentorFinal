from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.database.database import get_db
from app.models.user import User
from app.models.career_persona import CareerPersona
from app.schemas.career_persona import (
    CareerPersonaCreate,
    CareerPersonaResponse,
    CareerPersonaUpdate,
)
from app.services.career_persona_service import CareerPersonaService


router = APIRouter(
    prefix="/career-personas",
    tags=["Career Personas"],
)


# ============================================================
# GET MY CAREER PERSONA
# ============================================================

@router.get(
    "/me",
    response_model=CareerPersonaResponse,
)
async def get_my_career_persona(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    service = CareerPersonaService(session)

    persona = await service.get_by_user_id(
        current_user.id
    )

    if persona is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Career persona not found.",
        )

    return CareerPersonaResponse.model_validate(persona)


# ============================================================
# CREATE MY CAREER PERSONA
# ============================================================

@router.post(
    "/me",
    response_model=CareerPersonaResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_my_career_persona(
    data: CareerPersonaCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    service = CareerPersonaService(session)

    existing_persona = await service.get_by_user_id(
        current_user.id
    )

    if existing_persona is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Career persona already exists.",
        )

    persona = CareerPersona(
        user_id=current_user.id,
        goal=data.goal,
        profile=data.profile,
        answers=data.answers,
        result=data.result,
    )

    created_persona = await service.create_persona(
        persona
    )

    return CareerPersonaResponse.model_validate(
        created_persona
    )


# ============================================================
# UPDATE MY CAREER PERSONA
# ============================================================

@router.put(
    "/me",
    response_model=CareerPersonaResponse,
)
async def update_my_career_persona(
    data: CareerPersonaUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    service = CareerPersonaService(session)

    persona = await service.get_by_user_id(
        current_user.id
    )

    if persona is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Career persona not found.",
        )

    if data.goal is not None:
        persona.goal = data.goal

    if data.profile is not None:
        persona.profile = data.profile

    if data.answers is not None:
        persona.answers = data.answers

    if data.result is not None:
        persona.result = data.result

    updated_persona = await service.update_persona(
        persona
    )

    return CareerPersonaResponse.model_validate(
        updated_persona
    )


# ============================================================
# GET CAREER PERSONA BY ID
# ============================================================

@router.get(
    "/{persona_id}",
    response_model=CareerPersonaResponse,
)
async def get_career_persona_by_id(
    persona_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    service = CareerPersonaService(session)

    persona = await service.get_by_id(
        persona_id
    )

    if persona is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Career persona not found.",
        )

    return CareerPersonaResponse.model_validate(
        persona
    )