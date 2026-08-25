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
from app.schemas.auth import LoginRequest, TokenResponse
from app.schemas.user import UserCreate, UserResponse
from app.services.auth_service import AuthService
from app.services.google_auth_service import GoogleAuthService

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
    session: AsyncSession = Depends(get_db),
):
    service = AuthService(session)

    try:
        user = await service.register(data)

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )

    return user


# ============================================================
# LOGIN
# ============================================================

@router.post(
    "/login",
    response_model=TokenResponse,
)
async def login(
    data: LoginRequest,
    session: AsyncSession = Depends(get_db),
):
    service = AuthService(session)

    user = await service.authenticate(
        email=data.email,
        password=data.password,
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    access_token = service.create_token(user)

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
    )


# ============================================================
# ADMIN LOGIN
# ============================================================

@router.post(
    "/admin/login",
    response_model=TokenResponse,
)
async def admin_login(
    data: LoginRequest,
    session: AsyncSession = Depends(get_db),
):
    service = AuthService(session)

    user = await service.authenticate(
        email=data.email,
        password=data.password,
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    if user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required.",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin account is inactive.",
        )

    access_token = service.create_token(user)

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
    )


# ============================================================
# CURRENT USER
# ============================================================

@router.get("/me")
async def get_me(
    current_user: User = Depends(get_current_user),
):
    return UserResponse.model_validate(current_user)


# ============================================================
# GOOGLE LOGIN
# ============================================================

# ============================================================
# GOOGLE LOGIN
# ============================================================

@router.get("/google")
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

    service = GoogleAuthService(None)

    google_url = service.get_authorization_url(
        state=frontend_url
    )

    return RedirectResponse(
        url=google_url,
        status_code=status.HTTP_302_FOUND,
    )


# ============================================================
# GOOGLE CALLBACK
# ============================================================

@router.get("/google/callback")
async def google_callback(
    code: str,
    state: str,
    session: AsyncSession = Depends(get_db),
):
    service = GoogleAuthService(session)

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
            exc,
        )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Google authentication failed.",
        )

    # --------------------------------------------------------
    # Validate frontend
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Redirect user to the frontend that started login
    # --------------------------------------------------------

    print(
        "Google login successful"
    )

    print(
        "Redirecting to:",
        frontend_url,
    )

    return RedirectResponse(
        url=(
            f"{frontend_url}"
            f"/auth/callback"
            f"?token={jwt_token}"
        ),
        status_code=status.HTTP_302_FOUND,
    )