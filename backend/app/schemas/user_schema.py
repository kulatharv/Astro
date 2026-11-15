"""Pydantic schemas for User Profile, Cosmic Identity Badges, and Family Chart Vault."""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class CosmicBadges(BaseModel):
    """Auto-calculated classical Vedic identity metrics."""
    lagna_sign: Optional[str] = None
    moon_sign: Optional[str] = None
    sun_sign: Optional[str] = None
    nakshatra: Optional[str] = None
    nakshatra_pada: Optional[int] = None
    mahadasha: Optional[str] = None
    antardasha: Optional[str] = None
    pratyantardasha: Optional[str] = None
    is_calculated: bool = False


class UserProfileResponse(BaseModel):
    """Full user profile response payload with auto-computed cosmic badges."""
    user_id: int
    name: str
    email: str
    phone: Optional[str] = None
    birth_date: Optional[str] = None
    birth_time: Optional[str] = None
    birth_city: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    timezone_offset: float = 5.5
    tz_name: Optional[str] = "Asia/Kolkata"
    birth_uncertainty: str = "exact"  # exact, approximate, uncertain
    zodiac_sign: Optional[str] = None
    notes: Optional[str] = None
    preferred_language: str = "en"

    # WhatsApp daily forecast preferences
    whatsapp_number: Optional[str] = None
    whatsapp_opt_in: bool = False
    whatsapp_time: str = "07:00"
    whatsapp_language: str = "en"

    # Auto-calculated Cosmic Identity
    cosmic_badges: Optional[CosmicBadges] = None
    saved_charts_count: int = 0
    updated_at: Optional[datetime] = None


class UserProfileUpdateRequest(BaseModel):
    """Payload for updating user profile and birth parameters."""
    name: Optional[str] = None
    phone: Optional[str] = None
    birth_date: Optional[str] = None
    birth_time: Optional[str] = None
    birth_city: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    timezone_offset: Optional[float] = 5.5
    tz_name: Optional[str] = "Asia/Kolkata"
    birth_uncertainty: Optional[str] = "exact"
    zodiac_sign: Optional[str] = None
    notes: Optional[str] = None
    preferred_language: Optional[str] = "en"

    # WhatsApp settings
    whatsapp_number: Optional[str] = None
    whatsapp_opt_in: Optional[bool] = None
    whatsapp_time: Optional[str] = None
    whatsapp_language: Optional[str] = None


class WhatsAppPreferencesUpdate(BaseModel):
    """Payload specifically for updating WhatsApp notification preferences."""
    whatsapp_number: str
    whatsapp_opt_in: bool = True
    whatsapp_time: str = "07:00"
    whatsapp_language: str = "en"


class SavedChartCreate(BaseModel):
    """Payload to add a family member or client chart into the user's vault."""
    title: str = Field(..., description="Relation / Category (e.g. Spouse, Son, Mother, Client)")
    person_name: str = Field(..., description="Full name of the person")
    gender: Optional[str] = "unknown"
    birth_date: str = Field(..., description="YYYY-MM-DD")
    birth_time: str = Field(..., description="HH:MM")
    birth_city: str = Field(..., description="City of birth")
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    timezone_offset: float = 5.5
    tz_name: Optional[str] = "Asia/Kolkata"
    notes: Optional[str] = None


class SavedChartResponse(BaseModel):
    """Response payload for a saved chart entry."""
    id: int
    user_id: int
    title: str
    person_name: Optional[str] = None
    gender: Optional[str] = None
    birth_date: str
    birth_time: str
    birth_city: str
    latitude: float
    longitude: float
    timezone_offset: float
    tz_name: Optional[str] = None
    ayanamsa: str = "Lahiri"
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # Cosmic summary for the saved profile
    lagna_sign: Optional[str] = None
    moon_sign: Optional[str] = None
    nakshatra: Optional[str] = None

