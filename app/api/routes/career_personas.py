# app/api/routes/career_personas.py

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

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
    # 1. Get logged-in user + profile
    # --------------------------------------------------------

    result = await session.execute(
        select(User)
        .options(
            selectinload(User.profile)
        )
        .where(User.id == current_user.id)
    )

    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )

    profile = user.profile

    # --------------------------------------------------------
    # 2. Profile does not exist
    #
    # IMPORTANT:
    # Do NOT return 404 here.
    #
    # Frontend should show class selection popup.
    # --------------------------------------------------------

    if profile is None:

        return CareerPersonaFlowResponse(
            requires_class_selection=True,
            career_persona=None,
        )

    # --------------------------------------------------------
    # 3. Check education / class
    #
    # If class_year is missing:
    #     Show class selection popup
    #
    # If class_year exists:
    #     Skip popup and continue to AI
    # --------------------------------------------------------

    if not profile.education or not profile.class_year:

        return CareerPersonaFlowResponse(
            requires_class_selection=True,
            career_persona=None,
        )

    # --------------------------------------------------------
    # 4. Career Persona Service
    # --------------------------------------------------------

    service = CareerPersonaService(session)

    existing_persona = await service.get_by_user_id(
        user.id
    )

    # --------------------------------------------------------
    # 5. Educational context ONLY
    #
    # Do NOT send old career_goal or career_interests.
    #
    # Current request goal has priority.
    # --------------------------------------------------------

    education_context = {
        "age": profile.age,
        "education": profile.education,
        "class_year": profile.class_year,
    }

    # --------------------------------------------------------
    # 6. Generate AI Career Persona
    # --------------------------------------------------------

    try:

        gemini_service = GeminiService()

        ai_result = await gemini_service.generate_career_persona(
            goal=data.goal,
            profile=education_context,
            answers=data.answers,
        )

    except Exception as exc:

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        )

    # --------------------------------------------------------
    # 7. Create / Update Career Persona
    # --------------------------------------------------------

    if existing_persona is None:

        persona = CareerPersona(
            user_id=user.id,
            goal=data.goal,
            profile=education_context,
            answers=data.answers,
            result=ai_result,
        )

        persona = await service.create_persona(
            persona
        )

    else:

        # Update current goal
        existing_persona.goal = data.goal

        # Update educational context
        existing_persona.profile = education_context

        # Update answers
        existing_persona.answers = data.answers

        # Update AI result
        existing_persona.result = ai_result

        persona = await service.update_persona(
            existing_persona
        )

    # --------------------------------------------------------
    # 8. Return AI Career Path
    # --------------------------------------------------------

    return CareerPersonaFlowResponse(
        requires_class_selection=False,
        career_persona=CareerPersonaResponse.model_validate(
            persona
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