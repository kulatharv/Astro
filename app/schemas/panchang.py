from typing import Optional, Any
from pydantic import BaseModel, Field, ConfigDict


class PanchangRequest(BaseModel):
    model_config = ConfigDict(extra="allow")

    city: Optional[str] = Field(default="Pune")
    date_str: Optional[str] = None  # Format YYYY-MM-DD optional
    lat: Optional[float] = None
    lon: Optional[float] = None
    timezone: Optional[str] = None
    user_rashi: Optional[str] = None
    user_nakshatra: Optional[str] = None


class ProfileResolveRequest(BaseModel):
    """Resolve natal Moon sign (Rashi) and Nakshatra from birth details."""
    model_config = ConfigDict(extra="allow")

    name: Optional[str] = None
    birth_date: str  # YYYY-MM-DD
    birth_time: Optional[str] = None  # HH:MM (24h)
    birth_place: Optional[str] = Field(default="Pune")
    lat: Optional[float] = None
    lon: Optional[float] = None


class DecisionRequest(BaseModel):
    """Interactive Decision Assistant request."""
    model_config = ConfigDict(extra="allow")

    activity: str = Field(..., description="Activity type: travel, investment, meeting, spiritual, purchase")
    city: Optional[str] = Field(default="Pune")
    user_rashi: Optional[str] = None
    user_nakshatra: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None


class PanchangResponse(BaseModel):
    date: str | None = None
    city: str
    tithi: str | None = None
    nakshatra: str | None = None
    yoga: str | None = None
    karana: str | None = None
    vara: str | None = None
    sunrise: str | None = None
    sunset: str | None = None
    rahu_kaal: str | None = None
    gulika_kaal: str | None = None
    yamaganda: str | None = None
    abhijit_muhurta: str | None = None
