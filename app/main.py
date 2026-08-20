from pathlib import Path
import traceback

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from fastapi.staticfiles import StaticFiles

from app.api.routes.router import api_router
from app.api.routes.career_calendar import (
    router as career_calendar_router,
)
from app.core.config import settings


# ============================================================
# STORAGE DIRECTORY
# ============================================================

storage_path = Path(settings.STORAGE_LOCAL_PATH)

storage_path.mkdir(
    parents=True,
    exist_ok=True,
)


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="MyMentor API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)


# ============================================================
# GLOBAL EXCEPTION HANDLER
# ============================================================

@app.exception_handler(Exception)
async def global_exception_handler(
    request: Request,
    exc: Exception,
):
    print("\n" + "=" * 80)
    print("🔥 INTERNAL SERVER ERROR")
    print("=" * 80)
    print(f"Request: {request.method} {request.url}")
    print(f"Error: {exc}")
    print("\nFULL TRACEBACK:")
    traceback.print_exc()
    print("=" * 80 + "\n")

    return PlainTextResponse(
        content=f"Internal Server Error\n\n{exc}",
        status_code=500,
    )


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# API ROUTES
# ============================================================

app.include_router(
    api_router,
    prefix="/api",
)


# ============================================================
# CAREER CALENDAR ROUTES
# ============================================================

app.include_router(
    career_calendar_router,
    prefix="/api",
)


# ============================================================
# STATIC FILE STORAGE
# ============================================================

app.mount(
    "/uploads",
    StaticFiles(directory=str(storage_path)),
    name="uploads",
)


# ============================================================
# ROOT
# ============================================================

@app.get("/")
async def root():
    return {
        "message": "MyMentor API is running",
        "version": settings.APP_VERSION,
    }


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
async def health():
    return {
        "status": "healthy",
    }