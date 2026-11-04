"""
Jaimini Astrology Pure Calculation Primitives (shared.veda.jaimini_rules).

Stateless, pure mathematical and astrological calculations for:
1. Chara Karakas (7-karaka and 8-karaka schemes with bounded Rahu traversal and deterministic tie-breaking)
2. Arudha Padas (A1–A12, Arudha Lagna, Upapada Lagna with BPHS 1st/7th Pada-locus exceptions)
3. Rashi Drishti (sign-based structural aspects, 36 directed pairs with adjacent exclusions)

Governing Standard: Master Specification v3.0 §10, §9.1, §9.2, §15, Appendix C.
Zero side-effects, zero DB, zero Redis.
"""

from __future__ import annotations

import math
from enum import Enum
from typing import Any, Optional


# ==============================================================================
# 1. Enums and Configurations
# ==============================================================================

class KarakaSchemeEnum(str, Enum):
    """Chara Karaka scheme selection (DEC-JAI-01)."""
    SEVEN_KARAKA = "SEVEN_KARAKA"   # Sun through Saturn (7 planets; Rahu excluded)
    EIGHT_KARAKA = "EIGHT_KARAKA"   # 7 classical planets + Rahu (8 planets)


class TieBreakerEnum(str, Enum):
    """Deterministic degree tie-breaker fallback (DEC-JAI-03)."""
    NATURAL_SPEED = "NATURAL_SPEED"  # Sun > Moon > Mars > Mercury > Jupiter > Venus > Saturn > Rahu
    STHIRA_KARAKA = "STHIRA_KARAKA"  # Shared role with Sthira Karaka fallback


class ArudhaExceptionEnum(str, Enum):
    """Arudha Pada 1st and 7th exception handling (DEC-JAI-09)."""
    STANDARD_EXCEPTION = "STANDARD_EXCEPTION"    # BPHS Pada-locus: if raw Pada in 1st -> 10th; if in 7th -> 4th
    NO_EXCEPTION = "NO_EXCEPTION"                # Pure symmetrical projection without exceptions
    RATH_KUMBHA_VRISHIK = "RATH_KUMBHA_VRISHIK"  # Sanjay Rath lineage with Scorpio/Aquarius co-lord exceptions


class DualLordshipEnum(str, Enum):
    """Scorpio and Aquarius dual lordship convention (DEC-JAI-04)."""
    PARASHARI_SINGLE = "PARASHARI_SINGLE"  # Mars for Scorpio, Saturn for Aquarius
    JAIMINI_STRONGER = "JAIMINI_STRONGER"  # Stronger of (Mars, Ketu) or (Saturn, Rahu)


class RashiMobilityEnum(str, Enum):
    """Zodiac sign mobility classification."""
    CHARA = "CHARA"             # Movable / Cardinal: 1, 4, 7, 10
    STHIRA = "STHIRA"           # Fixed: 2, 5, 8, 11
    DVISVABHAVA = "DVISVABHAVA" # Dual / Mutable: 3, 6, 9, 12


# Aliases for backward and cross-module compatibility
KarakaScheme = KarakaSchemeEnum
ArudhaExceptionMode = ArudhaExceptionEnum


class RashiDrishtiMode(str, Enum):
    """Rashi Drishti mode."""
    STANDARD = "STANDARD"


class SevenKarakaRole(str, Enum):
    """7-Karaka Roles."""
    AK = "AK"
    AmK = "AmK"
    BK = "BK"
    MK = "MK"
    PK = "PK"
    GK = "GK"
    DK = "DK"


class EightKarakaRole(str, Enum):
    """8-Karaka Roles."""
    AK = "AK"
    AmK = "AmK"
    BK = "BK"
    MK = "MK"
    PiK = "PiK"
    PK = "PK"
    GK = "GK"
    DK = "DK"


# ==============================================================================
# 2. Astrological Constants
# ==============================================================================

CLASSICAL_7_BODIES = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
EIGHT_KARAKA_BODIES = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu"]

# Roles for 7-karaka scheme (Rahu excluded)
ROLES_7_KARAKA = ["AK", "AmK", "BK", "MK", "PK", "GK", "DK"]

# Roles for 8-karaka scheme (Pitrikaraka inserted at rank 4, Putrakaraka at rank 5)
ROLES_8_KARAKA = ["AK", "AmK", "BK", "MK", "PiK", "PK", "GK", "DK"]

