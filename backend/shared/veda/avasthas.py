"""
Planetary Avasthas (States / Conditions) Engine.

Source:  Brihat Parasara Hora Shastra (BPHS), Chapter 45-47.
         Saravali, Jataka Parijata.

Avasthas describe the experiential state a planet is in — directly
influencing the quality of results it gives. Multiple Avastha layers
are implemented:

  1. Baladi (Age) Avasthas    — 5 states based on degree in sign.
  2. Jagradi (Waking) Avasthas — 3 states (Jagrad/Swapna/Sushupti) based
                                  on sign element.
  3. Lajjitadi Avasthas       — 6 states arising from house/conjunction/
                                  aspect context.

Public API
----------
  get_baladi_avastha(planet, degree_in_sign) -> str
  get_jagradi_avastha(sign) -> str
  get_lajjitadi_avasthas(planet, house, sign, planet_map) -> list[str]
  evaluate_avasthas(planet, sign, house, degree_in_sign, planet_map) -> dict
"""

from __future__ import annotations

from typing import Optional
from .zodiac import SIGNS_SK

# ---------------------------------------------------------------------------
# 1. Baladi Avasthas — based on degree within sign (0-29.99)
# ---------------------------------------------------------------------------

# For odd signs: Bala (0-6), Kumara (6-12), Yuva (12-18), Vriddha (18-24), Mrita (24-30)
# For even signs: reversed order
BALADI_STATES = ["Bala", "Kumara", "Yuva", "Vriddha", "Mrita"]
BALADI_STRENGTH = {
    "Bala":    0.25,   # infant — very weak results
    "Kumara":  0.50,   # adolescent
    "Yuva":    1.00,   # youth — full strength
    "Vriddha": 0.75,   # old
    "Mrita":   0.25,   # dead — gives results with great difficulty
}


def get_baladi_avastha(sign: str, degree_in_sign: float) -> str:
    """
    Baladi Avastha — 5 age states based on degree in sign.
    Odd sign: Bala at 0-6, Mrita at 24-30.
    Even sign: Mrita at 0-6, Bala at 24-30.
    """
    try:
        sign_idx = SIGNS_SK.index(sign) + 1  # 1-based
    except ValueError:
        return "Yuva"

    is_odd = (sign_idx % 2 == 1)
    segment = int(degree_in_sign / 6)  # 0 to 4
    segment = min(segment, 4)

    if is_odd:
        return BALADI_STATES[segment]
    else:
        return BALADI_STATES[4 - segment]


def baladi_strength_multiplier(sign: str, degree_in_sign: float) -> float:
    """Return strength multiplier [0.25 to 1.0] for a planet's Baladi Avastha."""
    avastha = get_baladi_avastha(sign, degree_in_sign)
    return BALADI_STRENGTH.get(avastha, 0.75)


# ---------------------------------------------------------------------------
# 2. Jagradi Avasthas — based on sign element
# ---------------------------------------------------------------------------

# Sign element mapping for Jagradi (per BPHS / Saravali conventions)
# Fire (1,5,9) and Earth (2,6,10) signs have different states for each planet
# Simplified model: sign modality determines state
JAGRADI_STATE_BY_MODALITY = {
    "Cardinal": "Jagrat",   # Fully awake — gives full results
    "Fixed":    "Swapna",   # Dreaming — gives half results
    "Mutable":  "Sushupti", # Deep sleep — gives quarter results
}

MODALITY_BY_SIGN_IDX = {
    1: "Cardinal", 2: "Fixed", 3: "Mutable",
    4: "Cardinal", 5: "Fixed", 6: "Mutable",
    7: "Cardinal", 8: "Fixed", 9: "Mutable",
    10: "Cardinal", 11: "Fixed", 12: "Mutable",
}

JAGRADI_STRENGTH = {
    "Jagrat":   1.00,
    "Swapna":   0.50,
    "Sushupti": 0.25,
}


