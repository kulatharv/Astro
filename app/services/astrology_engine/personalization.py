"""
Vedic Personalization & Decision Engine.
Calculates:
1. Tara Bala (9 Cosmic Tara categories from Natal Nakshatra).
2. Chandra Bala (Natal Moon to Transit Moon house alignment).
3. 5-Domain Category Auspiciousness Scores (Career, Finance, Love, Health, Spiritual).
4. Personalized Do's & Don'ts and Personalized Today Score.
5. Deterministic, explainable Decision Assistant for key real-world activities.
6. Natal Moon & Nakshatra derivation from birth parameters.
"""

from datetime import datetime, date, time, timezone, timedelta
from typing import Dict, Any, List, Optional, Tuple
import zoneinfo
import swisseph as swe

from app.services.astrology_engine.nakshatra import NAKSHATRAS
from app.services.astrology_engine.zodiac import SIGNS, SIGNS_EN
from app.services.astrology_engine.cities import get_city

try:
    from shared.timezone.tz import resolve_timezone
except ImportError:
    IST_TZ = timezone(timedelta(hours=5, minutes=30), name="IST")
    def resolve_timezone(lat=None, lon=None, tz_str=None, tz_name=None, city_name=None, **kwargs):
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

# ── 9 Classical Tara Bala Categories ───────────────────────────────────────────
TARA_BALA_MAP = {
    1: {
        "name": "Janma",
        "category": "Body / Self",
        "is_auspicious": False,
        "score_mod": -0.5,
        "desc": "Janma Tara: Demands physical energy and discipline. Average for high-risk ventures.",
        "advice": "Focus on personal wellness, routine tasks, and spiritual grounding."
    },
    2: {
        "name": "Sampat",
        "category": "Wealth & Gains",
        "is_auspicious": True,
        "score_mod": +1.5,
        "desc": "Sampat Tara: Highly auspicious for financial prosperity, asset growth, and profits.",
        "advice": "Excellent for financial investments, contracts, business deals, and acquisitions."
    },
    3: {
        "name": "Vipat",
        "category": "Danger & Losses",
        "is_auspicious": False,
        "score_mod": -2.0,
        "desc": "Vipat Tara: Prone to unexpected hurdles, misunderstandings, and expenditure.",
        "advice": "Exercise caution in financial commitments, avoid speculative risks, drive safely."
    },
    4: {
        "name": "Kshema",
        "category": "Security & Well-being",
        "is_auspicious": True,
        "score_mod": +1.2,
        "desc": "Kshema Tara: Protects health, domestic harmony, stability, and family well-being.",
        "advice": "Favorable for home improvements, family decisions, health therapies, and travel."
    },
    5: {
        "name": "Pratyak",
        "category": "Opposition & Delays",
        "is_auspicious": False,
        "score_mod": -1.5,
        "desc": "Pratyak Tara: Potential for minor conflicts, friction, or administrative delays.",
        "advice": "Avoid confrontations, review legal documents carefully, maintain patience."
    },
    6: {
        "name": "Sadhana",
        "category": "Achievement & Success",
        "is_auspicious": True,
        "score_mod": +1.8,
        "desc": "Sadhana Tara: Fulfills ambitions, complex projects, and spiritual sadhana.",
        "advice": "Supreme for executing important goals, signing agreements, and competitive ventures."
    },
    7: {
        "name": "Naidhana (Vadh)",
        "category": "Severe Obstacle",
        "is_auspicious": False,
        "score_mod": -2.5,
        "desc": "Naidhana Tara: High friction period. Avoid initiating critical life events.",
        "advice": "Defer non-essential elective commitments, high-stakes contracts, or major asset purchases today."
    },
    8: {
        "name": "Mitra",
        "category": "Friendly & Supportive",
        "is_auspicious": True,
        "score_mod": +1.2,
        "desc": "Mitra Tara: Fosters camaraderie, fruitful partnerships, and pleasant discussions.",
        "advice": "Great for networking, romantic dates, client meetings, and social gatherings."
    },
    9: {
        "name": "Param Mitra",
        "category": "Supreme Friend / Grace",
        "is_auspicious": True,
        "score_mod": +1.8,
        "desc": "Param Mitra Tara: Bestows immense cosmic backing, divine grace, and joy.",
        "advice": "Ideal for spiritual initiation, major breakthroughs, and celebration of milestones."
    }
}

