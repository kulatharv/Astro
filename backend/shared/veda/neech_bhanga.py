"""Neech Bhanga (Debilitation Cancellation) Engine (Pure Shared Library).

Classical Jyotish reference: Brihat Parashara Hora Shastra Ch. 41; Phaladeepika Ch. 6, v. 26-30.
Distinguishes between:
  1. Debilitation detected
  2. Neecha Bhanga (cancellation of debility) confirmed
  3. Neecha Bhanga Raja Yoga (NBRY) established
"""

from typing import Any, Dict, List, Optional
from .strength import DEBILITATION
from .zodiac import SIGN_LORDS

# Correct classical exaltation lords:
# Sun is exalted in Mesha (ruled by Mars)
# Moon is exalted in Vrishabha (ruled by Venus)
# Mars is exalted in Makara (ruled by Saturn)
# Mercury is exalted in Kanya (ruled by Mercury)
# Jupiter is exalted in Karka (ruled by Moon)
# Venus is exalted in Meena (ruled by Jupiter)
# Saturn is exalted in Tula (ruled by Venus)
NEECH_BHANGA_EXALT_LORDS = {
    "Sun": "Mars",
    "Moon": "Venus",
    "Mars": "Saturn",
    "Mercury": "Mercury",
    "Jupiter": "Moon",
    "Venus": "Jupiter",
    "Saturn": "Venus",
}