def get_jagradi_avastha(sign: str) -> str:
    """Return Jagradi Avastha (Jagrat/Swapna/Sushupti) for the given sign."""
    try:
        sign_idx = SIGNS_SK.index(sign) + 1
    except ValueError:
        return "Jagrat"
    modality = MODALITY_BY_SIGN_IDX.get(sign_idx, "Cardinal")
    return JAGRADI_STATE_BY_MODALITY[modality]


def jagradi_strength_multiplier(sign: str) -> float:
    """Return Jagradi strength multiplier [0.25 to 1.0]."""
    avastha = get_jagradi_avastha(sign)
    return JAGRADI_STRENGTH.get(avastha, 1.0)


# ---------------------------------------------------------------------------
# 3. Lajjitadi Avasthas — arising from chart context
# ---------------------------------------------------------------------------

# Lajjitadi Avasthas and their conditions (BPHS Ch. 45-47)
LAJJITADI_DEFS = {
    "Lajjita": {
        "description": "Ashamed — planet in 5th house with Rahu/Ketu/Saturn",
        "effect": "Negative — suppresses 5th house significations (children, intellect, past karma)",
    },
    "Garvita": {
        "description": "Proud — planet in exaltation or Moolatrikona",
        "effect": "Positive — amplifies significations, planet gives very good results",
    },
    "Kshudita": {
        "description": "Hungry — planet associated with enemy or in enemy sign, or aspected by enemy",
        "effect": "Negative — planet struggles, gives mixed or poor results",
    },
    "Trushita": {
        "description": "Thirsty — planet in watery sign aspected by Saturn, or in enemy sign",
        "effect": "Negative — planet is agitated, gives delayed results",
    },
    "Mudita": {
        "description": "Delighted — planet in friend's sign or conjunct/aspected by friend",
        "effect": "Positive — planet gives good results happily and freely",
    },
    "Kopana": {
        "description": "Angry — planet conjunct or aspected by Mars, Rahu, or Ketu",
        "effect": "Negative — planet gives results with struggle and conflict",
    },
}

# Watery signs for Trushita calculation
WATERY_SIGNS = {"Karka", "Vrischika", "Meena"}

# Natural enemies (simplified — see dignity.py for full matrix)
NATURAL_ENEMIES_SIMPLE = {
    "Sun":     {"Venus", "Saturn"},
    "Moon":    {"Mercury"},
    "Mars":    {"Mercury"},
    "Mercury": {"Moon"},
    "Jupiter": {"Mercury", "Venus"},
    "Venus":   {"Sun", "Moon"},
    "Saturn":  {"Sun", "Moon", "Mars"},
}

# Natural friends (simplified)
NATURAL_FRIENDS_SIMPLE = {
    "Sun":     {"Moon", "Mars", "Jupiter"},
    "Moon":    {"Sun", "Mercury"},
    "Mars":    {"Sun", "Moon", "Jupiter"},
    "Mercury": {"Sun", "Venus"},
    "Jupiter": {"Sun", "Moon", "Mars"},
    "Venus":   {"Mercury", "Saturn"},
    "Saturn":  {"Mercury", "Venus"},
}


