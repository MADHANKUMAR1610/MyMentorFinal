
import asyncio

from sqlalchemy import select

from app.database.database import AsyncSessionLocal
from app.models.skill_assessment_category import (
    SkillAssessmentCategory,
)


CATEGORIES = [
    {
        "name": "Technical Skills",
        "description": (
            "Technical and programming-based challenges."
        ),
        "max_questions": 5,
        "display_order": 1,
    },
    {
        "name": "Problem Solving",
        "description": (
            "Logic, algorithms and practical "
            "problem-solving challenges."
        ),
        "max_questions": 5,
        "display_order": 2,
    },
    {
        "name": "Critical Thinking",
        "description": (
            "Reasoning, analysis and decision-making "
            "challenges."
        ),
        "max_questions": 5,
        "display_order": 3,
    },
    {
        "name": "Interview Readiness",
        "description": (
            "Interview preparation, technical explanation "
            "and workplace scenarios."
        ),
        "max_questions": 5,
        "display_order": 4,
    },
    {
        "name": "Soft Skills",
        "description": (
            "Communication, teamwork, leadership and "
            "professional situations."
        ),
        "max_questions": 5,
        "display_order": 5,
    },
]


async def seed_categories():
    async with AsyncSessionLocal() as session:
        try:
            for item in CATEGORIES:
                result = await session.execute(
                    select(SkillAssessmentCategory).where(
                        SkillAssessmentCategory.name
                        == item["name"]
                    )
                )

                category = result.scalar_one_or_none()

                if category is None:
                    category = SkillAssessmentCategory(
                        **item,
                        is_active=True,
                    )
                    session.add(category)
                    print(f"Created: {item['name']}")
                else:
                    category.description = item["description"]
                    category.max_questions = item["max_questions"]
                    category.display_order = item["display_order"]
                    category.is_active = True
                    print(f"Updated: {item['name']}")

            await session.commit()
            print("Skill Assessment categories seeded successfully.")

        except Exception:
            await session.rollback()
            raise


if __name__ == "__main__":
    asyncio.run(seed_categories())
