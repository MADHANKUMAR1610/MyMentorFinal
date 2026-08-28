from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.company import Company


class OrganizationRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_admin_user_id(
        self,
        admin_user_id: UUID,
    ) -> Company | None:

        result = await self.db.execute(
            select(Company).where(
                Company.admin_user_id == admin_user_id
            )
        )

        return result.scalar_one_or_none()
    async def update(
        self,
        company,
        data: dict,
    ):
        for field, value in data.items():
            if value is not None:
                setattr(company, field, value)

        await self.db.commit()
        await self.db.refresh(company)

        return company