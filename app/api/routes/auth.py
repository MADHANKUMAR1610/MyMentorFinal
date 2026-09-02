from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.database.database import get_db
from app.models.user import User

from app.schemas.auth import (
    LoginRequest,
    TokenResponse,
    PasswordResetRequest,
)

from app.schemas.user import (
    UserCreate,
    UserResponse,
)

from app.services.auth_service import (
    AuthService,
)

from app.services.google_auth_service import (
    GoogleAuthService,
)

from app.services.audit_log_service import (
    AuditLogService,
)

from app.repositories.user_repository import (
    UserRepository,
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


# ============================================================
# REGISTER
# ============================================================

@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    data: UserCreate,
    session: AsyncSession = Depends(
        get_db
    ),
):

    service = AuthService(
        session
    )

    try:

        user = await service.register(
            data
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )

    return user


# ============================================================
# NORMAL LOGIN
# ============================================================

@router.post(
    "/login",
    response_model=TokenResponse,
)
async def login(
    data: LoginRequest,
    session: AsyncSession = Depends(
        get_db
    ),
):

    service = AuthService(
        session
    )

    user = await service.authenticate(
        email=data.email,
        password=data.password,
    )

    if user is None:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    if not user.is_active:

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive.",
        )

    access_token = (
        service.create_token(
            user
        )
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
    )


# ============================================================
# ADMIN LOGIN
# SYSTEM ADMIN + COMPANY ADMIN
# ============================================================

@router.post(
    "/admin/login",
    response_model=TokenResponse,
)
async def admin_login(
    data: LoginRequest,
    session: AsyncSession = Depends(
        get_db
    ),
):

    service = AuthService(
        session
    )

    user = await service.authenticate(
        email=data.email,
        password=data.password,
    )

    if user is None:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    if user.role not in {
        "admin",
        "company_admin",
        "organization_admin",
    }:

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required.",
        )

    if not user.is_active:

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin account is inactive.",
        )

    if (
        user.role in {
            "company_admin",
            "organization_admin",
        }
        and user.company_id is None
    ):

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Admin is not linked "
                "to a company."
            ),
        )

    access_token = (
        service.create_token(
            user
        )
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
    )


# ============================================================
# LOGOUT
# ============================================================

@router.post(
    "/logout",
)
async def logout(
    current_user: User = Depends(
        get_current_user
    ),
    session: AsyncSession = Depends(
        get_db
    ),
):

    audit_service = AuditLogService(
        session
    )

    if current_user.company_id is not None:

        await audit_service.log_logout(
            current_user
        )

        await session.commit()

    return {
        "message": "Logout successful."
    }


# ============================================================
# PASSWORD RESET REQUEST
# ============================================================

@router.post(
    "/password-reset/request",
)
async def request_password_reset(
    data: PasswordResetRequest,
    session: AsyncSession = Depends(
        get_db
    ),
):

    repository = UserRepository(
        session
    )

    user = await repository.get_by_email(
        data.email
    )

    # --------------------------------------------------------
    # SECURITY:
    # Do not reveal whether the email exists.
    # --------------------------------------------------------

    if user is not None:

        audit_service = AuditLogService(
            session
        )

        if user.company_id is not None:

            await audit_service.log_password_reset_requested(
                user
            )

            await session.commit()

    return {
        "message": (
            "If an account exists with this email, "
            "a password reset request has been recorded."
        )
    }


# ============================================================
# CURRENT USER
# ============================================================

@router.get(
    "/me"
)
async def get_me(
    current_user: User = Depends(
        get_current_user
    ),
):

    return UserResponse.model_validate(
        current_user
    )


# ============================================================
# GOOGLE LOGIN
# ============================================================

@router.get(
    "/google"
)
async def google_login(
    frontend_url: str = Query(...),
):

    allowed_frontends = {
        "http://localhost:3000",
        "https://careercampus-bd89.onrender.com",
    }

    if frontend_url not in allowed_frontends:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid frontend URL.",
        )

    service = GoogleAuthService(
        None
    )

    google_url = (
        service.get_authorization_url(
            state=frontend_url
        )
    )

    return RedirectResponse(
        url=google_url,
        status_code=status.HTTP_302_FOUND,
    )


# ============================================================
# GOOGLE CALLBACK
# ============================================================

@router.get(
    "/google/callback"
)
async def google_callback(
    code: str,
    state: str,
    session: AsyncSession = Depends(
        get_db
    ),
):

    service = GoogleAuthService(
        session
    )

    try:

        user, jwt_token = (
            await service.authenticate_with_code(
                code
            )
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )

    except Exception as exc:

        print(
            "Google OAuth Error:",
            exc
        )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Google authentication failed.",
        )

    allowed_frontends = {
        "http://localhost:3000",
        "https://careercampus-bd89.onrender.com",
    }

    if state not in allowed_frontends:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid OAuth redirect.",
        )

    frontend_url = state.rstrip("/")

    print(
        "Google login successful"
    )

    print(
        "Redirecting to:",
        frontend_url
    )

    return RedirectResponse(
        url=(
            f"{frontend_url}"
            f"/auth/callback"
            f"?token={jwt_token}"
        ),
        status_code=status.HTTP_302_FOUND,
    )