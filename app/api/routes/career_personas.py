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

    service = CareerPersonaService(session)

    existing_persona = await service.get_by_user_id(
        current_user.id
    )

    # ========================================================
    # GEMINI
    # DO NOT CHANGE THIS
    # ========================================================

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

    # ========================================================
    # CREATE
    # ========================================================

    if existing_persona is None:

        persona = CareerPersona(
            user_id=current_user.id,
            goal=data.goal,
            profile={},
            answers=data.answers,
            result=ai_result,

            # IMPORTANT
            # New career result is NOT visible initially
            is_profile_visible=False,
        )

        persona = await service.create_persona(
            persona
        )

    # ========================================================
    # UPDATE EXISTING
    # ========================================================

    else:

        existing_persona.goal = data.goal
        existing_persona.profile = {}
        existing_persona.answers = data.answers
        existing_persona.result = ai_result

        # IMPORTANT
        # Every new AI result requires a new YES/NO decision
        existing_persona.is_profile_visible = False

        persona = await service.update_persona(
            existing_persona
        )

    # ========================================================
    # RETURN AI RESULT + YES/NO CONFIRMATION
    # ========================================================

    return CareerPersonaFlowResponse(
        requires_class_selection=False,

        career_persona=CareerPersonaResponse.model_validate(
            persona
        ),

        show_profile_confirmation=True,

        profile_confirmation_message=(
            "Would you like to show this Career Plan "
            "on your Profile?"
        ),
    )


# ============================================================
# YES - SHOW CAREER PERSONA ON PROFILE
# ============================================================

@router.post(
    "/me/profile/yes",
    response_model=CareerPersonaResponse,
)
async def show_career_persona_on_profile(
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

    # ========================================================
    # USER CLICKED YES
    # ========================================================

    persona.is_profile_visible = True

    updated_persona = await service.update_persona(
        persona
    )

    return CareerPersonaResponse.model_validate(
        updated_persona
    )


# ============================================================
# NO - DON'T SHOW CAREER PERSONA ON PROFILE
# ============================================================

@router.post(
    "/me/profile/no",
    response_model=CareerPersonaResponse,
)
async def hide_career_persona_from_profile(
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

    # ========================================================
    # USER CLICKED NO
    # ========================================================

    persona.is_profile_visible = False

    updated_persona = await service.update_persona(
        persona
    )

    return CareerPersonaResponse.model_validate(
        updated_persona
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

    # ========================================================
    # SECURITY
    # ========================================================

    if persona.user_id != current_user.id:

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "You do not have access to this "
                "career persona."
            ),
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

    # ========================================================
    # UPDATE GOAL
    # ========================================================

    if data.goal is not None:
        persona.goal = data.goal

    # ========================================================
    # UPDATE PROFILE
    # ========================================================

    if data.profile is not None:
        persona.profile = data.profile

    # ========================================================
    # UPDATE ANSWERS
    # ========================================================

    if data.answers is not None:
        persona.answers = data.answers

    # ========================================================
    # UPDATE AI RESULT
    # ========================================================

    if data.result is not None:
        persona.result = data.result

    # ========================================================
    # SAVE
    # ========================================================

    updated_persona = await service.update_persona(
        persona
    )

    return CareerPersonaResponse.model_validate(
        updated_persona
    )