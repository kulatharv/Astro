"""
Bhava Bala — House Strength Computation Engine.

Source:  Brihat Parasara Hora Shastra (BPHS), Chapter 28.
         Phaladeepika Ch. 22.

Bhava Bala has three primary components:
  1. Bhavadhipati Bala  — Strength contributed by the house lord.
  2. Bhava Digbala      — Directional strength of the house itself.
  3. Bhava Drik Bala    — Aspectual strength received by the house cusp/midpoint.

Units: Virupas (1 Rupa = 60 Virupas).

Public API
----------
  bhava_bala(house, lagna_idx, planet_map, shadbala_results) -> BhavaBalaResult
  bhava_bala_summary(lagna_idx, planet_map, shadbala_results) -> dict
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from .zodiac import SIGNS_SK, SIGN_LORDS
from .shadbala import ShadbalaResult, NATURAL_BENEFICS, _get_aspected_houses

# ---------------------------------------------------------------------------
# Bhava Dig Bala — house directional strength
# ---------------------------------------------------------------------------

# Houses with inherent directional strength (maximum = 60 Virupas)
BHAVA_DIG_BALA_MAX: dict[int, float] = {
    1:  60.0,   # Lagna — strongest Kendra
    4:  45.0,
    7:  45.0,
    10: 60.0,   # Midheaven — strongest upachaya
    2:  30.0,
    5:  30.0,
    9:  30.0,
    11: 30.0,
    3:  15.0,
    6:  15.0,
    8:  15.0,
    12: 15.0,
}


# ---------------------------------------------------------------------------
# Result dataclass
# ---------------------------------------------------------------------------

@dataclass
class BhavaBalaResult:
    """Bhava Bala breakdown for a single house."""
    house: int
    sign: str

    bhavadhipati_bala: float = 0.0    # Lord's Shadbala contribution
    bhava_digbala: float = 0.0        # House directional strength
    bhava_drik_bala: float = 0.0      # Aspectual strength on house cusp

    total_virupas: float = 0.0
    total_rupas: float = 0.0

    # BPHS minimum: ~5.5 Rupas for a strong house
    is_strong: bool = False

    breakdown: dict = field(default_factory=dict)


MINIMUM_BHAVA_RUPAS = 5.5


# ---------------------------------------------------------------------------
# 1. Bhavadhipati Bala
# ---------------------------------------------------------------------------

def _bhavadhipati_bala(
    house: int,
    lagna_idx: int,
    shadbala_results: dict[str, ShadbalaResult],
) -> float:
    """
    Bhavadhipati Bala — contribution from the house lord's total Shadbala.
    The lord's total Virupas are scaled to a max of 60 Virupas for the house.
    """
    sign = SIGNS_SK[(lagna_idx + house - 1) % 12]
    lord = SIGN_LORDS.get(sign)
    if not lord or lord not in shadbala_results:
        return 30.0  # Default neutral if lord's Shadbala not available

    lord_total = shadbala_results[lord].total_virupas
    # Scale: assume a nominal "strong" total of ~300 Virupas -> map to 60
    scaled = min(60.0, lord_total / 5.0)
    return round(scaled, 2)


# ---------------------------------------------------------------------------
# 2. Bhava Dig Bala
# ---------------------------------------------------------------------------

def _bhava_digbala(house: int) -> float:
    """Return house directional strength in Virupas."""
    return BHAVA_DIG_BALA_MAX.get(house, 15.0)


# ---------------------------------------------------------------------------
# 3. Bhava Drik Bala (aspectual strength received by the house)
# ---------------------------------------------------------------------------

def _bhava_drik_bala(house: int, planet_map: dict) -> float:
    """
    Bhava Drik Bala — aggregate aspect strength received by a house.
    Benefic aspects add; Malefic aspects subtract.
    """
    score = 0.0
    for planet_name, planet_data in planet_map.items():
        from_house = planet_data.get("house", 0)
        if not from_house:
            continue
        for (asp_house, asp_strength) in _get_aspected_houses(planet_name, from_house):
            if asp_house == house:
                if planet_name in NATURAL_BENEFICS:
                    score += 30.0 * asp_strength
                else:
                    score -= 30.0 * asp_strength

    return round(max(-60.0, min(60.0, score)), 2)


# ---------------------------------------------------------------------------
# Main public API
# ---------------------------------------------------------------------------

def bhava_bala(
    house: int,
    lagna_idx: int,
    planet_map: dict,
    shadbala_results: Optional[dict[str, ShadbalaResult]] = None,
) -> BhavaBalaResult:
    """
    Compute Bhava Bala for a single house.

    Parameters
    ----------
    house            : House number 1-12.
    lagna_idx        : Lagna sign index (0=Mesha, 11=Meena).
    planet_map       : Chart planet positions {planet: {"house": int, ...}}.
    shadbala_results : Precomputed Shadbala results dict; if None, Bhavadhipati
                       Bala defaults to neutral.

    Returns
    -------
    BhavaBalaResult with component breakdown.
    """
    sign = SIGNS_SK[(lagna_idx + house - 1) % 12]
    result = BhavaBalaResult(house=house, sign=sign)

    result.bhavadhipati_bala = _bhavadhipati_bala(
        house, lagna_idx, shadbala_results or {}
    )
    result.bhava_digbala  = _bhava_digbala(house)
    result.bhava_drik_bala = _bhava_drik_bala(house, planet_map)

    result.total_virupas = round(
        result.bhavadhipati_bala + result.bhava_digbala + result.bhava_drik_bala,
        2,
    )
    result.total_rupas = round(result.total_virupas / 60.0, 4)
    result.is_strong   = result.total_rupas >= MINIMUM_BHAVA_RUPAS

    result.breakdown = {
        "house": house,
        "sign": sign,
        "bhavadhipati_bala": result.bhavadhipati_bala,
        "bhava_digbala": result.bhava_digbala,
        "bhava_drik_bala": result.bhava_drik_bala,
        "total_virupas": result.total_virupas,
        "total_rupas": result.total_rupas,
        "minimum_required_rupas": MINIMUM_BHAVA_RUPAS,
        "is_strong": result.is_strong,
    }

    return result


def bhava_bala_summary(
    lagna_idx: int,
    planet_map: dict,
    shadbala_results: Optional[dict[str, ShadbalaResult]] = None,
) -> dict[int, BhavaBalaResult]:
    """
    Compute Bhava Bala for all 12 houses.

    Returns
    -------
    dict mapping house_number (1-12) -> BhavaBalaResult.
    """
    return {
        house: bhava_bala(house, lagna_idx, planet_map, shadbala_results)
        for house in range(1, 13)
    }
