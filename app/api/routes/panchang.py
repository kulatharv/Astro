"""Panchang, Personalization, Decision Assistant, and Festival API routes."""

from datetime import datetime, time as dt_time
from typing import Optional
from fastapi import APIRouter, HTTPException, Query, Response

from app.schemas.panchang import DecisionRequest, PanchangRequest, ProfileResolveRequest
from app.services.astrology_engine.festival import get_today_festivals, get_upcoming_festivals
from app.services.astrology_engine.ics import generate_panchang_ics
from app.services.astrology_engine.panchang import get_full_panchang
from app.services.astrology_engine.personalization import derive_natal_moon, evaluate_decision

router = APIRouter(prefix="/api", tags=["Panchang & Festivals"])


@router.post("/panchang")
def panchang_city(request: PanchangRequest):
    """Calculate daily Panchang (Tithi, Nakshatra, Yoga, Karana, Vara, Rahu Kaal) for a city."""
    city = request.city or "Pune"
    return get_full_panchang(city)


@router.post("/panchang/resolve-profile")
def resolve_profile(request: ProfileResolveRequest):
    """Resolve natal Moon sign (Rashi) and Nakshatra from birth date and time."""
    try:
        birth_date = datetime.strptime(request.birth_date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid birth_date format. Expected YYYY-MM-DD.")

    birth_time = None
    if request.birth_time:
        try:
            parts = request.birth_time.split(":")
            birth_time = dt_time(int(parts[0]), int(parts[1]))
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid birth_time format. Expected HH:MM (24h).")

    try:
        result = derive_natal_moon(
            birth_date=birth_date,
            birth_time=birth_time,
            city_name=request.birth_place or "Pune",
            lat=request.lat,
            lon=request.lon,
        )
        result["name"] = request.name or ""
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to resolve birth chart: {e}")


@router.post("/panchang/decision")
def decision_assistant(request: DecisionRequest):
    """Evaluate decision auspiciousness (Tara Bala, Chandra Bala) for an activity."""
    try:
        city = request.city or "Pune"
        panchang_data = get_full_panchang(city)

        result = evaluate_decision(
            activity_type=request.activity,
            user_rashi=request.user_rashi,
            user_nakshatra=request.user_nakshatra,
            current_panchang=panchang_data,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Decision engine encountered an error: {e}")


@router.get("/panchang/calendar.ics")
def panchang_calendar_ics(
    city: str = Query(default="Pune", description="City for festival and muhurta timings"),
    limit: int = Query(default=45, ge=1, le=120, description="Number of upcoming events to include"),
):
    """Generate and return an RFC 5545 compliant .ics iCalendar file."""
    try:
        ics_content = generate_panchang_ics(city=city, limit=limit)
        return Response(
            content=ics_content,
            media_type="text/calendar",
            headers={
                "Content-Disposition": f'attachment; filename="vedic_panchang_{city.lower().replace(" ", "_")}.ics"',
                "Cache-Control": "public, max-age=3600",
            },
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate iCalendar export: {e}")


@router.get("/festivals/today")
def festivals_today():
    """Return Hindu festivals falling on today's date."""
    try:
        return {"festivals": get_today_festivals()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/festivals/upcoming")
def festivals_upcoming(limit: int = 12):
    """Return upcoming Hindu festivals for the next 60 days."""
    try:
        return {"festivals": get_upcoming_festivals(limit)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

