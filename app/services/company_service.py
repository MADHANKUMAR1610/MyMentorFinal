from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.models.company import Company
from app.models.user import User
from app.repositories.company_repository import (
    CompanyRepository,
)
from app.utils.email_utils import (
    validate_official_company_email,
)


class CompanyService:

    def __init__(
        self,
        session: AsyncSession,
    ):
        self.session = session

        self.repository = CompanyRepository(
            session
        )

    # ========================================================
    # GET BY ID
    # ========================================================

    async def get_by_id(
        self,
        company_id: UUID,
    ) -> Company | None:

        return await self.repository.get_by_id(
            company_id
        )

    # ========================================================
    # GET BY NAME
    # ========================================================

    async def get_by_name(
        self,
        name: str,
    ) -> Company | None:

        return await self.repository.get_by_name(
            name
        )

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

        return await self.repository.get_by_industry(
            industry,
            skip=skip,
            limit=limit,
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

        return await self.repository.get_by_status(
            status,
            skip=skip,
            limit=limit,
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

        return await self.repository.get_verified(
            skip=skip,
            limit=limit,
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

        return await self.repository.get_by_location(
            location,
            skip=skip,
            limit=limit,
        )

    # ========================================================
    # CREATE COMPANY
    # ========================================================

    async def create_company(
        self,
        company: Company,
    ) -> Company:

        return await self.repository.create(
            company
        )

    # ========================================================
    # UPDATE COMPANY
    # ========================================================

    async def update_company(
        self,
        company: Company,
    ) -> Company:

        return await self.repository.update(
            company
        )

    # ========================================================
    # DELETE COMPANY
    # ========================================================

    async def delete_company(
        self,
        company: Company,
    ) -> None:

        await self.repository.delete(
            company
        )

    # ========================================================
    # COMPANY ONBOARDING
    # ========================================================

    async def onboard_company(
        self,
        *,
        company_data,
        current_user: User,
    ) -> Company:

        # ====================================================
        # STEP 1
        # CHECK COMPANY NAME
        # ====================================================

        existing_company = (
            await self.repository.get_by_name(
                company_data.name
            )
        )

        if existing_company is not None:
            raise ValueError(
                "A company with this name already exists."
            )

        # ====================================================
        # STEP 2
        # GOOGLE USER MUST EXIST
        # ====================================================

        if not current_user.google_id:
            raise ValueError(
                "Company onboarding requires "
                "Google authentication."
            )

        # ====================================================
        # STEP 3
        # VALIDATE ADMIN EMAIL
        # ====================================================

        admin_email = (
            validate_official_company_email(
                company_data.admin_official_email,
                company_data.website,
            )
        )

        # ====================================================
        # CHECK ADMIN EMAIL ALREADY EXISTS
        # ====================================================

        result = await self.session.execute(
            select(User).where(
                User.email == admin_email
            )
        )

        existing_admin = (
            result.scalar_one_or_none()
        )

        if existing_admin is not None:
            raise ValueError(
                "An account with this admin email "
                "already exists."
            )

        # ====================================================
        # CREATE COMPANY
        # ====================================================

        company = Company(
            name=company_data.name,
            industry=company_data.industry,
            logo=company_data.logo,
            location=company_data.location,
            size=company_data.size,
            open_roles=company_data.open_roles,
            about=company_data.about,
            website=company_data.website,

            # NEVER TRUST FRONTEND FOR THESE
            status="pending",
            verified=False,

            # GOOGLE USER DATA
            contact_person_name=current_user.name,
            contact_email=current_user.email,
            contact_phone=company_data.contact_phone,
            contact_role=company_data.contact_role,
        )

        self.session.add(company)

        # Get company UUID before creating admin
        await self.session.flush()

        # ====================================================
        # CREATE ADMIN USER
        # ====================================================

        admin_user = User(
    email=admin_email,

    password_hash=hash_password(
        company_data.password
    ),

    name=current_user.name,

    # ✅ ADD THIS
    phone=company_data.contact_phone,

    role="organization_admin",

    company_id=company.id,

    is_active=True,

    is_verified=False,

    onboarded=True,
)

        self.session.add(admin_user)

        await self.session.flush()

        # ====================================================
        # LINK ADMIN TO COMPANY
        # ====================================================

        company.admin_user_id = (
            admin_user.id
        )

        await self.session.flush()

        # ====================================================
        # COMMIT
        # ====================================================

        await self.session.commit()

        await self.session.refresh(
            company
        )

        return company