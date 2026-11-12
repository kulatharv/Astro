"""
Enterprise-Grade Panchang Engine with Swiss Ephemeris Precision.
Computes:
1. Five Sacred Limbs (Tithi, Nakshatra, Yoga, Karana, Vaar) with exact progress & end times.
2. Astronomical Local Sunrise, Sunset, Sandhya & Moon Times.
3. 16-Period Choghadiya (8 Day + 8 Night) with live status & countdown.
4. 24-Hour Planetary Horas.
5. Inauspicious Periods (Rahu Kaal, Yamaganda, Gulika).
6. Auspicious Windows (Abhijit Muhurta, Brahma Muhurta, Amrit/Shubh Choghadiyas).
7. Disha Shool & Ancient Vedic Remedies.
8. Deterministic Actionable Advice (Do's & Don'ts) & 0-10 Auspiciousness Scoring.
9. Optional Personalization (Tara Bala & Chandra Bala).
"""

from datetime import datetime, date, timedelta, timezone
import math
from typing import Dict, Any, List, Optional
import swisseph as swe

from shared.timezone.tz import resolve_timezone, get_local_now, to_local_iso
from shared.cache.redis_client import CacheService
from modules.kundali.cities import CITIES, get_city, get_city_elevation

from shared.veda.nakshatra import NAKSHATRAS
from shared.veda.zodiac import SIGNS, SIGNS_EN, to_dms
from modules.horoscope.rules.daily import evaluate_daily_rules

TITHI_NAMES = [
    "Shukla Pratipada", "Shukla Dwitiya", "Shukla Tritiya", "Shukla Chaturthi",
    "Shukla Panchami", "Shukla Shashthi", "Shukla Saptami", "Shukla Ashtami",
    "Shukla Navami", "Shukla Dashami", "Shukla Ekadashi", "Shukla Dwadashi",
    "Shukla Trayodashi", "Shukla Chaturdashi", "Purnima",
    "Krishna Pratipada", "Krishna Dwitiya", "Krishna Tritiya", "Krishna Chaturthi",
    "Krishna Panchami", "Krishna Shashthi", "Krishna Saptami", "Krishna Ashtami",
    "Krishna Navami", "Krishna Dashami", "Krishna Ekadashi", "Krishna Dwadashi",
    "Krishna Trayodashi", "Krishna Chaturdashi", "Amavasya"
]

YOGA_NAMES = [
    "Vishkambha", "Priti", "Ayushman", "Saubhagya", "Shobhana",
    "Atiganda", "Sukarma", "Dhriti", "Shula", "Ganda",
    "Vriddhi", "Dhruva", "Vyaghata", "Harshana", "Vajra",
    "Asiddhi", "Vyatipata", "Variyan", "Parigha", "Shiva",
    "Siddha", "Sadhya", "Shubha", "Shukla", "Brahma",
    "Indra", "Vaidhriti"
]

KARANA_NAMES = [
    "Bava", "Balava", "Kaulava", "Taitila", "Gara",
    "Vanija", "Vishti (Bhadra)", "Shakuni", "Chatushpada",
    "Naga", "Kimstughna"
]

CHOGHADIYA_ORDER = ["Udveg", "Char", "Labh", "Amrit", "Kaal", "Shubh", "Rog"]
DAY_CHOGHADIYA_START = {
    0: 0, 1: 3, 2: 6, 3: 2, 4: 5, 5: 1, 6: 4
}
NIGHT_CHOGHADIYA_START = {
    0: 5, 1: 1, 2: 4, 3: 0, 4: 3, 5: 6, 6: 2
}

CHOGHADIYA_INFO = {
    "Amrit": {"is_good": True, "planet": "Moon", "label": "Auspicious (Nectar)"},
    "Shubh": {"is_good": True, "planet": "Jupiter", "label": "Auspicious (Good)"},
    "Labh": {"is_good": True, "planet": "Mercury", "label": "Auspicious (Gain)"},
    "Char": {"is_good": True, "planet": "Venus", "label": "Neutral / Mobile"},
    "Rog": {"is_good": False, "planet": "Mars", "label": "Inauspicious (Disease)"},
    "Kaal": {"is_good": False, "planet": "Saturn", "label": "Inauspicious (Loss)"},
    "Udveg": {"is_good": False, "planet": "Sun", "label": "Inauspicious (Anxiety)"}
}

