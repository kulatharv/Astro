"""Master Kundali Engine assembling Rasi, Navamsa D9, Dasha, Yogas, Doshas, and Scores."""

from datetime import datetime, timedelta
import swisseph as swe

from shared.veda.zodiac import SIGNS_SK, SIGN_LORDS, to_dms
from shared.veda.nakshatra import calculate_nakshatra
from modules.kundali.varga import calculate_navamsa
from shared.veda.strength import planet_strength_label
from modules.kundali.dasha import calculate_mahadasha, generate_antardasha, generate_dasha_timeline
from shared.veda.yogas import calculate_yogas
from shared.veda.doshas import calculate_doshas

PLANET_LIST = [
    ("Sun", swe.SUN),
    ("Moon", swe.MOON),
    ("Mars", swe.MARS),
    ("Mercury", swe.MERCURY),
    ("Jupiter", swe.JUPITER),
    ("Venus", swe.VENUS),
    ("Saturn", swe.SATURN),
    ("Rahu", swe.TRUE_NODE),
]

TITHI_NAMES = [
    "Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami",
    "Shashthi", "Saptami", "Ashtami", "Navami", "Dashami",
    "Ekadashi", "Dwadashi", "Trayodashi", "Chaturdashi", "Purnima",
    "Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami",
    "Shashthi", "Saptami", "Ashtami", "Navami", "Dashami",
    "Ekadashi", "Dwadashi", "Trayodashi", "Chaturdashi", "Amavasya",
]

YOGA_NAMES = [
    "Vishkambha", "Preeti", "Ayushman", "Saubhagya", "Shobhana",
    "Atiganda", "Sukarma", "Dhriti", "Shoola", "Ganda", "Vriddhi",
    "Dhruva", "Vyaghata", "Harshana", "Vajra", "Siddhi", "Vyatipata",
    "Variyana", "Parigha", "Shiva", "Siddha", "Sadhya", "Shubha",
    "Shukla", "Brahma", "Indra", "Vaidhriti",
]

KARANA_NAMES = ["Bava", "Balava", "Kaulava", "Taitila", "Garaja", "Vanija", "Vishti"]


