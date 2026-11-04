"""
Functional Lordship Matrix — 12-Lagna Ownership and Role Classification.

Source:  Brihat Parasara Hora Shastra (BPHS), Chapter 34.
         Uttara Kalamrita, Phaladeepika.

This module programmatically generates the complete 12-Lagna functional
lordship matrix without manual hardcoding. All role classifications
(Kendra, Trikona, Dusthana, Maraka, Badhaka, Yogakaraka) are derived
from the lagna sign index and classical Parashari rules.

Functional Benefic / Malefic Determination (BPHS rules)
---------------------------------------------------------
- Lords of Trikona houses (1, 5, 9) are always functional benefics.
- Lords of Kendra houses (1, 4, 7, 10):
    - If a Kendra lord is ALSO a Trikona lord -> Yogakaraka (highest benefit).
    - Pure Kendra lords (not Trikona): subject to Kendradhipati Dosha.
      For natural benefics (Jupiter, Venus, Mercury, Moon): become functional
      malefics as pure Kendra lords.
      For natural malefics (Sun, Mars, Saturn): Kendradhipati Dosha is reduced
      or neutralized.
- Lords of Dusthana houses (6, 8, 12): functional malefics (with exceptions
  for Viparita Raja Yoga lords in WP3).
- Lords of Maraka houses (2, 7): neutral-to-malefic (especially 2nd for Moon/
  Sun lagna).
- Rahu and Ketu: act as agents of their sign dispositor; additionally adopt
  functional roles from the houses they occupy/aspect.

Kendradhipati Dosha
-------------------
Natural benefics (Jupiter, Venus, Mercury, Moon as Lagna lord = Karka) that
own only Kendra houses (without also owning a Trikona) suffer Kendradhipati
Dosha and become functional malefics. This is a contested convention in some
traditions; the implementation flags it explicitly.

Badhaka Rules (BPHS Ch. 34)
----------------------------
- Movable (Cardinal) Lagnas: 11th house lord is the Badhaka lord.
- Fixed Lagnas:              9th house lord is the Badhaka lord.
- Dual (Mutable) Lagnas:     7th house lord is the Badhaka lord.

Public API
----------
  get_lagna_matrix(lagna: str) -> LagnaMatrix
  get_house_lord(lagna: str, house: int) -> str
  get_planet_roles(lagna: str, planet: str) -> list[str]
  is_functional_benefic(lagna: str, planet: str) -> bool
  is_functional_malefic(lagna: str, planet: str) -> bool
  is_yogakaraka(lagna: str, planet: str) -> bool
  ALL_LAGNA_MATRICES: dict[str, LagnaMatrix]  (pre-computed at module load)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from .zodiac import SIGNS_SK, SIGN_LORDS

# ---------------------------------------------------------------------------
# Sign modality (for Badhaka calculation)
# ---------------------------------------------------------------------------

SIGN_MODALITY: dict[str, str] = {
    "Mesha":     "Movable",
    "Vrishabha": "Fixed",
    "Mithuna":   "Mutable",
    "Karka":     "Movable",
    "Simha":     "Fixed",
    "Kanya":     "Mutable",
    "Tula":      "Movable",
    "Vrischika": "Fixed",
    "Dhanu":     "Mutable",
    "Makara":    "Movable",
    "Kumbha":    "Fixed",
    "Meena":     "Mutable",
}

BADHAKA_HOUSE: dict[str, int] = {
    "Movable": 11,
    "Fixed":   9,
    "Mutable": 7,
}

# Natural benefics (for Kendradhipati Dosha)
NATURAL_BENEFIC_PLANETS = {"Jupiter", "Venus", "Mercury", "Moon"}
NATURAL_MALEFIC_PLANETS = {"Sun", "Mars", "Saturn", "Rahu", "Ketu"}

# House role classification
KENDRA_HOUSES   = {1, 4, 7, 10}
TRIKONA_HOUSES  = {1, 5, 9}
DUSTHANA_HOUSES = {6, 8, 12}
MARAKA_HOUSES   = {2, 7}
UPACHAYA_HOUSES = {3, 6, 10, 11}


# ---------------------------------------------------------------------------
# Result dataclass
# ---------------------------------------------------------------------------

@dataclass
class PlanetRoleInfo:
    """Functional role information for one planet in one lagna."""
    planet: str
    owned_houses: list[int] = field(default_factory=list)

    # House-type tags for each owned house
    is_kendra_lord: bool = False
    is_trikona_lord: bool = False
    is_dusthana_lord: bool = False
    is_maraka_lord: bool = False
    is_badhaka_lord: bool = False
    is_lagna_lord: bool = False

    # Derived functional status
    is_yogakaraka: bool = False
    is_functional_benefic: bool = False
    is_functional_malefic: bool = False
    is_neutral: bool = False
    has_kendradhipati_dosha: bool = False

    # Role tags as string list (for API serialisation)
    roles: list[str] = field(default_factory=list)


@dataclass
class LagnaMatrix:
    """Complete functional lordship matrix for one lagna sign."""
    lagna: str
    lagna_idx: int

    # House-to-lord mapping: {house_number: planet_name}
    house_lords: dict[int, str] = field(default_factory=dict)

    # Planet-to-role mapping
    planet_roles: dict[str, PlanetRoleInfo] = field(default_factory=dict)

    # Convenience groupings
    yogakarakas: list[str] = field(default_factory=list)
    functional_benefics: list[str] = field(default_factory=list)
    functional_malefics: list[str] = field(default_factory=list)
    badhaka_lord: Optional[str] = None
    badhaka_house: int = 0


# ---------------------------------------------------------------------------
# Core matrix builder
# ---------------------------------------------------------------------------

def _build_house_lords(lagna_idx: int) -> dict[int, str]:
    """Return {house: lord} mapping for all 12 houses from lagna."""
    return {
        house: SIGN_LORDS[SIGNS_SK[(lagna_idx + house - 1) % 12]]
        for house in range(1, 13)
    }


def _collect_owned_houses(house_lords: dict[int, str]) -> dict[str, list[int]]:
    """Invert house_lords to {planet: [house1, house2]}."""
    owned: dict[str, list[int]] = {}
    for house, lord in house_lords.items():
        owned.setdefault(lord, []).append(house)
    return owned


def _determine_roles(
    planet: str,
    owned_houses: list[int],
    badhaka_house: int,
) -> PlanetRoleInfo:
    """Classify a planet's functional roles for a given lagna."""
    info = PlanetRoleInfo(planet=planet, owned_houses=sorted(owned_houses))

    house_set = set(owned_houses)

    info.is_lagna_lord    = 1 in house_set
    info.is_kendra_lord   = bool(house_set & KENDRA_HOUSES)
    info.is_trikona_lord  = bool(house_set & TRIKONA_HOUSES)
    info.is_dusthana_lord = bool(house_set & DUSTHANA_HOUSES)
    info.is_maraka_lord   = bool(house_set & MARAKA_HOUSES)
    info.is_badhaka_lord  = badhaka_house in house_set

    roles = []

    # --- Yogakaraka: own BOTH a non-Lagna Kendra (4,7,10) AND a non-Lagna Trikona (5,9) ---
    # Classical definition (BPHS): a planet that simultaneously owns one of the
    # angular houses (4, 7, or 10) AND one of the trinal houses (5 or 9) is a
    # Yogakaraka. House 1 is common to both categories for every Lagna lord and
    # therefore does NOT independently fulfil either requirement.
    # Example correct: Vrishabha/Saturn (owns 9+10), Karka/Mars (owns 5+10).
    # Example incorrect if not fixed: Mithuna/Mercury (owns 1+4 — Trikona only via H1).
    kendra_owned  = house_set & KENDRA_HOUSES        # {1, 4, 7, 10} intersection
    trikona_owned = house_set & TRIKONA_HOUSES       # {1, 5, 9} intersection
    non_lagna_kendra  = kendra_owned - {1}           # {4, 7, 10} only
    non_lagna_trikona = trikona_owned - {1}          # {5, 9} only
    info.is_yogakaraka = bool(non_lagna_kendra and non_lagna_trikona)
    if info.is_yogakaraka:
        roles.append("Yogakaraka")


    # --- Lagna lord: always functionally beneficial ---
    if info.is_lagna_lord:
        roles.append("Lagna Lord")

    # --- Trikona lord (5, 9): strong functional benefic ---
    if non_lagna_trikona:
        roles.append("Trikona Lord")

    # --- Kendra lord only (not Trikona): Kendradhipati Dosha for benefics ---
    pure_kendra = bool(kendra_owned - {1}) and not info.is_trikona_lord
    if pure_kendra and not info.is_lagna_lord:
        if planet in NATURAL_BENEFIC_PLANETS:
            info.has_kendradhipati_dosha = True
            roles.append("Kendra Lord (Kendradhipati Dosha)")
        else:
            roles.append("Kendra Lord")

    # --- Dusthana lord ---
    if info.is_dusthana_lord:
        dusthanas = sorted(house_set & DUSTHANA_HOUSES)
        roles.append(f"Dusthana Lord ({', '.join(str(h) for h in dusthanas)})")

    # --- Maraka lord ---
    if info.is_maraka_lord:
        marakas = sorted(house_set & MARAKA_HOUSES)
        roles.append(f"Maraka Lord ({', '.join(str(h) for h in marakas)})")

    # --- Badhaka lord ---
    if info.is_badhaka_lord:
        roles.append(f"Badhaka Lord ({badhaka_house}H)")

    info.roles = roles

    # --- Functional benefic/malefic determination ---
    # BPHS rule: Lagna lord is ALWAYS a functional benefic regardless of other house
    # ownership. Even if it also owns a dusthana (e.g. Mesha/Mars owns 1+8), the
    # Lagna lord status overrides. Yogakaraka is the highest benefic tier.
    if info.is_yogakaraka:
        info.is_functional_benefic = True
    elif info.is_lagna_lord:
        # Lagna lord unconditionally functional benefic (BPHS absolute rule)
        info.is_functional_benefic = True
    elif info.is_trikona_lord and not info.is_dusthana_lord:
        info.is_functional_benefic = True
    elif info.has_kendradhipati_dosha and not info.is_trikona_lord:
        info.is_functional_malefic = True
    elif info.is_dusthana_lord and not info.is_trikona_lord:
        info.is_functional_malefic = True
    else:
        info.is_neutral = True

    return info


