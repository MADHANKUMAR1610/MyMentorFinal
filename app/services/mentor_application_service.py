from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.mentor_application import MentorApplication
from app.repositories.mentor_application_repository import (
    MentorApplicationRepository,
)


class MentorApplicationService:

    def __init__(self, session: AsyncSession):
        self.repository = MentorApplicationRepository(session)

    async def get_by_id(
        self,
        application_id: UUID,
    ) -> MentorApplication | None:

        return await self.repository.get_by_id(application_id)

    async def get_by_email(
        self,
        email: str,
    ) -> MentorApplication | None:

        return await self.repository.get_by_email(email)

    async def get_by_status(
        self,
        status: str,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[MentorApplication]:

        return await self.repository.get_by_status(
            status,
            skip=skip,
            limit=limit,
        )

    async def get_by_industry(
        self,
        industry: str,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[MentorApplication]:

        return await self.repository.get_by_industry(
            industry,
            skip=skip,
            limit=limit,
        )

    async def get_pending(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[MentorApplication]:

        return await self.repository.get_pending(
            skip=skip,
            limit=limit,
        )

    async def create_application(
        self,
        application: MentorApplication,
    ) -> MentorApplication:

        return await self.repository.create(application)

    async def update_application(
        self,
        application: MentorApplication,
    ) -> MentorApplication:

        return await self.repository.update(application)

    async def delete_application(
        self,
        application: MentorApplication,
    ) -> None:

        await self.repository.delete(application)