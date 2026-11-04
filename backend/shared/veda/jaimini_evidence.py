"""
Jaimini Astrology Evidence Primitives (shared.veda.jaimini_evidence).

Governing Standards:
- Master Specification v3.0 §10, §9.9, §13.2, §15, Appendix C
- WP0 Traceability Matrix v1.1 TR-051, TR-052, TR-053, TR-054
- ASTROLOGIC_WP7_DESIGN_DECISION_REGISTER.md (DEC-JAI-07, DEC-JAI-08)
- ASTROLOGIC_WP7_RULE_CATALOG_DRAFT.md (Rule JAI-ASP-02, Rule JAI-KAR-01)

This module provides pure, stateless mathematical calculations for:
1. Karakamsa framing under NAVAMSHA_IN_RASHI and KARAKAMSA_KUNDALI_D9.
2. Jaimini Argala and Virodhargala (intervention and obstruction) evaluation (Rule JAI-ASP-02).
3. Primary pairs (4 vs 10, 2 vs 12, 11 vs 3) and secondary pair (5 vs 9).
4. Configurable Ketu forward vs reverse Argala direction (DEC-JAI-08).
5. Zero side-effects, zero DB, zero Redis.
"""

from __future__ import annotations

import math
from enum import Enum
from typing import Any, Optional

from .jaimini_rules import (
    KarakaSchemeEnum,
    TieBreakerEnum,
    SIGN_NAMES_SK,
    SIGN_NAMES_EN,
    parse_sign_index,
    validate_finite_degree,
    calculate_chara_karakas,
)


# ==============================================================================
# 1. Enums and Conventions (DEC-JAI-07, DEC-JAI-08)
# ==============================================================================

class KarakamsaFramingMode(str, Enum):
    """
    Karakamsa framing options (DEC-JAI-07).
    
    NAVAMSHA_IN_RASHI:
        The Navamsha sign of Atmakaraka (S_nav) is projected onto the D1 Rashi chart.
        Houses 1..12 are counted from S_nav using D1 planet placements and aspects.
        
    KARAKAMSA_KUNDALI_D9:
        S_nav is treated as the Lagna of the D9 Navamsha chart itself.
        Houses 1..12 are counted from S_nav using D9 planet placements.
    """
    NAVAMSHA_IN_RASHI = "NAVAMSHA_IN_RASHI"
    KARAKAMSA_KUNDALI_D9 = "KARAKAMSA_KUNDALI_D9"


class KetuArgalaConvention(str, Enum):
    """
    Ketu Argala and Virodhargala direction convention (DEC-JAI-08).
    
    STANDARD_ARGALA:
        Ketu evaluates Argala in the standard direct forward order along with all other planets.
        Positions: Argala in 2, 4, 11, 5; Obstructions in 12, 10, 3, 9.
        
    REVERSE_KETU_ARGALA:
        Ketu evaluates Argala in reverse order due to nodal retrograde nature.
        Positions for Ketu: Argala in 12, 10, 3, 9; Obstructions in 2, 4, 11, 5.
    """
    STANDARD_ARGALA = "STANDARD_ARGALA"
    REVERSE_KETU_ARGALA = "REVERSE_KETU_ARGALA"


# ==============================================================================
# 2. Astrological Constants for Evidence & Aspects
# ==============================================================================

# Classical Argala - Virodhargala pairs: (Argala house offset, Obstruction house offset)
ARGALA_PAIRS: list[tuple[int, int]] = [
    (4, 10),   # 4th house Argala obstructed by 10th house
    (2, 12),   # 2nd house Argala obstructed by 12th house
    (11, 3),   # 11th house Argala obstructed by 3rd house
    (5, 9),    # 5th house secondary Argala obstructed by 9th house
]

# Natural Benefics and Malefics in Vedic Astrology
NATURAL_BENEFICS: set[str] = {"Jupiter", "Venus", "Moon", "Mercury"}
NATURAL_MALEFICS: set[str] = {"Sun", "Mars", "Saturn", "Rahu", "Ketu"}

# Navamsha Pada span in arcdegrees: 30° / 9 = 3°20' = 3.3333333333333335°
PADA_SPAN_DEG: float = 30.0 / 9.0

# Starting signs for Navamsha calculation:
# Movable signs (1, 4, 7, 10): start from sign itself
# Fixed signs (2, 5, 8, 11): start from 9th from sign ((S - 1 + 8) % 12) + 1
# Dual signs (3, 6, 9, 12): start from 5th from sign ((S - 1 + 4) % 12) + 1
def get_navamsha_start_sign(sign_index: int) -> int:
    """Determine the starting sign of the first Navamsha for a given sign (1..12)."""
    s = parse_sign_index(sign_index)
    if s in {1, 4, 7, 10}:
        return s
    elif s in {2, 5, 8, 11}:
        return ((s - 1 + 8) % 12) + 1
    else:  # 3, 6, 9, 12
        return ((s - 1 + 4) % 12) + 1