CHANDRA_BALA_RULES = {
    1: {"is_auspicious": True, "score_mod": +1.0, "status": "Strong Self", "desc": "Moon transits your 1st House (Lagna) — High vitality, clarity, and personal charisma."},
    2: {"is_auspicious": False, "score_mod": 0.0, "status": "Moderate Wealth", "desc": "Moon transits your 2nd House — Good for family discussions, moderate for expenditures."},
    3: {"is_auspicious": True, "score_mod": +1.2, "status": "Courage & Victory", "desc": "Moon transits your 3rd House — Excellent initiative, courage, short journeys, and gains."},
    4: {"is_auspicious": False, "score_mod": -1.2, "status": "Mental Caution", "desc": "Moon transits your 4th House (Kantaka) — Emotional sensitivity, avoid hasty domestic or vehicle decisions."},
    5: {"is_auspicious": False, "score_mod": +0.2, "status": "Intellectual Focus", "desc": "Moon transits your 5th House — Favorable for learning, creativity, and spiritual chanting."},
    6: {"is_auspicious": True, "score_mod": +1.5, "status": "Victory over Obstacles", "desc": "Moon transits your 6th House — Overcomes rivals, debts, and obstacles. Good for health recovery."},
    7: {"is_auspicious": True, "score_mod": +1.0, "status": "Partnership Harmony", "desc": "Moon transits your 7th House — Fosters enjoyable social interactions and partner alignment."},
    8: {"is_auspicious": False, "score_mod": -2.0, "status": "Ashtama Chandra (High Caution)", "desc": "Moon transits your 8th House (Ashtama) — Transitory lunar phase favoring introspection. A time for extra care, rest, and mindfulness."},
    9: {"is_auspicious": False, "score_mod": +0.5, "status": "Dharma & Learning", "desc": "Moon transits your 9th House — Auspicious for temples, pilgrimage, and advisory work."},
    10: {"is_auspicious": True, "score_mod": +1.5, "status": "Career & Authority", "desc": "Moon transits your 10th House — Supreme for professional success, leadership, and recognition."},
    11: {"is_auspicious": True, "score_mod": +1.5, "status": "Fulfillment of Desires", "desc": "Moon transits your 11th House (Labha) — Inflow of profits, joyful news, and goal completion."},
    12: {"is_auspicious": False, "score_mod": -1.5, "status": "Loss & Fatigue", "desc": "Moon transits your 12th House (Vyaya) — High expenses and fatigue. Rest and practice meditation."}
}


def calculate_tara_bala(natal_nakshatra: str, transit_nakshatra: str) -> Dict[str, Any]:
    if natal_nakshatra not in NAKSHATRAS or transit_nakshatra not in NAKSHATRAS:
        return {
            "tara_number": 6,
            "tara_name": "Sadhana",
            "category": "Achievement",
            "is_auspicious": True,
            "score_mod": 1.0,
            "desc": "Favorable stellar alignment supporting your efforts.",
            "advice": "Engage with planned activities with steady focus."
        }

    natal_idx = NAKSHATRAS.index(natal_nakshatra)
    transit_idx = NAKSHATRAS.index(transit_nakshatra)

    count = ((transit_idx - natal_idx) % 27) + 1
    tara_num = ((count - 1) % 9) + 1
    tara_data = TARA_BALA_MAP.get(tara_num, TARA_BALA_MAP[6])

    return {
        "tara_number": tara_num,
        "tara_name": tara_data["name"],
        "category": tara_data["category"],
        "is_auspicious": tara_data["is_auspicious"],
        "score_mod": tara_data["score_mod"],
        "desc": tara_data["desc"],
        "advice": tara_data["advice"]
    }


def calculate_chandra_bala(natal_rashi: str, transit_rashi: str) -> Dict[str, Any]:
    def _find_sign_idx(s: str) -> int:
        if not s:
            return 0
        s_clean = s.split()[0].replace("(", "").replace(")", "").strip()
        for idx, (sk, en) in enumerate(zip(SIGNS, SIGNS_EN)):
            if s_clean.lower() in (sk.lower(), en.lower()):
                return idx
        return 0

    natal_idx = _find_sign_idx(natal_rashi)
    transit_idx = _find_sign_idx(transit_rashi)

    house_distance = ((transit_idx - natal_idx) % 12) + 1
    rule = CHANDRA_BALA_RULES.get(house_distance, CHANDRA_BALA_RULES[1])

    return {
        "house_distance": house_distance,
        "is_auspicious": rule["is_auspicious"],
        "status": rule["status"],
        "score_mod": rule["score_mod"],
        "desc": rule["desc"]
    }


def calculate_category_scores(
    tara_bala: Dict[str, Any],
    chandra_bala: Dict[str, Any],
    today_base_score: float,
    active_hora_planet: str = "Jupiter",
    active_chog_auspicious: bool = True
) -> Dict[str, float]:
    t_mod = tara_bala.get("score_mod", 0.0)
    c_mod = chandra_bala.get("score_mod", 0.0)
    h_dist = chandra_bala.get("house_distance", 1)

    def _clamp(val: float) -> float:
        return round(max(1.0, min(10.0, val)), 1)

    base = today_base_score

    career = base + (c_mod * 0.7) + (t_mod * 0.5)
    if h_dist in (10, 11, 6, 1):
        career += 0.8
    if active_hora_planet in ("Sun", "Mars", "Jupiter"):
        career += 0.5

    finance = base + (t_mod * 0.8) + (c_mod * 0.5)
    if h_dist in (11, 2, 9):
        finance += 0.8
    if tara_bala.get("tara_name") == "Sampat":
        finance += 1.2
    if active_hora_planet in ("Jupiter", "Venus", "Mercury"):
        finance += 0.5

    relationships = base + (c_mod * 0.6) + (t_mod * 0.6)
    if h_dist in (7, 5, 1):
        relationships += 0.8
    if tara_bala.get("tara_name") in ("Mitra", "Param Mitra", "Kshema"):
        relationships += 0.8
    if active_hora_planet in ("Venus", "Moon", "Jupiter"):
        relationships += 0.5

    health = base + (c_mod * 0.8) + (t_mod * 0.4)
    if h_dist in (1, 3, 11):
        health += 0.6
    if h_dist in (8, 12, 4):
        health -= 1.0
    if tara_bala.get("tara_name") in ("Naidhana (Vadh)", "Vipat"):
        health -= 1.2

    spiritual = base + (t_mod * 0.6) + 0.5
    if h_dist in (9, 5, 1, 12):
        spiritual += 0.8
    if active_hora_planet in ("Jupiter", "Sun", "Moon"):
        spiritual += 0.7

    return {
        "career": _clamp(career),
        "finance": _clamp(finance),
        "relationships": _clamp(relationships),
        "health": _clamp(health),
        "spiritual": _clamp(spiritual)
    }


