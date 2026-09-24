from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import (
    get_current_admin,
)
from app.database.database import get_db

from app.models.user import User
from app.models.skill_assessment_question import (
    SkillAssessmentQuestion,
)

from app.schemas.skill_assessment import (
    SkillAssessmentCategoryResponse,
    SkillAssessmentQuestionCreate,
    SkillAssessmentQuestionResponse,
    SkillAssessmentQuestionUpdate,
)

from app.services.skill_assessment_service import (
    SkillAssessmentService,
)


router = APIRouter(
    prefix="/skill-assessment",
    tags=["Skill Assessment"],
)


# ============================================================
# GET CATEGORIES
# ============================================================

@router.get(
    "/categories",
    response_model=list[
        SkillAssessmentCategoryResponse
    ],
)
async def get_categories(
    current_user: User = Depends(
        get_current_admin
    ),
    session: AsyncSession = Depends(
        get_db
    ),
):

    service = SkillAssessmentService(
        session
    )

    rows = await service.get_categories()

    return [
        SkillAssessmentCategoryResponse(
            id=category.id,
            name=category.name,
            description=category.description,
            max_questions=category.max_questions,
            question_count=question_count,
            display_order=category.display_order,
            is_active=category.is_active,
        )
        for category, question_count in rows
    ]


# ============================================================
# GET QUESTIONS BY CATEGORY
# ============================================================

@router.get(
    "/categories/{category_id}/questions",
    response_model=list[
        SkillAssessmentQuestionResponse
    ],
)
async def get_questions(
    category_id: UUID,
    current_user: User = Depends(
        get_current_admin
    ),
    session: AsyncSession = Depends(
        get_db
    ),
):

    service = SkillAssessmentService(
        session
    )

    category = await service.get_category(
        category_id
    )

    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment category not found.",
        )

    questions = await service.get_questions(
        category_id
    )

    return [
        SkillAssessmentQuestionResponse.model_validate(
            question
        )
        for question in questions
    ]


# ============================================================
# CREATE QUESTION
# ============================================================

@router.post(
    "/questions",
    response_model=SkillAssessmentQuestionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_question(
    data: SkillAssessmentQuestionCreate,
    current_user: User = Depends(
        get_current_admin
    ),
    session: AsyncSession = Depends(
        get_db
    ),
):

    service = SkillAssessmentService(
        session
    )

    # --------------------------------------------------------
    # CHECK CATEGORY
    # --------------------------------------------------------

    category = await service.get_category(
        data.category_id
    )

    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment category not found.",
        )

    # --------------------------------------------------------
    # CHECK MAX 5 QUESTIONS
    # --------------------------------------------------------

    question_count = await (
        service.get_question_count(
            data.category_id
        )
    )

    if question_count >= category.max_questions:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"This category already has "
                f"{category.max_questions} questions."
            ),
        )

    # --------------------------------------------------------
    # ORDER
    # --------------------------------------------------------

    question_order = await (
        service.get_next_order(
            data.category_id
        )
    )

    question = SkillAssessmentQuestion(
        category_id=data.category_id,
        question_order=question_order,
        title=data.title.strip(),
        problem=data.problem,
        instructions=data.instructions,
        language=data.language,
        difficulty=data.difficulty,
        points=data.points,
        starter_code=data.starter_code,
        expected_answer=data.expected_answer,
        evaluation_criteria=data.evaluation_criteria,
    )

    created_question = await (
        service.create_question(
            question
        )
    )

    return SkillAssessmentQuestionResponse.model_validate(
        created_question
    )


# ============================================================
# GET QUESTION
# ============================================================

@router.get(
    "/questions/{question_id}",
    response_model=SkillAssessmentQuestionResponse,
)
async def get_question(
    question_id: UUID,
    current_user: User = Depends(
        get_current_admin
    ),
    session: AsyncSession = Depends(
        get_db
    ),
):

    service = SkillAssessmentService(
        session
    )

    question = await service.get_question(
        question_id
    )

    if question is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found.",
        )

    return SkillAssessmentQuestionResponse.model_validate(
        question
    )


# ============================================================
# UPDATE QUESTION
# ============================================================

@router.put(
    "/questions/{question_id}",
    response_model=SkillAssessmentQuestionResponse,
)
async def update_question(
    question_id: UUID,
    data: SkillAssessmentQuestionUpdate,
    current_user: User = Depends(
        get_current_admin
    ),
    session: AsyncSession = Depends(
        get_db
    ),
):

    service = SkillAssessmentService(
        session
    )

    question = await service.get_question(
        question_id
    )

    if question is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found.",
        )

    if data.title is not None:
        question.title = data.title.strip()

    if data.problem is not None:
        question.problem = data.problem

    if data.instructions is not None:
        question.instructions = data.instructions

    if data.language is not None:
        question.language = data.language

    if data.difficulty is not None:
        question.difficulty = data.difficulty

    if data.points is not None:
        question.points = data.points

    if data.starter_code is not None:
        question.starter_code = data.starter_code

    if data.expected_answer is not None:
        question.expected_answer = data.expected_answer

    if data.evaluation_criteria is not None:
        question.evaluation_criteria = (
            data.evaluation_criteria
        )

    if data.is_active is not None:
        question.is_active = data.is_active

    updated_question = await (
        service.update_question(
            question
        )
    )

    return SkillAssessmentQuestionResponse.model_validate(
        updated_question
    )


# ============================================================
# DELETE QUESTION
# ============================================================

@router.delete(
    "/questions/{question_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_question(
    question_id: UUID,
    current_user: User = Depends(
        get_current_admin
    ),
    session: AsyncSession = Depends(
        get_db
    ),
):

    service = SkillAssessmentService(
        session
    )

    question = await service.get_question(
        question_id
    )

    if question is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found.",
        )

    await service.delete_question(
        question
    )

    return None