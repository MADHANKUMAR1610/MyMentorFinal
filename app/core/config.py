from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    APP_NAME: str = "MyMentor API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
        # Code Execution
    CODE_EXECUTION_URL: str = (
        "https://ce.judge0.com"
    )

    CODE_EXECUTION_API_KEY: str | None = None
    DATABASE_URL: str

    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080

    CORS_ORIGINS: str = (
    "http://localhost:3000,"
    "https://careercampus-bd89.onrender.com"
)
    FRONTEND_URL: str = "https://careercampus-bd89.onrender.com"
    
    # Google OAuth
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    GOOGLE_REDIRECT_URI: str

    # Gemini AI
    GEMINI_API_KEY: str

    # File Storage
    STORAGE_TYPE: str = "local"
    STORAGE_LOCAL_PATH: str = "storage/uploads"
    PUBLIC_BASE_URL: str = "http://localhost:8000"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10 MB

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    @property
    def cors_origins_list(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.CORS_ORIGINS.split(",")
            if origin.strip()
        ]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()