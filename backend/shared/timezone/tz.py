
"""Timezone utilities for IST (UTC+5:30) and local conversions."""

from datetime import datetime, timezone, timedelta

IST_OFFSET = timedelta(hours=5, minutes=30)
IST_TZ = timezone(IST_OFFSET, name="IST")


def now_ist() -> datetime:
    """Return current datetime in IST timezone."""
    return datetime.now(timezone.utc).astimezone(IST_TZ)


def to_ist(dt: datetime) -> datetime:
    """Convert a UTC or naive datetime to IST."""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(IST_TZ)


import zoneinfo
from typing import Optional, Tuple, Any

def resolve_timezone(
    lat: Optional[float] = None,
    lon: Optional[float] = None,
    tz_str: Optional[str] = None,
    tz_name: Optional[str] = None,
    city_name: Optional[str] = None,
    **kwargs: Any
) -> Tuple[Any, str]:
    chosen = tz_str or tz_name
    if not chosen and lat is not None and lon is not None:
        if -125.0 <= lon <= -65.0 and 24.0 <= lat <= 50.0:
            chosen = "America/New_York"
    if not chosen:
        chosen = "Asia/Kolkata"
    try:
        tz = zoneinfo.ZoneInfo(chosen)
    except Exception:
        tz = IST_TZ
        chosen = "Asia/Kolkata"
    return tz, chosen



def validate_iana_timezone(tz_name: str) -> bool:
    if not tz_name or not isinstance(tz_name, str):
        return False
    try:
        zoneinfo.ZoneInfo(tz_name)
        return True
    except Exception:
        return False



def get_local_now(tz_name: str = "Asia/Kolkata") -> datetime:
    """Return current datetime in the specified timezone (falls back to IST)."""
    try:
        zi = zoneinfo.ZoneInfo(tz_name)
        return datetime.now(timezone.utc).astimezone(zi)
    except Exception:
        return now_ist()


def to_local_iso(dt: datetime, tz_name: str = "Asia/Kolkata") -> str:
    """Convert datetime to ISO 8601 string in the specified timezone."""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    try:
        zi = zoneinfo.ZoneInfo(tz_name)
        return dt.astimezone(zi).isoformat()
    except Exception:
        return to_ist(dt).isoformat()


def to_utc_jd(
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int,
    second: int = 0,
    tz_name: Optional[str] = None,
    tz_offset: Optional[float] = None,
) -> Tuple[int, int, int, float, float]:
    """
    Convert local wall-clock date and time in an IANA timezone or decimal offset to:
    (utc_year, utc_month, utc_day, decimal_utc_hour, julian_day).

    Guarantees seamless handling of:
    - Month and year wrapping (including near-midnight births on the 1st of any month)
    - Leap years (e.g. Feb 29)
    - Daylight Saving Time (DST) historical and future transitions
    - Safe fallback to tz_offset or IST (+5.5) if tz_name is invalid
    """
    import swisseph as swe

    # Attempt IANA ZoneInfo conversion first
    if tz_name and validate_iana_timezone(tz_name):
        try:
            zi = zoneinfo.ZoneInfo(tz_name)
            dt_local = datetime(year, month, day, hour, minute, second, tzinfo=zi)
            dt_utc = dt_local.astimezone(timezone.utc)
        except Exception:
            offset = 5.5 if tz_offset is None else tz_offset
            dt_utc = datetime(year, month, day, hour, minute, second) - timedelta(hours=offset)
    elif tz_offset is not None:
        dt_utc = datetime(year, month, day, hour, minute, second) - timedelta(hours=tz_offset)
    else:
        # Default fallback is Indian Standard Time (UTC+5:30)
        dt_utc = datetime(year, month, day, hour, minute, second) - timedelta(hours=5.5)

    decimal_utc_hour = (
        dt_utc.hour
        + dt_utc.minute / 60.0
        + dt_utc.second / 3600.0
        + dt_utc.microsecond / 3.6e9
    )
    jd = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day, decimal_utc_hour)
    return dt_utc.year, dt_utc.month, dt_utc.day, decimal_utc_hour, jd