def build_lagna_matrix(lagna: str) -> LagnaMatrix:
    """
    Build the complete functional lordship matrix for a given lagna sign.

    Parameters
    ----------
    lagna : Sanskrit sign name (e.g. "Mesha", "Vrishabha", ...).

    Returns
    -------
    LagnaMatrix with all planet roles, yogakarakas, benefics, malefics.
    """
    if lagna not in SIGNS_SK:
        raise ValueError(f"Unknown lagna: '{lagna}'. Must be one of {SIGNS_SK}.")

    lagna_idx = SIGNS_SK.index(lagna)
    house_lords = _build_house_lords(lagna_idx)
    owned_by    = _collect_owned_houses(house_lords)

    # Determine badhaka house from lagna modality
    modality   = SIGN_MODALITY[lagna]
    bh_number  = BADHAKA_HOUSE[modality]
    bh_lord    = house_lords[bh_number]

    matrix = LagnaMatrix(
        lagna=lagna,
        lagna_idx=lagna_idx,
        house_lords=house_lords,
        badhaka_house=bh_number,
        badhaka_lord=bh_lord,
    )

    for planet, houses in owned_by.items():
        role_info = _determine_roles(planet, houses, bh_number)
        matrix.planet_roles[planet] = role_info

        if role_info.is_yogakaraka:
            matrix.yogakarakas.append(planet)
        if role_info.is_functional_benefic:
            matrix.functional_benefics.append(planet)
        if role_info.is_functional_malefic:
            matrix.functional_malefics.append(planet)

    return matrix