def evaluate_neech_bhanga(
    name: str,
    sign: str,
    planet_map: dict,
    lagna: str = "",
) -> Dict[str, Any]:
    """
    Evaluate explicit classical Neecha Bhanga and Raja Yoga predicates.
    
    Returns structured analysis:
      - is_debilitated: bool
      - is_cancelled: bool (Neecha Bhanga detected)
      - is_raja_yoga: bool (Neecha Bhanga Raja Yoga established)
      - status: "NOT_DEBILITATED" | "ACTIVE_DEBILITY" | "NEECH_BHANGA_CONFIRMED" | "NBRY_ESTABLISHED"
      - conditions_met: list of condition dicts
      - conditions_unmet: list of condition dicts
      - primary_reason: human-readable summary
    """
    if DEBILITATION.get(name) != sign:
        return {
            "planet": name,
            "sign": sign,
            "is_debilitated": False,
            "is_cancelled": False,
            "is_raja_yoga": False,
            "status": "NOT_DEBILITATED",
            "conditions_met": [],
            "conditions_unmet": [],
            "primary_reason": f"{name} is not debilitated in {sign}",
        }

    p_data = planet_map.get(name, {})
    p_house = p_data.get("house", 0)
    moon_h = planet_map.get("Moon", {}).get("house", 0)

    def _in_kendra_lagna(h: int) -> bool:
        return h in (1, 4, 7, 10)

    def _in_kendra_moon(h: int) -> bool:
        return moon_h > 0 and (((h - moon_h) % 12) + 1) in (1, 4, 7, 10)

    def _is_kendra(h: int) -> bool:
        return _in_kendra_lagna(h) or _in_kendra_moon(h)

    conditions_met = []
    conditions_unmet = []

    # Condition 1: Retrograde motion reverses debilitation weakness
    if p_data.get("retrograde"):
        conditions_met.append({
            "id": "NB-COND-01",
            "name": "Retrograde Debilitation Reversal",
            "evidence": f"{name} is retrograde in {sign}, reversing debility",
            "type": "CANCELLATION",
        })
    else:
        conditions_unmet.append({
            "id": "NB-COND-01",
            "name": "Retrograde Debilitation Reversal",
            "evidence": f"{name} is direct (not retrograde)",
        })

    # Condition 2: Dispositor (Lord of debilitation sign) in Kendra from Lagna or Moon
    dispositor = SIGN_LORDS.get(sign)
    disp_h = planet_map.get(dispositor, {}).get("house", 0) if dispositor else 0
    if dispositor and _is_kendra(disp_h):
        k_type = "Lagna" if _in_kendra_lagna(disp_h) else "Moon"
        conditions_met.append({
            "id": "NB-COND-02",
            "name": "Dispositor in Kendra",
            "evidence": f"Dispositor {dispositor} occupies Kendra ({disp_h}) from {k_type}",
            "type": "CANCELLATION",
        })
    else:
        conditions_unmet.append({
            "id": "NB-COND-02",
            "name": "Dispositor in Kendra",
            "evidence": f"Dispositor {dispositor} in house {disp_h} is not in a Kendra from Lagna or Moon",
        })

    # Condition 3: Exaltation Lord in Kendra from Lagna or Moon
    exalt_lord = NEECH_BHANGA_EXALT_LORDS.get(name)
    exalt_h = planet_map.get(exalt_lord, {}).get("house", 0) if exalt_lord else 0
    if exalt_lord and _is_kendra(exalt_h):
        k_type = "Lagna" if _in_kendra_lagna(exalt_h) else "Moon"
        conditions_met.append({
            "id": "NB-COND-03",
            "name": "Exaltation Lord in Kendra",
            "evidence": f"Exaltation lord {exalt_lord} occupies Kendra ({exalt_h}) from {k_type}",
            "type": "CANCELLATION",
        })
    else:
        conditions_unmet.append({
            "id": "NB-COND-03",
            "name": "Exaltation Lord in Kendra",
            "evidence": f"Exaltation lord {exalt_lord} in house {exalt_h} is not in Kendra",
        })

    # Core cancellation (Neecha Bhanga): Conditions 1, 2, or 3
    is_cancelled = any(c["id"] in ("NB-COND-01", "NB-COND-02", "NB-COND-03") for c in conditions_met)

    # Condition 4: Mutual Kendras between Dispositor and Exaltation Lord (Phaladeepika 6.27)
    # Requires at least one lord to be in a Kendra from Lagna or Moon to anchor the quadrant
    mutual_kendra = False
    if disp_h > 0 and exalt_h > 0 and (_is_kendra(disp_h) or _is_kendra(exalt_h)):
        dist_mutual = ((disp_h - exalt_h) % 12) + 1
        if dist_mutual in (1, 4, 7, 10):
            mutual_kendra = True
            conditions_met.append({
                "id": "NB-COND-04",
                "name": "Mutual Kendra (Dispositor & Exaltation Lord)",
                "evidence": f"{dispositor} (H{disp_h}) and {exalt_lord} (H{exalt_h}) are in mutual quadrant {dist_mutual}",
                "type": "RAJA_YOGA_CATALYST",
            })
    if not mutual_kendra:
        conditions_unmet.append({
            "id": "NB-COND-04",
            "name": "Mutual Kendra (Dispositor & Exaltation Lord)",
            "evidence": f"{dispositor} and {exalt_lord} are not in qualifying mutual Kendra",
        })

    # Condition 5: Both Dispositor AND Exaltation Lord simultaneously in Kendras from Lagna
    both_in_lagna_kendra = _in_kendra_lagna(disp_h) and _in_kendra_lagna(exalt_h)
    if both_in_lagna_kendra:
        conditions_met.append({
            "id": "NB-COND-05",
            "name": "Dual Kendra Anchor (BPHS 41)",
            "evidence": f"Both dispositor {dispositor} and exaltation lord {exalt_lord} anchor Kendras from Lagna",
            "type": "RAJA_YOGA_FOUNDATION",
        })

    # Explicit Raja Yoga Requirement:
    # Requires either Condition 4 (Mutual Kendras with Kendra anchor) OR Condition 5 (Dual Kendras) OR
    # (debilitated planet in Kendra AND dispositor in Kendra)
    p_in_kendra = _in_kendra_lagna(p_house)
    is_raja_yoga = is_cancelled and (
        mutual_kendra or both_in_lagna_kendra or (p_in_kendra and _in_kendra_lagna(disp_h))
    )

    if is_raja_yoga:
        status = "NBRY_ESTABLISHED"
        primary_reason = f"Neecha Bhanga Raja Yoga established: {conditions_met[0]['evidence']}"
    elif is_cancelled:
        status = "NEECH_BHANGA_CONFIRMED"
        primary_reason = f"Neecha Bhanga confirmed (debilitation cancelled; Raja Yoga not established): {conditions_met[0]['evidence']}"
    else:
        status = "ACTIVE_DEBILITY"
        primary_reason = f"Debilitation active in {sign}; no classical cancellation condition satisfied"

    return {
        "planet": name,
        "sign": sign,
        "is_debilitated": True,
        "is_cancelled": is_cancelled,
        "is_raja_yoga": is_raja_yoga,
        "status": status,
        "conditions_met": conditions_met,
        "conditions_unmet": conditions_unmet,
        "primary_reason": primary_reason,
    }


def is_neech_bhanga(name: str, sign: str, planet_map: dict) -> bool:
    """
    True if the planet's debilitation is cancelled according to classical rules.
    Maintains backward compatibility for existing callers.
    """
    res = evaluate_neech_bhanga(name, sign, planet_map)
    return res["is_cancelled"]


def is_neech_bhanga_raja_yoga(name: str, sign: str, planet_map: dict, lagna: str = "") -> bool:
    """
    True ONLY if Neecha Bhanga Raja Yoga is strictly established under classical conditions.
    """
    res = evaluate_neech_bhanga(name, sign, planet_map, lagna)
    return res["is_raja_yoga"]

