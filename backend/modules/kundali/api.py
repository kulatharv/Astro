"""Kundali generation, Chart calculation, PDF download, and Kundali chat API routes."""

import json
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Request, Depends, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import swisseph as swe

from shared.db.session import get_db
from gateway.deps import require_authenticated_user
from modules.auth.models import User
from modules.kundali.models import UserSavedChart
from modules.kundali.schemas import (
    BirthData, KundaliChatRequest, KundaliRequest,
    SavedChartCreate, SavedChartUpdate, SavedChartResponse
)
from modules.kundali.cities import CITIES, get_city, get_city_details
from modules.kundali.houses import calculate_lagna
from modules.kundali.engine import calculate_kundali
from modules.kundali.planets import calculate_all_planets
try:
    from modules.narrative.chat import chat_service
except ImportError:
    from app.services.ai_engine.chat_service import chat_service

try:
    from workers.pdf_worker import generate_kundali_pdf_buffer
except ImportError:
    from app.services.pdf_service import generate_kundali_pdf_buffer

router = APIRouter(prefix="/api", tags=["Kundali & Charts"])


from shared.cache.decorators import cached_chart


class KundaliService:
    @cached_chart(ttl=2592000)
    def compute_chart(self, req: KundaliRequest) -> dict:
        city_details = get_city_details(req.city)
        if city_details is None:
            coords = get_city(req.city)
            if coords is None:
                raise HTTPException(
                    status_code=400,
                    detail=f"City '{req.city}' not found in database. Please try a nearby major city.",
                )
            lat, lon, tz = coords
            tz_name = getattr(req, "timezone", None) or ("Asia/Kolkata" if tz == 5.5 else None)
        else:
            lat = city_details["lat"]
            lon = city_details["lon"]
            tz = city_details.get("timezone", 5.5)
            tz_name = getattr(req, "timezone", None) or city_details.get("tz_name")

        return calculate_kundali(
            year=req.year,
            month=req.month,
            day=req.day,
            hour=req.hour,
            minute=req.minute,
            lat=lat,
            lon=lon,
            timezone_offset=tz,
            tz_name=tz_name,
        )


    def get_chart(self, chart_hash: str) -> dict:
        from modules.kundali.cache import kundali_cache
        return kundali_cache.get(chart_hash) or {}

    def compute_varga(self, chart_hash: str, varga: str) -> dict:
        from modules.kundali.varga import calculate_navamsa
        return {"varga": varga, "chart_hash": chart_hash}


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


kundali_service = KundaliService()
_CHART_CACHE: dict[str, dict] = {}


@router.post("/kundali")
def get_kundali(request: Request, data: KundaliRequest):
    """Calculate comprehensive Vedic Kundali with D9, Yogas, Doshas, and Dasha."""
    result = kundali_service.compute_chart(data)
    result["disclaimer"] = (
        "Vedic astrology interpretations represent traditional symbolic frameworks for self-reflection and personal growth. "
        "Outputs are non-binding and do not constitute professional medical, legal, or financial advice."
    )

    chart_id = f"{data.year}_{data.month}_{data.day}_{data.hour}_{data.minute}_{data.city}"
    _CHART_CACHE[chart_id] = result
    request.session["kundali_chart_id"] = chart_id
    result["chart_id"] = chart_id
    return result



@router.get("/download-kundali")
def download_kundali(request: Request, chart_id: str | None = None):
    """Generate and return an in-memory PDF report for the session's Kundali."""
    cid = chart_id or request.session.get("kundali_chart_id")
    chart = _CHART_CACHE.get(cid) if cid else request.session.get("kundali_chart")

    # If missing from server memory cache, attempt deterministic recomputation from chart_id
    if not chart and cid:
        parts = cid.split("_")
        if len(parts) >= 6:
            try:
                city_name = "_".join(parts[5:])
                recomp_req = KundaliRequest(
                    year=int(parts[0]),
                    month=int(parts[1]),
                    day=int(parts[2]),
                    hour=int(parts[3]),
                    minute=int(parts[4]),
                    city=city_name,
                )
                chart = kundali_service.compute_chart(recomp_req)
                chart["chart_id"] = cid
                _CHART_CACHE[cid] = chart
            except Exception:
                chart = None

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


