from urllib.parse import urlparse

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.models.company import Company
from app.models.user import User
from app.schemas.company_onboarding import (
    CompanyOnboardingCreate,
)


class CompanyOnboardingService:

    def __init__(
        self,
        session: AsyncSession,
    ):
        self.session = session

    # ========================================================
    # WEBSITE DOMAIN
    # ========================================================

    @staticmethod
    def get_website_domain(
        website: str,
    ) -> str:

        parsed = urlparse(
            website.strip()
        )

        domain = parsed.netloc.lower()

        if not domain:
            raise ValueError(
                "Invalid company website."
            )

        if domain.startswith("www."):
            domain = domain[4:]

        return domain

    # ========================================================
    # EMAIL DOMAIN
    # ========================================================

    @staticmethod
    def get_email_domain(
        email: str,
    ) -> str:

        email = email.strip().lower()

        if "@" not in email:
            raise ValueError(
                "Invalid email address."
            )

        return email.split(
            "@",
            1,
        )[1]

    # ========================================================
    # VALIDATE OFFICIAL EMAIL
    # ========================================================

    @classmethod
    def validate_official_email(
        cls,
        website: str,
        admin_email: str,
    ) -> None:

        website_domain = (
            cls.get_website_domain(
                website
            )
        )

        email_domain = (
            cls.get_email_domain(
                admin_email
            )
        )

        blocked_domains = {
            "gmail.com",
            "googlemail.com",
            "yahoo.com",
            "yahoo.co.in",
            "outlook.com",
            "hotmail.com",
            "live.com",
            "icloud.com",
            "protonmail.com",
            "proton.me",
            "rediffmail.com",
        }

        if email_domain in blocked_domains:
            raise ValueError(
                "Please use an official company email address."
            )

        if email_domain != website_domain:
            raise ValueError(
                "Admin email must use the company's official domain."
            )

    # ========================================================
    # COMPANY ONBOARDING
    # ========================================================

    async def create_company(
        self,
        data: CompanyOnboardingCreate,
    ):

        # ====================================================
        # VALIDATE ADMIN OFFICIAL EMAIL
        # ====================================================

        self.validate_official_email(
            website=data.website,
            admin_email=str(
                data.admin_official_email
            ),
        )

        # ====================================================
        # FIND EXISTING COMPANY
        # ====================================================

        company_result = await self.session.execute(
            select(Company).where(
                Company.name == data.name
            )
        )

        company = (
            company_result
            .scalar_one_or_none()
        )

        # ====================================================
        # COMPANY MUST ALREADY EXIST
        # ====================================================

        if company is None:
            raise ValueError(
                "Company profile not found. Please create the company first."
            )

        # ====================================================
        # CHECK WHETHER COMPANY ALREADY HAS ADMIN
        # ====================================================

        if company.admin_user_id is not None:
            raise ValueError(
                "This company already has a company admin."
            )

        # ====================================================
        # CHECK ADMIN EMAIL
        # ====================================================

        admin_email = str(
            data.admin_official_email
        ).lower()

        existing_user_result = await self.session.execute(
            select(User).where(
                User.email == admin_email
            )
        )

        existing_user = (
            existing_user_result
            .scalar_one_or_none()
        )

        if existing_user is not None:
            raise ValueError(
                "A user with this admin email already exists."
            )

        # ====================================================
        # UPDATE COMPANY INFORMATION
        # ====================================================

        company.industry = data.industry
        company.logo = data.logo
        company.website = data.website
        company.location = data.location
        company.size = data.size
        company.open_roles = data.open_roles
        company.about = data.about

        company.contact_role = (
            data.contact_role
        )

        # ====================================================
        # CREATE COMPANY ADMIN
        # ====================================================

        admin_user = User(
            name="",
            email=admin_email,

            password_hash=hash_password(
                data.password
            ),

            role="company_admin",

            company_id=company.id,

            is_active=True,

            is_verified=True,

            onboarded=True,
        )

        self.session.add(
            admin_user
        )

        # ====================================================
        # FLUSH USER
        # ====================================================

        await self.session.flush()

        # ====================================================
        # LINK ADMIN TO COMPANY
        # ====================================================

        company.admin_user_id = (
            admin_user.id
        )

        # ====================================================
        # COMMIT
        # ====================================================

        await self.session.commit()

        # ====================================================
        # REFRESH
        # ====================================================

        await self.session.refresh(
            company
        )

        await self.session.refresh(
            admin_user
        )

        return company, admin_user