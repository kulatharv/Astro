"""
Classical Vedic Astrology Children & Progeny Domain Rule Pack (Pure Shared Library).

Implements 21 canonical, deterministic Parashari rules regarding family caregiving,
youth mentorship, generational continuity, and parental responsibility, separating 5 safe dimensions:
  1. Family Caregiving Values (family_caregiving_values)
  2. Intellectual Mentorship (intellectual_mentorship)
  3. Next-Generation Continuity (next_gen_continuity)
  4. Parental Responsibility & Discipline (parental_responsibility_discipline)
  5. Spiritual & Cultural Traditions (spiritual_cultural_traditions)

Includes mathematically verified D7 Saptamsa (Chaturvimshamsa) calculation per BPHS Ch. 6, v. 9-10.

Strictly adheres to Master Specification v3.0 §9.6 & §21 (Medical & Reproductive Safety Guardrails).
ABSOLUTE PROHIBITION: Never assesses fertility or infertility, predicts pregnancy or conception dates,
predicts miscarriage/stillbirth, predicts number of children, determines fetal sex/gender (PC-PNDT Act compliance),
predicts child mortality/health, or advises on reproductive choices.
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

PROGENY_DIMENSIONS = [
    "family_caregiving_values",
    "intellectual_mentorship",
    "next_gen_continuity",
    "parental_responsibility_discipline",
    "spiritual_cultural_traditions",
]

SAFETY_DISCLAIMER = (
    "AstroLogic AI provides non-deterministic cultural, philosophical, and astrological reflections only. "
    "Astrological charts CANNOT evaluate medical fertility, reproductive health, conception likelihood, pregnancy outcomes, "
    "or predict the number, sex, or health of children. For all reproductive, medical, or family planning guidance, "
    "always consult a licensed medical physician or certified healthcare specialist."
)


# ---------------------------------------------------------------------------
# Canonical Progeny Rule Dataclass
# ---------------------------------------------------------------------------

@dataclass
class ProgenyRule:
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
# D7 Saptamsa Calculator (BPHS Ch. 6, v. 9-10)
# ---------------------------------------------------------------------------

def calculate_saptamsha_d7(sign: str, degree: float) -> str:
    """
    Calculate Saptamsa (D7) rashi according to classical BPHS Ch. 6, v. 9-10.

    Each sign of 30° is divided into 7 equal parts of 30°/7 ≈ 4.2857142857° (4° 17' 8.57'').
    - In Odd signs (Mesha, Mithuna, Simha, Tula, Dhanu, Kumbha), counting starts from the sign itself.
    - In Even signs (Vrishabha, Karka, Kanya, Vrischika, Makara, Meena), counting starts from the 7th sign therefrom.

    Parameters:
        sign: Sanskrit name of the sign (e.g., 'Mesha', 'Vrishabha')
        degree: Longitudinal position within the sign [0.0, 30.0)

    Returns:
        Sanskrit name of the D7 sign.
    """
    if not sign:
        return "Mesha"
    norm = sign.strip().capitalize()
    if norm == "Vrishika":
        norm = "Vrischika"
    if norm not in SIGNS_SK:
        return "Mesha"

    sign_idx = SIGNS_SK.index(norm)
    # Odd signs (Mesha=0, Mithuna=2, Simha=4, etc.) are even indices: 0, 2, 4, 6, 8, 10
    is_odd = (sign_idx % 2 == 0)
    start_idx = sign_idx if is_odd else (sign_idx + 6) % 12

    deg = float(degree) % 30.0
    part_size = 30.0 / 7.0
    part = int(deg / part_size)
    if part > 6:
        part = 6
    elif part < 0:
        part = 0

    return SIGNS_SK[(start_idx + part) % 12]


def build_d7_chart(ctx: dict) -> dict[str, Any]:
    """
    Construct D7 positions and houses for Lagna and all planets.
    Uses planet degrees and lagna degree if provided, else defaults to 15.0°.
    """
    pmap = ctx.get("planet_map", {})
    lagna_sign = ctx.get("lagna", "Mesha")
    lagna_deg = ctx.get("ascendant_degree", 15.0)

    d7_lagna = calculate_saptamsha_d7(lagna_sign, lagna_deg)
    d7_lagna_idx = SIGNS_SK.index(d7_lagna)

    d7_planets: dict[str, dict[str, Any]] = {}
    for p, pdata in pmap.items():
        psign = pdata.get("sign", "Mesha")
        pdeg = pdata.get("degree", 15.0)
        d7_sign = calculate_saptamsha_d7(psign, pdeg)
        d7_sign_idx = SIGNS_SK.index(d7_sign)
        d7_house = ((d7_sign_idx - d7_lagna_idx) % 12) + 1
        d7_planets[p] = {
            "sign": d7_sign,
            "house": d7_house,
            "lord": SIGN_LORDS.get(d7_sign, ""),
        }

    return {
        "d7_lagna": d7_lagna,
        "d7_lagna_lord": SIGN_LORDS.get(d7_lagna, ""),
        "d7_planets": d7_planets,
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
# Canonical 21 Rules (Families A through G)
# ---------------------------------------------------------------------------

PROGENY_RULES_CATALOG: list[ProgenyRule] = []


def _register(rule: ProgenyRule) -> ProgenyRule:
    PROGENY_RULES_CATALOG.append(rule)
    return rule


# ---------------------------------------------------------------------------
# Family A: 5th House & Foundational Caregiving / Youth Guidance (3 rules)
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
        return True, f"5th lord {l5} is combust, requiring conscious emotional attunement"
    return False, ""

_register(ProgenyRule(
    rule_id="PROG-H5-LORD-KENDRA-TRIKONA-01",
    version="1.0.0",
    domain="progeny",
    profile="parashari_classical",
    chart_frame="D1_LAGNA",
    predicate=_pred_h5_lord_kt,
    ordered_exceptions=[_exc_h5_lord_kt_combust],
    dedupe_key="PROG_H5_LORD_POSITION",
    effect="SUPPORTS",
    birth_time_sensitive=False,
    explanation_template="5th lord in Kendra or Trikona supports warmth, mentoring engagement, and constructive responsibility toward youth.",
    source_family="BPHS",
    source_reference="BPHS Ch. 24, v. 49-50; Phaladeepika Ch. 6, v. 12",
    source_status="VERIFIED",
    review_status="ACCEPTED",
    confidence="[HIGH]",
    tests=["test_prog_h5_lord_kendra_trikona_positive", "test_prog_h5_lord_kendra_trikona_combust_exception"],
    dimensions=["family_caregiving_values", "intellectual_mentorship"],
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

_register(ProgenyRule(
    rule_id="PROG-H5-LORD-OWN-EXALTED-02",
    version="1.0.0",
    domain="progeny",
    profile="parashari_classical",
    chart_frame="D1_LAGNA",
    predicate=_pred_h5_lord_dignity,
    ordered_exceptions=[],
    dedupe_key="PROG_H5_LORD_DIGNITY",
    effect="SUPPORTS",
    birth_time_sensitive=False,
    explanation_template="5th lord in dignity reflects deep commitment to parental care, creative legacy, and moral guidance.",
    source_family="BPHS",
    source_reference="BPHS Ch. 24, v. 51; Saravali Ch. 34, v. 7",
    source_status="VERIFIED",
    review_status="ACCEPTED",
    confidence="[HIGH]",
    tests=["test_prog_h5_lord_dignity_positive", "test_prog_h5_lord_dignity_negative"],
    dimensions=["family_caregiving_values", "spiritual_cultural_traditions"],
))


def _pred_h5_benefic_occ(ctx: dict, pmap: dict) -> tuple[bool, str, list[str]]:
    benefics_in_5 = [p for p in get_planets_in_house(pmap, 5) if p in NATURAL_BENEFICS]
    if benefics_in_5:
        names = ", ".join(benefics_in_5)
        return True, f"Benefic(s) occupying 5th house: {names}", benefics_in_5
    return False, "", []

def _exc_h5_benefic_debilitated(ctx: dict, pmap: dict) -> tuple[bool, str]:
    benefics_in_5 = [p for p in get_planets_in_house(pmap, 5) if p in NATURAL_BENEFICS]
    debilitated = [p for p in benefics_in_5 if is_planet_debilitated(p, pmap[p])]
    if len(debilitated) == len(benefics_in_5) and len(debilitated) > 0:
        return True, f"Benefic in 5th house is debilitated ({', '.join(debilitated)})"
    return False, ""

_register(ProgenyRule(
    rule_id="PROG-H5-BENEFIC-OCCUPANCY-03",
    version="1.0.0",
    domain="progeny",
    profile="parashari_classical",
    chart_frame="D1_LAGNA",
    predicate=_pred_h5_benefic_occ,
    ordered_exceptions=[_exc_h5_benefic_debilitated],
    dedupe_key="PROG_H5_OCCUPANCY",
    effect="SUPPORTS",
    birth_time_sensitive=False,
    explanation_template="Benefic occupation of 5th house fosters a peaceful, affectionate, and supportive domestic atmosphere for family harmony.",
    source_family="BPHS",
    source_reference="BPHS Ch. 24, v. 52",
    source_status="VERIFIED",
    review_status="ACCEPTED",
    confidence="[HIGH]",
    tests=["test_prog_h5_benefic_occupancy_positive", "test_prog_h5_benefic_debilitated_exception"],
    dimensions=["family_caregiving_values", "intellectual_mentorship"],
))


# ---------------------------------------------------------------------------
# Family B: 5th House Restraint & Mindful Pacing (3 rules)
# ---------------------------------------------------------------------------

def _pred_h5_lord_dusthana(ctx: dict, pmap: dict) -> tuple[bool, str, list[str]]:
    lagna = ctx.get("lagna", "")
    l5 = safe_house_lord(lagna, 5)
    if not l5 or l5 not in pmap:
        return False, "", []
    h = pmap[l5].get("house", 0)
    if h in DUSTHANA:
        return True, f"5th lord {l5} placed in Dusthana house {h}", [l5]
    return False, "", []

def _exc_h5_dusthana_own_sign(ctx: dict, pmap: dict) -> tuple[bool, str]:
    lagna = ctx.get("lagna", "")
    l5 = safe_house_lord(lagna, 5)
    if l5 and l5 in pmap and is_planet_dignified(l5, pmap[l5]):
        return True, f"5th lord {l5} is in own sign in house {pmap[l5].get('house')}, mitigating friction"
    return False, ""

_register(ProgenyRule(
    rule_id="PROG-H5-LORD-DUSTHANA-AFFLICTION-04",
    version="1.0.0",
    domain="progeny",
    profile="parashari_classical",
    chart_frame="D1_LAGNA",
    predicate=_pred_h5_lord_dusthana,
    ordered_exceptions=[_exc_h5_dusthana_own_sign],
    dedupe_key="PROG_H5_LORD_DUSTHANA",
    effect="OBSTRUCTS",
    birth_time_sensitive=False,
    explanation_template="5th lord in Dusthana highlights balancing personal priorities with family commitments, encouraging patient emotional pacing.",
    source_family="BPHS",
    source_reference="BPHS Ch. 24, v. 57",
    source_status="VERIFIED",
    review_status="ACCEPTED",
    confidence="[HIGH]",
    tests=["test_prog_h5_lord_dusthana_positive", "test_prog_h5_lord_dusthana_own_sign_exception"],
    dimensions=["parental_responsibility_discipline", "family_caregiving_values"],
))


def _pred_h5_saturn_discipline(ctx: dict, pmap: dict) -> tuple[bool, str, list[str]]:
    saturn = pmap.get("Saturn", {})
    sh = saturn.get("house", 0)
    lagna = ctx.get("lagna", "")
    l5 = safe_house_lord(lagna, 5)
    l5_h = pmap.get(l5, {}).get("house", 0) if l5 in pmap else 0

    # Saturn in 5th or aspecting 5th (Saturn aspects 3rd, 7th, 10th from itself)
    sat_aspects = {((sh + 2) % 12) or 12, ((sh + 6) % 12) or 12, ((sh + 9) % 12) or 12}
    if sh == 5 or 5 in sat_aspects or (l5_h != 0 and l5_h in sat_aspects):
        return True, f"Saturn influencing 5th house/lord (Saturn in H{sh})", ["Saturn"]
    return False, "", []

_register(ProgenyRule(
    rule_id="PROG-H5-SATURN-DISCIPLINE-05",
    version="1.0.0",
    domain="progeny",
    profile="parashari_classical",
    chart_frame="D1_LAGNA",
    predicate=_pred_h5_saturn_discipline,
    ordered_exceptions=[],
    dedupe_key="PROG_H5_SATURN_DISCIPLINE",
    effect="CONDITIONAL",
    birth_time_sensitive=False,
    explanation_template="Saturn connection to 5th house cultivates emotional maturity, structured discipline, and long-term parental responsibility.",
    source_family="BPHS",
    source_reference="BPHS Ch. 24, v. 54; Phaladeepika Ch. 8, v. 21",
    source_status="VERIFIED",
    review_status="ACCEPTED",
    confidence="[HIGH]",
    tests=["test_prog_h5_saturn_discipline_positive", "test_prog_h5_saturn_discipline_negative"],
    dimensions=["parental_responsibility_discipline"],
))


def _pred_h5_rahu_mentorship(ctx: dict, pmap: dict) -> tuple[bool, str, list[str]]:
    rahu = pmap.get("Rahu", {})
    if rahu.get("house") == 5:
        return True, "Rahu placed in 5th house indicates unconventional mentorship and creative thinking", ["Rahu"]
    return False, "", []

_register(ProgenyRule(
    rule_id="PROG-H5-RAHU-INNOVATIVE-MENTORSHIP-06",
    version="1.0.0",
    domain="progeny",
    profile="parashari_classical",
    chart_frame="D1_LAGNA",
    predicate=_pred_h5_rahu_mentorship,
    ordered_exceptions=[],
    dedupe_key="PROG_H5_RAHU_INNOVATION",
    effect="CONDITIONAL",
    birth_time_sensitive=False,
    explanation_template="Rahu in 5th house encourages innovative, open-minded, and culturally diverse approaches in guiding the younger generation.",
    source_family="BPHS",
    source_reference="BPHS Ch. 24, v. 55",
    source_status="VERIFIED",
    review_status="ACCEPTED",
    confidence="[HIGH]",
    tests=["test_prog_h5_rahu_mentorship_positive", "test_prog_h5_rahu_mentorship_negative"],
    dimensions=["intellectual_mentorship"],
))


# ---------------------------------------------------------------------------
# Family C: Jupiter as Traditional Significator (Putrakaraka / Guru) (4 rules)
# ---------------------------------------------------------------------------

def _pred_jupiter_dignity(ctx: dict, pmap: dict) -> tuple[bool, str, list[str]]:
    jup = pmap.get("Jupiter", {})
    sign = jup.get("sign", "")
    if sign in {"Karka", "Dhanu", "Meena"}:
        label = "exalted" if sign == "Karka" else "own"
        return True, f"Jupiter (significator) dignified in {sign} ({label})", ["Jupiter"]
    return False, "", []

_register(ProgenyRule(
    rule_id="PROG-JUPITER-DIGNITY-EXALTED-OWN-01",
    version="1.0.0",
    domain="progeny",
    profile="parashari_classical",
    chart_frame="D1_LAGNA",
    predicate=_pred_jupiter_dignity,
    ordered_exceptions=[],
    dedupe_key="PROG_JUPITER_DIGNITY",
    effect="SUPPORTS",
    birth_time_sensitive=False,
    explanation_template="Dignified Jupiter reflects broad wisdom, protective generosity, and ethical commitment in nurturing the next generation.",
    source_family="BPHS",
    source_reference="BPHS Ch. 24, v. 140; Phaladeepika Ch. 2, v. 28",
    source_status="VERIFIED",
    review_status="ACCEPTED",
    confidence="[HIGH]",
    tests=["test_prog_jupiter_dignity_positive", "test_prog_jupiter_dignity_negative"],
    dimensions=["spiritual_cultural_traditions", "intellectual_mentorship"],
))


def _pred_jupiter_kt(ctx: dict, pmap: dict) -> tuple[bool, str, list[str]]:
    jup = pmap.get("Jupiter", {})
    h = jup.get("house", 0)
    if h in KENDRA or h in TRIKONA:
        return True, f"Jupiter placed in auspicious house {h} (Kendra/Trikona)", ["Jupiter"]
    return False, "", []

def _exc_jupiter_debilitated(ctx: dict, pmap: dict) -> tuple[bool, str]:
    jup = pmap.get("Jupiter", {})
    if is_planet_debilitated("Jupiter", jup):
        return True, "Jupiter is debilitated in Capricorn, requiring conscious grounding in advisory roles"
    return False, ""

_register(ProgenyRule(
    rule_id="PROG-JUPITER-KENDRA-TRIKONA-02",
    version="1.0.0",
    domain="progeny",
    profile="parashari_classical",
    chart_frame="D1_LAGNA",
    predicate=_pred_jupiter_kt,
    ordered_exceptions=[_exc_jupiter_debilitated],
    dedupe_key="PROG_JUPITER_POSITION",
    effect="SUPPORTS",
    birth_time_sensitive=False,
    explanation_template="Jupiter in Kendra or Trikona provides strong moral leadership, protective support, and harmonious family traditions.",
    source_family="BPHS",
    source_reference="BPHS Ch. 24, v. 51; Phaladeepika Ch. 8, v. 11",
    source_status="VERIFIED",
    review_status="ACCEPTED",
    confidence="[HIGH]",
    tests=["test_prog_jupiter_kt_positive", "test_prog_jupiter_debilitated_exception"],
    dimensions=["family_caregiving_values", "intellectual_mentorship"],
))


def _pred_jupiter_h5_karakasthana(ctx: dict, pmap: dict) -> tuple[bool, str, list[str]]:
    jup = pmap.get("Jupiter", {})
    if jup.get("house") == 5:
        return True, "Jupiter in 5th house occupies its karakasthana, highlighting deep devotion to youth guidance", ["Jupiter"]
    return False, "", []

_register(ProgenyRule(
    rule_id="PROG-JUPITER-H5-OCCUPANCY-KARAKASTHANA-03",
    version="1.0.0",
    domain="progeny",
    profile="parashari_classical",
    chart_frame="D1_LAGNA",
    predicate=_pred_jupiter_h5_karakasthana,
    ordered_exceptions=[],
    dedupe_key="PROG_JUPITER_H5_KARAKASTHANA",
    effect="CONDITIONAL",
    birth_time_sensitive=False,
    explanation_template="Jupiter in 5th house reflects profound dedication to youth education; traditional Karako Bhavanashta reminder encourages balancing high standards with gentle patience.",
    source_family="Phaladeepika",
    source_reference="Phaladeepika Ch. 15, v. 28; Bhavartha Ratnakara Ch. 5, v. 1",
    source_status="VERIFIED",
    review_status="ACCEPTED",
    confidence="[HIGH]",
    tests=["test_prog_jupiter_h5_karakasthana_positive", "test_prog_jupiter_h5_karakasthana_negative"],
    dimensions=["intellectual_mentorship", "parental_responsibility_discipline"],
))


def _pred_jupiter_affliction(ctx: dict, pmap: dict) -> tuple[bool, str, list[str]]:
    jup = pmap.get("Jupiter", {})
    h = jup.get("house", 0)
    is_dusthana = (h in DUSTHANA)
    is_cb = is_planet_combust(jup)
    if is_dusthana and is_cb:
        return True, f"Jupiter combust in Dusthana house {h}, advising patient caregiving routines", ["Jupiter"]
    return False, "", []

_register(ProgenyRule(
    rule_id="PROG-JUPITER-AFFLICTION-COMBUST-04",
    version="1.0.0",
    domain="progeny",
    profile="parashari_classical",
    chart_frame="D1_LAGNA",
    predicate=_pred_jupiter_affliction,
    ordered_exceptions=[],
    dedupe_key="PROG_JUPITER_AFFLICTION",
    effect="OBSTRUCTS",
    birth_time_sensitive=False,
    explanation_template="Afflicted Jupiter suggests setting steady, realistic expectations and practicing mindful presence in family caregiving.",
    source_family="BPHS",
    source_reference="BPHS Ch. 24, v. 145",
    source_status="VERIFIED",
    review_status="ACCEPTED",
    confidence="[HIGH]",
    tests=["test_prog_jupiter_affliction_positive", "test_prog_jupiter_affliction_negative"],
    dimensions=["parental_responsibility_discipline"],
))


# ---------------------------------------------------------------------------
# Family D: 9th House as Bhavat Bhavam (5th from 5th) (3 rules)
# ---------------------------------------------------------------------------

def _pred_h9_lord_kt(ctx: dict, pmap: dict) -> tuple[bool, str, list[str]]:
    lagna = ctx.get("lagna", "")
    l9 = safe_house_lord(lagna, 9)
    if not l9 or l9 not in pmap:
        return False, "", []
    h = pmap[l9].get("house", 0)
    if h in KENDRA or h in TRIKONA:
        return True, f"9th lord {l9} (Bhavat Bhavam) placed in auspicious house {h}", [l9]
    return False, "", []

_register(ProgenyRule(
    rule_id="PROG-H9-LORD-KENDRA-TRIKONA-01",
    version="1.0.0",
    domain="progeny",
    profile="parashari_classical",
    chart_frame="D1_LAGNA",
    predicate=_pred_h9_lord_kt,
    ordered_exceptions=[],
    dedupe_key="PROG_H9_LORD_POSITION",
    effect="SUPPORTS",
    birth_time_sensitive=False,
    explanation_template="9th lord (5th from 5th) in Kendra or Trikona supports ethical continuity, philosophical wisdom, and transgenerational respect.",
    source_family="BPHS",
    source_reference="BPHS Ch. 24, v. 97-98",
    source_status="VERIFIED",
    review_status="ACCEPTED",
    confidence="[HIGH]",
    tests=["test_prog_h9_lord_kt_positive", "test_prog_h9_lord_kt_negative"],
    dimensions=["next_gen_continuity", "spiritual_cultural_traditions"],
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

_register(ProgenyRule(
    rule_id="PROG-H9-LORD-OWN-EXALTED-02",
    version="1.0.0",
    domain="progeny",
    profile="parashari_classical",
    chart_frame="D1_LAGNA",
    predicate=_pred_h9_lord_dignity,
    ordered_exceptions=[],
    dedupe_key="PROG_H9_LORD_DIGNITY",
    effect="SUPPORTS",
    birth_time_sensitive=False,
    explanation_template="Dignified 9th lord inspires generational moral leadership, honorable ancestral values, and virtuous family traditions.",
    source_family="BPHS",
    source_reference="BPHS Ch. 24, v. 99",
    source_status="VERIFIED",
    review_status="ACCEPTED",
    confidence="[HIGH]",
    tests=["test_prog_h9_lord_dignity_positive", "test_prog_h9_lord_dignity_negative"],
    dimensions=["next_gen_continuity", "spiritual_cultural_traditions"],
))


def _pred_h9_benefic_occ(ctx: dict, pmap: dict) -> tuple[bool, str, list[str]]:
    benefics_in_9 = [p for p in get_planets_in_house(pmap, 9) if p in {"Jupiter", "Venus", "Mercury"}]
    if benefics_in_9:
        names = ", ".join(benefics_in_9)
        return True, f"Benefic(s) occupying 9th house: {names}", benefics_in_9
    return False, "", []

_register(ProgenyRule(
    rule_id="PROG-H9-BENEFIC-OCCUPANCY-03",
    version="1.0.0",
    domain="progeny",
    profile="parashari_classical",
    chart_frame="D1_LAGNA",
    predicate=_pred_h9_benefic_occ,
    ordered_exceptions=[],
    dedupe_key="PROG_H9_OCCUPANCY",
    effect="SUPPORTS",
    birth_time_sensitive=False,
    explanation_template="Benefics in 9th house encourage upright role-modeling, cultural harmony, and respect for family lineage traditions.",
    source_family="Phaladeepika",
    source_reference="Phaladeepika Ch. 8, v. 19",
    source_status="VERIFIED",
    review_status="ACCEPTED",
    confidence="[HIGH]",
    tests=["test_prog_h9_benefic_occupancy_positive", "test_prog_h9_benefic_occupancy_negative"],
    dimensions=["next_gen_continuity", "spiritual_cultural_traditions"],
))


# ---------------------------------------------------------------------------
# Family E: Moon & Lagna Nurturing & Domestic Context (3 rules)
# ---------------------------------------------------------------------------

def _pred_moon_dignity(ctx: dict, pmap: dict) -> tuple[bool, str, list[str]]:
    moon = pmap.get("Moon", {})
    sign = moon.get("sign", "")
    if sign in {"Vrishabha", "Karka"}:
        label = "exalted" if sign == "Vrishabha" else "own"
        return True, f"Moon dignified in {sign} ({label})", ["Moon"]
    return False, "", []

_register(ProgenyRule(
    rule_id="PROG-MOON-DIGNITY-EXALTED-OWN-01",
    version="1.0.0",
    domain="progeny",
    profile="parashari_classical",
    chart_frame="D1_LAGNA",
    predicate=_pred_moon_dignity,
    ordered_exceptions=[],
    dedupe_key="PROG_MOON_DIGNITY",
    effect="SUPPORTS",
    birth_time_sensitive=False,
    explanation_template="Dignified Moon in Taurus or Cancer brings emotional warmth, intuitive empathy, and protective domestic nourishment.",
    source_family="BPHS",
    source_reference="BPHS Ch. 24, v. 140; Phaladeepika Ch. 2, v. 26",
    source_status="VERIFIED",
    review_status="ACCEPTED",
    confidence="[HIGH]",
    tests=["test_prog_moon_dignity_positive", "test_prog_moon_dignity_negative"],
    dimensions=["family_caregiving_values"],
))


def _pred_moon_5th_chandra_lagna(ctx: dict, pmap: dict) -> tuple[bool, str, list[str]]:
    moon = pmap.get("Moon", {})
    mh = moon.get("house", 0)
    if mh == 0:
        return False, "", []
    h5_chandra = ((mh + 4 - 1) % 12) + 1
    benefics = [p for p in get_planets_in_house(pmap, h5_chandra) if p in NATURAL_BENEFICS]
    if benefics:
        names = ", ".join(benefics)
        return True, f"5th house from Moon (Chandra Lagna H{h5_chandra}) occupied by benefic(s): {names}", benefics
    return False, "", []

_register(ProgenyRule(
    rule_id="PROG-MOON-5TH-CHANDRA-LAGNA-02",
    version="1.0.0",
    domain="progeny",
    profile="parashari_classical",
    chart_frame="D1_CHANDRA",
    predicate=_pred_moon_5th_chandra_lagna,
    ordered_exceptions=[],
    dedupe_key="PROG_MOON_5TH_CHANDRA",
    effect="SUPPORTS",
    birth_time_sensitive=False,
    explanation_template="Benefic alignment from Chandra Lagna reinforces emotional sensitivity, responsive caregiving, and harmonious parent-child rapport.",
    source_family="BPHS",
    source_reference="BPHS Ch. 24, v. 53",
    source_status="VERIFIED",
    review_status="ACCEPTED",
    confidence="[HIGH]",
    tests=["test_prog_moon_5th_chandra_lagna_positive", "test_prog_moon_5th_chandra_lagna_negative"],
    dimensions=["family_caregiving_values"],
))


def _pred_lagna_lord_5th(ctx: dict, pmap: dict) -> tuple[bool, str, list[str]]:
    lagna = ctx.get("lagna", "")
    l1 = safe_house_lord(lagna, 1)
    if not l1 or l1 not in pmap:
        return False, "", []
    h = pmap[l1].get("house", 0)
    if h == 5:
        return True, f"Lagna lord {l1} occupying 5th house", [l1]
    return False, "", []

_register(ProgenyRule(
    rule_id="PROG-LAGNA-LORD-5TH-CONNECTION-03",
    version="1.0.0",
    domain="progeny",
    profile="parashari_classical",
    chart_frame="D1_LAGNA",
    predicate=_pred_lagna_lord_5th,
    ordered_exceptions=[],
    dedupe_key="PROG_LAGNA_LORD_5TH",
    effect="SUPPORTS",
    birth_time_sensitive=False,
    explanation_template="Lagna lord in 5th house directs personal focus and purpose toward creative mentorship, education, and family nurturing.",
    source_family="BPHS",
    source_reference="BPHS Ch. 24, v. 3",
    source_status="VERIFIED",
    review_status="ACCEPTED",
    confidence="[HIGH]",
    tests=["test_prog_lagna_lord_5th_positive", "test_prog_lagna_lord_5th_negative"],
    dimensions=["family_caregiving_values", "intellectual_mentorship"],
))


# ---------------------------------------------------------------------------
# Family F: Inter-Lord Connections & Family Raja Yogas (3 rules)
# ---------------------------------------------------------------------------

def _pred_5_9_yoga(ctx: dict, pmap: dict) -> tuple[bool, str, list[str]]:
    lagna = ctx.get("lagna", "")
    l5 = safe_house_lord(lagna, 5)
    l9 = safe_house_lord(lagna, 9)
    if not l5 or not l9 or l5 not in pmap or l9 not in pmap:
        return False, "", []

    h5 = pmap[l5].get("house", 0)
    h9 = pmap[l9].get("house", 0)

    if h5 != 0 and h5 == h9 and h5 not in DUSTHANA:
        return True, f"Dharma Trikona Yoga: 5th lord {l5} and 9th lord {l9} conjoined in house {h5}", [l5, l9]

    if abs(h5 - h9) == 6 and h5 not in DUSTHANA and h9 not in DUSTHANA:
        return True, f"5th lord {l5} (H{h5}) and 9th lord {l9} (H{h9}) in mutual aspect", [l5, l9]

    return False, "", []

_register(ProgenyRule(
    rule_id="PROG-5-9-DHARMA-TRIKONA-YOGA-01",
    version="1.0.0",
    domain="progeny",
    profile="parashari_classical",
    chart_frame="D1_LAGNA",
    predicate=_pred_5_9_yoga,
    ordered_exceptions=[],
    dedupe_key="PROG_5_9_CONNECTION",
    effect="SUPPORTS",
    birth_time_sensitive=False,
    explanation_template="Conjunction or mutual aspect between 5th and 9th lords forms an auspicious Dharma Trikona Yoga, symbolizing noble family legacy.",
    source_family="BPHS",
    source_reference="BPHS Ch. 41, v. 15; Phaladeepika Ch. 6, v. 37",
    source_status="VERIFIED",
    review_status="ACCEPTED",
    confidence="[HIGH]",
    tests=["test_prog_5_9_yoga_positive", "test_prog_5_9_yoga_negative"],
    dimensions=["next_gen_continuity", "spiritual_cultural_traditions"],
))


def _pred_1_5_sambandha(ctx: dict, pmap: dict) -> tuple[bool, str, list[str]]:
    lagna = ctx.get("lagna", "")
    l1 = safe_house_lord(lagna, 1)
    l5 = safe_house_lord(lagna, 5)
    if not l1 or not l5 or l1 not in pmap or l5 not in pmap:
        return False, "", []

    h1 = pmap[l1].get("house", 0)
    h5 = pmap[l5].get("house", 0)

    if l1 == l5:
        return True, f"Single planet {l1} rules both Lagna and 5th house", [l1]

    if h1 != 0 and h1 == h5 and h1 not in DUSTHANA:
        return True, f"Lagna lord {l1} and 5th lord {l5} conjoined in house {h1}", [l1, l5]

    s1 = pmap[l1].get("sign", "")
    s5 = pmap[l5].get("sign", "")
    l1_own = OWN_SIGNS.get(l1, [])
    l5_own = OWN_SIGNS.get(l5, [])
    if s1 in l5_own and s5 in l1_own:
        return True, f"Parivartana exchange between Lagna lord {l1} and 5th lord {l5}", [l1, l5]

    return False, "", []

_register(ProgenyRule(
    rule_id="PROG-1-5-SAMBANDHA-YOGA-02",
    version="1.0.0",
    domain="progeny",
    profile="parashari_classical",
    chart_frame="D1_LAGNA",
    predicate=_pred_1_5_sambandha,
    ordered_exceptions=[],
    dedupe_key="PROG_1_5_CONNECTION",
    effect="SUPPORTS",
    birth_time_sensitive=False,
    explanation_template="Union between 1st and 5th lords harmonizes personal identity with caregiving commitment and affectionate parental devotion.",
    source_family="BPHS",
    source_reference="BPHS Ch. 41, v. 11",
    source_status="VERIFIED",
    review_status="ACCEPTED",
    confidence="[HIGH]",
    tests=["test_prog_1_5_sambandha_positive", "test_prog_1_5_sambandha_negative"],
    dimensions=["family_caregiving_values", "intellectual_mentorship"],
))


def _pred_4_5_connection(ctx: dict, pmap: dict) -> tuple[bool, str, list[str]]:
    lagna = ctx.get("lagna", "")
    l4 = safe_house_lord(lagna, 4)
    l5 = safe_house_lord(lagna, 5)
    if not l4 or not l5 or l4 not in pmap or l5 not in pmap:
        return False, "", []

    h4 = pmap[l4].get("house", 0)
    h5 = pmap[l5].get("house", 0)

    if l4 == l5:
        return True, f"Yoga-karaka {l4} rules both 4th (domestic foundation) and 5th (youth/intellect)", [l4]

    if h4 != 0 and h4 == h5 and h4 not in DUSTHANA:
        return True, f"4th lord {l4} and 5th lord {l5} conjoined in house {h4}", [l4, l5]

    return False, "", []

_register(ProgenyRule(
    rule_id="PROG-4-5-KENDRA-TRIKONA-UNION-03",
    version="1.0.0",
    domain="progeny",
    profile="parashari_classical",
    chart_frame="D1_LAGNA",
    predicate=_pred_4_5_connection,
    ordered_exceptions=[],
    dedupe_key="PROG_4_5_CONNECTION",
    effect="SUPPORTS",
    birth_time_sensitive=False,
    explanation_template="Connection between 4th and 5th lords establishes a supportive domestic home foundation for youth growth and family nourishment.",
    source_family="BPHS",
    source_reference="BPHS Ch. 41, v. 12",
    source_status="VERIFIED",
    review_status="ACCEPTED",
    confidence="[HIGH]",
    tests=["test_prog_4_5_connection_positive", "test_prog_4_5_connection_negative"],
    dimensions=["family_caregiving_values"],
))


# ---------------------------------------------------------------------------
# Family G: D7 Saptamsa Divisional Corroboration (2 rules)
# ---------------------------------------------------------------------------

def _pred_d7_lagna_lord(ctx: dict, pmap: dict) -> tuple[bool, str, list[str]]:
    d7_chart = ctx.get("d7_chart")
    if not d7_chart:
        d7_chart = build_d7_chart(ctx)

    d7_ll = d7_chart.get("d7_lagna_lord", "")
    if not d7_ll:
        return False, "", []

    d7_pdata = d7_chart.get("d7_planets", {}).get(d7_ll, {})
    d7_h = d7_pdata.get("house", 0)
    d7_s = d7_pdata.get("sign", "")

    is_dig = (d7_s in OWN_SIGNS.get(d7_ll, []) or d7_s == EXALTATION.get(d7_ll))
    is_kt = (d7_h in KENDRA or d7_h in TRIKONA)

    if is_dig or is_kt:
        return True, f"D7 Saptamsa Lagna lord {d7_ll} well-placed in {d7_s} (H{d7_h})", [d7_ll]
    return False, "", []

_register(ProgenyRule(
    rule_id="PROG-D7-LAGNA-LORD-DIGNITY-01",
    version="1.0.0",
    domain="progeny",
    profile="parashari_classical",
    chart_frame="D7_SAPTAMSA",
    predicate=_pred_d7_lagna_lord,
    ordered_exceptions=[],
    dedupe_key="PROG_D7_LAGNA_LORD",
    effect="SUPPORTS",
    birth_time_sensitive=True,
    explanation_template="D7 Saptamsa Lagna lord well-placed corroborates internal dedication, patience, and character strength in family caregiving.",
    source_family="BPHS",
    source_reference="BPHS Ch. 6, v. 9-10",
    source_status="VERIFIED",
    review_status="ACCEPTED",
    confidence="[HIGH]",
    tests=["test_prog_d7_lagna_lord_positive", "test_prog_d7_lagna_lord_negative"],
    dimensions=["family_caregiving_values", "parental_responsibility_discipline"],
))


def _pred_d7_jupiter_well_placed(ctx: dict, pmap: dict) -> tuple[bool, str, list[str]]:
    d7_chart = ctx.get("d7_chart")
    if not d7_chart:
        d7_chart = build_d7_chart(ctx)

    j_data = d7_chart.get("d7_planets", {}).get("Jupiter", {})
    jh = j_data.get("house", 0)
    js = j_data.get("sign", "")

    j_strong = (jh in KENDRA or jh in TRIKONA or js in OWN_SIGNS.get("Jupiter", []) or js == EXALTATION.get("Jupiter"))
    if j_strong:
        return True, f"Jupiter in D7 Saptamsa well-placed in {js} (H{jh})", ["Jupiter"]
    return False, "", []

_register(ProgenyRule(
    rule_id="PROG-D7-JUPITER-WELL-PLACED-02",
    version="1.0.0",
    domain="progeny",
    profile="parashari_classical",
    chart_frame="D7_SAPTAMSA",
    predicate=_pred_d7_jupiter_well_placed,
    ordered_exceptions=[],
    dedupe_key="PROG_D7_JUPITER",
    effect="SUPPORTS",
    birth_time_sensitive=True,
    explanation_template="Strong D7 Saptamsa placement for Jupiter corroborates moral guidance, protective benevolence, and transgenerational harmony.",
    source_family="BPHS",
    source_reference="BPHS Ch. 6, v. 9-10",
    source_status="VERIFIED",
    review_status="ACCEPTED",
    confidence="[HIGH]",
    tests=["test_prog_d7_jupiter_positive", "test_prog_d7_jupiter_negative"],
    dimensions=["spiritual_cultural_traditions", "intellectual_mentorship"],
))


# ---------------------------------------------------------------------------
# Evaluator Engine
# ---------------------------------------------------------------------------

def evaluate_progeny_rules(ctx: dict, profile: str = "all") -> dict[str, Any]:
    """
    Evaluate deterministic Parashari progeny and family caregiving rules from chart context.

    Separates evidence across 5 safe, non-diagnostic dimensions:
      - family_caregiving_values
      - intellectual_mentorship
      - next_gen_continuity
      - parental_responsibility_discipline
      - spiritual_cultural_traditions

    Adheres strictly to Specification v3.0 §9.6 & §21 (Medical & Reproductive Safety Guardrails).
    NEVER assesses fertility/infertility, predicts conception dates/pregnancy, determines child sex,
    predicts child counts, or diagnoses medical conditions.
    """
    pmap = get_planet_map(ctx)
    lagna = ctx.get("lagna", "")

    # Build D7 Saptamsa chart context if not already present
    if "d7_chart" not in ctx:
        ctx["d7_chart"] = build_d7_chart(ctx)

    matched_rules = []
    rejected_rules = []
    cancelled_rules = []

    dim_ledgers: dict[str, dict] = {
        d: {"support": 0, "obstruct": 0, "conditional": 0, "evidence": []}
        for d in PROGENY_DIMENSIONS
    }

    for rule in PROGENY_RULES_CATALOG:
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
            return "Patient Discipline Advised"
        if c > 0:
            return "Adaptive Caregiving Alignment"
        return "Baseline Caregiving Equilibrium"

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
    # Strictly an interpretive evidence index, NOT fertility probability or child likelihood
    tot_support = sum(l["support"] for l in dim_ledgers.values())
    tot_obstruct = sum(l["obstruct"] for l in dim_ledgers.values())
    raw_score = 50 + (tot_support * 5) - (tot_obstruct * 6)
    evidence_score = max(25, min(92, raw_score))

    jup = pmap.get("Jupiter", {})
    l5 = safe_house_lord(lagna, 5)

    return {
        "domain": "progeny",
        "profile": profile,
        "lagna": lagna,
        "is_diagnostic": False,
        "d7_status": "VERIFIED_ACTIVE",
        "internal_evidence_score": evidence_score,
        "dimensions": dimensions_output,
        "matched_rules": matched_rules,
        "rejected_rules": rejected_rules,
        "cancelled_rules": cancelled_rules,
        "karaka_status": {
            "jupiter": {
                "house": jup.get("house", 0),
                "sign": jup.get("sign", ""),
                "role": "Guru / Putrakaraka (Traditional Wisdom & Youth Significator)",
            },
            "fifth_lord": {
                "planet": l5,
                "house": pmap.get(l5, {}).get("house", 0) if l5 in pmap else 0,
                "role": "5th House Ruler (Buddhi, Mentorship, Caregiving)",
            },
        },
        "safety_disclaimer": SAFETY_DISCLAIMER,
    }
