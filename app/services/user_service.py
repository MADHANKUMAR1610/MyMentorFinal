from uuid import UUID

from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from app.models.user import User

from app.repositories.user_repository import (
    UserRepository,
)

from app.services.audit_log_service import (
    AuditLogService,
)


class UserService:

    def __init__(
        self,
        session: AsyncSession,
    ):

        self.session = session

        self.repository = UserRepository(
            session
        )

        self.audit_service = (
            AuditLogService(session)
        )

    # ============================================================
    # GET USER BY ID
    # ============================================================

    async def get_by_id(
        self,
        user_id: UUID,
    ) -> User | None:

        return await self.repository.get_by_id(
            user_id
        )

    # ============================================================
    # GET USER BY EMAIL
    # ============================================================

    async def get_by_email(
        self,
        email: str,
    ) -> User | None:

        return await self.repository.get_by_email(
            email
        )

    # ============================================================
    # GET USER BY PHONE
    # ============================================================

    async def get_by_phone(
        self,
        phone: str,
    ) -> User | None:

        return await self.repository.get_by_phone(
            phone
        )

    # ============================================================
    # CREATE USER
    # ============================================================

    async def create_user(
        self,
        user: User,
        *,
        performed_by_user_id: UUID | None = None,
        performed_by_name: str | None = None,
    ) -> User:

        created_user = await (
            self.repository.create(
                user
            )
        )

        if (
            created_user.company_id is not None
            and performed_by_user_id is not None
        ):

            await self.audit_service.log_user_created(
                company_id=created_user.company_id,
                performed_by_user_id=performed_by_user_id,
                performed_by_name=(
                    performed_by_name
                    or "System"
                ),
                created_user=created_user,
            )

            await self.session.commit()

        return created_user

    # ============================================================
    # UPDATE USER
    # ============================================================

    async def update_user(
        self,
        user: User,
        *,
        changed_fields: dict | None = None,
        performed_by_user_id: UUID | None = None,
        performed_by_name: str | None = None,
    ) -> User:

        updated_user = await (
            self.repository.update(
                user
            )
        )

        if (
            changed_fields
            and user.company_id is not None
            and performed_by_user_id is not None
        ):

            await self.audit_service.log_user_updated(
                company_id=user.company_id,
                performed_by_user_id=performed_by_user_id,
                performed_by_name=(
                    performed_by_name
                    or user.name
                ),
                updated_user=updated_user,
                changed_fields=changed_fields,
            )

            await self.session.commit()

        return updated_user

    # ============================================================
    # DELETE USER
    # ============================================================

    async def delete_user(
        self,
        user: User,
        *,
        performed_by_user_id: UUID | None = None,
        performed_by_name: str | None = None,
    ) -> None:

        # --------------------------------------------------------
        # AUDIT BEFORE DELETE
        # --------------------------------------------------------

        if (
            user.company_id is not None
            and performed_by_user_id is not None
        ):

            await self.audit_service.log_user_deleted(
                company_id=user.company_id,
                performed_by_user_id=performed_by_user_id,
                performed_by_name=(
                    performed_by_name
                    or "System"
                ),
                deleted_user_id=user.id,
            )

        await self.repository.delete(
            user
        )

        await self.session.commit()

    # ============================================================
    # GET ALL STUDENTS WITH PROGRESS
    # ============================================================

    async def get_students_with_progress(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
    ):

        return await (
            self.repository
            .get_students_with_progress(
                skip=skip,
                limit=limit,
            )
        )

    # ============================================================
    # GET STUDENT STREAK
    # ============================================================

    async def get_student_streak(
        self,
        user_id: UUID,
    ) -> int:

        return await (
            self.repository
            .get_student_streak(
                user_id
            )
        )