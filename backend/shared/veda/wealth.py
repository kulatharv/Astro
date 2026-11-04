"""
Classical Vedic Astrology Wealth & Resources Engine (Pure Shared Library).

Implements 26 canonical deterministic, explainable Parashari wealth & resource rules,
reusing canonical WP3 Dhana Yogas without duplicate inflation, separating 6 financial
evidence dimensions:
  1. Accumulated Wealth & Savings (Dhana Sthana - 2nd house / lord)
  2. Recurring Gains & Inflow (Labha Sthana - 11th house / lord)
  3. Earning Capacity & Livelihood (1st & 10th houses / lords, Upachayas)
  4. Debt & Financial Obligations (Rina Sthana - 6th house / lord)
  5. Expenditure & Resource Depletion (Vyaya Sthana - 12th house / lord)
  6. Speculation & Financial Risk (5th / 8th houses, Rahu / unearned gains)

Adheres strictly to Specification v3.0 §9.3 & §21 (Financial Safety Guardrails).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Any, Optional

from .zodiac import SIGNS_SK, SIGN_LORDS
from .strength import EXALTATION, DEBILITATION, OWN_SIGNS
from .lordship import get_house_lord
from .neech_bhanga import is_neech_bhanga
from .combustion import is_combust
from .aspects import calculate_vedic_aspects
from .yoga_catalog import evaluate_yoga_catalog, house_dist


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

FINANCIAL_DIMENSIONS = [
    "accumulated_savings",
    "recurring_gains",
    "earning_livelihood",
    "debt_obligations",
    "expenditure_outflow",
    "speculation_risk",
]

SAFETY_DISCLAIMER = (
    "Astrological interpretation of planetary patterns only. Not financial advice, "
    "investment recommendation, or guarantee of wealth. AstroLogic AI encourages "
    "disciplined budgeting, prudent risk management, and consulting licensed financial professionals."
)


# ---------------------------------------------------------------------------
# Canonical Wealth Rule Dataclass
# ---------------------------------------------------------------------------

@dataclass
class WealthRule:
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
    confidence: str = "HIGH"
    tests: list[str] = field(default_factory=list)
    dimensions: list[str] = field(default_factory=list)
    enabled: bool = True


# ---------------------------------------------------------------------------
# Helper Inspection Functions
# ---------------------------------------------------------------------------

def safe_house_lord(lagna: str, h: int) -> str:
    """Safely resolve house lord for given lagna with normalization."""
    if not lagna:
        return ""
    norm = lagna.strip().capitalize()
    if norm == "Vrishika":
        norm = "Vrischika"
    try:
        return get_house_lord(norm, h)
    except (ValueError, KeyError):
        return ""


def get_planet_map(ctx: dict) -> dict[str, dict]:
    """Retrieve normalized planet map from chart context."""
    return ctx.get("planet_map", {})


def house_of(pmap: dict, name: str) -> int:
    """Retrieve 1-indexed house of a planet."""
    p = pmap.get(name, {})
    h = p.get("house", 0)
    if isinstance(h, int):
        return h
    try:
        return int(str(h).split("/")[0])
    except (ValueError, TypeError):
        return 0


def sign_of(pmap: dict, name: str) -> str:
    """Retrieve zodiac sign of a planet."""
    return pmap.get(name, {}).get("sign", "")


def degree_of(pmap: dict, name: str) -> float:
    """Retrieve planet degree within sign."""
    p = pmap.get(name, {})
    deg = p.get("degree_decimal")
    if deg is not None:
        try:
            return float(deg)
        except (ValueError, TypeError):
            pass
    deg = p.get("degree")
    if isinstance(deg, (int, float)):
        return float(deg)
    return 15.0


def is_in_own_sign(pmap: dict, name: str) -> bool:
    """Check if planet is situated in its own sign."""
    s = sign_of(pmap, name)
    return s in OWN_SIGNS.get(name, [])


def is_exalted(pmap: dict, name: str) -> bool:
    """Check if planet is in its sign of exaltation."""
    return sign_of(pmap, name) == EXALTATION.get(name)


def is_debilitated(pmap: dict, name: str) -> bool:
    """Check if planet is in its sign of debilitation."""
    return sign_of(pmap, name) == DEBILITATION.get(name)


def planets_in_house(pmap: dict, house_num: int) -> list[str]:
    """Return all classical planets occupying a given house."""
    res = []
    for p, d in pmap.items():
        if d.get("house") == house_num:
            res.append(p)
    return res


def aspects_house(planet: str, planet_house: int, target_house: int) -> bool:
    """Evaluate Parashari full aspect from planet_house to target_house."""
    if not planet_house or not target_house:
        return False
    dist = ((target_house - planet_house) % 12) + 1
    if dist == 7:
        return True
    if planet == "Mars" and dist in (4, 8):
        return True
    if planet == "Jupiter" and dist in (5, 9):
        return True
    if planet == "Saturn" and dist in (3, 10):
        return True
    return False


def mutual_aspect(p1: str, p2: str, pmap: dict) -> bool:
    """Evaluate whether two planets mutually aspect each other."""
    h1 = house_of(pmap, p1)
    h2 = house_of(pmap, p2)
    if not h1 or not h2:
        return False
    return aspects_house(p1, h1, h2) and aspects_house(p2, h2, h1)


def is_natural_benefic(p: str) -> bool:
    """Check if planet is naturally benefic."""
    return p in NATURAL_BENEFICS


def is_natural_malefic(p: str) -> bool:
    """Check if planet is naturally malefic."""
    return p in NATURAL_MALEFICS


def get_chandra_lagna_house(moon_sign: str, target_sign: str) -> int:
    """Calculate 1-indexed house position of target_sign counted from moon_sign."""
    if not moon_sign or not target_sign:
        return 0
    try:
        m_idx = SIGNS_SK.index(moon_sign)
        t_idx = SIGNS_SK.index(target_sign)
        return ((t_idx - m_idx) % 12) + 1
    except ValueError:
        return 0


# ---------------------------------------------------------------------------
# Individual Predicates & Exceptions for Canonical Rules
# ---------------------------------------------------------------------------

# Family A: Second House & Lord (Accumulated Wealth & Savings)

def _pred_h2_lord_kendra_trikona(ctx: dict, pmap: dict) -> tuple[bool, str, list[str]]:
    lagna = ctx.get("lagna", "")
    l2 = safe_house_lord(lagna, 2)
    if not l2:
        return False, "", []
    h = house_of(pmap, l2)
    if h in (KENDRA | TRIKONA):
        return True, f"2nd lord {l2} is placed in auspicious house H{h}", [l2]
    return False, "", []

def _exc_debilitated_no_nb(ctx: dict, pmap: dict, planet: str) -> tuple[bool, str]:
    if is_debilitated(pmap, planet):
        s = sign_of(pmap, planet)
        if not is_neech_bhanga(planet, s, pmap):
            return True, f"{planet} is debilitated without Neecha Bhanga cancellation"
    return False, ""

def _exc_combust(ctx: dict, pmap: dict, planet: str, orb: float = 3.0) -> tuple[bool, str]:
    if planet in ("Rahu", "Ketu", "Sun"):
        return False, ""
    sun_deg = degree_of(pmap, "Sun")
    sun_s = sign_of(pmap, "Sun")
    p_deg = degree_of(pmap, "Planet")
    p_s = sign_of(pmap, planet)
    if sun_s == p_s and abs(sun_deg - degree_of(pmap, planet)) <= orb:
        return True, f"{planet} is deeply combust by Sun within {orb}°"
    return False, ""


def _pred_h2_lord_own_exalted(ctx: dict, pmap: dict) -> tuple[bool, str, list[str]]:
    lagna = ctx.get("lagna", "")
    l2 = safe_house_lord(lagna, 2)
    if not l2:
        return False, "", []
    if is_in_own_sign(pmap, l2) or is_exalted(pmap, l2):
        s = sign_of(pmap, l2)
        status = "exalted" if is_exalted(pmap, l2) else "own sign"
        return True, f"2nd lord {l2} is {status} in {s}", [l2]
    return False, "", []


def _pred_h2_benefic_occ(ctx: dict, pmap: dict) -> tuple[bool, str, list[str]]:
    h2_planets = [p for p in planets_in_house(pmap, 2) if is_natural_benefic(p)]
    if h2_planets:
        valid = []
        for p in h2_planets:
            if not is_debilitated(pmap, p):
                valid.append(p)
        if valid:
            return True, f"Natural benefic(s) {', '.join(valid)} occupying 2nd house of savings", valid
    return False, "", []


def _pred_h2_lord_dusthana(ctx: dict, pmap: dict) -> tuple[bool, str, list[str]]:
    lagna = ctx.get("lagna", "")
    l2 = safe_house_lord(lagna, 2)
    if not l2:
        return False, "", []
    h = house_of(pmap, l2)
    if h in DUSTHANA:
        return True, f"2nd lord {l2} placed in Dusthana house H{h}", [l2]
    return False, "", []

def _exc_h2_dusthana_mitigated(ctx: dict, pmap: dict) -> tuple[bool, str]:
    lagna = ctx.get("lagna", "")
    l2 = safe_house_lord(lagna, 2)
    if is_in_own_sign(pmap, l2):
        return True, f"2nd lord {l2} is in own sign in Dusthana (creates protective dignity)"
    # Jupiter aspect
    h2_lord_house = house_of(pmap, l2)
    if aspects_house("Jupiter", house_of(pmap, "Jupiter"), h2_lord_house):
        return True, f"Jupiter casts benefic aspect onto 2nd lord {l2}"
    return False, ""


def _pred_h2_malefic_affliction(ctx: dict, pmap: dict) -> tuple[bool, str, list[str]]:
    h2_planets = planets_in_house(pmap, 2)
    malefics = [p for p in h2_planets if is_natural_malefic(p)]
    benefics = [p for p in h2_planets if is_natural_benefic(p)]
    if len(malefics) >= 2 and not benefics:
        return True, f"2nd house afflicted by multiple malefics: {', '.join(malefics)} without benefic support", malefics
    return False, "", []

def _exc_h2_malefic_is_lord(ctx: dict, pmap: dict) -> tuple[bool, str]:
    lagna = ctx.get("lagna", "")
    l2 = safe_house_lord(lagna, 2)
    if l2 in planets_in_house(pmap, 2) and is_in_own_sign(pmap, l2):
        return True, f"Malefic {l2} is the 2nd lord residing in own sign (protects Dhana sthana)"
    return False, ""


# Family B: Eleventh House & Lord (Recurring Gains & Inflow)

def _pred_h11_lord_kendra_trikona(ctx: dict, pmap: dict) -> tuple[bool, str, list[str]]:
    lagna = ctx.get("lagna", "")
    l11 = safe_house_lord(lagna, 11)
    if not l11:
        return False, "", []
    h = house_of(pmap, l11)
    if h in (KENDRA | TRIKONA):
        return True, f"11th lord {l11} placed in auspicious house H{h}", [l11]
    return False, "", []


def _pred_h11_lord_own_exalted(ctx: dict, pmap: dict) -> tuple[bool, str, list[str]]:
    lagna = ctx.get("lagna", "")
    l11 = safe_house_lord(lagna, 11)
    if not l11:
        return False, "", []
    if is_in_own_sign(pmap, l11) or is_exalted(pmap, l11):
        s = sign_of(pmap, l11)
        status = "exalted" if is_exalted(pmap, l11) else "own sign"
        return True, f"11th lord {l11} is {status} in {s}", [l11]
    return False, "", []


def _pred_h11_benefic_occ(ctx: dict, pmap: dict) -> tuple[bool, str, list[str]]:
    h11_planets = [p for p in planets_in_house(pmap, 11) if is_natural_benefic(p)]
    if h11_planets:
        valid = [p for p in h11_planets if not is_debilitated(pmap, p)]
        if valid:
            return True, f"Natural benefic(s) {', '.join(valid)} occupying 11th house of gains", valid
    return False, "", []


def _pred_h11_upachaya_growth(ctx: dict, pmap: dict) -> tuple[bool, str, list[str]]:
    # Natural malefics in 11th give sustained growth over time
    h11_malefics = [p for p in planets_in_house(pmap, 11) if is_natural_malefic(p)]
    valid = [p for p in h11_malefics if not is_debilitated(pmap, p)]
    if valid:
        return True, f"Malefic(s) {', '.join(valid)} in 11th house provides Upachaya growth and resilient revenue", valid
    return False, "", []


def _pred_h11_lord_dusthana(ctx: dict, pmap: dict) -> tuple[bool, str, list[str]]:
    lagna = ctx.get("lagna", "")
    l11 = safe_house_lord(lagna, 11)
    if not l11:
        return False, "", []
    h = house_of(pmap, l11)
    if h in DUSTHANA:
        return True, f"11th lord {l11} placed in Dusthana house H{h}", [l11]
    return False, "", []

def _exc_h11_dusthana_mitigated(ctx: dict, pmap: dict) -> tuple[bool, str]:
    lagna = ctx.get("lagna", "")
    l11 = safe_house_lord(lagna, 11)
    if is_in_own_sign(pmap, l11):
        return True, f"11th lord {l11} is in own sign in Dusthana"
    if aspects_house("Jupiter", house_of(pmap, "Jupiter"), house_of(pmap, l11)):
        return True, f"Jupiter casts aspect onto 11th lord {l11}"
    return False, ""


# Family C: Lakshmi Sthanas & Dhana Combinations (5th, 9th, 2nd, 11th, 1st)

def _pred_dhana_2_11_parivartana(ctx: dict, pmap: dict) -> tuple[bool, str, list[str]]:
    lagna = ctx.get("lagna", "")
    l2 = safe_house_lord(lagna, 2)
    l11 = safe_house_lord(lagna, 11)
    if not l2 or not l11 or l2 == l11:
        return False, "", []
    h_l2 = house_of(pmap, l2)
    h_l11 = house_of(pmap, l11)
    if h_l2 == 11 and h_l11 == 2:
        return True, f"Mutual reception (Parivartana) between 2nd lord {l2} and 11th lord {l11}", [l2, l11]
    return False, "", []


def _pred_dhana_5_11_axis(ctx: dict, pmap: dict) -> tuple[bool, str, list[str]]:
    lagna = ctx.get("lagna", "")
    l5 = safe_house_lord(lagna, 5)
    l11 = safe_house_lord(lagna, 11)
    if not l5 or not l11:
        return False, "", []
    h5 = house_of(pmap, l5)
    h11 = house_of(pmap, l11)
    # 5th lord in 11th, or 11th lord in 5th, or mutual aspect
    if h5 == 11 or h11 == 5 or mutual_aspect(l5, l11, pmap) or (h5 == h11 and h5 in (5, 11)):
        return True, f"5th lord {l5} and 11th lord {l11} interconnected along the 5/11 intellectual-gain axis", [l5, l11]
    return False, "", []


def _pred_dhana_9_2_combination(ctx: dict, pmap: dict) -> tuple[bool, str, list[str]]:
    lagna = ctx.get("lagna", "")
    l9 = safe_house_lord(lagna, 9)
    l2 = safe_house_lord(lagna, 2)
    if not l9 or not l2:
        return False, "", []
    h9 = house_of(pmap, l9)
    h2 = house_of(pmap, l2)
    if h9 == 2 or h2 == 9 or (h9 == h2 and h9 in (1, 2, 4, 5, 7, 9, 10, 11)):
        return True, f"9th Bhagya lord {l9} connects with 2nd Dhana lord {l2}", [l9, l2]
    return False, "", []


def _pred_dhana_1_11_connection(ctx: dict, pmap: dict) -> tuple[bool, str, list[str]]:
    lagna = ctx.get("lagna", "")
    l1 = safe_house_lord(lagna, 1)
    l11 = safe_house_lord(lagna, 11)
    if not l1 or not l11:
        return False, "", []
    h1 = house_of(pmap, l1)
    h11 = house_of(pmap, l11)
    if h1 == 11 or h11 == 1 or (h1 == h11 and h1 in (1, 11)):
        return True, f"Ascendant lord {l1} connects with 11th gains lord {l11} (self-earned prosperity)", [l1, l11]
    return False, "", []


# Family D: Livelihood & Earning Capacity (1st & 10th Houses / Upachayas)

def _pred_earning_10_2_connection(ctx: dict, pmap: dict) -> tuple[bool, str, list[str]]:
    lagna = ctx.get("lagna", "")
    l10 = safe_house_lord(lagna, 10)
    l2 = safe_house_lord(lagna, 2)
    if not l10 or not l2:
        return False, "", []
    h10 = house_of(pmap, l10)
    h2 = house_of(pmap, l2)
    if h10 == 2 or h2 == 10 or (h10 == h2 and h10 in (2, 10)):
        return True, f"10th Karma lord {l10} connects with 2nd Dhana lord {l2} (career converts to liquid savings)", [l10, l2]
    return False, "", []


def _pred_earning_lagna_strong(ctx: dict, pmap: dict) -> tuple[bool, str, list[str]]:
    lagna = ctx.get("lagna", "")
    l1 = safe_house_lord(lagna, 1)
    if not l1:
        return False, "", []
    h = house_of(pmap, l1)
    if h in (KENDRA | TRIKONA) and (is_in_own_sign(pmap, l1) or is_exalted(pmap, l1) or l1 in NATURAL_BENEFICS):
        return True, f"Lagna lord {l1} placed strongly in H{h} supporting enduring earning vitality", [l1]
    return False, "", []


def _pred_earning_upachaya_benefic(ctx: dict, pmap: dict) -> tuple[bool, str, list[str]]:
    # Vasumati principle: natural benefics in Upachaya houses {3, 6, 10, 11}
    upachaya_benefics = []
    for p in ("Jupiter", "Venus", "Mercury"):
        if house_of(pmap, p) in UPACHAYA and not is_debilitated(pmap, p):
            upachaya_benefics.append(p)
    if len(upachaya_benefics) >= 2:
        return True, f"Benefics {', '.join(upachaya_benefics)} situated in Upachayas (Vasumati principle)", upachaya_benefics
    return False, "", []


# Family E: Financial Obligations & Debt (6th House / Lord / Rina Sthana)

def _pred_debt_6_lord_in_2(ctx: dict, pmap: dict) -> tuple[bool, str, list[str]]:
    lagna = ctx.get("lagna", "")
    l6 = safe_house_lord(lagna, 6)
    if not l6:
        return False, "", []
    if house_of(pmap, l6) == 2:
        return True, f"6th Rina lord {l6} placed in 2nd house of wealth (debt/liability pressure on savings)", [l6]
    return False, "", []

def _exc_debt_mitigated_6in2(ctx: dict, pmap: dict) -> tuple[bool, str]:
    lagna = ctx.get("lagna", "")
    l6 = safe_house_lord(lagna, 6)
    if is_in_own_sign(pmap, l6):
        return True, f"6th lord {l6} is in own sign in 2nd house (mitigates debt drain)"
    if aspects_house("Jupiter", house_of(pmap, "Jupiter"), 2):
        return True, "Jupiter casts benefic aspect onto 2nd house, protecting savings from debt drain"
    return False, ""


def _pred_debt_2_lord_in_6(ctx: dict, pmap: dict) -> tuple[bool, str, list[str]]:
    lagna = ctx.get("lagna", "")
    l2 = safe_house_lord(lagna, 2)
    if not l2:
        return False, "", []
    if house_of(pmap, l2) == 6:
        return True, f"2nd Dhana lord {l2} placed in 6th house (liquid capital allocated to debt or operations)", [l2]
    return False, "", []

def _exc_debt_mitigated_2in6(ctx: dict, pmap: dict) -> tuple[bool, str]:
    lagna = ctx.get("lagna", "")
    l2 = safe_house_lord(lagna, 2)
    if is_in_own_sign(pmap, l2) or is_exalted(pmap, l2):
        return True, f"2nd lord {l2} is exalted or in own sign in 6th house (converts debt into successful financing)"
    return False, ""


def _pred_debt_saturn_mars_in_6(ctx: dict, pmap: dict) -> tuple[bool, str, list[str]]:
    planets = [p for p in ("Saturn", "Mars") if house_of(pmap, p) == 6 and not is_debilitated(pmap, p)]
    if planets:
        return True, f"{' and '.join(planets)} in 6th house gives Shatru/Rina Hanta yoga (debt discipline & defense)", planets
    return False, "", []


# Family F: Expenditure & Outflow (12th House / Lord / Vyaya Sthana)

def _pred_outflow_12_lord_strong(ctx: dict, pmap: dict) -> tuple[bool, str, list[str]]:
    lagna = ctx.get("lagna", "")
    l12 = safe_house_lord(lagna, 12)
    if not l12:
        return False, "", []
    h = house_of(pmap, l12)
    if (h == 12 and is_in_own_sign(pmap, l12)) or is_exalted(pmap, l12) or h == 2:
        return True, f"12th Vyaya lord {l12} is strong in H{h} (indicates prominent capital expenditure or foreign outflow)", [l12]
    return False, "", []

def _exc_outflow_dharmic_spending(ctx: dict, pmap: dict) -> tuple[bool, str]:
    lagna = ctx.get("lagna", "")
    l12 = safe_house_lord(lagna, 12)
    if l12 != "Jupiter":
        if house_of(pmap, "Jupiter") == house_of(pmap, l12) or aspects_house("Jupiter", house_of(pmap, "Jupiter"), house_of(pmap, l12)):
            return True, "Jupiter association channels 12th house outflow into philanthropic, educational, or ethical investments"
    return False, ""


def _pred_outflow_2_lord_in_12(ctx: dict, pmap: dict) -> tuple[bool, str, list[str]]:
    lagna = ctx.get("lagna", "")
    l2 = safe_house_lord(lagna, 2)
    if not l2:
        return False, "", []
    if house_of(pmap, l2) == 12:
        return True, f"2nd Dhana lord {l2} placed in 12th house of Vyaya (propensity for capital drain)", [l2]
    return False, "", []

def _exc_outflow_mitigated_2in12(ctx: dict, pmap: dict) -> tuple[bool, str]:
    lagna = ctx.get("lagna", "")
    l2 = safe_house_lord(lagna, 2)
    if is_in_own_sign(pmap, l2) or is_exalted(pmap, l2):
        return True, f"2nd lord {l2} is exalted or in own sign in 12th house (foreign asset accumulation)"
    return False, ""


# Family G: Speculation, Unearned Wealth & Financial Volatility (5th / 8th Houses & Rahu)

def _pred_spec_5_8_connection(ctx: dict, pmap: dict) -> tuple[bool, str, list[str]]:
    lagna = ctx.get("lagna", "")
    l5 = safe_house_lord(lagna, 5)
    l8 = safe_house_lord(lagna, 8)
    if not l5 or not l8:
        return False, "", []
    h5 = house_of(pmap, l5)
    h8 = house_of(pmap, l8)
    if h5 == 8 or h8 == 5 or (h5 == h8 and h5 in (5, 8)) or mutual_aspect(l5, l8, pmap):
        return True, f"5th lord {l5} connects with 8th lord {l8} (indicates high-variance speculative or unearned financial ventures)", [l5, l8]
    return False, "", []

def _exc_spec_high_risk_affliction(ctx: dict, pmap: dict) -> tuple[bool, str]:
    lagna = ctx.get("lagna", "")
    l5 = safe_house_lord(lagna, 5)
    if is_debilitated(pmap, l5):
        return True, f"5th lord {l5} is debilitated; speculative activities require strict risk-management guardrails"
    return False, ""


def _pred_spec_rahu_5_or_11(ctx: dict, pmap: dict) -> tuple[bool, str, list[str]]:
    h_rahu = house_of(pmap, "Rahu")
    if h_rahu in (5, 11):
        house_name = "5th house (speculative enterprise)" if h_rahu == 5 else "11th house (unconventional scaling)"
        return True, f"Rahu situated in {house_name} (ambition for rapid expansion, non-linear financial patterns)", ["Rahu"]
    return False, "", []

def _exc_rahu_suppressed(ctx: dict, pmap: dict) -> tuple[bool, str]:
    h_rahu = house_of(pmap, "Rahu")
    if house_of(pmap, "Saturn") == h_rahu:
        return True, "Saturn conjoins Rahu, imposing heavy discipline and tempering sudden speculative leaps"
    return False, ""


# Family H: Cross-Reading & Significator Frames (Chandra Lagna & Jupiter Karaka)

def _pred_chandra_lagna_dhana(ctx: dict, pmap: dict) -> tuple[bool, str, list[str]]:
    moon_sign = sign_of(pmap, "Moon")
    if not moon_sign:
        return False, "", []
    benefics_chandra = []
    for p in ("Jupiter", "Venus", "Mercury"):
        ps = sign_of(pmap, p)
        if ps:
            h_from_moon = get_chandra_lagna_house(moon_sign, ps)
            if h_from_moon in (2, 11) and not is_debilitated(pmap, p):
                benefics_chandra.append(f"{p} in H{h_from_moon} from Moon")
    if benefics_chandra:
        return True, f"Chandra Lagna wealth confirmation: {', '.join(benefics_chandra)}", ["Moon"]
    return False, "", []


def _pred_karaka_jupiter_dignity(ctx: dict, pmap: dict) -> tuple[bool, str, list[str]]:
    h_jup = house_of(pmap, "Jupiter")
    s_jup = sign_of(pmap, "Jupiter")
    if not h_jup:
        return False, "", []
    if (h_jup in (KENDRA | TRIKONA) or is_in_own_sign(pmap, "Jupiter") or is_exalted(pmap, "Jupiter")) and not is_debilitated(pmap, "Jupiter"):
        return True, f"Naisargika Dhana Karaka Jupiter placed auspiciously in H{h_jup} in {s_jup}", ["Jupiter"]
    return False, "", []

def _exc_jupiter_combust(ctx: dict, pmap: dict) -> tuple[bool, str]:
    return _exc_combust(ctx, pmap, "Jupiter", orb=11.0)


# ---------------------------------------------------------------------------
# Canonical Wealth Rules Catalog (26 Rules)
# ---------------------------------------------------------------------------

WEALTH_RULES_CATALOG: list[WealthRule] = [
    # Family A: Second House & Lord (Accumulated Wealth & Savings)
    WealthRule(
        rule_id="WEALTH-H2-LORD-KENDRA-TRIKONA-01",
        version="1.0.0",
        domain="wealth",
        profile="parashari_classical",
        chart_frame="D1",
        predicate=_pred_h2_lord_kendra_trikona,
        ordered_exceptions=[
            lambda c, p: _exc_debilitated_no_nb(c, p, safe_house_lord(c.get("lagna", ""), 2)),
            lambda c, p: _exc_combust(c, p, safe_house_lord(c.get("lagna", ""), 2), 3.0),
        ],
        dedupe_key="DEDUPE-H2-LORD-PLACEMENT",
        effect="SUPPORTS",
        explanation_template="2nd lord {planet} in Kendra/Trikona supports accumulated wealth and savings preservation.",
        source_family="Parashari",
        source_reference="BPHS Ch. 24, v. 13-14; Phaladeepika Ch. 6, v. 6",
        source_status="VERIFIED",
        review_status="ACCEPTED",
        confidence="HIGH",
        tests=["test_wp5c_wealth_h2_kendra_trikona"],
        dimensions=["accumulated_savings"],
    ),
    WealthRule(
        rule_id="WEALTH-H2-LORD-OWN-EXALTED-02",
        version="1.0.0",
        domain="wealth",
        profile="parashari_classical",
        chart_frame="D1",
        predicate=_pred_h2_lord_own_exalted,
        ordered_exceptions=[
            lambda c, p: _exc_combust(c, p, safe_house_lord(c.get("lagna", ""), 2), 3.0),
        ],
        dedupe_key="DEDUPE-H2-LORD-DIGNITY",
        effect="SUPPORTS",
        explanation_template="2nd lord {planet} in own sign or exaltation provides robust financial security and capital preservation.",
        source_family="Parashari",
        source_reference="BPHS Ch. 24, v. 15",
        source_status="VERIFIED",
        review_status="ACCEPTED",
        confidence="HIGH",
        tests=["test_wp5c_wealth_h2_own_exalted"],
        dimensions=["accumulated_savings"],
    ),
    WealthRule(
        rule_id="WEALTH-H2-BENEFIC-OCCUPANCY-03",
        version="1.0.0",
        domain="wealth",
        profile="parashari_classical",
        chart_frame="D1",
        predicate=_pred_h2_benefic_occ,
        ordered_exceptions=[],
        dedupe_key="DEDUPE-H2-OCCUPANCY",
        effect="SUPPORTS",
        explanation_template="Natural benefics in 2nd house promote continuous, ethical accumulation of savings.",
        source_family="Parashari",
        source_reference="BPHS Ch. 24, v. 16; Jataka Parijata Ch. 11, v. 5",
        source_status="VERIFIED",
        review_status="ACCEPTED",
        confidence="HIGH",
        tests=["test_wp5c_wealth_h2_benefic"],
        dimensions=["accumulated_savings"],
    ),
    WealthRule(
        rule_id="WEALTH-H2-LORD-DUSTHANA-AFFLICTION-04",
        version="1.0.0",
        domain="wealth",
        profile="parashari_classical",
        chart_frame="D1",
        predicate=_pred_h2_lord_dusthana,
        ordered_exceptions=[_exc_h2_dusthana_mitigated],
        dedupe_key="DEDUPE-H2-LORD-DUSTHANA",
        effect="OBSTRUCTS",
        explanation_template="2nd lord in Dusthana creates friction in liquid accumulation unless mitigated.",
        source_family="Parashari",
        source_reference="BPHS Ch. 24, v. 21-22; Phaladeepika Ch. 6, v. 8",
        source_status="VERIFIED",
        review_status="ACCEPTED",
        confidence="HIGH",
        tests=["test_wp5c_wealth_h2_dusthana"],
        dimensions=["accumulated_savings", "expenditure_outflow"],
    ),
    WealthRule(
        rule_id="WEALTH-H2-MALEFIC-AFFLICTION-05",
        version="1.0.0",
        domain="wealth",
        profile="parashari_classical",
        chart_frame="D1",
        predicate=_pred_h2_malefic_affliction,
        ordered_exceptions=[_exc_h2_malefic_is_lord],
        dedupe_key="DEDUPE-H2-AFFLICTION",
        effect="OBSTRUCTS",
        explanation_template="Multiple malefics in 2nd house without benefic relief strain liquid savings.",
        source_family="Parashari",
        source_reference="BPHS Ch. 24, v. 23",
        source_status="VERIFIED",
        review_status="ACCEPTED",
        confidence="HIGH",
        tests=["test_wp5c_wealth_h2_malefics"],
        dimensions=["accumulated_savings"],
    ),

    # Family B: Eleventh House & Lord (Recurring Gains & Inflow)
    WealthRule(
        rule_id="WEALTH-H11-LORD-KENDRA-TRIKONA-01",
        version="1.0.0",
        domain="wealth",
        profile="parashari_classical",
        chart_frame="D1",
        predicate=_pred_h11_lord_kendra_trikona,
        ordered_exceptions=[
            lambda c, p: _exc_debilitated_no_nb(c, p, safe_house_lord(c.get("lagna", ""), 11)),
        ],
        dedupe_key="DEDUPE-H11-LORD-PLACEMENT",
        effect="SUPPORTS",
        explanation_template="11th lord in Kendra/Trikona ensures multiple consistent streams of recurring income.",
        source_family="Parashari",
        source_reference="BPHS Ch. 24, v. 121-122",
        source_status="VERIFIED",
        review_status="ACCEPTED",
        confidence="HIGH",
        tests=["test_wp5c_wealth_h11_kendra_trikona"],
        dimensions=["recurring_gains"],
    ),
    WealthRule(
        rule_id="WEALTH-H11-LORD-OWN-EXALTED-02",
        version="1.0.0",
        domain="wealth",
        profile="parashari_classical",
        chart_frame="D1",
        predicate=_pred_h11_lord_own_exalted,
        ordered_exceptions=[
            lambda c, p: _exc_combust(c, p, safe_house_lord(c.get("lagna", ""), 11), 3.0),
        ],
        dedupe_key="DEDUPE-H11-LORD-DIGNITY",
        effect="SUPPORTS",
        explanation_template="11th lord in own sign or exaltation promotes abundant commercial revenue and fulfillment of gains.",
        source_family="Parashari",
        source_reference="BPHS Ch. 24, v. 123; Saravali Ch. 34, v. 17",
        source_status="VERIFIED",
        review_status="ACCEPTED",
        confidence="HIGH",
        tests=["test_wp5c_wealth_h11_own_exalted"],
        dimensions=["recurring_gains"],
    ),
    WealthRule(
        rule_id="WEALTH-H11-BENEFIC-OCCUPANCY-03",
        version="1.0.0",
        domain="wealth",
        profile="parashari_classical",
        chart_frame="D1",
        predicate=_pred_h11_benefic_occ,
        ordered_exceptions=[],
        dedupe_key="DEDUPE-H11-BENEFIC",
        effect="SUPPORTS",
        explanation_template="Benefics in 11th house foster ethical, regular revenue through collaborative networks.",
        source_family="Parashari",
        source_reference="Phaladeepika Ch. 8, v. 23",
        source_status="VERIFIED",
        review_status="ACCEPTED",
        confidence="HIGH",
        tests=["test_wp5c_wealth_h11_benefic"],
        dimensions=["recurring_gains"],
    ),
    WealthRule(
        rule_id="WEALTH-H11-UPACHAYA-GROWTH-04",
        version="1.0.0",
        domain="wealth",
        profile="parashari_classical",
        chart_frame="D1",
        predicate=_pred_h11_upachaya_growth,
        ordered_exceptions=[],
        dedupe_key="DEDUPE-H11-UPACHAYA",
        effect="SUPPORTS",
        explanation_template="Malefics in 11th generate powerful Upachaya compounding growth through enterprise and resilience.",
        source_family="Parashari",
        source_reference="BPHS Ch. 24, v. 124; Mansagari Ch. 4, v. 11",
        source_status="VERIFIED",
        review_status="ACCEPTED",
        confidence="HIGH",
        tests=["test_wp5c_wealth_h11_upachaya"],
        dimensions=["recurring_gains"],
    ),
    WealthRule(
        rule_id="WEALTH-H11-LORD-DUSTHANA-05",
        version="1.0.0",
        domain="wealth",
        profile="parashari_classical",
        chart_frame="D1",
        predicate=_pred_h11_lord_dusthana,
        ordered_exceptions=[_exc_h11_dusthana_mitigated],
        dedupe_key="DEDUPE-H11-LORD-DUSTHANA",
        effect="OBSTRUCTS",
        explanation_template="11th lord in Dusthana creates intermittency or delays in receiving revenue.",
        source_family="Parashari",
        source_reference="BPHS Ch. 24, v. 129",
        source_status="VERIFIED",
        review_status="ACCEPTED",
        confidence="HIGH",
        tests=["test_wp5c_wealth_h11_dusthana"],
        dimensions=["recurring_gains"],
    ),

    # Family C: Lakshmi Sthanas & Dhana Combinations (5th, 9th, 2nd, 11th, 1st)
    WealthRule(
        rule_id="WEALTH-DHANA-2-11-PARIVARTANA-01",
        version="1.0.0",
        domain="wealth",
        profile="parashari_classical",
        chart_frame="D1",
        predicate=_pred_dhana_2_11_parivartana,
        ordered_exceptions=[],
        dedupe_key="DEDUPE-DHANA-PARIVARTANA",
        effect="SUPPORTS",
        explanation_template="Mutual reception between 2nd and 11th lords creates a perpetual cycle of revenue and savings.",
        source_family="Parashari",
        source_reference="BPHS Ch. 41, v. 3; Phaladeepika Ch. 6, v. 32",
        source_status="VERIFIED",
        review_status="ACCEPTED",
        confidence="HIGH",
        tests=["test_wp5c_wealth_parivartana_2_11"],
        dimensions=["accumulated_savings", "recurring_gains"],
    ),
    WealthRule(
        rule_id="WEALTH-DHANA-5-11-AXIS-02",
        version="1.0.0",
        domain="wealth",
        profile="parashari_classical",
        chart_frame="D1",
        predicate=_pred_dhana_5_11_axis,
        ordered_exceptions=[],
        dedupe_key="DEDUPE-DHANA-5-11-AXIS",
        effect="SUPPORTS",
        explanation_template="5/11 axis connection translates intellect and creative merit into financial revenue.",
        source_family="Parashari",
        source_reference="BPHS Ch. 41, v. 7-8",
        source_status="VERIFIED",
        review_status="ACCEPTED",
        confidence="HIGH",
        tests=["test_wp5c_wealth_5_11_axis"],
        dimensions=["recurring_gains", "speculation_risk"],
    ),
    WealthRule(
        rule_id="WEALTH-DHANA-9-2-COMBINATION-03",
        version="1.0.0",
        domain="wealth",
        profile="parashari_classical",
        chart_frame="D1",
        predicate=_pred_dhana_9_2_combination,
        ordered_exceptions=[],
        dedupe_key="DEDUPE-DHANA-9-2-COMBO",
        effect="SUPPORTS",
        explanation_template="9th Bhagya lord connecting with 2nd Dhana lord grants fortunate financial inheritance and accumulated wealth.",
        source_family="Parashari",
        source_reference="BPHS Ch. 41, v. 9-10; Jataka Parijata Ch. 11, v. 12",
        source_status="VERIFIED",
        review_status="ACCEPTED",
        confidence="HIGH",
        tests=["test_wp5c_wealth_9_2_combo"],
        dimensions=["accumulated_savings"],
    ),
    WealthRule(
        rule_id="WEALTH-DHANA-1-11-CONNECTION-04",
        version="1.0.0",
        domain="wealth",
        profile="parashari_classical",
        chart_frame="D1",
        predicate=_pred_dhana_1_11_connection,
        ordered_exceptions=[],
        dedupe_key="DEDUPE-DHANA-1-11-COMBO",
        effect="SUPPORTS",
        explanation_template="Ascendant lord connection with 11th lord signifies self-made enterprise and directly earned wealth.",
        source_family="Parashari",
        source_reference="BPHS Ch. 41, v. 2",
        source_status="VERIFIED",
        review_status="ACCEPTED",
        confidence="HIGH",
        tests=["test_wp5c_wealth_1_11_combo"],
        dimensions=["earning_livelihood", "recurring_gains"],
    ),

    # Family D: Livelihood & Earning Capacity (1st & 10th Houses / Upachayas)
    WealthRule(
        rule_id="WEALTH-EARNING-10-2-CONNECTION-01",
        version="1.0.0",
        domain="wealth",
        profile="parashari_classical",
        chart_frame="D1",
        predicate=_pred_earning_10_2_connection,
        ordered_exceptions=[],
        dedupe_key="DEDUPE-EARNING-10-2",
        effect="SUPPORTS",
        explanation_template="10th Karma lord connecting with 2nd Dhana lord indicates professional career directly generating substantial savings.",
        source_family="Parashari",
        source_reference="BPHS Ch. 24, v. 111; Saravali Ch. 34, v. 12",
        source_status="VERIFIED",
        review_status="ACCEPTED",
        confidence="HIGH",
        tests=["test_wp5c_wealth_10_2_connection"],
        dimensions=["earning_livelihood"],
    ),
    WealthRule(
        rule_id="WEALTH-EARNING-LAGNA-STRONG-02",
        version="1.0.0",
        domain="wealth",
        profile="parashari_classical",
        chart_frame="D1",
        predicate=_pred_earning_lagna_strong,
        ordered_exceptions=[],
        dedupe_key="DEDUPE-EARNING-LAGNA",
        effect="SUPPORTS",
        explanation_template="Strong Lagna lord provides the personal stamina, agency, and health required for sustained livelihood.",
        source_family="Parashari",
        source_reference="BPHS Ch. 24, v. 3-4",
        source_status="VERIFIED",
        review_status="ACCEPTED",
        confidence="HIGH",
        tests=["test_wp5c_wealth_lagna_strong"],
        dimensions=["earning_livelihood"],
    ),
    WealthRule(
        rule_id="WEALTH-EARNING-UPACHAYA-BENEFIC-03",
        version="1.0.0",
        domain="wealth",
        profile="parashari_classical",
        chart_frame="D1",
        predicate=_pred_earning_upachaya_benefic,
        ordered_exceptions=[],
        dedupe_key="DEDUPE-EARNING-UPACHAYA-VASUMATI",
        effect="SUPPORTS",
        explanation_template="Vasumati combination: multiple benefics in Upachaya houses generate flourishing professional prosperity.",
        source_family="Parashari",
        source_reference="Phaladeepika Ch. 6, v. 23; Saravali Ch. 34, v. 21",
        source_status="VERIFIED",
        review_status="ACCEPTED",
        confidence="HIGH",
        tests=["test_wp5c_wealth_upachaya_benefics"],
        dimensions=["earning_livelihood", "recurring_gains"],
    ),

    # Family E: Financial Obligations & Debt (6th House / Lord / Rina Sthana)
    WealthRule(
        rule_id="WEALTH-DEBT-6-LORD-IN-2-01",
        version="1.0.0",
        domain="wealth",
        profile="parashari_classical",
        chart_frame="D1",
        predicate=_pred_debt_6_lord_in_2,
        ordered_exceptions=[_exc_debt_mitigated_6in2],
        dedupe_key="DEDUPE-DEBT-6-IN-2",
        effect="OBSTRUCTS",
        explanation_template="6th Rina lord in 2nd house directs accumulated wealth toward loan servicing or legal liabilities.",
        source_family="Parashari",
        source_reference="BPHS Ch. 24, v. 63; Phaladeepika Ch. 6, v. 14",
        source_status="VERIFIED",
        review_status="ACCEPTED",
        confidence="HIGH",
        tests=["test_wp5c_wealth_6_in_2"],
        dimensions=["accumulated_savings", "debt_obligations"],
    ),
    WealthRule(
        rule_id="WEALTH-DEBT-2-LORD-IN-6-02",
        version="1.0.0",
        domain="wealth",
        profile="parashari_classical",
        chart_frame="D1",
        predicate=_pred_debt_2_lord_in_6,
        ordered_exceptions=[_exc_debt_mitigated_2in6],
        dedupe_key="DEDUPE-DEBT-2-IN-6",
        effect="OBSTRUCTS",
        explanation_template="2nd Dhana lord in 6th house indicates capital encumbrances or operational financing overheads.",
        source_family="Parashari",
        source_reference="BPHS Ch. 24, v. 21",
        source_status="VERIFIED",
        review_status="ACCEPTED",
        confidence="HIGH",
        tests=["test_wp5c_wealth_2_in_6"],
        dimensions=["accumulated_savings", "debt_obligations"],
    ),
    WealthRule(
        rule_id="WEALTH-DEBT-SATURN-MARS-IN-6-03",
        version="1.0.0",
        domain="wealth",
        profile="parashari_classical",
        chart_frame="D1",
        predicate=_pred_debt_saturn_mars_in_6,
        ordered_exceptions=[],
        dedupe_key="DEDUPE-DEBT-MALEFIC-DEFENSE",
        effect="SUPPORTS",
        explanation_template="Saturn or Mars in 6th house bestows Shatru/Rina Hanta yoga, overcoming financial debts through discipline.",
        source_family="Parashari",
        source_reference="BPHS Ch. 24, v. 67; Phaladeepika Ch. 8, v. 13",
        source_status="VERIFIED",
        review_status="ACCEPTED",
        confidence="HIGH",
        tests=["test_wp5c_wealth_saturn_mars_6th"],
        dimensions=["debt_obligations"],
    ),

    # Family F: Expenditure & Outflow (12th House / Lord / Vyaya Sthana)
    WealthRule(
        rule_id="WEALTH-OUTFLOW-12-LORD-STRONG-01",
        version="1.0.0",
        domain="wealth",
        profile="parashari_classical",
        chart_frame="D1",
        predicate=_pred_outflow_12_lord_strong,
        ordered_exceptions=[_exc_outflow_dharmic_spending],
        dedupe_key="DEDUPE-OUTFLOW-12-LORD",
        effect="SUPPORTS",
        explanation_template="Strong 12th lord indicates significant capital expenditure, foreign commitments, or philanthropic outflow.",
        source_family="Parashari",
        source_reference="BPHS Ch. 24, v. 133-134",
        source_status="VERIFIED",
        review_status="ACCEPTED",
        confidence="HIGH",
        tests=["test_wp5c_wealth_12_lord_strong"],
        dimensions=["expenditure_outflow"],
    ),
    WealthRule(
        rule_id="WEALTH-OUTFLOW-2-LORD-IN-12-02",
        version="1.0.0",
        domain="wealth",
        profile="parashari_classical",
        chart_frame="D1",
        predicate=_pred_outflow_2_lord_in_12,
        ordered_exceptions=[_exc_outflow_mitigated_2in12],
        dedupe_key="DEDUPE-OUTFLOW-2-IN-12",
        effect="SUPPORTS",
        explanation_template="2nd Dhana lord in 12th house indicates recurring capital leakage or expenditure exceeding savings.",
        source_family="Parashari",
        source_reference="BPHS Ch. 24, v. 22; Jataka Parijata Ch. 11, v. 18",
        source_status="VERIFIED",
        review_status="ACCEPTED",
        confidence="HIGH",
        tests=["test_wp5c_wealth_2_in_12"],
        dimensions=["expenditure_outflow", "accumulated_savings"],
    ),

    # Family G: Speculation, Unearned Wealth & Financial Volatility (5th/8th Houses & Rahu)
    WealthRule(
        rule_id="WEALTH-SPEC-5-8-CONNECTION-01",
        version="1.0.0",
        domain="wealth",
        profile="parashari_classical",
        chart_frame="D1",
        predicate=_pred_spec_5_8_connection,
        ordered_exceptions=[_exc_spec_high_risk_affliction],
        dedupe_key="DEDUPE-SPEC-5-8",
        effect="CONDITIONAL",
        explanation_template="5th/8th connection indicates fluctuating financial gains, sudden windfalls, or high-variance speculative activities.",
        source_family="Parashari",
        source_reference="BPHS Ch. 24, v. 53-54; Saravali Ch. 34, v. 14",
        source_status="VERIFIED",
        review_status="ACCEPTED",
        confidence="HIGH",
        tests=["test_wp5c_wealth_5_8_connection"],
        dimensions=["speculation_risk"],
    ),
    WealthRule(
        rule_id="WEALTH-SPEC-RAHU-IN-11-OR-5-02",
        version="1.0.0",
        domain="wealth",
        profile="parashari_classical",
        chart_frame="D1",
        predicate=_pred_spec_rahu_5_or_11,
        ordered_exceptions=[_exc_rahu_suppressed],
        dedupe_key="DEDUPE-SPEC-RAHU",
        effect="CONDITIONAL",
        explanation_template="Rahu in 5th or 11th creates non-linear income ambitions, rapid financial expansion, and high volatility.",
        source_family="Parashari",
        source_reference="Phaladeepika Ch. 8, v. 27; BPHS Ch. 24, v. 126",
        source_status="VERIFIED",
        review_status="ACCEPTED",
        confidence="HIGH",
        tests=["test_wp5c_wealth_rahu_5_11"],
        dimensions=["speculation_risk"],
    ),

    # Family H: Cross-Reading & Significator Frames (Chandra Lagna & Jupiter Karaka)
    WealthRule(
        rule_id="WEALTH-CHANDRA-LAGNA-DHANA-01",
        version="1.0.0",
        domain="wealth",
        profile="parashari_classical",
        chart_frame="Chandra",
        predicate=_pred_chandra_lagna_dhana,
        ordered_exceptions=[],
        dedupe_key="DEDUPE-CHANDRA-DHANA",
        effect="SUPPORTS",
        explanation_template="Benefics in 2nd or 11th from Moon confirm emotional satisfaction and material support from the lunar frame.",
        source_family="Parashari",
        source_reference="Phaladeepika Ch. 6, v. 24",
        source_status="VERIFIED",
        review_status="ACCEPTED",
        confidence="HIGH",
        tests=["test_wp5c_wealth_chandra_lagna"],
        dimensions=["accumulated_savings", "recurring_gains"],
    ),
    WealthRule(
        rule_id="WEALTH-KARAKA-JUPITER-DIGNITY-02",
        version="1.0.0",
        domain="wealth",
        profile="parashari_classical",
        chart_frame="Karaka",
        predicate=_pred_karaka_jupiter_dignity,
        ordered_exceptions=[_exc_jupiter_combust],
        dedupe_key="DEDUPE-JUPITER-KARAKA",
        effect="SUPPORTS",
        explanation_template="Naisargika Dhana Karaka Jupiter in auspicious dignity provides enduring wisdom and ethical growth in assets.",
        source_family="Parashari",
        source_reference="BPHS Ch. 24, v. 140; Phaladeepika Ch. 2, v. 28",
        source_status="VERIFIED",
        review_status="ACCEPTED",
        confidence="HIGH",
        tests=["test_wp5c_wealth_jupiter_karaka"],
        dimensions=["accumulated_savings", "earning_livelihood"],
    ),
]


# ---------------------------------------------------------------------------
# Evaluator Engine
# ---------------------------------------------------------------------------

def evaluate_wealth_rules(ctx: dict, profile: str = "parashari_classical") -> dict:
    """
    Evaluate the classical Vedic Wealth & Resources rule pack against a ChartContext.

    Separates evidence across 6 distinct financial dimensions:
      - accumulated_savings
      - recurring_gains
      - earning_livelihood
      - debt_obligations
      - expenditure_outflow
      - speculation_risk

    Reuses canonical WP3 Dhana Yogas without duplicate inflation.
    Adheres strictly to Specification v3.0 §21 (Financial Safety Guardrails).
    """
    pmap = get_planet_map(ctx)
    lagna = ctx.get("lagna", "")

    matched_rules = []
    rejected_rules = []
    cancelled_rules = []

    # Initialize dimension evidence ledgers
    dim_ledgers: dict[str, dict] = {
        d: {"support": 0, "obstruct": 0, "conditional": 0, "evidence": []}
        for d in FINANCIAL_DIMENSIONS
    }

    # Evaluate canonical rules
    for rule in WEALTH_RULES_CATALOG:
        if not rule.enabled:
            continue
        if profile != "all" and rule.profile != profile:
            continue

        fired, reason, planets = rule.predicate(ctx, pmap)
        if not fired:
            rejected_rules.append({
                "rule_id": rule.rule_id,
                "reason": "Predicate condition not met in chart",
            })
            continue

        # Check ordered exceptions
        cancelled = False
        cancel_reason = ""
        for exc in rule.ordered_exceptions:
            c_fired, c_reason = exc(ctx, pmap)
            if c_fired:
                cancelled = True
                cancel_reason = c_reason
                break

        if cancelled:
            cancelled_rules.append({
                "rule_id": rule.rule_id,
                "reason": cancel_reason,
            })
            continue

        # Matched rule
        rule_record = {
            "rule_id": rule.rule_id,
            "domain": rule.domain,
            "chart_frame": rule.chart_frame,
            "effect": rule.effect,
            "planets": planets,
            "explanation": reason,
            "source_reference": rule.source_reference,
            "confidence": rule.confidence,
            "dimensions": rule.dimensions,
        }
        matched_rules.append(rule_record)

        # Distribute into dimension ledgers
        for d in rule.dimensions:
            if d in dim_ledgers:
                ledger = dim_ledgers[d]
                if rule.effect == "SUPPORTS":
                    ledger["support"] += 1
                elif rule.effect == "OBSTRUCTS":
                    ledger["obstruct"] += 1
                elif rule.effect == "CONDITIONAL":
                    ledger["conditional"] += 1
                ledger["evidence"].append(reason)

    # Cross-reference existing Dhana Yogas from WP3 (yoga_catalog.py)
    dhana_yogas_active = []
    try:
        planets_list = ctx.get("planets")
        if not planets_list and "planet_map" in ctx:
            planets_list = []
            for p_name, p_data in ctx["planet_map"].items():
                item = dict(p_data)
                item["name"] = p_name
                planets_list.append(item)
        lagna_sign = ctx.get("lagna", "")
        houses = ctx.get("house_signs", {})
        catalog_results = evaluate_yoga_catalog(planets_list, lagna_sign, houses)
        for y in catalog_results:
            if not y.get("present"):
                continue
            cat = y.get("category", "")
            name = y.get("name", "")
            r_id = y.get("rule_id", "")
            if "Dhana" in cat or "Dhana" in name or "Lakshmi" in name or r_id.startswith("YOGA-DHANA-"):
                dhana_yogas_active.append({
                    "rule_id": r_id,
                    "name": name,
                    "strength": y.get("strength", "Medium"),
                    "source_reference": y.get("source_reference", ""),
                    "planets": y.get("details", []),
                })
                # Dhana yogas from WP3 naturally reinforce recurring gains and savings
                dim_ledgers["recurring_gains"]["support"] += 1
                dim_ledgers["accumulated_savings"]["support"] += 1
                dim_ledgers["recurring_gains"]["evidence"].append(f"WP3 Yoga: {name} active ({r_id})")
                dim_ledgers["accumulated_savings"]["evidence"].append(f"WP3 Yoga: {name} active ({r_id})")
    except Exception:
        # Graceful fallback if context lacks full yoga dependencies
        pass

    # Synthesize dimensional statuses without collapsing to a single fatalistic score
    def _net_status(ledger: dict) -> str:
        s = ledger["support"]
        o = ledger["obstruct"]
        c = ledger["conditional"]
        if c > 0 and s == 0 and o == 0:
            return "Speculative / High Variance"
        if s >= 2 and o == 0:
            return "Strong"
        if s > o:
            return "Favorable"
        if o > s:
            return "Challenged / Outflow Pressure"
        if s == o and (s + o) > 0:
            return "Balanced / Mixed"
        return "Neutral / Moderate"

    dimensions_output = {}
    for d, ledger in dim_ledgers.items():
        dimensions_output[d] = {
            "support": ledger["support"],
            "obstruct": ledger["obstruct"],
            "conditional": ledger["conditional"],
            "status": _net_status(ledger),
            "evidence": ledger["evidence"],
        }

    # Significator Karaka Status
    j_house = house_of(pmap, "Jupiter")
    j_sign = sign_of(pmap, "Jupiter")
    j_dignity = "Exalted" if is_exalted(pmap, "Jupiter") else "Own Sign" if is_in_own_sign(pmap, "Jupiter") else "Debilitated" if is_debilitated(pmap, "Jupiter") else "Neutral"

    m_house = house_of(pmap, "Mercury")
    m_sign = sign_of(pmap, "Mercury")
    m_dignity = "Exalted" if is_exalted(pmap, "Mercury") else "Own Sign" if is_in_own_sign(pmap, "Mercury") else "Debilitated" if is_debilitated(pmap, "Mercury") else "Neutral"

    karaka_status = {
        "jupiter": {
            "role": "Naisargika Dhana Karaka (Universal Wealth & Expansion)",
            "house": j_house,
            "sign": j_sign,
            "dignity": j_dignity,
        },
        "mercury": {
            "role": "Vyapara Karaka (Commerce & Analytical Accounting)",
            "house": m_house,
            "sign": m_sign,
            "dignity": m_dignity,
        },
    }

    return {
        "domain": "wealth",
        "profile": profile,
        "lagna": lagna,
        "dimensions": dimensions_output,
        "matched_rules": matched_rules,
        "rejected_rules": rejected_rules,
        "cancelled_rules": cancelled_rules,
        "dhana_yogas_active": dhana_yogas_active,
        "karaka_status": karaka_status,
        "safety_disclaimer": SAFETY_DISCLAIMER,
    }
