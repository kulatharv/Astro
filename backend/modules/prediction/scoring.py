"""
Scoring and Chart Context Utilities for Life Domain Analysis.
"""

from datetime import datetime, timezone
import swisseph as swe

from shared.veda import (
    evaluate_mangal_dosha, evaluate_pitru_dosha,
    PLANET_FRIENDS, MOOLATRIKONA, PLANET_ENEMIES,
    get_naisargika_dignity, get_positional_strength,
    is_combust, check_combustion, is_neech_bhanga
)

from shared.ephemeris.wrapper import get_active_ephe_path
swe.set_ephe_path(get_active_ephe_path())
swe.set_sid_mode(swe.SIDM_LAHIRI)

RASHI = ["Mesha","Vrishabha","Mithuna","Karka","Simha","Kanya",
         "Tula","Vrischika","Dhanu","Makara","Kumbha","Meena"]

RASHI_EN = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo",
            "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]

NAKSHATRAS = [
    "Ashwini","Bharani","Krittika","Rohini","Mrigashira","Ardra",
    "Punarvasu","Pushya","Ashlesha","Magha","Purva Phalguni",
    "Uttara Phalguni","Hasta","Chitra","Swati","Vishakha",
    "Anuradha","Jyeshtha","Mula","Purva Ashadha","Uttara Ashadha",
    "Shravana","Dhanishta","Shatabhisha","Purva Bhadrapada",
    "Uttara Bhadrapada","Revati",
]

SIGN_LORDS = {
    "Mesha":"Mars","Vrishabha":"Venus","Mithuna":"Mercury","Karka":"Moon",
    "Simha":"Sun","Kanya":"Mercury","Tula":"Venus","Vrischika":"Mars",
    "Dhanu":"Jupiter","Makara":"Saturn","Kumbha":"Saturn","Meena":"Jupiter"
}

DASHA_ORDER = ["Ketu","Venus","Sun","Moon","Mars","Rahu","Jupiter","Saturn","Mercury"]
DASHA_YEARS = dict(Ketu=7,Venus=20,Sun=6,Moon=10,Mars=7,Rahu=18,Jupiter=16,Saturn=19,Mercury=17)
NAK_DIV     = 360 / 27

EXALTATION   = dict(Sun="Mesha",Moon="Vrishabha",Mars="Makara",Mercury="Kanya",
                    Jupiter="Karka",Venus="Meena",Saturn="Tula",Rahu="Vrishabha",Ketu="Vrischika")
DEBILITATION = dict(Sun="Tula",Moon="Vrischika",Mars="Karka",Mercury="Meena",
                    Jupiter="Makara",Venus="Kanya",Saturn="Mesha",Rahu="Vrischika",Ketu="Vrischabha")
OWN_SIGNS    = dict(Sun=["Simha"],Moon=["Karka"],Mars=["Mesha","Vrischika"],
                    Mercury=["Mithuna","Kanya"],Jupiter=["Dhanu","Meena"],
                    Venus=["Vrishabha","Tula"],Saturn=["Makara","Kumbha"])

PLANET_IDS = dict(Sun=swe.SUN,Moon=swe.MOON,Mercury=swe.MERCURY,Venus=swe.VENUS,
                  Mars=swe.MARS,Jupiter=swe.JUPITER,Saturn=swe.SATURN,Rahu=swe.TRUE_NODE)


def parse_degree(value):
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            parts = value.replace("°", " ").replace("'", "").split()
            deg = float(parts[0])
            minute = float(parts[1]) if len(parts) > 1 else 0
            return deg + minute / 60
        except Exception:
            return 0.0
    return 0.0


def _planet_strength(name: str, sign: str) -> tuple:
    """Returns (label, score) — score from -2 to +3."""
    if EXALTATION.get(name) == sign:   return "Exalted",      3
    if DEBILITATION.get(name) == sign: return "Debilitated",  -2
    if sign in OWN_SIGNS.get(name,[]):  return "Own Sign",     2
    return "Neutral", 0


def _house_from(planet_sign_idx: int, lagna_sign_idx: int) -> int:
    return ((planet_sign_idx - lagna_sign_idx) % 12) + 1


def _ordinal(n: int) -> str:
    s = {1:"st",2:"nd",3:"rd"}.get(n if n < 20 else n % 10,"th")
    return f"{n}{s}"


def _sign_lord(sign: str) -> str:
    return SIGN_LORDS.get(sign, "Unknown")


def _house_lord(lagna_idx: int, house: int) -> str:
    sign = RASHI[(lagna_idx + house - 1) % 12]
    return _sign_lord(sign)


def _house_sign(lagna_idx: int, house: int) -> str:
    return RASHI[(lagna_idx + house - 1) % 12]


