from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.organization_ats_config import (
    OrganizationATSConfig,
)



class OrganizationATSConfigRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    # ============================================================
    # GET CONFIGURATION
    # ============================================================

    async def get_by_company_id(
        self,
        company_id: UUID,
    ) -> OrganizationATSConfig | None:

        result = await self.db.execute(
            select(OrganizationATSConfig)
            .where(
                OrganizationATSConfig.company_id
                == company_id
            )
        )

        return result.scalar_one_or_none()

    # ============================================================
    # CREATE CONFIGURATION
    # ============================================================

    async def create(
        self,
        company_id: UUID,
        data: dict,
    ) -> OrganizationATSConfig:

        config = OrganizationATSConfig(
            company_id=company_id,
            skills=data.get("skills", 30),
            experience=data.get("experience", 20),
            education=data.get("education", 15),
            role_relevance=data.get(
                "role_relevance",
                20,
            ),
            screening_questions=data.get(
                "screening_questions",
                10,
            ),
            certifications=data.get(
                "certifications",
                5,
            ),
        )

        self.db.add(config)

        await self.db.commit()
        await self.db.refresh(config)

        return config

    # ============================================================
    # UPDATE CONFIGURATION
    # ============================================================

    async def update(
        self,
        config: OrganizationATSConfig,
        data: dict,
    ) -> OrganizationATSConfig:

        config.skills = data["skills"]
        config.experience = data["experience"]
        config.education = data["education"]
        config.role_relevance = data["role_relevance"]
        config.screening_questions = data[
            "screening_questions"
        ]
        config.certifications = data[
            "certifications"
        ]

        await self.db.commit()
        await self.db.refresh(config)

        return config