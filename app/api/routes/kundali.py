"""Kundali generation, Chart calculation, PDF download, and Kundali chat API routes."""

from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
import swisseph as swe

from app.schemas.kundali import BirthData, KundaliChatRequest, KundaliRequest
from app.services.ai_engine.chat_service import chat_service
from app.services.astrology_engine.cities import CITIES, get_city
from app.services.astrology_engine.houses import calculate_lagna
from app.services.astrology_engine.kundali import calculate_kundali
from app.services.astrology_engine.planets import calculate_all_planets
from app.services.pdf_service import generate_kundali_pdf_buffer

router = APIRouter(prefix="/api", tags=["Kundali & Charts"])


@router.get("/cities")
def get_cities():
    """Return sorted list of all supported city names."""
    return sorted(CITIES.keys())


@router.post("/generate-chart")
def generate_chart_api(data: BirthData):
    """Generate basic planetary degrees and Lagna for chart rendering."""
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    jd = swe.julday(data.year, data.month, data.day, data.hour)
    planets = calculate_all_planets(jd)

    lagna_degree, lagna_sign = calculate_lagna(jd)

    return {
        "basic_details": {
            "date": f"{data.day:02d}-{data.month:02d}-{data.year}",
            "time": data.hour,
            "lagna": lagna_sign,
            "lagna_degree": round(lagna_degree % 30.0, 2),
        },
        "planets": planets,
    }


_CHART_CACHE: dict[str, dict] = {}


@router.post("/kundali")
def get_kundali(request: Request, data: KundaliRequest):
    """Calculate comprehensive Vedic Kundali with D9, Yogas, Doshas, and Dasha."""
    coords = get_city(data.city)
    if coords is None:
        raise HTTPException(
            status_code=400,
            detail=f"City '{data.city}' not found in database. Please try a nearby major city.",
        )
    lat, lon, tz = coords

    # Handle timezone adjustment if not standard IST
    ist_offset = 5.5
    if tz != ist_offset:
        dt_local = datetime(data.year, data.month, data.day, data.hour, data.minute)
        dt_ist = dt_local + timedelta(hours=(ist_offset - tz))
        year, month, day = dt_ist.year, dt_ist.month, dt_ist.day
        hour, minute = dt_ist.hour, dt_ist.minute
    else:
        year, month, day, hour, minute = data.year, data.month, data.day, data.hour, data.minute

    result = calculate_kundali(year, month, day, hour, minute, lat, lon)

    # Server-side cache by chart key to avoid Cookie Header Overflow (>4KB)
    chart_id = f"{year}_{month}_{day}_{hour}_{minute}_{round(lat,2)}_{round(lon,2)}"
    _CHART_CACHE[chart_id] = result
    request.session["kundali_chart_id"] = chart_id
    result["chart_id"] = chart_id

    return result


@router.get("/download-kundali")
def download_kundali(request: Request, chart_id: str | None = None):
    """Generate and return an in-memory PDF report for the session's Kundali."""
    cid = chart_id or request.session.get("kundali_chart_id")
    chart = _CHART_CACHE.get(cid) if cid else request.session.get("kundali_chart")
    if not chart:
        raise HTTPException(
            status_code=400,
            detail="No Kundali chart found in current session. Please calculate a chart first.",
        )

    pdf_buffer = generate_kundali_pdf_buffer(chart)
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=AstroLogic_Kundali_Report.pdf"},
    )


@router.post("/kundali-chat")
def kundali_chat(data: KundaliChatRequest):
    """Contextual life questions assistant using natal chart positions."""
    return chat_service.answer_kundali_chat(data.message, data.chart)
