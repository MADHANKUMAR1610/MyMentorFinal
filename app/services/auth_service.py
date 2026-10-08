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

from app.core.config import settings

from app.services.message_central import (
    MessageCentralService,
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

        # ========================================================
        # MESSAGE CENTRAL
        # ========================================================

        self.message_central = MessageCentralService(
            customer_id=settings.MESSAGECENTRAL_CUSTOMER_ID,
            email=settings.MESSAGECENTRAL_EMAIL,
            password=settings.MESSAGECENTRAL_PASSWORD,
            country=settings.MESSAGECENTRAL_COUNTRY,
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
    # NORMAL LOGIN
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

        if user.company_id is not None:

            await self.audit_service.log_login(
                user
            )

        await self.session.commit()

        await self.session.refresh(
            user
        )

        return user

    # ============================================================
    # CREATE JWT TOKEN
    # ============================================================

    def create_token(
        self,
        user: User,
    ) -> str:

        return create_access_token(
            user.id
        )

    # ============================================================
    # SEND OTP
    # ============================================================

    async def send_otp(
        self,
        phone: str,
    ) -> dict:

        result = await self.message_central.send_otp(
            phone
        )

        data = result.get(
            "data",
            {}
        )

        verification_id = data.get(
            "verificationId"
        )

        if not verification_id:
            raise ValueError(
                "Message Central did not return verification ID."
            )

        return {
            "success": True,
            "message": "OTP sent successfully.",
            "verification_id": str(
                verification_id
            ),
        }

    # ============================================================
    # VERIFY OTP
    # ============================================================

    async def verify_otp(
        self,
        phone: str,
        verification_id: str,
        otp: str,
    ) -> dict:

        # --------------------------------------------------------
        # VERIFY WITH MESSAGE CENTRAL
        # --------------------------------------------------------

        result = await self.message_central.verify_otp(
            verification_id=verification_id,
            otp=otp,
        )

        print(
            "AuthService OTP result:",
            result,
        )

        # --------------------------------------------------------
        # SAFETY CHECK
        # --------------------------------------------------------

        if not result:
            raise RuntimeError(
                "Message Central returned an empty verification response."
            )

        # --------------------------------------------------------
        # READ DATA
        # --------------------------------------------------------

        data = result.get(
            "data"
        )

        if not data:
            return {
                "success": False,
                "message": (
                    result.get(
                        "message",
                        "OTP verification failed.",
                    )
                ),
            }

        verification_status = data.get(
            "verificationStatus"
        )

        error_message = data.get(
            "errorMessage"
        )

        # --------------------------------------------------------
        # OTP FAILED
        # --------------------------------------------------------

        if (
            result.get("responseCode") != 200
            or verification_status
            != "VERIFICATION_COMPLETED"
        ):

            return {
                "success": False,
                "message": (
                    error_message
                    or "Invalid or expired OTP."
                ),
            }

        # --------------------------------------------------------
        # NORMALIZE PHONE
        # --------------------------------------------------------

        phone = phone.strip()

        phone = phone.replace(
            " ",
            "",
        ).replace(
            "-",
            "",
        )

        if phone.startswith("+91"):
            phone = phone[3:]

        elif (
            phone.startswith("91")
            and len(phone) == 12
        ):
            phone = phone[2:]

        # --------------------------------------------------------
        # FIND USER
        # --------------------------------------------------------

        user = await self.repository.get_by_phone(
            phone
        )

        # --------------------------------------------------------
        # CREATE NEW USER
        # --------------------------------------------------------

        if user is None:

            user = User(
                phone=phone,
                name="",
                is_verified=True,
                is_active=True,
            )

            user = await self.repository.create(
                user
            )

        # --------------------------------------------------------
        # EXISTING USER
        # --------------------------------------------------------

        else:

            user.is_verified = True

        # --------------------------------------------------------
        # SAVE
        # --------------------------------------------------------

        await self.session.commit()

        await self.session.refresh(
            user
        )

        # --------------------------------------------------------
        # CREATE JWT
        # --------------------------------------------------------

        access_token = self.create_token(
            user
        )

        # --------------------------------------------------------
        # SUCCESS
        # --------------------------------------------------------

        return {
            "success": True,
            "message": "OTP verified successfully.",
            "access_token": access_token,
            "token_type": "bearer",
            "user_id": str(
                user.id
            ),
            "phone": user.phone,
        }