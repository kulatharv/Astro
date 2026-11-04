"""
Classical Vedic Astrology Marriage & Relationship Engine (Pure Shared Library).

Implements 24 active deterministic, explainable Parashari marriage rules,
plus 2 formally registered Jaimini candidate rules (pending WP7 dependency),
with canonical schemas, structured predicates, explicit exception checks,
multi-frame cross-readings (D1, Chandra Lagna, Venus Frame, D9 Navamsa),
and relational dynamic archetype evidence synthesis.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Any, Optional

from .zodiac import SIGNS_SK, SIGN_LORDS
from .strength import EXALTATION, DEBILITATION, OWN_SIGNS
from .lordship import get_house_lord
from .neech_bhanga import is_neech_bhanga, evaluate_neech_bhanga, is_neech_bhanga_raja_yoga
from .combustion import is_combust
from .doshas import evaluate_mangal_dosha_multiframe, check_mangal_cancellations


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

KENDRA = {1, 4, 7, 10}
TRIKONA = {1, 5, 9}
DUSTHANA = {6, 8, 12}
UPACHAYA = {3, 6, 10, 11}
DHANA_HOUSES = {2, 11}

CLASSICAL_7 = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
NATURAL_BENEFICS = {"Jupiter", "Venus", "Mercury", "Moon"}
NATURAL_MALEFICS = {"Sun", "Mars", "Saturn", "Rahu", "Ketu"}

RELATION_ARCHETYPES = [
    "Harmony & Devotion",
    "Romantic Courtship & Passion",
    "Familial Cohesion & Tradition",
    "Growth Through Effort & Adjustment",
    "Transformative & Independent Dynamic",
]


# ---------------------------------------------------------------------------
# Canonical Rule Dataclass
# ---------------------------------------------------------------------------

@dataclass
class MarriageRule:
    rule_id: str
    version: str
    domain: str
    profile: str
    chart_frame: str
    predicate: Callable[[dict, dict], tuple[bool, str, list[str]]]
    ordered_exceptions: list[Callable[[dict, dict], tuple[bool, str]]] = field(default_factory=list)
    dedupe_key: Optional[str] = None
    effect: str = "SUPPORTS"  # SUPPORTS, OBSTRUCTS, CONDITIONAL
    birth_time_sensitive: bool = False
    explanation_template: str = ""
    source_family: str = ""
    source_reference: str = ""
    source_status: str = "VERIFIED"  # VERIFIED, SOURCE VERIFICATION REQUIRED
    review_status: str = "ACCEPTED"  # ACCEPTED, EXPERT REVIEW REQUIRED, PENDING_WP7_DEPENDENCY
    confidence: str = "HIGH"  # HIGH, MEDIUM, LOW, needs expert check
    tests: dict[str, Any] = field(default_factory=dict)
    archetypes: list[str] = field(default_factory=list)
    enabled_by_default: bool = True


# ---------------------------------------------------------------------------
# Computational Helpers
# ---------------------------------------------------------------------------

def safe_house_lord(lagna: str, h: int) -> str:
    """Safely get house lord with normalization and fallback for unknown lagnas."""
    if not lagna:
        return ""
    norm = lagna.strip().capitalize()
    if norm == "Vrishika":
        norm = "Vrischika"
    try:
        return get_house_lord(norm, h)
    except (ValueError, KeyError):
        return ""


# 9 Navamsa parts per sign (3°20' each)
NAVAMSA_START = {
    0: 0, 4: 0, 8: 0,   # Fire signs (Mesha, Simha, Dhanu) start from Mesha (0)
    1: 9, 5: 9, 9: 9,   # Earth signs (Vrishabha, Kanya, Makara) start from Makara (9)
    2: 6, 6: 6, 10: 6,  # Air signs (Mithuna, Tula, Kumbha) start from Tula (6)
    3: 3, 7: 3, 11: 3,  # Water signs (Karka, Vrischika, Meena) start from Karka (3)
}

PADA_DEG = 30.0 / 9.0  # 3.3333333333333335 degrees


def calculate_d9_navamsa_sign(sign: str, degree_in_sign: float) -> str:
    """
    Calculate D9 Navamsa sign name for a planet with given sign and degree within sign.
    """
    if sign not in SIGNS_SK:
        return sign
    sign_idx = SIGNS_SK.index(sign)
    deg = float(degree_in_sign) % 30.0
    pada = int(deg / PADA_DEG)
    pada = max(0, min(8, pada))

    start_sign = NAVAMSA_START.get(sign_idx, 0)
    nav_idx = (start_sign + pada) % 12
    return SIGNS_SK[nav_idx]


def get_planets_in_house(planet_map: dict, h: int) -> list[str]:
    """Return all planets occupying house h."""
    return [p for p, d in planet_map.items() if d.get("house") == h]


def get_planet_aspects_to_house(planet: str, planet_house: int, target_house: int) -> bool:
    """Check if planet casts a classical Vedic Graha Drishti onto target_house."""
    if planet_house <= 0 or target_house <= 0:
        return False
    diff = ((target_house - planet_house) % 12) + 1  # 1-based count from planet
    if diff == 7:
        return True
    if planet == "Mars" and diff in (4, 8):
        return True
    if planet == "Jupiter" and diff in (5, 9):
        return True
    if planet == "Saturn" and diff in (3, 10):
        return True
    if planet in ("Rahu", "Ketu") and diff in (5, 9):
        return True
    return False


def get_house_relative(base_house: int, count: int) -> int:
    """Cyclic house arithmetic: count-th house from base_house (1-indexed)."""
    return ((base_house + count - 2) % 12) + 1


# ---------------------------------------------------------------------------
# Predicates and Exceptions for the 26 Marriage Rules
# ---------------------------------------------------------------------------

# Rule 1: 7th Lord in Kendra
def _pred_h7_lord_kendra(ctx: dict, extra: dict) -> tuple[bool, str, list[str]]:
    hl = ctx.get("house_lords", {})
    l7 = hl.get(7) or safe_house_lord(ctx.get("lagna", ""), 7)
    pdata = ctx.get("planet_map", {}).get(l7, {})
    h = pdata.get("house")
    if h in KENDRA:
        return True, f"7th lord {l7} occupies Kendra house {h}", [l7, f"H{h}"]
    return False, "", []

def _exc_h7_debilitated_no_nb(ctx: dict, extra: dict) -> tuple[bool, str]:
    hl = ctx.get("house_lords", {})
    l7 = hl.get(7) or safe_house_lord(ctx.get("lagna", ""), 7)
    pdata = ctx.get("planet_map", {}).get(l7, {})
    sign = pdata.get("sign", "")
    if sign == DEBILITATION.get(l7):
        if not is_neech_bhanga(l7, sign, ctx.get("planet_map", {})):
            return True, f"7th lord {l7} is debilitated in {sign} without cancellation"
    return False, ""


# Rule 2: 7th Lord in Trikona
def _pred_h7_lord_trikona(ctx: dict, extra: dict) -> tuple[bool, str, list[str]]:
    hl = ctx.get("house_lords", {})
    l7 = hl.get(7) or safe_house_lord(ctx.get("lagna", ""), 7)
    pdata = ctx.get("planet_map", {}).get(l7, {})
    h = pdata.get("house")
    if h in (5, 9):
        return True, f"7th lord {l7} occupies auspicious Trikona house {h}", [l7, f"H{h}"]
    return False, "", []


# Rule 3: 7th Lord in Dusthana
def _pred_h7_lord_dusthana(ctx: dict, extra: dict) -> tuple[bool, str, list[str]]:
    hl = ctx.get("house_lords", {})
    l7 = hl.get(7) or safe_house_lord(ctx.get("lagna", ""), 7)
    pdata = ctx.get("planet_map", {}).get(l7, {})
    h = pdata.get("house")
    if h in DUSTHANA:
        return True, f"7th lord {l7} placed in Dusthana house {h}", [l7, f"H{h}"]
    return False, "", []

def _exc_h7_dusthana_own_or_exalted(ctx: dict, extra: dict) -> tuple[bool, str]:
    hl = ctx.get("house_lords", {})
    l7 = hl.get(7) or safe_house_lord(ctx.get("lagna", ""), 7)
    pdata = ctx.get("planet_map", {}).get(l7, {})
    sign = pdata.get("sign", "")
    if sign == EXALTATION.get(l7) or sign in OWN_SIGNS.get(l7, []):
        return True, f"7th lord {l7} is in dignity ({sign}) in Dusthana, mitigating relational friction"
    return False, ""


# Rule 4: 7th Lord Exalted or in Own Sign
def _pred_h7_lord_exalted_own(ctx: dict, extra: dict) -> tuple[bool, str, list[str]]:
    hl = ctx.get("house_lords", {})
    l7 = hl.get(7) or safe_house_lord(ctx.get("lagna", ""), 7)
    pdata = ctx.get("planet_map", {}).get(l7, {})
    sign = pdata.get("sign", "")
    if sign == EXALTATION.get(l7):
        return True, f"7th lord {l7} is exalted in {sign}", [l7, sign]
    if sign in OWN_SIGNS.get(l7, []):
        return True, f"7th lord {l7} is situated in own sign {sign}", [l7, sign]
    return False, "", []


# Rule 5: 7th Lord Debilitated
def _pred_h7_lord_debilitated(ctx: dict, extra: dict) -> tuple[bool, str, list[str]]:
    hl = ctx.get("house_lords", {})
    l7 = hl.get(7) or safe_house_lord(ctx.get("lagna", ""), 7)
    pdata = ctx.get("planet_map", {}).get(l7, {})
    sign = pdata.get("sign", "")
    if sign == DEBILITATION.get(l7):
        return True, f"7th lord {l7} is debilitated in {sign}", [l7, sign]
    return False, "", []

def _exc_h7_neech_bhanga(ctx: dict, extra: dict) -> tuple[bool, str]:
    hl = ctx.get("house_lords", {})
    l7 = hl.get(7) or safe_house_lord(ctx.get("lagna", ""), 7)
    pdata = ctx.get("planet_map", {}).get(l7, {})
    sign = pdata.get("sign", "")
    if is_neech_bhanga(l7, sign, ctx.get("planet_map", {})):
        nb = evaluate_neech_bhanga(l7, sign, ctx.get("planet_map", {}))
        return True, nb["primary_reason"]
    return False, ""


# Rule 6: Natural Benefic in 7th House
def _pred_h7_benefic_occupation(ctx: dict, extra: dict) -> tuple[bool, str, list[str]]:
    h7_planets = get_planets_in_house(ctx.get("planet_map", {}), 7)
    benefics_in_7 = [p for p in h7_planets if p in ("Jupiter", "Venus", "Mercury")]
    malefics_in_7 = [p for p in h7_planets if p in ("Sun", "Mars", "Saturn", "Rahu", "Ketu")]
    if benefics_in_7 and not malefics_in_7:
        return True, f"Unblemished natural benefic(s) {', '.join(benefics_in_7)} in 7th house", benefics_in_7
    return False, "", []


# Rule 7: Natural Malefic in 7th House
def _pred_h7_malefic_occupation(ctx: dict, extra: dict) -> tuple[bool, str, list[str]]:
    h7_planets = get_planets_in_house(ctx.get("planet_map", {}), 7)
    malefics_in_7 = [p for p in h7_planets if p in ("Sun", "Mars", "Saturn", "Rahu", "Ketu")]
    if malefics_in_7:
        return True, f"Natural malefic(s) {', '.join(malefics_in_7)} in 7th house", malefics_in_7
    return False, "", []

def _exc_h7_malefic_in_dignity(ctx: dict, extra: dict) -> tuple[bool, str]:
    h7_planets = get_planets_in_house(ctx.get("planet_map", {}), 7)
    pm = ctx.get("planet_map", {})
    for p in h7_planets:
        if p in ("Sun", "Mars", "Saturn"):
            sign = pm.get(p, {}).get("sign", "")
            if sign == EXALTATION.get(p) or sign in OWN_SIGNS.get(p, []):
                return True, f"Malefic {p} in 7th is in high dignity ({sign}), mitigating harshness"
    return False, ""


# Rule 8: Papa Kartari to 7th House
def _pred_h7_papakartari(ctx: dict, extra: dict) -> tuple[bool, str, list[str]]:
    pm = ctx.get("planet_map", {})
    h6_planets = get_planets_in_house(pm, 6)
    h8_planets = get_planets_in_house(pm, 8)
    h7_planets = get_planets_in_house(pm, 7)

    m6 = [p for p in h6_planets if p in NATURAL_MALEFICS]
    m8 = [p for p in h8_planets if p in NATURAL_MALEFICS]
    b7 = [p for p in h7_planets if p in NATURAL_BENEFICS]

    if m6 and m8 and not b7:
        return True, f"7th house hemmed between malefics {m6} in 6th and {m8} in 8th (Papa Kartari)", m6 + m8
    return False, "", []

def _exc_kartari_h7_relief(ctx: dict, extra: dict) -> tuple[bool, str]:
    pm = ctx.get("planet_map", {})
    b6 = [p for p in get_planets_in_house(pm, 6) if p in NATURAL_BENEFICS]
    b8 = [p for p in get_planets_in_house(pm, 8) if p in NATURAL_BENEFICS]
    if b6 or b8:
        return True, "Benefic presence in flanking house relieves the Papa Kartari affliction"
    return False, ""


# Rule 9: Venus Dignity (Naisargika Kalatrakaraka)
def _pred_karaka_venus_dignity(ctx: dict, extra: dict) -> tuple[bool, str, list[str]]:
    venus = ctx.get("planet_map", {}).get("Venus", {})
    sign = venus.get("sign", "")
    if sign == EXALTATION.get("Venus"):
        return True, f"Venus is exalted in {sign} (peak Kalatrakaraka vitality)", ["Venus", sign]
    if sign in OWN_SIGNS.get("Venus", []):
        return True, f"Venus is situated in own sign {sign}", ["Venus", sign]
    return False, "", []


# Rule 10: Venus Debilitated
def _pred_karaka_venus_debilitated(ctx: dict, extra: dict) -> tuple[bool, str, list[str]]:
    venus = ctx.get("planet_map", {}).get("Venus", {})
    sign = venus.get("sign", "")
    if sign == DEBILITATION.get("Venus"):
        return True, f"Venus is debilitated in {sign}", ["Venus", sign]
    return False, "", []

def _exc_venus_neech_bhanga(ctx: dict, extra: dict) -> tuple[bool, str]:
    venus = ctx.get("planet_map", {}).get("Venus", {})
    sign = venus.get("sign", "")
    if is_neech_bhanga("Venus", sign, ctx.get("planet_map", {})):
        nb = evaluate_neech_bhanga("Venus", sign, ctx.get("planet_map", {}))
        return True, nb["primary_reason"]
    return False, ""


# Rule 11: Venus Combust
def _pred_karaka_venus_combust(ctx: dict, extra: dict) -> tuple[bool, str, list[str]]:
    pm = ctx.get("planet_map", {})
    sun = pm.get("Sun", {})
    venus = pm.get("Venus", {})
    if sun and venus:
        s_sign = sun.get("sign", "")
        v_sign = venus.get("sign", "")
        s_deg = float(sun.get("degree_decimal", sun.get("degree", 0.0)))
        v_deg = float(venus.get("degree_decimal", venus.get("degree", 0.0)))
        if s_sign in SIGNS_SK and v_sign in SIGNS_SK:
            s_abs = SIGNS_SK.index(s_sign) * 30.0 + (s_deg % 30.0)
            v_abs = SIGNS_SK.index(v_sign) * 30.0 + (v_deg % 30.0)
            diff = abs(s_abs - v_abs) % 360.0
            if diff > 180.0:
                diff = 360.0 - diff
            threshold = 8.0 if venus.get("retrograde") else 10.0
            if diff <= threshold:
                return True, f"Venus is combust within {diff:.1f}° of Sun (threshold {threshold}°)", ["Venus", "Sun"]
    return False, "", []


# Rule 12: Jupiter Benefic Influence on 7th House / Lord
def _pred_karaka_jupiter_benefic(ctx: dict, extra: dict) -> tuple[bool, str, list[str]]:
    pm = ctx.get("planet_map", {})
    hl = ctx.get("house_lords", {})
    l7 = hl.get(7) or safe_house_lord(ctx.get("lagna", ""), 7)
    jup = pm.get("Jupiter", {})
    j_h = jup.get("house", 0)

    if j_h == 7:
        return True, "Jupiter occupies the 7th house, infusing partnerships with wisdom, ethics, and grace", ["Jupiter", "H7"]
    if get_planet_aspects_to_house("Jupiter", j_h, 7):
        return True, f"Jupiter casts classical Graha Drishti onto 7th house from house {j_h}", ["Jupiter", "H7"]
    l7_h = pm.get(l7, {}).get("house", 0)
    if j_h > 0 and l7_h > 0 and j_h == l7_h:
        return True, f"Jupiter conjoins 7th lord {l7} in house {j_h}", ["Jupiter", l7]
    return False, "", []


# Rule 13: Jupiter Debilitated
def _pred_karaka_jupiter_debilitated(ctx: dict, extra: dict) -> tuple[bool, str, list[str]]:
    jup = ctx.get("planet_map", {}).get("Jupiter", {})
    sign = jup.get("sign", "")
    if sign == DEBILITATION.get("Jupiter"):
        return True, f"Jupiter is debilitated in {sign}", ["Jupiter", sign]
    return False, "", []

def _exc_jupiter_neech_bhanga(ctx: dict, extra: dict) -> tuple[bool, str]:
    jup = ctx.get("planet_map", {}).get("Jupiter", {})
    sign = jup.get("sign", "")
    if is_neech_bhanga("Jupiter", sign, ctx.get("planet_map", {})):
        nb = evaluate_neech_bhanga("Jupiter", sign, ctx.get("planet_map", {}))
        return True, nb["primary_reason"]
    return False, ""


# Rule 14: 2nd House / Lord (Kutumba) Connection to 7th
def _pred_h2_kutumba_connection(ctx: dict, extra: dict) -> tuple[bool, str, list[str]]:
    hl = ctx.get("house_lords", {})
    lagna = ctx.get("lagna", "")
    l7 = hl.get(7) or safe_house_lord(lagna, 7)
    l2 = hl.get(2) or safe_house_lord(lagna, 2)
    pm = ctx.get("planet_map", {})

    l7_h = pm.get(l7, {}).get("house")
    l2_h = pm.get(l2, {}).get("house")

    if l7_h == 2:
        return True, f"7th lord {l7} in 2nd house integrates marriage with family life, lineage, and mutual wealth", [l7, "H2"]
    if l2_h == 7:
        return True, f"2nd lord {l2} in 7th house directly binds domestic wealth and lineage to marital partnership", [l2, "H7"]
    if l7_h and l2_h and l7_h == l2_h:
        return True, f"7th lord {l7} and 2nd lord {l2} conjoined in house {l7_h}", [l7, l2]
    return False, "", []


# Rule 15: 5th House / Lord (Romance) Alignment with 7th
def _pred_h5_romance_alignment(ctx: dict, extra: dict) -> tuple[bool, str, list[str]]:
    hl = ctx.get("house_lords", {})
    lagna = ctx.get("lagna", "")
    l7 = hl.get(7) or safe_house_lord(lagna, 7)
    l5 = hl.get(5) or safe_house_lord(lagna, 5)
    pm = ctx.get("planet_map", {})

    l7_h = pm.get(l7, {}).get("house")
    l5_h = pm.get(l5, {}).get("house")

    if l5_h == 7:
        return True, f"5th lord of romance {l5} in 7th house: strong alignment for affection, courtship, and emotional intimacy", [l5, "H7"]
    if l7_h == 5:
        return True, f"7th lord {l7} in 5th house of romance and creative joy", [l7, "H5"]
    if l7_h and l5_h and l7_h == l5_h:
        return True, f"7th lord {l7} and 5th lord {l5} conjoined in house {l7_h} (Kama-Trikona romantic alignment)", [l7, l5]
    return False, "", []


# Rule 16: 11th House / Lord (Fulfillment) Alignment with 7th
def _pred_h11_fulfillment_alignment(ctx: dict, extra: dict) -> tuple[bool, str, list[str]]:
    hl = ctx.get("house_lords", {})
    lagna = ctx.get("lagna", "")
    l7 = hl.get(7) or safe_house_lord(lagna, 7)
    l11 = hl.get(11) or safe_house_lord(lagna, 11)
    pm = ctx.get("planet_map", {})

    l7_h = pm.get(l7, {}).get("house")
    l11_h = pm.get(l11, {}).get("house")

    if l11_h == 7:
        return True, f"11th lord of fulfillment {l11} in 7th house: partnership fulfills personal aspirations and mutual desires", [l11, "H7"]
    if l7_h == 11:
        return True, f"7th lord {l7} in 11th house of gains and shared hopes", [l7, "H11"]
    if l7_h and l11_h and l7_h == l11_h:
        return True, f"7th lord {l7} and 11th lord {l11} conjoined in house {l7_h}", [l7, l11]
    return False, "", []


# Rule 17: Lagna Lord and 7th Lord Sambhandha
def _pred_lagna_lord_7th_lord_sambhandha(ctx: dict, extra: dict) -> tuple[bool, str, list[str]]:
    hl = ctx.get("house_lords", {})
    lagna = ctx.get("lagna", "")
    l1 = hl.get(1) or safe_house_lord(lagna, 1)
    l7 = hl.get(7) or safe_house_lord(lagna, 7)
    pm = ctx.get("planet_map", {})

    l1_h = pm.get(l1, {}).get("house")
    l7_h = pm.get(l7, {}).get("house")

    if l1 and l7 and l1 == l7:
        # Single planet rules both (e.g. Mars for Aries/Scorpio or Venus for Taurus/Libra... wait, Lagna and 7th are opposite signs so they never share the same lord in Parashari 7-planets)
        return False, "", []

    if l1_h and l7_h:
        if l1_h == l7_h:
            return True, f"Ascendant lord {l1} and 7th lord {l7} conjoined in house {l1_h} (deep mutual bond)", [l1, l7, f"H{l1_h}"]
        # Mutual aspect (7th from each other)
        if ((l7_h - l1_h) % 12) + 1 == 7:
            return True, f"Ascendant lord {l1} and 7th lord {l7} in direct mutual 7th aspect", [l1, l7]
        # Exchange (Parivartana)
        if l1_h == 7 and l7_h == 1:
            return True, f"Maha Parivartana: Lagna lord {l1} in 7th and 7th lord {l7} in Lagna", [l1, l7]
    return False, "", []


# Rule 18: Chandra Lagna Frame - Benefic in 7th from Moon
def _pred_chandra_lagna_h7(ctx: dict, extra: dict) -> tuple[bool, str, list[str]]:
    pm = ctx.get("planet_map", {})
    moon_h = pm.get("Moon", {}).get("house", 0)
    if not moon_h:
        return False, "", []
    target_h = get_house_relative(moon_h, 7)
    planets_in_target = get_planets_in_house(pm, target_h)
    benefics = [p for p in planets_in_target if p in ("Jupiter", "Venus", "Mercury")]
    if benefics:
        return True, f"Chandra Lagna frame: 7th from Moon (house {target_h}) occupied by benefic(s) {', '.join(benefics)}", benefics
    return False, "", []


# Rule 19: Chandra Lagna Frame - Malefic in 7th from Moon
def _pred_chandra_lagna_h7_malefic(ctx: dict, extra: dict) -> tuple[bool, str, list[str]]:
    pm = ctx.get("planet_map", {})
    moon_h = pm.get("Moon", {}).get("house", 0)
    if not moon_h:
        return False, "", []
    target_h = get_house_relative(moon_h, 7)
    planets_in_target = get_planets_in_house(pm, target_h)
    malefics = [p for p in planets_in_target if p in ("Sun", "Mars", "Saturn", "Rahu", "Ketu")]
    benefics = [p for p in planets_in_target if p in NATURAL_BENEFICS]
    if malefics and not benefics:
        return True, f"Chandra Lagna frame: 7th from Moon (house {target_h}) occupied by malefic(s) {', '.join(malefics)}", malefics
    return False, "", []


# Rule 20: Kalatrakaraka Venus Frame - 7th from Venus
def _pred_venus_frame_h7(ctx: dict, extra: dict) -> tuple[bool, str, list[str]]:
    pm = ctx.get("planet_map", {})
    venus_h = pm.get("Venus", {}).get("house", 0)
    if not venus_h:
        return False, "", []
    target_h = get_house_relative(venus_h, 7)
    planets_in_target = get_planets_in_house(pm, target_h)
    strong_planets = [
        p for p in planets_in_target
        if p in ("Jupiter", "Mercury", "Moon", "Sun") and pm.get(p, {}).get("str_score", 0) >= 0
    ]
    if strong_planets:
        return True, f"Venus frame: 7th from Venus (house {target_h}) occupied by supportive planet(s) {', '.join(strong_planets)}", strong_planets
    return False, "", []


# Rule 21: D9 Navamsa 7th Lord Dignity
def _pred_d9_7th_lord_dignity(ctx: dict, extra: dict) -> tuple[bool, str, list[str]]:
    hl = ctx.get("house_lords", {})
    lagna = ctx.get("lagna", "")
    l7 = hl.get(7) or safe_house_lord(lagna, 7)
    pm = ctx.get("planet_map", {})
    l7_p = pm.get(l7, {})
    sign = l7_p.get("sign", "")
    deg = float(l7_p.get("degree", 0.0))

    if not sign:
        return False, "", []

    d9_sign = calculate_d9_navamsa_sign(sign, deg)
    if d9_sign == EXALTATION.get(l7) or d9_sign in OWN_SIGNS.get(l7, []):
        return True, f"D9 Navamsa frame: D1 7th lord {l7} achieves dignity in Navamsa sign {d9_sign}", [l7, d9_sign]
    return False, "", []


# Rule 22: D9 Navamsa Lagna Benefic Occupation / Lordship
def _pred_d9_navamsa_lagna_benefic(ctx: dict, extra: dict) -> tuple[bool, str, list[str]]:
    # Requires D9 Lagna sign if present in extra or calculates from lagna degree
    d9_lagna_sign = extra.get("d9_navamsa_lagna_sign") or ctx.get("d9_lagna")
    if not d9_lagna_sign:
        lagna_deg = float(ctx.get("lagna_degree", 0.0))
        lagna_sign = ctx.get("lagna", "")
        if not lagna_sign:
            return False, "", []
        d9_lagna_sign = calculate_d9_navamsa_sign(lagna_sign, lagna_deg)
    d9_lagna_lord = SIGN_LORDS.get(d9_lagna_sign, "")
    if d9_lagna_lord in ("Jupiter", "Venus", "Mercury"):
        return True, f"D9 Navamsa Lagna is ruled by natural benefic {d9_lagna_lord} ({d9_lagna_sign})", [d9_lagna_lord, d9_lagna_sign]
    return False, "", []


# Rule 23: Multi-Frame Mangal Dosha Check
def _pred_mangal_dosha_multiframe(ctx: dict, extra: dict) -> tuple[bool, str, list[str]]:
    pm = ctx.get("planet_map", {})
    lagna = ctx.get("lagna", "")
    if not lagna or "Mars" not in pm:
        return False, "", []

    # Run WP4 multi-frame evaluation
    res = evaluate_mangal_dosha_multiframe(pm, lagna)
    has_dosha_raw = res.get("raw", False) or any(
        f.get("raw", False) for f in res.get("frames", {}).values()
    )
    if has_dosha_raw:
        afflicted_frames = [f for f, d in res.get("frames", {}).items() if d.get("raw")]
        extra["mangal_dosha_result"] = res
        return True, f"Multi-frame Mangal Dosha detected across frames: {', '.join(afflicted_frames)}", afflicted_frames
    return False, "", []

def _exc_mangal_dosha_cancelled(ctx: dict, extra: dict) -> tuple[bool, str]:
    res = extra.get("mangal_dosha_result")
    if not res:
        pm = ctx.get("planet_map", {})
        lagna = ctx.get("lagna", "")
        if not lagna or "Mars" not in pm:
            return False, ""
        res = evaluate_mangal_dosha_multiframe(pm, lagna)

    if res.get("overall_cancelled") or res.get("all_cancellation_reasons"):
        reasons = res.get("all_cancellation_reasons", [])
        return True, f"Mangal Dosha cancelled by classical rules: {', '.join(reasons[:2])}"
    return False, ""



# Rule 24: Timing - Dasha Activation of 7th House
def _pred_marriage_timing_dasha(ctx: dict, extra: dict) -> tuple[bool, str, list[str]]:
    hl = ctx.get("house_lords", {})
    lagna = ctx.get("lagna", "")
    l7 = hl.get(7) or safe_house_lord(lagna, 7)
    pm = ctx.get("planet_map", {})
    h7_planets = get_planets_in_house(pm, 7)

    md = ctx.get("mahadasha", "")
    ad = ctx.get("antardasha", "")

    active = set()
    if md in h7_planets or md == l7 or md == "Venus":
        active.add(f"MD: {md}")
    if ad in h7_planets or ad == l7 or ad == "Venus":
        active.add(f"AD: {ad}")

    if active:
        return True, f"Current Dasha period ({', '.join(active)}) directly activates marriage/relationship houses", list(active)
    return False, "", []


# Rule 25: Jaimini Darakaraka in Kendra (Pending WP7 Dependency)
def _pred_jaimini_darakaraka_pending(ctx: dict, extra: dict) -> tuple[bool, str, list[str]]:
    # Stubbed pending WP7 implementation
    return False, "Pending WP7 Jaimini implementation", []


# Rule 26: Jaimini Upapada Lagna Benefic (Pending WP7 Dependency)
def _pred_jaimini_upapada_pending(ctx: dict, extra: dict) -> tuple[bool, str, list[str]]:
    # Stubbed pending WP7 implementation
    return False, "Pending WP7 Jaimini implementation", []


# ---------------------------------------------------------------------------
# Canonical Marriage Rules Catalog (26 Rules)
# ---------------------------------------------------------------------------

MARRIAGE_RULES_CATALOG: list[MarriageRule] = [
    # Family A: 7th House & 7th Lord in D1
    MarriageRule(
        rule_id="MARRIAGE-H7-LORD-KENDRA-01",
        version="1.0.0",
        domain="marriage",
        profile="parashari",
        chart_frame="D1",
        predicate=_pred_h7_lord_kendra,
        ordered_exceptions=[_exc_h7_debilitated_no_nb],
        dedupe_key="H7_LORD_PLACEMENT",
        effect="SUPPORTS",
        birth_time_sensitive=False,
        explanation_template="7th lord placed in a Kendra house confers relational stability, social recognition of marriage, and an enduring life partnership.",
        source_family="BPHS",
        source_reference="BPHS Ch. 24, v. 73-74",
        source_status="VERIFIED",
        review_status="ACCEPTED",
        confidence="HIGH",
        archetypes=["Harmony & Devotion"],
    ),
    MarriageRule(
        rule_id="MARRIAGE-H7-LORD-TRIKONA-02",
        version="1.0.0",
        domain="marriage",
        profile="parashari",
        chart_frame="D1",
        predicate=_pred_h7_lord_trikona,
        ordered_exceptions=[_exc_h7_debilitated_no_nb],
        dedupe_key="H7_LORD_PLACEMENT",
        effect="SUPPORTS",
        birth_time_sensitive=False,
        explanation_template="7th lord in a Trikona (5th/9th) infuses marriage with mutual respect, spiritual fortune, romantic courtship, and shared dharma.",
        source_family="BPHS",
        source_reference="BPHS Ch. 24, v. 77-78",
        source_status="VERIFIED",
        review_status="ACCEPTED",
        confidence="HIGH",
        archetypes=["Harmony & Devotion", "Romantic Courtship & Passion"],
    ),
    MarriageRule(
        rule_id="MARRIAGE-H7-LORD-DUSTHANA-03",
        version="1.0.0",
        domain="marriage",
        profile="parashari",
        chart_frame="D1",
        predicate=_pred_h7_lord_dusthana,
        ordered_exceptions=[_exc_h7_dusthana_own_or_exalted],
        dedupe_key="H7_LORD_PLACEMENT",
        effect="OBSTRUCTS",
        birth_time_sensitive=False,
        explanation_template="7th lord placed in a Dusthana house (6, 8, 12) suggests temperamental friction, periods of emotional distance, or partner health adjustments requiring patience.",
        source_family="BPHS",
        source_reference="BPHS Ch. 24, v. 79-81",
        source_status="VERIFIED",
        review_status="ACCEPTED",
        confidence="HIGH",
        archetypes=["Growth Through Effort & Adjustment"],
    ),
    MarriageRule(
        rule_id="MARRIAGE-H7-LORD-EXALTED-OWN-04",
        version="1.0.0",
        domain="marriage",
        profile="parashari",
        chart_frame="D1",
        predicate=_pred_h7_lord_exalted_own,
        ordered_exceptions=[],
        dedupe_key="H7_LORD_DIGNITY",
        effect="SUPPORTS",
        birth_time_sensitive=False,
        explanation_template="7th lord in peak dignity (exalted or in own sign) indicates an accomplished, devoted, and supportive partner with high social integrity.",
        source_family="Phaladeepika",
        source_reference="Phaladeepika Ch. 15, v. 10",
        source_status="VERIFIED",
        review_status="ACCEPTED",
        confidence="HIGH",
        archetypes=["Harmony & Devotion"],
    ),
    MarriageRule(
        rule_id="MARRIAGE-H7-LORD-DEBILITATED-05",
        version="1.0.0",
        domain="marriage",
        profile="parashari",
        chart_frame="D1",
        predicate=_pred_h7_lord_debilitated,
        ordered_exceptions=[_exc_h7_neech_bhanga],
        dedupe_key="H7_LORD_DIGNITY",
        effect="OBSTRUCTS",
        birth_time_sensitive=False,
        explanation_template="7th lord in debilitation can bring partnership vulnerabilities, mismatched expectations, or relational sacrifices unless redeemed by Neecha Bhanga.",
        source_family="Phaladeepika",
        source_reference="Phaladeepika Ch. 15, v. 11",
        source_status="VERIFIED",
        review_status="ACCEPTED",
        confidence="HIGH",
        archetypes=["Growth Through Effort & Adjustment"],
    ),
    MarriageRule(
        rule_id="MARRIAGE-H7-BENEFIC-OCCUPATION-06",
        version="1.0.0",
        domain="marriage",
        profile="parashari",
        chart_frame="D1",
        predicate=_pred_h7_benefic_occupation,
        ordered_exceptions=[],
        dedupe_key="H7_BENEFIC",
        effect="SUPPORTS",
        birth_time_sensitive=False,
        explanation_template="Unblemished natural benefic in the 7th house bestows genuine affection, cultural refinement, and tender interpersonal communication.",
        source_family="BPHS",
        source_reference="BPHS Ch. 24; Phaladeepika Ch. 15, v. 12",
        source_status="VERIFIED",
        review_status="ACCEPTED",
        confidence="HIGH",
        archetypes=["Harmony & Devotion", "Romantic Courtship & Passion"],
    ),
    MarriageRule(
        rule_id="MARRIAGE-H7-MALEFIC-OCCUPATION-07",
        version="1.0.0",
        domain="marriage",
        profile="parashari",
        chart_frame="D1",
        predicate=_pred_h7_malefic_occupation,
        ordered_exceptions=[_exc_h7_malefic_in_dignity],
        dedupe_key="H7_MALEFIC",
        effect="CONDITIONAL",
        birth_time_sensitive=False,
        explanation_template="Natural malefic in the 7th house demands mutual patience and maturity to resolve assertive egos or differing personal philosophies.",
        source_family="BPHS",
        source_reference="BPHS Ch. 24; Phaladeepika Ch. 15, v. 13",
        source_status="VERIFIED",
        review_status="ACCEPTED",
        confidence="MEDIUM",
        archetypes=["Growth Through Effort & Adjustment", "Transformative & Independent Dynamic"],
    ),
    MarriageRule(
        rule_id="MARRIAGE-H7-PAPAKARTARI-08",
        version="1.0.0",
        domain="marriage",
        profile="parashari",
        chart_frame="D1",
        predicate=_pred_h7_papakartari,
        ordered_exceptions=[_exc_kartari_h7_relief],
        dedupe_key="H7_KARTARI",
        effect="OBSTRUCTS",
        birth_time_sensitive=False,
        explanation_template="7th house hemmed between natural malefics in 6th and 8th produces relational constriction, external stress, or feeling misunderstood by in-laws.",
        source_family="Jataka Parijata",
        source_reference="Classical Jataka Kartari principles",
        source_status="VERIFIED",
        review_status="ACCEPTED",
        confidence="MEDIUM",
        archetypes=["Growth Through Effort & Adjustment"],
    ),

    # Family B: Significators (Venus & Jupiter)
    MarriageRule(
        rule_id="MARRIAGE-KARAKA-VENUS-DIGNITY-09",
        version="1.0.0",
        domain="marriage",
        profile="parashari",
        chart_frame="D1",
        predicate=_pred_karaka_venus_dignity,
        ordered_exceptions=[],
        dedupe_key="VENUS_DIGNITY",
        effect="SUPPORTS",
        birth_time_sensitive=False,
        explanation_template="Venus in high dignity (exalted or in own sign) grants exquisite aesthetic harmony, emotional generosity, and deep romantic devotion.",
        source_family="Phaladeepika",
        source_reference="Phaladeepika Ch. 15, v. 14",
        source_status="VERIFIED",
        review_status="ACCEPTED",
        confidence="HIGH",
        archetypes=["Harmony & Devotion", "Romantic Courtship & Passion"],
    ),
    MarriageRule(
        rule_id="MARRIAGE-KARAKA-VENUS-DEBILITATED-10",
        version="1.0.0",
        domain="marriage",
        profile="parashari",
        chart_frame="D1",
        predicate=_pred_karaka_venus_debilitated,
        ordered_exceptions=[_exc_venus_neech_bhanga],
        dedupe_key="VENUS_DIGNITY",
        effect="OBSTRUCTS",
        birth_time_sensitive=False,
        explanation_template="Venus in Kanya (debilitation) can cause overcritical emotional attitudes or dissatisfaction with romantic reality unless cancelled.",
        source_family="Phaladeepika",
        source_reference="Phaladeepika Ch. 15, v. 15",
        source_status="VERIFIED",
        review_status="ACCEPTED",
        confidence="HIGH",
        archetypes=["Growth Through Effort & Adjustment"],
    ),
    MarriageRule(
        rule_id="MARRIAGE-KARAKA-VENUS-COMBUST-11",
        version="1.0.0",
        domain="marriage",
        profile="parashari",
        chart_frame="D1",
        predicate=_pred_karaka_venus_combust,
        ordered_exceptions=[],
        dedupe_key="VENUS_COMBUSTION",
        effect="CONDITIONAL",
        birth_time_sensitive=False,
        explanation_template="Combustion of Venus indicates ego dynamics or strong individual will that can temporarily eclipse romantic accommodation.",
        source_family="BPHS",
        source_reference="BPHS Ch. 3 (Combustion Sutras)",
        source_status="VERIFIED",
        review_status="ACCEPTED",
        confidence="MEDIUM",
        archetypes=["Growth Through Effort & Adjustment"],
    ),
    MarriageRule(
        rule_id="MARRIAGE-KARAKA-JUPITER-BENEFIC-12",
        version="1.0.0",
        domain="marriage",
        profile="parashari",
        chart_frame="D1",
        predicate=_pred_karaka_jupiter_benefic,
        ordered_exceptions=[],
        dedupe_key="JUPITER_BENEFIC_H7",
        effect="SUPPORTS",
        birth_time_sensitive=False,
        explanation_template="Jupiter's auspicious influence on the 7th house or its lord secures moral integrity, mutual reverence, and wise counsel in matrimonial life.",
        source_family="BPHS",
        source_reference="BPHS Ch. 24",
        source_status="VERIFIED",
        review_status="ACCEPTED",
        confidence="HIGH",
        archetypes=["Harmony & Devotion", "Familial Cohesion & Tradition"],
    ),
    MarriageRule(
        rule_id="MARRIAGE-KARAKA-JUPITER-DEBILITATED-13",
        version="1.0.0",
        domain="marriage",
        profile="parashari",
        chart_frame="D1",
        predicate=_pred_karaka_jupiter_debilitated,
        ordered_exceptions=[_exc_jupiter_neech_bhanga],
        dedupe_key="JUPITER_DIGNITY",
        effect="CONDITIONAL",
        birth_time_sensitive=False,
        explanation_template="Jupiter in Makara (debilitation) counsels against excessive rigidity or ideological expectations within partnership.",
        source_family="Phaladeepika",
        source_reference="Phaladeepika Ch. 8",
        source_status="VERIFIED",
        review_status="ACCEPTED",
        confidence="MEDIUM",
        archetypes=["Growth Through Effort & Adjustment"],
    ),

    # Family C: Supporting Houses
    MarriageRule(
        rule_id="MARRIAGE-H2-KUTUMBA-CONNECTION-14",
        version="1.0.0",
        domain="marriage",
        profile="parashari",
        chart_frame="D1",
        predicate=_pred_h2_kutumba_connection,
        ordered_exceptions=[],
        dedupe_key="H2_H7_LINK",
        effect="SUPPORTS",
        birth_time_sensitive=False,
        explanation_template="Connection between 2nd house of family/wealth and 7th house cements matrimonial integration into domestic lineage and mutual assets.",
        source_family="BPHS",
        source_reference="BPHS Ch. 24 (Kutumba Sthana)",
        source_status="VERIFIED",
        review_status="ACCEPTED",
        confidence="HIGH",
        archetypes=["Familial Cohesion & Tradition"],
    ),
    MarriageRule(
        rule_id="MARRIAGE-H5-ROMANCE-ALIGNMENT-15",
        version="1.0.0",
        domain="marriage",
        profile="parashari",
        chart_frame="D1",
        predicate=_pred_h5_romance_alignment,
        ordered_exceptions=[],
        dedupe_key="H5_H7_LINK",
        effect="SUPPORTS",
        birth_time_sensitive=False,
        explanation_template="Alignment between 5th lord (romance/courtship) and 7th house highlights genuine emotional intimacy, mutual adoration, and romantic courtship.",
        source_family="BPHS",
        source_reference="BPHS Ch. 24",
        source_status="VERIFIED",
        review_status="ACCEPTED",
        confidence="HIGH",
        archetypes=["Romantic Courtship & Passion"],
    ),
    MarriageRule(
        rule_id="MARRIAGE-H11-FULFILLMENT-ALIGNMENT-16",
        version="1.0.0",
        domain="marriage",
        profile="parashari",
        chart_frame="D1",
        predicate=_pred_h11_fulfillment_alignment,
        ordered_exceptions=[],
        dedupe_key="H11_H7_LINK",
        effect="SUPPORTS",
        birth_time_sensitive=False,
        explanation_template="Association of 11th lord (desire fulfillment/friendship) with 7th house makes marriage a foundation for shared dreams and enduring camaraderie.",
        source_family="BPHS",
        source_reference="BPHS Ch. 24",
        source_status="VERIFIED",
        review_status="ACCEPTED",
        confidence="HIGH",
        archetypes=["Harmony & Devotion"],
    ),
    MarriageRule(
        rule_id="MARRIAGE-LAGNA-LORD-7TH-LORD-17",
        version="1.0.0",
        domain="marriage",
        profile="parashari",
        chart_frame="D1",
        predicate=_pred_lagna_lord_7th_lord_sambhandha,
        ordered_exceptions=[],
        dedupe_key="L1_L7_SAMBHANDHA",
        effect="SUPPORTS",
        birth_time_sensitive=False,
        explanation_template="Direct connection between Ascendant lord (self) and 7th lord (partner) creates an exceptional natural magnetism and mutual understanding.",
        source_family="BPHS",
        source_reference="BPHS Ch. 24, v. 75",
        source_status="VERIFIED",
        review_status="ACCEPTED",
        confidence="HIGH",
        archetypes=["Harmony & Devotion", "Romantic Courtship & Passion"],
    ),

    # Family D: Multi-Frame Cross-Readings
    MarriageRule(
        rule_id="MARRIAGE-CHANDRA-LAGNA-H7-18",
        version="1.0.0",
        domain="marriage",
        profile="parashari",
        chart_frame="Chandra_Lagna",
        predicate=_pred_chandra_lagna_h7,
        ordered_exceptions=[],
        dedupe_key="CHANDRA_H7_BENEFIC",
        effect="SUPPORTS",
        birth_time_sensitive=False,
        explanation_template="7th house counted from Moon (Chandra Lagna) occupied by benefics ensures emotional peace, mental compatibility, and intuitive empathy.",
        source_family="Phaladeepika",
        source_reference="Phaladeepika Ch. 15, v. 16",
        source_status="VERIFIED",
        review_status="ACCEPTED",
        confidence="HIGH",
        archetypes=["Harmony & Devotion"],
    ),
    MarriageRule(
        rule_id="MARRIAGE-CHANDRA-LAGNA-H7-MALEFIC-19",
        version="1.0.0",
        domain="marriage",
        profile="parashari",
        chart_frame="Chandra_Lagna",
        predicate=_pred_chandra_lagna_h7_malefic,
        ordered_exceptions=[],
        dedupe_key="CHANDRA_H7_MALEFIC",
        effect="CONDITIONAL",
        birth_time_sensitive=False,
        explanation_template="7th house from Moon occupied by unassisted malefics points to emotional sensitivity and differing psychological tempos that require mindful communication.",
        source_family="Phaladeepika",
        source_reference="Phaladeepika Ch. 15",
        source_status="VERIFIED",
        review_status="ACCEPTED",
        confidence="MEDIUM",
        archetypes=["Growth Through Effort & Adjustment"],
    ),
    MarriageRule(
        rule_id="MARRIAGE-VENUS-FRAME-H7-20",
        version="1.0.0",
        domain="marriage",
        profile="parashari",
        chart_frame="Venus_Frame",
        predicate=_pred_venus_frame_h7,
        ordered_exceptions=[],
        dedupe_key="VENUS_H7",
        effect="SUPPORTS",
        birth_time_sensitive=False,
        explanation_template="7th house from Venus (Kalatrakaraka Lagna) occupied by supportive planets solidifies romantic contentment and joyful companionship.",
        source_family="Saravali",
        source_reference="Saravali Kalatra Adhyaya",
        source_status="VERIFIED",
        review_status="ACCEPTED",
        confidence="HIGH",
        archetypes=["Romantic Courtship & Passion", "Harmony & Devotion"],
    ),

    # Family E: D9 Navamsa & Timing
    MarriageRule(
        rule_id="MARRIAGE-D9-7TH-LORD-DIGNITY-21",
        version="1.0.0",
        domain="marriage",
        profile="parashari",
        chart_frame="D9",
        predicate=_pred_d9_7th_lord_dignity,
        ordered_exceptions=[],
        dedupe_key="D9_7TH_LORD",
        effect="SUPPORTS",
        birth_time_sensitive=True,
        explanation_template="7th lord occupying an exalted or own sign in D9 Navamsa confirms profound inner spiritual resilience and marital longevity.",
        source_family="BPHS",
        source_reference="BPHS Ch. 6; Phaladeepika Ch. 15",
        source_status="VERIFIED",
        review_status="ACCEPTED",
        confidence="HIGH",
        archetypes=["Harmony & Devotion"],
    ),
    MarriageRule(
        rule_id="MARRIAGE-D9-NAVAMSA-LAGNA-BENEFIC-22",
        version="1.0.0",
        domain="marriage",
        profile="parashari",
        chart_frame="D9",
        predicate=_pred_d9_navamsa_lagna_benefic,
        ordered_exceptions=[],
        dedupe_key="D9_LAGNA_BENEFIC",
        effect="SUPPORTS",
        birth_time_sensitive=True,
        explanation_template="D9 Navamsa Lagna ruled by a natural benefic bestows internal grace, dignified compromise, and mutual auspiciousness in union.",
        source_family="BPHS",
        source_reference="BPHS Ch. 6 (Navamsa Phala)",
        source_status="VERIFIED",
        review_status="ACCEPTED",
        confidence="MEDIUM",
        archetypes=["Harmony & Devotion"],
    ),
    MarriageRule(
        rule_id="MARRIAGE-MANGAL-DOSHA-MULTIFRAME-23",
        version="1.0.0",
        domain="marriage",
        profile="parashari",
        chart_frame="D1",
        predicate=_pred_mangal_dosha_multiframe,
        ordered_exceptions=[_exc_mangal_dosha_cancelled],
        dedupe_key="MANGAL_DOSHA",
        effect="CONDITIONAL",
        birth_time_sensitive=False,
        explanation_template="Multi-frame Mangal Dosha (Mars in 1, 4, 7, 8, 12 from Lagna, Moon, or Venus) counsels constructive channeling of assertive passion in partnership.",
        source_family="BPHS",
        source_reference="BPHS Ch. 81; Brihat Jataka",
        source_status="VERIFIED",
        review_status="ACCEPTED",
        confidence="HIGH",
        archetypes=["Growth Through Effort & Adjustment", "Transformative & Independent Dynamic"],
    ),
    MarriageRule(
        rule_id="MARRIAGE-TIMING-DASHA-ACTIVATION-24",
        version="1.0.0",
        domain="marriage",
        profile="parashari",
        chart_frame="D1",
        predicate=_pred_marriage_timing_dasha,
        ordered_exceptions=[],
        dedupe_key="TIMING_DASHA",
        effect="CONDITIONAL",
        birth_time_sensitive=False,
        explanation_template="Current Vimshottari Mahadasha or Antardasha connected to 7th house, 7th lord, or Venus brings partnership themes to the active forefront.",
        source_family="Parashari Timing",
        source_reference="BPHS Dasha Phala Adhyaya",
        source_status="VERIFIED",
        review_status="ACCEPTED",
        confidence="HIGH",
        archetypes=[],
    ),

    # Family F: Pending Jaimini Dependencies (Registered, Disabled)
    MarriageRule(
        rule_id="MARRIAGE-JAIMINI-DARAKARAKA-KENDRA-25",
        version="1.0.0",
        domain="marriage",
        profile="jaimini",
        chart_frame="D1",
        predicate=_pred_jaimini_darakaraka_pending,
        ordered_exceptions=[],
        dedupe_key="DARAKARAKA_KENDRA",
        effect="SUPPORTS",
        birth_time_sensitive=False,
        explanation_template="Jaimini Darakaraka (planet with lowest longitude) placed in Kendra/Trikona indicates high relational fulfillment (Pending WP7).",
        source_family="Jaimini Sutras",
        source_reference="Jaimini Upadesha Sutras 1.2",
        source_status="SOURCE VERIFICATION REQUIRED",
        review_status="PENDING_WP7_DEPENDENCY",
        confidence="LOW, needs expert check",
        archetypes=["Harmony & Devotion"],
        enabled_by_default=False,
    ),
    MarriageRule(
        rule_id="MARRIAGE-JAIMINI-UPAPADA-BENEFIC-26",
        version="1.0.0",
        domain="marriage",
        profile="jaimini",
        chart_frame="D1",
        predicate=_pred_jaimini_upapada_pending,
        ordered_exceptions=[],
        dedupe_key="UPAPADA_BENEFIC",
        effect="SUPPORTS",
        birth_time_sensitive=True,
        explanation_template="Upapada Lagna (Arudha of 12th house) aspected or occupied by benefics protects longevity and harmony of marriage (Pending WP7).",
        source_family="Jaimini Sutras",
        source_reference="Jaimini Upadesha Sutras 1.4",
        source_status="SOURCE VERIFICATION REQUIRED",
        review_status="PENDING_WP7_DEPENDENCY",
        confidence="LOW, needs expert check",
        archetypes=["Familial Cohesion & Tradition"],
        enabled_by_default=False,
    ),
]


# ---------------------------------------------------------------------------
# Evaluator Engine
# ---------------------------------------------------------------------------

def evaluate_marriage_rules(ctx: dict) -> dict:
    """
    Evaluate all canonical marriage rules against canonical ChartContext.
    Returns:
      - matched_rules: list of fired rules with reasons, tokens, effect, and metadata
      - rejected_rules: list of rules rejected by exceptions with reasons
      - archetype_weights: dictionary of relational dynamic archetype scores
      - primary_archetypes: top relational dynamic archetypes sorted by evidence
      - supports_count: count of supporting rules
      - obstructs_count: count of obstructing rules
      - conditional_count: count of conditional rules
      - d9_7th_lord_sign: sign of D1 7th lord in D9 Navamsa
      - d9_navamsa_lagna_sign: D9 Navamsa Lagna sign
      - summary_score: normalized evidence vitality score (25 to 95)
      - birth_time_sensitive_count: count of active rules depending on birth-time stability
      - pending_dependencies_count: count of catalog rules pending external packages (WP7)
    """
    matched = []
    rejected = []
    seen_dedupe_keys = {}

    archetype_scores = {arc: 0 for arc in RELATION_ARCHETYPES}
    supports_count = 0
    obstructs_count = 0
    conditional_count = 0

    extra = {}
    pm = ctx.get("planet_map", {})
    lagna_sign = ctx.get("lagna", "")
    lagna_deg = float(ctx.get("lagna_degree", 0.0))
    extra["d9_navamsa_lagna_sign"] = (
        ctx.get("d9_lagna")
        or (calculate_d9_navamsa_sign(lagna_sign, lagna_deg) if lagna_sign else "")
    )

    for rule in MARRIAGE_RULES_CATALOG:
        # Skip disabled rules (e.g. pending WP7 dependencies)
        if not rule.enabled_by_default:
            continue

        is_hit, reason, tokens = rule.predicate(ctx, extra)
        if not is_hit:
            continue

        # Evaluate ordered exceptions
        exception_fired = False
        exception_reason = ""
        for exc_fn in rule.ordered_exceptions:
            exc_hit, exc_msg = exc_fn(ctx, extra)
            if exc_hit:
                exception_fired = True
                exception_reason = exc_msg
                break

        if exception_fired:
            rejected.append({
                "rule_id": rule.rule_id,
                "version": rule.version,
                "reason": reason,
                "cancellation_reason": exception_reason,
                "source_reference": rule.source_reference,
            })
            continue

        # Deduplication check
        if rule.dedupe_key:
            if rule.dedupe_key in seen_dedupe_keys:
                continue
            seen_dedupe_keys[rule.dedupe_key] = rule.confidence

        if rule.effect == "SUPPORTS":
            supports_count += 1
            for arc in rule.archetypes:
                archetype_scores[arc] += 2
        elif rule.effect == "OBSTRUCTS":
            obstructs_count += 1
            for arc in rule.archetypes:
                archetype_scores[arc] += 1
        elif rule.effect == "CONDITIONAL":
            conditional_count += 1
            for arc in rule.archetypes:
                archetype_scores[arc] += 1

        matched.append({
            "rule_id": rule.rule_id,
            "version": rule.version,
            "domain": rule.domain,
            "profile": rule.profile,
            "chart_frame": rule.chart_frame,
            "effect": rule.effect,
            "confidence": rule.confidence,
            "reason": reason,
            "tokens": tokens,
            "explanation": rule.explanation_template,
            "source_family": rule.source_family,
            "source_reference": rule.source_reference,
            "source_status": rule.source_status,
            "birth_time_sensitive": rule.birth_time_sensitive,
            "archetypes": rule.archetypes,
        })

    # Sort archetypes by score descending
    sorted_archetypes = sorted(
        [{"archetype": k, "weight": v} for k, v in archetype_scores.items() if v > 0],
        key=lambda x: x["weight"],
        reverse=True
    )

    # Compute a balanced astrological evidence vitality score (25 to 95)
    raw_score = 50 + (supports_count * 6) - (obstructs_count * 6) + (conditional_count * 2)
    normalized_score = max(25, min(95, raw_score))

    # D9 sign of 7th lord
    hl = ctx.get("house_lords", {})
    l7 = hl.get(7) or safe_house_lord(lagna_sign, 7)
    l7_p = pm.get(l7, {})
    l7_d9_sign = calculate_d9_navamsa_sign(l7_p.get("sign", ""), float(l7_p.get("degree", 0.0))) if l7_p else ""

    return {
        "domain": "marriage",
        "score": normalized_score,
        "matched_rules": matched,
        "rejected_rules": rejected,
        "supports_count": supports_count,
        "obstructs_count": obstructs_count,
        "conditional_count": conditional_count,
        "archetype_scores": archetype_scores,
        "primary_archetypes": sorted_archetypes,
        "d9_7th_lord_sign": l7_d9_sign,
        "d9_navamsa_lagna_sign": extra.get("d9_navamsa_lagna_sign", ""),
        "birth_time_sensitive_count": sum(1 for r in matched if r["birth_time_sensitive"]),
        "pending_dependencies_count": sum(1 for r in MARRIAGE_RULES_CATALOG if not r.enabled_by_default),
    }
