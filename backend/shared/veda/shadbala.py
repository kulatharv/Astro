"""
Shadbala — Six-Fold Planetary Strength Computation Engine.

Source:  Brihat Parasara Hora Shastra (BPHS), Chapter 27.
         Phaladeepika, Bhavartha Ratnakara.
Units:   Virupas (1 Rupa = 60 Virupas).
         All intermediate values stored in Virupas; divide by 60 for Rupas.

Components
----------
1. Sthana Bala  — Positional / dignity strength (5 sub-components).
2. Dig Bala     — Directional strength by house placement.
3. Kala Bala    — Temporal strength (day/night, planetary hour, pack sub-types).
4. Chesta Bala  — Motional strength (retrograde, direct, stations).
5. Naisargika Bala — Natural / permanent strength (fixed ranking).
6. Drik Bala    — Aspectual strength from other planets.

Public API
----------
  shadbala(planet, sign, house, degree, retrograde, birth_dt, chart) -> ShadbalaResult
  shadbala_summary(chart_planets) -> dict[str, ShadbalaResult]
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from .zodiac import SIGNS_SK, SIGN_LORDS
from .strength import EXALTATION, DEBILITATION, OWN_SIGNS
from .dignity import MOOLATRIKONA, get_naisargika_dignity

# ---------------------------------------------------------------------------
# Constants — sourced from BPHS Ch. 27 unless otherwise noted
# ---------------------------------------------------------------------------

# Deep exaltation degrees (degrees within the sign, 0-based) — BPHS
DEEP_EXALTATION_DEGREE: dict[str, float] = {
    "Sun": 10.0,      # Mesha  10 deg
    "Moon": 3.0,      # Vrishabha 3 deg
    "Mars": 28.0,     # Makara 28 deg
    "Mercury": 15.0,  # Kanya  15 deg
    "Jupiter": 5.0,   # Karka  5 deg
    "Venus": 27.0,    # Meena  27 deg
    "Saturn": 20.0,   # Tula   20 deg
    "Rahu": 20.0,     # Vrishabha 20 deg (Parashari convention)
    "Ketu": 20.0,     # Vrischika 20 deg
}

# Moolatrikona spans — (sign, from_degree, to_degree) — BPHS Ch. 3
MOOLATRIKONA_SPAN: dict[str, tuple[str, float, float]] = {
    "Sun":     ("Simha",     0.0, 20.0),
    "Moon":    ("Vrishabha", 4.0, 20.0),
    "Mars":    ("Mesha",     0.0, 12.0),
    "Mercury": ("Kanya",     16.0, 20.0),
    "Jupiter": ("Dhanu",     0.0, 10.0),
    "Venus":   ("Tula",      0.0, 15.0),
    "Saturn":  ("Kumbha",    0.0, 20.0),
}

# Dig Bala — each planet has maximum directional strength in a specific house — BPHS
DIG_BALA_HOUSE: dict[str, int] = {
    "Sun":     10,  # 10th house (South)
    "Mars":    10,
    "Jupiter": 1,   # Lagna / 1st house (East)
    "Mercury": 1,
    "Moon":    4,   # 4th house (North)
    "Venus":   4,
    "Saturn":  7,   # 7th house (West)
    "Rahu":    3,   # conventional
    "Ketu":    9,
}

# Naisargika (Natural) Bala — fixed values in Virupas — BPHS Ch. 27
NAISARGIKA_BALA: dict[str, float] = {
    "Sun":     60.0,
    "Moon":    51.43,
    "Venus":   45.0,
    "Jupiter": 34.29,
    "Mercury": 25.71,
    "Mars":    17.14,
    "Saturn":   8.57,
    "Rahu":     8.57,
    "Ketu":     8.57,
}

# Sthana Bala sub-weights (Virupas at full score) — BPHS
STHANA_UCCHA_MAX = 60.0
STHANA_SAPTHAVARGA_MAX = 45.0
STHANA_OJAYUGMA_MAX = 15.0
STHANA_KP_MAX = 30.0
STHANA_DREKKANA_MAX = 15.0

# Kala Bala — day/night planet classification — BPHS Ch. 27
DAY_PLANETS = {"Sun", "Jupiter", "Saturn"}
NIGHT_PLANETS = {"Moon", "Venus", "Mars"}
DIURNAL_PLANETS = DAY_PLANETS
NOCTURNAL_PLANETS = NIGHT_PLANETS

# Natural benefics/malefics for aspect scoring
NATURAL_BENEFICS = {"Jupiter", "Venus", "Mercury", "Moon"}
NATURAL_MALEFICS = {"Sun", "Mars", "Saturn", "Rahu", "Ketu"}

# Aspect strength fractions for Drik Bala
PARASHARI_ASPECT_STRENGTH: dict[int, float] = {
    7: 1.0,
    4: 0.75,
    5: 0.75,
    8: 0.75,
    3: 0.5,
    9: 0.5,
    10: 0.5,
    12: 0.25,
}

# Planets with special aspects
SPECIAL_ASPECTS: dict[str, list[int]] = {
    "Mars":    [4, 7, 8],
    "Jupiter": [5, 7, 9],
    "Saturn":  [3, 7, 10],
    "Rahu":    [5, 7, 9],
    "Ketu":    [5, 7, 9],
}


# ---------------------------------------------------------------------------
# Result dataclass
# ---------------------------------------------------------------------------

@dataclass
class ShadbalaResult:
    """Full Shadbala breakdown for a single planet. All values in Virupas."""
    planet: str

    # Sthana Bala components
    uccha_bala: float = 0.0
    sapthavarga_bala: float = 0.0
    ojayugma_bala: float = 0.0
    kendra_bala: float = 0.0
    drekkana_bala: float = 0.0
    sthana_bala: float = 0.0

    # Other bala components
    dig_bala: float = 0.0
    kala_bala: float = 0.0
    chesta_bala: float = 0.0
    naisargika_bala: float = 0.0
    drik_bala: float = 0.0

    # Totals
    total_virupas: float = 0.0
    total_rupas: float = 0.0

    # BPHS minimum required Rupas norms
    minimum_rupas: float = 0.0
    is_strong: bool = False

    breakdown: dict = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Minimum required Rupas — BPHS Ch. 27
# ---------------------------------------------------------------------------

MINIMUM_RUPAS: dict[str, float] = {
    "Sun":     5.0,
    "Moon":    6.0,
    "Mars":    5.0,
    "Mercury": 7.0,
    "Jupiter": 6.5,
    "Venus":   5.5,
    "Saturn":  5.0,
    "Rahu":    4.0,
    "Ketu":    4.0,
}


# ---------------------------------------------------------------------------
# 1. Sthana Bala (Positional Strength)
# ---------------------------------------------------------------------------

def _uccha_bala(planet: str, sign: str, degree_in_sign: float) -> float:
    """
    Uccha Bala — strength based on distance from deep exaltation point.
    Max 60 Virupas at deep exaltation; 0 at deep debilitation point.
    Formula: (180 - abs(exalt_lon - planet_lon)) / 3
    """
    exalt_sign = EXALTATION.get(planet)
    if not exalt_sign:
        return 30.0

    try:
        exalt_sign_idx = SIGNS_SK.index(exalt_sign)
    except ValueError:
        return 30.0

    deep_deg = DEEP_EXALTATION_DEGREE.get(planet, 0.0)
    exalt_lon = exalt_sign_idx * 30.0 + deep_deg

    try:
        planet_sign_idx = SIGNS_SK.index(sign)
    except ValueError:
        return 30.0

    planet_lon = planet_sign_idx * 30.0 + degree_in_sign

    diff = abs(exalt_lon - planet_lon)
    if diff > 180:
        diff = 360 - diff

    return round((180 - diff) / 3.0, 2)


def _sapthavarga_bala(planet: str, sign: str) -> float:
    """
    Saptavarga Bala — positional score across seven divisional charts.
    NOTE: PARTIAL — uses D1 dignity proxy only.
    Full 7-varga computation planned for WP8.
    """
    dignity = get_naisargika_dignity(planet, sign)
    dignity_score_map = {
        "Exalted": 45.0,
        "Moolatrikona": 37.5,
        "Own Sign": 30.0,
        "Great Friend": 22.5,
        "Friend": 15.0,
        "Neutral": 7.5,
        "Enemy": 3.75,
        "Great Enemy": 1.875,
        "Debilitated": 0.0,
    }
    return dignity_score_map.get(dignity, 7.5)


def _ojayugma_bala(planet: str, sign: str) -> float:
    """
    Ojayugma Bala — odd/even sign bonus.
    Sun, Jupiter, Mars gain strength in odd signs.
    Moon, Venus gain strength in even signs.
    """
    try:
        sign_idx = SIGNS_SK.index(sign) + 1
    except ValueError:
        return 0.0

    is_odd = (sign_idx % 2 == 1)

    if planet in {"Sun", "Jupiter", "Mars"}:
        return 15.0 if is_odd else 0.0
    if planet in {"Moon", "Venus"}:
        return 0.0 if is_odd else 15.0
    return 7.5  # Mercury, Saturn, nodes


def _kendra_bala(house: int) -> float:
    """
    Kendra Bala — Kendras (1,4,7,10)=60; Panaparas (2,5,8,11)=30; Apoklimas=15.
    """
    if house in (1, 4, 7, 10):
        return 60.0
    if house in (2, 5, 8, 11):
        return 30.0
    return 15.0


def _drekkana_bala(planet: str, degree_in_sign: float) -> float:
    """
    Drekkana Bala — decanate position bonus.
    Male planets gain in 1st decanate; female planets gain in 3rd decanate.
    """
    decanate = int(degree_in_sign / 10)  # 0, 1, or 2
    if decanate == 0 and planet in {"Sun", "Mars", "Jupiter", "Rahu"}:
        return 15.0
    if decanate == 2 and planet in {"Moon", "Venus", "Ketu"}:
        return 15.0
    return 0.0


def compute_sthana_bala(planet: str, sign: str, house: int, degree_in_sign: float) -> dict:
    """Compute all five Sthana Bala sub-components. Returns dict with Virupa breakdown."""
    uccha  = _uccha_bala(planet, sign, degree_in_sign)
    sapta  = _sapthavarga_bala(planet, sign)
    oja    = _ojayugma_bala(planet, sign)
    kendra = _kendra_bala(house)
    drek   = _drekkana_bala(planet, degree_in_sign)
    total  = round(uccha + sapta + oja + kendra + drek, 2)
    return {
        "uccha_bala": uccha,
        "sapthavarga_bala": sapta,
        "ojayugma_bala": oja,
        "kendra_bala": kendra,
        "drekkana_bala": drek,
        "sthana_bala_total": total,
    }


# ---------------------------------------------------------------------------
# 2. Dig Bala (Directional Strength)
# ---------------------------------------------------------------------------

def compute_dig_bala(planet: str, house: int) -> float:
    """
    Dig Bala — max 60 Virupas at the planet's ideal directional house.
    Decreases linearly to 0 at the opposite house.
    """
    ideal_house = DIG_BALA_HOUSE.get(planet, 1)
    distance = abs(house - ideal_house)
    if distance > 6:
        distance = 12 - distance
    return round(max(0.0, 60.0 * (1 - distance / 6.0)), 2)


# ---------------------------------------------------------------------------
# 3. Kala Bala (Temporal Strength)
# ---------------------------------------------------------------------------

def compute_kala_bala(
    planet: str,
    birth_dt: Optional[datetime] = None,
    is_daytime: bool = True,
    is_shukla_paksha: bool = True,
) -> float:
    """
    Kala Bala (simplified, 3/9 sub-components).

    Covers: Paksha Bala, Nathonnatha (day/night), Vara Bala (weekday).
    NOTE: PARTIAL — full 9-component expansion planned for WP6.
    """
    score = 0.0

    # Paksha Bala
    if planet == "Moon":
        score += 60.0 if is_shukla_paksha else 0.0
    elif planet in NATURAL_BENEFICS:
        score += 30.0 if is_shukla_paksha else 15.0
    else:
        score += 15.0 if is_shukla_paksha else 30.0

    # Nathonnatha (day/night)
    if planet in DIURNAL_PLANETS and is_daytime:
        score += 30.0
    elif planet in NOCTURNAL_PLANETS and not is_daytime:
        score += 30.0
    elif planet == "Mercury":
        score += 30.0  # Mercury is ahoratra (always strong)

    # Vara Bala (weekday ruler)
    if birth_dt is not None:
        weekday = birth_dt.weekday()  # Mon=0 ... Sun=6
        VARA_LORD = {0: "Moon", 1: "Mars", 2: "Mercury",
                     3: "Jupiter", 4: "Venus", 5: "Saturn", 6: "Sun"}
        if VARA_LORD.get(weekday) == planet:
            score += 45.0

    return round(min(score, 60.0), 2)


# ---------------------------------------------------------------------------
# 4. Chesta Bala (Motional Strength)
# ---------------------------------------------------------------------------

def compute_chesta_bala(planet: str, retrograde: bool, speed_ratio: float = 0.0) -> float:
    """
    Chesta Bala — motional / kinetic strength.
    Retrograde = 60 Virupas; Stationary = 30; Direct = 0-30 based on speed.
    Sun and Moon have no Chesta Bala; Nodes are always retrograde.
    """
    if planet in ("Sun", "Moon"):
        return 0.0

    if planet in ("Rahu", "Ketu") or retrograde:
        return 60.0

    if speed_ratio == 0.0:
        return 30.0  # Stationary

    ratio_clamped = min(abs(speed_ratio), 1.0)
    return round(30.0 * ratio_clamped, 2)


# ---------------------------------------------------------------------------
# 5. Naisargika Bala (Natural Strength)
# ---------------------------------------------------------------------------

def compute_naisargika_bala(planet: str) -> float:
    """Return fixed natural permanent strength in Virupas — BPHS."""
    return NAISARGIKA_BALA.get(planet, 25.0)


# ---------------------------------------------------------------------------
# 6. Drik Bala (Aspectual Strength)
# ---------------------------------------------------------------------------

def compute_drik_bala(planet: str, planet_house: int, planet_map: dict) -> float:
    """
    Drik Bala — strength from aspects received from other planets.
    Benefic aspects add; Malefic aspects subtract.
    """
    score = 0.0

    for other_name, other_data in planet_map.items():
        if other_name == planet:
            continue
        other_house = other_data.get("house", 0)
        if not other_house:
            continue
        for (asp_house, asp_strength) in _get_aspected_houses(other_name, other_house):
            if asp_house == planet_house:
                if other_name in NATURAL_BENEFICS:
                    score += 30.0 * asp_strength
                else:
                    score -= 30.0 * asp_strength

    return round(max(-60.0, min(60.0, score)), 2)


def _get_aspected_houses(planet: str, from_house: int) -> list[tuple[int, float]]:
    """Return list of (house_number, strength_fraction) for a planet's Parashari aspects."""
    special = SPECIAL_ASPECTS.get(planet, [7])
    return [
        (((from_house - 1 + offset - 1) % 12) + 1, PARASHARI_ASPECT_STRENGTH.get(offset, 0.5))
        for offset in special
    ]


