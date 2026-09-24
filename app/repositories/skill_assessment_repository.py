from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.skill_assessment_category import (
    SkillAssessmentCategory,
)
from app.models.skill_assessment_question import (
    SkillAssessmentQuestion,
)
from app.repositories.base import BaseRepository


class SkillAssessmentCategoryRepository(
    BaseRepository[SkillAssessmentCategory]
):

    def __init__(self, session: AsyncSession):
        super().__init__(
            SkillAssessmentCategory,
            session,
        )

    async def get_all_categories(self):
        result = await self.session.execute(
            select(
                SkillAssessmentCategory,
                func.count(
                    SkillAssessmentQuestion.id
                ).label("question_count"),
            )
            .outerjoin(
                SkillAssessmentQuestion,
                SkillAssessmentQuestion.category_id
                == SkillAssessmentCategory.id,
            )
            .where(
                SkillAssessmentCategory.is_active.is_(True)
            )
            .group_by(
                SkillAssessmentCategory.id
            )
            .order_by(
                SkillAssessmentCategory.display_order.asc()
            )
        )

        return result.all()


class SkillAssessmentQuestionRepository(
    BaseRepository[SkillAssessmentQuestion]
):

    def __init__(self, session: AsyncSession):
        super().__init__(
            SkillAssessmentQuestion,
            session,
        )

    async def get_by_category(
        self,
        category_id: UUID,
    ):

        result = await self.session.execute(
            select(SkillAssessmentQuestion)
            .where(
                SkillAssessmentQuestion.category_id
                == category_id
            )
            .order_by(
                SkillAssessmentQuestion.question_order.asc()
            )
        )

        return list(
            result.scalars().all()
        )

    async def count_by_category(
        self,
        category_id: UUID,
    ) -> int:

        result = await self.session.execute(
            select(
                func.count(
                    SkillAssessmentQuestion.id
                )
            )
            .where(
                SkillAssessmentQuestion.category_id
                == category_id
            )
        )

        return result.scalar_one()

    async def get_next_order(
        self,
        category_id: UUID,
    ) -> int:

        result = await self.session.execute(
            select(
                func.coalesce(
                    func.max(
                        SkillAssessmentQuestion.question_order
                    ),
                    0,
                )
            )
            .where(
                SkillAssessmentQuestion.category_id
                == category_id
            )
        )

        return result.scalar_one() + 1