# Natural planetary average daily speed ranking for deterministic software tie-breaking
# Fastest to slowest: Moon > Mercury > Venus > Sun > Mars > Jupiter > Saturn > Rahu
# Or standard classical solar order: Sun=1, Moon=2, Mars=3, Mercury=4, Jupiter=5, Venus=6, Saturn=7, Rahu=8
NATURAL_SPEED_RANK: dict[str, int] = {
    "Sun": 1,
    "Moon": 2,
    "Mars": 3,
    "Mercury": 4,
    "Jupiter": 5,
    "Venus": 6,
    "Saturn": 7,
    "Rahu": 8,
}

# Sign Mobility Sets (1-indexed sign numbers)
CHARA_SIGNS: set[int] = {1, 4, 7, 10}       # Aries, Cancer, Libra, Capricorn
STHIRA_SIGNS: set[int] = {2, 5, 8, 11}      # Taurus, Leo, Scorpio, Aquarius
DVISVABHAVA_SIGNS: set[int] = {3, 6, 9, 12} # Gemini, Virgo, Sagittarius, Pisces

# 1-indexed Sign Names (Sanskrit and English)
SIGN_NAMES_SK: dict[int, str] = {
    1: "Mesha", 2: "Vrishabha", 3: "Mithuna", 4: "Karka",
    5: "Simha", 6: "Kanya", 7: "Tula", 8: "Vrischika",
    9: "Dhanu", 10: "Makara", 11: "Kumbha", 12: "Meena",
}

SIGN_NAMES_EN: dict[int, str] = {
    1: "Aries", 2: "Taurus", 3: "Gemini", 4: "Cancer",
    5: "Leo", 6: "Virgo", 7: "Libra", 8: "Scorpio",
    9: "Sagittarius", 10: "Capricorn", 11: "Aquarius", 12: "Pisces",
}

# Standard Parāśari Sign Lords (1-indexed sign -> planet)
PARASHARI_SIGN_LORDS: dict[int, str] = {
    1: "Mars", 2: "Venus", 3: "Mercury", 4: "Moon",
    5: "Sun", 6: "Mercury", 7: "Venus", 8: "Mars",
    9: "Jupiter", 10: "Saturn", 11: "Saturn", 12: "Jupiter",
}

# Normalization mapping for sign names (English & Sanskrit -> 1-indexed int)
SIGN_NAME_TO_INDEX: dict[str, int] = {
    "mesha": 1, "aries": 1,
    "vrishabha": 2, "taurus": 2, "vrishabh": 2,
    "mithuna": 3, "gemini": 3, "mithun": 3,
    "karka": 4, "cancer": 4, "kark": 4,
    "simha": 5, "leo": 5, "singh": 5,
    "kanya": 6, "virgo": 6,
    "tula": 7, "libra": 7,
    "vrischika": 8, "scorpio": 8, "vrishchik": 8, "vrischick": 8,
    "dhanu": 9, "sagittarius": 9, "dhanus": 9,
    "makara": 10, "capricorn": 10, "makar": 10,
    "kumbha": 11, "aquarius": 11, "kumbh": 11,
    "meena": 12, "pisces": 12, "meen": 12,
}


# ==============================================================================
# 3. Input Validation & Mathematical Normalization
# ==============================================================================

def validate_finite_degree(degree: Any) -> float:
    """Validate that degree is a finite, numeric float."""
    if degree is None:
        raise ValueError("Planetary degree cannot be None")
    try:
        val = float(degree)
    except (ValueError, TypeError):
        raise ValueError(f"Invalid degree value: {degree} (must be float)")
    if not math.isfinite(val):
        raise ValueError(f"Planetary degree must be a finite float, got: {val}")
    return val