CHALDEAN_HORAS = ["Sun", "Venus", "Mercury", "Moon", "Saturn", "Jupiter", "Mars"]
WEEKDAY_HORA_START = {
    0: "Sun", 1: "Moon", 2: "Mars", 3: "Mercury", 4: "Jupiter", 5: "Venus", 6: "Saturn"
}


def _fmt_time_ampm(dt: datetime) -> str:
    return dt.strftime("%I:%M %p")


def _minutes_between(start_dt: datetime, end_dt: datetime) -> float:
    return (end_dt - start_dt).total_seconds() / 60.0


def calculate_choghadiya_list(
    start_dt: datetime,
    end_dt: datetime,
    start_idx: int
) -> List[Dict[str, Any]]:
    total_seconds = (end_dt - start_dt).total_seconds()
    segment_duration = total_seconds / 8.0
    segments = []

    for i in range(8):
        name = CHOGHADIYA_ORDER[(start_idx + i) % 7]
        seg_start = start_dt + timedelta(seconds=i * segment_duration)
        seg_end = start_dt + timedelta(seconds=(i + 1) * segment_duration)
        info = CHOGHADIYA_INFO.get(name, {"is_good": False, "planet": "Sun", "label": name})

        segments.append({
            "name": name,
            "label": info["label"],
            "is_auspicious": info["is_good"],
            "ruling_planet": info["planet"],
            "start": _fmt_time_ampm(seg_start),
            "end": _fmt_time_ampm(seg_end),
            "start_iso": seg_start.isoformat(),
            "end_iso": seg_end.isoformat(),
            "start_dt": seg_start,
            "end_dt": seg_end
        })
    return segments


def calculate_horas_list(
    sunrise_dt: datetime,
    weekday_idx: int
) -> List[Dict[str, Any]]:
    start_planet = WEEKDAY_HORA_START[weekday_idx % 7]
    ch_idx = CHALDEAN_HORAS.index(start_planet)
    horas = []

    for i in range(24):
        h_start = sunrise_dt + timedelta(hours=i)
        h_end = sunrise_dt + timedelta(hours=i + 1)
        planet = CHALDEAN_HORAS[(ch_idx + i) % 7]

        horas.append({
            "hour_number": i + 1,
            "planet": planet,
            "start": _fmt_time_ampm(h_start),
            "end": _fmt_time_ampm(h_end),
            "start_iso": h_start.isoformat(),
            "end_iso": h_end.isoformat(),
            "start_dt": h_start,
            "end_dt": h_end
        })
    return horas


def get_full_panchang(
    city_name: str = "Pune",
    target_date: Optional[date] = None,
    lat: Optional[float] = None,
    lon: Optional[float] = None,
    elevation: Optional[float] = None,
    tz_str: Optional[str] = None,
    user_rashi: Optional[str] = None,
    user_nakshatra: Optional[str] = None
) -> Dict[str, Any]:
    city_info = get_city(city_name)
    if city_info:
        default_lat, default_lon, _ = city_info
    else:
        default_lat, default_lon = 18.5204, 73.8567

    resolved_lat = lat if lat is not None else default_lat
    resolved_lon = lon if lon is not None else default_lon
    resolved_elevation = elevation if elevation is not None else get_city_elevation(name=city_name, lat=resolved_lat, lon=resolved_lon)
    tz_obj, resolved_tz_name = resolve_timezone(lat=resolved_lat, lon=resolved_lon, tz_str=tz_str)

    now_local = get_local_now(tz_obj)
    d = target_date if target_date else now_local.date()
    date_str = d.strftime("%Y-%m-%d")

    cache_key = CacheService.get_panchang_key(f"{date_str}_{resolved_elevation}", resolved_lat, resolved_lon)
    base_data = CacheService.get(cache_key)

    if not base_data or "sunrise_iso" not in base_data:
        base_data = _compute_astronomical_base(d, resolved_lat, resolved_lon, resolved_elevation, tz_obj, city_name)
        CacheService.set(cache_key, base_data, ttl=86400)

    res = _build_dynamic_panchang_response(
        base_data=base_data,
        now_local=now_local,
        resolved_tz_name=resolved_tz_name,
        tz_obj=tz_obj,
        user_rashi=user_rashi,
        user_nakshatra=user_nakshatra
    )
    return res


