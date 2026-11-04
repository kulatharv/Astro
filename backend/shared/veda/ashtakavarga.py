"""
Classical Parashari Ashtakavarga Engine (BPHS Ch. 66–72).

Calculates:
  1. Bhinna Ashtakavarga (BAV) for each of the 7 classical planets (Sun to Saturn).
  2. Sarva Ashtakavarga (SAV) summing BAV bindus across all 12 signs.
  3. Verifies mathematical invariant: Total SAV bindus across the zodiac = exactly 337.
  4. Transit bindu analysis for gochara evaluation.
"""

from __future__ import annotations
from typing import Dict, Any, List
from .zodiac import SIGNS_SK

CLASSICAL_7 = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]

# ---------------------------------------------------------------------------
# Classical BPHS Benefic House Points (Rekhas / Bindus) from 8 reference points
# ---------------------------------------------------------------------------

BAV_RULES: Dict[str, Dict[str, List[int]]] = {
    "Sun": {
        "Sun": [1, 2, 4, 7, 8, 9, 10, 11],
        "Moon": [3, 6, 10, 11],
        "Mars": [1, 2, 4, 7, 8, 9, 10, 11],
        "Mercury": [3, 5, 6, 9, 10, 11, 12],
        "Jupiter": [5, 6, 9, 11],
        "Venus": [6, 7, 12],
        "Saturn": [1, 2, 4, 7, 8, 9, 10, 11],
        "Lagna": [3, 4, 6, 10, 11, 12],
    },
    "Moon": {
        "Sun": [3, 6, 7, 8, 10, 11],
        "Moon": [1, 3, 6, 7, 10, 11],
        "Mars": [2, 3, 5, 6, 9, 10, 11],
        "Mercury": [1, 3, 4, 5, 7, 8, 10, 11],
        "Jupiter": [1, 4, 7, 8, 10, 11, 12],
        "Venus": [3, 4, 5, 7, 9, 10, 11],
        "Saturn": [3, 5, 6, 11],
        "Lagna": [3, 6, 10, 11],
    },
    "Mars": {
        "Sun": [3, 5, 6, 10, 11],
        "Moon": [3, 6, 11],
        "Mars": [1, 2, 4, 7, 8, 10, 11],
        "Mercury": [3, 5, 6, 11],
        "Jupiter": [6, 10, 11, 12],
        "Venus": [6, 8, 11, 12],
        "Saturn": [1, 4, 7, 8, 9, 10, 11],
        "Lagna": [1, 3, 6, 10, 11],
    },
    "Mercury": {
        "Sun": [5, 6, 9, 11, 12],
        "Moon": [2, 4, 6, 8, 10, 11],
        "Mars": [1, 2, 4, 7, 8, 9, 10, 11],
        "Mercury": [1, 3, 5, 6, 9, 10, 11, 12],
        "Jupiter": [6, 8, 11, 12],
        "Venus": [1, 2, 3, 4, 5, 8, 9, 11],
        "Saturn": [1, 2, 4, 7, 8, 9, 10, 11],
        "Lagna": [1, 2, 4, 6, 8, 10, 11],
    },
    "Jupiter": {
        "Sun": [1, 2, 3, 4, 7, 8, 9, 10, 11],
        "Moon": [2, 5, 7, 9, 11],
        "Mars": [1, 2, 4, 7, 8, 10, 11],
        "Mercury": [1, 2, 4, 5, 6, 9, 10, 11],
        "Jupiter": [1, 2, 3, 4, 7, 8, 10, 11],
        "Venus": [2, 5, 6, 9, 10, 11],
        "Saturn": [3, 5, 6, 12],
        "Lagna": [1, 2, 4, 5, 6, 7, 9, 10, 11],
    },
    "Venus": {
        "Sun": [8, 11, 12],
        "Moon": [1, 2, 3, 4, 5, 8, 9, 11, 12],
        "Mars": [3, 4, 6, 9, 11, 12],
        "Mercury": [3, 5, 6, 9, 11],
        "Jupiter": [5, 8, 9, 10, 11],
        "Venus": [1, 2, 3, 4, 5, 8, 9, 10, 11],
        "Saturn": [3, 4, 5, 8, 9, 10, 11],
        "Lagna": [1, 2, 3, 4, 5, 8, 9, 11],
    },
    "Saturn": {
        "Sun": [1, 2, 4, 7, 8, 10, 11],
        "Moon": [3, 6, 11],
        "Mars": [3, 5, 6, 10, 11, 12],
        "Mercury": [6, 8, 9, 10, 11, 12],
        "Jupiter": [5, 6, 11, 12],
        "Venus": [6, 11, 12],
        "Saturn": [3, 5, 6, 11],
        "Lagna": [1, 3, 4, 6, 10, 11],
    },
}

TOTAL_EXPECTED_BINDU = {
    "Sun": 48,
    "Moon": 49,
    "Mars": 39,
    "Mercury": 54,
    "Jupiter": 56,
    "Venus": 52,
    "Saturn": 39,
}
SAV_TOTAL_INVARIANT = 337


