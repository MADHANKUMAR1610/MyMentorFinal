# app/api/routes/career_personas.py

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
    CareerPersonaFlowResponse,
    CareerPersonaUpdate,
)

from app.services.career_persona_service import CareerPersonaService
from app.services.gemini_service import GeminiService


# ============================================================
# ROUTER
# ============================================================

router = APIRouter(
    prefix="/career-personas",
    tags=["Career Personas"],
)


# ============================================================
# CREATE / GENERATE MY CAREER PERSONA
# ============================================================

@router.post(
    "/me",
    response_model=CareerPersonaFlowResponse,
)
async def create_my_career_persona(
    data: CareerPersonaCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):

    # --------------------------------------------------------
    # 1. Career Persona Service
    # --------------------------------------------------------

    service = CareerPersonaService(session)

    existing_persona = await service.get_by_user_id(
        current_user.id
    )

    # --------------------------------------------------------
    # 2. Generate Career Path using existing Gemini service
    # --------------------------------------------------------

    try:

        gemini_service = GeminiService()

        ai_result = await gemini_service.generate_career_persona(
            goal=data.goal,
            profile={},
            answers=data.answers,
        )

    except Exception as exc:

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        )

    # --------------------------------------------------------
    # 3. Create Career Persona
    # --------------------------------------------------------

    if existing_persona is None:

        persona = CareerPersona(
            user_id=current_user.id,
            goal=data.goal,
            profile={},
            answers=data.answers,
            result=ai_result,
        )

        persona = await service.create_persona(
            persona
        )

    # --------------------------------------------------------
    # 4. Update existing Career Persona
    # --------------------------------------------------------

    else:

        existing_persona.goal = data.goal
        existing_persona.profile = {}
        existing_persona.answers = data.answers
        existing_persona.result = ai_result

        persona = await service.update_persona(
            existing_persona
        )

    # --------------------------------------------------------
    # 5. Return Career Path + Calendar confirmation
    # --------------------------------------------------------

    return CareerPersonaFlowResponse(
        requires_class_selection=False,

        career_persona=CareerPersonaResponse.model_validate(
            persona
        ),

        show_calendar_confirmation=True,

        calendar_message=(
            "Would you like to add this Career Plan "
            "to your Career Calendar?"
        ),
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

    return CareerPersonaResponse.model_validate(
        persona
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

    # User can access only their own persona
    if persona.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this career persona.",
        )

    return CareerPersonaResponse.model_validate(
        persona
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

    # --------------------------------------------------------
    # Update goal
    # --------------------------------------------------------

    if data.goal is not None:
        persona.goal = data.goal

    # --------------------------------------------------------
    # Update profile
    # --------------------------------------------------------

    if data.profile is not None:
        persona.profile = data.profile

    # --------------------------------------------------------
    # Update answers
    # --------------------------------------------------------

    if data.answers is not None:
        persona.answers = data.answers

    # --------------------------------------------------------
    # Update AI result
    # --------------------------------------------------------

    if data.result is not None:
        persona.result = data.result

    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    updated_persona = await service.update_persona(
        persona
    )

    return CareerPersonaResponse.model_validate(
        updated_persona
    )