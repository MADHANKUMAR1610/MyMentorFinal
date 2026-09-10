from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.career_search_knowledge import CareerSearchKnowledge


class CareerSearchKnowledgeRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def search(
        self,
        normalized_query: str,
    ) -> CareerSearchKnowledge | None:

        result = await self.session.execute(
            select(CareerSearchKnowledge).where(
                CareerSearchKnowledge.is_active.is_(True),
                or_(
                    CareerSearchKnowledge.query == normalized_query,
                    CareerSearchKnowledge.keywords.contains(
                        [normalized_query]
                    ),
                ),
            )
        )

        return result.scalars().first()

    async def create(
        self,
        knowledge: CareerSearchKnowledge,
    ) -> CareerSearchKnowledge:

        self.session.add(knowledge)

        await self.session.flush()
        await self.session.refresh(knowledge)

        return knowledge