def get_lajjitadi_avasthas(
    planet: str,
    house: int,
    sign: str,
    degree_in_sign: float,
    planet_map: dict,
    exaltation_signs: dict,
    moolatrikona_signs: dict,
    own_signs: dict,
    enemy_signs: dict,
) -> list[str]:
    """
    Evaluate which Lajjitadi Avasthas a planet is in.

    Parameters
    ----------
    planet           : Planet name.
    house            : House number (1-12).
    sign             : Planet's sign (Sanskrit).
    degree_in_sign   : Degree within sign.
    planet_map       : Full chart {planet_name: {"house": int, "sign": str, ...}}.
    exaltation_signs : {planet: exalt_sign} dict.
    moolatrikona_signs: {planet: mt_sign} dict.
    own_signs        : {planet: [sign1, sign2]} dict.
    enemy_signs      : For dignity.

    Returns
    -------
    List of active Lajjitadi Avastha names.
    """
    active = []

    # Get planets in the same house (conjunctions)
    conjunct_planets = {
        name for name, data in planet_map.items()
        if name != planet and data.get("house") == house
    }

    # Get planets aspecting this house
    aspecting_planets = set()
    for other_name, other_data in planet_map.items():
        if other_name == planet:
            continue
        other_house = other_data.get("house", 0)
        if not other_house:
            continue
        from .shadbala import _get_aspected_houses
        for (asp_house, _) in _get_aspected_houses(other_name, other_house):
            if asp_house == house:
                aspecting_planets.add(other_name)

    # --- Lajjita: 5th house + Rahu/Ketu/Saturn ---
    if house == 5 and conjunct_planets & {"Rahu", "Ketu", "Saturn"}:
        active.append("Lajjita")

    # --- Garvita: Exaltation or Moolatrikona ---
    if sign == exaltation_signs.get(planet) or sign == moolatrikona_signs.get(planet):
        active.append("Garvita")

    # --- Kshudita: Enemy sign or aspected by enemy ---
    planet_enemies = NATURAL_ENEMIES_SIMPLE.get(planet, set())
    if (aspecting_planets | conjunct_planets) & planet_enemies:
        active.append("Kshudita")

    # --- Trushita: Watery sign + Saturn aspect ---
    if sign in WATERY_SIGNS and "Saturn" in aspecting_planets:
        active.append("Trushita")

    # --- Mudita: Friend's sign or friendly planet conjunct/aspect ---
    planet_friends = NATURAL_FRIENDS_SIMPLE.get(planet, set())
    # NOTE: must use any() — 'sign in (generator)' does NOT check list membership in Python 3
    if any(sign in own_signs.get(f, []) for f in planet_friends):
        active.append("Mudita")
    elif (conjunct_planets | aspecting_planets) & planet_friends:
        active.append("Mudita")

    # --- Kopana: Mars, Rahu, or Ketu conjunct or aspecting ---
    if (conjunct_planets | aspecting_planets) & {"Mars", "Rahu", "Ketu"}:
        active.append("Kopana")

    return active


# ---------------------------------------------------------------------------
# Combined evaluation
# ---------------------------------------------------------------------------

def evaluate_avasthas(
    planet: str,
    sign: str,
    house: int,
    degree_in_sign: float,
    planet_map: Optional[dict] = None,
    exaltation_signs: Optional[dict] = None,
    moolatrikona_signs: Optional[dict] = None,
    own_signs: Optional[dict] = None,
    enemy_signs: Optional[dict] = None,
) -> dict:
    """
    Complete Avastha evaluation for a single planet.

    Returns
    -------
    dict with:
      - baladi_avastha: str
      - baladi_multiplier: float
      - jagradi_avastha: str
      - jagradi_multiplier: float
      - lajjitadi_avasthas: list[str]
      - combined_multiplier: float (baladi * jagradi — use to scale planet results)
      - interpretations: dict of active lajjitadi avastha interpretations
    """
    from .strength import EXALTATION as _EX, OWN_SIGNS as _OWN
    from .dignity import MOOLATRIKONA as _MT

    baladi  = get_baladi_avastha(sign, degree_in_sign)
    bal_mul = BALADI_STRENGTH.get(baladi, 0.75)

    jagradi = get_jagradi_avastha(sign)
    jag_mul = JAGRADI_STRENGTH.get(jagradi, 1.0)

    lajjitadi = get_lajjitadi_avasthas(
        planet=planet,
        house=house,
        sign=sign,
        degree_in_sign=degree_in_sign,
        planet_map=planet_map or {},
        exaltation_signs=exaltation_signs or _EX,
        moolatrikona_signs=moolatrikona_signs or _MT,
        own_signs=own_signs or _OWN,
        enemy_signs=enemy_signs or {},
    )

    interpretations = {a: LAJJITADI_DEFS[a] for a in lajjitadi if a in LAJJITADI_DEFS}

    return {
        "baladi_avastha":       baladi,
        "baladi_multiplier":    bal_mul,
        "jagradi_avastha":      jagradi,
        "jagradi_multiplier":   jag_mul,
        "lajjitadi_avasthas":   lajjitadi,
        "combined_multiplier":  round(bal_mul * jag_mul, 4),
        "interpretations":      interpretations,
    }
