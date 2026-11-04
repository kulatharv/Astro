"""
Jaimini Chara Dasha Pure Calculation Engine (shared.veda.jaimini_dasha).

Governing Standards:
- Master Specification v3.0 §10, §13.2, §15, Appendix C
- WP0 Traceability Matrix v1.1 TR-054
- ASTROLOGIC_WP7_DESIGN_DECISION_REGISTER.md (DEC-JAI-05, DEC-JAI-06)
- ASTROLOGIC_WP7_RULE_CATALOG_DRAFT.md (Rules JAI-DSH-01 to JAI-DSH-06)

This module provides pure, stateless mathematical calculations for:
1. Chara Dasha progression sequences under KN_RAO and PARASHARA_9TH_HOUSE traditions.
2. Sign duration counting and Svastha (lord in own sign) rules.
3. Exaltation and Debilitation dignity modifiers.
4. Bounded duration clamping ([1, 12] integer years).
5. Antardasha (sub-period) subdivision and duration conservation.
6. Zero side-effects, zero DB, zero Redis.
"""

from __future__ import annotations

import math
from enum import Enum
from typing import Any, Optional

from .jaimini_rules import (
    SIGN_NAMES_SK,
    SIGN_NAMES_EN,
    PARASHARI_SIGN_LORDS,
    parse_sign_index,
    validate_finite_degree,
)


# ==============================================================================
# 1. Enums and Lineage Decision Settings (DEC-JAI-05, DEC-JAI-06)
# ==============================================================================

class CharaProgressionTradition(str, Enum):
    """
    Chara Dasha progression order tradition (DEC-JAI-05).
    
    KN_RAO:
        Direct (forward) for Aries, Taurus, Gemini, Libra, Scorpio, Sagittarius (1, 2, 3, 7, 8, 9).
        Reverse (backward) for Cancer, Leo, Virgo, Capricorn, Aquarius, Pisces (4, 5, 6, 10, 11, 12).
    
    PARASHARA_9TH_HOUSE:
        Look at 9th house from Lagna: if odd (1, 3, 5, 7, 9, 11), direct sequence;
        if even (2, 4, 6, 8, 10, 12), reverse sequence.
    """
    KN_RAO = "KN_RAO"
    PARASHARA_9TH_HOUSE = "PARASHARA_9TH_HOUSE"


class DurationClampMode(str, Enum):
    """
    Dasha duration clamping convention (DEC-JAI-06).
    
    CLAMPED_1_TO_12:
        Strict classical boundary clamping to [1, 12] integer years.
        Exalted lord with base 12 stays 12; debilitated lord with base 1 stays 1.
    
    UNCLAMPED:
        Unclamped calculation (can produce 0 or 13 years).
    
    ZERO_TO_TWELVE:
        Clamped to [0, 12] years.
    """
    CLAMPED_1_TO_12 = "CLAMPED_1_TO_12"
    UNCLAMPED = "UNCLAMPED"
    ZERO_TO_TWELVE = "ZERO_TO_TWELVE"


class SignCountingConvention(str, Enum):
    """
    Direction used when counting displacement from a sign to its lord.
    
    KN_RAO_GROUPS:
        Signs {1, 2, 3, 7, 8, 9} count forward; signs {4, 5, 6, 10, 11, 12} count backward.
    
    ODD_EVEN:
        Odd signs (1, 3, 5, 7, 9, 11) count forward; even signs (2, 4, 6, 8, 10, 12) count backward.
    
    ALL_FORWARD:
        All signs count forward to their lord.
    """
    KN_RAO_GROUPS = "KN_RAO_GROUPS"
    ODD_EVEN = "ODD_EVEN"
    ALL_FORWARD = "ALL_FORWARD"


class AntardashaOrderConvention(str, Enum):
    """
    Sign progression order within Antardashas (sub-periods).
    
    KN_RAO:
        Starts with Mahadasha sign M itself.
        If M in {1, 2, 3, 7, 8, 9}, progresses forward.
        If M in {4, 5, 6, 10, 11, 12}, progresses reverse.
    
    DIRECT_FROM_MAHADASHA:
        Starts with Mahadasha sign M and always progresses forward.
    
    REVERSE_FROM_MAHADASHA:
        Starts with Mahadasha sign M and always progresses reverse.
    """
    KN_RAO = "KN_RAO"
    DIRECT_FROM_MAHADASHA = "DIRECT_FROM_MAHADASHA"
    REVERSE_FROM_MAHADASHA = "REVERSE_FROM_MAHADASHA"