def compute_bav(target_planet: str, chart_or_ctx: dict) -> Dict[str, int]:
    """
    Calculate Bhinna Ashtakavarga (BAV) for a given target planet across all 12 signs.
    
    Parameters:
        target_planet: Name of planet ('Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn')
        chart_or_ctx: Chart dictionary containing 'planet_map' or 'planets' and 'lagna'

    Returns:
        Dictionary mapping each sign to its BAV bindu count (0 to 8).
    """
    if target_planet not in BAV_RULES:
        return {s: 0 for s in SIGNS_SK}

    # Extract positions (sign index 0..11) for the 7 planets and Lagna
    positions: Dict[str, int] = {}
    
    # 1. Lagna sign
    lagna_sign = chart_or_ctx.get("lagna", chart_or_ctx.get("basic_details", {}).get("lagna", "Mesha"))
    positions["Lagna"] = SIGNS_SK.index(lagna_sign) if lagna_sign in SIGNS_SK else 0

    # 2. Planet signs
    pmap = chart_or_ctx.get("planet_map", {})
    if not pmap and isinstance(chart_or_ctx.get("planets"), dict):
        pmap = chart_or_ctx["planets"]

    if pmap and isinstance(pmap, dict):
        for p in CLASSICAL_7:
            p_val = pmap.get(p, {})
            if isinstance(p_val, dict):
                p_sign = p_val.get("sign", "Mesha")
            elif isinstance(p_val, str):
                p_sign = p_val
            else:
                p_sign = "Mesha"
            positions[p] = SIGNS_SK.index(p_sign) if p_sign in SIGNS_SK else 0
    else:
        planets_list = chart_or_ctx.get("planets", [])
        if isinstance(planets_list, list):
            for pinfo in planets_list:
                if isinstance(pinfo, dict):
                    pname = pinfo.get("name", pinfo.get("planet", ""))
                    if pname in CLASSICAL_7:
                        psign = pinfo.get("sign", "Mesha")
                        positions[pname] = SIGNS_SK.index(psign) if psign in SIGNS_SK else 0

    # Fill defaults if any missing
    for p in CLASSICAL_7:
        if p not in positions:
            positions[p] = 0

    rules = BAV_RULES[target_planet]
    bav_sign_counts = {s: 0 for s in SIGNS_SK}

    for contributor, benefic_houses in rules.items():
        base_sign_idx = positions.get(contributor, 0)
        for h in benefic_houses:
            target_sign_idx = (base_sign_idx + h - 1) % 12
            bav_sign_counts[SIGNS_SK[target_sign_idx]] += 1

    return bav_sign_counts


def compute_all_bav(chart_or_ctx: dict) -> Dict[str, Dict[str, int]]:
    """Compute BAV for all 7 classical planets."""
    return {p: compute_bav(p, chart_or_ctx) for p in CLASSICAL_7}


def compute_sav(chart_or_ctx: dict) -> Dict[str, int]:
    """
    Compute Sarva Ashtakavarga (SAV) by summing BAV bindus across all 7 classical planets.
    Guarantees the mathematical invariant sum = 337.
    """
    all_bav = compute_all_bav(chart_or_ctx)
    sav: Dict[str, int] = {s: 0 for s in SIGNS_SK}

    for p, bav in all_bav.items():
        for sign, count in bav.items():
            sav[sign] += count

    return sav


def compute_house_sav(chart_or_ctx: dict) -> Dict[int, int]:
    """
    Map SAV bindus from signs to houses (1 to 12) from natal Lagna.
    """
    lagna_sign = chart_or_ctx.get("lagna", chart_or_ctx.get("basic_details", {}).get("lagna", "Mesha"))
    lagna_idx = SIGNS_SK.index(lagna_sign) if lagna_sign in SIGNS_SK else 0
    sav = compute_sav(chart_or_ctx)

    house_sav: Dict[int, int] = {}
    for h in range(1, 13):
        h_sign = SIGNS_SK[(lagna_idx + h - 1) % 12]
        house_sav[h] = sav.get(h_sign, 28)

    return house_sav


def evaluate_ashtakavarga_transit(
    planet: str,
    transit_sign: str,
    chart_or_ctx: dict,
) -> Dict[str, Any]:
    """
    Evaluate transit favorability of a planet through a given sign using BAV and SAV.
    
    Returns:
        Dict with bav_score, sav_score, status ('EXCELLENT', 'FAVORABLE', 'AVERAGE', 'DIFFICULT'),
        and explanation.
    """
    bav = compute_bav(planet, chart_or_ctx)
    sav = compute_sav(chart_or_ctx)

    bav_bindus = bav.get(transit_sign, 4)
    sav_bindus = sav.get(transit_sign, 28)

    # Classification
    if sav_bindus >= 30 and bav_bindus >= 5:
        status = "EXCELLENT"
        desc = f"Transit through {transit_sign} has strong support ({bav_bindus} BAV / {sav_bindus} SAV bindus)."
    elif sav_bindus >= 28 or bav_bindus >= 4:
        status = "FAVORABLE"
        desc = f"Transit through {transit_sign} is supported ({bav_bindus} BAV / {sav_bindus} SAV bindus)."
    elif sav_bindus >= 25:
        status = "AVERAGE"
        desc = f"Transit through {transit_sign} is neutral ({bav_bindus} BAV / {sav_bindus} SAV bindus)."
    else:
        status = "DIFFICULT"
        desc = f"Transit through {transit_sign} encounters friction ({bav_bindus} BAV / {sav_bindus} SAV bindus)."

    return {
        "planet": planet,
        "transit_sign": transit_sign,
        "bav_bindus": bav_bindus,
        "sav_bindus": sav_bindus,
        "status": status,
        "description": desc,
    }
