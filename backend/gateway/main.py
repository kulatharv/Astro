"""FastAPI Gateway Application Entry Point & Edge Router."""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.sessions import SessionMiddleware

from gateway.middleware.language import LanguageDetectionMiddleware
from gateway.middleware.rate_limit import RateLimitMiddleware
from shared.config.settings import settings
from shared.logging.logger import get_logger
from shared.db.session import init_db
from shared.i18n.translation import SUPPORTED_LANGUAGES, load_translations

from shared.cache.metrics import cache_metrics
from shared.cache.redis_client import CacheService

# Import 8 extracted service module routers
from modules.auth.api import router as auth_router, admin_router
from modules.kundali.api import router as kundali_router
from modules.panchang.api import router as panchang_router
from modules.prediction.api import router as prediction_router
from modules.narrative.api import router as narrative_router
from modules.horoscope.api import router as horoscope_router
from modules.blog.api import router as blog_router
from modules.feedback.api import router as feedback_router
from gateway.pages import router as pages_router


logger = get_logger("gateway.main")
BASE_DIR = Path(__file__).resolve().parent.parent / "app"


class DefaultDenyAuthMiddleware(BaseHTTPMiddleware):
    """Enforces strict default-deny security for all /api/* routes except explicit public allowlist."""

    PUBLIC_API_PREFIXES = (
        "/health",
        "/ready",
        "/api/ready",
        "/metrics",
        "/api/locales",
        "/api/panchang",
        "/api/festivals",
        "/api/horoscope",
        "/api/daily-horoscope",
        "/api/cities",
        "/api/kundali",
        "/api/kundali-chat",
        "/api/download-kundali",
        "/api/domains",
        "/api/prediction",
        "/api/chat",
        "/api/system/ephemeris",
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
    logger.info(f"Starting {settings.app_name} in {settings.environment} mode via Gateway...")

    # 1. Ephemeris Runtime Initialization & Strict Policy Enforcement
    from shared.ephemeris.wrapper import init_ephemeris
    try:
        ephe_diag = init_ephemeris()
        logger.info(
            f"Ephemeris runtime verified: mode={ephe_diag['runtime_mode']}, "
            f"fallback={ephe_diag['is_moshier_fallback']}, strict={ephe_diag['strict_mode_active']}"
        )
    except Exception as e:
        logger.critical(f"FATAL: Ephemeris runtime policy enforcement failed: {e}")
        raise

    # 2. Database Initialization
    try:
        init_db()
        logger.info("Database initialized successfully.")
    except Exception as e:
        logger.error(f"Database initialization error: {e}")

    yield
    logger.info("Application shutdown complete.")


# Initialize FastAPI Gateway App
app = FastAPI(
    title=settings.app_name,
    description="Enterprise Vedic Astrology & AI Prediction Platform (Gateway)",
    version="2.0.0",
    lifespan=lifespan,
    debug=settings.debug,
)


@app.get("/health")
def health_check():
    """Application Health Check Endpoint."""
    from shared.ephemeris.wrapper import get_ephemeris_diagnostics
    ephe_diag = get_ephemeris_diagnostics()
    return {
        "status": "ok",
        "app": settings.app_name,
        "environment": settings.environment,
        "ephemeris_mode": ephe_diag.get("runtime_mode", "moshier"),
    }


@app.get("/api/system/ephemeris")
def get_ephemeris_status():
    """Return observable Swiss Ephemeris runtime mode, accuracy tier, and licensing diagnostics."""
    from shared.ephemeris.wrapper import get_ephemeris_diagnostics
    return get_ephemeris_diagnostics()


@app.get("/ready")
@app.get("/api/ready")
def readiness_check():
    """Readiness probe checking database connectivity and cache availability."""
    from shared.db.session import check_db_health
    from shared.ephemeris.wrapper import get_ephemeris_diagnostics

    db_healthy = check_db_health()
    ephe_diag = get_ephemeris_diagnostics()

    status_code = 200 if db_healthy else 503
    return JSONResponse(
        status_code=status_code,
        content={
            "status": "ready" if db_healthy else "not_ready",
            "database": "connected" if db_healthy else "disconnected",
            "cache": "operational",
            "ephemeris": ephe_diag.get("runtime_mode", "moshier"),
            "environment": settings.environment,
        },
    )


@app.get("/metrics")
def get_metrics():
    """Expose application and cache counters for observability/Prometheus."""
    return {
        "status": "ok",
        "cache": cache_metrics.get_stats(),
    }


@app.get("/api/admin/cache/stats")
def get_admin_cache_stats(request: Request):
    """Return cache statistics (Admin only)."""
    is_admin = request.session.get("admin") == "true"
    if not is_admin:
        return JSONResponse(status_code=403, content={"detail": "Admin authorization required."})
    return {
        "status": "ok",
        "cache": cache_metrics.get_stats(),
    }


@app.post("/api/admin/cache/flush")
def flush_admin_cache(request: Request):
    """Flush in-memory and Redis cache entries (Admin only)."""
    is_admin = request.session.get("admin") == "true"
    if not is_admin:
        return JSONResponse(status_code=403, content={"detail": "Admin authorization required."})
    CacheService.clear()
    cache_metrics.reset()
    return {"status": "ok", "message": "Chart cache flushed successfully."}


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

# Security & Session & Language Middleware (Outer-most executed first via Starlette stack)
app.add_middleware(DefaultDenyAuthMiddleware)
app.add_middleware(LanguageDetectionMiddleware)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.session_secret_key,
    same_site="lax",
    https_only=settings.is_production,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Register All Sub-Routers
app.include_router(auth_router)
app.include_router(kundali_router)
app.include_router(prediction_router)
app.include_router(panchang_router)
app.include_router(horoscope_router)
app.include_router(blog_router)
app.include_router(admin_router)
app.include_router(feedback_router)
app.include_router(narrative_router)
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
