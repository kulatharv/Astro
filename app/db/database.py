from collections.abc import Generator
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker, Session

from app.core.config import settings

# Configure SQLite vs PostgreSQL engine options
if settings.database_url.startswith("sqlite"):
    engine = create_engine(
        settings.database_url,
        connect_args={"check_same_thread": False},
        future=True,
    )
else:
    engine = create_engine(
        settings.database_url,
        pool_pre_ping=True,
        pool_size=settings.database_pool_size,
        max_overflow=settings.database_max_overflow,
        pool_recycle=settings.database_pool_recycle_seconds,
        future=True,
    )

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=Session,
    expire_on_commit=False,
    future=True,
)

Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency for creating and closing a database session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Initialize all tables in the database, add missing columns, and seed initial admin user if empty."""
    from app import models  # noqa: F401
    Base.metadata.create_all(bind=engine)

    # Safely migrate existing tables if missing columns
    try:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE blogs ADD COLUMN language VARCHAR(10) DEFAULT 'en'"))
    except Exception:
        pass

    try:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE users ADD COLUMN preferred_language VARCHAR(10) DEFAULT 'en'"))
    except Exception:
        pass

    db = SessionLocal()
    try:
        from app.models.admin import AdminUser
        from app.core.security import hash_password
        admin_exists = db.query(AdminUser).first()
        if not admin_exists:
            initial_password = hash_password("AdminSecurePassword2026!")
            admin = AdminUser(
                username="admin",
                password_hash=initial_password,
                email="admin@astrologic.ai",
                is_active=True,
            )
            db.add(admin)
            db.commit()
    except Exception:
        db.rollback()
    finally:
        db.close()
