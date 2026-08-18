from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.company_application import CompanyApplication
from app.repositories.company_application_repository import (
    CompanyApplicationRepository,
)


class CompanyApplicationService:

    def __init__(self, session: AsyncSession):
        self.repository = CompanyApplicationRepository(session)

    async def get_by_id(
        self,
        application_id: UUID,
    ) -> CompanyApplication | None:

        return await self.repository.get_by_id(application_id)

    async def get_by_email(
        self,
        email: str,
    ) -> CompanyApplication | None:

        return await self.repository.get_by_email(email)

    async def get_by_submitted_user(
        self,
        user_id: UUID,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[CompanyApplication]:

        return await self.repository.get_by_submitted_user(
            user_id,
            skip=skip,
            limit=limit,
        )

    async def get_by_status(
        self,
        status: str,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[CompanyApplication]:

        return await self.repository.get_by_status(
            status,
            skip=skip,
            limit=limit,
        )

    async def get_pending(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[CompanyApplication]:

        return await self.repository.get_pending(
            skip=skip,
            limit=limit,
        )

    async def get_by_industry(
        self,
        industry: str,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[CompanyApplication]:

        return await self.repository.get_by_industry(
            industry,
            skip=skip,
            limit=limit,
        )

    async def create_application(
        self,
        application: CompanyApplication,
    ) -> CompanyApplication:

        return await self.repository.create(application)

    async def update_application(
        self,
        application: CompanyApplication,
    ) -> CompanyApplication:

        return await self.repository.update(application)

    async def delete_application(
        self,
        application: CompanyApplication,
    ) -> None:

        await self.repository.delete(application)