def calculate_navamsha_sign(sign_index: int, degree_in_sign: float) -> int:
    """
    Calculate the 1-indexed Navamsha (D9) sign number for a given sign and degree within sign.
    
    Args:
        sign_index: 1-indexed Rashi sign (1..12).
        degree_in_sign: Degree within sign [0.0, 30.0).
        
    Returns:
        1-indexed Navamsha sign number (1..12).
    """
    s = parse_sign_index(sign_index)
    deg = validate_finite_degree(degree_in_sign) % 30.0
    pada_idx = int(deg / PADA_SPAN_DEG)
    pada_idx = max(0, min(8, pada_idx))
    start_s = get_navamsha_start_sign(s)
    return ((start_s - 1 + pada_idx) % 12) + 1


# ==============================================================================
# 3. Karakamsa Framing Engine (DEC-JAI-07)
# ==============================================================================

def evaluate_karakamsa(
    planet_positions: dict[str, Any] | list[dict[str, Any]],
    lagna_sign: int | str,
    karaka_scheme: KarakaSchemeEnum = KarakaSchemeEnum.SEVEN_KARAKA,
    framing_mode: KarakamsaFramingMode = KarakamsaFramingMode.NAVAMSHA_IN_RASHI,
    d9_sign_placements: Optional[dict[str, int | str]] = None,
) -> dict[str, Any]:
    """
    Evaluate Karakamsa framing deterministically.
    
    Algorithm:
    1. Determine Atmakaraka (AK) using calculate_chara_karakas() under karaka_scheme.
    2. Derive Navamsha sign of AK (S_nav):
       - If d9_sign_placements is provided for AK planet, use it directly.
       - Otherwise compute S_nav from AK's D1 sign and degree_in_sign using calculate_navamsha_sign().
    3. Construct the 12 houses from Karakamsa:
       - If framing_mode == NAVAMSHA_IN_RASHI:
         Reference chart is D1.
         House 1 is S_nav.
         House h is ((S_nav - 1 + h - 1) % 12) + 1.
         Occupants are planets occupying that sign in D1.
       - If framing_mode == KARAKAMSA_KUNDALI_D9:
         Reference chart is D9.
         House 1 is S_nav.
         House h is ((S_nav - 1 + h - 1) % 12) + 1.
         Occupants are planets occupying that sign in D9.
         
    Returns:
        Structured dictionary with Karakamsa metadata, signs, and occupants by house.
    """
    lagna_idx = parse_sign_index(lagna_sign)

    # 1. Compute Chara Karakas to obtain AK
    karaka_res = calculate_chara_karakas(
        planets=planet_positions,
        scheme=karaka_scheme,
    )
    if "AK" not in karaka_res["karakas"]:
        raise ValueError("Could not determine Atmakaraka (AK) from planetary positions.")

    ak_info = karaka_res["karakas"]["AK"]
    ak_planet = ak_info["planet"]
    ak_d1_sign = ak_info["sign_index"]
    ak_deg_in_sign = ak_info["degree_in_sign"]

    # 2. Determine Navamsha sign of AK (Karakamsa sign)
    if d9_sign_placements and ak_planet in d9_sign_placements:
        karakamsa_sign = parse_sign_index(d9_sign_placements[ak_planet])
    else:
        karakamsa_sign = calculate_navamsha_sign(ak_d1_sign, ak_deg_in_sign)

    # 3. Determine planet placements in the target reference frame
    # Extract D1 placements
    d1_planet_signs: dict[str, int] = {}
    d9_derived_signs: dict[str, int] = {}
    
    for item in karaka_res["candidate_rankings"]:
        pname = item["name"]
        psign = item["sign_index"]
        pdeg = item["degree_in_sign"]
        d1_planet_signs[pname] = psign
        
        if d9_sign_placements and pname in d9_sign_placements:
            d9_derived_signs[pname] = parse_sign_index(d9_sign_placements[pname])
        else:
            d9_derived_signs[pname] = calculate_navamsha_sign(psign, pdeg)

    # 4. Map houses 1..12 from Karakamsa sign
    if framing_mode == KarakamsaFramingMode.NAVAMSHA_IN_RASHI:
        active_planet_signs = d1_planet_signs
        frame_chart_type = "D1_RASHI"
        house_from_lagna = ((karakamsa_sign - lagna_idx) % 12) + 1
        description = (
            f"Navamsha sign of AK ({SIGN_NAMES_SK[karakamsa_sign]}) projected onto D1 Rashi chart "
            f"(occupies house {house_from_lagna} from Lagna {SIGN_NAMES_SK[lagna_idx]})."
        )
    elif framing_mode == KarakamsaFramingMode.KARAKAMSA_KUNDALI_D9:
        active_planet_signs = d9_derived_signs
        frame_chart_type = "D9_NAVAMSHA"
        house_from_lagna = None
        description = (
            f"Karakamsa Kundali: D9 Navamsha chart oriented with Lagna = "
            f"AK Navamsha sign ({SIGN_NAMES_SK[karakamsa_sign]})."
        )
    else:
        raise ValueError(f"Unsupported Karakamsa framing mode: {framing_mode}")

    # Build house map (1..12) from Karakamsa
    signs_by_house: dict[int, int] = {}
    planets_by_house: dict[int, list[str]] = {h: [] for h in range(1, 13)}
    
    for h in range(1, 13):
        h_sign = ((karakamsa_sign - 1 + (h - 1)) % 12) + 1
        signs_by_house[h] = h_sign
        for p, s in active_planet_signs.items():
            if s == h_sign:
                planets_by_house[h].append(p)

    return {
        "ak_planet": ak_planet,
        "ak_d1_sign": ak_d1_sign,
        "ak_d1_sign_name": SIGN_NAMES_SK[ak_d1_sign],
        "ak_degree_in_sign": ak_deg_in_sign,
        "karakamsa_sign": karakamsa_sign,
        "karakamsa_sign_name": SIGN_NAMES_SK[karakamsa_sign],
        "karakamsa_sign_name_en": SIGN_NAMES_EN[karakamsa_sign],
        "framing_mode": framing_mode.value,
        "frame_chart_type": frame_chart_type,
        "house_from_lagna": house_from_lagna,
        "description": description,
        "signs_by_house": signs_by_house,
        "planets_by_house": planets_by_house,
        "active_planet_signs": active_planet_signs,
    }


