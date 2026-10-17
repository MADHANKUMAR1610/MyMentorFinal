
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.skill_assessment_question import (
    SkillAssessmentQuestion,
)
from app.models.skill_assessment_submission import (
    SkillAssessmentSubmission,
)
from app.repositories.skill_assessment_repository import (
    SkillAssessmentCategoryRepository,
    SkillAssessmentQuestionRepository,
)


class SkillAssessmentService:

    def __init__(self, session: AsyncSession):
        self.session = session

        self.category_repository = (
            SkillAssessmentCategoryRepository(session)
        )
        self.question_repository = (
            SkillAssessmentQuestionRepository(session)
        )

    # ========================================================
    # CATEGORIES
    # ========================================================

    async def get_categories(self):
        return await self.category_repository.get_all_categories()

    async def get_category(self, category_id: UUID):
        return await self.category_repository.get_by_id(category_id)

    # ========================================================
    # QUESTIONS
    # ========================================================

    async def get_question(self, question_id: UUID):
        return await self.question_repository.get_by_id(question_id)

    async def get_questions(self, category_id: UUID):
        return await self.question_repository.get_by_category(
            category_id
        )

    async def create_question(
        self,
        question: SkillAssessmentQuestion,
    ):
        return await self.question_repository.create(question)

    async def update_question(
        self,
        question: SkillAssessmentQuestion,
    ):
        return await self.question_repository.update(question)

    async def delete_question(
        self,
        question: SkillAssessmentQuestion,
    ):
        await self.question_repository.delete(question)

    async def get_question_count(self, category_id: UUID):
        return await self.question_repository.count_by_category(
            category_id
        )

    async def get_next_order(self, category_id: UUID):
        return await self.question_repository.get_next_order(
            category_id
        )

    # ========================================================
    # RECORD ASSESSMENT SCORE
    # ========================================================

    async def record_assessment_score(
        self,
        *,
        user_id: UUID,
        question: SkillAssessmentQuestion,
        passed: bool,
    ) -> dict:

        result = await self.session.execute(
            select(SkillAssessmentSubmission).where(
                SkillAssessmentSubmission.user_id == user_id,
                SkillAssessmentSubmission.question_id == question.id,
            )
        )
        submission = result.scalar_one_or_none()

        if submission is None:
            submission = SkillAssessmentSubmission(
                user_id=user_id,
                question_id=question.id,
                passed=passed,
                points_earned=question.points if passed else 0,
            )
            self.session.add(submission)

        elif passed and not submission.passed:
            submission.passed = True
            submission.points_earned = question.points

        await self.session.flush()

        score_result = await self.session.execute(
            select(
                func.coalesce(
                    func.sum(
                        SkillAssessmentSubmission.points_earned
                    ),
                    0,
                )
            )
            .join(
                SkillAssessmentQuestion,
                SkillAssessmentQuestion.id
                == SkillAssessmentSubmission.question_id,
            )
            .where(
                SkillAssessmentSubmission.user_id == user_id,
                SkillAssessmentQuestion.category_id
                == question.category_id,
            )
        )
        section_points = int(score_result.scalar_one())

        completed_result = await self.session.execute(
            select(func.count(SkillAssessmentSubmission.id))
            .join(
                SkillAssessmentQuestion,
                SkillAssessmentQuestion.id
                == SkillAssessmentSubmission.question_id,
            )
            .where(
                SkillAssessmentSubmission.user_id == user_id,
                SkillAssessmentQuestion.category_id
                == question.category_id,
                SkillAssessmentSubmission.passed.is_(True),
                SkillAssessmentQuestion.is_active.is_(True),
            )
        )
        completed_questions = int(completed_result.scalar_one())

        category = await self.get_category(question.category_id)
        total_questions = category.max_questions if category else 5

        return {
            "question_id": str(question.id),
            "passed": submission.passed,
            "points_earned": submission.points_earned,
            "section_points": section_points,
            "completed_questions": completed_questions,
            "total_questions": total_questions,
            "section_completed": (
                completed_questions >= total_questions
            ),
        }