def _build_ctx(chart: dict) -> dict:
    """
    Build structured calculation context from Kundali output.
    """
    planets   = chart.get("planets", [])
    lagna     = chart.get("lagna", "Mesha")
    lagna_idx = RASHI.index(lagna) if lagna in RASHI else 0

    planet_map = {}
    if isinstance(planets, dict):
        for name, p in planets.items():
            if isinstance(p, dict):
                sign = p.get("sign", "Mesha")
                house = int(p.get("house", _house_from(RASHI.index(sign) if sign in RASHI else 0, lagna_idx)))
                strength_label, strength_score = _planet_strength(name, sign)
                deg_val = parse_degree(p.get("degree", 0))
                s_idx = RASHI.index(sign) if sign in RASHI else 0
                calc_lon = (s_idx * 30.0 + (deg_val % 30.0)) % 360.0
                lon_val = p.get("_raw_lon") if p.get("_raw_lon") is not None else (p.get("longitude") if p.get("longitude") is not None else calc_lon)
                planet_map[name] = {
                    "sign": sign,
                    "house": house,
                    "degree": deg_val,
                    "degree_decimal": p.get("degree_decimal", deg_val),
                    "retrograde": bool(p.get("retrograde", False)),
                    "nakshatra": p.get("nakshatra", ""),
                    "strength": strength_label,
                    "str_score": strength_score,
                    "_raw_lon": lon_val,
                    "longitude": lon_val,
                    "is_combust": p.get("is_combust", p.get("combust")),
                    "combust": p.get("combust", p.get("is_combust")),
                }
    elif isinstance(planets, list):
        for p in planets:
            if isinstance(p, dict):
                name = p.get("name", "Sun")
                sign = p.get("sign", "Mesha")
                house = int(p.get("house", _house_from(RASHI.index(sign) if sign in RASHI else 0, lagna_idx)))
                strength_label, strength_score = _planet_strength(name, sign)
                deg_val = parse_degree(p.get("degree", 0))
                s_idx = RASHI.index(sign) if sign in RASHI else 0
                calc_lon = (s_idx * 30.0 + (deg_val % 30.0)) % 360.0
                lon_val = p.get("_raw_lon") if p.get("_raw_lon") is not None else (p.get("longitude") if p.get("longitude") is not None else calc_lon)
                planet_map[name] = {
                    "sign": sign,
                    "house": house,
                    "degree": deg_val,
                    "degree_decimal": p.get("degree_decimal", deg_val),
                    "retrograde": bool(p.get("retrograde", False)),
                    "nakshatra": p.get("nakshatra", ""),
                    "strength": strength_label,
                    "str_score": strength_score,
                    "_raw_lon": lon_val,
                    "longitude": lon_val,
                    "is_combust": p.get("is_combust", p.get("combust")),
                    "combust": p.get("combust", p.get("is_combust")),
                }

    if "Rahu" in planet_map and "Ketu" not in planet_map:
        rahu_h = planet_map["Rahu"]["house"]
        ketu_h = ((rahu_h - 1 + 6) % 12) + 1
        rahu_sign_idx = RASHI.index(planet_map["Rahu"]["sign"]) if planet_map["Rahu"]["sign"] in RASHI else 0
        ketu_sign = RASHI[(rahu_sign_idx + 6) % 12]
        rahu_raw = planet_map["Rahu"].get("_raw_lon")
        ketu_raw = ((rahu_raw + 180.0) % 360.0) if rahu_raw is not None else None
        planet_map["Ketu"] = {
            "sign": ketu_sign, "house": ketu_h, "degree": planet_map["Rahu"]["degree"],
            "degree_decimal": planet_map["Rahu"].get("degree_decimal", planet_map["Rahu"]["degree"]),
            "retrograde": True, "nakshatra": "", "strength": "Neutral", "str_score": 0,
            "_raw_lon": ketu_raw, "longitude": ketu_raw,
            "is_combust": False, "combust": False,
        }

    # Evaluate and ensure verified combustion status for all planets
    sun_data = planet_map.get("Sun")
    for name, pentry in planet_map.items():
        if pentry.get("is_combust") is None:
            c_res = check_combustion(name, pentry, sun_data)
            pentry["is_combust"] = c_res.is_combust
            pentry["combust"] = c_res.is_combust
            pentry["combustion_status"] = c_res.status.value
            pentry["combustion_separation"] = c_res.separation

    house_lords = {h: _house_lord(lagna_idx, h) for h in range(1,13)}
    house_signs = {h: _house_sign(lagna_idx, h) for h in range(1,13)}

    mahadasha = chart.get("mahadasha","")
    antardasha= chart.get("antardasha","")

    now  = datetime.now(timezone.utc)
    jd_t = swe.julday(now.year,now.month,now.day,now.hour+now.minute/60)
    FLAG = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
    transit_map = {}
    for pname, pid in PLANET_IDS.items():
        lon = swe.calc_ut(jd_t, pid, FLAG)[0][0] % 360
        if pname == "Rahu":
            ketu_lon = (lon+180)%360
            transit_map["Ketu"] = {"sign": RASHI[int(ketu_lon/30)],
                                   "house": _house_from(int(ketu_lon/30), lagna_idx)}
        transit_map[pname] = {"sign": RASHI[int(lon/30)],
                              "house": _house_from(int(lon/30), lagna_idx)}

    # Net scores
    net_scores = {}
    for pname, pdata in planet_map.items():
        net_scores[pname] = pdata["str_score"]

    lagna_deg = chart.get("lagna_degree_decimal")
    if lagna_deg is None:
        lagna_deg = parse_degree(chart.get("lagna_degree", 0.0))

    return {
        "lagna":                lagna,
        "lagna_idx":            lagna_idx,
        "lagna_degree":         lagna_deg,
        "lagna_degree_decimal": lagna_deg,
        "d9_lagna":             chart.get("d9_lagna", ""),
        "d9_houses":            chart.get("d9_houses", {}),
        "planet_map":           planet_map,
        "house_lords":          house_lords,
        "house_signs":          house_signs,
        "mahadasha":            mahadasha,
        "antardasha":           antardasha,
        "transit_map":          transit_map,
        "net_scores":           net_scores,
        "yogas":                chart.get("yogas", []),
        "doshas":               chart.get("doshas", []),
        "scores":               chart.get("scores", {}),
        "fn":                   {},
        "birth_date":           chart.get("birth_date") or chart.get("date") or chart.get("basic_details", {}).get("date", ""),
        "birth_datetime":       chart.get("birth_datetime"),
        "raw_chart":            chart,
    }