def normalize_sign_degree(raw_degree: float) -> tuple[int, float]:
    """
    Convert absolute degree [0, 360) to (sign_index_1_based, degree_in_sign).
    Enforces the half-open interval [0.0, 30.0) for degree_in_sign.
    """
    deg = validate_finite_degree(raw_degree) % 360.0
    sign_idx = int(deg // 30.0) + 1
    deg_in_sign = deg % 30.0
    # Guard against precision rollover at 30.0
    if deg_in_sign >= 30.0:
        deg_in_sign = 0.0
        sign_idx = ((sign_idx) % 12) + 1
    return sign_idx, deg_in_sign


def parse_sign_index(sign_input: Any) -> int:
    """Parse integer, string, or name into a 1-indexed sign number [1..12]."""
    if isinstance(sign_input, int):
        if 1 <= sign_input <= 12:
            return sign_input
        raise ValueError(f"Sign integer must be between 1 and 12, got: {sign_input}")
    if isinstance(sign_input, str):
        cleaned = sign_input.strip().lower()
        if cleaned.isdigit():
            val = int(cleaned)
            if 1 <= val <= 12:
                return val
            raise ValueError(f"Sign integer string must be 1..12, got: {val}")
        if cleaned in SIGN_NAME_TO_INDEX:
            return SIGN_NAME_TO_INDEX[cleaned]
    raise ValueError(f"Unrecognized zodiac sign: {sign_input}")


# ==============================================================================
# 4. Rahu Traversal Metric (DEC-JAI-02)
# ==============================================================================

def compute_rahu_traversal_arc(raw_degree: float, rahu_reverse: bool = True) -> float:
    """
    Compute the scalar traversed arc length for Rahu within its sign.
    
    In Jaimini astrology, because lunar nodes travel retrograde (from 30° toward 0°),
    their traversal progress through the sign is measured in reverse:
        tau = 30.0 - (raw_degree % 30.0)
    
    Domain:
        - When Rahu enters sign at 29.999999°, tau = 0.000001° (near beginning of traversal).
        - When Rahu exits sign at 0.000000°, tau = 30.000000° (full traversal completed).
        - Traversed arc length is in (0.0, 30.0].
    
    If rahu_reverse is False, returns direct degree in sign [0.0, 30.0).
    """
    deg = validate_finite_degree(raw_degree)
    deg_in_sign = deg % 30.0
    
    if rahu_reverse:
        traversed = 30.0 - deg_in_sign
        # Traversed arc is in range (0.0, 30.0]
        return round(traversed, 6)
    return round(deg_in_sign, 6)


calculate_rahu_traversal = compute_rahu_traversal_arc


# ==============================================================================
# 5. Chara Karaka Engine (Rules JAI-KAR-01 to JAI-KAR-05)
# ==============================================================================

def calculate_chara_karakas(
    planets: list[dict[str, Any]] | dict[str, Any],
    scheme: KarakaSchemeEnum = KarakaSchemeEnum.SEVEN_KARAKA,
    rahu_reverse: bool = True,
    tie_breaker: TieBreakerEnum = TieBreakerEnum.NATURAL_SPEED,
) -> dict[str, Any]:
    """
    Calculate Jaimini Chara Karakas deterministically.
    
    Args:
        planets: List or dict of planet objects with keys 'name'/'planet' and 'degree'/'longitude'.
        scheme: SEVEN_KARAKA (Sun-Saturn, 7 roles) or EIGHT_KARAKA (7 planets + Rahu, 8 roles).
        rahu_reverse: If True, Rahu uses inverted traversed arc (30.0 - deg).
        tie_breaker: Tie-breaking method for identical arcdegrees.
        
    Returns:
        dict containing:
            - karakas: Mapping of role -> planet details dict
            - scheme: active scheme string
            - tie_broken: bool flag
            - tie_break_details: list of notes if ties occurred
            - candidate_rankings: ordered list of all evaluated bodies
    """
    # 1. Normalize input planets into a map: planet_name -> raw_degree
    planet_degrees: dict[str, float] = {}
    if isinstance(planets, dict):
        for k, v in planets.items():
            if isinstance(v, dict):
                pname = v.get("name") or v.get("planet") or k
                deg = v.get("degree") if "degree" in v else v.get("longitude")
            else:
                pname = k
                deg = v
            if pname and deg is not None:
                planet_degrees[str(pname)] = validate_finite_degree(deg)
    elif isinstance(planets, list):
        for p in planets:
            if not isinstance(p, dict):
                continue
            pname = p.get("name") or p.get("planet")
            deg = p.get("degree") if "degree" in p else p.get("longitude")
            if pname and deg is not None:
                planet_degrees[str(pname)] = validate_finite_degree(deg)
    else:
        raise ValueError("Planets input must be a list of dicts or a dictionary.")

    # 2. Filter eligible bodies
    required_bodies = CLASSICAL_7_BODIES if scheme == KarakaSchemeEnum.SEVEN_KARAKA else EIGHT_KARAKA_BODIES
    missing_bodies = [b for b in required_bodies if b not in planet_degrees]
    if missing_bodies:
        raise ValueError(
            f"Insufficient planetary candidates for {scheme.value} scheme. "
            f"Missing required bodies: {missing_bodies}"
        )

    # 3. Compute effective traversed arc for each candidate
    candidate_items: list[dict[str, Any]] = []
    for b in required_bodies:
        raw_deg = planet_degrees[b]
        sign_idx, deg_in_sign = normalize_sign_degree(raw_deg)
        
        if b == "Rahu":
            effective_arc = compute_rahu_traversal_arc(raw_deg, rahu_reverse=rahu_reverse)
        else:
            effective_arc = round(deg_in_sign, 6)
            
        candidate_items.append({
            "name": b,
            "raw_degree": round(raw_deg, 6),
            "sign_index": sign_idx,
            "sign_name": SIGN_NAMES_SK[sign_idx],
            "degree_in_sign": round(deg_in_sign, 6),
            "traversed_arc": effective_arc,
            "speed_rank": NATURAL_SPEED_RANK.get(b, 99),
        })

    # 4. Deterministic Sort
    # Primary: traversed_arc descending
    # Secondary: natural speed rank ascending (1 = Sun, 2 = Moon, ... 8 = Rahu)
    # Tertiary: alphabetical name
    def sort_key(item: dict[str, Any]) -> tuple[float, int, str]:
        return (-item["traversed_arc"], item["speed_rank"], item["name"])

    candidate_items.sort(key=sort_key)

    # 5. Check for degree ties down to 1e-5 arcdegrees
    tie_broken = False
    tie_break_details: list[str] = []
    for i in range(len(candidate_items) - 1):
        c1 = candidate_items[i]
        c2 = candidate_items[i + 1]
        if abs(c1["traversed_arc"] - c2["traversed_arc"]) < 1e-5:
            tie_broken = True
            msg = (
                f"Degree tie between {c1['name']} ({c1['traversed_arc']}°) and "
                f"{c2['name']} ({c2['traversed_arc']}°) resolved via {tie_breaker.value} fallback "
                f"({c1['name']} speed_rank={c1['speed_rank']} ahead of {c2['name']} speed_rank={c2['speed_rank']})."
            )
            tie_break_details.append(msg)

    # 6. Map Roles
    roles = ROLES_7_KARAKA if scheme == KarakaSchemeEnum.SEVEN_KARAKA else ROLES_8_KARAKA
    karaka_map: dict[str, Any] = {}
    for rank_idx, role_name in enumerate(roles):
        winner = candidate_items[rank_idx]
        karaka_map[role_name] = {
            "role": role_name,
            "planet": winner["name"],
            "rank": rank_idx,
            "degree_in_sign": winner["degree_in_sign"],
            "traversed_arc": winner["traversed_arc"],
            "sign_index": winner["sign_index"],
            "sign_name": winner["sign_name"],
        }

    return {
        "karakas": karaka_map,
        "scheme": scheme.value,
        "tie_broken": tie_broken,
        "tie_break_details": tie_break_details,
        "candidate_rankings": candidate_items,
    }


# ==============================================================================
# 6. Arudha Pada Engine (Rules JAI-ARD-01 to JAI-ARD-05)
# ==============================================================================

def calculate_raw_arudha(house_sign: int, lord_sign: int) -> int:
    """
    Calculate the raw, unshifted Arudha Pada sign before exceptions.
    Formula:
        Distance D = ((lord_sign - house_sign) % 12) + 1
        Raw Pada P = ((lord_sign - 1 + (D - 1)) % 12) + 1
                   = ((2 * lord_sign - house_sign - 1) % 12) + 1
    Returns:
        Sign index in 1..12.
    """
    h = parse_sign_index(house_sign)
    l = parse_sign_index(lord_sign)
    return ((2 * l - h - 1) % 12) + 1


def apply_arudha_exception(
    house_sign: int,
    raw_pada: int,
    convention: ArudhaExceptionEnum = ArudhaExceptionEnum.STANDARD_EXCEPTION,
) -> tuple[int, bool, Optional[str]]:
    """
    Apply classical Arudha exceptions (BPHS Ch. 30, v. 5-7).
    
    Standard BPHS Pada-Locus Rule:
        An Arudha cannot occupy the house itself (H) or the 7th from it (H_7).
        - If raw_pada == H (Swastha): Shift 10 houses forward from H.
        - If raw_pada == H_7 (Saptama): Shift 10 houses from H_7 (= 4th from H).
        
    Returns:
        tuple of (final_sign_index, exception_applied_bool, exception_type_str)
    """
    h = parse_sign_index(house_sign)
    p = parse_sign_index(raw_pada)
    
    if convention == ArudhaExceptionEnum.NO_EXCEPTION:
        return p, False, None
        
    h7 = ((h - 1 + 6) % 12) + 1
    
    if convention == ArudhaExceptionEnum.STANDARD_EXCEPTION:
        if p == h:
            # Swastha exception: Pada falls in source house -> 10th from house
            final_pada = ((h - 1 + 9) % 12) + 1
            return final_pada, True, "SWASTHA_10TH_SHIFT"
        elif p == h7:
            # Saptama exception: Pada falls in 7th from source -> 10th from 7th (= 4th from H)
            final_pada = ((h7 - 1 + 9) % 12) + 1
            return final_pada, True, "SAPTAMA_4TH_SHIFT"
        else:
            return p, False, None
            
    # Rath Kumbha / Vrishik fallback convention if specified
    if convention == ArudhaExceptionEnum.RATH_KUMBHA_VRISHIK:
        if p == h:
            final_pada = ((h - 1 + 9) % 12) + 1
            return final_pada, True, "SWASTHA_10TH_SHIFT"
        elif p == h7:
            final_pada = ((h7 - 1 + 9) % 12) + 1
            return final_pada, True, "SAPTAMA_4TH_SHIFT"
        return p, False, None

    raise ValueError(f"Unsupported Arudha exception convention: {convention}")


def calculate_arudha_pada(
    house_num: int,
    lagna_sign: int | str,
    lord_sign: int | str,
    convention: ArudhaExceptionEnum = ArudhaExceptionEnum.STANDARD_EXCEPTION,
) -> dict[str, Any]:
    """
    Calculate the Arudha Pada for any given house number (1 to 12).
    
    Args:
        house_num: Target house number (1..12).
        lagna_sign: Sign of the 1st house (Lagna).
        lord_sign: Sign occupied by the lord of the target house.
        convention: Exception convention enum.
        
    Returns:
        dict containing:
            - house: house number (1..12)
            - name: e.g. "AL" for house 1, "UL" for house 12, "A2".."A11"
            - house_sign: sign index of source house
            - house_sign_name: Sanskrit name of source house sign
            - lord_sign: sign index of lord
            - lord_sign_name: Sanskrit name of lord sign
            - raw_pada: raw sign index
            - final_pada: final sign index after exception
            - final_sign_name: Sanskrit name of final sign
            - exception_applied: bool
            - exception_type: str or None
    """
    if not (1 <= house_num <= 12):
        raise ValueError(f"House number must be 1..12, got: {house_num}")
    
    lagna_idx = parse_sign_index(lagna_sign)
    lord_idx = parse_sign_index(lord_sign)
    
    # Sign index of target house in whole-sign system
    h_sign = ((lagna_idx - 1 + (house_num - 1)) % 12) + 1
    
    raw_p = calculate_raw_arudha(h_sign, lord_idx)
    final_p, exc_applied, exc_type = apply_arudha_exception(h_sign, raw_p, convention)
    
    pada_names = {
        1: "AL", 2: "A2", 3: "A3", 4: "A4", 5: "A5", 6: "A6",
        7: "A7", 8: "A8", 9: "A9", 10: "A10", 11: "A11", 12: "UL",
    }
    
    return {
        "house": house_num,
        "name": pada_names[house_num],
        "house_sign": h_sign,
        "house_sign_name": SIGN_NAMES_SK[h_sign],
        "lord_sign": lord_idx,
        "lord_sign_name": SIGN_NAMES_SK[lord_idx],
        "raw_pada": raw_p,
        "final_pada": final_p,
        "final_sign_name": SIGN_NAMES_SK[final_p],
        "exception_applied": exc_applied,
        "exception_type": exc_type,
    }


def calculate_upapada_lagna(
    lagna_sign: int | str,
    twelfth_lord_sign: int | str,
    convention: ArudhaExceptionEnum = ArudhaExceptionEnum.STANDARD_EXCEPTION,
) -> dict[str, Any]:
    """
    Calculate Upapada Lagna (UL / A12), the Arudha of the 12th house.
    
    Mathematical Invariant:
        Under whole-sign houses and standard BPHS 1st/7th exceptions, UL relative
        to natal Lagna can ONLY fall in houses [2, 3, 4, 8, 9, 10].
        It can NEVER fall in houses [1, 5, 6, 7, 11, 12].
    """
    res = calculate_arudha_pada(12, lagna_sign, twelfth_lord_sign, convention)
    res["is_upapada"] = True
    
    # Calculate relative house from Lagna
    lagna_idx = parse_sign_index(lagna_sign)
    final_pada = res["final_pada"]
    rel_house_from_lagna = ((final_pada - lagna_idx) % 12) + 1
    res["house_from_lagna"] = rel_house_from_lagna
    
    return res


def calculate_all_arudhas(
    lagna_sign: int | str,
    lord_placements: dict[int, int | str],
    convention: ArudhaExceptionEnum = ArudhaExceptionEnum.STANDARD_EXCEPTION,
) -> dict[str, Any]:
    """
    Calculate all 12 Arudhas (AL, A2–A11, UL) simultaneously.
    
    Args:
        lagna_sign: Natal Lagna sign.
        lord_placements: Mapping of house number (1..12) -> lord sign (int or str).
        convention: Arudha exception enum.
        
    Returns:
        dict mapping pada name ("AL", "A2", ... "UL") -> pada details dict.
    """
    lagna_idx = parse_sign_index(lagna_sign)
    all_padas: dict[str, Any] = {}
    
    for h in range(1, 13):
        if h not in lord_placements:
            raise ValueError(f"Missing lord placement for house {h} in lord_placements dict.")
        lord_s = lord_placements[h]
        pada_info = calculate_arudha_pada(h, lagna_idx, lord_s, convention)
        all_padas[pada_info["name"]] = pada_info
        
    return all_padas


# ==============================================================================
# 7. Rashi Drishti Engine (Rule JAI-ASP-01)
# ==============================================================================

def get_rashi_drishti(sign: int | str) -> list[int]:
    """
    Calculate Jaimini Rashi Drishti (sign-based structural aspects).
    
    Classical Rule (Jaimini Sutras 1.1.3-6, BPHS Ch. 29, v. 12-15):
        - Movable (Chara: 1, 4, 7, 10) aspect all Fixed signs EXCEPT the adjacent one (S + 1).
        - Fixed (Sthira: 2, 5, 8, 11) aspect all Movable signs EXCEPT the adjacent one (S - 1).
        - Dual (Dvisvabhava: 3, 6, 9, 12) aspect all OTHER Dual signs.
        
    Returns:
        Sorted list of aspected sign indices (1..12). Exactly 3 signs are aspected.
    """
    s = parse_sign_index(sign)
    
    if s in CHARA_SIGNS:
        # Aspects Fixed signs EXCEPT adjacent one (s + 1)
        adjacent_fixed = (s % 12) + 1
        aspected = STHIRA_SIGNS - {adjacent_fixed}
    elif s in STHIRA_SIGNS:
        # Aspects Movable signs EXCEPT adjacent preceding one (s - 1)
        adjacent_chara = ((s - 2) % 12) + 1
        aspected = CHARA_SIGNS - {adjacent_chara}
    elif s in DVISVABHAVA_SIGNS:
        # Aspects all other Dual signs
        aspected = DVISVABHAVA_SIGNS - {s}
    else:
        raise ValueError(f"Invalid sign index for Rashi Drishti: {s}")
        
    return sorted(list(aspected))


def get_all_rashi_drishti_pairs() -> dict[int, list[int]]:
    """
    Generate all 36 directed aspect pairs across the entire zodiac.
    Invariant: Every sign aspects exactly 3 other signs. Total pairs = 12 * 3 = 36.
    Zero self-aspects; zero adjacent aspects.
    """
    return {s: get_rashi_drishti(s) for s in range(1, 13)}


# Function alias
get_rashi_drishti_aspects = get_rashi_drishti
