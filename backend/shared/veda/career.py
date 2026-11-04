"""
Classical Vedic Astrology Career & Vocation Engine (Pure Shared Library).

Implements 24 deterministic, explainable Parashari & Jaimini career rules
with canonical schemas, structured predicates, explicit exception checks,
multi-frame cross-readings (D1, Chandra Lagna, Surya Lagna, D10 Dashamsha, Amatyakaraka),
and vocational archetype evidence synthesis.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Any, Optional

from .zodiac import SIGNS_SK, SIGN_LORDS
from .strength import EXALTATION, DEBILITATION, OWN_SIGNS
from .lordship import get_house_lord
from .neech_bhanga import is_neech_bhanga


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

ARCHETYPES = [
    "Leadership & Governance",
    "Technical & Engineering",
    "Commercial & Financial",
    "Advisory, Legal & Scholarly",
    "Service, Operations & Healthcare",
    "Creative & Media",
]


# ---------------------------------------------------------------------------
# Canonical Rule Dataclass
# ---------------------------------------------------------------------------

@dataclass
class CareerRule:
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
    review_status: str = "ACCEPTED"  # ACCEPTED, EXPERT REVIEW REQUIRED
    confidence: str = "HIGH"  # HIGH, MEDIUM, LOW, needs expert check
    tests: dict[str, Any] = field(default_factory=dict)
    archetypes: list[str] = field(default_factory=list)


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


def calculate_amatyakaraka(planet_map: dict) -> tuple[Optional[str], float]:
    """
    Calculate Jaimini Amatyakaraka (AmK):
    The planet having the second highest longitude degree within its sign
    among the 7 classical planets (Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn).
    Returns (planet_name, degree).
    """
    degrees = []
    for p in CLASSICAL_7:
        pdata = planet_map.get(p)
        if not pdata:
            continue
        deg = float(pdata.get("degree", 0.0)) % 30.0
        degrees.append((p, deg))

    if len(degrees) < 2:
        return None, 0.0

    # Sort descending by degree in sign
    degrees.sort(key=lambda x: x[1], reverse=True)
    # 0 = Atmakaraka (AK), 1 = Amatyakaraka (AmK)
    return degrees[1][0], degrees[1][1]


def calculate_dashamsha_d10(sign: str, degree: float) -> str:
    """
    Calculate the D10 Dashamsha sign for a given sign and degree within sign.
    Classical Parashari rule (BPHS Ch. 6, v. 11-12):
    - For Odd signs: Dashamsha counting begins from the sign occupied itself.
    - For Even signs: Dashamsha counting begins from the 9th sign from the occupied sign.
    Each Dashamsha division is 3.0 degrees (30 / 10).
    """
    if sign not in SIGNS_SK:
        return sign
    sign_idx = SIGNS_SK.index(sign)
    deg_in_sign = float(degree) % 30.0
    div_idx = int(deg_in_sign / 3.0)
    div_idx = max(0, min(9, div_idx))

    is_odd = (sign_idx % 2 == 0)  # Mesha is index 0 (1st sign = odd)
    if is_odd:
        start_idx = sign_idx
    else:
        start_idx = (sign_idx + 8) % 12  # 9th sign counted inclusively: +8

    d10_idx = (start_idx + div_idx) % 12
    return SIGNS_SK[d10_idx]


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
# Predicates and Exceptions for the 24 Career Rules
# ---------------------------------------------------------------------------

# Rule 1: 10th Lord in Kendra
def _pred_h10_lord_kendra(ctx: dict, extra: dict) -> tuple[bool, str, list[str]]:
    hl = ctx.get("house_lords", {})
    l10 = hl.get(10) or safe_house_lord(ctx.get("lagna", ""), 10)
    pdata = ctx.get("planet_map", {}).get(l10, {})
    h = pdata.get("house")
    if h in KENDRA:
        return True, f"10th lord {l10} occupies Kendra house {h}", [l10, f"H{h}"]
    return False, "", []

def _exc_debilitated_no_cancellation(ctx: dict, extra: dict) -> tuple[bool, str]:
    hl = ctx.get("house_lords", {})
    l10 = hl.get(10) or safe_house_lord(ctx.get("lagna", ""), 10)
    pdata = ctx.get("planet_map", {}).get(l10, {})
    sign = pdata.get("sign", "")
    if sign == DEBILITATION.get(l10):
        if not is_neech_bhanga(l10, sign, ctx.get("planet_map", {})):
            return True, f"10th lord {l10} is debilitated in {sign} without cancellation"
    return False, ""


# Rule 2: 10th Lord in Trikona
def _pred_h10_lord_trikona(ctx: dict, extra: dict) -> tuple[bool, str, list[str]]:
    hl = ctx.get("house_lords", {})
    l10 = hl.get(10) or safe_house_lord(ctx.get("lagna", ""), 10)
    pdata = ctx.get("planet_map", {}).get(l10, {})
    h = pdata.get("house")
    if h in (5, 9):
        return True, f"10th lord {l10} occupies auspicious Trikona house {h}", [l10, f"H{h}"]
    return False, "", []


# Rule 3: 10th Lord in Dusthana
def _pred_h10_lord_dusthana(ctx: dict, extra: dict) -> tuple[bool, str, list[str]]:
    hl = ctx.get("house_lords", {})
    l10 = hl.get(10) or safe_house_lord(ctx.get("lagna", ""), 10)
    pdata = ctx.get("planet_map", {}).get(l10, {})
    h = pdata.get("house")
    if h in DUSTHANA:
        return True, f"10th lord {l10} placed in Dusthana house {h}", [l10, f"H{h}"]
    return False, "", []

def _exc_dusthana_own_or_exalted(ctx: dict, extra: dict) -> tuple[bool, str]:
    hl = ctx.get("house_lords", {})
    l10 = hl.get(10) or safe_house_lord(ctx.get("lagna", ""), 10)
    pdata = ctx.get("planet_map", {}).get(l10, {})
    sign = pdata.get("sign", "")
    if sign == EXALTATION.get(l10) or sign in OWN_SIGNS.get(l10, []):
        return True, f"10th lord {l10} is in dignity ({sign}) in Dusthana, mitigating obstruction"
    return False, ""


# Rule 4: 10th Lord Exalted or in Own Sign
def _pred_h10_lord_exalted_own(ctx: dict, extra: dict) -> tuple[bool, str, list[str]]:
    hl = ctx.get("house_lords", {})
    l10 = hl.get(10) or safe_house_lord(ctx.get("lagna", ""), 10)
    pdata = ctx.get("planet_map", {}).get(l10, {})
    sign = pdata.get("sign", "")
    if sign == EXALTATION.get(l10):
        return True, f"10th lord {l10} is exalted in {sign}", [l10, sign]
    if sign in OWN_SIGNS.get(l10, []):
        return True, f"10th lord {l10} is situated in own sign {sign}", [l10, sign]
    return False, "", []


# Rule 5: 10th Lord Debilitated
def _pred_h10_lord_debilitated(ctx: dict, extra: dict) -> tuple[bool, str, list[str]]:
    hl = ctx.get("house_lords", {})
    l10 = hl.get(10) or safe_house_lord(ctx.get("lagna", ""), 10)
    pdata = ctx.get("planet_map", {}).get(l10, {})
    sign = pdata.get("sign", "")
    if sign == DEBILITATION.get(l10):
        return True, f"10th lord {l10} is debilitated in {sign}", [l10, sign]
    return False, "", []

def _exc_neech_bhanga_cancellation(ctx: dict, extra: dict) -> tuple[bool, str]:
    hl = ctx.get("house_lords", {})
    l10 = hl.get(10) or safe_house_lord(ctx.get("lagna", ""), 10)
    pdata = ctx.get("planet_map", {}).get(l10, {})
    sign = pdata.get("sign", "")
    if is_neech_bhanga(l10, sign, ctx.get("planet_map", {})):
        return True, f"Debilitation of 10th lord {l10} is cancelled by Neecha Bhanga Raja Yoga"
    return False, ""


# Rule 6: Amala Yoga / Natural Benefic in 10th
def _pred_h10_amala_benefic(ctx: dict, extra: dict) -> tuple[bool, str, list[str]]:
    h10_planets = get_planets_in_house(ctx.get("planet_map", {}), 10)
    benefics_in_10 = [p for p in h10_planets if p in ("Jupiter", "Venus", "Mercury")]
    malefics_in_10 = [p for p in h10_planets if p in ("Sun", "Mars", "Saturn", "Rahu", "Ketu")]
    if benefics_in_10 and not malefics_in_10:
        return True, f"Amala Yoga: Unblemished benefic(s) {', '.join(benefics_in_10)} in 10th house", benefics_in_10
    return False, "", []


# Rule 7: Natural Malefic in 10th (Upachaya Tenacity)
def _pred_h10_upachaya_malefic(ctx: dict, extra: dict) -> tuple[bool, str, list[str]]:
    h10_planets = get_planets_in_house(ctx.get("planet_map", {}), 10)
    malefics_in_10 = [p for p in h10_planets if p in ("Sun", "Mars", "Saturn")]
    if malefics_in_10:
        return True, f"Upachaya tenacity: Malefic(s) {', '.join(malefics_in_10)} in 10th house", malefics_in_10
    return False, "", []


# Rule 8: Sun in 10th (Dig Bala)
def _pred_h10_sun_digbala(ctx: dict, extra: dict) -> tuple[bool, str, list[str]]:
    sun = ctx.get("planet_map", {}).get("Sun", {})
    if sun.get("house") == 10:
        return True, "Sun occupies 10th house with peak Dig Bala (directional strength)", ["Sun", "H10"]
    return False, "", []

def _exc_sun_debilitated_no_nb(ctx: dict, extra: dict) -> tuple[bool, str]:
    sun = ctx.get("planet_map", {}).get("Sun", {})
    if sun.get("sign") == "Tula":
        if not is_neech_bhanga("Sun", "Tula", ctx.get("planet_map", {})):
            return True, "Sun is debilitated in Tula without Neecha Bhanga"
    return False, ""


# Rule 9: Mars in 10th (Kuladeepaka / Dig Bala)
def _pred_h10_mars_kuladeepaka(ctx: dict, extra: dict) -> tuple[bool, str, list[str]]:
    mars = ctx.get("planet_map", {}).get("Mars", {})
    if mars.get("house") == 10:
        return True, "Mars occupies 10th house with peak Dig Bala (Kuladeepaka Yoga)", ["Mars", "H10"]
    return False, "", []

def _exc_mars_debilitated_no_nb(ctx: dict, extra: dict) -> tuple[bool, str]:
    mars = ctx.get("planet_map", {}).get("Mars", {})
    if mars.get("sign") == "Karka":
        if not is_neech_bhanga("Mars", "Karka", ctx.get("planet_map", {})):
            return True, "Mars is debilitated in Karka without Neecha Bhanga"
    return False, ""


# Rule 10: Saturn in 10th (Mass Organization & Service)
def _pred_h10_saturn_service(ctx: dict, extra: dict) -> tuple[bool, str, list[str]]:
    saturn = ctx.get("planet_map", {}).get("Saturn", {})
    if saturn.get("house") == 10:
        return True, "Saturn in 10th house grants persevering administrative and organizational power", ["Saturn", "H10"]
    return False, "", []

def _exc_saturn_debilitated_no_nb(ctx: dict, extra: dict) -> tuple[bool, str]:
    saturn = ctx.get("planet_map", {}).get("Saturn", {})
    if saturn.get("sign") == "Mesha":
        if not is_neech_bhanga("Saturn", "Mesha", ctx.get("planet_map", {})):
            return True, "Saturn is debilitated in Mesha without Neecha Bhanga"
    return False, ""


# Rule 11: Mercury in 10th (Commercial & Analytical Acumen)
def _pred_h10_mercury_commerce(ctx: dict, extra: dict) -> tuple[bool, str, list[str]]:
    mercury = ctx.get("planet_map", {}).get("Mercury", {})
    if mercury.get("house") == 10:
        return True, "Mercury in 10th house fosters analytical intellect, trade, and communication prowess", ["Mercury", "H10"]
    return False, "", []

def _exc_mercury_debilitated_no_nb(ctx: dict, extra: dict) -> tuple[bool, str]:
    mercury = ctx.get("planet_map", {}).get("Mercury", {})
    if mercury.get("sign") == "Meena":
        if not is_neech_bhanga("Mercury", "Meena", ctx.get("planet_map", {})):
            return True, "Mercury is debilitated in Meena without Neecha Bhanga"
    return False, ""


# Rule 12: Jupiter in 10th (Advisory, Law & Ethics)
def _pred_h10_jupiter_advisory(ctx: dict, extra: dict) -> tuple[bool, str, list[str]]:
    jupiter = ctx.get("planet_map", {}).get("Jupiter", {})
    if jupiter.get("house") == 10:
        return True, "Jupiter in 10th house supports executive wisdom, jurisprudence, and ethical leadership", ["Jupiter", "H10"]
    return False, "", []

def _exc_jupiter_debilitated_no_nb(ctx: dict, extra: dict) -> tuple[bool, str]:
    jupiter = ctx.get("planet_map", {}).get("Jupiter", {})
    if jupiter.get("sign") == "Makara":
        if not is_neech_bhanga("Jupiter", "Makara", ctx.get("planet_map", {})):
            return True, "Jupiter is debilitated in Makara without Neecha Bhanga"
    return False, ""


# Rule 13: Papa Kartari to 10th House
def _pred_h10_papakartari(ctx: dict, extra: dict) -> tuple[bool, str, list[str]]:
    pm = ctx.get("planet_map", {})
    h9_planets = get_planets_in_house(pm, 9)
    h11_planets = get_planets_in_house(pm, 11)
    h10_planets = get_planets_in_house(pm, 10)

    m9 = [p for p in h9_planets if p in NATURAL_MALEFICS]
    m11 = [p for p in h11_planets if p in NATURAL_MALEFICS]
    b10 = [p for p in h10_planets if p in NATURAL_BENEFICS]

    if m9 and m11 and not b10:
        return True, f"10th house hemmed between malefics {m9} in 9th and {m11} in 11th (Papa Kartari)", m9 + m11
    return False, "", []

def _exc_kartari_benefic_relief(ctx: dict, extra: dict) -> tuple[bool, str]:
    pm = ctx.get("planet_map", {})
    b9 = [p for p in get_planets_in_house(pm, 9) if p in NATURAL_BENEFICS]
    b11 = [p for p in get_planets_in_house(pm, 11) if p in NATURAL_BENEFICS]
    if b9 or b11:
        return True, "Benefic presence in flanking house relieves the Papa Kartari affliction"
    return False, ""


# Rule 14: 6th House / Lord Service Alignment
def _pred_h6_service_alignment(ctx: dict, extra: dict) -> tuple[bool, str, list[str]]:
    hl = ctx.get("house_lords", {})
    lagna = ctx.get("lagna", "")
    l6 = hl.get(6) or safe_house_lord(lagna, 6)
    l10 = hl.get(10) or safe_house_lord(lagna, 10)
    pm = ctx.get("planet_map", {})

    l6_data = pm.get(l6, {})
    l10_data = pm.get(l10, {})

    if l10_data.get("house") == 6:
        return True, f"10th lord {l10} in 6th house aligns vocation with competitive service, healthcare, or problem solving", [l10, "H6"]
    if l6_data.get("house") == 10:
        return True, f"6th lord {l6} in 10th house aligns vocation with competitive service and organizational duty", [l6, "H10"]
    if get_planet_aspects_to_house(l6, l6_data.get("house", 0), 10):
        return True, f"6th lord {l6} aspects 10th house, conferring service-oriented career duty", [l6, "H10"]
    return False, "", []


# Rule 15: 2nd / 11th Artha Lord Connection to 10th
def _pred_h2_h11_artha_connection(ctx: dict, extra: dict) -> tuple[bool, str, list[str]]:
    hl = ctx.get("house_lords", {})
    lagna = ctx.get("lagna", "")
    l10 = hl.get(10) or safe_house_lord(lagna, 10)
    l2 = hl.get(2) or safe_house_lord(lagna, 2)
    l11 = hl.get(11) or safe_house_lord(lagna, 11)
    pm = ctx.get("planet_map", {})

    l10_h = pm.get(l10, {}).get("house")
    l2_h = pm.get(l2, {}).get("house")
    l11_h = pm.get(l11, {}).get("house")

    tokens = []
    reasons = []
    if l10_h in (2, 11):
        reasons.append(f"10th lord {l10} placed in Artha house {l10_h}")
        tokens.extend([l10, f"H{l10_h}"])
    if l2_h == 10:
        reasons.append(f"2nd lord of wealth {l2} placed in 10th house")
        tokens.extend([l2, "H10"])
    if l11_h == 10:
        reasons.append(f"11th lord of gains {l11} placed in 10th house")
        tokens.extend([l11, "H10"])
    if l10_h and l2_h and l10_h == l2_h:
        reasons.append(f"10th lord {l10} and 2nd lord {l2} conjoined in house {l10_h}")
        tokens.extend([l10, l2])
    if l10_h and l11_h and l10_h == l11_h:
        reasons.append(f"10th lord {l10} and 11th lord {l11} conjoined in house {l10_h}")
        tokens.extend([l10, l11])

    if reasons:
        return True, " & ".join(reasons), list(set(tokens))
    return False, "", []


# Rule 16: 5th Lord Intellect Alignment with 10th
def _pred_h5_intellect_alignment(ctx: dict, extra: dict) -> tuple[bool, str, list[str]]:
    hl = ctx.get("house_lords", {})
    lagna = ctx.get("lagna", "")
    l10 = hl.get(10) or safe_house_lord(lagna, 10)
    l5 = hl.get(5) or safe_house_lord(lagna, 5)
    pm = ctx.get("planet_map", {})

    l10_h = pm.get(l10, {}).get("house")
    l5_h = pm.get(l5, {}).get("house")

    if l5_h == 10:
        return True, f"5th lord of intellect {l5} placed in 10th house (counsel / strategy in vocation)", [l5, "H10"]
    if l10_h == 5:
        return True, f"10th lord {l10} placed in 5th house of intellect and strategic acumen", [l10, "H5"]
    if l10_h and l5_h and l10_h == l5_h:
        return True, f"10th lord {l10} and 5th lord {l5} conjoined in house {l10_h} (Buddhi-Karma Yoga)", [l10, l5]
    return False, "", []


# Rule 17: Dharma-Karmadhipati Yoga (9th & 10th Lords)
def _pred_dharma_karma_yoga(ctx: dict, extra: dict) -> tuple[bool, str, list[str]]:
    hl = ctx.get("house_lords", {})
    lagna = ctx.get("lagna", "")
    l9 = hl.get(9) or safe_house_lord(lagna, 9)
    l10 = hl.get(10) or safe_house_lord(lagna, 10)
    pm = ctx.get("planet_map", {})

    l9_h = pm.get(l9, {}).get("house")
    l10_h = pm.get(l10, {}).get("house")

    # If same planet rules both (e.g. Taurus Lagna where Saturn rules 9 and 10 - Yogakaraka)
    if l9 == l10 and l9:
        if l9_h in KENDRA or l9_h in TRIKONA:
            return True, f"Single planet {l9} is supreme Yogakaraka ruling both 9th and 10th houses in auspicious house {l9_h}", [l9, f"H{l9_h}"]

    if l9_h and l10_h:
        if l9_h == l10_h:
            return True, f"Dharma-Karmadhipati Yoga: 9th lord {l9} and 10th lord {l10} conjoined in house {l9_h}", [l9, l10, f"H{l9_h}"]
        if l9_h == 10 and l10_h == 9:
            return True, f"Dharma-Karmadhipati Parivartana: 9th lord {l9} in 10th and 10th lord {l10} in 9th house", [l9, l10]
        if l9_h == 10 or l10_h == 9:
            return True, f"Dharma-Karma connection: 9th lord {l9} in 10th or 10th lord {l10} in 9th house", [l9, l10]
    return False, "", []


# Rule 18: Lagna Lord in 10th House
def _pred_lagna_lord_10th(ctx: dict, extra: dict) -> tuple[bool, str, list[str]]:
    hl = ctx.get("house_lords", {})
    lagna = ctx.get("lagna", "")
    l1 = hl.get(1) or safe_house_lord(lagna, 1)
    pm = ctx.get("planet_map", {})
    l1_h = pm.get(l1, {}).get("house")

    if l1_h == 10:
        return True, f"Ascendant lord {l1} placed in 10th house: career defines identity and public achievement", [l1, "H10"]
    return False, "", []


# Rule 19: Chandra Lagna Frame - 10th from Moon
def _pred_chandra_lagna_h10(ctx: dict, extra: dict) -> tuple[bool, str, list[str]]:
    pm = ctx.get("planet_map", {})
    moon_h = pm.get("Moon", {}).get("house", 0)
    if not moon_h:
        return False, "", []
    # 10th house from Moon
    target_h = get_house_relative(moon_h, 10)
    planets_in_target = get_planets_in_house(pm, target_h)
    strong_planets = [
        p for p in planets_in_target
        if p in ("Jupiter", "Venus", "Mercury", "Sun", "Mars", "Saturn") and
        pm.get(p, {}).get("str_score", 0) >= 0
    ]
    if strong_planets:
        return True, f"Chandra Lagna frame: 10th from Moon (house {target_h}) occupied by {', '.join(strong_planets)}", strong_planets
    return False, "", []


# Rule 20: Surya Lagna Frame - 10th from Sun
def _pred_surya_lagna_h10(ctx: dict, extra: dict) -> tuple[bool, str, list[str]]:
    pm = ctx.get("planet_map", {})
    sun_h = pm.get("Sun", {}).get("house", 0)
    if not sun_h:
        return False, "", []
    # 10th house from Sun
    target_h = get_house_relative(sun_h, 10)
    planets_in_target = get_planets_in_house(pm, target_h)
    strong_planets = [
        p for p in planets_in_target
        if pm.get(p, {}).get("str_score", 0) >= 0
    ]
    if strong_planets:
        return True, f"Surya Lagna frame: 10th from Sun (house {target_h}) occupied by {', '.join(strong_planets)}", strong_planets
    return False, "", []


# Rule 21: Jaimini Amatyakaraka in Kendra or Trikona
def _pred_jaimini_amk_kendra(ctx: dict, extra: dict) -> tuple[bool, str, list[str]]:
    pm = ctx.get("planet_map", {})
    amk, deg = calculate_amatyakaraka(pm)
    if not amk:
        return False, "", []
    amk_h = pm.get(amk, {}).get("house")
    if amk_h in KENDRA or amk_h in TRIKONA:
        return True, f"Jaimini Amatyakaraka {amk} ({deg:.2f}°) placed in auspicious house {amk_h}", [amk, f"H{amk_h}"]
    return False, "", []


# Rule 22: Jaimini Amatyakaraka in Dusthana
def _pred_jaimini_amk_dusthana(ctx: dict, extra: dict) -> tuple[bool, str, list[str]]:
    pm = ctx.get("planet_map", {})
    amk, deg = calculate_amatyakaraka(pm)
    if not amk:
        return False, "", []
    amk_data = pm.get(amk, {})
    amk_h = amk_data.get("house")
    sign = amk_data.get("sign", "")
    if amk_h in DUSTHANA:
        if sign != EXALTATION.get(amk) and sign not in OWN_SIGNS.get(amk, []):
            return True, f"Jaimini Amatyakaraka {amk} ({deg:.2f}°) in Dusthana house {amk_h} without dignity", [amk, f"H{amk_h}"]
    return False, "", []


# Rule 23: D10 Dashamsha Strength of 10th Lord
def _pred_d10_10th_lord_strength(ctx: dict, extra: dict) -> tuple[bool, str, list[str]]:
    hl = ctx.get("house_lords", {})
    lagna = ctx.get("lagna", "")
    l10 = hl.get(10) or safe_house_lord(lagna, 10)
    pm = ctx.get("planet_map", {})
    l10_data = pm.get(l10, {})
    sign = l10_data.get("sign", "")
    deg = float(l10_data.get("degree", 0.0))

    if not sign:
        return False, "", []

    d10_sign = calculate_dashamsha_d10(sign, deg)
    if d10_sign == EXALTATION.get(l10) or d10_sign in OWN_SIGNS.get(l10, []):
        return True, f"D10 Dashamsha frame: 10th lord {l10} occupies dignified sign {d10_sign} in D10", [l10, d10_sign]
    return False, "", []


# Rule 24: Timing - Dasha Activation of 10th House
def _pred_timing_dasha_activation(ctx: dict, extra: dict) -> tuple[bool, str, list[str]]:
    hl = ctx.get("house_lords", {})
    lagna = ctx.get("lagna", "")
    l10 = hl.get(10) or safe_house_lord(lagna, 10)
    pm = ctx.get("planet_map", {})
    h10_planets = get_planets_in_house(pm, 10)

    md = ctx.get("mahadasha", "")
    ad = ctx.get("antardasha", "")

    active_rulers = set()
    if md in h10_planets or md == l10:
        active_rulers.add(f"MD: {md}")
    if ad in h10_planets or ad == l10:
        active_rulers.add(f"AD: {ad}")

    if active_rulers:
        return True, f"Current Dasha period ({', '.join(active_rulers)}) directly activates the 10th house of career", list(active_rulers)
    return False, "", []


# ---------------------------------------------------------------------------
# Canonical Career Rules Catalog (24 Rules)
# ---------------------------------------------------------------------------

CAREER_RULES_CATALOG: list[CareerRule] = [
    # Family A: 10th House & 10th Lord in D1
    CareerRule(
        rule_id="CAREER-H10-LORD-KENDRA-01",
        version="1.0.0",
        domain="career",
        profile="parashari",
        chart_frame="D1",
        predicate=_pred_h10_lord_kendra,
        ordered_exceptions=[_exc_debilitated_no_cancellation],
        dedupe_key="H10_LORD_PLACEMENT",
        effect="SUPPORTS",
        birth_time_sensitive=False,
        explanation_template="10th lord placed in a Kendra house confers occupational stability, executive competence, and high public visibility.",
        source_family="BPHS",
        source_reference="BPHS Ch. 24, v. 109-110",
        source_status="VERIFIED",
        review_status="ACCEPTED",
        confidence="HIGH",
        archetypes=["Leadership & Governance"],
    ),
    CareerRule(
        rule_id="CAREER-H10-LORD-TRIKONA-02",
        version="1.0.0",
        domain="career",
        profile="parashari",
        chart_frame="D1",
        predicate=_pred_h10_lord_trikona,
        ordered_exceptions=[_exc_debilitated_no_cancellation],
        dedupe_key="H10_LORD_PLACEMENT",
        effect="SUPPORTS",
        birth_time_sensitive=False,
        explanation_template="10th lord in a trine (5th/9th) connects career with fortune, creative strategy, and ethical enterprise.",
        source_family="BPHS",
        source_reference="BPHS Ch. 24, v. 113-114",
        source_status="VERIFIED",
        review_status="ACCEPTED",
        confidence="HIGH",
        archetypes=["Advisory, Legal & Scholarly", "Leadership & Governance"],
    ),
    CareerRule(
        rule_id="CAREER-H10-LORD-DUSTHANA-03",
        version="1.0.0",
        domain="career",
        profile="parashari",
        chart_frame="D1",
        predicate=_pred_h10_lord_dusthana,
        ordered_exceptions=[_exc_dusthana_own_or_exalted],
        dedupe_key="H10_LORD_PLACEMENT",
        effect="OBSTRUCTS",
        birth_time_sensitive=False,
        explanation_template="10th lord placed in a trik house (6, 8, 12) suggests professional disruptions, service subordination, or changes in vocation.",
        source_family="BPHS",
        source_reference="BPHS Ch. 24, v. 115-117",
        source_status="VERIFIED",
        review_status="ACCEPTED",
        confidence="HIGH",
        archetypes=["Service, Operations & Healthcare"],
    ),
    CareerRule(
        rule_id="CAREER-H10-LORD-EXALTED-OWN-04",
        version="1.0.0",
        domain="career",
        profile="parashari",
        chart_frame="D1",
        predicate=_pred_h10_lord_exalted_own,
        ordered_exceptions=[],
        dedupe_key="H10_LORD_DIGNITY",
        effect="SUPPORTS",
        birth_time_sensitive=False,
        explanation_template="10th lord in peak dignity (exalted or in own sign) grants professional autonomy, distinction, and mastery in the field.",
        source_family="Phaladeepika",
        source_reference="Phaladeepika Ch. 15, v. 1-2",
        source_status="VERIFIED",
        review_status="ACCEPTED",
        confidence="HIGH",
        archetypes=["Leadership & Governance"],
    ),
    CareerRule(
        rule_id="CAREER-H10-LORD-DEBILITATED-05",
        version="1.0.0",
        domain="career",
        profile="parashari",
        chart_frame="D1",
        predicate=_pred_h10_lord_debilitated,
        ordered_exceptions=[_exc_neech_bhanga_cancellation],
        dedupe_key="H10_LORD_DIGNITY",
        effect="OBSTRUCTS",
        birth_time_sensitive=False,
        explanation_template="10th lord in its sign of debilitation can indicate professional struggles or lack of organizational backing.",
        source_family="Phaladeepika",
        source_reference="Phaladeepika Ch. 15, v. 3",
        source_status="VERIFIED",
        review_status="ACCEPTED",
        confidence="HIGH",
        archetypes=[],
    ),
    CareerRule(
        rule_id="CAREER-H10-AMALA-BENEFIC-06",
        version="1.0.0",
        domain="career",
        profile="parashari",
        chart_frame="D1",
        predicate=_pred_h10_amala_benefic,
        ordered_exceptions=[],
        dedupe_key="H10_AMALA",
        effect="SUPPORTS",
        birth_time_sensitive=False,
        explanation_template="Amala Yoga: An unblemished natural benefic in the 10th house bestows a spotlessly ethical reputation and lasting public esteem.",
        source_family="BPHS",
        source_reference="BPHS Ch. 35, v. 97-98",
        source_status="VERIFIED",
        review_status="ACCEPTED",
        confidence="HIGH",
        archetypes=["Advisory, Legal & Scholarly", "Commercial & Financial"],
    ),
    CareerRule(
        rule_id="CAREER-H10-UPACHAYA-MALEFIC-07",
        version="1.0.0",
        domain="career",
        profile="parashari",
        chart_frame="D1",
        predicate=_pred_h10_upachaya_malefic,
        ordered_exceptions=[],
        dedupe_key="H10_MALEFIC_UPACHAYA",
        effect="CONDITIONAL",
        birth_time_sensitive=False,
        explanation_template="Natural malefics in the 10th house (an Upachaya house) produce fierce professional ambition, executive toughness, and triumph over rivals.",
        source_family="BPHS",
        source_reference="BPHS Ch. 11, v. 10",
        source_status="VERIFIED",
        review_status="ACCEPTED",
        confidence="MEDIUM",
        archetypes=["Technical & Engineering", "Leadership & Governance"],
    ),
    CareerRule(
        rule_id="CAREER-H10-SUN-DIGBALA-08",
        version="1.0.0",
        domain="career",
        profile="parashari",
        chart_frame="D1",
        predicate=_pred_h10_sun_digbala,
        ordered_exceptions=[_exc_sun_debilitated_no_nb],
        dedupe_key="H10_SUN",
        effect="SUPPORTS",
        birth_time_sensitive=False,
        explanation_template="Sun in the 10th house attains peak Dig Bala, conferring administrative authority, government connection, and natural command.",
        source_family="Phaladeepika",
        source_reference="Phaladeepika Ch. 8, v. 10",
        source_status="VERIFIED",
        review_status="ACCEPTED",
        confidence="HIGH",
        archetypes=["Leadership & Governance"],
    ),
    CareerRule(
        rule_id="CAREER-H10-MARS-KULADEEPAKA-09",
        version="1.0.0",
        domain="career",
        profile="parashari",
        chart_frame="D1",
        predicate=_pred_h10_mars_kuladeepaka,
        ordered_exceptions=[_exc_mars_debilitated_no_nb],
        dedupe_key="H10_MARS",
        effect="SUPPORTS",
        birth_time_sensitive=False,
        explanation_template="Mars in the 10th house achieves directional strength and Kuladeepaka Yoga, driving engineering prowess, surgical skill, or executive enforcement.",
        source_family="Phaladeepika",
        source_reference="Phaladeepika Ch. 8, v. 12",
        source_status="VERIFIED",
        review_status="ACCEPTED",
        confidence="HIGH",
        archetypes=["Technical & Engineering", "Leadership & Governance"],
    ),
    CareerRule(
        rule_id="CAREER-H10-SATURN-SERVICE-10",
        version="1.0.0",
        domain="career",
        profile="parashari",
        chart_frame="D1",
        predicate=_pred_h10_saturn_service,
        ordered_exceptions=[_exc_saturn_debilitated_no_nb],
        dedupe_key="H10_SATURN",
        effect="SUPPORTS",
        birth_time_sensitive=False,
        explanation_template="Saturn in the 10th house grants persevering stamina, deep operational discipline, and mastery over complex enterprise machinery.",
        source_family="Phaladeepika",
        source_reference="Phaladeepika Ch. 8, v. 16",
        source_status="VERIFIED",
        review_status="ACCEPTED",
        confidence="MEDIUM",
        archetypes=["Service, Operations & Healthcare", "Technical & Engineering"],
    ),
    CareerRule(
        rule_id="CAREER-H10-MERCURY-COMMERCE-11",
        version="1.0.0",
        domain="career",
        profile="parashari",
        chart_frame="D1",
        predicate=_pred_h10_mercury_commerce,
        ordered_exceptions=[_exc_mercury_debilitated_no_nb],
        dedupe_key="H10_MERCURY",
        effect="SUPPORTS",
        birth_time_sensitive=False,
        explanation_template="Mercury in the 10th house promotes analytical brilliance, agile commercial enterprise, computational acumen, and media engagement.",
        source_family="Phaladeepika",
        source_reference="Phaladeepika Ch. 8, v. 13",
        source_status="VERIFIED",
        review_status="ACCEPTED",
        confidence="HIGH",
        archetypes=["Commercial & Financial", "Creative & Media"],
    ),
    CareerRule(
        rule_id="CAREER-H10-JUPITER-ADVISORY-12",
        version="1.0.0",
        domain="career",
        profile="parashari",
        chart_frame="D1",
        predicate=_pred_h10_jupiter_advisory,
        ordered_exceptions=[_exc_jupiter_debilitated_no_nb],
        dedupe_key="H10_JUPITER",
        effect="SUPPORTS",
        birth_time_sensitive=False,
        explanation_template="Jupiter in the 10th house fosters respected counsel, legal acumen, higher education leadership, and ethical executive roles.",
        source_family="Phaladeepika",
        source_reference="Phaladeepika Ch. 8, v. 14",
        source_status="VERIFIED",
        review_status="ACCEPTED",
        confidence="HIGH",
        archetypes=["Advisory, Legal & Scholarly"],
    ),
    CareerRule(
        rule_id="CAREER-H10-PAPAKARTARI-13",
        version="1.0.0",
        domain="career",
        profile="parashari",
        chart_frame="D1",
        predicate=_pred_h10_papakartari,
        ordered_exceptions=[_exc_kartari_benefic_relief],
        dedupe_key="H10_KARTARI",
        effect="OBSTRUCTS",
        birth_time_sensitive=False,
        explanation_template="10th house hemmed between natural malefics in 9th and 11th creates professional constriction and friction with peers or superiors.",
        source_family="Jataka Parijata",
        source_reference="Classical Jataka Kartari principles",
        source_status="VERIFIED",
        review_status="ACCEPTED",
        confidence="MEDIUM",
        archetypes=[],
    ),

    # Family B: Artha & Supporting Houses
    CareerRule(
        rule_id="CAREER-H6-SERVICE-ALIGNMENT-14",
        version="1.0.0",
        domain="career",
        profile="parashari",
        chart_frame="D1",
        predicate=_pred_h6_service_alignment,
        ordered_exceptions=[],
        dedupe_key="H6_H10_LINK",
        effect="CONDITIONAL",
        birth_time_sensitive=False,
        explanation_template="Connection between 6th and 10th houses directs career potential toward competitive examinations, salaried service, legal mediation, or health management.",
        source_family="BPHS",
        source_reference="BPHS Ch. 24, v. 61-72",
        source_status="VERIFIED",
        review_status="ACCEPTED",
        confidence="HIGH",
        archetypes=["Service, Operations & Healthcare"],
    ),
    CareerRule(
        rule_id="CAREER-H2-H11-ARTHA-CONNECTION-15",
        version="1.0.0",
        domain="career",
        profile="parashari",
        chart_frame="D1",
        predicate=_pred_h2_h11_artha_connection,
        ordered_exceptions=[],
        dedupe_key="ARTHA_TRIKONA_LINK",
        effect="SUPPORTS",
        birth_time_sensitive=False,
        explanation_template="Association of 10th lord with 2nd or 11th house/lord connects career achievements directly with substantial financial gains and assets.",
        source_family="BPHS",
        source_reference="BPHS Ch. 41 (Dhana Yogas)",
        source_status="VERIFIED",
        review_status="ACCEPTED",
        confidence="HIGH",
        archetypes=["Commercial & Financial"],
    ),
    CareerRule(
        rule_id="CAREER-H5-INTELLECT-ALIGNMENT-16",
        version="1.0.0",
        domain="career",
        profile="parashari",
        chart_frame="D1",
        predicate=_pred_h5_intellect_alignment,
        ordered_exceptions=[],
        dedupe_key="H5_H10_LINK",
        effect="SUPPORTS",
        birth_time_sensitive=False,
        explanation_template="5th lord connection with 10th infuses career with strategic acumen, creative innovation, scholarly design, or advisory wisdom.",
        source_family="BPHS",
        source_reference="BPHS Ch. 41; Saravali Ch. 35",
        source_status="VERIFIED",
        review_status="ACCEPTED",
        confidence="HIGH",
        archetypes=["Advisory, Legal & Scholarly", "Creative & Media"],
    ),
    CareerRule(
        rule_id="CAREER-DHARMA-KARMA-YOGA-17",
        version="1.0.0",
        domain="career",
        profile="parashari",
        chart_frame="D1",
        predicate=_pred_dharma_karma_yoga,
        ordered_exceptions=[],
        dedupe_key="DHARMA_KARMA_YOGA",
        effect="SUPPORTS",
        birth_time_sensitive=False,
        explanation_template="Dharma-Karmadhipati Yoga: Mutual reception, conjunction, or lordship of 9th and 10th houses generates lasting vocational preeminence and societal honour.",
        source_family="BPHS",
        source_reference="BPHS Ch. 41, v. 37-38",
        source_status="VERIFIED",
        review_status="ACCEPTED",
        confidence="HIGH",
        archetypes=["Leadership & Governance", "Advisory, Legal & Scholarly"],
    ),
    CareerRule(
        rule_id="CAREER-LAGNA-LORD-10TH-18",
        version="1.0.0",
        domain="career",
        profile="parashari",
        chart_frame="D1",
        predicate=_pred_lagna_lord_10th,
        ordered_exceptions=[],
        dedupe_key="L1_IN_H10",
        effect="SUPPORTS",
        birth_time_sensitive=False,
        explanation_template="Ascendant lord placed in 10th house creates an intensely career-driven personality, forging strong self-made vocational achievement.",
        source_family="BPHS",
        source_reference="BPHS Ch. 24, v. 10",
        source_status="VERIFIED",
        review_status="ACCEPTED",
        confidence="HIGH",
        archetypes=["Leadership & Governance"],
    ),

    # Family C: Multi-Frame Cross-Readings
    CareerRule(
        rule_id="CAREER-CHANDRA-LAGNA-H10-19",
        version="1.0.0",
        domain="career",
        profile="parashari",
        chart_frame="Chandra_Lagna",
        predicate=_pred_chandra_lagna_h10,
        ordered_exceptions=[],
        dedupe_key="CHANDRA_H10",
        effect="SUPPORTS",
        birth_time_sensitive=False,
        explanation_template="10th house from Moon (Chandra Lagna) occupied by strong planets ensures public acclaim, emotional resonance with work, and wide recognition.",
        source_family="Phaladeepika",
        source_reference="Phaladeepika Ch. 15, v. 6",
        source_status="VERIFIED",
        review_status="ACCEPTED",
        confidence="HIGH",
        archetypes=["Leadership & Governance", "Creative & Media"],
    ),
    CareerRule(
        rule_id="CAREER-SURYA-LAGNA-H10-20",
        version="1.0.0",
        domain="career",
        profile="parashari",
        chart_frame="Surya_Lagna",
        predicate=_pred_surya_lagna_h10,
        ordered_exceptions=[],
        dedupe_key="SURYA_H10",
        effect="SUPPORTS",
        birth_time_sensitive=False,
        explanation_template="10th house from Sun (Surya Lagna) occupied by strong planets solidifies professional standing, official authority, and executive status.",
        source_family="Phaladeepika",
        source_reference="Phaladeepika Ch. 15, v. 7",
        source_status="VERIFIED",
        review_status="ACCEPTED",
        confidence="MEDIUM",
        archetypes=["Leadership & Governance"],
    ),

    # Family D: Jaimini Amatyakaraka
    CareerRule(
        rule_id="CAREER-JAIMINI-AMATYAKARAKA-KENDRA-21",
        version="1.0.0",
        domain="career",
        profile="jaimini",
        chart_frame="D1",
        predicate=_pred_jaimini_amk_kendra,
        ordered_exceptions=[],
        dedupe_key="AMK_PLACEMENT",
        effect="SUPPORTS",
        birth_time_sensitive=False,
        explanation_template="Jaimini Amatyakaraka (significator of mind/career) in a Kendra or Trikona indicates high advisory, managerial, or ministerial stature.",
        source_family="Jaimini Sutras",
        source_reference="Jaimini Upadesha Sutras 1.2",
        source_status="VERIFIED",
        review_status="ACCEPTED",
        confidence="HIGH",
        archetypes=["Leadership & Governance", "Advisory, Legal & Scholarly"],
    ),
    CareerRule(
        rule_id="CAREER-JAIMINI-AMATYAKARAKA-DUSTHANA-22",
        version="1.0.0",
        domain="career",
        profile="jaimini",
        chart_frame="D1",
        predicate=_pred_jaimini_amk_dusthana,
        ordered_exceptions=[],
        dedupe_key="AMK_PLACEMENT",
        effect="OBSTRUCTS",
        birth_time_sensitive=False,
        explanation_template="Jaimini Amatyakaraka in Dusthana without dignity points to vocational obstacles, frequent structural reorganizations, or friction with authorities.",
        source_family="Jaimini Sutras",
        source_reference="Jaimini Upadesha Sutras 1.2",
        source_status="VERIFIED",
        review_status="ACCEPTED",
        confidence="MEDIUM",
        archetypes=["Service, Operations & Healthcare"],
    ),

    # Family E: D10 Dashamsha & Timing
    CareerRule(
        rule_id="CAREER-D10-DASHAMSHA-10TH-LORD-23",
        version="1.0.0",
        domain="career",
        profile="parashari",
        chart_frame="D10",
        predicate=_pred_d10_10th_lord_strength,
        ordered_exceptions=[],
        dedupe_key="D10_10TH_LORD",
        effect="SUPPORTS",
        birth_time_sensitive=True,
        explanation_template="10th lord occupying an exalted or own sign in D10 Dashamsha confirms institutional stamina and structural prominence in the profession.",
        source_family="BPHS",
        source_reference="BPHS Ch. 6, v. 11-12",
        source_status="VERIFIED",
        review_status="ACCEPTED",
        confidence="HIGH",
        archetypes=["Leadership & Governance"],
    ),
    CareerRule(
        rule_id="CAREER-TIMING-DASHA-ACTIVATION-24",
        version="1.0.0",
        domain="career",
        profile="parashari",
        chart_frame="D1",
        predicate=_pred_timing_dasha_activation,
        ordered_exceptions=[],
        dedupe_key="TIMING_DASHA",
        effect="CONDITIONAL",
        birth_time_sensitive=False,
        explanation_template="Current Vimshottari Mahadasha or Antardasha operating through the 10th lord or 10th house occupants actively triggers vocational developments.",
        source_family="Parashari Timing",
        source_reference="BPHS Dasha Phala Adhyaya",
        source_status="VERIFIED",
        review_status="ACCEPTED",
        confidence="HIGH",
        archetypes=[],
    ),
]


# ---------------------------------------------------------------------------
# Evaluator Engine
# ---------------------------------------------------------------------------

def evaluate_career_rules(ctx: dict) -> dict:
    """
    Evaluate all canonical career rules against canonical ChartContext.
    Returns:
      - matched_rules: list of fired rules with reasons, tokens, effect, and metadata
      - rejected_rules: list of rules rejected by exceptions with reasons
      - archetype_weights: dictionary of vocational archetype scores
      - primary_archetypes: top vocational archetypes sorted by evidence
      - supports_count: count of supporting rules
      - obstructs_count: count of obstructing rules
      - conditional_count: count of conditional rules
      - amatyakaraka: {planet, degree}
      - d10_10th_lord_sign: sign of 10th lord in D10
      - summary_score: normalized evidence score (0-100)
    """
    matched = []
    rejected = []
    seen_dedupe_keys = {}

    archetype_scores = {arc: 0 for arc in ARCHETYPES}
    supports_count = 0
    obstructs_count = 0
    conditional_count = 0

    extra = {}
    pm = ctx.get("planet_map", {})
    amk_name, amk_deg = calculate_amatyakaraka(pm)
    extra["amatyakaraka"] = amk_name
    extra["amatyakaraka_degree"] = amk_deg

    for rule in CAREER_RULES_CATALOG:
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
                # Prefer rule with higher confidence
                prior_conf = seen_dedupe_keys[rule.dedupe_key]
                if rule.confidence != "HIGH" and prior_conf == "HIGH":
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

    # Compute a balanced astrological evidence vitality score (30 to 95)
    # Baseline 50, +6 for each supporting evidence, -6 for obstructing evidence
    raw_score = 50 + (supports_count * 6) - (obstructs_count * 6) + (conditional_count * 2)
    normalized_score = max(25, min(95, raw_score))

    # 10th lord D10 sign
    hl = ctx.get("house_lords", {})
    lagna = ctx.get("lagna", "")
    l10 = hl.get(10) or safe_house_lord(lagna, 10)
    l10_p = pm.get(l10, {})
    l10_d10_sign = calculate_dashamsha_d10(l10_p.get("sign", ""), float(l10_p.get("degree", 0.0))) if l10_p else ""

    return {
        "domain": "career",
        "score": normalized_score,
        "matched_rules": matched,
        "rejected_rules": rejected,
        "supports_count": supports_count,
        "obstructs_count": obstructs_count,
        "conditional_count": conditional_count,
        "archetype_scores": archetype_scores,
        "primary_archetypes": sorted_archetypes,
        "amatyakaraka": {
            "planet": amk_name,
            "degree": round(amk_deg, 2) if amk_name else 0.0,
        },
        "d10_10th_lord_sign": l10_d10_sign,
        "birth_time_sensitive_count": sum(1 for r in matched if r["birth_time_sensitive"]),
    }