# ==============================================================================
# 2. Astrological Constants for Chara Dasha
# ==============================================================================

# K.N. Rao sign classification for direct/reverse movement
KN_RAO_DIRECT_SIGNS: set[int] = {1, 2, 3, 7, 8, 9}
KN_RAO_REVERSE_SIGNS: set[int] = {4, 5, 6, 10, 11, 12}

# Classical planetary exaltation signs (1-indexed sign number)
EXALTATION_SIGNS: dict[str, int] = {
    "Sun": 1,        # Aries
    "Moon": 2,       # Taurus
    "Mars": 10,      # Capricorn
    "Mercury": 6,    # Virgo
    "Jupiter": 4,    # Cancer
    "Venus": 12,     # Pisces
    "Saturn": 7,     # Libra
    "Rahu": 3,       # Gemini (or Taurus 2 by alternate traditions)
    "Ketu": 9,       # Sagittarius (or Scorpio 8 by alternate traditions)
}

# Classical planetary debilitation signs (1-indexed sign number)
DEBILITATION_SIGNS: dict[str, int] = {
    "Sun": 7,        # Libra
    "Moon": 8,       # Scorpio
    "Mars": 4,       # Cancer
    "Mercury": 12,   # Pisces
    "Jupiter": 10,   # Capricorn
    "Venus": 6,      # Virgo
    "Saturn": 1,     # Aries
    "Rahu": 9,       # Sagittarius
    "Ketu": 3,       # Gemini
}


# ==============================================================================
# 3. Chara Dasha Sign Progression Engine (Rule JAI-DSH-01)
# ==============================================================================

def get_chara_dasha_progression(
    start_sign: int | str,
    tradition: CharaProgressionTradition = CharaProgressionTradition.KN_RAO,
    lagna_sign: Optional[int | str] = None,
) -> tuple[list[int], bool, str]:
    """
    Calculate the ordered sequence of 12 Mahadasha signs for Chara Dasha.
    
    Args:
        start_sign: Sign to begin the dasha cycle (usually natal Lagna).
        tradition: Progression tradition (KN_RAO or PARASHARA_9TH_HOUSE).
        lagna_sign: Natal Lagna sign for 9th house oddity calculation (if different from start_sign).
        
    Returns:
        tuple of:
            - list of 12 unique 1-indexed sign integers [s1, s2, ..., s12].
            - boolean is_forward (True if sequence steps +1, False if -1).
            - string description of the progression rule applied.
            
    Raises:
        ValueError: On invalid signs or unrecognized tradition.
    """
    s_start = parse_sign_index(start_sign)
    s_lagna = parse_sign_index(lagna_sign) if lagna_sign is not None else s_start

    if tradition == CharaProgressionTradition.KN_RAO:
        # K.N. Rao rule: Direction is determined by whether the starting sign is direct or reverse
        is_forward = s_start in KN_RAO_DIRECT_SIGNS
        step = 1 if is_forward else -1
        direction_desc = (
            f"KN_RAO direct progression (+1)" if is_forward
            else f"KN_RAO reverse progression (-1)"
        )
    elif tradition == CharaProgressionTradition.PARASHARA_9TH_HOUSE:
        # Parāśari 9th house oddity: 9th house from Lagna
        ninth_house_sign = ((s_lagna - 1 + 8) % 12) + 1
        # If 9th sign is odd (1, 3, 5, 7, 9, 11), forward; if even (2, 4, 6, 8, 10, 12), reverse
        is_forward = (ninth_house_sign % 2 != 0)
        step = 1 if is_forward else -1
        direction_desc = (
            f"PARASHARA_9TH_HOUSE direct (+1) [9th house is sign {ninth_house_sign} (odd)]" if is_forward
            else f"PARASHARA_9TH_HOUSE reverse (-1) [9th house is sign {ninth_house_sign} (even)]"
        )
    else:
        raise ValueError(f"Unsupported Chara Dasha progression tradition: {tradition}")

    # Build sequence with wraparound
    sequence = [((s_start - 1 + (i * step)) % 12) + 1 for i in range(12)]

    # Invariant assertion: Exactly 12 unique signs, 1 through 12
    if len(sequence) != 12 or set(sequence) != set(range(1, 13)):
        raise RuntimeError(
            f"Progression generation error: generated {sequence}, expected permutation of 1..12"
        )

    return sequence, is_forward, direction_desc


