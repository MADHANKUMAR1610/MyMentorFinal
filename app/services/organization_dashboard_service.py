from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.organization_repository import (
    OrganizationRepository,
)

from app.repositories.organization_dashboard_repository import (
    OrganizationDashboardRepository,
)


class OrganizationDashboardService:

    def __init__(self, db: AsyncSession):

        self.organization_repository = (
            OrganizationRepository(db)
        )

        self.dashboard_repository = (
            OrganizationDashboardRepository(db)
        )

    async def get_my_dashboard(
        self,
        user_id: UUID,
    ):

        # --------------------------------------------
        # Find organization owned by logged-in admin
        # --------------------------------------------

        company = await (
            self.organization_repository
            .get_by_admin_user_id(user_id)
        )

        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found for this user",
            )

        # --------------------------------------------
        # Get dashboard statistics
        # --------------------------------------------

        stats = await (
            self.dashboard_repository
            .get_dashboard_data(company.id)
        )

        # --------------------------------------------
        # Final response
        # --------------------------------------------

        return {
            "organization_id": company.id,
            "organization_name": company.name,
            "industry": company.industry,
            "logo": company.logo,
            "verified": company.verified,
            "stats": stats,
        }