# ==============================================================================
# 4. Argala & Virodhargala Engine (Rule JAI-ASP-02, DEC-JAI-08)
# ==============================================================================

def evaluate_argala(
    target_sign: int | str,
    planet_placements: dict[str, int | str],
    ketu_mode: KetuArgalaConvention = KetuArgalaConvention.STANDARD_ARGALA,
    target_house: Optional[int] = None,
) -> dict[str, Any]:
    """
    Evaluate Jaimini Argala and Virodhargala (intervention and obstruction) on a target sign.
    
    Classical Rule (Jaimini Sutras 1.1.7-10; BPHS Ch. 31, v. 1-12):
    1. Primary Argala Pairs:
       - 4th house Argala obstructed by 10th house
       - 2nd house Argala obstructed by 12th house
       - 11th house Argala obstructed by 3rd house
    2. Secondary Argala Pair:
       - 5th house Argala obstructed by 9th house
    3. Obstruction Mechanics:
       - If relative house A has planets (count N_A > 0), an Argala is formed.
       - If corresponding obstruction house V has planets (count N_V):
         - If N_V >= N_A: Argala is obstructed (is_obstructed = True, is_active = False).
         - If N_V < N_A: Argala is active/unobstructed (is_obstructed = False, is_active = True).
       - If N_A == 0: No Argala exists (has_argala = False, is_active = False).
    4. Ketu Direction Convention (DEC-JAI-08):
       - STANDARD_ARGALA: Ketu placement evaluated in forward order (2, 4, 11, 5).
       - REVERSE_KETU_ARGALA: Ketu placement evaluated in reverse order (12, 10, 3, 9).
       
    Returns:
        Structured dictionary with position-by-position results, supporting and obstructing
        planets, active/obstructed status, and summary evidence.
    """
    t_sign = parse_sign_index(target_sign)

    # 1. Normalize planet placements: planet_name -> sign_index (1..12)
    norm_placements: dict[str, int] = {}
    for p, s in planet_placements.items():
        norm_placements[str(p)] = parse_sign_index(s)

    # 2. Evaluate each Argala pair
    position_results: dict[int, dict[str, Any]] = {}
    active_argalas: list[int] = []
    obstructed_argalas: list[int] = []
    all_supporting_planets: list[str] = []
    all_obstructing_planets: list[str] = []

    for arg_offset, vir_offset in ARGALA_PAIRS:
        # Determine target signs for this pair
        arg_sign = ((t_sign - 1 + (arg_offset - 1)) % 12) + 1
        vir_sign = ((t_sign - 1 + (vir_offset - 1)) % 12) + 1

        # Identify planets in Argala position
        arg_planets: list[str] = []
        for p, s in norm_placements.items():
            if p == "Ketu" and ketu_mode == KetuArgalaConvention.REVERSE_KETU_ARGALA:
                # In reverse mode, Ketu in reverse offset forms Argala
                # Reverse offset for Argala offset X is ((t_sign - 1 - (X - 1)) % 12) + 1
                ketu_arg_sign = ((t_sign - 1 - (arg_offset - 1)) % 12) + 1
                if s == ketu_arg_sign:
                    arg_planets.append(p)
            else:
                if s == arg_sign:
                    arg_planets.append(p)

        # Identify planets in Virodha position
        vir_planets: list[str] = []
        for p, s in norm_placements.items():
            if p == "Ketu" and ketu_mode == KetuArgalaConvention.REVERSE_KETU_ARGALA:
                ketu_vir_sign = ((t_sign - 1 - (vir_offset - 1)) % 12) + 1
                if s == ketu_vir_sign:
                    vir_planets.append(p)
            else:
                if s == vir_sign:
                    vir_planets.append(p)

        cnt_arg = len(arg_planets)
        cnt_vir = len(vir_planets)
        has_arg = (cnt_arg > 0)

        if has_arg:
            is_obs = (cnt_vir >= cnt_arg)
            is_act = not is_obs
            if is_act:
                active_argalas.append(arg_offset)
                all_supporting_planets.extend(arg_planets)
            else:
                obstructed_argalas.append(arg_offset)
                all_obstructing_planets.extend(vir_planets)
        else:
            is_obs = False
            is_act = False

        benefics_arg = [p for p in arg_planets if p in NATURAL_BENEFICS]
        malefics_arg = [p for p in arg_planets if p in NATURAL_MALEFICS]

        position_results[arg_offset] = {
            "argala_offset": arg_offset,
            "argala_sign": arg_sign,
            "argala_sign_name": SIGN_NAMES_SK[arg_sign],
            "argala_planets": sorted(arg_planets),
            "argala_count": cnt_arg,
            "virodha_offset": vir_offset,
            "virodha_sign": vir_sign,
            "virodha_sign_name": SIGN_NAMES_SK[vir_sign],
            "virodha_planets": sorted(vir_planets),
            "virodha_count": cnt_vir,
            "has_argala": has_arg,
            "is_obstructed": is_obs,
            "is_active": is_act,
            "benefic_planets": sorted(benefics_arg),
            "malefic_planets": sorted(malefics_arg),
            "argala_nature": (
                "SHUBHA" if len(benefics_arg) > len(malefics_arg)
                else "PAPA" if len(malefics_arg) > len(benefics_arg)
                else "MIXED" if has_arg else "NONE"
            ),
        }

    # Summary classification
    if active_argalas:
        net_status = "ACTIVE_ARGALA"
    elif obstructed_argalas:
        net_status = "OBSTRUCTED_ARGALA"
    else:
        net_status = "NO_ARGALA"

    return {
        "target_sign": t_sign,
        "target_sign_name": SIGN_NAMES_SK[t_sign],
        "target_sign_name_en": SIGN_NAMES_EN[t_sign],
        "target_house": target_house,
        "ketu_mode": ketu_mode.value,
        "net_status": net_status,
        "active_argalas": active_argalas,
        "obstructed_argalas": obstructed_argalas,
        "supporting_planets": sorted(list(set(all_supporting_planets))),
        "obstructing_planets": sorted(list(set(all_obstructing_planets))),
        "positions": position_results,
    }


def evaluate_all_house_argalas(
    lagna_sign: int | str,
    planet_placements: dict[str, int | str],
    ketu_mode: KetuArgalaConvention = KetuArgalaConvention.STANDARD_ARGALA,
) -> dict[int, dict[str, Any]]:
    """
    Evaluate Argala and Virodhargala for all 12 houses from natal Lagna.
    
    Returns:
        dict mapping house number (1..12) -> evaluate_argala() result dict.
    """
    l_sign = parse_sign_index(lagna_sign)
    all_houses: dict[int, dict[str, Any]] = {}
    
    for h in range(1, 13):
        h_sign = ((l_sign - 1 + (h - 1)) % 12) + 1
        all_houses[h] = evaluate_argala(
            target_sign=h_sign,
            planet_placements=planet_placements,
            ketu_mode=ketu_mode,
            target_house=h,
        )
        
    return all_houses