@router.post("/download-kundali")
def download_kundali_post(payload: dict):
    """Generate in-memory PDF report from posted chart payload."""
    chart = payload.get("chart") or payload
    if not chart or not isinstance(chart, dict):
        raise HTTPException(status_code=400, detail="Invalid chart data payload.")

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


def _format_saved_chart(chart: UserSavedChart) -> dict:
    chart_data = None
    if chart.chart_data:
        try:
            chart_data = json.loads(chart.chart_data)
        except Exception:
            chart_data = None
    return {
        "id": chart.id,
        "user_id": chart.user_id,
        "title": chart.title,
        "person_name": chart.person_name,
        "gender": chart.gender,
        "birth_date": chart.birth_date,
        "birth_time": chart.birth_time,
        "birth_city": chart.birth_city,
        "latitude": chart.latitude,
        "longitude": chart.longitude,
        "timezone_offset": chart.timezone_offset,
        "tz_name": chart.tz_name,
        "ayanamsa": chart.ayanamsa,
        "chart_data": chart_data,
        "notes": chart.notes,
        "created_at": chart.created_at.isoformat() if chart.created_at else None,
        "updated_at": chart.updated_at.isoformat() if chart.updated_at else None,
    }


@router.post("/kundali/saved-charts", status_code=status.HTTP_201_CREATED)
def create_saved_chart(
    payload: SavedChartCreate,
    current_user: User = Depends(require_authenticated_user),
    db: Session = Depends(get_db),
):
    """Create and persist a new birth chart for the authenticated user."""
    lat = payload.latitude
    lon = payload.longitude
    tz_offset = 5.5
    tz_name = payload.timezone

    if lat is None or lon is None:
        city_info = get_city_details(payload.city)
        if city_info:
            lat = city_info["lat"]
            lon = city_info["lon"]
            tz_offset = city_info.get("timezone", 5.5)
            tz_name = tz_name or city_info.get("tz_name")
        else:
            coords = get_city(payload.city)
            if coords:
                lat, lon, tz_offset = coords
                tz_name = tz_name or ("Asia/Kolkata" if tz_offset == 5.5 else "UTC")
            else:
                raise HTTPException(
                    status_code=400,
                    detail=f"City '{payload.city}' not recognized. Please provide latitude and longitude coordinates.",
                )

    dt_parts = payload.birth_date.split("-")
    tm_parts = payload.birth_time.split(":")
    computed = calculate_kundali(
        year=int(dt_parts[0]),
        month=int(dt_parts[1]),
        day=int(dt_parts[2]),
        hour=int(tm_parts[0]),
        minute=int(tm_parts[1]),
        second=int(tm_parts[2]) if len(tm_parts) > 2 else 0,
        lat=lat,
        lon=lon,
        timezone_offset=tz_offset,
        tz_name=tz_name,
    )

    saved_chart = UserSavedChart(
        user_id=current_user.id,
        title=payload.title,
        person_name=payload.person_name,
        gender=payload.gender,
        birth_date=payload.birth_date,
        birth_time=payload.birth_time,
        birth_city=payload.city,
        latitude=lat,
        longitude=lon,
        timezone_offset=tz_offset,
        tz_name=tz_name,
        ayanamsa=payload.ayanamsa,
        chart_data=json.dumps(computed),
        notes=payload.notes,
    )
    db.add(saved_chart)
    db.commit()
    db.refresh(saved_chart)
    return _format_saved_chart(saved_chart)


