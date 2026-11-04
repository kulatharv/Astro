"""SQLAlchemy database models for user saved birth charts."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from shared.db.session import Base


class UserSavedChart(Base):
    """Stores user birth charts, family profiles, and client horoscopes."""
    __tablename__ = "user_saved_charts"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(120), nullable=False)
    person_name = Column(String(120), nullable=True)
    gender = Column(String(20), nullable=True)
    birth_date = Column(String(20), nullable=False)  # Format: YYYY-MM-DD
    birth_time = Column(String(20), nullable=False)  # Format: HH:MM
    birth_city = Column(String(120), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    timezone_offset = Column(Float, nullable=False, default=5.5)
    tz_name = Column(String(64), nullable=True)
    ayanamsa = Column(String(40), nullable=False, default="Lahiri")
    chart_data = Column(Text, nullable=True)  # JSON-encoded computed planetary positions and houses
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="saved_charts")
