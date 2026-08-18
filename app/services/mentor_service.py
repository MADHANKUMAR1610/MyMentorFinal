from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.mentor import Mentor
from app.repositories.mentor_repository import MentorRepository


class MentorService:

    def __init__(self, session: AsyncSession):
        self.repository = MentorRepository(session)

    async def get_by_id(
        self,
        mentor_id: UUID,
    ) -> Mentor | None:

        return await self.repository.get_by_id(mentor_id)

    async def get_by_industry(
        self,
        industry: str,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Mentor]:

        return await self.repository.get_by_industry(
            industry,
            skip=skip,
            limit=limit,
        )

    async def get_by_status(
        self,
        status: str,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Mentor]:

        return await self.repository.get_by_status(
            status,
            skip=skip,
            limit=limit,
        )

    async def get_verified(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Mentor]:

        return await self.repository.get_verified(
            skip=skip,
            limit=limit,
        )

    async def get_by_role(
        self,
        role: str,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Mentor]:

        return await self.repository.get_by_role(
            role,
            skip=skip,
            limit=limit,
        )

    async def create_mentor(
        self,
        mentor: Mentor,
    ) -> Mentor:

        return await self.repository.create(mentor)

    async def update_mentor(
        self,
        mentor: Mentor,
    ) -> Mentor:

        return await self.repository.update(mentor)

    async def delete_mentor(
        self,
        mentor: Mentor,
    ) -> None:

        await self.repository.delete(mentor)