@router.get("/kundali/saved-charts")
def list_saved_charts(
    current_user: User = Depends(require_authenticated_user),
    db: Session = Depends(get_db),
):
    """List all birth charts saved by the authenticated user."""
    charts = (
        db.query(UserSavedChart)
        .filter(UserSavedChart.user_id == current_user.id)
        .order_by(UserSavedChart.updated_at.desc())
        .all()
    )
    return [_format_saved_chart(c) for c in charts]


@router.get("/kundali/saved-charts/{chart_id}")
def get_saved_chart(
    chart_id: int,
    current_user: User = Depends(require_authenticated_user),
    db: Session = Depends(get_db),
):
    """Retrieve a single saved birth chart with ownership verification."""
    chart = (
        db.query(UserSavedChart)
        .filter(UserSavedChart.id == chart_id, UserSavedChart.user_id == current_user.id)
        .first()
    )
    if not chart:
        raise HTTPException(status_code=404, detail="Saved chart not found")
    return _format_saved_chart(chart)


@router.put("/kundali/saved-charts/{chart_id}")
def update_saved_chart(
    chart_id: int,
    payload: SavedChartUpdate,
    current_user: User = Depends(require_authenticated_user),
    db: Session = Depends(get_db),
):
    """Update metadata or recalculate birth details of an owned chart."""
    chart = (
        db.query(UserSavedChart)
        .filter(UserSavedChart.id == chart_id, UserSavedChart.user_id == current_user.id)
        .first()
    )
    if not chart:
        raise HTTPException(status_code=404, detail="Saved chart not found")

    recompute = False
    if payload.title is not None:
        chart.title = payload.title
    if payload.person_name is not None:
        chart.person_name = payload.person_name
    if payload.gender is not None:
        chart.gender = payload.gender
    if payload.notes is not None:
        chart.notes = payload.notes

    if payload.birth_date is not None and payload.birth_date != chart.birth_date:
        chart.birth_date = payload.birth_date
        recompute = True
    if payload.birth_time is not None and payload.birth_time != chart.birth_time:
        chart.birth_time = payload.birth_time
        recompute = True
    if payload.city is not None and payload.city != chart.birth_city:
        chart.birth_city = payload.city
        city_info = get_city_details(payload.city)
        if city_info:
            chart.latitude = city_info["lat"]
            chart.longitude = city_info["lon"]
            chart.timezone_offset = city_info.get("timezone", 5.5)
            chart.tz_name = payload.timezone or city_info.get("tz_name")
        recompute = True

    if payload.latitude is not None:
        chart.latitude = payload.latitude
        recompute = True
    if payload.longitude is not None:
        chart.longitude = payload.longitude
        recompute = True
    if payload.timezone is not None:
        chart.tz_name = payload.timezone
        recompute = True
    if payload.ayanamsa is not None:
        chart.ayanamsa = payload.ayanamsa
        recompute = True

    if recompute:
        dt_parts = chart.birth_date.split("-")
        tm_parts = chart.birth_time.split(":")
        computed = calculate_kundali(
            year=int(dt_parts[0]),
            month=int(dt_parts[1]),
            day=int(dt_parts[2]),
            hour=int(tm_parts[0]),
            minute=int(tm_parts[1]),
            second=int(tm_parts[2]) if len(tm_parts) > 2 else 0,
            lat=chart.latitude,
            lon=chart.longitude,
            timezone_offset=chart.timezone_offset,
            tz_name=chart.tz_name,
        )
        chart.chart_data = json.dumps(computed)

    chart.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(chart)
    return _format_saved_chart(chart)


@router.delete("/kundali/saved-charts/{chart_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_saved_chart(
    chart_id: int,
    current_user: User = Depends(require_authenticated_user),
    db: Session = Depends(get_db),
):
    """Delete a saved chart with ownership verification."""
    chart = (
        db.query(UserSavedChart)
        .filter(UserSavedChart.id == chart_id, UserSavedChart.user_id == current_user.id)
        .first()
    )
    if not chart:
        raise HTTPException(status_code=404, detail="Saved chart not found")

    db.delete(chart)
    db.commit()
    return None