def evaluate_decision(
    activity_type: str,
    user_rashi: Optional[str],
    user_nakshatra: Optional[str],
    current_panchang: Dict[str, Any]
) -> Dict[str, Any]:
    act = (activity_type or "investment").lower().strip()
    
    transit_nak = current_panchang.get("nakshatra", "Pushya")
    transit_rashi = "Mesha"
    for p in current_panchang.get("planets", []):
        if "Moon" in p.get("name", ""):
            transit_rashi = p.get("sign", "Mesha")
            break

    has_profile = bool(user_rashi and user_nakshatra)
    tara = calculate_tara_bala(user_nakshatra, transit_nak) if user_nakshatra else None
    chandra = calculate_chandra_bala(user_rashi, transit_rashi) if user_rashi else None

    curr_chog = current_panchang.get("current_choghadiya", {})
    curr_hora = current_panchang.get("current_hora", {})
    is_rahu = "Rahu" in current_panchang.get("current_period_summary", "") or curr_chog.get("name") in ("Rog", "Kaal")
    disha = current_panchang.get("disha_shool", {})
    today_score = current_panchang.get("today_score", 7.5)

    reasons: List[str] = []
    cautions: List[str] = []
    points = 0

    if "invest" in act or "finance" in act or "money" in act:
        act_title = "Investment & Financial Deals"
        if tara:
            if tara["tara_name"] in ("Sampat", "Sadhana", "Param Mitra"):
                points += 2
                reasons.append(f"✨ Favorable Tara Bala: {tara['tara_name']} ({tara['category']}) attracts growth and prosperity.")
            elif tara["tara_name"] in ("Vipat", "Naidhana (Vadh)"):
                points -= 3
                cautions.append(f"⚠️ Challenging Tara Bala ({tara['tara_name']}): High risk of unexpected capital lockup or losses.")

        if chandra:
            if chandra["house_distance"] in (11, 2, 9, 10):
                points += 2
                reasons.append(f"📈 Chandra Bala in {chandra['house_distance']}th House: Strong fiscal alignment.")
            elif chandra["house_distance"] in (8, 12):
                points -= 2
                cautions.append(f"⚠️ Ashtama/Vyaya Moon transit ({chandra['house_distance']}th house): High probability of impulse spending.")

        if curr_chog.get("name") in ("Labh", "Shubh", "Amrit"):
            points += 2
            reasons.append(f"🟢 Active {curr_chog.get('name')} Choghadiya is ideal for transactions and agreements.")
        elif curr_chog.get("name") in ("Kaal", "Rog", "Udveg"):
            points -= 2
            cautions.append(f"🔴 Active {curr_chog.get('name')} Choghadiya brings anxiety and delay in deals.")

        if curr_hora.get("planet") in ("Jupiter", "Mercury", "Venus"):
            points += 1
            reasons.append(f"⚡ {curr_hora.get('planet')} Hora strengthens commercial intellect and wealth.")

    elif "travel" in act or "journey" in act or "trip" in act:
        act_title = "Travel & Journeys"
        if tara:
            if tara["tara_name"] in ("Kshema", "Sadhana", "Mitra"):
                points += 2
                reasons.append(f"✨ Favorable Tara Bala ({tara['tara_name']}): Safe and pleasant travel energy.")
            elif tara["tara_name"] in ("Vipat", "Pratyak", "Naidhana (Vadh)"):
                points -= 2
                cautions.append(f"⚠️ Tara Bala warning ({tara['tara_name']}): Risk of travel delays, vehicle trouble, or fatigue.")

        if chandra:
            if chandra["house_distance"] in (3, 7, 9, 11):
                points += 2
                reasons.append(f"🚗 Chandra Bala in {chandra['house_distance']}th House: Favorable for successful journeys.")
            elif chandra["house_distance"] in (8, 12, 4):
                points -= 2
                cautions.append(f"⚠️ Moon in {chandra['house_distance']}th house: Prone to travel fatigue and unexpected route deviations.")

        if curr_chog.get("name") in ("Char", "Amrit", "Shubh"):
            points += 2
            reasons.append(f"🟢 {curr_chog.get('name')} Choghadiya is classically designated for movement and travel.")
        elif curr_chog.get("name") in ("Rog", "Kaal"):
            points -= 2
            cautions.append(f"🔴 Avoid starting departures during {curr_chog.get('name')} Choghadiya.")

        if disha:
            cautions.append(f"🧭 Disha Shool is towards {disha.get('direction', 'West')}. Vedic Remedy: {disha.get('remedy', 'Consume betel leaf before leaving')}.")

    elif "meet" in act or "negotiat" in act or "interview" in act or "client" in act:
        act_title = "Important Meetings & Negotiations"
        if tara:
            if tara["tara_name"] in ("Mitra", "Param Mitra", "Sadhana"):
                points += 2
                reasons.append(f"✨ Tara Bala ({tara['tara_name']}): High interpersonal charm and mutual agreement.")
            elif tara["tara_name"] in ("Pratyak", "Naidhana (Vadh)"):
                points -= 2
                cautions.append(f"⚠️ Pratyak/Naidhana Tara: High likelihood of argumentative friction or disagreement.")

        if chandra:
            if chandra["house_distance"] in (7, 10, 11, 1):
                points += 2
                reasons.append(f"🤝 Chandra Bala in {chandra['house_distance']}th house supports diplomacy and persuasive authority.")

        if curr_hora.get("planet") in ("Mercury", "Jupiter", "Sun"):
            points += 2
            reasons.append(f"⚡ {curr_hora.get('planet')} Hora enhances cognitive clarity, communication, and executive presence.")

    elif "spirit" in act or "puja" in act or "temple" in act or "mantra" in act:
        act_title = "Spiritual Puja & Sacred Rituals"
        points += 2
        reasons.append("🕉️ Sacred prayer and japa are universally purifying under all planetary conditions.")
        if tara and tara["tara_name"] in ("Janma", "Sadhana", "Param Mitra"):
            points += 2
            reasons.append(f"✨ Deep meditative focus reinforced by {tara['tara_name']} Tara.")
        if curr_chog.get("name") in ("Shubh", "Amrit"):
            points += 2
            reasons.append(f"🟢 Auspicious {curr_chog.get('name')} Choghadiya enhances the efficacy of rituals.")

    elif "purchas" in act or "buy" in act or "vehicle" in act or "asset" in act:
        act_title = "Asset & Vehicle Purchase"
        if tara:
            if tara["tara_name"] in ("Sampat", "Kshema", "Sadhana"):
                points += 2
                reasons.append(f"✨ {tara['tara_name']} Tara ensures lasting longevity and utility of the acquired asset.")
            elif tara["tara_name"] in ("Vipat", "Naidhana (Vadh)"):
                points -= 3
                cautions.append(f"⚠️ Inauspicious Tara: High risk of maintenance defects or recurring repair costs.")

        if curr_chog.get("name") in ("Shubh", "Labh", "Amrit"):
            points += 2
            reasons.append(f"🟢 {curr_chog.get('name')} Choghadiya provides positive vibrational foundation.")
        else:
            points -= 1
            cautions.append(f"🔴 Wait for Shubh/Amrit Choghadiya to sign final purchase deeds.")

    else:
        act_title = "General Venture"
        if today_score >= 7.0:
            points += 2
            reasons.append(f"🌟 Cosmic Day Score is strong ({today_score}/10).")
        else:
            points -= 1
            cautions.append("Cosmic energy requires patience and structured focus today.")

    next_best = current_panchang.get("next_auspicious_window", {
        "name": "Abhijit Muhurat",
        "start": "12:15 PM",
        "end": "01:05 PM",
        "time_until_start": "Midday"
    })

    if points >= 2 and not is_rahu:
        recommendation = "FAVORABLE"
        verdict_color = "green"
        summary = f"Favorable time for aligned action regarding {act_title}."
    elif points >= 0 and not is_rahu:
        recommendation = "MIXED SIGNALS"
        verdict_color = "gold"
        summary = f"Mixed astrological indicators. Consider extra diligence before proceeding with {act_title}."
    else:
        recommendation = "REFLECT"
        verdict_color = "red"
        summary = f"Vedic timing suggests pausing to reflect. Consider waiting for a more auspicious window."

    return {
        "activity": act_title,
        "recommendation": recommendation,
        "verdict_color": verdict_color,
        "alignment_strength": 0.94 if has_profile else 0.86,
        "summary": summary,
        "reasons": reasons,
        "cautions": cautions,
        "next_best_time": next_best,
        "tara_bala": tara,
        "chandra_bala": chandra
    }


