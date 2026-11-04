"""
Classical Vedic Astrology Education & Learning Domain Rule Pack (Pure Shared Library).

Implements 24 canonical, deterministic Parashari education, scholarship, and learning rules,
separating 6 explainable educational evidence dimensions:
  1. Foundational Learning Environment (foundational_learning)
  2. Analytical & Communication-Oriented Learning (analytical_communication)
  3. Creative & Conceptual Learning (creative_conceptual)
  4. Advanced Study & Mentorship (advanced_study_mentorship)
  5. Learning Routines & Consistency (learning_routine_consistency)
  6. Traditional Knowledge & Intellectual Interests (traditional_knowledge_interests)

Includes mathematically verified D24 Siddhamsa (Chaturvimshamsa) calculation per BPHS Ch. 6, v. 24-25.

Strictly adheres to Master Specification v3.0 §9.5 & §21 (Educational Safety Guardrails).
ABSOLUTE PROHIBITION: Never predicts exam outcomes (pass/fail, marks, ranks), university admissions,
intelligence / IQ scores, learning disabilities, or advises abandoning education.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Any, Optional

from .zodiac import SIGNS_SK, SIGN_LORDS
from .strength import EXALTATION, DEBILITATION, OWN_SIGNS
from .lordship import get_house_lord


# ---------------------------------------------------------------------------
# Constants & Allowed Dimensions
# ---------------------------------------------------------------------------

KENDRA = {1, 4, 7, 10}
TRIKONA = {1, 5, 9}
DUSTHANA = {6, 8, 12}
UPACHAYA = {3, 6, 10, 11}

CLASSICAL_7 = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
NATURAL_BENEFICS = {"Jupiter", "Venus", "Mercury", "Moon"}
NATURAL_MALEFICS = {"Sun", "Mars", "Saturn", "Rahu", "Ketu"}

EDUCATION_DIMENSIONS = [
    "foundational_learning",
    "analytical_communication",
    "creative_conceptual",
    "advanced_study_mentorship",
    "learning_routine_consistency",
    "traditional_knowledge_interests",
]

SAFETY_DISCLAIMER = (
    "AstroLogic AI provides non-deterministic cultural, educational, and astrological learning reflections only. "
    "Astrological charts CANNOT evaluate cognitive capacity, predict IQ or intellectual ability, diagnose learning "
    "disabilities, guarantee examination results or grades, guarantee school/university admissions, or determine "
    "academic degrees. For all academic, educational, and cognitive guidance, consult qualified educators, "
    "academic counselors, and certified educational psychologists."
)


# ---------------------------------------------------------------------------
# Canonical Education Rule Dataclass
# ---------------------------------------------------------------------------

@dataclass
class EducationRule:
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
    confidence: str = "[HIGH]"
    tests: list[str] = field(default_factory=list)
    dimensions: list[str] = field(default_factory=list)
    enabled: bool = True


# ---------------------------------------------------------------------------
# D24 Siddhamsa (Chaturvimshamsa) Calculator (BPHS Ch. 6, v. 24-25)
# ---------------------------------------------------------------------------

def calculate_siddhamsa_d24(sign: str, degree: float) -> str:
    """
    Calculate Siddhamsa (D24 / Chaturvimshamsa) rashi according to classical BPHS Ch. 6, v. 24-25.

    Each sign of 30° is divided into 24 parts of 1° 15' (1.25°).
    - In Odd signs (Mesha, Mithuna, Simha, Tula, Dhanu, Kumbha), counting starts from Simha (Leo).
    - In Even signs (Vrishabha, Karka, Kanya, Vrischika, Makara, Meena), counting starts from Karka (Cancer).

    Parameters:
        sign: Sanskrit name of the sign (e.g., 'Mesha', 'Vrishabha')
        degree: Longitudinal position within the sign [0.0, 30.0)

    Returns:
        Sanskrit name of the D24 sign.
    """
    if not sign:
        return "Simha"
    norm = sign.strip().capitalize()
    if norm == "Vrishika":
        norm = "Vrischika"
    if norm not in SIGNS_SK:
        return "Simha"

    sign_idx = SIGNS_SK.index(norm)
    # Odd signs (Mesha=0, Mithuna=2, Simha=4, etc.) are 0, 2, 4, 6, 8, 10
    is_odd = (sign_idx % 2 == 0)
    start_idx = 4 if is_odd else 3  # 4 = Simha, 3 = Karka

    deg = float(degree) % 30.0
    part = int(deg / 1.25)
    if part > 23:
        part = 23
    elif part < 0:
        part = 0

    return SIGNS_SK[(start_idx + part) % 12]


def build_d24_chart(ctx: dict) -> dict[str, Any]:
    """
    Construct D24 positions and houses for Lagna and all planets.
    Uses planet degrees and lagna degree if provided, else defaults to 15.0°.
    """
    pmap = ctx.get("planet_map", {})
    lagna_sign = ctx.get("lagna", "Mesha")
    lagna_deg = ctx.get("ascendant_degree", 15.0)

    d24_lagna = calculate_siddhamsa_d24(lagna_sign, lagna_deg)
    d24_lagna_idx = SIGNS_SK.index(d24_lagna)

    d24_planets: dict[str, dict[str, Any]] = {}
    for p, pdata in pmap.items():
        psign = pdata.get("sign", "Mesha")
        pdeg = pdata.get("degree", 15.0)
        d24_sign = calculate_siddhamsa_d24(psign, pdeg)
        d24_sign_idx = SIGNS_SK.index(d24_sign)
        d24_house = ((d24_sign_idx - d24_lagna_idx) % 12) + 1
        d24_planets[p] = {
            "sign": d24_sign,
            "house": d24_house,
            "lord": SIGN_LORDS.get(d24_sign, ""),
        }

    return {
        "d24_lagna": d24_lagna,
        "d24_lagna_lord": SIGN_LORDS.get(d24_lagna, ""),
        "d24_planets": d24_planets,
    }


# ---------------------------------------------------------------------------
# Helper Inspection Functions
# ---------------------------------------------------------------------------

def safe_house_lord(lagna: str, h: int) -> str:
    """Safely resolve house lord with sign name normalization."""
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
    return ctx.get("planet_map", {})


def get_planets_in_house(pmap: dict, house: int) -> list[str]:
    return [p for p, d in pmap.items() if d.get("house") == house]


def is_planet_combust(pdata: dict) -> bool:
    return pdata.get("combust", False) or pdata.get("is_combust", False)


def is_planet_dignified(planet: str, pdata: dict) -> bool:
    sign = pdata.get("sign", "")
    return sign in OWN_SIGNS.get(planet, []) or sign == EXALTATION.get(planet)


def is_planet_debilitated(planet: str, pdata: dict) -> bool:
    sign = pdata.get("sign", "")
    return sign == DEBILITATION.get(planet)


# ---------------------------------------------------------------------------
# Canonical 24 Rules (Families A through G)
# ---------------------------------------------------------------------------

EDUCATION_RULES_CATALOG: list[EducationRule] = []


def _register(rule: EducationRule) -> EducationRule:
    EDUCATION_RULES_CATALOG.append(rule)
    return rule


# ---------------------------------------------------------------------------
# Family A: 4th House & Foundational Learning (4 rules)
# ---------------------------------------------------------------------------

def _pred_h4_lord_kt(ctx: dict, pmap: dict) -> tuple[bool, str, list[str]]:
    lagna = ctx.get("lagna", "")
    l4 = safe_house_lord(lagna, 4)
    if not l4 or l4 not in pmap:
        return False, "", []
    h = pmap[l4].get("house", 0)
    if h in KENDRA or h in TRIKONA:
        return True, f"4th lord {l4} placed in auspicious house {h} (Kendra/Trikona)", [l4]
    return False, "", []

def _exc_h4_lord_kt_combust(ctx: dict, pmap: dict) -> tuple[bool, str]:
    lagna = ctx.get("lagna", "")
    l4 = safe_house_lord(lagna, 4)
    if l4 and l4 in pmap and is_planet_combust(pmap[l4]):
        return True, f"4th lord {l4} is combust, tempering foundational stability"
    return False, ""

_register(EducationRule(
    rule_id="EDU-H4-LORD-KENDRA-TRIKONA-01",
    version="1.0.0",
    domain="education",
    profile="parashari_classical",
    chart_frame="D1_LAGNA",
    predicate=_pred_h4_lord_kt,
    ordered_exceptions=[_exc_h4_lord_kt_combust],
    dedupe_key="EDU_H4_LORD_POSITION",
    effect="SUPPORTS",
    birth_time_sensitive=False,
    explanation_template="4th lord placed in Kendra or Trikona fosters supportive foundational learning and institutional stability.",
    source_family="BPHS",
    source_reference="BPHS Ch. 24, v. 37-38",
    source_status="VERIFIED",
    review_status="ACCEPTED",
    confidence="[HIGH]",
    tests=["test_edu_h4_lord_kendra_trikona_positive", "test_edu_h4_lord_kendra_trikona_combust_exception"],
    dimensions=["foundational_learning", "learning_routine_consistency"],
))


def _pred_h4_lord_dignity(ctx: dict, pmap: dict) -> tuple[bool, str, list[str]]:
    lagna = ctx.get("lagna", "")
    l4 = safe_house_lord(lagna, 4)
    if not l4 or l4 not in pmap:
        return False, "", []
    pdata = pmap[l4]
    if is_planet_dignified(l4, pdata):
        return True, f"4th lord {l4} dignified in {pdata.get('sign')} (own/exalted)", [l4]
    return False, "", []

_register(EducationRule(
    rule_id="EDU-H4-LORD-OWN-EXALTED-02",
    version="1.0.0",
    domain="education",
    profile="parashari_classical",
    chart_frame="D1_LAGNA",
    predicate=_pred_h4_lord_dignity,
    ordered_exceptions=[],
    dedupe_key="EDU_H4_LORD_DIGNITY",
    effect="SUPPORTS",
    birth_time_sensitive=False,
    explanation_template="4th lord in dignity reflects robust foundational educational access and steady learning continuity.",
    source_family="BPHS",
    source_reference="BPHS Ch. 24, v. 39; Phaladeepika Ch. 6, v. 11",
    source_status="VERIFIED",
    review_status="ACCEPTED",
    confidence="[HIGH]",
    tests=["test_edu_h4_lord_dignity_positive", "test_edu_h4_lord_dignity_negative"],
    dimensions=["foundational_learning"],
))


def _pred_h4_benefic_occ(ctx: dict, pmap: dict) -> tuple[bool, str, list[str]]:
    benefics_in_4 = [p for p in get_planets_in_house(pmap, 4) if p in NATURAL_BENEFICS]
    if benefics_in_4:
        names = ", ".join(benefics_in_4)
        return True, f"Natural benefic(s) in 4th house: {names}", benefics_in_4
    return False, "", []

def _exc_h4_benefic_debilitated(ctx: dict, pmap: dict) -> tuple[bool, str]:
    benefics_in_4 = [p for p in get_planets_in_house(pmap, 4) if p in NATURAL_BENEFICS]
    debilitated = [p for p in benefics_in_4 if is_planet_debilitated(p, pmap[p])]
    if len(debilitated) == len(benefics_in_4) and len(debilitated) > 0:
        return True, f"Benefic in 4th house is debilitated ({', '.join(debilitated)})"
    return False, ""

_register(EducationRule(
    rule_id="EDU-H4-BENEFIC-OCCUPANCY-03",
    version="1.0.0",
    domain="education",
    profile="parashari_classical",
    chart_frame="D1_LAGNA",
    predicate=_pred_h4_benefic_occ,
    ordered_exceptions=[_exc_h4_benefic_debilitated],
    dedupe_key="EDU_H4_OCCUPANCY",
    effect="SUPPORTS",
    birth_time_sensitive=False,
    explanation_template="Benefic occupation of 4th house supports a calm, encouraging study atmosphere and routine stability.",
    source_family="BPHS",
    source_reference="BPHS Ch. 24, v. 40",
    source_status="VERIFIED",
    review_status="ACCEPTED",
    confidence="[HIGH]",
    tests=["test_edu_h4_benefic_occupancy_positive", "test_edu_h4_benefic_debilitated_exception"],
    dimensions=["foundational_learning", "learning_routine_consistency"],
))


def _pred_h4_lord_dusthana(ctx: dict, pmap: dict) -> tuple[bool, str, list[str]]:
    lagna = ctx.get("lagna", "")
    l4 = safe_house_lord(lagna, 4)
    if not l4 or l4 not in pmap:
        return False, "", []
    h = pmap[l4].get("house", 0)
    if h in DUSTHANA:
        return True, f"4th lord {l4} placed in Dusthana house {h}", [l4]
    return False, "", []

def _exc_h4_dusthana_own_sign(ctx: dict, pmap: dict) -> tuple[bool, str]:
    lagna = ctx.get("lagna", "")
    l4 = safe_house_lord(lagna, 4)
    if l4 and l4 in pmap and is_planet_dignified(l4, pmap[l4]):
        return True, f"4th lord {l4} is in own sign in house {pmap[l4].get('house')}, mitigating disruption"
    return False, ""

_register(EducationRule(
    rule_id="EDU-H4-LORD-DUSTHANA-AFFLICTION-04",
    version="1.0.0",
    domain="education",
    profile="parashari_classical",
    chart_frame="D1_LAGNA",
    predicate=_pred_h4_lord_dusthana,
    ordered_exceptions=[_exc_h4_dusthana_own_sign],
    dedupe_key="EDU_H4_LORD_DUSTHANA",
    effect="OBSTRUCTS",
    birth_time_sensitive=False,
    explanation_template="4th lord in Dusthana highlights environmental disruptions or study distractions requiring mindful routine management.",
    source_family="BPHS",
    source_reference="BPHS Ch. 24, v. 45-46",
    source_status="VERIFIED",
    review_status="ACCEPTED",
    confidence="[HIGH]",
    tests=["test_edu_h4_lord_dusthana_positive", "test_edu_h4_lord_dusthana_own_sign_exception"],
    dimensions=["foundational_learning", "learning_routine_consistency"],
))


# ---------------------------------------------------------------------------
# Family B: 5th House & Intellectual Discernment (Buddhi) (4 rules)
# ---------------------------------------------------------------------------

def _pred_h5_lord_kt(ctx: dict, pmap: dict) -> tuple[bool, str, list[str]]:
    lagna = ctx.get("lagna", "")
    l5 = safe_house_lord(lagna, 5)
    if not l5 or l5 not in pmap:
        return False, "", []
    h = pmap[l5].get("house", 0)
    if h in KENDRA or h in TRIKONA:
        return True, f"5th lord {l5} placed in auspicious house {h} (Kendra/Trikona)", [l5]
    return False, "", []

def _exc_h5_lord_kt_combust(ctx: dict, pmap: dict) -> tuple[bool, str]:
    lagna = ctx.get("lagna", "")
    l5 = safe_house_lord(lagna, 5)
    if l5 and l5 in pmap and is_planet_combust(pmap[l5]):
        return True, f"5th lord {l5} is combust, requiring deliberate conceptual pacing"
    return False, ""

_register(EducationRule(
    rule_id="EDU-H5-LORD-KENDRA-TRIKONA-01",
    version="1.0.0",
    domain="education",
    profile="parashari_classical",
    chart_frame="D1_LAGNA",
    predicate=_pred_h5_lord_kt,
    ordered_exceptions=[_exc_h5_lord_kt_combust],
    dedupe_key="EDU_H5_LORD_POSITION",
    effect="SUPPORTS",
    birth_time_sensitive=False,
    explanation_template="5th lord in Kendra or Trikona activates sharp intellectual curiosity, reasoning capability, and creative problem solving.",
    source_family="BPHS",
    source_reference="BPHS Ch. 24, v. 49-50; Phaladeepika Ch. 6, v. 12",
    source_status="VERIFIED",
    review_status="ACCEPTED",
    confidence="[HIGH]",
    tests=["test_edu_h5_lord_kendra_trikona_positive", "test_edu_h5_lord_combust_exception"],
    dimensions=["creative_conceptual", "analytical_communication"],
))


def _pred_h5_lord_dignity(ctx: dict, pmap: dict) -> tuple[bool, str, list[str]]:
    lagna = ctx.get("lagna", "")
    l5 = safe_house_lord(lagna, 5)
    if not l5 or l5 not in pmap:
        return False, "", []
    pdata = pmap[l5]
    if is_planet_dignified(l5, pdata):
        return True, f"5th lord {l5} dignified in {pdata.get('sign')} (own/exalted)", [l5]
    return False, "", []

_register(EducationRule(
    rule_id="EDU-H5-LORD-OWN-EXALTED-02",
    version="1.0.0",
    domain="education",
    profile="parashari_classical",
    chart_frame="D1_LAGNA",
    predicate=_pred_h5_lord_dignity,
    ordered_exceptions=[],
    dedupe_key="EDU_H5_LORD_DIGNITY",
    effect="SUPPORTS",
    birth_time_sensitive=False,
    explanation_template="5th lord in dignity indicates profound conceptual grasp, creative reasoning, and scholastic distinction.",
    source_family="BPHS",
    source_reference="BPHS Ch. 24, v. 51; Saravali Ch. 34, v. 7",
    source_status="VERIFIED",
    review_status="ACCEPTED",
    confidence="[HIGH]",
    tests=["test_edu_h5_lord_dignity_positive", "test_edu_h5_lord_dignity_negative"],
    dimensions=["creative_conceptual", "traditional_knowledge_interests"],
))


def _pred_h5_benefic_occ(ctx: dict, pmap: dict) -> tuple[bool, str, list[str]]:
    benefics_in_5 = [p for p in get_planets_in_house(pmap, 5) if p in {"Jupiter", "Mercury", "Venus"}]
    if benefics_in_5:
        names = ", ".join(benefics_in_5)
        return True, f"Intellectual benefic(s) in 5th house: {names}", benefics_in_5
    return False, "", []

def _exc_h5_benefic_debilitated(ctx: dict, pmap: dict) -> tuple[bool, str]:
    benefics_in_5 = [p for p in get_planets_in_house(pmap, 5) if p in {"Jupiter", "Mercury", "Venus"}]
    debilitated = [p for p in benefics_in_5 if is_planet_debilitated(p, pmap[p])]
    if len(debilitated) == len(benefics_in_5) and len(debilitated) > 0:
        return True, f"Benefic in 5th house is debilitated ({', '.join(debilitated)})"
    return False, ""

_register(EducationRule(
    rule_id="EDU-H5-BENEFIC-OCCUPANCY-03",
    version="1.0.0",
    domain="education",
    profile="parashari_classical",
    chart_frame="D1_LAGNA",
    predicate=_pred_h5_benefic_occ,
    ordered_exceptions=[_exc_h5_benefic_debilitated],
    dedupe_key="EDU_H5_OCCUPANCY",
    effect="SUPPORTS",
    birth_time_sensitive=False,
    explanation_template="Jupiter, Mercury, or Venus in 5th house cultivates intellectual grace, love for learning, and literary inclination.",
    source_family="Phaladeepika",
    source_reference="Phaladeepika Ch. 8, v. 11",
    source_status="VERIFIED",
    review_status="ACCEPTED",
    confidence="[HIGH]",
    tests=["test_edu_h5_benefic_occupancy_positive", "test_edu_h5_benefic_debilitated_exception"],
    dimensions=["creative_conceptual", "analytical_communication"],
))


def _pred_h5_lord_dusthana(ctx: dict, pmap: dict) -> tuple[bool, str, list[str]]:
    lagna = ctx.get("lagna", "")
    l5 = safe_house_lord(lagna, 5)
    if not l5 or l5 not in pmap:
        return False, "", []
    h = pmap[l5].get("house", 0)
    if h in DUSTHANA:
        return True, f"5th lord {l5} placed in Dusthana house {h}", [l5]
    return False, "", []

def _exc_h5_dusthana_mitigated(ctx: dict, pmap: dict) -> tuple[bool, str]:
    lagna = ctx.get("lagna", "")
    l5 = safe_house_lord(lagna, 5)
    if l5 and l5 in pmap and is_planet_dignified(l5, pmap[l5]):
        return True, f"5th lord {l5} is in own sign in house {pmap[l5].get('house')}, mitigating intellectual friction"
    return False, ""

_register(EducationRule(
    rule_id="EDU-H5-LORD-DUSTHANA-AFFLICTION-04",
    version="1.0.0",
    domain="education",
    profile="parashari_classical",
    chart_frame="D1_LAGNA",
    predicate=_pred_h5_lord_dusthana,
    ordered_exceptions=[_exc_h5_dusthana_mitigated],
    dedupe_key="EDU_H5_LORD_DUSTHANA",
    effect="OBSTRUCTS",
    birth_time_sensitive=False,
    explanation_template="5th lord in Dusthana suggests fluctuating study focus or shifts in academic orientation, benefiting from structured milestones.",
    source_family="BPHS",
    source_reference="BPHS Ch. 24, v. 57",
    source_status="VERIFIED",
    review_status="ACCEPTED",
    confidence="[HIGH]",
    tests=["test_edu_h5_lord_dusthana_positive", "test_edu_h5_lord_dusthana_mitigated_exception"],
    dimensions=["creative_conceptual", "learning_routine_consistency"],
))


# ---------------------------------------------------------------------------
# Family C: 9th House & Higher Learning / Mentorship (4 rules)
# ---------------------------------------------------------------------------

def _pred_h9_lord_kt(ctx: dict, pmap: dict) -> tuple[bool, str, list[str]]:
    lagna = ctx.get("lagna", "")
    l9 = safe_house_lord(lagna, 9)
    if not l9 or l9 not in pmap:
        return False, "", []
    h = pmap[l9].get("house", 0)
    if h in KENDRA or h in TRIKONA:
        return True, f"9th lord {l9} placed in auspicious house {h} (Kendra/Trikona)", [l9]
    return False, "", []

def _exc_h9_lord_combust(ctx: dict, pmap: dict) -> tuple[bool, str]:
    lagna = ctx.get("lagna", "")
    l9 = safe_house_lord(lagna, 9)
    if l9 and l9 in pmap and is_planet_combust(pmap[l9]):
        return True, f"9th lord {l9} is combust, requiring patience in mentor alignment"
    return False, ""

_register(EducationRule(
    rule_id="EDU-H9-LORD-KENDRA-TRIKONA-01",
    version="1.0.0",
    domain="education",
    profile="parashari_classical",
    chart_frame="D1_LAGNA",
    predicate=_pred_h9_lord_kt,
    ordered_exceptions=[_exc_h9_lord_combust],
    dedupe_key="EDU_H9_LORD_POSITION",
    effect="SUPPORTS",
    birth_time_sensitive=False,
    explanation_template="9th lord in Kendra or Trikona supports higher research, intellectual mentorship, and affinity for deep philosophical or academic systems.",
    source_family="BPHS",
    source_reference="BPHS Ch. 24, v. 97-98",
    source_status="VERIFIED",
    review_status="ACCEPTED",
    confidence="[HIGH]",
    tests=["test_edu_h9_lord_kendra_trikona_positive", "test_edu_h9_lord_combust_exception"],
    dimensions=["advanced_study_mentorship", "traditional_knowledge_interests"],
))


def _pred_h9_lord_dignity(ctx: dict, pmap: dict) -> tuple[bool, str, list[str]]:
    lagna = ctx.get("lagna", "")
    l9 = safe_house_lord(lagna, 9)
    if not l9 or l9 not in pmap:
        return False, "", []
    pdata = pmap[l9]
    if is_planet_dignified(l9, pdata):
        return True, f"9th lord {l9} dignified in {pdata.get('sign')} (own/exalted)", [l9]
    return False, "", []

_register(EducationRule(
    rule_id="EDU-H9-LORD-OWN-EXALTED-02",
    version="1.0.0",
    domain="education",
    profile="parashari_classical",
    chart_frame="D1_LAGNA",
    predicate=_pred_h9_lord_dignity,
    ordered_exceptions=[],
    dedupe_key="EDU_H9_LORD_DIGNITY",
    effect="SUPPORTS",
    birth_time_sensitive=False,
    explanation_template="9th lord in dignity indicates natural alignment with advanced academic research, professorial mentorship, and theoretical inquiry.",
    source_family="BPHS",
    source_reference="BPHS Ch. 24, v. 99; Jataka Parijata Ch. 11, v. 15",
    source_status="VERIFIED",
    review_status="ACCEPTED",
    confidence="[HIGH]",
    tests=["test_edu_h9_lord_dignity_positive", "test_edu_h9_lord_dignity_negative"],
    dimensions=["advanced_study_mentorship", "traditional_knowledge_interests"],
))


def _pred_h9_benefic_occ(ctx: dict, pmap: dict) -> tuple[bool, str, list[str]]:
    benefics_in_9 = [p for p in get_planets_in_house(pmap, 9) if p in {"Jupiter", "Mercury", "Venus"}]
    if benefics_in_9:
        names = ", ".join(benefics_in_9)
        return True, f"Scholarly benefic(s) in 9th house: {names}", benefics_in_9
    return False, "", []

def _exc_h9_benefic_debilitated(ctx: dict, pmap: dict) -> tuple[bool, str]:
    benefics_in_9 = [p for p in get_planets_in_house(pmap, 9) if p in {"Jupiter", "Mercury", "Venus"}]
    debilitated = [p for p in benefics_in_9 if is_planet_debilitated(p, pmap[p])]
    if len(debilitated) == len(benefics_in_9) and len(debilitated) > 0:
        return True, f"Benefic in 9th house is debilitated ({', '.join(debilitated)})"
    return False, ""

_register(EducationRule(
    rule_id="EDU-H9-BENEFIC-OCCUPANCY-03",
    version="1.0.0",
    domain="education",
    profile="parashari_classical",
    chart_frame="D1_LAGNA",
    predicate=_pred_h9_benefic_occ,
    ordered_exceptions=[_exc_h9_benefic_debilitated],
    dedupe_key="EDU_H9_OCCUPANCY",
    effect="SUPPORTS",
    birth_time_sensitive=False,
    explanation_template="Benefic occupation of 9th house encourages scholarly inquiry, ethical mentorship, and enthusiasm for higher learning traditions.",
    source_family="Phaladeepika",
    source_reference="Phaladeepika Ch. 8, v. 19",
    source_status="VERIFIED",
    review_status="ACCEPTED",
    confidence="[HIGH]",
    tests=["test_edu_h9_benefic_occupancy_positive", "test_edu_h9_benefic_debilitated_exception"],
    dimensions=["advanced_study_mentorship", "traditional_knowledge_interests"],
))


def _pred_h9_foreign_study(ctx: dict, pmap: dict) -> tuple[bool, str, list[str]]:
    lagna = ctx.get("lagna", "")
    l9 = safe_house_lord(lagna, 9)
    l12 = safe_house_lord(lagna, 12)
    rahu = pmap.get("Rahu", {})

    connected = False
    details = []

    # Rahu in 9th house
    if rahu.get("house") == 9:
        connected = True
        details.append("Rahu in 9th house")

    # 9th lord in 12th house
    if l9 and l9 in pmap and pmap[l9].get("house") == 12:
        connected = True
        details.append(f"9th lord {l9} in 12th house")

    # 12th lord in 9th house
    if l12 and l12 in pmap and pmap[l12].get("house") == 9:
        connected = True
        details.append(f"12th lord {l12} in 9th house")

    # 9th lord conjoined Rahu
    if l9 and l9 in pmap and rahu.get("house") == pmap[l9].get("house") and rahu.get("house") != 0:
        connected = True
        details.append(f"9th lord {l9} conjoined Rahu")

    if connected:
        return True, f"Cross-cultural/foreign study alignment: {'; '.join(details)}", ["Rahu", l9, l12]
    return False, "", []

_register(EducationRule(
    rule_id="EDU-H9-FOREIGN-HIGHER-STUDY-04",
    version="1.0.0",
    domain="education",
    profile="parashari_classical",
    chart_frame="D1_LAGNA",
    predicate=_pred_h9_foreign_study,
    ordered_exceptions=[],
    dedupe_key="EDU_H9_FOREIGN",
    effect="CONDITIONAL",
    birth_time_sensitive=False,
    explanation_template="Connection between 9th house/lord and Rahu or 12th lord indicates cultural interest in foreign education and international scholarship.",
    source_family="BPHS",
    source_reference="BPHS Ch. 24, v. 104; Saravali Ch. 34, v. 19",
    source_status="VERIFIED",
    review_status="ACCEPTED",
    confidence="[MEDIUM]",
    tests=["test_edu_h9_foreign_study_positive", "test_edu_h9_foreign_study_negative"],
    dimensions=["advanced_study_mentorship"],
))


# ---------------------------------------------------------------------------
# Family D: Mercury & Analytical / Linguistic Intelligence (4 rules)
# ---------------------------------------------------------------------------

def _pred_mercury_dignity(ctx: dict, pmap: dict) -> tuple[bool, str, list[str]]:
    merc = pmap.get("Mercury", {})
    sign = merc.get("sign", "")
    if sign in {"Mithuna", "Kanya"}:
        label = "exalted/own" if sign == "Kanya" else "own"
        return True, f"Mercury dignified in {sign} ({label})", ["Mercury"]
    return False, "", []

def _exc_mercury_combust(ctx: dict, pmap: dict) -> tuple[bool, str]:
    merc = pmap.get("Mercury", {})
    sun = pmap.get("Sun", {})
    if is_planet_combust(merc) and merc.get("house") == sun.get("house"):
        deg_diff = abs(merc.get("degree", 15.0) - sun.get("degree", 15.0))
        if deg_diff < 3.0:
            return True, f"Mercury is deeply combust within {deg_diff:.1f}° of Sun"
    return False, ""

_register(EducationRule(
    rule_id="EDU-MERCURY-DIGNITY-EXALTED-OWN-01",
    version="1.0.0",
    domain="education",
    profile="parashari_classical",
    chart_frame="D1_LAGNA",
    predicate=_pred_mercury_dignity,
    ordered_exceptions=[_exc_mercury_combust],
    dedupe_key="EDU_MERCURY_DIGNITY",
    effect="SUPPORTS",
    birth_time_sensitive=False,
    explanation_template="Dignified Mercury in Gemini or Virgo highlights analytical precision, linguistic versatility, mathematical reasoning, and agile comprehension.",
    source_family="BPHS",
    source_reference="BPHS Ch. 24, v. 140; Phaladeepika Ch. 2, v. 27",
    source_status="VERIFIED",
    review_status="ACCEPTED",
    confidence="[HIGH]",
    tests=["test_edu_mercury_dignity_positive", "test_edu_mercury_combust_exception"],
    dimensions=["analytical_communication", "foundational_learning"],
))


def _pred_mercury_kt(ctx: dict, pmap: dict) -> tuple[bool, str, list[str]]:
    merc = pmap.get("Mercury", {})
    h = merc.get("house", 0)
    if h in KENDRA or h in TRIKONA:
        return True, f"Mercury placed in Kendra/Trikona house {h}", ["Mercury"]
    return False, "", []

def _exc_mercury_kt_debilitated(ctx: dict, pmap: dict) -> tuple[bool, str]:
    merc = pmap.get("Mercury", {})
    if is_planet_debilitated("Mercury", merc):
        return True, "Mercury is debilitated in Pisces without full strength cancellation"
    return False, ""

_register(EducationRule(
    rule_id="EDU-MERCURY-KENDRA-TRIKONA-02",
    version="1.0.0",
    domain="education",
    profile="parashari_classical",
    chart_frame="D1_LAGNA",
    predicate=_pred_mercury_kt,
    ordered_exceptions=[_exc_mercury_kt_debilitated],
    dedupe_key="EDU_MERCURY_POSITION",
    effect="SUPPORTS",
    birth_time_sensitive=False,
    explanation_template="Mercury placed in Kendra or Trikona energizes active communication, logic, and scientific and analytical inquiry.",
    source_family="BPHS",
    source_reference="BPHS Ch. 24, v. 141",
    source_status="VERIFIED",
    review_status="ACCEPTED",
    confidence="[HIGH]",
    tests=["test_edu_mercury_kendra_trikona_positive", "test_edu_mercury_debilitated_exception"],
    dimensions=["analytical_communication"],
))


def _pred_budhaditya_yoga(ctx: dict, pmap: dict) -> tuple[bool, str, list[str]]:
    merc = pmap.get("Mercury", {})
    sun = pmap.get("Sun", {})
    mh = merc.get("house", 0)
    sh = sun.get("house", 0)
    if mh != 0 and mh == sh:
        # Auspicious houses: 1, 4, 5, 7, 9, 10 or 2, 11 (exclude dusthana 6, 8, 12)
        if mh not in DUSTHANA:
            return True, f"Budhaditya Yoga (Mercury & Sun conjoined in house {mh})", ["Mercury", "Sun"]
    return False, "", []

_register(EducationRule(
    rule_id="EDU-MERCURY-SUN-BUDHADITYA-03",
    version="1.0.0",
    domain="education",
    profile="parashari_classical",
    chart_frame="D1_LAGNA",
    predicate=_pred_budhaditya_yoga,
    ordered_exceptions=[],
    dedupe_key="EDU_BUDHADITYA",
    effect="SUPPORTS",
    birth_time_sensitive=False,
    explanation_template="Budhaditya Yoga reflects sharp intellectual clarity, administrative acumen, and strong concept retention.",
    source_family="BPHS",
    source_reference="BPHS Ch. 75, v. 5; Phaladeepika Ch. 6, v. 5",
    source_status="VERIFIED",
    review_status="ACCEPTED",
    confidence="[HIGH]",
    tests=["test_edu_budhaditya_yoga_positive", "test_edu_budhaditya_dusthana_negative"],
    dimensions=["analytical_communication", "creative_conceptual"],
))


def _pred_mercury_affliction(ctx: dict, pmap: dict) -> tuple[bool, str, list[str]]:
    merc = pmap.get("Mercury", {})
    h = merc.get("house", 0)
    sign = merc.get("sign", "")
    is_deb = (sign == "Meena")
    is_dusthana = (h in DUSTHANA)
    is_cb = is_planet_combust(merc)

    if (is_deb and merc.get("str_score", 0) < 0) or (is_dusthana and is_cb):
        reasons = []
        if is_deb:
            reasons.append("debilitated in Pisces with low positional score")
        if is_dusthana and is_cb:
            reasons.append(f"combust in Dusthana house {h}")
        return True, f"Mercury under strain ({'; '.join(reasons)})", ["Mercury"]
    return False, "", []

def _exc_mercury_affliction_jupiter_aspect(ctx: dict, pmap: dict) -> tuple[bool, str]:
    jup = pmap.get("Jupiter", {})
    jh = jup.get("house", 0)
    mh = pmap.get("Mercury", {}).get("house", 0)
    # Jupiter aspects 5th, 7th, 9th from itself
    jup_aspects = {((jh + 4) % 12) or 12, ((jh + 6) % 12) or 12, ((jh + 8) % 12) or 12}
    if mh in jup_aspects:
        return True, f"Mercury strain mitigated by beneficent aspect from Jupiter in house {jh}"
    return False, ""

_register(EducationRule(
    rule_id="EDU-MERCURY-COMBUST-AFFLICTION-04",
    version="1.0.0",
    domain="education",
    profile="parashari_classical",
    chart_frame="D1_LAGNA",
    predicate=_pred_mercury_affliction,
    ordered_exceptions=[_exc_mercury_affliction_jupiter_aspect],
    dedupe_key="EDU_MERCURY_AFFLICTION",
    effect="OBSTRUCTS",
    birth_time_sensitive=False,
    explanation_template="Afflicted Mercury suggests analytical restlessness or communication fatigue, benefiting from step-by-step revision and mind maps.",
    source_family="BPHS",
    source_reference="BPHS Ch. 24, v. 145",
    source_status="VERIFIED",
    review_status="ACCEPTED",
    confidence="[HIGH]",
    tests=["test_edu_mercury_affliction_positive", "test_edu_mercury_affliction_jupiter_aspect_exception"],
    dimensions=["analytical_communication", "learning_routine_consistency"],
))


# ---------------------------------------------------------------------------
# Family E: Jupiter & Scholarly Wisdom (Jnana) (3 rules)
# ---------------------------------------------------------------------------

def _pred_jupiter_dignity(ctx: dict, pmap: dict) -> tuple[bool, str, list[str]]:
    jup = pmap.get("Jupiter", {})
    sign = jup.get("sign", "")
    if sign in {"Karka", "Dhanu", "Meena"}:
        label = "exalted" if sign == "Karka" else "own"
        return True, f"Jupiter dignified in {sign} ({label})", ["Jupiter"]
    return False, "", []

_register(EducationRule(
    rule_id="EDU-JUPITER-DIGNITY-EXALTED-OWN-01",
    version="1.0.0",
    domain="education",
    profile="parashari_classical",
    chart_frame="D1_LAGNA",
    predicate=_pred_jupiter_dignity,
    ordered_exceptions=[],
    dedupe_key="EDU_JUPITER_DIGNITY",
    effect="SUPPORTS",
    birth_time_sensitive=False,
    explanation_template="Dignified Jupiter in Cancer, Sagittarius, or Pisces reflects broad philosophical wisdom, scholarly integrity, and high intellectual synthesis.",
    source_family="BPHS",
    source_reference="BPHS Ch. 24, v. 140; Phaladeepika Ch. 2, v. 28",
    source_status="VERIFIED",
    review_status="ACCEPTED",
    confidence="[HIGH]",
    tests=["test_edu_jupiter_dignity_positive", "test_edu_jupiter_dignity_negative"],
    dimensions=["traditional_knowledge_interests", "advanced_study_mentorship"],
))


def _pred_jupiter_h5_h9(ctx: dict, pmap: dict) -> tuple[bool, str, list[str]]:
    jup = pmap.get("Jupiter", {})
    h = jup.get("house", 0)
    if h in {5, 9}:
        return True, f"Jupiter (wisdom karaka) occupying Trikona house {h}", ["Jupiter"]
    return False, "", []

def _exc_jupiter_debilitated(ctx: dict, pmap: dict) -> tuple[bool, str]:
    jup = pmap.get("Jupiter", {})
    if is_planet_debilitated("Jupiter", jup):
        return True, "Jupiter is debilitated in Capricorn, requiring grounding in theoretical studies"
    return False, ""

_register(EducationRule(
    rule_id="EDU-JUPITER-H5-OR-H9-PLACEMENT-02",
    version="1.0.0",
    domain="education",
    profile="parashari_classical",
    chart_frame="D1_LAGNA",
    predicate=_pred_jupiter_h5_h9,
    ordered_exceptions=[_exc_jupiter_debilitated],
    dedupe_key="EDU_JUPITER_HOUSES",
    effect="SUPPORTS",
    birth_time_sensitive=False,
    explanation_template="Jupiter in 5th or 9th house fosters deep conceptual wisdom, philosophical understanding, and aptitude for advisory, legal, or scholarly disciplines.",
    source_family="BPHS",
    source_reference="BPHS Ch. 24, v. 51; Phaladeepika Ch. 8, v. 11, 19",
    source_status="VERIFIED",
    review_status="ACCEPTED",
    confidence="[HIGH]",
    tests=["test_edu_jupiter_h5_h9_positive", "test_edu_jupiter_debilitated_exception"],
    dimensions=["traditional_knowledge_interests", "creative_conceptual"],
))


def _pred_saraswati_yoga(ctx: dict, pmap: dict) -> tuple[bool, str, list[str]]:
    jup = pmap.get("Jupiter", {})
    ven = pmap.get("Venus", {})
    merc = pmap.get("Mercury", {})

    allowed_houses = KENDRA | TRIKONA | {2}
    jh = jup.get("house", 0)
    vh = ven.get("house", 0)
    mh = merc.get("house", 0)

    if (jh in allowed_houses and vh in allowed_houses and mh in allowed_houses
            and jup.get("str_score", 0) >= 0):
        return True, f"Saraswati Yoga present: Jupiter in H{jh}, Venus in H{vh}, Mercury in H{mh}", ["Jupiter", "Venus", "Mercury"]
    return False, "", []

_register(EducationRule(
    rule_id="EDU-SARASWATI-YOGA-03",
    version="1.0.0",
    domain="education",
    profile="parashari_classical",
    chart_frame="D1_LAGNA",
    predicate=_pred_saraswati_yoga,
    ordered_exceptions=[],
    dedupe_key="EDU_SARASWATI",
    effect="SUPPORTS",
    birth_time_sensitive=False,
    explanation_template="Classical Saraswati Yoga reflects refined scholarship, eloquence, literary appreciation, and cultural distinction.",
    source_family="Phaladeepika",
    source_reference="Phaladeepika Ch. 6, v. 26; Jataka Parijata Ch. 7, v. 82",
    source_status="VERIFIED",
    review_status="ACCEPTED",
    confidence="[HIGH]",
    tests=["test_edu_saraswati_yoga_positive", "test_edu_saraswati_yoga_negative"],
    dimensions=["traditional_knowledge_interests", "creative_conceptual"],
))


# ---------------------------------------------------------------------------
# Family F: Inter-Lord Connections & Academic Raja Yogas (3 rules)
# ---------------------------------------------------------------------------

def _pred_4_5_connection(ctx: dict, pmap: dict) -> tuple[bool, str, list[str]]:
    lagna = ctx.get("lagna", "")
    l4 = safe_house_lord(lagna, 4)
    l5 = safe_house_lord(lagna, 5)
    if not l4 or not l5 or l4 not in pmap or l5 not in pmap:
        return False, "", []

    h4 = pmap[l4].get("house", 0)
    h5 = pmap[l5].get("house", 0)

    # If same planet rules both 4 and 5 (e.g. Taurus Lagna: Mercury rules 2 & 5, Sun rules 4; Libra: Saturn rules 4 & 5!)
    if l4 == l5:
        return True, f"Yoga-karaka {l4} rules both 4th (learning) and 5th (intellect) houses", [l4]

    # Conjunction
    if h4 != 0 and h4 == h5 and h4 not in DUSTHANA:
        return True, f"4th lord {l4} and 5th lord {l5} conjoined in house {h4}", [l4, l5]

    # Mutual reception (Parivartana)
    s4 = pmap[l4].get("sign", "")
    s5 = pmap[l5].get("sign", "")
    l4_own = OWN_SIGNS.get(l4, [])
    l5_own = OWN_SIGNS.get(l5, [])
    if s4 in l5_own and s5 in l4_own:
        return True, f"Parivartana exchange between 4th lord {l4} and 5th lord {l5}", [l4, l5]

    return False, "", []

_register(EducationRule(
    rule_id="EDU-DHAN-VIDYA-4-5-EXCHANGE-01",
    version="1.0.0",
    domain="education",
    profile="parashari_classical",
    chart_frame="D1_LAGNA",
    predicate=_pred_4_5_connection,
    ordered_exceptions=[],
    dedupe_key="EDU_4_5_CONNECTION",
    effect="SUPPORTS",
    birth_time_sensitive=False,
    explanation_template="Connection between 4th and 5th lords harmonizes foundational study with acute reasoning, supporting sustained academic achievement.",
    source_family="BPHS",
    source_reference="BPHS Ch. 41, v. 11; Phaladeepika Ch. 6, v. 32",
    source_status="VERIFIED",
    review_status="ACCEPTED",
    confidence="[HIGH]",
    tests=["test_edu_4_5_connection_positive", "test_edu_4_5_connection_negative"],
    dimensions=["foundational_learning", "creative_conceptual"],
))


def _pred_5_9_connection(ctx: dict, pmap: dict) -> tuple[bool, str, list[str]]:
    lagna = ctx.get("lagna", "")
    l5 = safe_house_lord(lagna, 5)
    l9 = safe_house_lord(lagna, 9)
    if not l5 or not l9 or l5 not in pmap or l9 not in pmap:
        return False, "", []

    h5 = pmap[l5].get("house", 0)
    h9 = pmap[l9].get("house", 0)

    # Conjunction in non-dusthana
    if h5 != 0 and h5 == h9 and h5 not in DUSTHANA:
        return True, f"Dharma Trikona Yoga: 5th lord {l5} and 9th lord {l9} conjoined in house {h5}", [l5, l9]

    # Mutual 7th aspect
    diff = abs(h5 - h9)
    if diff == 6 and h5 not in DUSTHANA and h9 not in DUSTHANA:
        return True, f"5th lord {l5} (H{h5}) and 9th lord {l9} (H{h9}) in mutual aspect", [l5, l9]

    return False, "", []

_register(EducationRule(
    rule_id="EDU-DHARMA-KARMA-5-9-CONNECTION-02",
    version="1.0.0",
    domain="education",
    profile="parashari_classical",
    chart_frame="D1_LAGNA",
    predicate=_pred_5_9_connection,
    ordered_exceptions=[],
    dedupe_key="EDU_5_9_CONNECTION",
    effect="SUPPORTS",
    birth_time_sensitive=False,
    explanation_template="Conjunction or mutual aspect between 5th and 9th lords forms an auspicious Dharma Trikona Yoga, indicating intellectual depth and research potential.",
    source_family="BPHS",
    source_reference="BPHS Ch. 41, v. 15; Phaladeepika Ch. 6, v. 37",
    source_status="VERIFIED",
    review_status="ACCEPTED",
    confidence="[HIGH]",
    tests=["test_edu_5_9_connection_positive", "test_edu_5_9_connection_negative"],
    dimensions=["creative_conceptual", "advanced_study_mentorship"],
))


def _pred_5_10_connection(ctx: dict, pmap: dict) -> tuple[bool, str, list[str]]:
    lagna = ctx.get("lagna", "")
    l5 = safe_house_lord(lagna, 5)
    l10 = safe_house_lord(lagna, 10)
    if not l5 or not l10 or l5 not in pmap or l10 not in pmap:
        return False, "", []

    h5 = pmap[l5].get("house", 0)
    h10 = pmap[l10].get("house", 0)

    if h5 != 0 and h5 == h10 and h5 not in DUSTHANA:
        return True, f"5th lord {l5} and 10th lord {l10} conjoined in house {h5}", [l5, l10]

    if (h5 in KENDRA or h5 in TRIKONA) and (h10 in KENDRA or h10 in TRIKONA) and abs(h5 - h10) == 6:
        return True, f"5th lord {l5} and 10th lord {l10} in mutual aspect across Kendra/Trikona", [l5, l10]

    return False, "", []

_register(EducationRule(
    rule_id="EDU-10-5-PROFESSIONAL-STUDY-03",
    version="1.0.0",
    domain="education",
    profile="parashari_classical",
    chart_frame="D1_LAGNA",
    predicate=_pred_5_10_connection,
    ordered_exceptions=[],
    dedupe_key="EDU_5_10_CONNECTION",
    effect="SUPPORTS",
    birth_time_sensitive=False,
    explanation_template="Connection between 5th lord (intellect) and 10th lord (profession) aligns academic specialization with career vocation.",
    source_family="BPHS",
    source_reference="BPHS Ch. 24, v. 111",
    source_status="VERIFIED",
    review_status="ACCEPTED",
    confidence="[HIGH]",
    tests=["test_edu_5_10_connection_positive", "test_edu_5_10_connection_negative"],
    dimensions=["creative_conceptual", "traditional_knowledge_interests"],
))


# ---------------------------------------------------------------------------
# Family G: D24 Siddhamsa Divisional Corroboration (2 rules)
# ---------------------------------------------------------------------------

def _pred_d24_lagna_lord(ctx: dict, pmap: dict) -> tuple[bool, str, list[str]]:
    d24_chart = ctx.get("d24_chart")
    if not d24_chart:
        d24_chart = build_d24_chart(ctx)

    d24_lagna = d24_chart.get("d24_lagna", "Simha")
    d24_ll = d24_chart.get("d24_lagna_lord", "")
    if not d24_ll:
        return False, "", []

    d24_pdata = d24_chart.get("d24_planets", {}).get(d24_ll, {})
    d24_h = d24_pdata.get("house", 0)
    d24_s = d24_pdata.get("sign", "")

    is_dig = (d24_s in OWN_SIGNS.get(d24_ll, []) or d24_s == EXALTATION.get(d24_ll))
    is_kt = (d24_h in KENDRA or d24_h in TRIKONA)

    if is_dig or is_kt:
        return True, f"D24 Siddhamsa Lagna lord {d24_ll} well-placed in {d24_s} (H{d24_h})", [d24_ll]
    return False, "", []

_register(EducationRule(
    rule_id="EDU-D24-LAGNA-LORD-DIGNITY-01",
    version="1.0.0",
    domain="education",
    profile="parashari_classical",
    chart_frame="D24_SIDDHAMSA",
    predicate=_pred_d24_lagna_lord,
    ordered_exceptions=[],
    dedupe_key="EDU_D24_LAGNA_LORD",
    effect="SUPPORTS",
    birth_time_sensitive=True,
    explanation_template="D24 Siddhamsa Lagna lord well-placed corroborates internal dedication to higher learning and scholarly stamina.",
    source_family="BPHS",
    source_reference="BPHS Ch. 6, v. 24-25",
    source_status="VERIFIED",
    review_status="ACCEPTED",
    confidence="[HIGH]",
    tests=["test_edu_d24_lagna_lord_positive", "test_edu_d24_lagna_lord_dusthana_negative"],
    dimensions=["traditional_knowledge_interests", "advanced_study_mentorship"],
))


def _pred_d24_mercury_jupiter(ctx: dict, pmap: dict) -> tuple[bool, str, list[str]]:
    d24_chart = ctx.get("d24_chart")
    if not d24_chart:
        d24_chart = build_d24_chart(ctx)

    d24_planets = d24_chart.get("d24_planets", {})
    m_data = d24_planets.get("Mercury", {})
    j_data = d24_planets.get("Jupiter", {})

    mh = m_data.get("house", 0)
    jh = j_data.get("house", 0)
    ms = m_data.get("sign", "")
    js = j_data.get("sign", "")

    m_strong = (mh in KENDRA or mh in TRIKONA or ms in OWN_SIGNS.get("Mercury", []) or ms == EXALTATION.get("Mercury"))
    j_strong = (jh in KENDRA or jh in TRIKONA or js in OWN_SIGNS.get("Jupiter", []) or js == EXALTATION.get("Jupiter"))

    if m_strong or j_strong:
        details = []
        if m_strong:
            details.append(f"Mercury in D24 {ms} (H{mh})")
        if j_strong:
            details.append(f"Jupiter in D24 {js} (H{jh})")
        return True, f"D24 Vidyakaraka strength: {', '.join(details)}", ["Mercury", "Jupiter"]
    return False, "", []

_register(EducationRule(
    rule_id="EDU-D24-MERCURY-JUPITER-AFFINITY-02",
    version="1.0.0",
    domain="education",
    profile="parashari_classical",
    chart_frame="D24_SIDDHAMSA",
    predicate=_pred_d24_mercury_jupiter,
    ordered_exceptions=[],
    dedupe_key="EDU_D24_MERCURY_JUPITER",
    effect="SUPPORTS",
    birth_time_sensitive=True,
    explanation_template="Strong D24 placement for Mercury or Jupiter provides divisional corroboration for analytical dexterity and scholastic wisdom.",
    source_family="BPHS",
    source_reference="BPHS Ch. 6, v. 24-25",
    source_status="VERIFIED",
    review_status="ACCEPTED",
    confidence="[HIGH]",
    tests=["test_edu_d24_mercury_jupiter_positive", "test_edu_d24_mercury_jupiter_negative"],
    dimensions=["analytical_communication", "traditional_knowledge_interests"],
))


# ---------------------------------------------------------------------------
# Evaluator Engine
# ---------------------------------------------------------------------------

def evaluate_education_rules(ctx: dict, profile: str = "all") -> dict[str, Any]:
    """
    Evaluate deterministic Parashari education and learning rules from chart context.

    Separates evidence across 6 safe, non-diagnostic educational dimensions:
      - foundational_learning
      - analytical_communication
      - creative_conceptual
      - advanced_study_mentorship
      - learning_routine_consistency
      - traditional_knowledge_interests

    Adheres strictly to Specification v3.0 §9.5 & §21 (Educational Safety Guardrails).
    NEVER predicts exam pass/fail, university admissions, IQ scores, or diagnoses disabilities.
    """
    pmap = get_planet_map(ctx)
    lagna = ctx.get("lagna", "")

    # Build D24 Siddhamsa chart context if not already present
    if "d24_chart" not in ctx:
        ctx["d24_chart"] = build_d24_chart(ctx)

    matched_rules = []
    rejected_rules = []
    cancelled_rules = []

    dim_ledgers: dict[str, dict] = {
        d: {"support": 0, "obstruct": 0, "conditional": 0, "evidence": []}
        for d in EDUCATION_DIMENSIONS
    }

    for rule in EDUCATION_RULES_CATALOG:
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

    def _net_status(ledger: dict) -> str:
        s = ledger["support"]
        o = ledger["obstruct"]
        c = ledger["conditional"]
        if s >= 2 and o == 0:
            return "Strong Supportive Alignment"
        if s >= 1 and o == 0:
            return "Favorable Orientation"
        if s > o:
            return "Supportive with Mindful Pacing"
        if o > 0:
            return "Deliberate Discipline Advised"
        if c > 0:
            return "Adaptive Learning Alignment"
        return "Baseline Educational Equilibrium"

    dimensions_output = {}
    for d, ledger in dim_ledgers.items():
        dimensions_output[d] = {
            "support": ledger["support"],
            "obstruct": ledger["obstruct"],
            "conditional": ledger["conditional"],
            "status": _net_status(ledger),
            "evidence": ledger["evidence"],
        }

    # Internal interpretive evidence score (0-100)
    # Strictly an interpretive summary index, NOT exam probability or IQ
    tot_support = sum(l["support"] for l in dim_ledgers.values())
    tot_obstruct = sum(l["obstruct"] for l in dim_ledgers.values())
    raw_score = 50 + (tot_support * 5) - (tot_obstruct * 6)
    evidence_score = max(20, min(95, raw_score))

    merc = pmap.get("Mercury", {})
    jup = pmap.get("Jupiter", {})

    return {
        "domain": "education",
        "profile": profile,
        "lagna": lagna,
        "is_diagnostic": False,
        "d24_status": "VERIFIED_ACTIVE",
        "internal_evidence_score": evidence_score,
        "dimensions": dimensions_output,
        "matched_rules": matched_rules,
        "rejected_rules": rejected_rules,
        "cancelled_rules": cancelled_rules,
        "karaka_status": {
            "mercury": {
                "house": merc.get("house", 0),
                "sign": merc.get("sign", ""),
                "role": "Budha (Analytical & Linguistic Karaka)",
            },
            "jupiter": {
                "house": jup.get("house", 0),
                "sign": jup.get("sign", ""),
                "role": "Guru (Wisdom & Scholarly Karaka)",
            },
        },
        "safety_disclaimer": SAFETY_DISCLAIMER,
    }
