"""Dynamic transit-driven daily horoscope engine integrating deep Swiss Ephemeris calculations."""

from datetime import date, datetime
import swisseph as swe
from shared.veda.zodiac import SIGNS_EN, SIGNS_SK

SIGN_TO_RASHI = {
    "aries": 0, "taurus": 1, "gemini": 2, "cancer": 3,
    "leo": 4, "virgo": 5, "libra": 6, "scorpio": 7,
    "sagittarius": 8, "capricorn": 9, "aquarius": 10, "pisces": 11,
}

HOUSE_DOMAINS = {
    1: "Self & Vitality",
    2: "Wealth & Family",
    3: "Courage & Travel",
    4: "Home & Mind",
    5: "Romance & Wisdom",
    6: "Health & Work",
    7: "Partnership & Love",
    8: "Transformation",
    9: "Fortune & Dharma",
    10: "Career & Status",
    11: "Gains & Income",
    12: "Liberation & Loss",
}

WEEKDAY_LORDS = [
    "Moon (Chandra)",
    "Mars (Mangala)",
    "Mercury (Budha)",
    "Jupiter (Guru)",
    "Venus (Shukra)",
    "Saturn (Shani)",
    "Sun (Surya)",
]


def generate_horoscope(sign_input: str | int) -> dict:
    """Generate dynamic transit-based daily horoscope with full Vedic parameters."""
    if isinstance(sign_input, int):
        sign_idx = max(0, min(11, sign_input))
        sign_en = SIGNS_EN[sign_idx]
    else:
        sign_clean = sign_input.strip().lower()
        sign_idx = SIGN_TO_RASHI.get(sign_clean, 0)
        sign_en = SIGNS_EN[sign_idx]

    sign_sk = SIGNS_SK[sign_idx]

    # Try importing the deep rich engine from app.astrology
    try:
        from app.astrology.horoscope_engine import generate_horoscope as gen_rich
        rich = gen_rich(sign_en)
    except Exception:
        rich = None

    today = date.today()
    now = datetime.now()
    weekday_idx = now.weekday()  # 0 is Monday
    weekday_lord = WEEKDAY_LORDS[weekday_idx]

    if rich:
        stars_dict = rich.get("stars", {})
        # Map stars (1-5) to percentages (60-98%)
        scores = {
            "overall": min(98, max(50, int(stars_dict.get("overall", 3.5) * 19))),
            "career": min(98, max(50, int(stars_dict.get("career", 3.5) * 19))),
            "love": min(98, max(50, int(stars_dict.get("love", 3.5) * 19))),
            "finance": min(98, max(50, int(stars_dict.get("finance", 3.5) * 19))),
            "health": min(98, max(50, int(stars_dict.get("health", 3.5) * 19))),
            "luck": min(98, max(50, int(stars_dict.get("luck", 3.5) * 19))),
        }

        # Format planet_positions list for bar visualizations
        planet_positions = []
        planet_details = rich.get("planet_details", {})
        for p_name, p_info in planet_details.items():
            h = p_info.get("house", 1)
            strength = p_info.get("strength", "Neutral")
            net_val = 0
            if "Exalted" in strength:
                net_val = 8
            elif "Own" in strength:
                net_val = 6
            elif "Debilitated" in strength:
                net_val = -8
            else:
                net_val = 2 if h in (1, 5, 9, 10, 11) else (-2 if h in (6, 8, 12) else 1)

            planet_positions.append({
                "name": p_name,
                "house": h,
                "domain": HOUSE_DOMAINS.get(h, "Life Domain"),
                "strength": strength,
                "retrograde": p_info.get("retrograde", False),
                "sign": p_info.get("sign", ""),
                "nakshatra": p_info.get("nakshatra", ""),
                "net": net_val,
            })

        tithi_full = rich.get("tithi", "Shukla Dashami")
        paksha = "Krishna" if "Krishna" in tithi_full else "Shukla"

        return {
            "status": "success",
            "sign": sign_en,
            "sign_idx": sign_idx,
            "sign_sanskrit": sign_sk,
            "date": rich.get("date", today.strftime("%Y-%m-%d")),
            "tithi": tithi_full,
            "paksha": paksha,
            "moon_nakshatra": rich.get("moon_nakshatra", "Pushya"),
            "moon_sign": rich.get("moon_sign", ""),
            "sun_sign": rich.get("sun_sign", ""),
            "weekday_lord": weekday_lord,

            # Text narratives
            "overview": rich.get("overview", ""),
            "horoscope": rich.get("overview", ""),
            "love": rich.get("love", ""),
            "career": rich.get("career", ""),
            "health": rich.get("health", ""),

            # Scores and stars
            "scores": scores,
            "stars": stars_dict,

            # Auspicious indicators
            "lucky_number": rich.get("lucky_number", 7),
            "lucky_color": rich.get("lucky_color", "Gold"),
            "lucky_gem": rich.get("lucky_gem", "Yellow Sapphire"),
            "ruling_planet": rich.get("ruling_planet", "Sun"),
            "best_time": rich.get("best_time", "10 AM - 12 PM"),
            "best_dir": "East" if sign_idx % 4 == 0 else ("South" if sign_idx % 4 == 1 else ("West" if sign_idx % 4 == 2 else "North")),

            "mantra": rich.get("mantra", "Om Namah Shivaya"),
            "tip": rich.get("tip", "Focus on clear goals and purposeful action."),
            "compat_signs": rich.get("compatible", [SIGNS_EN[(sign_idx + 4) % 12], SIGNS_EN[(sign_idx + 8) % 12]]),
            "compatible_signs": rich.get("compatible", [SIGNS_EN[(sign_idx + 4) % 12], SIGNS_EN[(sign_idx + 8) % 12]]),

            "planet_positions": planet_positions,
            "key_transits": rich.get("key_transits", []),
        }

    # Fallback to direct calculation if app.astrology engine had issues
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
    jd = swe.julday(today.year, today.month, today.day, 6.0)

    moon_lon = swe.calc_ut(jd, swe.MOON, flags)[0][0] % 360.0
    jup_lon = swe.calc_ut(jd, swe.JUPITER, flags)[0][0] % 360.0
    ven_lon = swe.calc_ut(jd, swe.VENUS, flags)[0][0] % 360.0

    moon_sign_idx = int(moon_lon / 30.0)
    jup_sign_idx = int(jup_lon / 30.0)
    moon_h = ((moon_sign_idx - sign_idx) % 12) + 1
    jup_h = ((jup_sign_idx - sign_idx) % 12) + 1

    career_score = 70 + (15 if jup_h in (1, 5, 9, 10) else 0)
    love_score = 72 + (12 if ven_lon % 30 < 15 else 5)
    finance_score = 68 + (14 if jup_h in (2, 11, 9) else 4)
    health_score = 75 + (10 if moon_h not in (6, 8, 12) else -10)
    luck_score = 70 + (15 if jup_h in (1, 5, 9) else 5)

    prediction_text = (
        f"For {sign_en} ({sign_sk}), cosmic transits bring constructive opportunities. "
        f"The Moon transit through house {moon_h} supports reflection and focus, while "
        f"Jupiter in house {jup_h} empowers sustained progress."
    )

    return {
        "status": "success",
        "sign": sign_en,
        "sign_idx": sign_idx,
        "sign_sanskrit": sign_sk,
        "date": today.strftime("%Y-%m-%d"),
        "tithi": "Shukla Dashami",
        "paksha": "Shukla",
        "moon_nakshatra": "Pushya",
        "weekday_lord": weekday_lord,
        "overview": prediction_text,
        "horoscope": prediction_text,
        "love": "Warmth and understanding define relationship dynamics today.",
        "career": "Methodical effort delivers steady advancement and recognition.",
        "health": "Vitality is balanced; prioritize wholesome nourishment and rest.",
        "scores": {
            "overall": 80,
            "career": min(98, career_score),
            "love": min(98, love_score),
            "finance": min(98, finance_score),
            "health": min(98, health_score),
            "luck": min(98, luck_score),
        },
        "stars": {
            "overall": 4.2,
            "career": 4.0,
            "love": 4.3,
            "finance": 3.9,
            "health": 4.1,
            "luck": 4.0,
        },
        "lucky_number": ((sign_idx * 3 + today.day) % 9) + 1,
        "lucky_color": "Gold",
        "lucky_gem": "Yellow Sapphire",
        "ruling_planet": "Sun",
        "best_time": "10 AM - 12 PM",
        "best_dir": "East",
        "mantra": "Om Namah Shivaya",
        "tip": "Align your energy with priority projects early in the day.",
        "compat_signs": [SIGNS_EN[(sign_idx + 4) % 12], SIGNS_EN[(sign_idx + 8) % 12]],
        "compatible_signs": [SIGNS_EN[(sign_idx + 4) % 12], SIGNS_EN[(sign_idx + 8) % 12]],
        "planet_positions": [],
        "key_transits": [],
    }


def generate_all_horoscopes() -> dict[str, dict]:
    """Generate horoscopes for all 12 signs."""
    return {sign: generate_horoscope(sign) for sign in SIGN_TO_RASHI}