# ==============================================================================
# 4. Sign Duration Counting & Dignity Modifiers (Rules JAI-DSH-02, 03, 04)
# ==============================================================================

def is_sign_forward_counting(
    sign: int | str,
    convention: SignCountingConvention = SignCountingConvention.KN_RAO_GROUPS,
) -> bool:
    """
    Determine whether counting displacement from a sign to its lord is forward or backward.
    """
    s = parse_sign_index(sign)
    if convention == SignCountingConvention.KN_RAO_GROUPS:
        return s in KN_RAO_DIRECT_SIGNS
    elif convention == SignCountingConvention.ODD_EVEN:
        return (s % 2 != 0)
    elif convention == SignCountingConvention.ALL_FORWARD:
        return True
    raise ValueError(f"Unsupported counting convention: {convention}")


def calculate_sign_displacement(from_sign: int | str, to_sign: int | str, is_forward: bool) -> int:
    """
    Calculate inclusive sign displacement count from from_sign to to_sign.
    
    If is_forward:
        count = ((to_sign - from_sign) % 12) + 1
    If not is_forward (reverse):
        count = ((from_sign - to_sign) % 12) + 1
        
    Domain: [1, 12].
    """
    f_sign = parse_sign_index(from_sign)
    t_sign = parse_sign_index(to_sign)

    if is_forward:
        return ((t_sign - f_sign) % 12) + 1
    else:
        return ((f_sign - t_sign) % 12) + 1


def calculate_mahadasha_duration(
    sign: int | str,
    lord_sign: int | str,
    lord_planet: Optional[str] = None,
    counting_convention: SignCountingConvention = SignCountingConvention.KN_RAO_GROUPS,
    clamp_mode: DurationClampMode = DurationClampMode.CLAMPED_1_TO_12,
) -> dict[str, Any]:
    """
    Calculate the duration of a Mahadasha sign in integer years.
    
    Classical Formulas (BPHS Ch. 33, v. 7-13; Jaimini Sutras 2.1):
    1. Base Duration:
       - If lord is in own sign (S == L): duration = 12 years (Svastha rule).
       - If lord is in another sign (S != L):
         Count displacement inclusive from sign to lord (forward or reverse per convention).
         base_duration = count - 1. (Range: 1 to 11 years).
    2. Dignity Modifier (if S != L):
       - If lord is in its sign of exaltation: +1 year.
       - If lord is in its sign of debilitation: -1 year.
       - Otherwise: 0.
       (Note: If S == L, own-sign 12 years is self-contained; dignity modifiers do not alter it).
    3. Clamping:
       - CLAMPED_1_TO_12: max(1, min(12, raw_duration)).
       - UNCLAMPED: raw_duration without clamping.
       - ZERO_TO_TWELVE: max(0, min(12, raw_duration)).
       
    Returns:
        Structured dict with calculation trace and final integer duration.
    """
    s_idx = parse_sign_index(sign)
    l_idx = parse_sign_index(lord_sign)
    
    if lord_planet is None:
        lord_planet = PARASHARI_SIGN_LORDS[s_idx]

    is_forward = is_sign_forward_counting(s_idx, counting_convention)

    # 1. Base Duration Calculation
    is_own_sign = (s_idx == l_idx)
    if is_own_sign:
        # Svastha rule: 12 full years
        displacement = 1
        base_years = 12
        dignity = "OWN_SIGN"
        modifier = 0
        raw_years = 12
        rule_note = "Lord in own sign (Svastha) = 12 years"
    else:
        displacement = calculate_sign_displacement(s_idx, l_idx, is_forward)
        base_years = displacement - 1  # Range: 1..11
        
        # 2. Check exaltation / debilitation
        exalt_sign = EXALTATION_SIGNS.get(lord_planet)
        debilit_sign = DEBILITATION_SIGNS.get(lord_planet)
        
        if exalt_sign is not None and l_idx == exalt_sign:
            dignity = "EXALTED"
            modifier = 1
        elif debilit_sign is not None and l_idx == debilit_sign:
            dignity = "DEBILITATED"
            modifier = -1
        else:
            dignity = "NEUTRAL"
            modifier = 0
            
        raw_years = base_years + modifier
        rule_note = (
            f"Displacement={displacement} -> Base={base_years} + "
            f"DignityModifier={modifier} ({dignity})"
        )

    # 3. Apply Clamping
    if clamp_mode == DurationClampMode.CLAMPED_1_TO_12:
        final_years = max(1, min(12, raw_years))
    elif clamp_mode == DurationClampMode.ZERO_TO_TWELVE:
        final_years = max(0, min(12, raw_years))
    elif clamp_mode == DurationClampMode.UNCLAMPED:
        final_years = raw_years
    else:
        raise ValueError(f"Unsupported duration clamp mode: {clamp_mode}")

    is_clamped = (final_years != raw_years)

    return {
        "sign": s_idx,
        "sign_name": SIGN_NAMES_SK[s_idx],
        "lord_planet": lord_planet,
        "lord_sign": l_idx,
        "lord_sign_name": SIGN_NAMES_SK[l_idx],
        "is_forward_counting": is_forward,
        "displacement_count": displacement,
        "is_own_sign": is_own_sign,
        "base_years": base_years,
        "dignity": dignity,
        "dignity_modifier": modifier,
        "raw_years": raw_years,
        "final_years": final_years,
        "clamp_mode": clamp_mode.value,
        "is_clamped": is_clamped,
        "rule_note": rule_note,
    }


