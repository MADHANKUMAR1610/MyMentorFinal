import re

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.career_search_knowledge import CareerSearchKnowledge
from app.repositories.career_search_knowledge_repository import (
    CareerSearchKnowledgeRepository,
)
from app.services.gemini_service import GeminiService


class CareerSearchService:

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = CareerSearchKnowledgeRepository(session)
        self.gemini = GeminiService()

    # ---------------------------------------------------------
    # NORMALIZE SEARCH
    # ---------------------------------------------------------

    @staticmethod
    def normalize_query(query: str) -> str:

        query = query.lower().strip()

        query = re.sub(
            r"[^a-z0-9\s]",
            " ",
            query,
        )

        query = re.sub(
            r"\s+",
            " ",
            query,
        )

        return query.strip()

    # ---------------------------------------------------------
    # SEARCH CAREER
    # ---------------------------------------------------------

    async def search(
        self,
        query: str,
        profile: dict | None = None,
        answers: dict | None = None,
    ) -> dict:

        normalized_query = self.normalize_query(query)

        # =====================================================
        # 1. CHECK DATABASE
        # =====================================================

        cached = await self.repository.search(
            normalized_query
        )

        if cached:

            return {
                "source": "database",
                "query": query,
                "career": cached.result,
            }

        # =====================================================
        # 2. NOT FOUND → CALL GEMINI
        # =====================================================

        ai_result = await self.gemini.generate_career_persona(
            goal=query,
            profile=profile or {},
            answers=answers or {},
        )

        # =====================================================
        # 3. SAVE GEMINI RESULT
        # =====================================================

        knowledge = CareerSearchKnowledge(
            query=normalized_query,
            keywords=[
                normalized_query,
            ],
            result=ai_result,
            is_active=True,
        )

        await self.repository.create(knowledge)

        await self.session.commit()

        # =====================================================
        # 4. RETURN RESULT
        # =====================================================

        return {
            "source": "llm",
            "query": query,
            "career": ai_result,
        }