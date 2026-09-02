from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)

from app.models.user import User

from app.repositories.user_repository import (
    UserRepository,
)

from app.schemas.user import UserCreate

from app.services.audit_log_service import (
    AuditLogService,
)


class AuthService:
    """
    Service responsible for authentication operations.
    """

    def __init__(
        self,
        session: AsyncSession,
    ):
        self.session = session

        self.repository = UserRepository(
            session
        )

        self.audit_service = AuditLogService(
            session
        )

    # ============================================================
    # REGISTER
    # ============================================================

    async def register(
        self,
        data: UserCreate,
    ) -> User:

        existing_email = (
            await self.repository.get_by_email(
                data.email
            )
        )

        if existing_email is not None:
            raise ValueError(
                "A user with this email already exists."
            )

        user = User(
            name=data.name,
            email=data.email,
            password_hash=hash_password(
                data.password
            ),
        )

        created_user = (
            await self.repository.create(
                user
            )
        )

        return created_user

    # ============================================================
    # AUTHENTICATE
    # ============================================================

    async def authenticate(
        self,
        email: str,
        password: str,
    ) -> User | None:

        user = await (
            self.repository.get_by_email(
                email
            )
        )

        if user is None:
            return None

        if not user.password_hash:
            return None

        if not verify_password(
            password,
            user.password_hash,
        ):
            return None

        if not user.is_active:
            return None

        # --------------------------------------------------------
        # LOGIN AUDIT
        # --------------------------------------------------------

        if user.company_id is not None:

            await self.audit_service.log_login(
                user
            )

            await self.session.commit()

        return user

    # ============================================================
    # CREATE TOKEN
    # ============================================================

    def create_token(
        self,
        user: User,
    ) -> str:

        return create_access_token(
            user.id
        )