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

    def __init__(
        self,
        db: AsyncSession,
    ):

        self.organization_repository = (
            OrganizationRepository(db)
        )

        self.member_repository = (
            OrganizationMemberRepository(db)
        )

    # ============================================================
    # GET MY MEMBERS
    # ============================================================

    async def get_my_members(
        self,
        user_id: UUID,
        *,
        skip: int = 0,
        limit: int = 100,
    ):

        organization = await (
            self.organization_repository
            .get_by_admin_user_id(user_id)
        )

        if organization is None:

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found for this user.",
            )

        return await (
            self.member_repository
            .get_members_by_company_id(
                organization.id,
                skip=skip,
                limit=limit,
            )
        )

    # ============================================================
    # GET MEMBER
    # ============================================================

    async def get_member(
        self,
        user_id: UUID,
        member_id: UUID,
    ):

        organization = await (
            self.organization_repository
            .get_by_admin_user_id(user_id)
        )

        if organization is None:

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found for this user.",
            )

        member = await (
            self.member_repository
            .get_member_by_id(
                member_id,
                organization.id,
            )
        )

        if member is None:

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization member not found.",
            )

        return member

    # ============================================================
    # CREATE MEMBER
    # ============================================================

    async def create_member(
        self,
        user_id: UUID,
        name: str,
        email: str,
        phone: str | None,
        department: str | None,
        designation: str | None,
        role: str,
        password: str,
    ):

        # --------------------------------------------------------
        # Find organization
        # --------------------------------------------------------

        organization = await (
            self.organization_repository
            .get_by_admin_user_id(user_id)
        )

        if organization is None:

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found for this user.",
            )

        # --------------------------------------------------------
        # Check email already exists
        # --------------------------------------------------------

        existing_email = await (
            self.member_repository
            .get_user_by_email(email)
        )

        if existing_email is not None:

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A user with this email already exists.",
            )

        # --------------------------------------------------------
        # Check phone already exists
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
        # Create user
        # --------------------------------------------------------

        return await (
            self.member_repository
            .create_member(
                name=name,
                email=email,
                phone=phone,
                department=department,
                designation=designation,
                role=role,
                password_hash=password_hash,
                company_id=organization.id,
            )
        )

    # ============================================================
    # UPDATE MEMBER
    # ============================================================

    async def update_member(
        self,
        user_id: UUID,
        member_id: UUID,
        data: dict,
    ):

        member = await self.get_member(
            user_id,
            member_id,
        )

        # --------------------------------------------------------
        # Check email uniqueness
        # --------------------------------------------------------

        if "email" in data:

            email = data["email"]

            if email and email != member.email:

                existing = await (
                    self.member_repository
                    .get_user_by_email(email)
                )

                if (
                    existing is not None
                    and existing.id != member.id
                ):

                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="A user with this email already exists.",
                    )

        # --------------------------------------------------------
        # Check phone uniqueness
        # --------------------------------------------------------

        if "phone" in data:

            phone = data["phone"]

            if phone and phone != member.phone:

                existing = await (
                    self.member_repository
                    .get_user_by_phone(phone)
                )

                if (
                    existing is not None
                    and existing.id != member.id
                ):

                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="A user with this phone number already exists.",
                    )

        # --------------------------------------------------------
        # Update fields
        # --------------------------------------------------------

        for field, value in data.items():

            if value is not None:

                setattr(
                    member,
                    field,
                    value,
                )

        return await (
            self.member_repository
            .update(member)
        )

    # ============================================================
    # REMOVE MEMBER
    # ============================================================

    async def remove_member(
        self,
        user_id: UUID,
        member_id: UUID,
    ):

        member = await self.get_member(
            user_id,
            member_id,
        )

        await (
            self.member_repository
            .delete(member)
        )

    # ============================================================
    # UPDATE ACTIVE STATUS
    # ============================================================

    async def update_member_status(
        self,
        user_id: UUID,
        member_id: UUID,
        is_active: bool,
    ):

        member = await self.get_member(
            user_id,
            member_id,
        )

        member.is_active = is_active

        return await (
            self.member_repository
            .update(member)
        )

    async def reset_member_password(
        self,
        user_id: UUID,
        member_id: UUID,
        new_password: str,
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

        member = await (
            self.member_repository
            .get_member_by_id(
                member_id,
                company.id,
            )
        )

        if not member:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization member not found",
            )

        # Prevent admin from resetting their own password
        if member.id == user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You cannot reset your own password using this API",
            )

        password_hash = hash_password(new_password)

        return await (
            self.member_repository
            .update_password(
                member,
                password_hash,
            )
        )