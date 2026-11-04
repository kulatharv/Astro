"""FastAPI Application Entry Point & Server Bootstrap."""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.sessions import SessionMiddleware

from app.api.middleware.language import LanguageDetectionMiddleware
from app.api.routes import (
    admin_router,
    auth_router,
    blogs_router,
    feedback_router,
    horoscope_router,
    kundali_router,
    pages_router,
    panchang_router,
    prediction_router,
)
from app.core.config import settings
from app.core.logger import get_logger
from app.db.database import init_db
from app.services.translation_service import SUPPORTED_LANGUAGES, load_translations

logger = get_logger("app.main")
BASE_DIR = Path(__file__).resolve().parent


class DefaultDenyAuthMiddleware(BaseHTTPMiddleware):
    """Enforces strict default-deny security for all /api/* routes except explicit public allowlist."""

    PUBLIC_API_PREFIXES = (
        "/health",
        "/api/locales",
        "/api/panchang",
        "/api/festivals",
        "/api/horoscope",
        "/api/daily-horoscope",
        "/api/cities",
        "/api/kundali",
        "/api/kundali-chat",
        "/api/download-kundali",
        "/api/auth/login",
        "/api/auth/signup",
        "/api/auth/logout",
    )

    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        # Non-API routes (HTML pages, static files, docs) are allowed
        if not path.startswith("/api/"):
            return await call_next(request)

        # Public API routes allowed without authentication
        if any(path.startswith(prefix) for prefix in self.PUBLIC_API_PREFIXES):
            return await call_next(request)

        # Public GET endpoints for blogs
        if path.startswith("/api/blogs") and request.method == "GET":
            return await call_next(request)

        # Default-deny authorization check for all other API endpoints
        user_id = request.session.get("user_id")
        is_admin = request.session.get("admin") == "true"

        if not user_id and not is_admin:
            return JSONResponse(
                status_code=401,
                content={"detail": "Authentication required. Default-deny policy enforced."},
            )

        return await call_next(request)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for application startup and shutdown."""
    logger.info(f"Starting {settings.app_name} in {settings.environment} mode...")
    try:
        init_db()
        logger.info("Database initialized successfully.")
    except Exception as e:
        logger.error(f"Database initialization error: {e}")
    yield
    logger.info("Application shutdown complete.")


# Initialize FastAPI App
app = FastAPI(
    title=settings.app_name,
    description="Enterprise Vedic Astrology & AI Prediction Platform",
    version="2.0.0",
    lifespan=lifespan,
    debug=settings.debug,
)


@app.get("/health")
def health_check():
    """Application Health Check Endpoint."""
    return {"status": "ok", "app": settings.app_name, "environment": settings.environment}


@app.get("/api/locales/{lang}")
def get_locale_translations(lang: str):
    """Return JSON translation dictionary for client-side i18n dynamic switching."""
    translations = load_translations(lang)
    return {
        "lang": lang,
        "supported_languages": SUPPORTED_LANGUAGES,
        "translations": translations,
    }


# Set up Template Engine and Static Directory
static_dir = BASE_DIR / "static"
templates_dir = BASE_DIR / "templates"

if static_dir.exists():
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

templates = Jinja2Templates(directory=str(templates_dir))
app.state.templates = templates

# Security & Session & Language Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(LanguageDetectionMiddleware)
app.add_middleware(DefaultDenyAuthMiddleware)

app.add_middleware(
    SessionMiddleware,
    secret_key=settings.session_secret_key,
    same_site="lax",
    https_only=settings.is_production,
)

# Register All Sub-Routers (API routers included before pages_router)
app.include_router(auth_router)
app.include_router(kundali_router)
app.include_router(prediction_router)
app.include_router(panchang_router)
app.include_router(horoscope_router)
app.include_router(blogs_router)
app.include_router(admin_router)
app.include_router(feedback_router)
app.include_router(pages_router)


# Global Exception Handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception on {request.url.path}: {exc}", exc_info=True)
    if request.url.path.startswith("/api/"):
        return JSONResponse(
            status_code=500,
            content={"detail": "An internal error occurred. Please verify inputs or try again."},
        )
    # Return friendly error on web pages if needed
    return JSONResponse(
        status_code=500,
        content={"detail": "Something went wrong. Please check your request."},
    )