def calculate_chart_scores(planets: list[dict], lagna_sign: str, houses: dict) -> dict[str, int]:
    """Calculate normalized scores (0-100) across all life areas."""
    pmap = {p.get("name"): p for p in planets}
    KENDRA = {1, 4, 7, 10}
    TRIKONA = {1, 5, 9}
    DUSTHANA = {6, 8, 12}
    lagna_idx = SIGNS_SK.index(lagna_sign) if lagna_sign in SIGNS_SK else 0

    def ps(name: str) -> float:
        p = pmap.get(name)
        if not p:
            return 5.0
        label = p.get("strength", "Neutral")
        b = 10.0 if "Exalted" in label else 8.0 if "Own" in label else 2.0 if "Debilitated" in label else 5.0
        h = p.get("house", 1)
        if isinstance(h, int):
            if h in KENDRA or h in TRIKONA:
                b += 1.0
            elif h in DUSTHANA:
                b -= 1.5
        if p.get("retrograde"):
            b -= 0.5
        return max(1.0, min(10.0, b))

    def lord_of(house_num: int) -> str:
        return SIGN_LORDS.get(SIGNS_SK[(lagna_idx + house_num - 1) % 12], "Mars")

    overall = sum(ps(p) for p in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"])
    career = ps("Sun") * 1.5 + ps("Saturn") * 1.5 + ps("Mars") + ps(lord_of(10)) * 2.0
    finance = ps("Jupiter") * 2.0 + ps("Venus") * 1.5 + ps(lord_of(2)) * 1.5 + ps(lord_of(11))
    marriage = ps("Venus") * 2.0 + ps("Jupiter") * 1.5 + ps(lord_of(7)) * 2.0 + ps("Moon") * 0.5
    health = ps("Sun") * 1.5 + ps("Mars") * 1.5 + ps(lord_of(1)) * 2.0 + ps(lord_of(6))
    mental = ps("Moon") * 2.5 + ps("Mercury") * 2.0 + ps(lord_of(4)) * 1.5
    ketu_h = pmap.get("Ketu", {}).get("house", 1)
    spirit = ps("Jupiter") * 2.0 + ps(lord_of(9)) * 2.0 + (7.0 if ketu_h in {1, 5, 9, 12} else 5.0)

    def norm(val: float, denom: float) -> int:
        return round(min((val / denom) * 100.0, 100.0))

    return {
        "overall_strength": norm(overall, 70.0),
        "career_score": norm(career, 60.0),
        "finance_score": norm(finance, 60.0),
        "marriage_score": norm(marriage, 60.0),
        "health_score": norm(health, 60.0),
        "mental_score": norm(mental, 60.0),
        "spirituality_score": norm(spirit, 40.0),
    }


from typing import Optional
from shared.timezone.tz import to_utc_jd


def calculate_kundali(
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int,
    lat: float,
    lon: float,
    second: int = 0,
    timezone_offset: Optional[float] = None,
    tz_name: Optional[str] = None,
) -> dict:
    """
    Master Kundali engine returning complete Rasi, Navamsa D9, Panchang, Dasha, Yogas, Doshas, and Scores.
    Converts local wall-clock date/time to UTC Julian Day via IANA timezone name or numeric offset.
    Defaults to Indian Standard Time (UTC+5:30) if neither tz_name nor timezone_offset is provided.
    """
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED

    _, _, _, _, jd = to_utc_jd(
        year=year,
        month=month,
        day=day,
        hour=hour,
        minute=minute,
        second=second,
        tz_name=tz_name,
        tz_offset=timezone_offset,
    )

    cusps, ascmc = swe.houses_ex(jd, lat, lon, b'W', flags)
    lagna_lon = ascmc[0] % 360.0
    lagna_idx = int(lagna_lon / 30.0)
    lagna_sign = SIGNS_SK[lagna_idx]
    lagna_nak, lagna_pada = calculate_nakshatra(lagna_lon)

    houses = {i: [] for i in range(1, 13)}
    houses[1].append("Lagna")
    planet_data = []

    rahu_raw = 0.0

    for name, planet_id in PLANET_LIST:
        data = swe.calc_ut(jd, planet_id, flags)
        raw_lon = data[0][0] % 360.0
        speed = data[0][3]

        if name == "Rahu":
            rahu_raw = raw_lon

        sign_idx = int(raw_lon / 30.0)
        sign_name = SIGNS_SK[sign_idx]
        house_num = ((sign_idx - lagna_idx) % 12) + 1
        nak_name, pada = calculate_nakshatra(raw_lon)
        nav_sign = calculate_navamsa(raw_lon)
        strength = planet_strength_label(name, sign_name)

        houses[house_num].append(name)
        planet_data.append({
            "name": name,
            "sign": sign_name,
            "degree": to_dms(raw_lon % 30.0),
            "degree_decimal": round(raw_lon % 30.0, 4),
            "house": house_num,
            "nakshatra": nak_name,
            "pada": pada,
            "navamsa": nav_sign,
            "strength": strength,
            "retrograde": speed < 0 or name in ("Rahu", "Ketu"),
            "_raw_lon": raw_lon,
        })

    ketu_lon = (rahu_raw + 180.0) % 360.0
    ketu_sign_idx = int(ketu_lon / 30.0)
    ketu_sign = SIGNS_SK[ketu_sign_idx]
    ketu_house = ((ketu_sign_idx - lagna_idx) % 12) + 1
    ketu_nak, ketu_pada = calculate_nakshatra(ketu_lon)

    houses[ketu_house].append("Ketu")
    planet_data.append({
        "name": "Ketu",
        "sign": ketu_sign,
        "degree": to_dms(ketu_lon % 30.0),
        "degree_decimal": round(ketu_lon % 30.0, 4),
        "house": ketu_house,
        "nakshatra": ketu_nak,
        "pada": ketu_pada,
        "navamsa": calculate_navamsa(ketu_lon),
        "strength": planet_strength_label("Ketu", ketu_sign),
        "retrograde": True,
        "_raw_lon": ketu_lon,
    })

    sun_lon = next(p["_raw_lon"] for p in planet_data if p["name"] == "Sun")
    moon_lon = next(p["_raw_lon"] for p in planet_data if p["name"] == "Moon")
    diff = (moon_lon - sun_lon) % 360.0

    tithi_num = int(diff / 12.0) + 1
    tithi_name = TITHI_NAMES[(tithi_num - 1) % 30]
    paksha = "Shukla" if tithi_num <= 15 else "Krishna"
    moon_nak, moon_pada = calculate_nakshatra(moon_lon)
    yoga_name = YOGA_NAMES[int(((sun_lon + moon_lon) % 360.0) / (360.0 / 27.0)) % 27]
    karana_name = KARANA_NAMES[int(diff / 6.0) % 7]
    ayanamsa = swe.get_ayanamsa(jd)

    maha_lord, balance_years = calculate_mahadasha(moon_lon, moon_nak)
    antardasha = generate_antardasha(maha_lord)

    d9_houses = {i: [] for i in range(1, 13)}
    d9_lagna_nav = calculate_navamsa(lagna_lon)
    d9_lagna_idx = SIGNS_SK.index(d9_lagna_nav)
    d9_houses[1].append("Lagna")

    for p in planet_data:
        nav = p.get("navamsa", "")
        if nav in SIGNS_SK:
            nav_idx = SIGNS_SK.index(nav)
            d9_h = ((nav_idx - d9_lagna_idx) % 12) + 1
            d9_houses[d9_h].append(p["name"])

    planets_out = [{k: v for k, v in p.items() if k != "_raw_lon"} for p in planet_data]
    scores = calculate_chart_scores(planet_data, lagna_sign, houses)
    yogas = calculate_yogas(planet_data, lagna_sign, houses)
    doshas = calculate_doshas(planet_data, lagna_sign, houses)

    lagna_deg_in_sign = lagna_lon % 30.0
    is_near_boundary = lagna_deg_in_sign < 2.0 or lagna_deg_in_sign > 28.0
    boundary_warning = (
        f"Lagna (Ascendant) is situated at {round(lagna_deg_in_sign, 2)}° near a sign boundary (0°-2° or 28°-30°). "
        "Chart sensitivity is elevated; verify birth time precision within ±10 minutes for optimal stability."
        if is_near_boundary else "Lagna is comfortably positioned within sign boundaries."
    )

    return {
        "lagna": lagna_sign,
        "lagna_degree": to_dms(lagna_deg_in_sign),
        "lagna_degree_decimal": round(lagna_deg_in_sign, 4),
        "lagna_nakshatra": lagna_nak,
        "lagna_pada": lagna_pada,
        "is_near_boundary": is_near_boundary,
        "boundary_warning": boundary_warning,
        "time_sensitivity_note": "Ascendant degrees shift approximately 1° every 4 minutes. If exact birth time is uncertain, domain score boundaries may vary.",
        "houses": houses,
        "d9_houses": d9_houses,
        "d9_lagna": d9_lagna_nav,
        "planets": planets_out,
        "tithi_number": tithi_num,
        "tithi_name": tithi_name,
        "paksha": paksha,
        "nakshatra": moon_nak,
        "nakshatra_pada": moon_pada,
        "yoga_name": yoga_name,
        "karana_name": karana_name,
        "ayanamsa": round(ayanamsa, 4),
        "jd": round(jd, 6),
        "mahadasha": maha_lord,
        "dasha_balance": f"{balance_years:.1f} years",
        "dasha_balance_float": round(balance_years, 4),
        "antardasha": antardasha[0]["lord"] if antardasha else "",
        "antardasha_list": antardasha,
        "birth_datetime": datetime(year, month, day, hour, minute, second).isoformat(),
        "birth_date": f"{year:04d}-{month:02d}-{day:02d}",
        "birth_year": year,
        "birth_month": month,
        "birth_day": day,
        "birth_hour": hour,
        "birth_minute": minute,
        "dasha": {
            "current_mahadasha": maha_lord,
            "balance_years": round(balance_years, 4),
            "timeline": generate_dasha_timeline(maha_lord, balance_years),
            "birth_datetime": datetime(year, month, day, hour, minute, second).isoformat(),
        },
        "scores": scores,
        "yogas": yogas,
        "doshas": doshas,
    }
