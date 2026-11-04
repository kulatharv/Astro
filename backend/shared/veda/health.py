"""
Classical Vedic Astrology Health & Wellbeing Engine (Pure Shared Library).

Implements 12 canonical, deterministic, strictly non-diagnostic Parashari wellbeing
and lifestyle rules, separating 4 safe dimensions:
  1. Vitality & Physical Stamina (vitality_stamina)
  2. Daily Rhythm & Routine Discipline (routine_balance)
  3. Mindfulness & Restorative Rest (mindfulness_rest)
  4. Traditional Ayurvedic Lifestyle Temperament (lifestyle_temperament)

Strictly adheres to Master Specification v3.0 §9.4 & §21 (Medical Safety Guardrails).
ABSOLUTE PROHIBITION: Never diagnoses diseases, predicts longevity or time of death,
predicts surgeries or hospitalizations, predicts mental health disorders, or advises
on medication or medical treatments.
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
UPACHAYA = {3, 6, 10, 11}

CLASSICAL_7 = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
NATURAL_BENEFICS = {"Jupiter", "Venus", "Mercury", "Moon"}
NATURAL_MALEFICS = {"Sun", "Mars", "Saturn", "Rahu", "Ketu"}

FIRE_SIGNS = {"Mesha", "Simha", "Dhanu"}
EARTH_SIGNS = {"Vrishabha", "Kanya", "Makara"}
AIR_SIGNS = {"Mithuna", "Tula", "Kumbha"}
WATER_SIGNS = {"Karka", "Vrischika", "Meena"}

WELLBEING_DIMENSIONS = [
    "vitality_stamina",
    "routine_balance",
    "mindfulness_rest",
    "lifestyle_temperament",
]

SAFETY_DISCLAIMER = (
    "AstroLogic AI provides non-diagnostic cultural, lifestyle, and astrological interpretations only. "
    "Astrological charts CANNOT diagnose, treat, prevent, or predict diseases, medical conditions, surgical events, "
    "fertility outcomes, mental health disorders, or longevity. For any medical symptoms, diagnosis, treatment, "
    "or health decisions, always consult a licensed medical physician or qualified healthcare provider."
)


# ---------------------------------------------------------------------------
# Canonical Health Rule Dataclass
# ---------------------------------------------------------------------------

@dataclass
class HealthRule:
    rule_id: str
    version: str
    domain: str
    profile: str
    chart_frame: str
    predicate: Callable[[dict, dict], tuple[bool, str, list[str]]]
    ordered_exceptions: list[Callable[[dict, dict], tuple[bool, str]]] = field(default_factory=list)
    dedupe_key: Optional[str] = None
    effect: str = "SUPPORTS"  # SUPPORTS, CONDITIONAL
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
    """Safely resolve house lord with normalization."""
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
    """Check if planet is in its own sign."""
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


# ---------------------------------------------------------------------------
# Individual Predicates & Exceptions for Permitted Rules
# ---------------------------------------------------------------------------

def _pred_vitality_lagna_benefic(ctx: dict, pmap: dict) -> tuple[bool, str, list[str]]:
    # Natural benefics in 1st house or aspecting 1st house
    h1_benefics = [p for p in planets_in_house(pmap, 1) if p in NATURAL_BENEFICS]
    aspecting = [
        p for p in ("Jupiter", "Venus", "Mercury")
        if aspects_house(p, house_of(pmap, p), 1) and p not in h1_benefics
    ]
    all_benefics = h1_benefics + aspecting
    if all_benefics:
        return True, f"Benefic influence ({', '.join(all_benefics)}) on Ascendant supports baseline vitality and stamina", all_benefics
    return False, "", []


def _pred_vitality_sun_dignity(ctx: dict, pmap: dict) -> tuple[bool, str, list[str]]:
    # Sun in Kendra, Trikona, or own/exaltation
    h = house_of(pmap, "Sun")
    s = sign_of(pmap, "Sun")
    if (h in (KENDRA | TRIKONA) or is_in_own_sign(pmap, "Sun") or is_exalted(pmap, "Sun")) and not is_debilitated(pmap, "Sun"):
        return True, f"Sun (vitality karaka) in auspicious dignity in H{h} ({s}) encourages active physical movement", ["Sun"]
    return False, "", []


def _pred_mindfulness_moon_calm(ctx: dict, pmap: dict) -> tuple[bool, str, list[str]]:
    # Moon in exalted sign (Taurus), own sign (Cancer), or aspected by Jupiter
    s = sign_of(pmap, "Moon")
    jup_aspect = aspects_house("Jupiter", house_of(pmap, "Jupiter"), house_of(pmap, "Moon"))
    if s in ("Vrishabha", "Karka", "Meena") or jup_aspect:
        return True, "Harmonious lunar placement or Jupiter aspect supports mental calm and restful sleep hygiene", ["Moon"]
    return False, "", []


def _pred_routine_saturn_discipline(ctx: dict, pmap: dict) -> tuple[bool, str, list[str]]:
    # Saturn in Upachayas {3, 6, 11} or own signs
    h = house_of(pmap, "Saturn")
    if (h in UPACHAYA or is_in_own_sign(pmap, "Saturn")) and not is_debilitated(pmap, "Saturn"):
        return True, f"Saturn in H{h} encourages consistency, disciplined daily routines, and endurance", ["Saturn"]
    return False, "", []


def _pred_rest_12th_benefic(ctx: dict, pmap: dict) -> tuple[bool, str, list[str]]:
    # Benefics in 12th house (Restorative nocturnal sleep)
    h12_benefics = [p for p in planets_in_house(pmap, 12) if p in NATURAL_BENEFICS]
    if h12_benefics:
        return True, f"Benefic influence ({', '.join(h12_benefics)}) in 12th house encourages restorative sleep and quiet relaxation", h12_benefics
    return False, "", []


def _pred_temperament_pitta(ctx: dict, pmap: dict) -> tuple[bool, str, list[str]]:
    # Lagna in Fire sign
    lagna = ctx.get("lagna", "")
    if lagna in FIRE_SIGNS:
        return True, f"Ascendant in {lagna} reflects a traditional Ayurvedic Pitta temperament (metabolic drive, priority on hydration and pacing)", []
    return False, "", []


def _pred_temperament_kapha(ctx: dict, pmap: dict) -> tuple[bool, str, list[str]]:
    # Lagna in Water or Earth sign
    lagna = ctx.get("lagna", "")
    if lagna in (WATER_SIGNS | EARTH_SIGNS):
        return True, f"Ascendant in {lagna} reflects a traditional Ayurvedic Kapha temperament (steady endurance, benefits from vigorous daily activity)", []
    return False, "", []


def _pred_temperament_vata(ctx: dict, pmap: dict) -> tuple[bool, str, list[str]]:
    # Lagna in Air sign
    lagna = ctx.get("lagna", "")
    if lagna in AIR_SIGNS:
        return True, f"Ascendant in {lagna} reflects a traditional Ayurvedic Vata temperament (active mental pace, benefits from warm grounding routines)", []
    return False, "", []


def _pred_habit_6th_lord_upachaya(ctx: dict, pmap: dict) -> tuple[bool, str, list[str]]:
    lagna = ctx.get("lagna", "")
    l6 = safe_house_lord(lagna, 6)
    if not l6:
        return False, "", []
    h = house_of(pmap, l6)
    if h in UPACHAYA:
        return True, f"6th lord {l6} placed in Upachaya H{h} indicates strength in overcoming inertia through structured habits", [l6]
    return False, "", []


def _pred_mindfulness_pace_awareness(ctx: dict, pmap: dict) -> tuple[bool, str, list[str]]:
    # Mars or Rahu on Moon or Lagna
    h_moon = house_of(pmap, "Moon")
    influences = []
    if house_of(pmap, "Mars") in (1, h_moon):
        influences.append("Mars")
    if house_of(pmap, "Rahu") in (1, h_moon):
        influences.append("Rahu")
    if influences:
        return True, f"{' and '.join(influences)} dynamic presence suggests mindful pacing, intentional unwinding, and screen-free rest", influences
    return False, "", []


def _pred_rejuvenation_jupiter_grace(ctx: dict, pmap: dict) -> tuple[bool, str, list[str]]:
    # Jupiter aspecting Lagna, 5th, or 9th
    j_h = house_of(pmap, "Jupiter")
    aspects_tgt = [tgt for tgt in (1, 5, 9) if aspects_house("Jupiter", j_h, tgt)]
    if aspects_tgt:
        return True, "Jupiter casts expansive benefic aspect on primary houses, supporting natural resilience and vitality", ["Jupiter"]
    return False, "", []


def _pred_routine_solar_diurnal(ctx: dict, pmap: dict) -> tuple[bool, str, list[str]]:
    # Sun in 1st or 10th
    h = house_of(pmap, "Sun")
    if h in (1, 10):
        return True, f"Sun prominent in H{h} aligns well with early morning circadian sunlight exposure and regular daily rhythm", ["Sun"]
    return False, "", []


# ---------------------------------------------------------------------------
# Permitted Non-Diagnostic Wellbeing Rule Catalog (12 Rules)
# ---------------------------------------------------------------------------

HEALTH_RULES_CATALOG: list[HealthRule] = [
    HealthRule(
        rule_id="HEALTH-VITALITY-LAGNA-BENEFIC-01",
        version="1.0.0",
        domain="health",
        profile="parashari_classical",
        chart_frame="D1",
        predicate=_pred_vitality_lagna_benefic,
        ordered_exceptions=[],
        dedupe_key="DEDUPE-HEALTH-LAGNA-BENEFIC",
        effect="SUPPORTS",
        explanation_template="Benefic association on Lagna supports natural baseline physical vitality and stamina.",
        source_family="Parashari",
        source_reference="BPHS Ch. 24, v. 3-4",
        source_status="VERIFIED",
        review_status="ACCEPTED",
        confidence="HIGH",
        tests=["test_wp5d_health_lagna_benefic"],
        dimensions=["vitality_stamina"],
    ),
    HealthRule(
        rule_id="HEALTH-VITALITY-SUN-DIGNITY-02",
        version="1.0.0",
        domain="health",
        profile="parashari_classical",
        chart_frame="D1",
        predicate=_pred_vitality_sun_dignity,
        ordered_exceptions=[],
        dedupe_key="DEDUPE-HEALTH-SUN-VITALITY",
        effect="SUPPORTS",
        explanation_template="Sun in auspicious dignity encourages energetic willpower and active physical habits.",
        source_family="Parashari",
        source_reference="BPHS Ch. 24, v. 140; Phaladeepika Ch. 2, v. 24",
        source_status="VERIFIED",
        review_status="ACCEPTED",
        confidence="HIGH",
        tests=["test_wp5d_health_sun_dignity"],
        dimensions=["vitality_stamina"],
    ),
    HealthRule(
        rule_id="HEALTH-MINDFULNESS-MOON-CALM-03",
        version="1.0.0",
        domain="health",
        profile="parashari_classical",
        chart_frame="D1",
        predicate=_pred_mindfulness_moon_calm,
        ordered_exceptions=[],
        dedupe_key="DEDUPE-HEALTH-MOON-CALM",
        effect="SUPPORTS",
        explanation_template="Favorable Moon dignity fosters mental relaxation, equanimity, and restful sleep habits.",
        source_family="Parashari",
        source_reference="BPHS Ch. 76, v. 1-2; Phaladeepika Ch. 6, v. 10",
        source_status="VERIFIED",
        review_status="ACCEPTED",
        confidence="HIGH",
        tests=["test_wp5d_health_moon_calm"],
        dimensions=["mindfulness_rest"],
    ),
    HealthRule(
        rule_id="HEALTH-ROUTINE-SATURN-DISCIPLINE-04",
        version="1.0.0",
        domain="health",
        profile="parashari_classical",
        chart_frame="D1",
        predicate=_pred_routine_saturn_discipline,
        ordered_exceptions=[],
        dedupe_key="DEDUPE-HEALTH-SATURN-DISCIPLINE",
        effect="SUPPORTS",
        explanation_template="Saturn in Upachaya supports consistent self-discipline, routine adherence, and endurance.",
        source_family="Parashari",
        source_reference="BPHS Ch. 24, v. 67; Phaladeepika Ch. 8, v. 13",
        source_status="VERIFIED",
        review_status="ACCEPTED",
        confidence="HIGH",
        tests=["test_wp5d_health_saturn_discipline"],
        dimensions=["routine_balance"],
    ),
    HealthRule(
        rule_id="HEALTH-REST-12TH-BENEFIC-05",
        version="1.0.0",
        domain="health",
        profile="parashari_classical",
        chart_frame="D1",
        predicate=_pred_rest_12th_benefic,
        ordered_exceptions=[],
        dedupe_key="DEDUPE-HEALTH-12TH-REST",
        effect="SUPPORTS",
        explanation_template="Benefics influencing the 12th house indicate restorative sleep hygiene and quiet retreat.",
        source_family="Parashari",
        source_reference="BPHS Ch. 24, v. 135; Phaladeepika Ch. 8, v. 25",
        source_status="VERIFIED",
        review_status="ACCEPTED",
        confidence="HIGH",
        tests=["test_wp5d_health_12th_rest"],
        dimensions=["mindfulness_rest"],
    ),
    HealthRule(
        rule_id="HEALTH-TEMPERAMENT-PITTA-06",
        version="1.0.0",
        domain="health",
        profile="parashari_classical",
        chart_frame="D1",
        predicate=_pred_temperament_pitta,
        ordered_exceptions=[],
        dedupe_key="DEDUPE-HEALTH-TEMPERAMENT",
        effect="SUPPORTS",
        explanation_template="Traditional Pitta temperament suggests prioritizing hydration, cooling routines, and pacing during intense exertion.",
        source_family="Ayurvedic Tradition",
        source_reference="Charaka Samhita Sutrasthana Ch. 1; BPHS Ch. 3, v. 21",
        source_status="VERIFIED",
        review_status="ACCEPTED",
        confidence="HIGH",
        tests=["test_wp5d_health_temperament_pitta"],
        dimensions=["lifestyle_temperament"],
    ),
    HealthRule(
        rule_id="HEALTH-TEMPERAMENT-KAPHA-07",
        version="1.0.0",
        domain="health",
        profile="parashari_classical",
        chart_frame="D1",
        predicate=_pred_temperament_kapha,
        ordered_exceptions=[],
        dedupe_key="DEDUPE-HEALTH-TEMPERAMENT",
        effect="SUPPORTS",
        explanation_template="Traditional Kapha temperament suggests maintaining regular vigorous physical activity and structured schedules.",
        source_family="Ayurvedic Tradition",
        source_reference="Charaka Samhita Sutrasthana Ch. 1; BPHS Ch. 3, v. 22",
        source_status="VERIFIED",
        review_status="ACCEPTED",
        confidence="HIGH",
        tests=["test_wp5d_health_temperament_kapha"],
        dimensions=["lifestyle_temperament"],
    ),
    HealthRule(
        rule_id="HEALTH-TEMPERAMENT-VATA-08",
        version="1.0.0",
        domain="health",
        profile="parashari_classical",
        chart_frame="D1",
        predicate=_pred_temperament_vata,
        ordered_exceptions=[],
        dedupe_key="DEDUPE-HEALTH-TEMPERAMENT",
        effect="SUPPORTS",
        explanation_template="Traditional Vata temperament suggests cultivating warm grounding meals, regular sleep schedules, and reduced sensory overstimulation.",
        source_family="Ayurvedic Tradition",
        source_reference="Charaka Samhita Sutrasthana Ch. 1; BPHS Ch. 3, v. 23",
        source_status="VERIFIED",
        review_status="ACCEPTED",
        confidence="HIGH",
        tests=["test_wp5d_health_temperament_vata"],
        dimensions=["lifestyle_temperament"],
    ),
    HealthRule(
        rule_id="HEALTH-HABIT-6TH-LORD-UPACHAYA-09",
        version="1.0.0",
        domain="health",
        profile="parashari_classical",
        chart_frame="D1",
        predicate=_pred_habit_6th_lord_upachaya,
        ordered_exceptions=[],
        dedupe_key="DEDUPE-HEALTH-6TH-HABIT",
        effect="SUPPORTS",
        explanation_template="6th lord in Upachaya supports proactive habit formation and resilience in daily self-care.",
        source_family="Parashari",
        source_reference="BPHS Ch. 24, v. 67",
        source_status="VERIFIED",
        review_status="ACCEPTED",
        confidence="HIGH",
        tests=["test_wp5d_health_6th_habit"],
        dimensions=["routine_balance"],
    ),
    HealthRule(
        rule_id="HEALTH-MINDFULNESS-PACE-AWARENESS-10",
        version="1.0.0",
        domain="health",
        profile="parashari_classical",
        chart_frame="D1",
        predicate=_pred_mindfulness_pace_awareness,
        ordered_exceptions=[],
        dedupe_key="DEDUPE-HEALTH-PACE-AWARENESS",
        effect="CONDITIONAL",
        explanation_template="Active planetary tempo suggests scheduling intentional pauses, mindful breathing, and screen-free unwind time.",
        source_family="Parashari",
        source_reference="Saravali Ch. 30, v. 12",
        source_status="VERIFIED",
        review_status="ACCEPTED",
        confidence="HIGH",
        tests=["test_wp5d_health_pace_awareness"],
        dimensions=["mindfulness_rest"],
    ),
    HealthRule(
        rule_id="HEALTH-REJUVENATION-JUPITER-GRACE-11",
        version="1.0.0",
        domain="health",
        profile="parashari_classical",
        chart_frame="D1",
        predicate=_pred_rejuvenation_jupiter_grace,
        ordered_exceptions=[],
        dedupe_key="DEDUPE-HEALTH-JUPITER-GRACE",
        effect="SUPPORTS",
        explanation_template="Jupiter aspect on key houses encourages a positive outlook, outdoor rejuvenation, and wholesome nourishment.",
        source_family="Parashari",
        source_reference="BPHS Ch. 24, v. 9; Phaladeepika Ch. 6, v. 22",
        source_status="VERIFIED",
        review_status="ACCEPTED",
        confidence="HIGH",
        tests=["test_wp5d_health_jupiter_grace"],
        dimensions=["vitality_stamina"],
    ),
    HealthRule(
        rule_id="HEALTH-ROUTINE-SOLAR-DIURNAL-12",
        version="1.0.0",
        domain="health",
        profile="parashari_classical",
        chart_frame="D1",
        predicate=_pred_routine_solar_diurnal,
        ordered_exceptions=[],
        dedupe_key="DEDUPE-HEALTH-SOLAR-DIURNAL",
        effect="SUPPORTS",
        explanation_template="Solar prominence encourages early circadian alignment, morning light exposure, and regular daytime activity.",
        source_family="Parashari",
        source_reference="BPHS Ch. 24, v. 5; Phaladeepika Ch. 2, v. 25",
        source_status="VERIFIED",
        review_status="ACCEPTED",
        confidence="HIGH",
        tests=["test_wp5d_health_solar_diurnal"],
        dimensions=["routine_balance"],
    ),
]


# ---------------------------------------------------------------------------
# Evaluator Engine
# ---------------------------------------------------------------------------

def evaluate_health_rules(ctx: dict, profile: str = "parashari_classical") -> dict:
    """
    Evaluate the strictly non-diagnostic Health & Wellbeing rule pack.

    Separates evidence across 4 safe, non-medical wellbeing dimensions:
      - vitality_stamina
      - routine_balance
      - mindfulness_rest
      - lifestyle_temperament

    Adheres strictly to Specification v3.0 §9.4 & §21 (Medical Safety Guardrails).
    NEVER diagnoses diseases, predicts longevity/mortality, or advises on medical treatments.
    """
    pmap = get_planet_map(ctx)
    lagna = ctx.get("lagna", "")

    matched_rules = []
    rejected_rules = []
    cancelled_rules = []

    dim_ledgers: dict[str, dict] = {
        d: {"support": 0, "conditional": 0, "evidence": []}
        for d in WELLBEING_DIMENSIONS
    }

    for rule in HEALTH_RULES_CATALOG:
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
                elif rule.effect == "CONDITIONAL":
                    ledger["conditional"] += 1
                ledger["evidence"].append(reason)

    def _net_status(ledger: dict) -> str:
        s = ledger["support"]
        c = ledger["conditional"]
        if s >= 2:
            return "Strong Supportive Habit Alignment"
        if s >= 1:
            return "Supportive Alignment"
        if c > 0:
            return "Mindful Pacing Advised"
        return "Baseline Equilibrium"

    dimensions_output = {}
    for d, ledger in dim_ledgers.items():
        dimensions_output[d] = {
            "support": ledger["support"],
            "conditional": ledger["conditional"],
            "status": _net_status(ledger),
            "evidence": ledger["evidence"],
        }

    return {
        "domain": "health",
        "profile": profile,
        "lagna": lagna,
        "is_diagnostic": False,
        "dimensions": dimensions_output,
        "matched_rules": matched_rules,
        "rejected_rules": rejected_rules,
        "cancelled_rules": cancelled_rules,
        "safety_disclaimer": SAFETY_DISCLAIMER,
    }
