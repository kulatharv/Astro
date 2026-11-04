"""
Divisional Charts (Varga) Engine: Navamsa (D9), Dashamsha (D10), etc.
"""

from collections import defaultdict
from datetime import datetime
import swisseph as swe

from shared.veda.zodiac import SIGNS_SK, SIGN_LORDS, degree_to_sign
from modules.kundali.planets import calculate_all_planets
from modules.kundali.houses import calculate_lagna, assign_house, assign_bhava_house
from shared.veda.nakshatra import calculate_nakshatra
from shared.veda.strength import final_strength, calculate_weighted_strength
from modules.kundali.dasha import calculate_mahadasha, generate_dasha_timeline
from shared.veda.aspects import calculate_vedic_aspects

# 9 Navamsa parts per sign (3°20' each)
NAVAMSA_START = {
    # Fire signs (Mesha, Simha, Dhanu) start from Mesha (0)
    0: 0, 4: 0, 8: 0,
    # Earth signs (Vrishabha, Kanya, Makara) start from Makara (9)
    1: 9, 5: 9, 9: 9,
    # Air signs (Mithuna, Tula, Kumbha) start from Tula (6)
    2: 6, 6: 6, 10: 6,
    # Water signs (Karka, Vrischika, Meena) start from Karka (3)
    3: 3, 7: 3, 11: 3,
}

PADA_DEG = 30.0 / 9.0  # 3.3333333333333335 degrees


def calculate_navamsa(longitude: float) -> str:
    """
    Calculate the D9 Navamsa sign name for a given absolute longitude degree (0-360).
    """
    norm_deg = longitude % 360.0
    sign_idx = int(norm_deg / 30.0)
    deg_in_sign = norm_deg % 30.0

    pada = int(deg_in_sign / PADA_DEG)
    start_sign = NAVAMSA_START[sign_idx]
    nav_idx = (start_sign + pada) % 12

    return SIGNS_SK[nav_idx]


def calculate_navamsa_sign(longitude: float) -> str:
    """Alias for calculate_navamsa."""
    return calculate_navamsa(longitude)


def calculate_house_lords(lagna_sign: str) -> dict[int, str]:
    """Calculate the planetary ruler for each of the 12 houses from Lagna."""
    lagna_idx = SIGNS_SK.index(lagna_sign) if lagna_sign in SIGNS_SK else 0
    lords = {}
    for h in range(1, 13):
        sign = SIGNS_SK[(lagna_idx + h - 1) % 12]
        lords[h] = SIGN_LORDS.get(sign, "Mars")
    return lords


def classify_functional_nature(lagna_sign: str, house_lords: dict[int, str]) -> dict:
    """Classify functional benefics, malefics, and yogakarakas for a given Lagna."""
    benefics = []
    malefics = []
    neutral = []

    for h, lord in house_lords.items():
        if h in (1, 5, 9) and lord not in benefics:
            benefics.append(lord)
        elif h in (6, 8, 12) and lord not in malefics and lord not in benefics:
            malefics.append(lord)
        elif lord not in neutral and lord not in benefics and lord not in malefics:
            neutral.append(lord)

    return {
        "functional_benefics": benefics,
        "functional_malefics": malefics,
        "neutral": neutral,
    }


def calculate_dispositors(chart: dict) -> dict[str, str]:
    """Calculate the sign dispositor (ruler of sign occupied) for each planet."""
    dispositors = {}
    planets_by_house = chart.get("planets_by_house", {})
    for h, p_list in planets_by_house.items():
        for p in p_list:
            name = p.get("planet")
            sign = p.get("sign")
            disp = SIGN_LORDS.get(sign, "Mars")
            dispositors[name] = disp
    return dispositors


def evaluate_event(chart: dict, event_type: str) -> dict:
    """Evaluate overall score, confidence, and level for an event (marriage / career)."""
    weights = chart.get("planet_strength_scores", {})
    if event_type == "marriage":
        v_score = weights.get("Venus", 6.0)
        j_score = weights.get("Jupiter", 6.0)
        raw_score = (v_score * 0.6 + j_score * 0.4) * 10.0
    else:  # career
        s_score = weights.get("Sun", 6.0)
        sat_score = weights.get("Saturn", 6.0)
        m_score = weights.get("Mars", 6.0)
        raw_score = (s_score * 0.4 + sat_score * 0.4 + m_score * 0.2) * 10.0

    score = round(max(30.0, min(95.0, raw_score)), 1)
    if score >= 75:
        level = "Strong"
    elif score >= 55:
        level = "Moderate"
    else:
        level = "Challenging"

    reasons = [
        f"Key karaka planetary strength evaluated at {score}% vitality.",
        f"Active Mahadasha period shaping current karmic cycle.",
    ]

    return {
        "event": event_type,
        "score": score,
        "alignment_strength": 88.0,
        "level": level,
        "reasons": reasons,
    }


