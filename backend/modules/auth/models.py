from typing import TYPE_CHECKING
from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from shared.db.session import Base

if TYPE_CHECKING:
    from modules.feedback.models import Feedback
    from modules.kundali.models import UserSavedChart


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False)
    email = Column(String(255), nullable=True, unique=True, index=True)
    phone = Column(String(32), nullable=True, unique=True, index=True)
    password_hash = Column(String(255), nullable=True)
    auth_provider = Column(String(32), default="email")  # 'google', 'whatsapp', 'email'
    provider_user_id = Column(String(255), nullable=True)
    preferred_language = Column(String(10), default="en")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login_at = Column(DateTime, nullable=True)

    profile = relationship(
        "UserProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    activities = relationship(
        "UserActivity",
        back_populates="user",
        passive_deletes=True,
    )
    feedback_items = relationship(
        "Feedback",
        back_populates="user",
        passive_deletes=True,
    )
    saved_charts = relationship(
        "UserSavedChart",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    phone = Column(String(32), nullable=True)
    birth_date = Column(String(20), nullable=True)
    birth_time = Column(String(20), nullable=True)
    birth_city = Column(String(120), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    timezone_offset = Column(Float, default=5.5)
    tz_name = Column(String(64), default="Asia/Kolkata")
    birth_uncertainty = Column(String(20), default="exact")  # exact, approximate, uncertain
    zodiac_sign = Column(String(40), nullable=True)
    notes = Column(Text, nullable=True)
    
    # Daily WhatsApp briefing preferences
    whatsapp_number = Column(String(32), nullable=True)
    whatsapp_opt_in = Column(Boolean, default=False)
    whatsapp_time = Column(String(10), default="07:00")
    whatsapp_language = Column(String(10), default="en")

    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="profile")


class AdminUser(Base):
    __tablename__ = "admin_users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(120), nullable=False, unique=True, index=True)
    password_hash = Column(String(255), nullable=False)
    email = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class UserActivity(Base):
    __tablename__ = "user_activities"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    action = Column(String(80), nullable=False)
    details = Column(Text, nullable=True)
    ip_address = Column(String(64), nullable=True)
    user_agent = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    user = relationship("User", back_populates="activities")


class AuthOtp(Base):
    __tablename__ = "auth_otps"

    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String(32), nullable=False, index=True)
    otp_hash = Column(String(128), nullable=False)
    salt = Column(String(64), nullable=False)
    attempts = Column(Integer, default=0)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class GuestSession(Base):
    """
    Guest Session Cache for Zero-Cookie Retargeting and Ghost Session Recovery.
    Preserves calculated charts for unauthenticated visitors keyed by composite device fingerprint.
    """
    __tablename__ = "guest_sessions"

    id = Column(Integer, primary_key=True, index=True)
    device_fingerprint = Column(String(64), nullable=False, index=True)
    session_token = Column(String(64), nullable=False, unique=True, index=True)
    chart_type = Column(String(32), default="kundali")  # 'kundali', 'prediction', 'match'
    person_name = Column(String(120), nullable=True)
    birth_date = Column(String(20), nullable=True)
    birth_time = Column(String(20), nullable=True)
    birth_place = Column(String(120), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    timezone_offset = Column(Float, default=5.5)
    chart_payload = Column(Text, nullable=True)
    telemetry_data = Column(Text, nullable=True)
    is_claimed = Column(Boolean, default=False)
    claimed_by_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    expires_at = Column(DateTime, nullable=False)


