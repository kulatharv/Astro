from typing import Any, Optional
from pydantic import BaseModel, Field


class BirthData(BaseModel):
    name: str = "Seeker"
    year: int = Field(..., ge=1900, le=2100)
    month: int = Field(..., ge=1, le=12)
    day: int = Field(..., ge=1, le=31)
    hour: float = Field(..., ge=0, lt=24)
    place: str = "Unknown"


class KundaliRequest(BaseModel):
    year: int = Field(..., ge=1900, le=2100)
    month: int = Field(..., ge=1, le=12)
    day: int = Field(..., ge=1, le=31)
    hour: int = Field(..., ge=0, le=23)
    minute: int = Field(..., ge=0, le=59)
    city: str = Field(..., min_length=1)
    timezone: Optional[str] = None


class KundaliChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    chart: dict[str, Any]


class PlanetDetail(BaseModel):
    name: str
    sign: str
    degree: str
    degree_decimal: float
    house: int
    nakshatra: str
    pada: int
    navamsa: str
    strength: str
    retrograde: bool


class KundaliResponse(BaseModel):
    lagna: str
    lagna_degree: str
    lagna_degree_decimal: float
    lagna_nakshatra: str
    lagna_pada: int
    houses: dict[int, list[str]]
    d9_houses: dict[int, list[str]]
    d9_lagna: str
    planets: list[PlanetDetail]
    tithi_number: int
    tithi_name: str
    paksha: str
    nakshatra: str
    nakshatra_pada: int
    yoga_name: str
    karana_name: str
    ayanamsa: float
    jd: float
    mahadasha: str
    dasha_balance: str
    antardasha: str
    antardasha_list: list[dict[str, Any]]
    scores: dict[str, int]
    yogas: list[dict[str, Any]]
    doshas: list[dict[str, Any]]


class SavedChartCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=120)
    person_name: Optional[str] = Field(None, max_length=120)
    gender: Optional[str] = Field(None, max_length=20)
    birth_date: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$")
    birth_time: str = Field(..., pattern=r"^\d{1,2}:\d{2}(:\d{2})?$")
    city: str = Field(..., min_length=1, max_length=120)
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    timezone: Optional[str] = None
    ayanamsa: str = Field("Lahiri", max_length=40)
    notes: Optional[str] = None


class SavedChartUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=120)
    person_name: Optional[str] = Field(None, max_length=120)
    gender: Optional[str] = Field(None, max_length=20)
    birth_date: Optional[str] = Field(None, pattern=r"^\d{4}-\d{2}-\d{2}$")
    birth_time: Optional[str] = Field(None, pattern=r"^\d{1,2}:\d{2}(:\d{2})?$")
    city: Optional[str] = Field(None, min_length=1, max_length=120)
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    timezone: Optional[str] = None
    ayanamsa: Optional[str] = Field(None, max_length=40)
    notes: Optional[str] = None


class SavedChartResponse(BaseModel):
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
    ayanamsa: str
    chart_data: Optional[dict[str, Any]] = None
    notes: Optional[str] = None
    created_at: Optional[Any] = None
    updated_at: Optional[Any] = None

