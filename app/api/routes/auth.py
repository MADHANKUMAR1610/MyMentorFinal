from fastapi import APIRouter, Depends, HTTPException, status
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

@router.get("/me")
async def get_me(
    current_user: User = Depends(get_current_user),
):
    return UserResponse.model_validate(current_user)


# ============================================================
# GOOGLE LOGIN
# ============================================================

@router.get("/google")
async def google_login():

    service = GoogleAuthService(None)

    authorization_url = service.get_authorization_url()

    return RedirectResponse(
        url=authorization_url,
        status_code=status.HTTP_307_TEMPORARY_REDIRECT,
    )


# ============================================================
# GOOGLE CALLBACK
# ============================================================

@router.get("/google/callback")
async def google_callback(
    code: str,
    session: AsyncSession = Depends(get_db),
):
    service = GoogleAuthService(session)

    try:
        user, jwt_token = await service.authenticate_with_code(code)

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )

    except Exception as exc:
        print("Google OAuth Error:", exc)

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Google authentication failed.",
        )

    return RedirectResponse(
        url=f"http://localhost:3000/auth/callback?token={jwt_token}",
        status_code=status.HTTP_302_FOUND,
    )

    # Redirect back to React frontend
    frontend_url = "http://localhost:3000"

    return RedirectResponse(
        url=f"{frontend_url}/auth/callback?token={jwt_token}",
        status_code=status.HTTP_302_FOUND,
    )