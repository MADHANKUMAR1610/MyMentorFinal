from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.organization import OrganizationUpdate
from app.repositories.organization_repository import (
    OrganizationRepository,
)


class OrganizationService:

    def __init__(self, db: AsyncSession):
        self.repository = OrganizationRepository(db)

    async def get_my_organization(
        self,
        user_id: UUID,
    ):
        company = await self.repository.get_by_admin_user_id(
            user_id
        )

        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found for this user",
            )

        return company
    async def update_my_organization(
        self,
        user_id: UUID,
        data: OrganizationUpdate,
    ):
        company = await self.repository.get_by_admin_user_id(
            user_id
        )

        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found for this user",
            )

        update_data = data.model_dump(
            exclude_unset=True
        )

        return await self.repository.update(
            company,
            update_data,
        )