def derive_natal_moon(
    birth_date: date,
    birth_time: Optional[time] = None,
    city_name: str = "Pune",
    lat: Optional[float] = None,
    lon: Optional[float] = None
) -> Dict[str, Any]:
    city_info = get_city(city_name)
    if city_info:
        default_lat, default_lon, _ = city_info
    else:
        default_lat, default_lon = 18.5204, 73.8567

    res_lat = lat if lat is not None else default_lat
    res_lon = lon if lon is not None else default_lon
    tz_obj, _ = resolve_timezone(lat=res_lat, lon=res_lon)

    b_time = birth_time if birth_time else time(12, 0)
    dt_local = datetime.combine(birth_date, b_time).replace(tzinfo=tz_obj)
    dt_utc = dt_local.astimezone(datetime.now().astimezone().tzinfo)

    ut_hour = dt_utc.hour + (dt_utc.minute / 60.0) + (dt_utc.second / 3600.0)
    jd_ut = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day, ut_hour)

    swe.set_sid_mode(swe.SIDM_LAHIRI)
    flags = swe.FLG_SWIEPH | swe.FLG_SPEED
    moon_res, _ = swe.calc_ut(jd_ut, swe.MOON, flags)
    ayanamsa = swe.get_ayanamsa_ut(jd_ut)

    moon_sid = (moon_res[0] - ayanamsa) % 360.0
    sign_idx = int(moon_sid / 30.0) % 12
    nak_deg = 360.0 / 27.0
    nak_idx = int(moon_sid / nak_deg) % 27
    pada = int((moon_sid % nak_deg) / (nak_deg / 4.0)) + 1
    rashi_sk = SIGNS[sign_idx]
    rashi_en = SIGNS_EN[sign_idx]
    nak_name = NAKSHATRAS[nak_idx]

    moon_deg_in_sign = moon_sid % 30.0
    moon_deg_in_nak = moon_sid % nak_deg
    is_estimated_time = birth_time is None

    is_near_sign_boundary = (moon_deg_in_sign < 1.0 or moon_deg_in_sign > 29.0)
    is_near_nak_boundary = (moon_deg_in_nak < 0.5 or moon_deg_in_nak > (nak_deg - 0.5))
    is_near_boundary = is_near_sign_boundary or is_near_nak_boundary or (
        is_estimated_time and (
            moon_deg_in_sign < 6.6 or moon_deg_in_sign > 23.4 or
            moon_deg_in_nak < 6.6 or moon_deg_in_nak > (nak_deg - 6.6)
        )
    )

    if is_estimated_time:
        boundary_warning = (
            "Birth time defaulted to 12:00 PM (Noon). The Moon traverses ~13° daily (~1 Nakshatra). "
            "If your actual birth time was early morning or late night, your Moon Rashi or Nakshatra may differ. "
            "Please provide exact birth time for pinpoint Tara Bala and Chandra Bala accuracy."
        )
    elif is_near_boundary:
        boundary_warning = (
            f"Natal Moon is at {round(moon_deg_in_sign, 2)}° near a sign or nakshatra boundary. "
            "Ensure birth time is accurate within ±15 minutes."
        )
    else:
        boundary_warning = "Natal Moon is comfortably positioned within sign and nakshatra boundaries."

    time_sensitivity_note = (
        "The Moon moves approximately 0.55° per hour (1 Nakshatra every ~24 hours). "
        "Tara Bala and Chandra Bala calculations rely on exact Moon coordinates."
    )

    return {
        "rashi": f"{rashi_sk} ({rashi_en})",
        "rashi_sanskrit": rashi_sk,
        "rashi_english": rashi_en,
        "nakshatra": nak_name,
        "nakshatra_pada": pada,
        "moon_longitude": round(moon_sid, 4),
        "moon_deg_in_sign": round(moon_deg_in_sign, 4),
        "is_estimated_time": is_estimated_time,
        "is_near_boundary": is_near_boundary,
        "boundary_warning": boundary_warning,
        "time_sensitivity_note": time_sensitivity_note,
        "birth_date": birth_date.strftime("%Y-%m-%d"),
        "birth_time": b_time.strftime("%H:%M")
    }


