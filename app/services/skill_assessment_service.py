from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.skill_assessment_question import (
    SkillAssessmentQuestion,
)
from app.repositories.skill_assessment_repository import (
    SkillAssessmentCategoryRepository,
    SkillAssessmentQuestionRepository,
)


class SkillAssessmentService:

    def __init__(
        self,
        session: AsyncSession,
    ):
        self.category_repository = (
            SkillAssessmentCategoryRepository(
                session
            )
        )

        self.question_repository = (
            SkillAssessmentQuestionRepository(
                session
            )
        )

    # ========================================================
    # CATEGORIES
    # ========================================================

    async def get_categories(self):

        return await (
            self.category_repository
            .get_all_categories()
        )

    async def get_category(
        self,
        category_id: UUID,
    ):

        return await (
            self.category_repository
            .get_by_id(category_id)
        )

    # ========================================================
    # QUESTIONS
    # ========================================================

    async def get_question(
        self,
        question_id: UUID,
    ):

        return await (
            self.question_repository
            .get_by_id(question_id)
        )

    async def get_questions(
        self,
        category_id: UUID,
    ):

        return await (
            self.question_repository
            .get_by_category(category_id)
        )

    async def create_question(
        self,
        question: SkillAssessmentQuestion,
    ):

        return await (
            self.question_repository
            .create(question)
        )

    async def update_question(
        self,
        question: SkillAssessmentQuestion,
    ):

        return await (
            self.question_repository
            .update(question)
        )

    async def delete_question(
        self,
        question: SkillAssessmentQuestion,
    ):

        await (
            self.question_repository
            .delete(question)
        )

    async def get_question_count(
        self,
        category_id: UUID,
    ):

        return await (
            self.question_repository
            .count_by_category(category_id)
        )

    async def get_next_order(
        self,
        category_id: UUID,
    ):

        return await (
            self.question_repository
            .get_next_order(category_id)
        )