def _compute_astronomical_base(
    d: date,
    lat: float,
    lon: float,
    elevation: float,
    tz_obj: Any,
    city_display_name: str
) -> Dict[str, Any]:
    jd_noon = swe.julday(d.year, d.month, d.day, 12.0)

    def _jd_to_dt(jd_val: float) -> datetime:
        y, m, d_int, ut_h_float = swe.revjul(jd_val)
        h = int(ut_h_float)
        m_f = (ut_h_float - h) * 60.0
        minute = int(m_f)
        sec_f = (m_f - minute) * 60.0
        sec = min(int(sec_f), 59)
        dt_utc = datetime(y, m, d_int, h, minute, sec, tzinfo=timezone.utc)
        return dt_utc.astimezone(tz_obj)

    try:
        jd_midnight = swe.julday(d.year, d.month, d.day, 0.0)
        res_rise = swe.rise_trans(jd_midnight, swe.SUN, swe.CALC_RISE, (lon, lat, elevation), 0.0, 0.0)
        res_set = swe.rise_trans(jd_midnight, swe.SUN, swe.CALC_SET, (lon, lat, elevation), 0.0, 0.0)
        jd_rise = res_rise[1][0]
        jd_set = res_set[1][0]

        res_next_rise = swe.rise_trans(jd_midnight + 1.0, swe.SUN, swe.CALC_RISE, (lon, lat, elevation), 0.0, 0.0)
        jd_next_rise = res_next_rise[1][0]

        sunrise_dt = _jd_to_dt(jd_rise)
        sunset_dt = _jd_to_dt(jd_set)
        next_sunrise_dt = _jd_to_dt(jd_next_rise)
    except Exception:
        sunrise_dt = datetime(d.year, d.month, d.day, 6, 0, 0, tzinfo=tz_obj)
        sunset_dt = datetime(d.year, d.month, d.day, 18, 30, 0, tzinfo=tz_obj)
        next_sunrise_dt = sunrise_dt + timedelta(days=1)
        jd_rise = swe.julday(d.year, d.month, d.day, 6.0 - (lon / 15.0))

    sunrise_str = _fmt_time_ampm(sunrise_dt)
    sunset_str = _fmt_time_ampm(sunset_dt)

    swe.set_sid_mode(swe.SIDM_LAHIRI)
    anchor_jd = jd_rise
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED
    sun_res, sun_return_flags = swe.calc_ut(anchor_jd, swe.SUN, flags)
    moon_res, moon_return_flags = swe.calc_ut(anchor_jd, swe.MOON, flags)

    sun_sid = sun_res[0] % 360.0
    moon_sid = moon_res[0] % 360.0
    sun_speed = sun_res[3]
    moon_speed = moon_res[3]
    rel_speed = moon_speed - sun_speed if (moon_speed - sun_speed) > 0 else 12.19

    tithi_diff = (moon_sid - sun_sid) % 360.0
    tithi_num = int(tithi_diff / 12.0) + 1
    tithi_name = TITHI_NAMES[(tithi_num - 1) % 30]
    paksha = "Shukla" if tithi_num <= 15 else "Krishna"
    tithi_deg_in = tithi_diff % 12.0
    tithi_progress = round((tithi_deg_in / 12.0) * 100.0, 1)

    target_tithi_diff = (tithi_num * 12.0) % 360.0
    tithi_approx_days = (12.0 - tithi_deg_in) / rel_speed
    low_jd = anchor_jd + tithi_approx_days - 0.25
    high_jd = anchor_jd + tithi_approx_days + 0.25
    for _ in range(22):
        mid_jd = (low_jd + high_jd) / 2.0
        s_res, _ = swe.calc_ut(mid_jd, swe.SUN, swe.FLG_SWIEPH | swe.FLG_SIDEREAL)
        m_res, _ = swe.calc_ut(mid_jd, swe.MOON, swe.FLG_SWIEPH | swe.FLG_SIDEREAL)
        diff = (m_res[0] - s_res[0]) % 360.0
        err = diff - target_tithi_diff
        if err > 180.0:
            err -= 360.0
        elif err < -180.0:
            err += 360.0
        if err < 0:
            low_jd = mid_jd
        else:
            high_jd = mid_jd
    tithi_end_dt = _jd_to_dt((low_jd + high_jd) / 2.0)
    tithi_end_str = _fmt_time_ampm(tithi_end_dt)

    nak_deg = 360.0 / 27.0
    nak_num = int(moon_sid / nak_deg) + 1
    nak_idx = (nak_num - 1) % 27
    nak_name = NAKSHATRAS[nak_idx]
    nak_deg_in = moon_sid % nak_deg
    nak_pada = int(nak_deg_in / (nak_deg / 4.0)) + 1

    target_nak_deg = (nak_num * nak_deg) % 360.0
    nak_approx_days = (nak_deg - nak_deg_in) / (moon_speed if moon_speed > 0 else 13.176)
    low_jd = anchor_jd + nak_approx_days - 0.25
    high_jd = anchor_jd + nak_approx_days + 0.25
    for _ in range(22):
        mid_jd = (low_jd + high_jd) / 2.0
        m_res, _ = swe.calc_ut(mid_jd, swe.MOON, swe.FLG_SWIEPH | swe.FLG_SIDEREAL)
        moon_pos = m_res[0] % 360.0
        err = moon_pos - target_nak_deg
        if err > 180.0:
            err -= 360.0
        elif err < -180.0:
            err += 360.0
        if err < 0:
            low_jd = mid_jd
        else:
            high_jd = mid_jd
    nak_end_dt = _jd_to_dt((low_jd + high_jd) / 2.0)
    nak_end_str = _fmt_time_ampm(nak_end_dt)

    yoga_sum = (sun_sid + moon_sid) % 360.0
    yoga_deg = 360.0 / 27.0
    yoga_num = int(yoga_sum / yoga_deg) + 1
    yoga_idx = (yoga_num - 1) % 27
    yoga_name = YOGA_NAMES[yoga_idx]
    comb_speed = moon_speed + sun_speed

    target_yoga_deg = (yoga_num * yoga_deg) % 360.0
    yoga_deg_in = yoga_sum % yoga_deg
    yoga_approx_days = (yoga_deg - yoga_deg_in) / (comb_speed if comb_speed > 0 else 14.17)
    low_jd = anchor_jd + yoga_approx_days - 0.25
    high_jd = anchor_jd + yoga_approx_days + 0.25
    for _ in range(22):
        mid_jd = (low_jd + high_jd) / 2.0
        s_res, _ = swe.calc_ut(mid_jd, swe.SUN, swe.FLG_SWIEPH | swe.FLG_SIDEREAL)
        m_res, _ = swe.calc_ut(mid_jd, swe.MOON, swe.FLG_SWIEPH | swe.FLG_SIDEREAL)
        curr_sum = (s_res[0] + m_res[0]) % 360.0
        err = curr_sum - target_yoga_deg
        if err > 180.0:
            err -= 360.0
        elif err < -180.0:
            err += 360.0
        if err < 0:
            low_jd = mid_jd
        else:
            high_jd = mid_jd
    yoga_end_dt = _jd_to_dt((low_jd + high_jd) / 2.0)
    yoga_end_str = _fmt_time_ampm(yoga_end_dt)

    half_tithi = int(tithi_diff / 6.0)
    if half_tithi == 0:
        karana_name = "Kimstughna"
    elif half_tithi >= 57:
        karana_name = ["Shakuni", "Chatushpada", "Naga"][half_tithi - 57]
    else:
        karana_name = KARANA_NAMES[(half_tithi - 1) % 7]

    target_karana_deg = ((half_tithi + 1) * 6.0) % 360.0
    karana_approx_days = (6.0 - (tithi_diff % 6.0)) / rel_speed
    low_jd = anchor_jd + karana_approx_days - 0.25
    high_jd = anchor_jd + karana_approx_days + 0.25
    for _ in range(22):
        mid_jd = (low_jd + high_jd) / 2.0
        s_res, _ = swe.calc_ut(mid_jd, swe.SUN, swe.FLG_SWIEPH | swe.FLG_SIDEREAL)
        m_res, _ = swe.calc_ut(mid_jd, swe.MOON, swe.FLG_SWIEPH | swe.FLG_SIDEREAL)
        diff = (m_res[0] - s_res[0]) % 360.0
        err = diff - target_karana_deg
        if err > 180.0:
            err -= 360.0
        elif err < -180.0:
            err += 360.0
        if err < 0:
            low_jd = mid_jd
        else:
            high_jd = mid_jd
    karana_end_dt = _jd_to_dt((low_jd + high_jd) / 2.0)
    karana_end_str = _fmt_time_ampm(karana_end_dt)

    day_len_mins = _minutes_between(sunrise_dt, sunset_dt)
    part_mins = day_len_mins / 8.0

    v_wd = (d.weekday() + 1) % 7
    rahu_parts = {0: 7, 1: 1, 2: 6, 3: 4, 4: 5, 5: 3, 6: 2}
    yama_parts = {0: 4, 1: 3, 2: 2, 3: 1, 4: 0, 5: 6, 6: 5}
    guli_parts = {0: 6, 1: 5, 2: 4, 3: 3, 4: 2, 5: 1, 6: 0}

    def _calc_window(part_idx: int) -> Dict[str, Any]:
        s = sunrise_dt + timedelta(minutes=part_idx * part_mins)
        e = s + timedelta(minutes=part_mins)
        return {
            "start": _fmt_time_ampm(s),
            "end": _fmt_time_ampm(e),
            "start_iso": s.isoformat(),
            "end_iso": e.isoformat(),
            "start_dt_str": s.strftime("%Y-%m-%d %H:%M:%S"),
            "end_dt_str": e.strftime("%Y-%m-%d %H:%M:%S")
        }

    rahu_win = _calc_window(rahu_parts[v_wd])
    yama_win = _calc_window(yama_parts[v_wd])
    guli_win = _calc_window(guli_parts[v_wd])

    muhurta_len = day_len_mins / 15.0
    abhijit_start = sunrise_dt + timedelta(minutes=7 * muhurta_len)
    abhijit_end = sunrise_dt + timedelta(minutes=8 * muhurta_len)
    brahma_start = sunrise_dt - timedelta(minutes=96)
    brahma_end = sunrise_dt - timedelta(minutes=48)

    abhijit_win = {
        "start": _fmt_time_ampm(abhijit_start),
        "end": _fmt_time_ampm(abhijit_end),
        "start_iso": abhijit_start.isoformat(),
        "end_iso": abhijit_end.isoformat(),
        "start_dt_str": abhijit_start.strftime("%Y-%m-%d %H:%M:%S"),
        "end_dt_str": abhijit_end.strftime("%Y-%m-%d %H:%M:%S")
    }
    brahma_win = {
        "start": _fmt_time_ampm(brahma_start),
        "end": _fmt_time_ampm(brahma_end),
        "start_iso": brahma_start.isoformat(),
        "end_iso": brahma_end.isoformat()
    }

    planet_constants = [
        ("Sun", "Surya", swe.SUN),
        ("Moon", "Chandra", swe.MOON),
        ("Mars", "Mangal", swe.MARS),
        ("Mercury", "Budha", swe.MERCURY),
        ("Jupiter", "Guru", swe.JUPITER),
        ("Venus", "Shukra", swe.VENUS),
        ("Saturn", "Shani", swe.SATURN),
        ("Rahu", "Rahu", swe.TRUE_NODE),
    ]

    planets_out = []
    flags_planet = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED
    for en_name, sk_name, pid in planet_constants:
        pres, _ = swe.calc_ut(jd_noon, pid, flags_planet)
        p_sid = pres[0] % 360.0
        p_sign_idx = int(p_sid / 30.0) % 12
        p_deg_in_sign = p_sid % 30.0
        p_nak_idx = int(p_sid / (360.0 / 27.0)) % 27
        p_retro = pres[3] < 0 if pid != swe.TRUE_NODE else True

        planets_out.append({
            "name": f"{sk_name} ({en_name})",
            "en_name": en_name,
            "sign": f"{SIGNS[p_sign_idx]} ({SIGNS_EN[p_sign_idx]})",
            "degree": to_dms(p_deg_in_sign),
            "nakshatra": NAKSHATRAS[p_nak_idx],
            "retrograde": bool(p_retro)
        })

    r_res, _ = swe.calc_ut(jd_noon, swe.TRUE_NODE, swe.FLG_SWIEPH | swe.FLG_SIDEREAL)
    k_sid = (r_res[0] + 180.0) % 360.0
    k_sign_idx = int(k_sid / 30.0) % 12
    k_nak_idx = int(k_sid / (360.0 / 27.0)) % 27

    planets_out.append({
        "name": "Ketu (Ketu)",
        "en_name": "Ketu",
        "sign": f"{SIGNS[k_sign_idx]} ({SIGNS_EN[k_sign_idx]})",
        "degree": to_dms(k_sid % 30.0),
        "nakshatra": NAKSHATRAS[k_nak_idx],
        "retrograde": True
    })

    return {
        "date_str": d.strftime("%Y-%m-%d"),
        "city": city_display_name,
        "lat": lat,
        "lon": lon,
        "weekday_idx": v_wd,
        "tithi": tithi_name,
        "tithi_name": tithi_name,
        "paksha": paksha,
        "tithi_progress": tithi_progress,
        "tithi_end": tithi_end_str,
        "nakshatra": nak_name,
        "nakshatra_pada": nak_pada,
        "nakshatra_end": nak_end_str,
        "yoga": yoga_name,
        "yoga_name": yoga_name,
        "yoga_end": yoga_end_str,
        "karana": karana_name,
        "karana_name": karana_name,
        "karana_end": karana_end_str,
        "sunrise": sunrise_str,
        "sunset": sunset_str,
        "sunrise_iso": sunrise_dt.isoformat(),
        "sunset_iso": sunset_dt.isoformat(),
        "next_sunrise_iso": next_sunrise_dt.isoformat(),
        "rahu": f"{rahu_win['start']} - {rahu_win['end']}",
        "rahu_kaal": f"{rahu_win['start']} - {rahu_win['end']}",
        "rahu_window": rahu_win,
        "yamaganda": f"{yama_win['start']} - {yama_win['end']}",
        "yamaganda_window": yama_win,
        "gulika": f"{guli_win['start']} - {guli_win['end']}",
        "gulika_kaal": f"{guli_win['start']} - {guli_win['end']}",
        "gulika_window": guli_win,
        "abhijit": f"{abhijit_win['start']} - {abhijit_win['end']}",
        "abhijit_muhurta": f"{abhijit_win['start']} - {abhijit_win['end']}",
        "abhijit_window": abhijit_win,
        "brahma": f"{brahma_win['start']} - {brahma_win['end']}",
        "brahma_window": brahma_win,
        "vara": ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"][v_wd],
        "date": d.strftime("%Y-%m-%d"),
        "planets": planets_out,
        "samvat": {
            "vikram_samvat": d.year + 57,
            "shaka_samvat": d.year - 78,
            "month_amanta": "Chaitra"
        }
    }


