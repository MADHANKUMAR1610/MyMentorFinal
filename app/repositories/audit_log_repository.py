from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog
from app.repositories.base import BaseRepository


class AuditLogRepository(BaseRepository[AuditLog]):

    def __init__(
        self,
        session: AsyncSession,
    ):
        super().__init__(
            AuditLog,
            session,
        )

    # ============================================================
    # CREATE AUDIT LOG
    # ============================================================

    async def create_log(
        self,
        audit_log: AuditLog,
    ) -> AuditLog:

        return await self.create(
            audit_log
        )

    # ============================================================
    # GET ALL COMPANY AUDIT LOGS
    # ============================================================

    async def get_by_company_id(
        self,
        company_id: UUID,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[AuditLog]:

        result = await self.session.execute(
            select(AuditLog)
            .where(
                AuditLog.company_id == company_id
            )
            .order_by(
                AuditLog.created_at.desc()
            )
            .offset(skip)
            .limit(limit)
        )

        return list(
            result.scalars().all()
        )

    # ============================================================
    # GET AUDIT LOG BY ID
    # ============================================================

    async def get_by_id(
        self,
        audit_log_id: UUID,
    ) -> Optional[AuditLog]:

        result = await self.session.execute(
            select(AuditLog)
            .where(
                AuditLog.id == audit_log_id
            )
        )

        return result.scalar_one_or_none()

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

        result = await self.session.execute(
            select(AuditLog)
            .where(
                AuditLog.company_id == company_id,
                AuditLog.entity == "user",
            )
            .order_by(
                AuditLog.created_at.desc()
            )
            .offset(skip)
            .limit(limit)
        )

        return list(
            result.scalars().all()
        )

    # ============================================================
    # GET AUDIT LOGS BY USER
    # ============================================================

    async def get_by_user(
        self,
        company_id: UUID,
        user_id: UUID,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[AuditLog]:

        result = await self.session.execute(
            select(AuditLog)
            .where(
                AuditLog.company_id == company_id,
                AuditLog.user_id == user_id,
            )
            .order_by(
                AuditLog.created_at.desc()
            )
            .offset(skip)
            .limit(limit)
        )

        return list(
            result.scalars().all()
        )

    # ============================================================
    # GET AUDIT LOGS BY ENTITY
    # ============================================================

    async def get_by_entity(
        self,
        company_id: UUID,
        entity: str,
        entity_id: UUID,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[AuditLog]:

        result = await self.session.execute(
            select(AuditLog)
            .where(
                AuditLog.company_id == company_id,
                AuditLog.entity == entity,
                AuditLog.entity_id == entity_id,
            )
            .order_by(
                AuditLog.created_at.desc()
            )
            .offset(skip)
            .limit(limit)
        )

        return list(
            result.scalars().all()
        )