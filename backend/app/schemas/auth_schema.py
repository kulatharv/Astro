"""
Pydantic Schemas for Federated (Google One-Tap) and Passwordless (WhatsApp OTP) Authentication.
"""

from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from app.schemas.user_schema import CosmicBadges


class GoogleAuthRequest(BaseModel):
    credential: str = Field(..., description="Google One-Tap JWT ID token from Google Identity Services")
    client_id: Optional[str] = Field(None, description="Client ID for verification")


class WhatsAppOtpRequest(BaseModel):
    phone_number: str = Field(..., description="Full international phone number (e.g., +919876543210)")
    language: Optional[str] = Field("en", description="Preferred language for WhatsApp template")


class WhatsAppOtpVerifyRequest(BaseModel):
    phone_number: str = Field(..., description="Full international phone number")
    otp_code: str = Field(..., min_length=4, max_length=6, description="6-digit verification code")


class ClaimGuestChartRequest(BaseModel):
    profile_name: str = Field(..., description="Name for the chart profile")
    relationship: str = Field("self", description="Relationship: self, spouse, child, parent, etc.")
    birth_date: str = Field(..., description="YYYY-MM-DD")
    birth_time: str = Field(..., description="HH:MM")
    birth_city: str = Field(..., description="City name")
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    timezone_offset: Optional[float] = 5.5
    tz_name: Optional[str] = "Asia/Kolkata"
    notes: Optional[str] = None


class UserAuthSummary(BaseModel):
    id: int
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    auth_provider: str
    preferred_language: str = "en"
    whatsapp_opt_in: bool = False
    whatsapp_number: Optional[str] = None
    cosmic_badges: Optional[CosmicBadges] = None
    is_new_user: bool = False


class AuthResponse(BaseModel):
    status: str = "success"
    message: str = "Authentication successful"
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 86400  # 24 hours
    user: UserAuthSummary


class GuestSessionCreateRequest(BaseModel):
    device_fingerprint: str = Field(..., description="Device fingerprint hash (df_<hash>)")
    chart_type: str = Field("kundali", description="Type of chart: kundali, prediction, match")
    person_name: str = Field(..., description="Name of the person")
    birth_date: str = Field(..., description="YYYY-MM-DD")
    birth_time: str = Field(..., description="HH:MM")
    birth_place: str = Field(..., description="Birth city or locality")
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    timezone_offset: Optional[float] = 5.5
    chart_payload: Optional[dict] = None
    telemetry: Optional[dict] = None


class GhostSessionSummary(BaseModel):
    has_active_session: bool
    session_token: Optional[str] = None
    chart_type: Optional[str] = None
    person_name: Optional[str] = None
    birth_date: Optional[str] = None
    birth_time: Optional[str] = None
    birth_place: Optional[str] = None
    created_at: Optional[str] = None
    chart_payload: Optional[dict] = None


