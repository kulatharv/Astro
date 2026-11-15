"""User service for profile management, cosmic badge calculation, and family chart vault."""

import json
from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session

from modules.auth.models import User, UserProfile
from modules.kundali.models import UserSavedChart
from modules.feedback.models import Feedback
from modules.kundali.cities import get_city
from modules.kundali.engine import calculate_kundali
from app.schemas.user_schema import (
    CosmicBadges,
    UserProfileResponse,
    UserProfileUpdateRequest,
    WhatsAppPreferencesUpdate,
    SavedChartCreate,
    SavedChartResponse,
)
from shared.logging.logger import get_logger

logger = get_logger("user_service")


def compute_cosmic_badges_for_birth_data(
    birth_date_str: str,
    birth_time_str: str,
    lat: float,
    lon: float,
    tz_offset: float = 5.5,
) -> Optional[CosmicBadges]:
    """
    Computes classical Vedic Cosmic Badges (Lagna, Moon Sign, Sun Sign, Nakshatra, Dasha)
    using the verified Kundali ephemeris calculation engine.
    """
    try:
        parts = birth_date_str.split("-")
        if len(parts) != 3:
            return None
        year, month, day = int(parts[0]), int(parts[1]), int(parts[2])

        time_parts = birth_time_str.split(":")
        hour = int(time_parts[0]) if len(time_parts) > 0 else 12
        minute = int(time_parts[1]) if len(time_parts) > 1 else 0

        chart = calculate_kundali(
            year=year,
            month=month,
            day=day,
            hour=hour,
            minute=minute,
            lat=lat,
            lon=lon,
            second=0,
            timezone_offset=tz_offset,
        )

        lagna_sign = chart.get("lagna", "")
        planets = chart.get("planets", [])

        moon_sign, moon_nak, moon_pada = None, None, None
        sun_sign = None

        for p in planets:
            p_name = p.get("name", "")
            if p_name == "Moon":
                moon_sign = p.get("sign")
                moon_nak = p.get("nakshatra")
                moon_pada = p.get("pada")
            elif p_name == "Sun":
                sun_sign = p.get("sign")

        # Current dasha
        dasha_info = chart.get("dasha", {})
        mahadasha = dasha_info.get("current_mahadasha")
        antardasha = None

        # Attempt to get antardasha if available from timeline
        timeline = dasha_info.get("timeline", [])
        if timeline and len(timeline) > 0:
            antardasha = timeline[0].get("lord")

        return CosmicBadges(
            lagna_sign=lagna_sign,
            moon_sign=moon_sign,
            sun_sign=sun_sign,
            nakshatra=moon_nak,
            nakshatra_pada=moon_pada,
            mahadasha=mahadasha,
            antardasha=antardasha,
            is_calculated=True,
        )
    except Exception as e:
        logger.warning(f"Could not compute cosmic badges: {e}")
        return None


