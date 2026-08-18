from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.company_application import CompanyApplication
from app.repositories.base import BaseRepository


class CompanyApplicationRepository(
    BaseRepository[CompanyApplication]
):
    """
    Repository responsible for CompanyApplication
    database operations.

    Business rules belong in the service layer.
    """

    def __init__(self, session: AsyncSession):
        super().__init__(CompanyApplication, session)

    async def get_by_email(
        self,
        email: str,
    ) -> Optional[CompanyApplication]:
        """
        Get a company application by contact email.
        """

        result = await self.session.execute(
            select(CompanyApplication).where(
                CompanyApplication.email == email
            )
        )

        return result.scalar_one_or_none()

    async def get_by_submitted_user(
        self,
        user_id: UUID,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[CompanyApplication]:
        """
        Get applications submitted by a specific user.
        """

        result = await self.session.execute(
            select(CompanyApplication)
            .where(
                CompanyApplication.submitted_by == user_id
            )
            .order_by(
                CompanyApplication.created_at.desc()
            )
            .offset(skip)
            .limit(limit)
        )

        return list(result.scalars().all())

    async def get_by_status(
        self,
        status: str,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[CompanyApplication]:
        """
        Get company applications by status.
        """

        result = await self.session.execute(
            select(CompanyApplication)
            .where(
                CompanyApplication.status == status
            )
            .order_by(
                CompanyApplication.created_at.desc()
            )
            .offset(skip)
            .limit(limit)
        )

        return list(result.scalars().all())

    async def get_pending(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[CompanyApplication]:
        """
        Get applications waiting for review.
        """

        result = await self.session.execute(
            select(CompanyApplication)
            .where(
                CompanyApplication.status == "pending"
            )
            .order_by(
                CompanyApplication.created_at.asc()
            )
            .offset(skip)
            .limit(limit)
        )

        return list(result.scalars().all())

    async def get_by_industry(
        self,
        industry: str,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[CompanyApplication]:
        """
        Get applications by industry.
        """

        result = await self.session.execute(
            select(CompanyApplication)
            .where(
                CompanyApplication.industry == industry
            )
            .offset(skip)
            .limit(limit)
        )

        return list(result.scalars().all())