from uuid import UUID

from fastapi import (
    HTTPException,
    status,
)

from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from app.repositories.organization_repository import (
    OrganizationRepository,
)

from app.repositories.organization_member_repository import (
    OrganizationMemberRepository,
)

from app.core.security import (
    hash_password,
)

from app.services.audit_log_service import (
    AuditLogService,
)


class OrganizationMemberService:

    def __init__(
        self,
        db: AsyncSession,
    ):

        self.db = db

        self.organization_repository = (
            OrganizationRepository(db)
        )

        self.member_repository = (
            OrganizationMemberRepository(db)
        )

        self.audit_service = (
            AuditLogService(db)
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

    # --------------------------------------------------------
        # FIND ORGANIZATION
    # --------------------------------------------------------

        organization = await (
            self.organization_repository
            .get_by_admin_user_id(
                user_id
            )
        )

        if organization is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    "Organization not found "
                    "for this user."
                ),
            )

    # --------------------------------------------------------
        # GET MEMBERS
    # --------------------------------------------------------

        members = await (
            self.member_repository
            .get_members_by_company_id(
                organization.id,
                skip=skip,
                limit=limit,
            )
        )

    # --------------------------------------------------------
        # GET LAST LOGIN FOR ALL MEMBERS
    # --------------------------------------------------------

        user_ids = [
            member.id
            for member in members
        ]

        last_logins = await (
            self.member_repository
            .get_last_logins(
                user_ids
            )
        )

    # --------------------------------------------------------
        # BUILD RESPONSE
    # --------------------------------------------------------

        result = []

        for member in members:

            result.append({
    "id": member.id,
    "company_id": member.company_id,
    "name": member.name,
    "email": member.email,
    "phone": member.phone,
    "role": member.role,
    "department": member.department,
    "designation": member.designation,
    "is_active": member.is_active,
    "is_verified": member.is_verified,
    "created_at": member.created_at,
    "updated_at": member.updated_at,
    "last_login": last_logins.get(member.id),
})

        return result

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
            .get_by_admin_user_id(
                user_id
            )
        )

        if organization is None:

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    "Organization not found "
                    "for this user."
                ),
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
                detail=(
                    "Organization member "
                    "not found."
                ),
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
        performed_by_name: str | None = None,
    ):

        # --------------------------------------------------------
        # FIND ORGANIZATION
        # --------------------------------------------------------

        organization = await (
            self.organization_repository
            .get_by_admin_user_id(
                user_id
            )
        )

        if organization is None:

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    "Organization not found "
                    "for this user."
                ),
            )

        # --------------------------------------------------------
        # CHECK EMAIL
        # --------------------------------------------------------

        existing_email = await (
            self.member_repository
            .get_user_by_email(
                email
            )
        )

        if existing_email is not None:

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "A user with this email "
                    "already exists."
                ),
            )

        # --------------------------------------------------------
        # CHECK PHONE
        # --------------------------------------------------------

        if phone:

            existing_phone = await (
                self.member_repository
                .get_user_by_phone(
                    phone
                )
            )

            if existing_phone is not None:

                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=(
                        "A user with this phone "
                        "number already exists."
                    ),
                )

        # --------------------------------------------------------
        # HASH PASSWORD
        # --------------------------------------------------------

        password_hash = hash_password(
            password
        )

        # --------------------------------------------------------
        # CREATE MEMBER
        # --------------------------------------------------------

        member = await (
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

        # --------------------------------------------------------
        # USER CREATED AUDIT
        # --------------------------------------------------------

        await self.audit_service.log_user_created(
            company_id=organization.id,
            performed_by_user_id=user_id,
            performed_by_name=(
                performed_by_name
                or "Organization Admin"
            ),
            created_user=member,
        )

        await self.db.commit()

        return member

    # ============================================================
    # UPDATE MEMBER
    # ============================================================

    async def update_member(
        self,
        user_id: UUID,
        member_id: UUID,
        data: dict,
        performed_by_name: str | None = None,
    ):

        member = await self.get_member(
            user_id,
            member_id,
        )

        changed_fields = {}

        # --------------------------------------------------------
        # EMAIL
        # --------------------------------------------------------

        if "email" in data:

            email = data["email"]

            if (
                email
                and email != member.email
            ):

                existing = await (
                    self.member_repository
                    .get_user_by_email(
                        email
                    )
                )

                if (
                    existing is not None
                    and existing.id
                    != member.id
                ):

                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail=(
                            "A user with this "
                            "email already exists."
                        ),
                    )

                changed_fields["email"] = email

        # --------------------------------------------------------
        # PHONE
        # --------------------------------------------------------

        if "phone" in data:

            phone = data["phone"]

            if (
                phone
                and phone != member.phone
            ):

                existing = await (
                    self.member_repository
                    .get_user_by_phone(
                        phone
                    )
                )

                if (
                    existing is not None
                    and existing.id
                    != member.id
                ):

                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail=(
                            "A user with this "
                            "phone number "
                            "already exists."
                        ),
                    )

                changed_fields["phone"] = phone

        # --------------------------------------------------------
        # OTHER FIELDS
        # --------------------------------------------------------

        for field, value in data.items():

            if value is None:
                continue

            old_value = getattr(
                member,
                field,
                None,
            )

            if old_value != value:

                if field not in changed_fields:
                    changed_fields[field] = value

                setattr(
                    member,
                    field,
                    value,
                )

        # --------------------------------------------------------
        # UPDATE
        # --------------------------------------------------------

        updated_member = await (
            self.member_repository
            .update(member)
        )

        # --------------------------------------------------------
        # AUDIT
        # --------------------------------------------------------

        if changed_fields:

            await self.audit_service.log_user_updated(
                company_id=member.company_id,
                performed_by_user_id=user_id,
                performed_by_name=(
                    performed_by_name
                    or "Organization Admin"
                ),
                updated_user=updated_member,
                changed_fields=changed_fields,
            )

            await self.db.commit()

        return updated_member

    # ============================================================
    # REMOVE MEMBER
    # ============================================================

    async def remove_member(
        self,
        user_id: UUID,
        member_id: UUID,
        performed_by_name: str | None = None,
    ):

        member = await self.get_member(
            user_id,
            member_id,
        )

        company_id = member.company_id

        # --------------------------------------------------------
        # AUDIT BEFORE DELETE
        # --------------------------------------------------------

        if company_id is not None:

            await self.audit_service.log_user_deleted(
                company_id=company_id,
                performed_by_user_id=user_id,
                performed_by_name=(
                    performed_by_name
                    or "Organization Admin"
                ),
                deleted_user_id=member.id,
            )

        # --------------------------------------------------------
        # DELETE
        # --------------------------------------------------------

        await (
            self.member_repository
            .delete(member)
        )

        return None

    # ============================================================
    # UPDATE ACTIVE STATUS
    # ============================================================

    async def update_member_status(
        self,
        user_id: UUID,
        member_id: UUID,
        is_active: bool,
        performed_by_name: str | None = None,
    ):

        member = await self.get_member(
            user_id,
            member_id,
        )

        old_status = member.is_active

        member.is_active = is_active

        updated_member = await (
            self.member_repository
            .update(member)
        )

        if old_status != is_active:

            await self.audit_service.log_user_updated(
                company_id=member.company_id,
                performed_by_user_id=user_id,
                performed_by_name=(
                    performed_by_name
                    or "Organization Admin"
                ),
                updated_user=updated_member,
                changed_fields={
                    "is_active": is_active
                },
            )

            await self.db.commit()

        return updated_member

    # ============================================================
    # RESET MEMBER PASSWORD
    # ============================================================

    async def reset_member_password(
        self,
        user_id: UUID,
        member_id: UUID,
        new_password: str,
        performed_by_name: str | None = None,
    ):

        company = await (
            self.organization_repository
            .get_by_admin_user_id(
                user_id
            )
        )

        if not company:

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    "Organization not found "
                    "for this user."
                ),
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
                detail=(
                    "Organization member "
                    "not found."
                ),
            )

        # --------------------------------------------------------
        # PREVENT SELF RESET
        # --------------------------------------------------------

        if member.id == user_id:

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "You cannot reset your own "
                    "password using this API"
                ),
            )

        # --------------------------------------------------------
        # PASSWORD HASH
        # --------------------------------------------------------

        password_hash = hash_password(
            new_password
        )

        # --------------------------------------------------------
        # UPDATE PASSWORD
        # --------------------------------------------------------

        updated_member = await (
            self.member_repository
            .update_password(
                member,
                password_hash,
            )
        )

        # --------------------------------------------------------
        # PASSWORD RESET REQUESTED AUDIT
        # --------------------------------------------------------

        await self.audit_service.log_password_reset(
            member,
            performed_by_user_id=user_id,
            performed_by_name=(
                performed_by_name
                or "Organization Admin"
            ),
        )

        await self.db.commit()

        return updated_member