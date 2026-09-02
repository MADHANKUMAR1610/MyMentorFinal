import uuid
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog
from app.models.user import User
from app.repositories.audit_log_repository import (
    AuditLogRepository,
)


class AuditLogService:

    def __init__(
        self,
        session: AsyncSession,
    ):
        self.repository = AuditLogRepository(
            session
        )

    # ============================================================
    # GENERIC CREATE
    # ============================================================

    async def create_log(
        self,
        *,
        company_id: UUID,
        user_id: UUID | None,
        user: str | None,
        action: str,
        entity: str,
        entity_id: UUID | None = None,
        info: str | None = None,
    ) -> AuditLog:

        audit_log = AuditLog(
            id=uuid.uuid4(),
            company_id=company_id,
            user_id=user_id,
            user=user,
            action=action,
            entity=entity,
            entity_id=entity_id,
            info=info,
            created_at=datetime.now(
                timezone.utc
            ),
        )

        return await self.repository.create_log(
            audit_log
        )

    # ============================================================
    # LOGIN
    # ============================================================

    async def log_login(
        self,
        user: User,
    ) -> AuditLog | None:

        if user.company_id is None:
            return None

        return await self.create_log(
            company_id=user.company_id,
            user_id=user.id,
            user=user.name,
            action="login",
            entity="user",
            entity_id=user.id,
            info=None,
        )

    # ============================================================
    # LOGOUT
    # ============================================================

    async def log_logout(
        self,
        user: User,
    ) -> AuditLog | None:

        if user.company_id is None:
            return None

        return await self.create_log(
            company_id=user.company_id,
            user_id=user.id,
            user=user.name,
            action="logout",
            entity="user",
            entity_id=user.id,
            info=None,
        )

    # ============================================================
    # USER CREATED
    # ============================================================

    async def log_user_created(
        self,
        *,
        company_id: UUID,
        performed_by_user_id: UUID,
        performed_by_name: str,
        created_user: User,
    ) -> AuditLog:

        return await self.create_log(
            company_id=company_id,
            user_id=performed_by_user_id,
            user=performed_by_name,
            action="user_created",
            entity="user",
            entity_id=created_user.id,
            info=f"role={created_user.role}",
        )

    # ============================================================
    # USER UPDATED
    # ============================================================

    async def log_user_updated(
        self,
        *,
        company_id: UUID,
        performed_by_user_id: UUID,
        performed_by_name: str,
        updated_user: User,
        changed_fields: dict,
    ) -> AuditLog:

        return await self.create_log(
            company_id=company_id,
            user_id=performed_by_user_id,
            user=performed_by_name,
            action="user_updated",
            entity="user",
            entity_id=updated_user.id,
            info=str(changed_fields),
        )

    # ============================================================
    # USER DELETED
    # ============================================================

    async def log_user_deleted(
        self,
        *,
        company_id: UUID,
        performed_by_user_id: UUID,
        performed_by_name: str,
        deleted_user_id: UUID,
    ) -> AuditLog:

        return await self.create_log(
            company_id=company_id,
            user_id=performed_by_user_id,
            user=performed_by_name,
            action="user_deleted",
            entity="user",
            entity_id=deleted_user_id,
            info=None,
        )

    # ============================================================
    # PASSWORD RESET REQUESTED
    # ============================================================

    async def log_password_reset_requested(
        self,
        user: User,
        *,
        performed_by_user_id: UUID | None = None,
        performed_by_name: str | None = None,
    ) -> AuditLog | None:

        if user.company_id is None:
            return None

        actor_id = (
            performed_by_user_id
            if performed_by_user_id is not None
            else user.id
        )

        actor_name = (
            performed_by_name
            if performed_by_name is not None
            else user.name
        )

        return await self.create_log(
            company_id=user.company_id,
            user_id=actor_id,
            user=actor_name,
            action="password_reset_requested",
            entity="user",
            entity_id=user.id,
            info=None,
        )

    # ============================================================
    # GET COMPANY LOGS
    # ============================================================

    async def get_by_company_id(
        self,
        company_id: UUID,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[AuditLog]:

        return await self.repository.get_by_company_id(
            company_id,
            skip=skip,
            limit=limit,
        )

    # ============================================================
    # GET BY ID
    # ============================================================

    async def get_by_id(
        self,
        audit_log_id: UUID,
    ) -> AuditLog | None:

        return await self.repository.get_by_id(
            audit_log_id
        )

    # ============================================================
    # GET USER AUDIT LOGS
    # ============================================================

    async def get_user_audit_logs(
        self,
        company_id: UUID,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[AuditLog]:

        return await self.repository.get_user_audit_logs(
            company_id,
            skip=skip,
            limit=limit,
        )

    # ============================================================
    # GET LOGS BY USER
    # ============================================================

    async def get_by_user(
        self,
        company_id: UUID,
        user_id: UUID,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[AuditLog]:

        return await self.repository.get_by_user(
            company_id,
            user_id,
            skip=skip,
            limit=limit,
        )