# ---------------------------------------------------------------------------
# Pre-compute all 12 matrices at module load (deterministic, zero side-effects)
# ---------------------------------------------------------------------------

ALL_LAGNA_MATRICES: dict[str, LagnaMatrix] = {
    sign: build_lagna_matrix(sign)
    for sign in SIGNS_SK
}


# ---------------------------------------------------------------------------
# Public convenience functions
# ---------------------------------------------------------------------------

def get_lagna_matrix(lagna: str) -> LagnaMatrix:
    """Return the pre-computed LagnaMatrix for the given lagna sign."""
    if lagna not in ALL_LAGNA_MATRICES:
        raise ValueError(f"Unknown lagna: '{lagna}'.")
    return ALL_LAGNA_MATRICES[lagna]


def get_house_lord(lagna: str, house: int) -> str:
    """Return the planet that rules the given house for a lagna."""
    matrix = get_lagna_matrix(lagna)
    return matrix.house_lords.get(house, "Unknown")


def get_planet_roles(lagna: str, planet: str) -> list[str]:
    """Return the functional role tags for a planet in a given lagna."""
    matrix = get_lagna_matrix(lagna)
    role_info = matrix.planet_roles.get(planet)
    return role_info.roles if role_info else []


def is_functional_benefic(lagna: str, planet: str) -> bool:
    """True if the planet is a functional benefic for the given lagna."""
    matrix = get_lagna_matrix(lagna)
    role = matrix.planet_roles.get(planet)
    return role.is_functional_benefic if role else False


def is_functional_malefic(lagna: str, planet: str) -> bool:
    """True if the planet is a functional malefic for the given lagna."""
    matrix = get_lagna_matrix(lagna)
    role = matrix.planet_roles.get(planet)
    return role.is_functional_malefic if role else False


def is_yogakaraka(lagna: str, planet: str) -> bool:
    """True if the planet is a Yogakaraka for the given lagna."""
    matrix = get_lagna_matrix(lagna)
    return planet in matrix.yogakarakas


def is_badhaka_lord(lagna: str, planet: str) -> bool:
    """True if the planet is the Badhaka lord for the given lagna."""
    matrix = get_lagna_matrix(lagna)
    return matrix.badhaka_lord == planet


def matrix_to_dict(lagna: str) -> dict:
    """Serialise the LagnaMatrix to a plain dict for API responses."""
    m = get_lagna_matrix(lagna)
    return {
        "lagna": m.lagna,
        "house_lords": {str(k): v for k, v in m.house_lords.items()},
        "yogakarakas": m.yogakarakas,
        "functional_benefics": m.functional_benefics,
        "functional_malefics": m.functional_malefics,
        "badhaka_lord": m.badhaka_lord,
        "badhaka_house": m.badhaka_house,
        "planet_roles": {
            p: {
                "owned_houses": r.owned_houses,
                "roles": r.roles,
                "is_functional_benefic": r.is_functional_benefic,
                "is_functional_malefic": r.is_functional_malefic,
                "is_yogakaraka": r.is_yogakaraka,
                "has_kendradhipati_dosha": r.has_kendradhipati_dosha,
            }
            for p, r in m.planet_roles.items()
        },
    }