class UserService:
    @staticmethod
    def calculate_cosmic_badges(profile: UserProfile) -> Optional[CosmicBadges]:
        if not profile or not profile.birth_date or not profile.birth_time:
            return None
        lat = profile.latitude or 28.6139
        lon = profile.longitude or 77.2090
        tz = profile.timezone_offset or 5.5
        return compute_cosmic_badges_for_birth_data(profile.birth_date, profile.birth_time, lat, lon, tz)

    @staticmethod
    def get_or_create_profile(db: Session, user: User) -> UserProfile:
        profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
        if not profile:
            profile = UserProfile(user_id=user.id)
            db.add(profile)
            db.commit()
            db.refresh(profile)
        return profile

    @staticmethod
    def get_user_profile(db: Session, user_id: int) -> Optional[UserProfileResponse]:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return None

        profile = UserService.get_or_create_profile(db, user)
        saved_count = db.query(UserSavedChart).filter(UserSavedChart.user_id == user.id).count()

        # Check if cosmic badges can be computed
        badges = None
        if profile.birth_date and profile.birth_time:
            lat = profile.latitude
            lon = profile.longitude
            if (lat is None or lon is None) and profile.birth_city:
                try:
                    c_lat, c_lon, c_tz = get_city(profile.birth_city)
                    lat, lon = c_lat, c_lon
                    profile.latitude = lat
                    profile.longitude = lon
                    profile.timezone_offset = c_tz
                    db.commit()
                except Exception:
                    lat, lon = 18.5204, 73.8567

            if lat is not None and lon is not None:
                badges = compute_cosmic_badges_for_birth_data(
                    profile.birth_date,
                    profile.birth_time,
                    lat,
                    lon,
                    profile.timezone_offset or 5.5,
                )

        return UserProfileResponse(
            user_id=user.id,
            name=user.name,
            email=user.email,
            phone=profile.phone,
            birth_date=profile.birth_date,
            birth_time=profile.birth_time,
            birth_city=profile.birth_city,
            latitude=profile.latitude,
            longitude=profile.longitude,
            timezone_offset=profile.timezone_offset or 5.5,
            tz_name=profile.tz_name or "Asia/Kolkata",
            birth_uncertainty=profile.birth_uncertainty or "exact",
            zodiac_sign=profile.zodiac_sign,
            notes=profile.notes,
            preferred_language=user.preferred_language or "en",
            whatsapp_number=profile.whatsapp_number,
            whatsapp_opt_in=bool(profile.whatsapp_opt_in),
            whatsapp_time=profile.whatsapp_time or "07:00",
            whatsapp_language=profile.whatsapp_language or "en",
            cosmic_badges=badges,
            saved_charts_count=saved_count,
            updated_at=profile.updated_at,
        )

    @staticmethod
    def update_user_profile(
        db: Session, user_id: int, req: UserProfileUpdateRequest
    ) -> Optional[UserProfileResponse]:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return None

        profile = UserService.get_or_create_profile(db, user)

        if req.name is not None:
            user.name = req.name.strip()
        if req.preferred_language is not None:
            user.preferred_language = req.preferred_language

        if req.phone is not None:
            profile.phone = req.phone.strip()
        if req.birth_date is not None:
            profile.birth_date = req.birth_date.strip()
        if req.birth_time is not None:
            profile.birth_time = req.birth_time.strip()

        if req.birth_city is not None:
            city_clean = req.birth_city.strip()
            profile.birth_city = city_clean
            # Auto-resolve coordinates if not explicitly provided
            if req.latitude is None or req.longitude is None:
                try:
                    c_lat, c_lon, c_tz = get_city(city_clean)
                    profile.latitude = c_lat
                    profile.longitude = c_lon
                    profile.timezone_offset = c_tz
                except Exception:
                    pass

        if req.latitude is not None:
            profile.latitude = req.latitude
        if req.longitude is not None:
            profile.longitude = req.longitude
        if req.timezone_offset is not None:
            profile.timezone_offset = req.timezone_offset
        if req.tz_name is not None:
            profile.tz_name = req.tz_name

        if req.birth_uncertainty is not None:
            profile.birth_uncertainty = req.birth_uncertainty
        if req.zodiac_sign is not None:
            profile.zodiac_sign = req.zodiac_sign
        if req.notes is not None:
            profile.notes = req.notes

        # WhatsApp settings
        if req.whatsapp_number is not None:
            profile.whatsapp_number = req.whatsapp_number.strip()
        if req.whatsapp_opt_in is not None:
            profile.whatsapp_opt_in = req.whatsapp_opt_in
        if req.whatsapp_time is not None:
            profile.whatsapp_time = req.whatsapp_time
        if req.whatsapp_language is not None:
            profile.whatsapp_language = req.whatsapp_language

        profile.updated_at = datetime.utcnow()
        db.commit()

        return UserService.get_user_profile(db, user_id)

    @staticmethod
    def update_whatsapp_preferences(
        db: Session, user_id: int, req: WhatsAppPreferencesUpdate
    ) -> Optional[UserProfileResponse]:
        profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        if not profile:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return None
            profile = UserService.get_or_create_profile(db, user)

        profile.whatsapp_number = req.whatsapp_number.strip()
        profile.whatsapp_opt_in = req.whatsapp_opt_in
        profile.whatsapp_time = req.whatsapp_time
        profile.whatsapp_language = req.whatsapp_language
        profile.updated_at = datetime.utcnow()
        db.commit()

        return UserService.get_user_profile(db, user_id)

    @staticmethod
    def list_saved_charts(db: Session, user_id: int) -> List[SavedChartResponse]:
        charts = (
            db.query(UserSavedChart)
            .filter(UserSavedChart.user_id == user_id)
            .order_by(UserSavedChart.created_at.desc())
            .all()
        )

        res: List[SavedChartResponse] = []
        for c in charts:
            lagna_sign, moon_sign, nakshatra = None, None, None
            if c.chart_data:
                try:
                    cdata = json.loads(c.chart_data)
                    lagna_sign = cdata.get("lagna")
                    for p in cdata.get("planets", []):
                        if p.get("name") == "Moon":
                            moon_sign = p.get("sign")
                            nakshatra = p.get("nakshatra")
                except Exception:
                    pass

            res.append(
                SavedChartResponse(
                    id=c.id,
                    user_id=c.user_id,
                    title=c.title,
                    person_name=c.person_name,
                    gender=c.gender,
                    birth_date=c.birth_date,
                    birth_time=c.birth_time,
                    birth_city=c.birth_city,
                    latitude=c.latitude,
                    longitude=c.longitude,
                    timezone_offset=c.timezone_offset,
                    tz_name=c.tz_name,
                    ayanamsa=c.ayanamsa or "Lahiri",
                    notes=c.notes,
                    created_at=c.created_at,
                    updated_at=c.updated_at,
                    lagna_sign=lagna_sign,
                    moon_sign=moon_sign,
                    nakshatra=nakshatra,
                )
            )
        return res

    @staticmethod
    def create_saved_chart(
        db: Session, user_id: int, req: SavedChartCreate
    ) -> SavedChartResponse:
        lat = req.latitude
        lon = req.longitude
        tz_offset = req.timezone_offset

        if lat is None or lon is None:
            try:
                c_lat, c_lon, c_tz = get_city(req.birth_city)
                lat, lon, tz_offset = c_lat, c_lon, c_tz
            except Exception:
                lat, lon = 18.5204, 73.8567

        # Precompute chart data for instant retrieval
        chart_data_json = None
        lagna_sign, moon_sign, nakshatra = None, None, None
        try:
            parts = req.birth_date.split("-")
            tparts = req.birth_time.split(":")
            chart = calculate_kundali(
                year=int(parts[0]),
                month=int(parts[1]),
                day=int(parts[2]),
                hour=int(tparts[0]),
                minute=int(tparts[1]) if len(tparts) > 1 else 0,
                lat=lat,
                lon=lon,
                second=0,
                timezone_offset=tz_offset,
            )
            chart_data_json = json.dumps(chart)
            lagna_sign = chart.get("lagna")
            for p in chart.get("planets", []):
                if p.get("name") == "Moon":
                    moon_sign = p.get("sign")
                    nakshatra = p.get("nakshatra")
        except Exception as e:
            logger.warning(f"Could not precalculate chart for {req.person_name}: {e}")

        new_chart = UserSavedChart(
            user_id=user_id,
            title=req.title.strip(),
            person_name=req.person_name.strip(),
            gender=req.gender or "unknown",
            birth_date=req.birth_date.strip(),
            birth_time=req.birth_time.strip(),
            birth_city=req.birth_city.strip(),
            latitude=lat,
            longitude=lon,
            timezone_offset=tz_offset,
            tz_name=req.tz_name or "Asia/Kolkata",
            ayanamsa="Lahiri",
            chart_data=chart_data_json,
            notes=req.notes,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.add(new_chart)
        db.commit()
        db.refresh(new_chart)

        return SavedChartResponse(
            id=new_chart.id,
            user_id=new_chart.user_id,
            title=new_chart.title,
            person_name=new_chart.person_name,
            gender=new_chart.gender,
            birth_date=new_chart.birth_date,
            birth_time=new_chart.birth_time,
            birth_city=new_chart.birth_city,
            latitude=new_chart.latitude,
            longitude=new_chart.longitude,
            timezone_offset=new_chart.timezone_offset,
            tz_name=new_chart.tz_name,
            ayanamsa=new_chart.ayanamsa,
            notes=new_chart.notes,
            created_at=new_chart.created_at,
            updated_at=new_chart.updated_at,
            lagna_sign=lagna_sign,
            moon_sign=moon_sign,
            nakshatra=nakshatra,
        )

    @staticmethod
    def delete_saved_chart(db: Session, user_id: int, chart_id: int) -> bool:
        chart = (
            db.query(UserSavedChart)
            .filter(UserSavedChart.id == chart_id, UserSavedChart.user_id == user_id)
            .first()
        )
        if not chart:
            return False
        db.delete(chart)
        db.commit()
        return True


user_service = UserService()
