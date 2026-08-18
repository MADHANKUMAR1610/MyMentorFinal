from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.company import Company
from app.repositories.company_repository import CompanyRepository


class CompanyService:

    def __init__(self, session: AsyncSession):
        self.repository = CompanyRepository(session)

    async def get_by_id(
        self,
        company_id: UUID,
    ) -> Company | None:

        return await self.repository.get_by_id(company_id)

    async def get_by_name(
        self,
        name: str,
    ) -> Company | None:

        return await self.repository.get_by_name(name)

    async def get_by_industry(
        self,
        industry: str,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Company]:

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
    ) -> list[Company]:

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
    ) -> list[Company]:

        return await self.repository.get_verified(
            skip=skip,
            limit=limit,
        )

    async def get_by_location(
        self,
        location: str,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Company]:

        return await self.repository.get_by_location(
            location,
            skip=skip,
            limit=limit,
        )

    async def create_company(
        self,
        company: Company,
    ) -> Company:

        return await self.repository.create(company)

    async def update_company(
        self,
        company: Company,
    ) -> Company:

        return await self.repository.update(company)

    async def delete_company(
        self,
        company: Company,
    ) -> None:

        await self.repository.delete(company)