# ==============================================================================
# 5. Antardasha Subdivision & Duration Conservation (Rule JAI-DSH-06)
# ==============================================================================

def calculate_antardashas(
    mahadasha_sign: int | str,
    mahadasha_duration_years: int | float,
    order_convention: AntardashaOrderConvention = AntardashaOrderConvention.KN_RAO,
) -> list[dict[str, Any]]:
    """
    Subdivide a Mahadasha into 12 Antardashas (sub-periods).
    
    Sub-period Sign Progression:
    - KN_RAO:
      Starts with Mahadasha sign M itself.
      If M in {1, 2, 3, 7, 8, 9}, progresses forward (+1).
      If M in {4, 5, 6, 10, 11, 12}, progresses reverse (-1).
    - DIRECT_FROM_MAHADASHA: Always forward (+1) starting from M.
    - REVERSE_FROM_MAHADASHA: Always reverse (-1) starting from M.
    
    Duration Representation & Conservation:
    - Each Antardasha duration in months: exactly D months (where D is Mahadasha duration in years).
      Proof: 12 Antardashas * D months = 12 * D months = D years.
    - Each Antardasha duration in fractional years: D / 12.0.
    - Total duration conservation invariant:
      Sum of all 12 Antardasha fractional years == D.
      Rounding residuals are absorbed by the 12th Antardasha to maintain exact bitwise equality.
      
    Returns:
        List of 12 Antardasha dictionaries.
    """
    m_sign = parse_sign_index(mahadasha_sign)
    d_years = float(mahadasha_duration_years)
    
    if not math.isfinite(d_years) or d_years < 0:
        raise ValueError(f"Mahadasha duration must be a non-negative finite number, got: {d_years}")

    # 1. Determine sub-period progression order
    if order_convention == AntardashaOrderConvention.KN_RAO:
        is_forward = m_sign in KN_RAO_DIRECT_SIGNS
        step = 1 if is_forward else -1
    elif order_convention == AntardashaOrderConvention.DIRECT_FROM_MAHADASHA:
        is_forward = True
        step = 1
    elif order_convention == AntardashaOrderConvention.REVERSE_FROM_MAHADASHA:
        is_forward = False
        step = -1
    else:
        raise ValueError(f"Unsupported Antardasha order convention: {order_convention}")

    sub_signs = [((m_sign - 1 + (i * step)) % 12) + 1 for i in range(12)]

    # 2. Allocate durations
    # Base fractional year duration per sub-period
    base_fractional = round(d_years / 12.0, 8)
    sub_periods: list[dict[str, Any]] = []
    accumulated_years = 0.0

    for i in range(12):
        s_sign = sub_signs[i]
        is_last = (i == 11)
        
        if is_last:
            # Conserve exact total duration by assigning remaining residual
            sub_year_dur = round(d_years - accumulated_years, 8)
        else:
            sub_year_dur = base_fractional
            accumulated_years = round(accumulated_years + sub_year_dur, 8)
            
        sub_months = d_years  # 1 year in Mahadasha = 1 month in Antardasha
        
        sub_periods.append({
            "antardasha_index": i + 1,
            "sign": s_sign,
            "sign_name": SIGN_NAMES_SK[s_sign],
            "duration_years_fractional": sub_year_dur,
            "duration_months": sub_months,
            "parent_mahadasha_sign": m_sign,
        })

    # Assert total duration conservation
    total_conserved = sum(sp["duration_years_fractional"] for sp in sub_periods)
    if not math.isclose(total_conserved, d_years, abs_tol=1e-6):
        raise RuntimeError(
            f"Duration conservation violated: sum={total_conserved}, expected={d_years}"
        )

    return sub_periods