def build_event_explanation(chart: dict, event_type: str) -> str:
    """Build a concise, classical interpretation for an event."""
    pred = evaluate_event(chart, event_type)
    lagna = chart.get("basic_details", {}).get("lagna", "Mesha")
    md = chart.get("dasha", {}).get("current_mahadasha", "Jupiter")
    return (
        f"With {lagna} Lagna and {md} Mahadasha currently operating, {event_type} potential is {pred['level']} "
        f"(vitality score: {pred['score']}/100). Focus on favorable astrological windows for optimal success."
    )


def generate_full_chart(
    year: int,
    month: int,
    day: int,
    hour: float,
    latitude: float,
    longitude: float,
    timezone_offset: float = 5.5,
    tz_name: str | None = None,
) -> dict:
    """
    Generate comprehensive birth chart for prediction and AI reasoning.
    Supports timezone offset and IANA tz_name conversions.
    """
    from shared.timezone.tz import to_utc_jd

    int_hour = int(hour)
    int_minute = int(round((hour - int_hour) * 60.0))
    if int_minute >= 60:
        int_hour += 1
        int_minute -= 60

    _, _, _, _, jd = to_utc_jd(
        year=year,
        month=month,
        day=day,
        hour=int_hour,
        minute=int_minute,
        tz_name=tz_name,
        tz_offset=timezone_offset,
    )

    swe.set_sid_mode(swe.SIDM_LAHIRI)

    planet_positions = calculate_all_planets(jd)
    asc_degree, lagna_sign = calculate_lagna(jd, latitude, longitude)
    house_lords = calculate_house_lords(lagna_sign)
    functional_nature = classify_functional_nature(lagna_sign, house_lords)

    house_data = defaultdict(list)
    for planet, degree in planet_positions.items():
        sign, sign_degree = degree_to_sign(degree)
        navamsa_sign = calculate_navamsa(degree)
        strength = final_strength(planet, sign, navamsa_sign)
        rasi_house = assign_house(sign, lagna_sign)
        bhava_house = assign_bhava_house(jd, latitude, longitude, degree)
        nak, pada = calculate_nakshatra(degree)

        house_data[rasi_house].append({
            "planet": planet,
            "degree": round(sign_degree, 2),
            "sign": sign,
            "navamsa": navamsa_sign,
            "nakshatra": nak,
            "pada": pada,
            "bhava_house": bhava_house,
            "strength": strength,
        })

    planets_by_house = dict(house_data)

    moon_longitude = planet_positions.get("Moon", 0.0)
    moon_nak, _ = calculate_nakshatra(moon_longitude)
    dasha_lord, balance = calculate_mahadasha(moon_longitude, moon_nak)
    timeline = generate_dasha_timeline(dasha_lord, balance)

    chart = {
        "basic_details": {
            "date": f"{day:02d}-{month:02d}-{year}",
            "time": hour,
            "lagna": lagna_sign,
        },
        "planets_by_house": planets_by_house,
        "house_lords": house_lords,
        "dasha": {
            "current_mahadasha": dasha_lord,
            "balance_years": round(balance, 2),
            "timeline": timeline,
        },
        "activated_houses": [1, 5, 9, 10],
        "functional_nature": functional_nature,
    }

    chart["dispositors"] = calculate_dispositors(chart)
    chart["vedic_aspects"] = calculate_vedic_aspects(chart)

    try:
        from modules.prediction.transits import calculate_transits
        from shared.veda.yogas import detect_advanced_yogas
        from modules.prediction.timing import evaluate_event_trigger


        today = datetime.today()
        chart["current_transits"] = calculate_transits(chart, today.year, today.month, today.day)
        chart["marriage_timing"] = evaluate_event_trigger(chart, "marriage")
        chart["career_timing"] = evaluate_event_trigger(chart, "career")
        chart["advanced_yogas"] = detect_advanced_yogas(chart)
    except Exception:
        pass

    chart["planet_strength_scores"] = calculate_weighted_strength(chart)
    chart["marriage_prediction"] = evaluate_event(chart, "marriage")
    chart["career_prediction"] = evaluate_event(chart, "career")
    chart["marriage_explanation"] = build_event_explanation(chart, "marriage")
    chart["career_explanation"] = build_event_explanation(chart, "career")

    return chart
