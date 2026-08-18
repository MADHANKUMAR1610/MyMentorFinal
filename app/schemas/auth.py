from pydantic import BaseModel, EmailStr, Field


class SignupRequest(BaseModel):
    """
    Register a new user.
    """

    name: str = Field(
        min_length=2,
        max_length=150,
    )

    email: EmailStr

    password: str = Field(
        min_length=8,
        max_length=128,
    )


class LoginRequest(BaseModel):
    """
    Login using email and password.
    """

    email: EmailStr

    password: str = Field(
        min_length=8,
        max_length=128,
    )


class TokenResponse(BaseModel):
    """
    JWT authentication response.
    """

    access_token: str

    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    """
    Request a new access token.
    """

    refresh_token: str


class MessageResponse(BaseModel):
    """
    Generic API message response.
    """

    message: str