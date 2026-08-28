from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.organization_repository import (
    OrganizationRepository,
)
from app.repositories.organization_member_repository import (
    OrganizationMemberRepository,
)
from app.core.security import hash_password


class OrganizationMemberService:

    def __init__(self, db: AsyncSession):

        self.organization_repository = (
            OrganizationRepository(db)
        )

        self.member_repository = (
            OrganizationMemberRepository(db)
        )

    # ============================================================
    # GET MY ORGANIZATION MEMBERS
    # ============================================================

    async def get_my_members(
        self,
        user_id: UUID,
        *,
        skip: int = 0,
        limit: int = 100,
    ):

        company = await (
            self.organization_repository
            .get_by_admin_user_id(user_id)
        )

        if company is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found for this user.",
            )

        return await (
            self.member_repository
            .get_members_by_company_id(
                company.id,
                skip=skip,
                limit=limit,
            )
        )

    # ============================================================
    # GET SINGLE ORGANIZATION MEMBER
    # ============================================================

    async def get_member(
        self,
        user_id: UUID,
        member_id: UUID,
    ):

        company = await (
            self.organization_repository
            .get_by_admin_user_id(user_id)
        )

        if company is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found for this user.",
            )

        member = await (
            self.member_repository
            .get_member_by_id(
                user_id=member_id,
                company_id=company.id,
            )
        )

        if member is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization member not found.",
            )

        return member

    # ============================================================
    # CREATE ORGANIZATION MEMBER
    # ============================================================

    async def create_member(
        self,
        user_id: UUID,
        *,
        name: str,
        email: str,
        phone: str | None,
        password: str,
    ):

        # --------------------------------------------------------
        # Find organization of logged-in admin
        # --------------------------------------------------------

        company = await (
            self.organization_repository
            .get_by_admin_user_id(user_id)
        )

        if company is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found for this user.",
            )

        # --------------------------------------------------------
        # Check email
        # --------------------------------------------------------

        existing_user = await (
            self.member_repository
            .get_user_by_email(email)
        )

        if existing_user is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A user with this email already exists.",
            )

        # --------------------------------------------------------
        # Check phone
        # --------------------------------------------------------

        if phone:

            existing_phone = await (
                self.member_repository
                .get_user_by_phone(phone)
            )

            if existing_phone is not None:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="A user with this phone number already exists.",
                )

        # --------------------------------------------------------
        # Hash password
        # --------------------------------------------------------

        password_hash = hash_password(password)

        # --------------------------------------------------------
        # Create organization member
        # --------------------------------------------------------

        member = await (
            self.member_repository
            .create_member(
                name=name,
                email=email,
                phone=phone,
                password_hash=password_hash,
                company_id=company.id,
            )
        )

        return member

    # ============================================================
    # UPDATE ORGANIZATION MEMBER
    # ============================================================

    async def update_member(
        self,
        user_id: UUID,
        member_id: UUID,
        data: dict,
    ):

        company = await (
            self.organization_repository
            .get_by_admin_user_id(user_id)
        )

        if company is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found for this user.",
            )

        member = await (
            self.member_repository
            .get_member_by_id(
                user_id=member_id,
                company_id=company.id,
            )
        )

        if member is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization member not found.",
            )

        # --------------------------------------------------------
        # Protected fields
        # --------------------------------------------------------

        data.pop("company_id", None)
        data.pop("password", None)
        data.pop("password_hash", None)

        # --------------------------------------------------------
        # Update fields
        # --------------------------------------------------------

        for field, value in data.items():

            if value is not None:
                setattr(member, field, value)

        return await self.member_repository.update(
            member
        )

    # ============================================================
    # REMOVE ORGANIZATION MEMBER
    # ============================================================

    async def remove_member(
        self,
        user_id: UUID,
        member_id: UUID,
    ):

        company = await (
            self.organization_repository
            .get_by_admin_user_id(user_id)
        )

        if company is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found for this user.",
            )

        member = await (
            self.member_repository
            .get_member_by_id(
                user_id=member_id,
                company_id=company.id,
            )
        )

        if member is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization member not found.",
            )

        # --------------------------------------------------------
        # Protect organization admin
        # --------------------------------------------------------

        if company.admin_user_id == member.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Organization admin cannot be removed.",
            )

        # --------------------------------------------------------
        # Remove organization association
        # --------------------------------------------------------

        member.company_id = None

        return await self.member_repository.update(
            member
        )

    # ============================================================
    # UPDATE MEMBER ACTIVE STATUS
    # ============================================================

    async def update_member_status(
        self,
        user_id: UUID,
        member_id: UUID,
        is_active: bool,
    ):

        company = await (
            self.organization_repository
            .get_by_admin_user_id(user_id)
        )

        if company is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found for this user.",
            )

        member = await (
            self.member_repository
            .get_member_by_id(
                user_id=member_id,
                company_id=company.id,
            )
        )

        if member is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization member not found.",
            )

        # --------------------------------------------------------
        # Protect organization admin
        # --------------------------------------------------------

        if company.admin_user_id == member.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Organization admin status cannot be changed.",
            )

        member.is_active = is_active

        return await self.member_repository.update(
            member
        )