# ==============================================================================
# 6. Complete Chara Dasha Cycle Orchestrator
# ==============================================================================

def calculate_chara_dasha_cycle(
    start_sign: int | str,
    lord_placements: dict[int, int | str],
    tradition: CharaProgressionTradition = CharaProgressionTradition.KN_RAO,
    clamp_mode: DurationClampMode = DurationClampMode.CLAMPED_1_TO_12,
    counting_convention: SignCountingConvention = SignCountingConvention.KN_RAO_GROUPS,
    antardasha_convention: AntardashaOrderConvention = AntardashaOrderConvention.KN_RAO,
    lagna_sign: Optional[int | str] = None,
) -> dict[str, Any]:
    """
    Calculate a complete 12-sign Chara Dasha cycle with all Mahadashas and Antardashas.
    
    Args:
        start_sign: Initial sign to begin progression.
        lord_placements: Mapping of sign index (1..12) -> sign occupied by its lord (1..12 or name).
        tradition: Progression tradition (KN_RAO or PARASHARA_9TH_HOUSE).
        clamp_mode: Duration clamping mode.
        counting_convention: Forward/reverse sign counting convention.
        antardasha_convention: Antardasha sub-period progression convention.
        lagna_sign: Natal Lagna sign for 9th house oddity calculation (if different from start_sign).
        
    Returns:
        Structured dictionary containing all 12 Mahadashas, their 144 Antardashas,
        cumulative elapsed years, and full calculation metadata.
    """
    s_start = parse_sign_index(start_sign)
    s_lagna = parse_sign_index(lagna_sign) if lagna_sign is not None else s_start

    # 1. Generate the 12-sign Mahadasha progression sequence
    sign_sequence, is_forward, direction_desc = get_chara_dasha_progression(
        start_sign=s_start,
        tradition=tradition,
        lagna_sign=s_lagna,
    )

    # 2. Compute duration and Antardashas for each Mahadasha
    mahadashas: list[dict[str, Any]] = []
    cumulative_years = 0.0
    
    for rank, s in enumerate(sign_sequence):
        if s not in lord_placements:
            raise ValueError(f"Missing lord placement for sign {s} in lord_placements mapping.")
            
        l_sign = lord_placements[s]
        dur_info = calculate_mahadasha_duration(
            sign=s,
            lord_sign=l_sign,
            counting_convention=counting_convention,
            clamp_mode=clamp_mode,
        )
        
        d_years = dur_info["final_years"]
        antardashas = calculate_antardashas(
            mahadasha_sign=s,
            mahadasha_duration_years=d_years,
            order_convention=antardasha_convention,
        )
        
        start_elapsed = cumulative_years
        cumulative_years = round(cumulative_years + d_years, 6)
        end_elapsed = cumulative_years
        
        mahadashas.append({
            "order_index": rank + 1,
            "sign": s,
            "sign_name": SIGN_NAMES_SK[s],
            "sign_name_en": SIGN_NAMES_EN[s],
            "duration_years": d_years,
            "elapsed_start_years": start_elapsed,
            "elapsed_end_years": end_elapsed,
            "calculation_details": dur_info,
            "antardashas": antardashas,
        })

    return {
        "start_sign": s_start,
        "start_sign_name": SIGN_NAMES_SK[s_start],
        "lagna_sign": s_lagna,
        "lagna_sign_name": SIGN_NAMES_SK[s_lagna],
        "tradition": tradition.value,
        "direction_description": direction_desc,
        "is_progression_forward": is_forward,
        "clamp_mode": clamp_mode.value,
        "counting_convention": counting_convention.value,
        "antardasha_convention": antardasha_convention.value,
        "total_cycle_years": cumulative_years,
        "mahadasha_count": len(mahadashas),
        "total_antardasha_count": sum(len(m["antardashas"]) for m in mahadashas),
        "mahadashas": mahadashas,
    }