def _score_planets_in_houses(ctx: dict, key_houses: list) -> float:
    """Score based on which planets occupy key_houses and their strengths."""
    planet_map = ctx["planet_map"]
    score = 0.0
    NATURE = dict(Jupiter=3,Venus=2,Moon=1,Mercury=1,Sun=0,Mars=-1,Saturn=-2,Rahu=-1,Ketu=-1)
    for pname, pdata in planet_map.items():
        if pdata["house"] in key_houses:
            n = NATURE.get(pname, 0)
            s = pdata["str_score"]
            h_amp = 1.4 if pdata["house"] in (1,4,7,10) else 1.1 if pdata["house"] in (5,9) else 0.9
            score += (n + s) * h_amp
    return score


def _score_house_lord(ctx: dict, house: int) -> float:
    """Score based on where the house lord is placed and its strength."""
    lord = ctx["house_lords"][house]
    pdata = ctx["planet_map"].get(lord)
    if not pdata: return 0
    h = pdata["house"]
    s = pdata["str_score"]
    h_score = 1 if h in (1,2,4,5,7,9,10,11) else -1
    return s + h_score


def _dasha_activates(ctx: dict, houses: list) -> bool:
    """True if current Mahadasha or Antardasha lord rules or occupies any key house."""
    for dasha_lord in [ctx["mahadasha"], ctx["antardasha"]]:
        if not dasha_lord: continue
        pdata = ctx["planet_map"].get(dasha_lord,{})
        if pdata.get("house") in houses: return True
        for h in houses:
            if ctx["house_lords"].get(h) == dasha_lord: return True
    return False


def _transit_influence(ctx: dict, houses: list, benefic_planets: list) -> float:
    """Score how beneficial current transits are for key houses."""
    score = 0.0
    for pname, tdata in ctx["transit_map"].items():
        if tdata["house"] in houses:
            score += 1.5 if pname in benefic_planets else -1 if pname in ("Saturn","Rahu","Ketu","Mars") else 0
    return score


def _yoga_present(ctx: dict, yoga_names: list) -> list:
    active = [y.get("name","") if isinstance(y,dict) else str(y) for y in ctx["yogas"] if (isinstance(y,dict) and y.get("present")) or isinstance(y,str)]
    return [y for y in active if any(n.lower() in y.lower() for n in yoga_names)]


def _dosha_present(ctx: dict, dosha_names: list) -> list:
    active = [d.get("name","") if isinstance(d,dict) else str(d) for d in ctx["doshas"] if (isinstance(d,dict) and d.get("present")) or isinstance(d,str)]
    return [d for d in active if any(n.lower() in d.lower() for n in dosha_names)]


def _clamp(v: float, lo=0.0, hi=100.0) -> float:
    return max(lo, min(hi, v))


def _pct(base: float, score: float, dasha_bonus: float = 0) -> int:
    return int(_clamp(50 + score * 6 + dasha_bonus, 15, 95))



def _domain_score(ctx: dict, key_houses: list, karaka: str = None, secondary_houses: list = None) -> dict:
    sec = secondary_houses or []
    base_score = _score_planets_in_houses(ctx, key_houses)
    lord_scores = sum(_score_house_lord(ctx, h) for h in key_houses)
    
    karaka_score = 0.0
    if karaka:
        kp = ctx["planet_map"].get(karaka, {})
        karaka_score = kp.get("str_score", 0) + (1.5 if kp.get("house") in key_houses + sec else 0)

    total_score = base_score + lord_scores + karaka_score
    dasha_act = _dasha_activates(ctx, key_houses)
    score_pct = _pct(50, total_score, 10 if dasha_act else 0)

    return {
        "score": score_pct,
        "raw_score": round(total_score, 2),
        "dasha_active": dasha_act,
    }
