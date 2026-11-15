from datetime import datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text, Boolean
from sqlalchemy.orm import relationship
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False)
    email = Column(String(255), nullable=False, unique=True, index=True)
    password_hash = Column(String(255), nullable=False)
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
    preferred_language = Column(
        String(10),
        default="en"
    )

class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
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


class UserActivity(Base):
    __tablename__ = "user_activities"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    action = Column(String(80), nullable=False)
    details = Column(Text)
    ip_address = Column(String(64))
    user_agent = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="activities")


class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    module = Column(String(40), nullable=False)
    person_name = Column(String(120))
    birth_date = Column(String(20))
    birth_time = Column(String(20))
    birth_city = Column(String(120))
    accuracy = Column(String(40))
    experience = Column(String(40))
    usefulness = Column(String(40))
    comments = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    user = relationship("User", back_populates="feedback_items")