PLANET_COLOR_MAP = {
    "Sun":     {"color": "Orange",       "hex": "#FF8C00"},
    "Moon":    {"color": "White",        "hex": "#F0F0F0"},
    "Mars":    {"color": "Red",          "hex": "#DC2626"},
    "Mercury": {"color": "Green",        "hex": "#16A34A"},
    "Jupiter": {"color": "Yellow",       "hex": "#EAB308"},
    "Venus":   {"color": "Pink",         "hex": "#EC4899"},
    "Saturn":  {"color": "Blue",         "hex": "#3B82F6"},
    "Rahu":    {"color": "Grey",         "hex": "#9CA3AF"},
    "Ketu":    {"color": "Brown",        "hex": "#92400E"},
}

WEEKDAY_PLANET = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]

RASHI_RULER = {
    "Mesha": "Mars",    "Aries": "Mars",
    "Vrishabha": "Venus", "Taurus": "Venus",
    "Mithuna": "Mercury", "Gemini": "Mercury",
    "Karka": "Moon",    "Cancer": "Moon",
    "Simha": "Sun",     "Leo": "Sun",
    "Kanya": "Mercury", "Virgo": "Mercury",
    "Tula": "Venus",    "Libra": "Venus",
    "Vrischika": "Mars", "Scorpio": "Mars",
    "Dhanu": "Jupiter", "Sagittarius": "Jupiter",
    "Makara": "Saturn", "Capricorn": "Saturn",
    "Kumbha": "Saturn", "Aquarius": "Saturn",
    "Meena": "Jupiter", "Pisces": "Jupiter",
}

NUMBER_MEANINGS = {
    0: "Cycle completion & cosmic reset — good for introspection",
    1: "Leadership & new beginnings — take initiative",
    2: "Cooperation & diplomacy — good for partnerships",
    3: "Expression & creativity — ideal for artistic pursuits",
    4: "Stability & structure — organize and plan",
    5: "Communication & adaptability — good for networking",
    6: "Harmony & love — nurture relationships",
    7: "Spirituality & reflection — seek inner wisdom",
    8: "Power & material gains — strong for financial moves",
}

