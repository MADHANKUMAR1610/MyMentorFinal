from urllib.parse import urlencode

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import create_access_token
from app.models.user import User
from app.repositories.user_repository import UserRepository


GOOGLE_AUTH_URL = (
    "https://accounts.google.com/o/oauth2/v2/auth"
)

GOOGLE_TOKEN_URL = (
    "https://oauth2.googleapis.com/token"
)

GOOGLE_USERINFO_URL = (
    "https://openidconnect.googleapis.com/v1/userinfo"
)


class GoogleAuthService:

    def __init__(
        self,
        session: AsyncSession,
    ):
        self.repository = UserRepository(session)

    # =========================================================
    # GOOGLE AUTHORIZATION URL
    # =========================================================

    def get_authorization_url(
        self,
        state: str,
    ) -> str:

        params = {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "response_type": "code",
            "scope": "openid email profile",
            "access_type": "offline",
            "prompt": "select_account",

            # IMPORTANT
            # This tells Google to return the frontend
            # URL back to our callback.
            "state": state,
        }

        return (
            f"{GOOGLE_AUTH_URL}"
            f"?{urlencode(params)}"
        )

    # =========================================================
    # GOOGLE CALLBACK / AUTHENTICATION
    # =========================================================

    async def authenticate_with_code(
        self,
        code: str,
    ) -> tuple[User, str]:

        async with httpx.AsyncClient(
            timeout=15.0
        ) as client:

            # -------------------------------------------------
            # Exchange Google authorization code for token
            # -------------------------------------------------

            token_response = await client.post(
                GOOGLE_TOKEN_URL,
                data={
                    "code": code,
                    "client_id": settings.GOOGLE_CLIENT_ID,
                    "client_secret": (
                        settings.GOOGLE_CLIENT_SECRET
                    ),
                    "redirect_uri": (
                        settings.GOOGLE_REDIRECT_URI
                    ),
                    "grant_type": "authorization_code",
                },
            )

            token_response.raise_for_status()

            token_data = token_response.json()

            access_token = token_data.get(
                "access_token"
            )

            if not access_token:
                raise ValueError(
                    "Google did not return an access token."
                )

            # -------------------------------------------------
            # Get Google user information
            # -------------------------------------------------

            userinfo_response = await client.get(
                GOOGLE_USERINFO_URL,
                headers={
                    "Authorization": (
                        f"Bearer {access_token}"
                    ),
                },
            )

            userinfo_response.raise_for_status()

            google_user = userinfo_response.json()

        # -----------------------------------------------------
        # Extract Google user information
        # -----------------------------------------------------

        google_id = google_user.get("sub")

        email = google_user.get("email")

        name = google_user.get("name") or ""

        if not google_id:
            raise ValueError(
                "Google account ID was not returned."
            )

        if not email:
            raise ValueError(
                "Google account email was not returned."
            )

        # -----------------------------------------------------
        # Find existing user
        # -----------------------------------------------------

        user = await self.repository.get_by_google_id(
            google_id
        )

        if user is None:
            user = await self.repository.get_by_email(
                email
            )

        # -----------------------------------------------------
        # Create new Google user
        # -----------------------------------------------------

        if user is None:

            user = User(
                google_id=google_id,
                email=email,
                name=name,
                password_hash=None,
                is_verified=True,
            )

            user = await self.repository.create(
                user
            )

        # -----------------------------------------------------
        # Update existing user
        # -----------------------------------------------------

        else:

            if user.google_id is None:
                user.google_id = google_id

            if not user.name and name:
                user.name = name

            user.is_verified = True

            user = await self.repository.update(
                user
            )

        # -----------------------------------------------------
        # Create MyMentor JWT
        # -----------------------------------------------------

        jwt_token = create_access_token(
            user.id
        )

        return user, jwt_token