# ---------------------------------------------------------------------------
# Main public API
# ---------------------------------------------------------------------------

def shadbala(
    planet: str,
    sign: str,
    house: int,
    degree_in_sign: float = 0.0,
    retrograde: bool = False,
    birth_dt: Optional[datetime] = None,
    is_daytime: bool = True,
    is_shukla_paksha: bool = True,
    speed_ratio: float = 0.0,
    planet_map: Optional[dict] = None,
) -> ShadbalaResult:
    """
    Compute full Shadbala for a single planet.

    Parameters
    ----------
    planet          : Planet name (e.g. "Sun", "Mars").
    sign            : Rasi sign in Sanskrit (e.g. "Mesha").
    house           : House number 1-12.
    degree_in_sign  : Longitude within the sign (0.0-29.99).
    retrograde      : True if planet is retrograde.
    birth_dt        : Birth datetime for Kala Bala weekday calculation.
    is_daytime      : True if birth is during daytime.
    is_shukla_paksha: True if Moon is in waxing phase.
    speed_ratio     : actual_speed / mean_speed for Chesta Bala.
    planet_map      : Full chart planet positions for Drik Bala.

    Returns
    -------
    ShadbalaResult with individual component values and totals.
    """
    result = ShadbalaResult(planet=planet)

    sthana = compute_sthana_bala(planet, sign, house, degree_in_sign)
    result.uccha_bala       = sthana["uccha_bala"]
    result.sapthavarga_bala = sthana["sapthavarga_bala"]
    result.ojayugma_bala    = sthana["ojayugma_bala"]
    result.kendra_bala      = sthana["kendra_bala"]
    result.drekkana_bala    = sthana["drekkana_bala"]
    result.sthana_bala      = sthana["sthana_bala_total"]

    result.dig_bala        = compute_dig_bala(planet, house)
    result.kala_bala       = compute_kala_bala(planet, birth_dt, is_daytime, is_shukla_paksha)
    result.chesta_bala     = compute_chesta_bala(planet, retrograde, speed_ratio)
    result.naisargika_bala = compute_naisargika_bala(planet)
    result.drik_bala       = compute_drik_bala(planet, house, planet_map or {})

    result.total_virupas = round(
        result.sthana_bala + result.dig_bala + result.kala_bala +
        result.chesta_bala + result.naisargika_bala + result.drik_bala,
        2,
    )
    result.total_rupas   = round(result.total_virupas / 60.0, 4)
    result.minimum_rupas = MINIMUM_RUPAS.get(planet, 5.0)
    result.is_strong     = result.total_rupas >= result.minimum_rupas

    result.breakdown = {
        "sthana_bala": {
            "uccha_bala": result.uccha_bala,
            "sapthavarga_bala": result.sapthavarga_bala,
            "ojayugma_bala": result.ojayugma_bala,
            "kendra_bala": result.kendra_bala,
            "drekkana_bala": result.drekkana_bala,
            "total": result.sthana_bala,
        },
        "dig_bala": result.dig_bala,
        "kala_bala": result.kala_bala,
        "chesta_bala": result.chesta_bala,
        "naisargika_bala": result.naisargika_bala,
        "drik_bala": result.drik_bala,
        "total_virupas": result.total_virupas,
        "total_rupas": result.total_rupas,
        "minimum_required_rupas": result.minimum_rupas,
        "is_strong": result.is_strong,
        "notes": [
            "sapthavarga_bala: D1-only proxy; full 7-varga expansion in WP8.",
            "kala_bala: 3/9 sub-components; full 9-component expansion in WP6.",
        ],
    }

    return result


def shadbala_summary(chart_planets: dict) -> dict[str, ShadbalaResult]:
    """
    Compute Shadbala for all planets in the chart.

    Input format:
    {
      "Sun": {"sign": "Mesha", "house": 1, "degree": 10.0, "retrograde": False},
      ...
    }
    """
    results = {}
    for planet, data in chart_planets.items():
        if not isinstance(data, dict):
            continue
        results[planet] = shadbala(
            planet=planet,
            sign=data.get("sign", "Mesha"),
            house=int(data.get("house", 1)),
            degree_in_sign=float(data.get("degree", 0.0)),
            retrograde=bool(data.get("retrograde", False)),
            birth_dt=data.get("birth_dt"),
            is_daytime=data.get("is_daytime", True),
            is_shukla_paksha=data.get("is_shukla_paksha", True),
            speed_ratio=float(data.get("speed_ratio", 0.0)),
            planet_map=chart_planets,
        )
    return results