PLANET_FOCUS_AREA = {
    "Sun":     {"area": "Leadership & Authority",  "emoji": "👑", "advice": "Take charge of pending decisions and assert your vision."},
    "Moon":    {"area": "Emotional Wellbeing",      "emoji": "🌙", "advice": "Focus on self-care, family connections, and emotional clarity."},
    "Mars":    {"area": "Action & Execution",       "emoji": "⚔️", "advice": "Channel energy into competitive tasks, fitness, and bold moves."},
    "Mercury": {"area": "Study & Communication",    "emoji": "📚", "advice": "Prioritize learning, writing, presentations, and intellectual work."},
    "Jupiter": {"area": "Finance & Wisdom",         "emoji": "💎", "advice": "Focus on investments, mentoring, knowledge sharing, and expansion."},
    "Venus":   {"area": "Relationships & Creativity","emoji": "💕", "advice": "Strengthen bonds, engage in creative work, and appreciate beauty."},
    "Saturn":  {"area": "Discipline & Long-Term",   "emoji": "🏗️", "advice": "Work on structured goals, compliance, and long-term planning."},
}

TITHI_SPIRITUAL = {
    "Pratipada":  {"mantra": "Om Gam Ganapataye Namaha", "practice": "Ganesh worship for fresh beginnings", "fast": None},
    "Dwitiya":    {"mantra": "Om Chandraya Namaha", "practice": "Moon meditation for emotional balance", "fast": None},
    "Tritiya":    {"mantra": "Om Aim Saraswatyai Namaha", "practice": "Saraswati puja for knowledge", "fast": None},
    "Chaturthi":  {"mantra": "Om Gam Ganapataye Namaha", "practice": "Vinayaka prayers for obstacle removal", "fast": "Ganesh Chaturthi Vrat"},
    "Panchami":   {"mantra": "Om Namah Shivaya", "practice": "Shiva meditation for inner peace", "fast": None},
    "Shashthi":   {"mantra": "Om Subrahmanyaya Namaha", "practice": "Kartikeya worship for courage", "fast": None},
    "Saptami":    {"mantra": "Om Suryaya Namaha", "practice": "Surya Namaskar at sunrise for vitality", "fast": None},
    "Ashtami":    {"mantra": "Om Durgayai Namaha", "practice": "Durga meditation for strength", "fast": "Ashtami Vrat"},
    "Navami":     {"mantra": "Om Ramaya Namaha", "practice": "Ram bhajan for righteous conduct", "fast": "Ram Navami Vrat"},
    "Dashami":    {"mantra": "Om Dhanvantraye Namaha", "practice": "Health-focused meditation and gratitude", "fast": None},
    "Ekadashi":   {"mantra": "Om Namo Bhagavate Vasudevaya", "practice": "Vishnu puja & spiritual reading", "fast": "Ekadashi Vrat (recommended)"},
    "Dwadashi":   {"mantra": "Om Namo Bhagavate Vasudevaya", "practice": "Continue Vishnu devotion, break Ekadashi fast", "fast": None},
    "Trayodashi":  {"mantra": "Om Namah Shivaya", "practice": "Pradosh Vrat Shiva puja (if applicable)", "fast": "Pradosh Vrat"},
    "Chaturdashi": {"mantra": "Om Namah Shivaya", "practice": "Deep Shiva dhyana for transformation", "fast": "Shivratri Vrat (if applicable)"},
    "Purnima":    {"mantra": "Om Chandraya Namaha", "practice": "Satyanarayan puja, moonlight meditation", "fast": "Purnima Vrat"},
    "Amavasya":   {"mantra": "Om Pitrebhyo Namaha", "practice": "Pitru Tarpan, ancestral prayer & gratitude", "fast": "Amavasya Vrat"},
}

NAKSHATRA_MANTRA = {
    "Ashwini": "Om Ashwini Kumarabhyam Namaha",
    "Bharani": "Om Yamaya Namaha",
    "Krittika": "Om Agnaye Namaha",
    "Rohini": "Om Brahmane Namaha",
    "Mrigashira": "Om Chandraya Namaha",
    "Ardra": "Om Rudraya Namaha",
    "Punarvasu": "Om Aditya Namaha",
    "Pushya": "Om Brihaspathaye Namaha",
    "Ashlesha": "Om Sarpebhyo Namaha",
    "Magha": "Om Pitrebhyo Namaha",
    "Purva Phalguni": "Om Bhagaya Namaha",
    "Uttara Phalguni": "Om Aryamne Namaha",
    "Hasta": "Om Savitre Namaha",
    "Chitra": "Om Tvashtaye Namaha",
    "Swati": "Om Vayuve Namaha",
    "Vishakha": "Om Indragnibhyam Namaha",
    "Anuradha": "Om Mitraya Namaha",
    "Jyeshtha": "Om Indraya Namaha",
    "Mula": "Om Nirritaye Namaha",
    "Purva Ashadha": "Om Apebhyo Namaha",
    "Uttara Ashadha": "Om Vishvebhyo Devebhyo Namaha",
    "Shravana": "Om Vishnave Namaha",
    "Dhanishta": "Om Vasubhyo Namaha",
    "Shatabhisha": "Om Varunaya Namaha",
    "Purva Bhadrapada": "Om Ajaikapadaya Namaha",
    "Uttara Bhadrapada": "Om Ahirbudhnyaya Namaha",
    "Revati": "Om Pushne Namaha",
}


