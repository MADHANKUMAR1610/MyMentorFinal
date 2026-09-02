from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.organization_repository import (
    OrganizationRepository,
)
from app.repositories.organization_ats_config_repository import (
    OrganizationATSConfigRepository,
)


DEFAULT_ATS_CONFIG = {
    "skills": 30,
    "experience": 20,
    "education": 15,
    "role_relevance": 20,
    "screening_questions": 10,
    "certifications": 5,
}


class OrganizationATSConfigService:

    def __init__(self, db: AsyncSession):
        self.organization_repository = OrganizationRepository(db)
        self.ats_repository = OrganizationATSConfigRepository(db)

    # ============================================================
    # GET COMPANY
    # ============================================================

    async def get_company(
        self,
        user_id: UUID,
    ):

        company = await (
            self.organization_repository
            .get_by_admin_user_id(user_id)
        )

        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found for this user",
            )

        return company

    # ============================================================
    # GET ATS CONFIG
    # ============================================================

    async def get_config(
        self,
        user_id: UUID,
    ):

        company = await self.get_company(user_id)

        config = await (
            self.ats_repository
            .get_by_company_id(company.id)
        )

        # If configuration doesn't exist,
        # create it using default values.
        if not config:

            config = await self.ats_repository.create(
                company_id=company.id,
                data=DEFAULT_ATS_CONFIG,
            )

        return config

    # ============================================================
    # UPDATE ATS CONFIG
    # ============================================================

    async def update_config(
        self,
        user_id: UUID,
        data,
    ):

        company = await self.get_company(user_id)

        config = await (
            self.ats_repository
            .get_by_company_id(company.id)
        )

        update_data = data.model_dump(
            exclude_unset=True
        )

        # --------------------------------------------------------
        # If config doesn't exist
        # --------------------------------------------------------

        if not config:

            final_values = {
                **DEFAULT_ATS_CONFIG,
                **update_data,
            }

            # Validate total
            if sum(final_values.values()) != 100:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="ATS configuration weights must total 100",
                )

            return await self.ats_repository.create(
                company_id=company.id,
                data=final_values,
            )

        # --------------------------------------------------------
        # Existing configuration
        # --------------------------------------------------------

        current_values = {
            "skills": config.skills,
            "experience": config.experience,
            "education": config.education,
            "role_relevance": config.role_relevance,
            "screening_questions": config.screening_questions,
            "certifications": config.certifications,
        }

        # Apply only the fields sent by frontend
        current_values.update(update_data)

        # --------------------------------------------------------
        # Validate total
        # --------------------------------------------------------

        if sum(current_values.values()) != 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ATS configuration weights must total 100",
            )

        return await self.ats_repository.update(
            config=config,
            data=current_values,
        )