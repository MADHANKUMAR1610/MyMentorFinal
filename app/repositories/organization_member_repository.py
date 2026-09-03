from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog
from app.models.user import User


class OrganizationMemberRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    # ============================================================
    # GET ALL MEMBERS
    # ============================================================

    async def get_members_by_company_id(
        self,
        company_id: UUID,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[User]:

        result = await self.db.execute(
            select(User)
            .where(
                User.company_id == company_id
            )
            .order_by(
                User.created_at.desc()
            )
            .offset(skip)
            .limit(limit)
        )

        return list(
            result.scalars().all()
        )

    # ============================================================
    # GET SINGLE MEMBER
    # ============================================================

    async def get_member_by_id(
        self,
        user_id: UUID,
        company_id: UUID,
    ) -> User | None:

        result = await self.db.execute(
            select(User).where(
                User.id == user_id,
                User.company_id == company_id,
            )
        )

        return result.scalar_one_or_none()

    # ============================================================
    # GET USER BY ID
    # ============================================================

    async def get_user_by_id(
        self,
        user_id: UUID,
    ) -> User | None:

        result = await self.db.execute(
            select(User).where(
                User.id == user_id
            )
        )

        return result.scalar_one_or_none()

    # ============================================================
    # GET USER BY EMAIL
    # ============================================================

    async def get_user_by_email(
        self,
        email: str,
    ) -> User | None:

        result = await self.db.execute(
            select(User).where(
                User.email == email
            )
        )

        return result.scalar_one_or_none()

    # ============================================================
    # GET USER BY PHONE
    # ============================================================

    async def get_user_by_phone(
        self,
        phone: str,
    ) -> User | None:

        result = await self.db.execute(
            select(User).where(
                User.phone == phone
            )
        )

        return result.scalar_one_or_none()

    # ============================================================
    # CREATE ORGANIZATION MEMBER
    # ============================================================

    async def create_member(
        self,
        *,
        name: str,
        email: str,
        phone: str | None,
        department: str | None,
        designation: str | None,
        role: str,
        password_hash: str,
        company_id: UUID,
    ) -> User:

        user = User(
            name=name,
            email=email,
            phone=phone,

            department=department,
            designation=designation,

            password_hash=password_hash,

            company_id=company_id,

            role=role,

            is_active=True,
            is_verified=False,
        )

        self.db.add(user)

        await self.db.commit()
        await self.db.refresh(user)

        return user

    # ============================================================
    # UPDATE MEMBER
    # ============================================================

    async def update(
        self,
        user: User,
    ) -> User:

        await self.db.commit()
        await self.db.refresh(user)

        return user

    # ============================================================
    # DELETE MEMBER
    # ============================================================

    async def delete(
        self,
        user: User,
    ) -> None:

        await self.db.delete(user)

        await self.db.commit()

    # ============================================================
    # UPDATE PASSWORD
    # ============================================================

    async def update_password(
        self,
        user: User,
        password_hash: str,
    ) -> User:

        user.password_hash = password_hash

        await self.db.commit()
        await self.db.refresh(user)

        return user

    # ============================================================
    # GET LAST LOGIN FOR MEMBERS
    # ============================================================

    async def get_last_logins(
        self,
        user_ids: list[UUID],
    ) -> dict[UUID, object]:

        if not user_ids:
            return {}

        result = await self.db.execute(
            select(
               AuditLog.user_id,
               AuditLog.created_at,
            )
            .where(
               AuditLog.user_id.in_(user_ids),
               AuditLog.action == "login",
            )
           .distinct(
               AuditLog.user_id
            )
            .order_by(
               AuditLog.user_id,
               AuditLog.created_at.desc(),
            )
        )

        rows = result.all()

        return {
            row.user_id: row.created_at
            for row in rows
        }