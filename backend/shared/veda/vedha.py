"""
Classical Gochara Vedha (Transit Obstruction) Engine (Phaladeepika Ch. 26).

Implements:
  1. Benefic transit house rules from Janma Rashi (natal Moon).
  2. Exact classical Vedha obstruction pairs.
  3. Canonical exemptions:
     - Sun and Saturn (father-son) do not cause Vedha to each other.
     - Moon and Mercury (mother-son) do not cause Vedha to each other.
  4. Deterministic obstruction status calculation for transiting planets.
"""

from __future__ import annotations
from typing import Dict, Any, List, Optional

# ---------------------------------------------------------------------------
# Classical Vedha Mapping Table: Benefic House -> Obstructing House
# ---------------------------------------------------------------------------

GOCHARA_BENEFIC_HOUSES: Dict[str, List[int]] = {
    "Sun": [3, 6, 10, 11],
    "Moon": [1, 3, 6, 7, 10, 11],
    "Mars": [3, 6, 11],
    "Mercury": [2, 4, 6, 8, 10, 11],
    "Jupiter": [2, 5, 7, 9, 11],
    "Venus": [1, 2, 3, 4, 5, 8, 9, 11, 12],
    "Saturn": [3, 6, 11],
    "Rahu": [3, 6, 10, 11],
    "Ketu": [3, 6, 11],
}

VEDHA_PAIRS: Dict[str, Dict[int, int]] = {
    "Sun": {3: 9, 6: 12, 10: 4, 11: 5},
    "Moon": {1: 5, 3: 9, 6: 12, 7: 2, 10: 4, 11: 8},
    "Mars": {3: 12, 6: 9, 11: 5},
    "Mercury": {2: 5, 4: 3, 6: 9, 8: 1, 10: 8, 11: 12},
    "Jupiter": {2: 12, 5: 4, 7: 3, 9: 10, 11: 8},
    "Venus": {1: 8, 2: 7, 3: 1, 4: 10, 5: 9, 8: 5, 9: 11, 11: 6, 12: 3},
    "Saturn": {3: 12, 6: 9, 11: 5},
    "Rahu": {3: 12, 6: 9, 10: 4, 11: 5},
    "Ketu": {3: 12, 6: 9, 11: 5},
}

# Pairs exempt from causing Vedha to each other
VEDHA_EXEMPT_PAIRS = {
    ("Sun", "Saturn"),
    ("Saturn", "Sun"),
    ("Moon", "Mercury"),
    ("Mercury", "Moon"),
}


def check_transit_vedha(
    planet: str,
    house_from_moon: int,
    transit_positions_from_moon: Dict[str, int],
) -> Dict[str, Any]:
    """
    Check if a transiting planet's benefic position is obstructed by another transiting planet.
    
    Parameters:
        planet: Transiting planet being evaluated
        house_from_moon: House position from natal Moon (1 to 12)
        transit_positions_from_moon: Dict mapping planet names to their house position from natal Moon

    Returns:
        Dict detailing is_benefic, is_obstructed, obstructing_planets, and explanation.
    """
    benefic_houses = GOCHARA_BENEFIC_HOUSES.get(planet, [])
    is_benefic = house_from_moon in benefic_houses

    if not is_benefic:
        return {
            "planet": planet,
            "house_from_moon": house_from_moon,
            "is_benefic": False,
            "is_obstructed": False,
            "obstructing_planets": [],
            "status": "NON_BENEFIC_HOUSE",
            "description": f"{planet} in house {house_from_moon} from Moon is not in an intrinsically benefic transit house.",
        }

    vedha_map = VEDHA_PAIRS.get(planet, {})
    vedha_target_house = vedha_map.get(house_from_moon)

    if vedha_target_house is None:
        return {
            "planet": planet,
            "house_from_moon": house_from_moon,
            "is_benefic": True,
            "is_obstructed": False,
            "obstructing_planets": [],
            "status": "UNOBSTRUCTED_BENEFIC",
            "description": f"{planet} in house {house_from_moon} from Moon operates with unobstructed benefic Gochara influence.",
        }

    # Check which planets occupy the vedha_target_house
    obstructors = []
    for p, h in transit_positions_from_moon.items():
        if p == planet:
            continue
        if h == vedha_target_house:
            # Check classical exemption
            if (planet, p) in VEDHA_EXEMPT_PAIRS:
                continue
            obstructors.append(p)

    if obstructors:
        return {
            "planet": planet,
            "house_from_moon": house_from_moon,
            "is_benefic": True,
            "is_obstructed": True,
            "vedha_house": vedha_target_house,
            "obstructing_planets": obstructors,
            "status": "OBSTRUCTED_BY_VEDHA",
            "description": f"{planet}'s benefic transit in house {house_from_moon} is obstructed (Vedha) by {', '.join(obstructors)} in house {vedha_target_house}.",
        }

    return {
        "planet": planet,
        "house_from_moon": house_from_moon,
        "is_benefic": True,
        "is_obstructed": False,
        "vedha_house": vedha_target_house,
        "obstructing_planets": [],
        "status": "UNOBSTRUCTED_BENEFIC",
        "description": f"{planet} in house {house_from_moon} from Moon is free from Vedha obstruction (Vedha point H{vedha_target_house} is vacant).",
    }