def get_daily_color(
    user_rashi: Optional[str],
    active_hora_planet: str,
    weekday_idx: int,
    tara_bala: Optional[Dict[str, Any]] = None,
    chandra_bala: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    reasons = []
    wd_planet = WEEKDAY_PLANET[weekday_idx % 7]
    dominant = active_hora_planet

    if tara_bala and tara_bala.get("is_auspicious") and tara_bala.get("score_mod", 0) >= 1.5:
        rashi_clean = (user_rashi or "").split("(")[0].strip().split()[0]
        rashi_ruler = RASHI_RULER.get(rashi_clean, active_hora_planet)
        dominant = rashi_ruler
        reasons.append(f"Strong {tara_bala['tara_name']} Tara amplifies {rashi_ruler} energy")
    elif chandra_bala and chandra_bala.get("house_distance") in (1, 10, 11):
        dominant = wd_planet
        reasons.append(f"Favorable Chandra Bala ({chandra_bala['status']}) aligns with {wd_planet}")
    else:
        reasons.append(f"{active_hora_planet} Hora dominates current period")

    color_data = PLANET_COLOR_MAP.get(dominant, PLANET_COLOR_MAP["Sun"])
    return {
        "color": color_data["color"],
        "hex": color_data["hex"],
        "planet": dominant,
        "reason": " + ".join(reasons)
    }


def get_lucky_number(
    nakshatra_name: str,
    tithi_name: str
) -> Dict[str, Any]:
    nak_idx = 0
    if nakshatra_name in NAKSHATRAS:
        nak_idx = NAKSHATRAS.index(nakshatra_name) + 1

    TITHI_NUM_MAP = {
        "Pratipada": 1, "Dwitiya": 2, "Tritiya": 3, "Chaturthi": 4,
        "Panchami": 5, "Shashthi": 6, "Saptami": 7, "Ashtami": 8,
        "Navami": 9, "Dashami": 10, "Ekadashi": 11, "Dwadashi": 12,
        "Trayodashi": 13, "Chaturdashi": 14, "Purnima": 15, "Amavasya": 30,
    }
    tithi_clean = (tithi_name or "Panchami").split()[0].strip()
    tithi_num = TITHI_NUM_MAP.get(tithi_clean, 5)

    lucky = (nak_idx + tithi_num) % 9
    return {
        "number": lucky,
        "meaning": NUMBER_MEANINGS.get(lucky, "Balanced cosmic energy"),
        "source": f"Nakshatra #{nak_idx} ({nakshatra_name}) + Tithi #{tithi_num} ({tithi_clean})"
    }


def get_personal_best_time(
    choghadiya_day: List[Dict[str, Any]],
    choghadiya_night: List[Dict[str, Any]],
    horas: List[Dict[str, Any]],
    tara_bala: Optional[Dict[str, Any]] = None,
    rahu_window: Optional[Dict[str, Any]] = None,
    yamaganda_window: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    all_chogs = (choghadiya_day or []) + (choghadiya_night or [])
    best = None
    best_score = -100

    for c in all_chogs:
        if not c.get("is_auspicious"):
            continue

        score = 0
        reasons = []

        name = c.get("name", "")
        if name == "Amrit":
            score += 3
            reasons.append("Amrit Choghadiya (highest auspiciousness)")
        elif name == "Shubh":
            score += 2
            reasons.append("Shubh Choghadiya (very favorable)")
        elif name == "Labh":
            score += 2
            reasons.append("Labh Choghadiya (gains & profit)")
        elif name == "Char":
            score += 1
            reasons.append("Char Choghadiya (good for movement)")

        if tara_bala and tara_bala.get("is_auspicious"):
            score += 1
            reasons.append(f"Strong Tara Bala ({tara_bala['tara_name']})")

        if score > best_score:
            best_score = score
            best = {
                "start": c.get("start", ""),
                "end": c.get("end", ""),
                "choghadiya": name,
                "reasons": reasons,
                "score": score
            }

    if not best:
        best = {
            "start": "12:00 PM",
            "end": "01:00 PM",
            "choghadiya": "Abhijit Muhurat",
            "reasons": ["Abhijit Muhurat is universally auspicious"],
            "score": 2
        }

    return best


def get_avoid_time(
    choghadiya_day: List[Dict[str, Any]],
    choghadiya_night: List[Dict[str, Any]],
    rahu_window: Optional[Dict[str, Any]] = None,
    yamaganda_window: Optional[Dict[str, Any]] = None,
    gulika_window: Optional[Dict[str, Any]] = None,
    chandra_bala: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    avoid_windows = []

    if rahu_window:
        avoid_windows.append({
            "name": "Rahu Kaal",
            "start": rahu_window.get("start", ""),
            "end": rahu_window.get("end", ""),
            "severity": "high",
            "reason": "Rahu Kaal — avoid starting any new venture or journey"
        })

    if yamaganda_window:
        avoid_windows.append({
            "name": "Yamaganda Kaal",
            "start": yamaganda_window.get("start", ""),
            "end": yamaganda_window.get("end", ""),
            "severity": "medium",
            "reason": "Yamaganda — avoid important signings and financial transfers"
        })

    if gulika_window:
        avoid_windows.append({
            "name": "Gulika Kaal",
            "start": gulika_window.get("start", ""),
            "end": gulika_window.get("end", ""),
            "severity": "low",
            "reason": "Gulika Kaal — exercise caution in health matters"
        })

    all_chogs = (choghadiya_day or []) + (choghadiya_night or [])
    for c in all_chogs:
        if not c.get("is_auspicious") and c.get("name") in ("Rog", "Kaal"):
            avoid_windows.append({
                "name": f"{c.get('name')} Choghadiya",
                "start": c.get("start", ""),
                "end": c.get("end", ""),
                "severity": "medium",
                "reason": f"{c.get('name')} Choghadiya — adverse for health & new starts"
            })

    if chandra_bala and chandra_bala.get("house_distance") in (8, 12):
        avoid_windows.append({
            "name": f"Ashtama/Vyaya Moon ({chandra_bala['house_distance']}th House)",
            "start": "All day",
            "end": "",
            "severity": "high",
            "reason": f"{chandra_bala['status']} — avoid high-risk decisions"
        })

    return {
        "windows": avoid_windows[:5],
        "total_count": len(avoid_windows)
    }


def get_focus_area(
    active_hora_planet: str,
    tara_bala: Optional[Dict[str, Any]] = None,
    chandra_bala: Optional[Dict[str, Any]] = None,
    weekday_idx: int = 0
) -> Dict[str, Any]:
    dominant = active_hora_planet

    if chandra_bala:
        h = chandra_bala.get("house_distance", 1)
        if h == 10:
            dominant = "Sun"
        elif h == 11:
            dominant = "Jupiter"
        elif h == 7:
            dominant = "Venus"
        elif h in (3, 6):
            dominant = "Mars"

    if tara_bala:
        t_name = tara_bala.get("tara_name", "")
        if t_name == "Sampat":
            dominant = "Jupiter"
        elif t_name == "Mitra" or t_name == "Param Mitra":
            dominant = "Venus"
        elif t_name == "Sadhana":
            dominant = "Mars"

    focus = PLANET_FOCUS_AREA.get(dominant, PLANET_FOCUS_AREA["Jupiter"])
    return {
        "area": focus["area"],
        "emoji": focus["emoji"],
        "advice": focus["advice"],
        "planet": dominant,
        "reason": f"Dominant {dominant} energy from Hora + Chandra Bala + Tara alignment"
    }


def get_spiritual_suggestion(
    tithi_name: str,
    nakshatra_name: str,
    chandra_bala: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    tithi_clean = (tithi_name or "Panchami").split()[0].strip()
    spiritual = TITHI_SPIRITUAL.get(tithi_clean, {
        "mantra": "Om Namah Shivaya",
        "practice": "General meditation and gratitude",
        "fast": None
    })

    nak_mantra = NAKSHATRA_MANTRA.get(nakshatra_name)
    mantras = [spiritual["mantra"]]
    if nak_mantra and nak_mantra != spiritual["mantra"]:
        mantras.append(nak_mantra)

    moon_note = None
    if chandra_bala:
        h = chandra_bala.get("house_distance", 1)
        if h in (9, 5, 12):
            moon_note = "Moon position highly favorable for spiritual practice today"
        elif h == 8:
            moon_note = "Ashtama Moon — meditation especially recommended for inner peace"

    return {
        "mantra": mantras[0],
        "additional_mantra": mantras[1] if len(mantras) > 1 else None,
        "practice": spiritual["practice"],
        "fasting": spiritual["fast"],
        "moon_note": moon_note,
        "source": f"Tithi: {tithi_clean} + Nakshatra: {nakshatra_name}"
    }


def compute_daily_insights(
    user_rashi: Optional[str],
    user_nakshatra: Optional[str],
    weekday_idx: int,
    active_hora_planet: str,
    nakshatra_name: str,
    tithi_name: str,
    choghadiya_day: List[Dict[str, Any]],
    choghadiya_night: List[Dict[str, Any]],
    horas: List[Dict[str, Any]],
    tara_bala: Optional[Dict[str, Any]] = None,
    chandra_bala: Optional[Dict[str, Any]] = None,
    rahu_window: Optional[Dict[str, Any]] = None,
    yamaganda_window: Optional[Dict[str, Any]] = None,
    gulika_window: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    color = get_daily_color(
        user_rashi=user_rashi,
        active_hora_planet=active_hora_planet,
        weekday_idx=weekday_idx,
        tara_bala=tara_bala,
        chandra_bala=chandra_bala
    )

    number = get_lucky_number(
        nakshatra_name=nakshatra_name,
        tithi_name=tithi_name
    )

    best_time = get_personal_best_time(
        choghadiya_day=choghadiya_day,
        choghadiya_night=choghadiya_night,
        horas=horas,
        tara_bala=tara_bala,
        rahu_window=rahu_window,
        yamaganda_window=yamaganda_window
    )

    avoid_time = get_avoid_time(
        choghadiya_day=choghadiya_day,
        choghadiya_night=choghadiya_night,
        rahu_window=rahu_window,
        yamaganda_window=yamaganda_window,
        gulika_window=gulika_window,
        chandra_bala=chandra_bala
    )

    focus = get_focus_area(
        active_hora_planet=active_hora_planet,
        tara_bala=tara_bala,
        chandra_bala=chandra_bala,
        weekday_idx=weekday_idx
    )

    spiritual = get_spiritual_suggestion(
        tithi_name=tithi_name,
        nakshatra_name=nakshatra_name,
        chandra_bala=chandra_bala
    )

    return {
        "color": color,
        "number": number,
        "best_time": best_time,
        "avoid_time": avoid_time,
        "focus_area": focus,
        "spiritual": spiritual
    }
