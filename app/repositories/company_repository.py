from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.company import Company
from app.repositories.base import BaseRepository


class CompanyRepository(
    BaseRepository[Company]
):

    def __init__(
        self,
        session: AsyncSession,
    ):
        super().__init__(
            Company,
            session,
        )

    # ========================================================
    # GET BY NAME
    # ========================================================

    async def get_by_name(
        self,
        name: str,
    ) -> Optional[Company]:

        result = await self.session.execute(
            select(Company).where(
                Company.name == name
            )
        )

        return result.scalar_one_or_none()

    # ========================================================
    # GET BY INDUSTRY
    # ========================================================

    async def get_by_industry(
        self,
        industry: str,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Company]:

        result = await self.session.execute(
            select(Company)
            .where(
                Company.industry == industry
            )
            .offset(skip)
            .limit(limit)
        )

        return list(
            result.scalars().all()
        )

    # ========================================================
    # GET BY STATUS
    # ========================================================

    async def get_by_status(
        self,
        status: str,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Company]:

        result = await self.session.execute(
            select(Company)
            .where(
                Company.status == status
            )
            .offset(skip)
            .limit(limit)
        )

        return list(
            result.scalars().all()
        )

    # ========================================================
    # GET VERIFIED
    # ========================================================

    async def get_verified(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Company]:

        result = await self.session.execute(
            select(Company)
            .where(
                Company.verified.is_(True)
            )
            .offset(skip)
            .limit(limit)
        )

        return list(
            result.scalars().all()
        )

    # ========================================================
    # GET BY LOCATION
    # ========================================================

    async def get_by_location(
        self,
        location: str,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Company]:

        result = await self.session.execute(
            select(Company)
            .where(
                Company.location == location
            )
            .offset(skip)
            .limit(limit)
        )

        return list(
            result.scalars().all()
        )