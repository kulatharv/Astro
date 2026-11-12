"""
Classical Vedic Astrology Property & Residence Domain Rule Pack (Pure Shared Library).

Implements 27 canonical, deterministic Parāśari rules regarding domestic stability,
property acquisition, property disposal/sale, construction & land development,
relocation/foreign residence, ancestral/inherited property, and financial obligations.

Separates 7 safe, explainable dimensions:
  1. Residential Stability & Domestic Environment (residential_stability)
  2. Property Ownership & Acquisition (property_acquisition)
  3. Property Sale & Disposal (property_disposal_sale)
  4. Construction & Land Development (construction_development)
  5. Relocation & Residence Changes (relocation_residence)
  6. Inherited & Ancestral Property (inherited_property)
  7. Property Financial Obligations (property_obligations)

Includes mathematically verified D4 Chaturthamsa (Turyamsha) calculation per BPHS Ch. 6, v. 5-6.

Strictly adheres to Master Specification v3.0 §9.7 & §21 (Safety Guardrails).
ABSOLUTE PROHIBITION: Never guarantees property purchases, sales, prices, appreciation,
rental income, construction completion dates, relocation timing, mortgage/loan approvals,
or legal ownership/dispute outcomes.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Any, Optional

from .zodiac import SIGNS_SK, SIGN_LORDS
from .strength import EXALTATION, DEBILITATION, OWN_SIGNS
from .lordship import get_house_lord
from .combustion import is_combust


# ---------------------------------------------------------------------------
# Constants & Allowed Dimensions
# ---------------------------------------------------------------------------

KENDRA = {1, 4, 7, 10}
TRIKONA = {1, 5, 9}
DUSTHANA = {6, 8, 12}
UPACHAYA = {3, 6, 10, 11}

EARTH_SIGNS = {"Vrishabha", "Kanya", "Makara"}
MOVABLE_SIGNS = {"Mesha", "Karka", "Tula", "Makara"}
FIXED_SIGNS = {"Vrishabha", "Simha", "Vrischika", "Kumbha"}
DUAL_SIGNS = {"Mithuna", "Kanya", "Dhanu", "Meena"}

CLASSICAL_7 = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
NATURAL_BENEFICS = {"Jupiter", "Venus", "Mercury", "Moon"}
NATURAL_MALEFICS = {"Sun", "Mars", "Saturn", "Rahu", "Ketu"}

PROPERTY_DIMENSIONS = [
    "residential_stability",
    "property_acquisition",
    "property_disposal_sale",
    "construction_development",
    "relocation_residence",
    "inherited_property",
    "property_obligations",
]

PROPERTY_SAFETY_DISCLAIMER = (
    "AstroLogic AI provides non-deterministic cultural, philosophical, and astrological reflections only. "
    "Astrological charts CANNOT guarantee property acquisition, price appreciation, rental yield, mortgage approval, "
    "legal title, or inheritance outcomes. Real estate decisions involve significant financial and legal commitments "
    "and must be based on qualified financial advice, legal due diligence, title verification, and local regulatory compliance."
)


# ---------------------------------------------------------------------------
# Canonical Property Rule Dataclass
# ---------------------------------------------------------------------------

@dataclass
class PropertyRule:
    rule_id: str
    version: str
    domain: str
    profile: str
    chart_frame: str
    predicate: Callable[[dict, dict], tuple[bool, str, list[str]]]
    ordered_exceptions: list[Callable[[dict, dict], tuple[Optional[bool], str]]] = field(default_factory=list)
    dedupe_key: Optional[str] = None
    effect: str = "SUPPORTS"  # SUPPORTS, OBSTRUCTS, CONDITIONAL
    birth_time_sensitive: bool = False
    explanation_template: str = ""
    source_family: str = ""
    source_reference: str = ""
    source_status: str = "VERIFIED"  # VERIFIED, SOURCE VERIFICATION REQUIRED
    review_status: str = "ACCEPTED"  # ACCEPTED, EXPERT REVIEW REQUIRED
    confidence: str = "[HIGH]"
    tests: list[str] = field(default_factory=list)
    dimensions: list[str] = field(default_factory=list)
    enabled: bool = True


# ---------------------------------------------------------------------------
# D4 Chaturthamsa Calculator (BPHS Ch. 6, v. 5-6)
# ---------------------------------------------------------------------------

def calculate_chaturthamsa_d4(sign: str, degree: float) -> str:
    """
    Calculate Chaturthamsa (D4 / Turyamsha) rashi according to classical BPHS Ch. 6, v. 5-6.

    Each sign of 30° is divided into 4 equal quarters of 7° 30' (7.5°).
    The 4 divisions map to the four Kendras (1st, 4th, 7th, 10th) counted from the natal sign itself:
      - Quarter 0 [0.0°, 7.5°): Sign itself (1st Kendra)
      - Quarter 1 [7.5°, 15.0°): 4th sign from it (4th Kendra)
      - Quarter 2 [15.0°, 22.5°): 7th sign from it (7th Kendra)
      - Quarter 3 [22.5°, 30.0°): 10th sign from it (10th Kendra)

    Parameters:
        sign: Sanskrit name of the sign (e.g., 'Mesha', 'Vrishabha')
        degree: Longitudinal position within the sign [0.0, 30.0)

    Returns:
        Sanskrit name of the D4 sign.
    """
    if not sign:
        return "Mesha"
    norm = sign.strip().capitalize()
    if norm == "Vrishika":
        norm = "Vrischika"
    if norm not in SIGNS_SK:
        return "Mesha"

    sign_idx = SIGNS_SK.index(norm)
    deg = float(degree) % 30.0
    part = int(deg / 7.5)
    if part > 3:
        part = 3
    elif part < 0:
        part = 0

    return SIGNS_SK[(sign_idx + part * 3) % 12]


def build_d4_chart(ctx: dict) -> dict[str, Any]:
    """
    Construct D4 positions and houses for Lagna and all planets.
    Uses planet degrees and lagna degree if provided, else defaults to 15.0°.
    """
    pmap = ctx.get("planet_map", {})
    lagna_sign = ctx.get("lagna", "Mesha")
    lagna_deg = ctx.get("ascendant_degree", 15.0)

    d4_lagna = calculate_chaturthamsa_d4(lagna_sign, lagna_deg)
    d4_lagna_idx = SIGNS_SK.index(d4_lagna)

    d4_planets = {}
    for p, pdata in pmap.items():
        p_sign = pdata.get("sign", "Mesha")
        raw_lon = pdata.get("longitude")
        fallback_deg = (raw_lon % 30.0) if raw_lon is not None else 15.0
        p_deg = pdata.get("degree") if pdata.get("degree") is not None else fallback_deg
        d4_sign = calculate_chaturthamsa_d4(p_sign, p_deg)
        d4_s_idx = SIGNS_SK.index(d4_sign)
        d4_house = (d4_s_idx - d4_lagna_idx) % 12 + 1
        d4_planets[p] = {
            "sign": d4_sign,
            "house": d4_house,
            "degree": float(p_deg) % 7.5 * 4.0,  # mapped within D4 sign
        }

    d4_houses = {h: [] for h in range(1, 13)}
    for p, pinfo in d4_planets.items():
        d4_houses[pinfo["house"]].append(p)

    d4_house_lords = {}
    for h in range(1, 13):
        h_sign = SIGNS_SK[(d4_lagna_idx + h - 1) % 12]
        d4_house_lords[h] = SIGN_LORDS.get(h_sign, "Mars")

    return {
        "lagna": d4_lagna,
        "planet_map": d4_planets,
        "houses": d4_houses,
        "house_lords": d4_house_lords,
    }


# ---------------------------------------------------------------------------
# Context Helper Utilities
# ---------------------------------------------------------------------------

def _get_lagna(ctx: dict) -> str:
    return ctx.get("lagna", ctx.get("lagna_sign", "Mesha"))


def _get_house_lord_safe(ctx: dict, h: int) -> str:
    hl = ctx.get("house_lords", {})
    if h in hl:
        return hl[h]
    lagna = _get_lagna(ctx)
    return get_house_lord(lagna, h)


def _get_occupants(ctx: dict, h: int) -> list[str]:
    pm = ctx.get("planet_map", {})
    return [p for p, d in pm.items() if d.get("house") == h]


def _has_aspect(ctx: dict, planet: str, target_house: int) -> bool:
    aspect_map = ctx.get("aspect_map", {})
    if planet in aspect_map:
        return target_house in aspect_map[planet]
    pm = ctx.get("planet_map", {})
    if planet not in pm:
        return False
    p_house = pm[planet].get("house", 1)
    diff = (target_house - p_house) % 12
    if diff == 6:  # 7th house aspect (all planets)
        return True
    if planet == "Mars" and diff in (3, 7):  # 4th and 8th aspect
        return True
    if planet == "Jupiter" and diff in (4, 8):  # 5th and 9th aspect
        return True
    if planet == "Saturn" and diff in (2, 9):  # 3rd and 10th aspect
        return True
    return False


def _is_combust(ctx: dict, planet: str) -> Optional[bool]:
    pm = ctx.get("planet_map", {})
    pdata = pm.get(planet, {})
    if pdata.get("is_combust") is not None:
        return pdata["is_combust"]
    if pdata.get("combust") is not None:
        return pdata["combust"]
    sun_data = pm.get("Sun", {})
    return is_combust(planet, pdata, sun_data)


def _is_retrograde(ctx: dict, planet: str) -> bool:
    pm = ctx.get("planet_map", {})
    pdata = pm.get(planet, {})
    return bool(pdata.get("is_retrograde", False))


def _has_neecha_bhanga(ctx: dict, planet: str) -> bool:
    yogas = ctx.get("yogas", [])
    if isinstance(yogas, list):
        for y in yogas:
            y_name = y.get("name", "") if isinstance(y, dict) else str(y)
            if "Neecha Bhanga" in y_name or "Neechabhanga" in y_name:
                return True
    return False


# ---------------------------------------------------------------------------
# Canonical 27 Property Rules Definitions
# ---------------------------------------------------------------------------

PROPERTY_RULES_CATALOG: list[PropertyRule] = []


def _register(rule: PropertyRule) -> None:
    PROPERTY_RULES_CATALOG.append(rule)


# ===========================================================================
# DIMENSION 1: Residential Stability & Domestic Environment (residential_stability)
# ===========================================================================

def pred_prop_res_01(ctx: dict, d4: dict) -> tuple[bool, str, list[str]]:
    l4 = _get_house_lord_safe(ctx, 4)
    pm = ctx.get("planet_map", {})
    l4_data = pm.get(l4, {})
    h = l4_data.get("house", 0)
    sign = l4_data.get("sign", "")
    is_own = sign in OWN_SIGNS.get(l4, set())
    is_exalted = sign == EXALTATION.get(l4, "")
    if h in (KENDRA | TRIKONA) and (is_own or is_exalted):
        return True, f"4th lord {l4} is well-placed in house {h} in {'own' if is_own else 'exalted'} sign {sign}, supporting residential stability.", [l4]
    return False, "", []

def exc_prop_res_01(ctx: dict, d4: dict) -> tuple[Optional[bool], str]:
    l4 = _get_house_lord_safe(ctx, 4)
    if not l4:
        return None, "4th lord not found in chart; combustion status is unknown"
    cb = _is_combust(ctx, l4)
    if cb is None:
        return None, f"4th lord {l4} combustion status is unknown due to missing or invalid coordinates"
    if cb is True:
        return True, f"4th lord {l4} is combust, mitigating domestic stability."
    return False, f"4th lord {l4} is free from combustion"

_register(PropertyRule(
    rule_id="PROP-RES-01",
    version="1.0.0",
    domain="property",
    profile="parashari",
    chart_frame="D1",
    predicate=pred_prop_res_01,
    ordered_exceptions=[exc_prop_res_01],
    dedupe_key="l4_kendra_exalted",
    effect="SUPPORTS",
    birth_time_sensitive=False,
    explanation_template="4th lord in Kendra/Trikona in dignity provides domestic contentment and stable living environment.",
    source_family="Parashari",
    source_reference="BPHS Ch. 12, v. 2-4",
    source_status="VERIFIED",
    review_status="ACCEPTED",
    confidence="[HIGH]",
    dimensions=["residential_stability"],
    tests=["test_prop_res_01_positive", "test_prop_res_01_negative", "test_prop_res_01_exception"],
))


def pred_prop_res_02(ctx: dict, d4: dict) -> tuple[bool, str, list[str]]:
    occ = _get_occupants(ctx, 4)
    benefics_in_4 = [p for p in occ if p in NATURAL_BENEFICS and p in ("Jupiter", "Venus")]
    if benefics_in_4:
        malefics_aspecting = [m for m in ("Mars", "Saturn", "Rahu", "Ketu") if _has_aspect(ctx, m, 4)]
        if not malefics_aspecting:
            return True, f"Natural benefic {', '.join(benefics_in_4)} in 4th house without malefic aspects fosters domestic harmony.", benefics_in_4
    return False, "", []

_register(PropertyRule(
    rule_id="PROP-RES-02",
    version="1.0.0",
    domain="property",
    profile="parashari",
    chart_frame="D1",
    predicate=pred_prop_res_02,
    dedupe_key="benefic_in_4h",
    effect="SUPPORTS",
    birth_time_sensitive=False,
    explanation_template="Natural benefics in the 4th house without malefic affliction create an auspicious, peaceful residential environment.",
    source_family="Parashari",
    source_reference="Phaladeepika Ch. 16, v. 8",
    source_status="VERIFIED",
    review_status="ACCEPTED",
    confidence="[HIGH]",
    dimensions=["residential_stability"],
    tests=["test_prop_res_02_positive", "test_prop_res_02_negative"],
))


def pred_prop_res_03(ctx: dict, d4: dict) -> tuple[bool, str, list[str]]:
    occ = _get_occupants(ctx, 4)
    malefics_in_4 = [p for p in occ if p in ("Saturn", "Mars", "Rahu")]
    if malefics_in_4:
        benefics_aspecting = [b for b in ("Jupiter", "Venus") if _has_aspect(ctx, b, 4)]
        if not benefics_aspecting:
            return True, f"Natural malefic(s) {', '.join(malefics_in_4)} occupying 4th house without benefic relief indicates domestic friction.", malefics_in_4
    return False, "", []

def exc_prop_res_03(ctx: dict, d4: dict) -> tuple[bool, str]:
    occ = _get_occupants(ctx, 4)
    l4 = _get_house_lord_safe(ctx, 4)
    if l4 in occ:
        return True, f"4th lord {l4} is present in 4th house, mitigating malefic distress."
    return False, ""

_register(PropertyRule(
    rule_id="PROP-RES-03",
    version="1.0.0",
    domain="property",
    profile="parashari",
    chart_frame="D1",
    predicate=pred_prop_res_03,
    ordered_exceptions=[exc_prop_res_03],
    dedupe_key="malefic_in_4h",
    effect="OBSTRUCTS",
    birth_time_sensitive=False,
    explanation_template="Malefic occupancy in 4th house without benefic aspects points to domestic friction or unrest in residence.",
    source_family="Parashari",
    source_reference="BPHS Ch. 12, v. 9",
    source_status="VERIFIED",
    review_status="ACCEPTED",
    confidence="[HIGH]",
    dimensions=["residential_stability"],
    tests=["test_prop_res_03_positive", "test_prop_res_03_negative", "test_prop_res_03_exception"],
))


def pred_prop_res_04(ctx: dict, d4: dict) -> tuple[bool, str, list[str]]:
    pm = ctx.get("planet_map", {})
    moon = pm.get("Moon", {})
    h = moon.get("house", 0)
    sign = moon.get("sign", "")
    if h in (KENDRA | TRIKONA) and sign != "Vrischika":  # not debilitated
        saturn_aspect = _has_aspect(ctx, "Saturn", h)
        rahu_occ = "Rahu" in _get_occupants(ctx, h)
        if not saturn_aspect and not rahu_occ:
            return True, f"Moon well-placed in house {h} in {sign} without major malefic affliction fosters psychological comfort at home.", ["Moon"]
    return False, "", []

_register(PropertyRule(
    rule_id="PROP-RES-04",
    version="1.0.0",
    domain="property",
    profile="parashari",
    chart_frame="D1",
    predicate=pred_prop_res_04,
    dedupe_key="moon_comfort",
    effect="SUPPORTS",
    birth_time_sensitive=False,
    explanation_template="Moon as Karaka of domestic peace in Kendra/Trikona promotes serenity and familial comfort.",
    source_family="Parashari",
    source_reference="Saravali Ch. 16",
    source_status="VERIFIED",
    review_status="ACCEPTED",
    confidence="[MEDIUM]",
    dimensions=["residential_stability"],
    tests=["test_prop_res_04_positive", "test_prop_res_04_negative"],
))


# ===========================================================================
# DIMENSION 2: Property Ownership & Acquisition (property_acquisition)
# ===========================================================================

def pred_prop_acq_01(ctx: dict, d4: dict) -> tuple[bool, str, list[str]]:
    pm = ctx.get("planet_map", {})
    mars = pm.get("Mars", {})
    h = mars.get("house", 0)
    sign = mars.get("sign", "")
    is_own = sign in OWN_SIGNS.get("Mars", set())
    is_exalted = (sign == EXALTATION.get("Mars", ""))
    if h in (KENDRA | TRIKONA) and (is_own or is_exalted):
        return True, f"Mars (Bhumi-karaka) strong in house {h} in {'own' if is_own else 'exalted'} sign {sign} supports landed asset capacity.", ["Mars"]
    return False, "", []

def exc_prop_acq_01(ctx: dict, d4: dict) -> tuple[Optional[bool], str]:
    cb = _is_combust(ctx, "Mars")
    if cb is None:
        return None, "Mars combustion status is unknown due to missing or invalid coordinates"
    if cb is True:
        return True, "Mars is combust by the Sun, reducing landed asset signification."
    return False, "Mars is free from combustion"

_register(PropertyRule(
    rule_id="PROP-ACQ-01",
    version="1.0.0",
    domain="property",
    profile="parashari",
    chart_frame="D1",
    predicate=pred_prop_acq_01,
    ordered_exceptions=[exc_prop_acq_01],
    dedupe_key="mars_karaka_exalted",
    effect="SUPPORTS",
    birth_time_sensitive=False,
    explanation_template="Mars as Bhumi-karaka (real estate signifier) exalted or in own sign in Kendra/Trikona strengthens capacity for landed assets.",
    source_family="Parashari",
    source_reference="BPHS Ch. 16, v. 21",
    source_status="VERIFIED",
    review_status="ACCEPTED",
    confidence="[HIGH]",
    dimensions=["property_acquisition"],
    tests=["test_prop_acq_01_positive", "test_prop_acq_01_negative", "test_prop_acq_01_exception"],
))


def pred_prop_acq_02(ctx: dict, d4: dict) -> tuple[bool, str, list[str]]:
    l4 = _get_house_lord_safe(ctx, 4)
    l11 = _get_house_lord_safe(ctx, 11)
    pm = ctx.get("planet_map", {})
    l4_data = pm.get(l4, {})
    l11_data = pm.get(l11, {})
    h4 = l4_data.get("house", 0)
    h11 = l11_data.get("house", 0)

    # 4th lord in 11th or conjunction with 11th lord or mutual aspect
    if h4 == 11 or h4 == h11 or _has_aspect(ctx, l4, h11):
        return True, f"4th lord {l4} forms sambandha with 11th lord {l11} (house {h4}/{h11}), indicating material gain through fixed assets.", [l4, l11]
    return False, "", []

_register(PropertyRule(
    rule_id="PROP-ACQ-02",
    version="1.0.0",
    domain="property",
    profile="parashari",
    chart_frame="D1",
    predicate=pred_prop_acq_02,
    dedupe_key="l4_l11_sambandha",
    effect="SUPPORTS",
    birth_time_sensitive=False,
    explanation_template="Sambandha between 4th lord and 11th lord signifies auspicious acquisition and gains through fixed property.",
    source_family="Parashari",
    source_reference="Phaladeepika Ch. 16, v. 10",
    source_status="VERIFIED",
    review_status="ACCEPTED",
    confidence="[HIGH]",
    dimensions=["property_acquisition"],
    tests=["test_prop_acq_02_positive", "test_prop_acq_02_negative"],
))


def pred_prop_acq_03(ctx: dict, d4: dict) -> tuple[bool, str, list[str]]:
    l4 = _get_house_lord_safe(ctx, 4)
    l2 = _get_house_lord_safe(ctx, 2)
    pm = ctx.get("planet_map", {})
    l4_data = pm.get(l4, {})
    l2_data = pm.get(l2, {})
    h4 = l4_data.get("house", 0)
    h2 = l2_data.get("house", 0)

    if h4 == 2 or h4 == h2 or _has_aspect(ctx, l4, h2):
        return True, f"4th lord {l4} connects with 2nd lord {l2} (accumulated wealth), signifying financial capital allocated to real estate.", [l4, l2]
    return False, "", []

_register(PropertyRule(
    rule_id="PROP-ACQ-03",
    version="1.0.0",
    domain="property",
    profile="parashari",
    chart_frame="D1",
    predicate=pred_prop_acq_03,
    dedupe_key="l4_l2_sambandha",
    effect="SUPPORTS",
    birth_time_sensitive=False,
    explanation_template="Dhana-sthana (2nd) connection with 4th lord signifies capital accumulation directed into immovable property.",
    source_family="Parashari",
    source_reference="BPHS Ch. 24, v. 38",
    source_status="VERIFIED",
    review_status="ACCEPTED",
    confidence="[HIGH]",
    dimensions=["property_acquisition"],
    tests=["test_prop_acq_03_positive", "test_prop_acq_03_negative"],
))


def pred_prop_acq_04(ctx: dict, d4: dict) -> tuple[bool, str, list[str]]:
    l4 = _get_house_lord_safe(ctx, 4)
    pm = ctx.get("planet_map", {})
    l4_data = pm.get(l4, {})
    if l4_data.get("house") == 4:
        return True, f"4th lord {l4} is in its own 4th house (Swakshetra), bestowing property ownership security.", [l4]
    return False, "", []

_register(PropertyRule(
    rule_id="PROP-ACQ-04",
    version="1.0.0",
    domain="property",
    profile="parashari",
    chart_frame="D1",
    predicate=pred_prop_acq_04,
    dedupe_key="l4_swakshetra",
    effect="SUPPORTS",
    birth_time_sensitive=False,
    explanation_template="4th lord situated in 4th house itself provides strong domestic foundations and reliable asset ownership comfort.",
    source_family="Parashari",
    source_reference="Saravali Ch. 34, v. 12",
    source_status="VERIFIED",
    review_status="ACCEPTED",
    confidence="[HIGH]",
    dimensions=["property_acquisition"],
    tests=["test_prop_acq_04_positive", "test_prop_acq_04_negative"],
))


def pred_prop_acq_05(ctx: dict, d4: dict) -> tuple[bool, str, list[str]]:
    l4 = _get_house_lord_safe(ctx, 4)
    pm = ctx.get("planet_map", {})
    l4_data = pm.get(l4, {})
    mars_data = pm.get("Mars", {})
    h_l4 = l4_data.get("house", 0)
    h_m = mars_data.get("house", 0)

    if h_l4 > 0 and h_m > 0:
        diff = (h_m - h_l4) % 12
        if diff in (0, 3, 6, 9):  # Conjunction or mutual Kendra
            return True, f"Mars (Bhumi-karaka) and 4th lord {l4} are in mutual Kendra/conjunction (houses {h_m} and {h_l4}), reinforcing real estate capacity.", ["Mars", l4]
    return False, "", []

_register(PropertyRule(
    rule_id="PROP-ACQ-05",
    version="1.0.0",
    domain="property",
    profile="parashari",
    chart_frame="D1",
    predicate=pred_prop_acq_05,
    dedupe_key="mars_l4_sambandha",
    effect="SUPPORTS",
    birth_time_sensitive=False,
    explanation_template="Real estate karaka Mars interacting with the 4th house lord strengthens property acquisition themes.",
    source_family="Parashari",
    source_reference="BPHS Ch. 16, v. 22",
    source_status="VERIFIED",
    review_status="ACCEPTED",
    confidence="[HIGH]",
    dimensions=["property_acquisition"],
    tests=["test_prop_acq_05_positive", "test_prop_acq_05_negative"],
))


def pred_prop_acq_06(ctx: dict, d4: dict) -> tuple[bool, str, list[str]]:
    l4 = _get_house_lord_safe(ctx, 4)
    pm = ctx.get("planet_map", {})
    l4_data = pm.get(l4, {})
    sign = l4_data.get("sign", "")
    is_deb = (sign == DEBILITATION.get(l4, ""))
    is_comb = (_is_combust(ctx, l4) is True)
    if is_deb or is_comb:
        return True, f"4th lord {l4} is {'debilitated in ' + sign if is_deb else 'combust'}, indicating obstacles in real estate ownership.", [l4]
    return False, "", []

def exc_prop_acq_06(ctx: dict, d4: dict) -> tuple[bool, str]:
    l4 = _get_house_lord_safe(ctx, 4)
    if _has_neecha_bhanga(ctx, l4):
        return True, f"Debilitation of 4th lord {l4} is cancelled via Neecha Bhanga Raja Yoga."
    return False, ""

_register(PropertyRule(
    rule_id="PROP-ACQ-06",
    version="1.0.0",
    domain="property",
    profile="parashari",
    chart_frame="D1",
    predicate=pred_prop_acq_06,
    ordered_exceptions=[exc_prop_acq_06],
    dedupe_key="l4_debilitated",
    effect="OBSTRUCTS",
    birth_time_sensitive=False,
    explanation_template="Debilitated or combust 4th lord indicates procedural hurdles, delays, or challenges in securing clear property assets.",
    source_family="Parashari",
    source_reference="Phaladeepika Ch. 16, v. 12",
    source_status="VERIFIED",
    review_status="ACCEPTED",
    confidence="[HIGH]",
    dimensions=["property_acquisition"],
    tests=["test_prop_acq_06_positive", "test_prop_acq_06_negative", "test_prop_acq_06_exception"],
))


# ===========================================================================
# DIMENSION 3: Property Sale & Disposal (property_disposal_sale)
# ===========================================================================

def pred_prop_sal_01(ctx: dict, d4: dict) -> tuple[bool, str, list[str]]:
    l4 = _get_house_lord_safe(ctx, 4)
    pm = ctx.get("planet_map", {})
    l4_data = pm.get(l4, {})
    if l4_data.get("house") == 3:  # 3rd is 12th from 4th
        return True, f"4th lord {l4} resides in 3rd house (12th from 4th sthana), indicating property conveyance, transfer, or sale symbolism.", [l4]
    return False, "", []

_register(PropertyRule(
    rule_id="PROP-SAL-01",
    version="1.0.0",
    domain="property",
    profile="parashari",
    chart_frame="D1",
    predicate=pred_prop_sal_01,
    dedupe_key="l4_in_3h",
    effect="CONDITIONAL",
    birth_time_sensitive=False,
    explanation_template="3rd house represents loss/transfer of 4th house (Bhavat Bhavam), indicating property disposal, relocation conveyance, or sale.",
    source_family="Parashari",
    source_reference="BPHS Ch. 24, v. 40",
    source_status="VERIFIED",
    review_status="ACCEPTED",
    confidence="[HIGH]",
    dimensions=["property_disposal_sale"],
    tests=["test_prop_sal_01_positive", "test_prop_sal_01_negative"],
))


def pred_prop_sal_02(ctx: dict, d4: dict) -> tuple[bool, str, list[str]]:
    l4 = _get_house_lord_safe(ctx, 4)
    pm = ctx.get("planet_map", {})
    l4_data = pm.get(l4, {})
    if l4_data.get("house") == 12:
        malefics_12 = [p for p in _get_occupants(ctx, 12) if p in NATURAL_MALEFICS]
        if malefics_12:
            return True, f"4th lord {l4} in 12th house (expenditure/relinquishment) with malefic {', '.join(malefics_12)} signifies asset liquidation or relocation disposal.", [l4] + malefics_12
    return False, "", []

_register(PropertyRule(
    rule_id="PROP-SAL-02",
    version="1.0.0",
    domain="property",
    profile="parashari",
    chart_frame="D1",
    predicate=pred_prop_sal_02,
    dedupe_key="l4_in_12h_malefic",
    effect="CONDITIONAL",
    birth_time_sensitive=False,
    explanation_template="4th lord situated in 12th house under malefic influence symbolizes liquidation, divestment, or transfer of residential assets.",
    source_family="Parashari",
    source_reference="Saravali Ch. 34",
    source_status="VERIFIED",
    review_status="ACCEPTED",
    confidence="[MEDIUM]",
    dimensions=["property_disposal_sale"],
    tests=["test_prop_sal_02_positive", "test_prop_sal_02_negative"],
))


def pred_prop_sal_03(ctx: dict, d4: dict) -> tuple[bool, str, list[str]]:
    l4 = _get_house_lord_safe(ctx, 4)
    l10 = _get_house_lord_safe(ctx, 10)
    pm = ctx.get("planet_map", {})
    l4_data = pm.get(l4, {})
    l10_data = pm.get(l10, {})
    h4 = l4_data.get("house", 0)
    h10 = l10_data.get("house", 0)

    # 10th house is 7th from 4th (transactional partner/market)
    if h4 == 10 or h10 == 4 or h4 == h10 or _has_aspect(ctx, l4, h10):
        return True, f"4th lord {l4} and 10th lord {l10} interact, indicating commercial real estate engagement and active property transactions.", [l4, l10]
    return False, "", []

_register(PropertyRule(
    rule_id="PROP-SAL-03",
    version="1.0.0",
    domain="property",
    profile="parashari",
    chart_frame="D1",
    predicate=pred_prop_sal_03,
    dedupe_key="l4_l10_sambandha",
    effect="CONDITIONAL",
    birth_time_sensitive=False,
    explanation_template="Commercial engagement with property (10th as 7th from 4th) indicates active property transactions and market dealings rather than passive holding.",
    source_family="Parashari",
    source_reference="Jataka Parijata Ch. 11",
    source_status="VERIFIED",
    review_status="ACCEPTED",
    confidence="[MEDIUM]",
    dimensions=["property_disposal_sale"],
    tests=["test_prop_sal_03_positive", "test_prop_sal_03_negative"],
))


# ===========================================================================
# DIMENSION 4: Construction & Land Development (construction_development)
# ===========================================================================

def pred_prop_con_01(ctx: dict, d4: dict) -> tuple[bool, str, list[str]]:
    pm = ctx.get("planet_map", {})
    mars = pm.get("Mars", {})
    saturn = pm.get("Saturn", {})
    h_m = mars.get("house", 0)
    h_s = saturn.get("house", 0)
    sign_m = mars.get("sign", "")

    # Mars conjunct Saturn or Mars aspected by Saturn, especially in earth sign or 4th house
    if (h_m == h_s or _has_aspect(ctx, "Saturn", h_m)) and (sign_m in EARTH_SIGNS or h_m == 4):
        return True, f"Mars (land/bricks) and Saturn (foundations/masonry) connect in {sign_m}/house {h_m}, indicating structural construction and civil development themes.", ["Mars", "Saturn"]
    return False, "", []

_register(PropertyRule(
    rule_id="PROP-CON-01",
    version="1.0.0",
    domain="property",
    profile="parashari",
    chart_frame="D1",
    predicate=pred_prop_con_01,
    dedupe_key="mars_saturn_construction",
    effect="SUPPORTS",
    birth_time_sensitive=False,
    explanation_template="Mars (land/materials) interacting with Saturn (foundations/stone/masonry) signifies physical construction and structural development.",
    source_family="Parashari",
    source_reference="BPHS Ch. 16, v. 25",
    source_status="VERIFIED",
    review_status="ACCEPTED",
    confidence="[HIGH]",
    dimensions=["construction_development"],
    tests=["test_prop_con_01_positive", "test_prop_con_01_negative"],
))


def pred_prop_con_02(ctx: dict, d4: dict) -> tuple[bool, str, list[str]]:
    h_signs = ctx.get("house_signs", {})
    sign4 = h_signs.get(4, "")
    l4 = _get_house_lord_safe(ctx, 4)
    pm = ctx.get("planet_map", {})
    l4_sign = pm.get(l4, {}).get("sign", "")

    if sign4 in EARTH_SIGNS or l4_sign in EARTH_SIGNS:
        return True, f"4th house or lord in Earth sign ({sign4 or l4_sign}) emphasizes solid architectural foundations and durable immovable property.", [l4]
    return False, "", []

_register(PropertyRule(
    rule_id="PROP-CON-02",
    version="1.0.0",
    domain="property",
    profile="parashari",
    chart_frame="D1",
    predicate=pred_prop_con_02,
    dedupe_key="earth_sign_4h",
    effect="SUPPORTS",
    birth_time_sensitive=False,
    explanation_template="Earthy signs (Taurus, Virgo, Capricorn) governing 4th house or its lord indicate solid foundations, durable masonry, and land development.",
    source_family="Parashari",
    source_reference="Saravali Ch. 16",
    source_status="VERIFIED",
    review_status="ACCEPTED",
    confidence="[HIGH]",
    dimensions=["construction_development"],
    tests=["test_prop_con_02_positive", "test_prop_con_02_negative"],
))


def pred_prop_con_03(ctx: dict, d4: dict) -> tuple[bool, str, list[str]]:
    occ = _get_occupants(ctx, 4)
    if "Ketu" in occ:
        benefics_in_4 = [p for p in occ if p in NATURAL_BENEFICS]
        if not benefics_in_4:
            return True, "Ketu in 4th house indicates unconventional architecture, old/ancestral structures, extensive renovations, or solitary dwellings.", ["Ketu"]
    return False, "", []

_register(PropertyRule(
    rule_id="PROP-CON-03",
    version="1.0.0",
    domain="property",
    profile="parashari",
    chart_frame="D1",
    predicate=pred_prop_con_03,
    dedupe_key="ketu_in_4h",
    effect="CONDITIONAL",
    birth_time_sensitive=False,
    explanation_template="Ketu in 4th house symbolizes unconventional construction, vintage/heritage properties, or periodic structural remodeling.",
    source_family="Parashari",
    source_reference="Phaladeepika Ch. 16, v. 9",
    source_status="VERIFIED",
    review_status="ACCEPTED",
    confidence="[MEDIUM]",
    dimensions=["construction_development"],
    tests=["test_prop_con_03_positive", "test_prop_con_03_negative"],
))


# ===========================================================================
# DIMENSION 5: Relocation & Residence Changes (relocation_residence)
# ===========================================================================

def pred_prop_rel_01(ctx: dict, d4: dict) -> tuple[bool, str, list[str]]:
    l4 = _get_house_lord_safe(ctx, 4)
    pm = ctx.get("planet_map", {})
    l4_data = pm.get(l4, {})
    h = l4_data.get("house", 0)
    sign = l4_data.get("sign", "")
    if sign in MOVABLE_SIGNS and h in DUSTHANA:
        return True, f"4th lord {l4} in movable sign {sign} in Dusthana (house {h}) indicates frequent residence changes or living away from birthplace.", [l4]
    return False, "", []

_register(PropertyRule(
    rule_id="PROP-REL-01",
    version="1.0.0",
    domain="property",
    profile="parashari",
    chart_frame="D1",
    predicate=pred_prop_rel_01,
    dedupe_key="l4_movable_dusthana",
    effect="SUPPORTS",
    birth_time_sensitive=False,
    explanation_template="Movable 4th lord placed in Dusthana houses symbolizes displacement from native place and migratory residential habits.",
    source_family="Parashari",
    source_reference="BPHS Ch. 24, v. 42",
    source_status="VERIFIED",
    review_status="ACCEPTED",
    confidence="[HIGH]",
    dimensions=["relocation_residence"],
    tests=["test_prop_rel_01_positive", "test_prop_rel_01_negative"],
))


def pred_prop_rel_02(ctx: dict, d4: dict) -> tuple[bool, str, list[str]]:
    occ = _get_occupants(ctx, 4)
    rahu_aspect = _has_aspect(ctx, "Rahu", 4)
    if "Rahu" in occ or rahu_aspect:
        return True, "Rahu influencing 4th house indicates residing in foreign lands, distant cities, or multicultural environments.", ["Rahu"]
    return False, "", []

_register(PropertyRule(
    rule_id="PROP-REL-02",
    version="1.0.0",
    domain="property",
    profile="parashari",
    chart_frame="D1",
    predicate=pred_prop_rel_02,
    dedupe_key="rahu_in_4h",
    effect="SUPPORTS",
    birth_time_sensitive=False,
    explanation_template="Rahu influencing 4th house shifts domestic orientation toward distant regions, overseas residence, or non-traditional dwellings.",
    source_family="Parashari",
    source_reference="Saravali Ch. 34",
    source_status="VERIFIED",
    review_status="ACCEPTED",
    confidence="[HIGH]",
    dimensions=["relocation_residence"],
    tests=["test_prop_rel_02_positive", "test_prop_rel_02_negative"],
))


def pred_prop_rel_03(ctx: dict, d4: dict) -> tuple[bool, str, list[str]]:
    l4 = _get_house_lord_safe(ctx, 4)
    l12 = _get_house_lord_safe(ctx, 12)
    pm = ctx.get("planet_map", {})
    l4_data = pm.get(l4, {})
    l12_data = pm.get(l12, {})
    h4 = l4_data.get("house", 0)
    h12 = l12_data.get("house", 0)

    if h4 == 12 or h4 == h12 or _has_aspect(ctx, l4, h12):
        return True, f"4th lord {l4} forms sambandha with 12th lord {l12} (house {h4}/{h12}), indicating residence in distant regions or foreign settlements.", [l4, l12]
    return False, "", []

_register(PropertyRule(
    rule_id="PROP-REL-03",
    version="1.0.0",
    domain="property",
    profile="parashari",
    chart_frame="D1",
    predicate=pred_prop_rel_03,
    dedupe_key="l4_l12_sambandha",
    effect="SUPPORTS",
    birth_time_sensitive=False,
    explanation_template="12th house (foreign lands) sambandha with 4th lord symbolizes living away from birthplace and distant residential setup.",
    source_family="Parashari",
    source_reference="BPHS Ch. 24, v. 44",
    source_status="VERIFIED",
    review_status="ACCEPTED",
    confidence="[HIGH]",
    dimensions=["relocation_residence"],
    tests=["test_prop_rel_03_positive", "test_prop_rel_03_negative"],
))


def pred_prop_rel_04(ctx: dict, d4: dict) -> tuple[bool, str, list[str]]:
    l4 = _get_house_lord_safe(ctx, 4)
    pm = ctx.get("planet_map", {})
    l4_data = pm.get(l4, {})
    h = l4_data.get("house", 0)
    sign = l4_data.get("sign", "")
    if sign in FIXED_SIGNS and h in KENDRA:
        return True, f"4th lord {l4} in fixed sign {sign} in Kendra (house {h}) anchors native to sedentary, long-term residence.", [l4]
    return False, "", []

_register(PropertyRule(
    rule_id="PROP-REL-04",
    version="1.0.0",
    domain="property",
    profile="parashari",
    chart_frame="D1",
    predicate=pred_prop_rel_04,
    dedupe_key="l4_fixed_kendra",
    effect="OBSTRUCTS",
    birth_time_sensitive=False,
    explanation_template="4th lord in a fixed sign within Kendra houses resists frequent relocation, providing long-term residential anchorage.",
    source_family="Parashari",
    source_reference="Phaladeepika Ch. 16, v. 14",
    source_status="VERIFIED",
    review_status="ACCEPTED",
    confidence="[HIGH]",
    dimensions=["relocation_residence"],
    tests=["test_prop_rel_04_positive", "test_prop_rel_04_negative"],
))


# ===========================================================================
# DIMENSION 6: Inherited & Ancestral Property (inherited_property)
# ===========================================================================

def pred_prop_inh_01(ctx: dict, d4: dict) -> tuple[bool, str, list[str]]:
    l4 = _get_house_lord_safe(ctx, 4)
    l8 = _get_house_lord_safe(ctx, 8)
    pm = ctx.get("planet_map", {})
    l4_data = pm.get(l4, {})
    l8_data = pm.get(l8, {})
    h4 = l4_data.get("house", 0)
    h8 = l8_data.get("house", 0)

    if h8 == 4 or h4 == 8 or h4 == h8 or _has_aspect(ctx, l8, h4):
        return True, f"8th lord {l8} (inheritance) connects with 4th lord {l4} (house {h4}/{h8}), signifying ancestral property and patrimony.", [l4, l8]
    return False, "", []

_register(PropertyRule(
    rule_id="PROP-INH-01",
    version="1.0.0",
    domain="property",
    profile="parashari",
    chart_frame="D1",
    predicate=pred_prop_inh_01,
    dedupe_key="l4_l8_sambandha",
    effect="SUPPORTS",
    birth_time_sensitive=False,
    explanation_template="8th house (unearned wealth/inheritance) connecting with 4th house signifies ancestral property and patrimonial legacy.",
    source_family="Parashari",
    source_reference="BPHS Ch. 24, v. 41",
    source_status="VERIFIED",
    review_status="ACCEPTED",
    confidence="[HIGH]",
    dimensions=["inherited_property"],
    tests=["test_prop_inh_01_positive", "test_prop_inh_01_negative"],
))


def pred_prop_inh_02(ctx: dict, d4: dict) -> tuple[bool, str, list[str]]:
    l4 = _get_house_lord_safe(ctx, 4)
    l9 = _get_house_lord_safe(ctx, 9)
    pm = ctx.get("planet_map", {})
    l4_data = pm.get(l4, {})
    l9_data = pm.get(l9, {})
    h4 = l4_data.get("house", 0)
    h9 = l9_data.get("house", 0)

    if h4 == 9 or h9 == 4 or h4 == h9 or _has_aspect(ctx, l9, h4):
        return True, f"9th lord {l9} (patrimony/father) interacts with 4th lord {l4}, indicating paternal real estate preservation.", [l4, l9]
    return False, "", []

_register(PropertyRule(
    rule_id="PROP-INH-02",
    version="1.0.0",
    domain="property",
    profile="parashari",
    chart_frame="D1",
    predicate=pred_prop_inh_02,
    dedupe_key="l4_l9_sambandha",
    effect="SUPPORTS",
    birth_time_sensitive=False,
    explanation_template="9th lord (Pitru Sthana) sambandha with 4th lord reinforces ancestral patrimony and familial estate preservation.",
    source_family="Parashari",
    source_reference="Saravali Ch. 34",
    source_status="VERIFIED",
    review_status="ACCEPTED",
    confidence="[HIGH]",
    dimensions=["inherited_property"],
    tests=["test_prop_inh_02_positive", "test_prop_inh_02_negative"],
))


def pred_prop_inh_03(ctx: dict, d4: dict) -> tuple[bool, str, list[str]]:
    l8 = _get_house_lord_safe(ctx, 8)
    pm = ctx.get("planet_map", {})
    l8_data = pm.get(l8, {})
    if l8_data.get("house") == 4:
        occ = _get_occupants(ctx, 4)
        affliction = [p for p in occ if p in ("Saturn", "Rahu", "Mars") and p != l8]
        if affliction:
            return True, f"8th lord {l8} in 4th house afflicted by {', '.join(affliction)} signals legal complexities or joint family encumbrances regarding ancestral land.", [l8] + affliction
    return False, "", []

_register(PropertyRule(
    rule_id="PROP-INH-03",
    version="1.0.0",
    domain="property",
    profile="parashari",
    chart_frame="D1",
    predicate=pred_prop_inh_03,
    dedupe_key="l8_afflicted_4h",
    effect="CONDITIONAL",
    birth_time_sensitive=False,
    explanation_template="Afflicted inheritance indicator in 4th house signals procedural complexities, probate obligations, or joint family delays regarding ancestral assets.",
    source_family="Parashari",
    source_reference="Phaladeepika Ch. 16, v. 15",
    source_status="VERIFIED",
    review_status="ACCEPTED",
    confidence="[MEDIUM]",
    dimensions=["inherited_property"],
    tests=["test_prop_inh_03_positive", "test_prop_inh_03_negative"],
))


# ===========================================================================
# DIMENSION 7: Financial Obligations Associated with Property (property_obligations)
# ===========================================================================

def pred_prop_obl_01(ctx: dict, d4: dict) -> tuple[bool, str, list[str]]:
    l4 = _get_house_lord_safe(ctx, 4)
    l6 = _get_house_lord_safe(ctx, 6)
    pm = ctx.get("planet_map", {})
    l4_data = pm.get(l4, {})
    l6_data = pm.get(l6, {})
    h4 = l4_data.get("house", 0)
    h6 = l6_data.get("house", 0)

    if h4 == 6 or h6 == 4 or h4 == h6 or _has_aspect(ctx, l6, h4):
        return True, f"4th lord {l4} connects with 6th house/lord {l6} (Rina / liabilities), indicating property acquisition via borrowing or mortgages.", [l4, l6]
    return False, "", []

_register(PropertyRule(
    rule_id="PROP-OBL-01",
    version="1.0.0",
    domain="property",
    profile="parashari",
    chart_frame="D1",
    predicate=pred_prop_obl_01,
    dedupe_key="l4_in_6h",
    effect="CONDITIONAL",
    birth_time_sensitive=False,
    explanation_template="4th-6th connection symbolizes property financed through debt gearing or institutional encumbrances (evaluated symbolically, not as a loan approval).",
    source_family="Parashari",
    source_reference="BPHS Ch. 24, v. 43",
    source_status="VERIFIED",
    review_status="ACCEPTED",
    confidence="[HIGH]",
    dimensions=["property_obligations"],
    tests=["test_prop_obl_01_positive", "test_prop_obl_01_negative"],
))


def pred_prop_obl_02(ctx: dict, d4: dict) -> tuple[bool, str, list[str]]:
    l6 = _get_house_lord_safe(ctx, 6)
    pm = ctx.get("planet_map", {})
    mars_data = pm.get("Mars", {})
    l6_data = pm.get(l6, {})
    h_m = mars_data.get("house", 0)
    h_6 = l6_data.get("house", 0)

    if h_m == 6 or h_m == h_6:
        return True, f"Mars (Bhumi-karaka) in 6th house or conjunct 6th lord {l6} emphasizes due diligence regarding real estate liabilities.", ["Mars", l6]
    return False, "", []

_register(PropertyRule(
    rule_id="PROP-OBL-02",
    version="1.0.0",
    domain="property",
    profile="parashari",
    chart_frame="D1",
    predicate=pred_prop_obl_02,
    dedupe_key="mars_in_6h",
    effect="CONDITIONAL",
    birth_time_sensitive=False,
    explanation_template="Mars connecting with 6th house highlights financial gearing and diligence considerations in property transactions.",
    source_family="Parashari",
    source_reference="Saravali Ch. 34",
    source_status="VERIFIED",
    review_status="ACCEPTED",
    confidence="[MEDIUM]",
    dimensions=["property_obligations"],
    tests=["test_prop_obl_02_positive", "test_prop_obl_02_negative"],
))


# ===========================================================================
# DIMENSION 8: D4 Chaturthamsa Support Rules (property_acquisition)
# ===========================================================================

def pred_prop_d4_01(ctx: dict, d4: dict) -> tuple[bool, str, list[str]]:
    d4_hl = d4.get("house_lords", {})
    d4_l1 = d4_hl.get(1, "")
    d4_l4 = d4_hl.get(4, "")
    d4_pm = d4.get("planet_map", {})

    l1_h = d4_pm.get(d4_l1, {}).get("house", 0)
    l4_h = d4_pm.get(d4_l4, {}).get("house", 0)

    strong = []
    if l1_h in (KENDRA | TRIKONA):
        strong.append(f"D4 Lagna lord {d4_l1} in H{l1_h}")
    if l4_h in (KENDRA | TRIKONA):
        strong.append(f"D4 4th lord {d4_l4} in H{l4_h}")

    if strong:
        return True, f"Chaturthamsa (D4) shows auspicious asset anchorage: {', '.join(strong)}.", [d4_l1, d4_l4]
    return False, "", []

_register(PropertyRule(
    rule_id="PROP-D4-01",
    version="1.0.0",
    domain="property",
    profile="parashari",
    chart_frame="D4",
    predicate=pred_prop_d4_01,
    dedupe_key="d4_lord_strong",
    effect="SUPPORTS",
    birth_time_sensitive=True,
    explanation_template="Chaturthamsa (D4) divisional verification confirms foundational resilience regarding immovable assets.",
    source_family="Parashari",
    source_reference="BPHS Ch. 6, v. 5-6",
    source_status="VERIFIED",
    review_status="ACCEPTED",
    confidence="[HIGH]",
    dimensions=["property_acquisition"],
    tests=["test_prop_d4_01_positive", "test_prop_d4_01_negative"],
))


def pred_prop_d4_02(ctx: dict, d4: dict) -> tuple[bool, str, list[str]]:
    d4_pm = d4.get("planet_map", {})
    mars_d4 = d4_pm.get("Mars", {})
    h = mars_d4.get("house", 0)
    sign = mars_d4.get("sign", "")
    is_own = sign in OWN_SIGNS.get("Mars", set())
    is_exalted = (sign == EXALTATION.get("Mars", ""))

    if h in (KENDRA | TRIKONA) and (is_own or is_exalted):
        return True, f"Mars in D4 Chaturthamsa is strong in house {h} in {'own' if is_own else 'exalted'} sign {sign}, reinforcing fixed asset support.", ["Mars"]
    return False, "", []

_register(PropertyRule(
    rule_id="PROP-D4-02",
    version="1.0.0",
    domain="property",
    profile="parashari",
    chart_frame="D4",
    predicate=pred_prop_d4_02,
    dedupe_key="d4_mars_strong",
    effect="SUPPORTS",
    birth_time_sensitive=True,
    explanation_template="Mars exalted or in own sign within Chaturthamsa (D4) Kendras/Trikonas reinforces real estate capacity.",
    source_family="Parashari",
    source_reference="BPHS Ch. 6, v. 5-6",
    source_status="VERIFIED",
    review_status="ACCEPTED",
    confidence="[HIGH]",
    dimensions=["property_acquisition"],
    tests=["test_prop_d4_02_positive", "test_prop_d4_02_negative"],
))


# ---------------------------------------------------------------------------
# Evaluator Engine
# ---------------------------------------------------------------------------

def evaluate_property_rules(ctx: dict, profile: str = "parashari") -> dict[str, Any]:
    """
    Evaluate the Property & Residence Rule Pack deterministically across 7 dimensions.

    Parameters:
        ctx: Unified ChartContext dictionary (D1 chart, planet_map, house_lords, etc.)
        profile: Interpretive profile ('parashari' standard)

    Returns:
        Structured evaluation dictionary containing:
          - evidence_ledger: Contributing rules, predicates, exceptions, deduplication
          - dimensions: Scores across the 7 separate property dimensions
          - d4_chart: Calculated Chaturthamsa positions and houses
          - safety_disclaimer: Non-deterministic legal/financial disclaimer
    """
    d4_chart = build_d4_chart(ctx)

    evidence_ledger: list[dict[str, Any]] = []
    seen_dedupe_keys: set[str] = set()
    unverified_exceptions: list[dict[str, Any]] = []

    dimension_scores: dict[str, float] = {d: 50.0 for d in PROPERTY_DIMENSIONS}

    for rule in PROPERTY_RULES_CATALOG:
        if not rule.enabled:
            continue
        if rule.profile != profile and rule.profile != "all":
            continue

        # Deduplication check
        if rule.dedupe_key and rule.dedupe_key in seen_dedupe_keys:
            continue

        passed, reason, planets = rule.predicate(ctx, d4_chart)
        if not passed:
            continue

        # Check ordered exceptions
        exception_triggered = False
        exception_reason = ""
        unverified_rule_exceptions = []
        for exc in rule.ordered_exceptions:
            exc_hit, exc_msg = exc(ctx, d4_chart)
            if exc_hit is True:
                exception_triggered = True
                exception_reason = exc_msg
                break
            elif exc_hit is None:
                unverified_rule_exceptions.append({
                    "rule_id": rule.rule_id,
                    "reason": exc_msg,
                })

        if exception_triggered:
            evidence_ledger.append({
                "rule_id": rule.rule_id,
                "version": rule.version,
                "effect": "EXCEPTION",
                "exception_reason": exception_reason,
                "dimensions": rule.dimensions,
                "confidence": rule.confidence,
                "chart_frame": rule.chart_frame,
                "birth_time_sensitive": rule.birth_time_sensitive,
                "source_reference": rule.source_reference,
            })
            if rule.dedupe_key:
                seen_dedupe_keys.add(rule.dedupe_key)
            continue

        if unverified_rule_exceptions:
            unverified_exceptions.extend(unverified_rule_exceptions)
            ctx.setdefault("unverified_exceptions", []).extend(unverified_rule_exceptions)

        if rule.dedupe_key:
            seen_dedupe_keys.add(rule.dedupe_key)

        rule_entry = {
            "rule_id": rule.rule_id,
            "version": rule.version,
            "effect": rule.effect,
            "reason": reason,
            "planets": planets,
            "dimensions": rule.dimensions,
            "confidence": rule.confidence,
            "chart_frame": rule.chart_frame,
            "birth_time_sensitive": rule.birth_time_sensitive,
            "source_reference": rule.source_reference,
        }
        if unverified_rule_exceptions:
            rule_entry["unverified_exceptions"] = [e["reason"] for e in unverified_rule_exceptions]
        evidence_ledger.append(rule_entry)

        # Dimension delta
        delta = 6.0 if rule.effect == "SUPPORTS" else (-6.0 if rule.effect == "OBSTRUCTS" else 3.0)
        for dim in rule.dimensions:
            if dim in dimension_scores:
                dimension_scores[dim] = max(10.0, min(95.0, dimension_scores[dim] + delta))

    active_rules_count = len([e for e in evidence_ledger if e["effect"] in ("SUPPORTS", "OBSTRUCTS", "CONDITIONAL")])
    overall_score = round(sum(dimension_scores.values()) / len(dimension_scores), 1)

    return {
        "domain": "Property & Residence",
        "active_rules_count": active_rules_count,
        "evidence_ledger": evidence_ledger,
        "unverified_exceptions": unverified_exceptions,
        "dimensions": dimension_scores,
        "overall_score": overall_score,
        "d4_chart": d4_chart,
        "safety_disclaimer": PROPERTY_SAFETY_DISCLAIMER,
    }