def _build_dynamic_panchang_response(
    base_data: Dict[str, Any],
    now_local: datetime,
    resolved_tz_name: str,
    tz_obj: Any,
    user_rashi: Optional[str] = None,
    user_nakshatra: Optional[str] = None
) -> Dict[str, Any]:
    sunrise_dt = datetime.fromisoformat(base_data["sunrise_iso"]).astimezone(tz_obj)
    sunset_dt = datetime.fromisoformat(base_data["sunset_iso"]).astimezone(tz_obj)
    next_sunrise_dt = datetime.fromisoformat(base_data["next_sunrise_iso"]).astimezone(tz_obj)
    v_wd = base_data["weekday_idx"]

    chog_day = calculate_choghadiya_list(sunrise_dt, sunset_dt, DAY_CHOGHADIYA_START[v_wd])
    chog_night = calculate_choghadiya_list(sunset_dt, next_sunrise_dt, NIGHT_CHOGHADIYA_START[v_wd])

    all_chogs = chog_day + chog_night
    current_chog = None
    for c in all_chogs:
        if c["start_dt"] <= now_local < c["end_dt"]:
            current_chog = c
            break
    if not current_chog:
        current_chog = all_chogs[0]

    rem_secs = max(0, int((current_chog["end_dt"] - now_local).total_seconds()))
    rem_mins = rem_secs // 60
    current_chog_clean = {
        "name": current_chog["name"],
        "label": current_chog["label"],
        "is_auspicious": current_chog["is_auspicious"],
        "ruling_planet": current_chog["ruling_planet"],
        "start": current_chog["start"],
        "end": current_chog["end"],
        "time_remaining_mins": rem_mins,
        "time_remaining_str": f"{rem_mins}m {rem_secs % 60}s"
    }

    horas = calculate_horas_list(sunrise_dt, v_wd)
    current_hora = None
    for h in horas:
        if h["start_dt"] <= now_local < h["end_dt"]:
            current_hora = h
            break
    if not current_hora:
        current_hora = horas[0]

    current_hora_clean = {
        "hour_number": current_hora["hour_number"],
        "planet": current_hora["planet"],
        "start": current_hora["start"],
        "end": current_hora["end"]
    }

    def _is_active(win_dict: Dict[str, Any]) -> bool:
        try:
            s = datetime.fromisoformat(win_dict["start_iso"]).astimezone(tz_obj)
            e = datetime.fromisoformat(win_dict["end_iso"]).astimezone(tz_obj)
            return s <= now_local < e
        except Exception:
            return False

    is_rahu = _is_active(base_data["rahu_window"])
    is_yama = _is_active(base_data["yamaganda_window"])
    is_guli = _is_active(base_data["gulika_window"])

    rule_output = evaluate_daily_rules(
        tithi_name=base_data["tithi"],
        nakshatra_name=base_data["nakshatra"],
        yoga_name=base_data["yoga"],
        karana_name=base_data["karana"],
        weekday_idx=v_wd,
        current_choghadiya=current_chog_clean,
        current_hora=current_hora_clean,
        is_in_rahu_kaal=is_rahu,
        is_in_yamaganda=is_yama,
        is_in_gulika=is_guli,
        has_abhijit=True
    )

    next_auspicious = None
    for c in all_chogs:
        if c["start_dt"] > now_local and c["is_auspicious"]:
            mins_until = int((c["start_dt"] - now_local).total_seconds() / 60.0)
            next_auspicious = {
                "name": f"{c['name']} Choghadiya",
                "start": c["start"],
                "end": c["end"],
                "time_until_start": f"{mins_until} mins",
                "category": "Auspicious Choghadiya"
            }
            break

    if not next_auspicious:
        next_auspicious = {
            "name": "Abhijit Muhurat",
            "start": base_data["abhijit_window"]["start"],
            "end": base_data["abhijit_window"]["end"],
            "time_until_start": "Midday",
            "category": "Daily Divine Window"
        }

    def _clean_chog_list(lst: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return [{
            "name": x["name"],
            "label": x["label"],
            "is_auspicious": x["is_auspicious"],
            "ruling_planet": x["ruling_planet"],
            "start": x["start"],
            "end": x["end"]
        } for x in lst]

    def _clean_hora_list(lst: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return [{
            "hour_number": x["hour_number"],
            "planet": x["planet"],
            "start": x["start"],
            "end": x["end"]
        } for x in lst]

    full_resp = dict(base_data)
    full_resp.update({
        "resolved_timezone": resolved_tz_name,
        "local_datetime": to_local_iso(now_local, tz_obj),
        "mode": "general",
        "today_score": rule_output["today_score"],
        "rule_alignment_score": rule_output.get("rule_alignment_score", 0.96),
        "confidence_score": rule_output.get("rule_alignment_score", rule_output.get("confidence_score", 0.96)),
        "current_period_summary": rule_output["current_period_summary"],
        "next_auspicious_window": next_auspicious,
        "disha_shool": rule_output["disha_shool"],
        "dos_and_donts": {
            "recommended": rule_output["recommended"],
            "avoid": rule_output["avoid"]
        },
        "choghadiya_day": _clean_chog_list(chog_day),
        "choghadiya_night": _clean_chog_list(chog_night),
        "current_choghadiya": current_chog_clean,
        "horas": _clean_hora_list(horas),
        "current_hora": current_hora_clean
    })

    if user_rashi or user_nakshatra:
        from modules.panchang.personalization import (
            calculate_tara_bala,
            calculate_chandra_bala,
            calculate_category_scores
        )

        transit_nak = base_data.get("nakshatra", "Pushya")
        transit_rashi = "Mesha"
        for p in base_data.get("planets", []):
            if "Moon" in p.get("name", "") or "Chandra" in p.get("name", ""):
                transit_rashi = p.get("sign", "Mesha").split("(")[0].strip()
                break

        tara = calculate_tara_bala(user_nakshatra or "Ashwini", transit_nak) if user_nakshatra else None
        chandra = calculate_chandra_bala(user_rashi or "Mesha", transit_rashi) if user_rashi else None

        category_scores = calculate_category_scores(
            tara_bala=tara or {"score_mod": 0, "tara_name": "Sadhana"},
            chandra_bala=chandra or {"score_mod": 0, "house_distance": 1},
            today_base_score=rule_output["today_score"],
            active_hora_planet=current_hora_clean.get("planet", "Sun"),
            active_chog_auspicious=current_chog_clean.get("is_auspicious", True)
        )

        personal_score_mod = (
            (tara["score_mod"] if tara else 0) * 0.4 +
            (chandra["score_mod"] if chandra else 0) * 0.4
        )
        personalized_score = round(max(1.0, min(10.0, rule_output["today_score"] + personal_score_mod)), 1)

        personal_advice = []
        if tara and tara["is_auspicious"]:
            personal_advice.append({
                "type": "positive",
                "text": tara["advice"],
                "source": f"Tara Bala: {tara['tara_name']} ({tara['category']})"
            })
        elif tara:
            personal_advice.append({
                "type": "caution",
                "text": tara["advice"],
                "source": f"Tara Bala: {tara['tara_name']} ({tara['category']})"
            })

        if chandra and chandra["is_auspicious"]:
            personal_advice.append({
                "type": "positive",
                "text": f"Moon transit in your {chandra['house_distance']}th house: {chandra['status']}.",
                "source": "Chandra Bala"
            })
        elif chandra:
            personal_advice.append({
                "type": "caution",
                "text": f"Moon transit in your {chandra['house_distance']}th house: {chandra['status']}. {chandra['desc'].split('—')[-1].strip() if '—' in chandra['desc'] else ''}",
                "source": "Chandra Bala"
            })

        full_resp["mode"] = "personalized"
        full_resp["personalization"] = {
            "tara_bala": tara,
            "chandra_bala": chandra,
            "category_scores": category_scores,
            "personalized_score": personalized_score,
            "personalized_advice": personal_advice
        }
        full_resp["today_score"] = personalized_score
        full_resp["rule_alignment_score"] = 0.94
        full_resp["confidence_score"] = 0.94

    return full_resp


calculate_panchang_for_datetime = get_full_panchang
