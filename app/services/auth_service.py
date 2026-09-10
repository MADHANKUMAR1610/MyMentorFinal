from datetime import date, timedelta

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
    # UPDATE DAILY LOGIN STREAK
    # ============================================================

    async def update_login_streak(
        self,
        user: User,
    ) -> None:
        """
        Update daily login streak.

        Rules:
        - First login                  -> 1
        - Login again same day         -> unchanged
        - Login on consecutive day    -> +1
        - Miss one or more days        -> reset to 1
        """

        # Current date as string because
        # users.last_active is VARCHAR.
        today = date.today()

        today_str = today.isoformat()

        yesterday_str = (
            today - timedelta(days=1)
        ).isoformat()

        # ========================================================
        # FIRST LOGIN
        # ========================================================

        if not user.last_active:

            user.streak = 1
            user.last_active = today_str

        else:

            # Always compare as string
            last_active = str(
                user.last_active
            )

            # ====================================================
            # ALREADY LOGGED IN TODAY
            # ====================================================

            if last_active == today_str:

                # Don't increase streak.
                pass

            # ====================================================
            # LOGGED IN YESTERDAY
            # ====================================================

            elif last_active == yesterday_str:

                user.streak = (
                    user.streak or 0
                ) + 1

                user.last_active = today_str

            # ====================================================
            # MISSED ONE OR MORE DAYS
            # ====================================================

            else:

                user.streak = 1
                user.last_active = today_str

    # ============================================================
    # AUTHENTICATE
    # ============================================================

    async def authenticate(
        self,
        email: str,
        password: str,
    ) -> User | None:

        # --------------------------------------------------------
        # GET USER
        # --------------------------------------------------------

        user = await (
            self.repository.get_by_email(
                email
            )
        )

        if user is None:
            return None

        # --------------------------------------------------------
        # PASSWORD CHECK
        # --------------------------------------------------------

        if not user.password_hash:
            return None

        if not verify_password(
            password,
            user.password_hash,
        ):
            return None

        # --------------------------------------------------------
        # ACTIVE USER CHECK
        # --------------------------------------------------------

        if not user.is_active:
            return None

        # ========================================================
        # UPDATE DAILY LOGIN STREAK
        # ========================================================

        await self.update_login_streak(
            user
        )

        # ========================================================
        # LOGIN AUDIT
        # ========================================================

        if user.company_id is not None:

            await self.audit_service.log_login(
                user
            )

        # ========================================================
        # SAVE EVERYTHING
        # ========================================================

        await self.session.commit()

        await self.session.refresh(
            user
        )

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