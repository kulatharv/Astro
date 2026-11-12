"""
Classical Vedic Astrology Yoga Catalog (Pure Shared Library).

Implements 60+ classical Parashari, Jataka, and Phaladeepika yogas with
standardized rule schemas, structured predicates, explicit cancellation checks,
and classical source references.

Rule Schema:
  rule_id: Unique string identifier (e.g. 'YOGA-PANCHA-RUCHAKA-01')
  version: Version string (e.g. '1.0.0')
  name: Canonical name of the yoga
  category: Astrological family / category
  description: Classical significance and interpretation
  source_reference: Primary classical citation (e.g. 'BPHS Ch. 75, v. 1-2')
  predicate: Callable(pmap, lagna_sign, houses) -> (bool, str, list[str])
  cancellation_rules: List of Callable(pmap, lagna_sign, houses) -> (bool, str)
  enabled_by_default: bool (True for classical, False for contested modern)
  contested_modern: bool (True for Kaal Sarp and disputed modern heuristics)
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

MOVABLE_SIGNS = {"Mesha", "Karka", "Tula", "Makara"}
FIXED_SIGNS = {"Vrishabha", "Simha", "Vrischika", "Kumbha"}
DUAL_SIGNS = {"Mithuna", "Kanya", "Dhanu", "Meena"}


# ---------------------------------------------------------------------------
# YogaRule Dataclass
# ---------------------------------------------------------------------------

@dataclass
class YogaRule:
    rule_id: str
    version: str
    name: str
    category: str
    description: str
    source_reference: str
    predicate: Callable[[dict[str, dict], str, dict], tuple[bool, str, list[str]]]
    cancellation_rules: list[Callable[[dict[str, dict], str, dict], tuple[bool, str]]] = field(default_factory=list)
    enabled_by_default: bool = True
    contested_modern: bool = False
    is_umbrella: bool = False
    dedupe_key: Optional[str] = None


# ---------------------------------------------------------------------------
# Helper Inspection Functions
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


def get_planet_map(planets: list[dict]) -> dict[str, dict]:
    """Index planets by normalized name."""
    pmap = {}
    for p in planets:
        name = p.get("name") or p.get("planet")
        if name:
            pmap[name] = p
            pmap[name.capitalize()] = p
    return pmap


def house_of(pmap: dict, name: str) -> int:
    """Retrieve 1-indexed house number of a planet."""
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
    """Retrieve degree within sign."""
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


def is_retrograde(pmap: dict, name: str) -> bool:
    """Check if planet is retrograde."""
    return bool(pmap.get(name, {}).get("retrograde", False))


def house_dist(from_h: int, to_h: int) -> int:
    """Inclusive distance in houses from from_h to to_h (1-indexed)."""
    if not from_h or not to_h:
        return 0
    return ((to_h - from_h) % 12) + 1


def planets_in_house(pmap: dict, house_num: int) -> list[str]:
    """List classical planets occupying a house."""
    res = []
    for p in CLASSICAL_7:
        if house_of(pmap, p) == house_num:
            res.append(p)
    return res


def house_has_planet(pmap: dict, house_num: int, candidates: list[str]) -> bool:
    """Check if house contains any of the specified candidate planets."""
    for c in candidates:
        if house_of(pmap, c) == house_num:
            return True
    return False


def aspects_house(planet: str, planet_house: int, target_house: int) -> bool:
    """True if planet aspects target_house by Parashari full aspect."""
    if not planet_house or not target_house:
        return False
    dist = house_dist(planet_house, target_house)
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
    """Check if two planets mutually aspect each other."""
    h1 = house_of(pmap, p1)
    h2 = house_of(pmap, p2)
    if not h1 or not h2:
        return False
    return aspects_house(p1, h1, h2) and aspects_house(p2, h2, h1)


def is_in_own_sign(pmap: dict, planet: str) -> bool:
    s = sign_of(pmap, planet)
    return s in OWN_SIGNS.get(planet, [])


def is_exalted(pmap: dict, planet: str) -> bool:
    return sign_of(pmap, planet) == EXALTATION.get(planet)


def is_debilitated(pmap: dict, planet: str) -> bool:
    return sign_of(pmap, planet) == DEBILITATION.get(planet)


# ---------------------------------------------------------------------------
# Individual Yoga Rule Definitions (65+ rules)
# ---------------------------------------------------------------------------

CATALOG: list[YogaRule] = []

def _register(rule: YogaRule):
    CATALOG.append(rule)
    return rule


# ---------------------------------------------------------------------------
# 1. Pancha Mahapurusha Yogas (5 rules + 1 umbrella)
# ---------------------------------------------------------------------------

def _pred_ruchaka(pmap, lagna, houses):
    h = house_of(pmap, "Mars")
    s = sign_of(pmap, "Mars")
    present = h in KENDRA and (s in OWN_SIGNS.get("Mars", []) or s == EXALTATION.get("Mars"))
    strength = "Strong" if present and s == EXALTATION.get("Mars") else ("Medium" if present else "Absent")
    return present, strength, [f"Mars in {s} in H{h}"] if present else []

_register(YogaRule(
    rule_id="YOGA-PANCHA-RUCHAKA-01",
    dedupe_key="DEDUPE-PANCHA-MAHAPURUSHA",
    version="1.0.0",
    name="Ruchaka Yoga",
    category="Pancha Mahapurusha",
    description="Mars in Kendra in own or exaltation sign — courage, leadership, martial victory, and commanding executive authority.",
    source_reference="BPHS Ch. 75, v. 1-2; Phaladeepika Ch. 6, v. 1-4",
    predicate=_pred_ruchaka,
))


def _pred_bhadra(pmap, lagna, houses):
    h = house_of(pmap, "Mercury")
    s = sign_of(pmap, "Mercury")
    present = h in KENDRA and (s in OWN_SIGNS.get("Mercury", []) or s == EXALTATION.get("Mercury"))
    strength = "Strong" if present and s == EXALTATION.get("Mercury") else ("Medium" if present else "Absent")
    return present, strength, [f"Mercury in {s} in H{h}"] if present else []

_register(YogaRule(
    rule_id="YOGA-PANCHA-BHADRA-01",
    dedupe_key="DEDUPE-PANCHA-MAHAPURUSHA",
    version="1.0.0",
    name="Bhadra Yoga",
    category="Pancha Mahapurusha",
    description="Mercury in Kendra in own or exaltation sign — sharp intellect, commerce, exceptional eloquence, and mathematical erudition.",
    source_reference="BPHS Ch. 75, v. 3-4; Phaladeepika Ch. 6, v. 1-4",
    predicate=_pred_bhadra,
))


def _pred_hamsa(pmap, lagna, houses):
    h = house_of(pmap, "Jupiter")
    s = sign_of(pmap, "Jupiter")
    present = h in KENDRA and (s in OWN_SIGNS.get("Jupiter", []) or s == EXALTATION.get("Jupiter"))
    strength = "Strong" if present and s == EXALTATION.get("Jupiter") else ("Medium" if present else "Absent")
    return present, strength, [f"Jupiter in {s} in H{h}"] if present else []

_register(YogaRule(
    rule_id="YOGA-PANCHA-HAMSA-01",
    dedupe_key="DEDUPE-PANCHA-MAHAPURUSHA",
    version="1.0.0",
    name="Hamsa Yoga",
    category="Pancha Mahapurusha",
    description="Jupiter in Kendra in own or exaltation sign — supreme spiritual wisdom, righteous demeanor, scholarly grace, and kingly esteem.",
    source_reference="BPHS Ch. 75, v. 5-6; Phaladeepika Ch. 6, v. 1-4",
    predicate=_pred_hamsa,
))


def _pred_malavya(pmap, lagna, houses):
    h = house_of(pmap, "Venus")
    s = sign_of(pmap, "Venus")
    present = h in KENDRA and (s in OWN_SIGNS.get("Venus", []) or s == EXALTATION.get("Venus"))
    strength = "Strong" if present and s == EXALTATION.get("Venus") else ("Medium" if present else "Absent")
    return present, strength, [f"Venus in {s} in H{h}"] if present else []

_register(YogaRule(
    rule_id="YOGA-PANCHA-MALAVYA-01",
    dedupe_key="DEDUPE-PANCHA-MAHAPURUSHA",
    version="1.0.0",
    name="Malavya Yoga",
    category="Pancha Mahapurusha",
    description="Venus in Kendra in own or exaltation sign — opulent lifestyle, artistic mastery, vehicular comforts, and magnetic grace.",
    source_reference="BPHS Ch. 75, v. 7-8; Phaladeepika Ch. 6, v. 1-4",
    predicate=_pred_malavya,
))


def _pred_sasa(pmap, lagna, houses):
    h = house_of(pmap, "Saturn")
    s = sign_of(pmap, "Saturn")
    present = h in KENDRA and (s in OWN_SIGNS.get("Saturn", []) or s == EXALTATION.get("Saturn"))
    strength = "Strong" if present and s == EXALTATION.get("Saturn") else ("Medium" if present else "Absent")
    return present, strength, [f"Saturn in {s} in H{h}"] if present else []

_register(YogaRule(
    rule_id="YOGA-PANCHA-SASA-01",
    dedupe_key="DEDUPE-PANCHA-MAHAPURUSHA",
    version="1.0.0",
    name="Sasa Yoga",
    category="Pancha Mahapurusha",
    description="Saturn in Kendra in own or exaltation sign — unyielding perseverance, leadership over the masses, strategic endurance, and lasting authority.",
    source_reference="BPHS Ch. 75, v. 9-10; Phaladeepika Ch. 6, v. 1-4",
    predicate=_pred_sasa,
))


def _pred_mahapurusha_umbrella(pmap, lagna, houses):
    results = [_pred_ruchaka(pmap, lagna, houses), _pred_bhadra(pmap, lagna, houses),
               _pred_hamsa(pmap, lagna, houses), _pred_malavya(pmap, lagna, houses),
               _pred_sasa(pmap, lagna, houses)]
    active = [r for r in results if r[0]]
    present = len(active) > 0
    str_val = "Strong" if any(r[1] == "Strong" for r in active) else ("Medium" if present else "Absent")
    details = [d for r in active for d in r[2]]
    return present, str_val, details

_register(YogaRule(
    rule_id="YOGA-PANCHA-MAHAPURUSHA-01",
    is_umbrella=True,
    dedupe_key="DEDUPE-PANCHA-MAHAPURUSHA",
    version="1.0.0",
    name="Pancha Mahapurusha Yoga",
    category="Pancha Mahapurusha",
    description="Umbrella rule for the five great planetary configurations formed by non-luminary planets in Kendra in own/exaltation signs.",
    source_reference="BPHS Ch. 75; Brihat Jataka Ch. 13",
    predicate=_pred_mahapurusha_umbrella,
))


# ---------------------------------------------------------------------------
# 2. Solar Yogas (Ravi Yogas) (3 rules)
# ---------------------------------------------------------------------------

def _eligible_solar_planets(pmap, target_h):
    # Planets other than Moon, Rahu, Ketu in target house
    eligible = ["Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
    return [p for p in eligible if house_of(pmap, p) == target_h]


def _pred_vesi(pmap, lagna, houses):
    sun_h = house_of(pmap, "Sun")
    if not sun_h:
        return False, "Absent", []
    target_h = (sun_h % 12) + 1  # 2nd from Sun
    planets_found = _eligible_solar_planets(pmap, target_h)
    present = len(planets_found) > 0
    benefics = [p for p in planets_found if p in ("Jupiter", "Venus", "Mercury")]
    strength = "Strong" if benefics else ("Medium" if present else "Absent")
    return present, strength, [f"Planets in 2nd from Sun (H{target_h}): {', '.join(planets_found)}"] if present else []

_register(YogaRule(
    rule_id="YOGA-SOLAR-VESI-01",
    version="1.0.0",
    name="Vesi Yoga",
    category="Solar Yogas",
    description="Planet other than Moon/Rahu/Ketu in the 2nd house from Sun — steady speech, good reputation, and financial security.",
    source_reference="BPHS Ch. 36, v. 1-2; Brihat Jataka Ch. 13, v. 1",
    predicate=_pred_vesi,
))


def _pred_vosi(pmap, lagna, houses):
    sun_h = house_of(pmap, "Sun")
    if not sun_h:
        return False, "Absent", []
    target_h = ((sun_h - 2) % 12) + 1  # 12th from Sun
    planets_found = _eligible_solar_planets(pmap, target_h)
    present = len(planets_found) > 0
    benefics = [p for p in planets_found if p in ("Jupiter", "Venus", "Mercury")]
    strength = "Strong" if benefics else ("Medium" if present else "Absent")
    return present, strength, [f"Planets in 12th from Sun (H{target_h}): {', '.join(planets_found)}"] if present else []

_register(YogaRule(
    rule_id="YOGA-SOLAR-VOSI-01",
    version="1.0.0",
    name="Vosi Yoga",
    category="Solar Yogas",
    description="Planet other than Moon/Rahu/Ketu in the 12th house from Sun — sharp intellect, charitable disposition, and genuine renown.",
    source_reference="BPHS Ch. 36, v. 1-2; Brihat Jataka Ch. 13, v. 1",
    predicate=_pred_vosi,
))


def _pred_ubhaya(pmap, lagna, houses):
    p_vesi, _, det_vesi = _pred_vesi(pmap, lagna, houses)
    p_vosi, _, det_vosi = _pred_vosi(pmap, lagna, houses)
    present = p_vesi and p_vosi
    return present, "Strong" if present else "Absent", (det_vesi + det_vosi) if present else []

_register(YogaRule(
    rule_id="YOGA-SOLAR-UBHAYACHARI-01",
    version="1.0.0",
    name="Ubhayachari Yoga",
    category="Solar Yogas",
    description="Planets other than Moon/Rahu/Ketu in both the 2nd and 12th houses from Sun — majestic presence, widespread fame, and executive capability.",
    source_reference="BPHS Ch. 36, v. 3; Brihat Jataka Ch. 13, v. 2",
    predicate=_pred_ubhaya,
))


# ---------------------------------------------------------------------------
# 3. Lunar Yogas (Chandra Yogas) (4 rules)
# ---------------------------------------------------------------------------

def _eligible_lunar_planets(pmap, target_h):
    # Planets other than Sun, Rahu, Ketu in target house
    eligible = ["Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
    return [p for p in eligible if house_of(pmap, p) == target_h]


def _pred_sunapha(pmap, lagna, houses):
    moon_h = house_of(pmap, "Moon")
    if not moon_h:
        return False, "Absent", []
    target_h = (moon_h % 12) + 1  # 2nd from Moon
    planets_found = _eligible_lunar_planets(pmap, target_h)
    present = len(planets_found) > 0
    return present, "Medium" if present else "Absent", [f"Planets in 2nd from Moon (H{target_h}): {', '.join(planets_found)}"] if present else []

_register(YogaRule(
    rule_id="YOGA-LUNAR-SUNAPHA-01",
    version="1.0.0",
    name="Sunapha Yoga",
    category="Lunar Yogas",
    description="Planet other than Sun/Rahu/Ketu in the 2nd house from Moon — self-acquired wealth, high status, and comfortable possessions.",
    source_reference="BPHS Ch. 37, v. 1-2; Brihat Jataka Ch. 13, v. 3",
    predicate=_pred_sunapha,
))


def _pred_anapha(pmap, lagna, houses):
    moon_h = house_of(pmap, "Moon")
    if not moon_h:
        return False, "Absent", []
    target_h = ((moon_h - 2) % 12) + 1  # 12th from Moon
    planets_found = _eligible_lunar_planets(pmap, target_h)
    present = len(planets_found) > 0
    return present, "Medium" if present else "Absent", [f"Planets in 12th from Moon (H{target_h}): {', '.join(planets_found)}"] if present else []

_register(YogaRule(
    rule_id="YOGA-LUNAR-ANAPHA-01",
    version="1.0.0",
    name="Anapha Yoga",
    category="Lunar Yogas",
    description="Planet other than Sun/Rahu/Ketu in the 12th house from Moon — well-formed physique, noble conduct, generous nature, and peace of mind.",
    source_reference="BPHS Ch. 37, v. 3-4; Brihat Jataka Ch. 13, v. 3",
    predicate=_pred_anapha,
))


def _pred_dhurdhura(pmap, lagna, houses):
    p_su, _, det_su = _pred_sunapha(pmap, lagna, houses)
    p_an, _, det_an = _pred_anapha(pmap, lagna, houses)
    present = p_su and p_an
    return present, "Strong" if present else "Absent", (det_su + det_an) if present else []

_register(YogaRule(
    rule_id="YOGA-LUNAR-DHURDHURA-01",
    version="1.0.0",
    name="Durudhara Yoga",
    category="Lunar Yogas",
    description="Planets other than Sun/Rahu/Ketu in both 2nd and 12th houses from Moon — great generosity, abundant conveyance, and continuous prosperity.",
    source_reference="BPHS Ch. 37, v. 5-6; Brihat Jataka Ch. 13, v. 4",
    predicate=_pred_dhurdhura,
))


def _pred_kemadruma(pmap, lagna, houses):
    moon_h = house_of(pmap, "Moon")
    if not moon_h:
        return False, "Absent", []
    h2 = (moon_h % 12) + 1
    h12 = ((moon_h - 2) % 12) + 1
    planets_h2 = _eligible_lunar_planets(pmap, h2)
    planets_h12 = _eligible_lunar_planets(pmap, h12)
    # Kemadruma raw predicate: no planets in 2nd and 12th from Moon
    present = (len(planets_h2) == 0 and len(planets_h12) == 0)
    return present, "Medium" if present else "Absent", ["Moon isolated without planets in 2nd and 12th"] if present else []

def _cancel_kemadruma(pmap, lagna, houses):
    moon_h = house_of(pmap, "Moon")
    if not moon_h:
        return False, ""
    # Cancellation 1: Planet in Kendra from Moon
    for p in ["Mars", "Mercury", "Jupiter", "Venus", "Saturn"]:
        hp = house_of(pmap, p)
        if hp and house_dist(moon_h, hp) in {1, 4, 7, 10}:
            return True, f"Kemadruma Bhanga: {p} in Kendra from Moon (H{hp})"
    # Cancellation 2: Planet in Kendra from Lagna
    for p in ["Mars", "Mercury", "Jupiter", "Venus", "Saturn"]:
        hp = house_of(pmap, p)
        if hp in KENDRA:
            return True, f"Kemadruma Bhanga: {p} in Kendra from Lagna (H{hp})"
    # Cancellation 3: Moon conjunct another planet
    for p in ["Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Sun"]:
        if house_of(pmap, p) == moon_h:
            return True, f"Kemadruma Bhanga: Moon conjoined with {p}"
    return False, ""

_register(YogaRule(
    rule_id="YOGA-LUNAR-KEMADRUMA-01",
    version="1.0.0",
    name="Kemadruma Yoga",
    category="Lunar Yogas",
    description="No non-luminary planets in 2nd or 12th from Moon — inner isolation or financial fluctuation, subject to Kemadruma Bhanga cancellations.",
    source_reference="BPHS Ch. 37, v. 7-10",
    predicate=_pred_kemadruma,
    cancellation_rules=[_cancel_kemadruma],
))


# ---------------------------------------------------------------------------
# 4. Auspicious Chandra & Association Yogas (4 rules)
# ---------------------------------------------------------------------------

def _pred_gajakesari(pmap, lagna, houses):
    m_h = house_of(pmap, "Moon")
    j_h = house_of(pmap, "Jupiter")
    if not m_h or not j_h:
        return False, "Absent", []
    dist = house_dist(m_h, j_h)
    present = dist in {1, 4, 7, 10}
    j_s = sign_of(pmap, "Jupiter")
    is_strong = j_s in OWN_SIGNS.get("Jupiter", []) or j_s == EXALTATION.get("Jupiter")
    strength = "Strong" if present and is_strong else ("Medium" if present else "Absent")
    return present, strength, [f"Jupiter in H{j_h} ({dist}th from Moon H{m_h})"] if present else []

_register(YogaRule(
    rule_id="YOGA-CHANDRA-GAJAKESARI-01",
    version="1.0.0",
    name="Gajakesari Yoga",
    category="Chandra Yogas",
    description="Jupiter in Kendra (1/4/7/10) from Moon — supreme wisdom, lasting fame, unimpeachable integrity, and royal patronage.",
    source_reference="BPHS Ch. 38, v. 1-2; Phaladeepika Ch. 6, v. 16-17",
    predicate=_pred_gajakesari,
))


def _pred_chandra_mangala(pmap, lagna, houses):
    m_h = house_of(pmap, "Moon")
    ma_h = house_of(pmap, "Mars")
    if not m_h or not ma_h:
        return False, "Absent", []
    present = (m_h == ma_h) or (house_dist(m_h, ma_h) == 7)
    return present, "Medium" if present else "Absent", [f"Moon in H{m_h}, Mars in H{ma_h}"] if present else []

_register(YogaRule(
    rule_id="YOGA-CHANDRA-MANGALA-01",
    version="1.0.0",
    name="Chandra-Mangala Yoga",
    category="Chandra Yogas",
    description="Moon-Mars conjunction or mutual aspect — high commercial enterprise, resourcefulness, financial drive, and material acquisition.",
    source_reference="Phaladeepika Ch. 6, v. 57; Saravali Ch. 15",
    predicate=_pred_chandra_mangala,
))


def _pred_adhi(pmap, lagna, houses):
    m_h = house_of(pmap, "Moon")
    if not m_h:
        return False, "Absent", []
    target_houses = {((m_h + 4) % 12) + 1, ((m_h + 5) % 12) + 1, ((m_h + 6) % 12) + 1}
    benefics_found = []
    for b in ["Mercury", "Jupiter", "Venus"]:
        if house_of(pmap, b) in target_houses:
            benefics_found.append(b)
    present = len(benefics_found) > 0
    strength = "Strong" if len(benefics_found) == 3 else ("Medium" if len(benefics_found) == 2 else "Weak")
    return present, strength if present else "Absent", [f"Benefics {', '.join(benefics_found)} in 6/7/8 from Moon"] if present else []

_register(YogaRule(
    rule_id="YOGA-CHANDRA-ADHI-01",
    version="1.0.0",
    name="Adhi Yoga",
    category="Chandra Yogas",
    description="Benefics (Jupiter, Venus, Mercury) situated in 6th, 7th, or 8th from Moon — victorious over rivals, eminent position, and prosperity.",
    source_reference="BPHS Ch. 38, v. 3-4; Brihat Jataka Ch. 13, v. 5",
    predicate=_pred_adhi,
))


def _pred_lagnadhi(pmap, lagna, houses):
    target_houses = {6, 7, 8}
    benefics_found = []
    for b in ["Mercury", "Jupiter", "Venus"]:
        if house_of(pmap, b) in target_houses:
            benefics_found.append(b)
    present = len(benefics_found) > 0
    strength = "Strong" if len(benefics_found) == 3 else ("Medium" if len(benefics_found) == 2 else "Weak")
    return present, strength if present else "Absent", [f"Benefics {', '.join(benefics_found)} in 6/7/8 from Lagna"] if present else []

_register(YogaRule(
    rule_id="YOGA-LAGNADHI-01",
    version="1.0.0",
    name="Lagnadhi Yoga",
    category="Raja Yogas",
    description="Benefics occupying 6th, 7th, or 8th from Lagna — scholarly mastery, wealth, and aristocratic prominence.",
    source_reference="Phaladeepika Ch. 6, v. 18",
    predicate=_pred_lagnadhi,
))


# ---------------------------------------------------------------------------
# 5. Budha & Surya-related Yogas (1 rule)
# ---------------------------------------------------------------------------

def _pred_budhaditya(pmap, lagna, houses):
    s_h = house_of(pmap, "Sun")
    me_h = house_of(pmap, "Mercury")
    if not s_h or not me_h:
        return False, "Absent", []
    present = (s_h == me_h)
    strength = "Strong" if present and (s_h in KENDRA or s_h in TRIKONA) else ("Medium" if present else "Absent")
    return present, strength, [f"Sun and Mercury conjunct in H{s_h}"] if present else []

_register(YogaRule(
    rule_id="YOGA-BUDHADITYA-01",
    version="1.0.0",
    name="Budhaditya Yoga",
    category="Solar Yogas",
    description="Sun and Mercury conjoined — sharp analytical acumen, intellectual eloquence, and administrative distinction.",
    source_reference="Brihat Jataka Ch. 14, v. 1; Saravali Ch. 31",
    predicate=_pred_budhaditya,
))


# ---------------------------------------------------------------------------
# 6. Viparita Raja Yogas (3 distinct variants + 1 umbrella)
# ---------------------------------------------------------------------------

def _pred_harsha(pmap, lagna, houses):
    l6 = safe_house_lord(lagna, 6)
    h6 = house_of(pmap, l6)
    present = h6 in DUSTHANA
    return present, "Medium" if present else "Absent", [f"6th lord {l6} placed in dusthana H{h6}"] if present else []

_register(YogaRule(
    rule_id="YOGA-VIPARITA-HARSHA-01",
    dedupe_key="DEDUPE-VIPARITA-RAJA",
    version="1.0.0",
    name="Harsha Viparita Raja Yoga",
    category="Viparita Raja",
    description="6th lord situated in a dusthana (6/8/12) — destruction of enemies, immunity from legal strife, and triumph through adversity.",
    source_reference="Uttara Kalamrita Sloka 22; Phaladeepika Ch. 6, v. 63",
    predicate=_pred_harsha,
))


def _pred_sarala(pmap, lagna, houses):
    l8 = safe_house_lord(lagna, 8)
    h8 = house_of(pmap, l8)
    present = h8 in DUSTHANA
    return present, "Medium" if present else "Absent", [f"8th lord {l8} placed in dusthana H{h8}"] if present else []

_register(YogaRule(
    rule_id="YOGA-VIPARITA-SARALA-01",
    dedupe_key="DEDUPE-VIPARITA-RAJA",
    version="1.0.0",
    name="Sarala Viparita Raja Yoga",
    category="Viparita Raja",
    description="8th lord situated in a dusthana (6/8/12) — fearless longevity, unexpected windfalls, and resilience against sudden catastrophes.",
    source_reference="Uttara Kalamrita Sloka 22; Phaladeepika Ch. 6, v. 64",
    predicate=_pred_sarala,
))


def _pred_vimala(pmap, lagna, houses):
    l12 = safe_house_lord(lagna, 12)
    h12 = house_of(pmap, l12)
    present = h12 in DUSTHANA
    return present, "Medium" if present else "Absent", [f"12th lord {l12} placed in dusthana H{h12}"] if present else []

_register(YogaRule(
    rule_id="YOGA-VIPARITA-VIMALA-01",
    dedupe_key="DEDUPE-VIPARITA-RAJA",
    version="1.0.0",
    name="Vimala Viparita Raja Yoga",
    category="Viparita Raja",
    description="12th lord situated in a dusthana (6/8/12) — independent wealth, righteous expenditures, and preservation of honor.",
    source_reference="Uttara Kalamrita Sloka 22; Phaladeepika Ch. 6, v. 65",
    predicate=_pred_vimala,
))


def _pred_viparita_umbrella(pmap, lagna, houses):
    r_h = _pred_harsha(pmap, lagna, houses)
    r_s = _pred_sarala(pmap, lagna, houses)
    r_v = _pred_vimala(pmap, lagna, houses)
    present = r_h[0] or r_s[0] or r_v[0]
    details = r_h[2] + r_s[2] + r_v[2]
    return present, "Medium" if present else "Absent", details

_register(YogaRule(
    rule_id="YOGA-VIPARITA-UMBRELLA-01",
    is_umbrella=True,
    dedupe_key="DEDUPE-VIPARITA-RAJA",
    version="1.0.0",
    name="Viparita Raja Yoga",
    category="Viparita Raja",
    description="Lords of dusthana houses (6th, 8th, or 12th) situated in dusthanas — triumph over adversity and resilience after hardship.",
    source_reference="Uttara Kalamrita Sloka 22; Phaladeepika Ch. 6",
    predicate=_pred_viparita_umbrella,
))


# ---------------------------------------------------------------------------
# 7. Neecha Bhanga & Neecha Bhanga Raja Yoga (2 rules)
# ---------------------------------------------------------------------------

def _pred_neechabhanga(pmap, lagna, houses):
    cancelled_planets = []
    for p in CLASSICAL_7:
        s = sign_of(pmap, p)
        if s == DEBILITATION.get(p) and is_neech_bhanga(p, s, pmap):
            cancelled_planets.append(p)
    present = len(cancelled_planets) > 0
    return present, "Medium" if present else "Absent", [f"Debilitation cancelled for: {', '.join(cancelled_planets)}"] if present else []

_register(YogaRule(
    rule_id="YOGA-NEECHABHANGA-01",
    version="1.0.0",
    name="Neecha Bhanga",
    category="Cancellation",
    description="Planetary debilitation cancelled by retrograde motion, dispositor in Kendra, or exaltation lord in Kendra.",
    source_reference="BPHS Ch. 41; Phaladeepika Ch. 6, v. 26-30",
    predicate=_pred_neechabhanga,
))


def _pred_nbry(pmap, lagna, houses):
    cancelled_planets = []
    m_h = house_of(pmap, "Moon")
    for p in CLASSICAL_7:
        s = sign_of(pmap, p)
        if s == DEBILITATION.get(p) and is_neech_bhanga(p, s, pmap):
            ph = house_of(pmap, p)
            disp = SIGN_LORDS.get(s)
            dh = house_of(pmap, disp) if disp else 0
            # Qualifies for Raja Yoga if the planet or its dispositor is in Kendra from Lagna or Moon
            in_kendra_lagna = ph in KENDRA or dh in KENDRA
            in_kendra_moon = (m_h > 0 and (house_dist(m_h, ph) in {1, 4, 7, 10} or house_dist(m_h, dh) in {1, 4, 7, 10}))
            if in_kendra_lagna or in_kendra_moon:
                cancelled_planets.append(p)
    present = len(cancelled_planets) > 0
    return present, "Strong" if present else "Absent", [f"Neecha Bhanga Raja Yoga for {', '.join(cancelled_planets)}"] if present else []

_register(YogaRule(
    rule_id="YOGA-NEECHABHANGA-RAJA-01",
    version="1.0.0",
    name="Neecha Bhanga Raja Yoga",
    category="Raja Yogas",
    description="Debilitation cancelled with planet or dispositor in Kendra from Lagna or Moon — initial adversity transforms into high regal status.",
    source_reference="BPHS Ch. 41; Phaladeepika Ch. 6, v. 26-30",
    predicate=_pred_nbry,
))


# ---------------------------------------------------------------------------
# 8. Raja Yogas & Royal Association Yogas (12 rules)
# ---------------------------------------------------------------------------

def _pred_dharma_karmadhipati(pmap, lagna, houses):
    l9 = safe_house_lord(lagna, 9)
    l10 = safe_house_lord(lagna, 10)
    if not l9 or not l10 or l9 == l10:
        return False, "Absent", []
    h9 = house_of(pmap, l9)
    h10 = house_of(pmap, l10)
    if not h9 or not h10:
        return False, "Absent", []
    # Conjunction, mutual aspect, or Parivartana
    conj = (h9 == h10)
    aspect = mutual_aspect(l9, l10, pmap)
    s9 = sign_of(pmap, l9)
    s10 = sign_of(pmap, l10)
    exchange = (s9 in OWN_SIGNS.get(l10, []) and s10 in OWN_SIGNS.get(l9, []))
    present = conj or aspect or exchange
    return present, "Strong" if present else "Absent", [f"9th lord {l9} & 10th lord {l10} related (H{h9}/H{h10})"] if present else []

_register(YogaRule(
    rule_id="YOGA-RAJA-DHARMA-KARMADHIPATI-01",
    version="1.0.0",
    name="Dharma-Karmadhipati Yoga",
    category="Raja Yogas",
    description="9th and 10th lords conjoined, aspecting, or in mutual reception — peak career glory, dharmic honor, and sovereign eminence.",
    source_reference="BPHS Ch. 41, v. 37-38",
    predicate=_pred_dharma_karmadhipati,
))


def _pred_kendra_trikona(pmap, lagna, houses):
    # Conjunction of a Kendra lord and a Trikona lord (distinct planets, non-lagna)
    kendras = [4, 7, 10]
    trikonas = [5, 9]
    pairs = []
    for kh in kendras:
        kl = safe_house_lord(lagna, kh)
        for th in trikonas:
            tl = safe_house_lord(lagna, th)
            if kl and tl and kl != tl:
                h_k = house_of(pmap, kl)
                h_t = house_of(pmap, tl)
                if h_k and h_t and (h_k == h_t or mutual_aspect(kl, tl, pmap)):
                    pairs.append(f"{kl}(H{kh})-{tl}(H{th})")
    present = len(pairs) > 0
    return present, "Strong" if present else "Absent", pairs if present else []

_register(YogaRule(
    rule_id="YOGA-RAJA-KENDRA-TRIKONA-01",
    version="1.0.0",
    name="Kendra-Trikona Raja Yoga",
    category="Raja Yogas",
    description="Lords of Kendra and Trikona in conjunction or mutual aspect — high administrative authority, prosperity, and honorable rise.",
    source_reference="BPHS Ch. 41, v. 28-32",
    predicate=_pred_kendra_trikona,
))


def _pred_raja_sambandha(pmap, lagna, houses):
    l1 = safe_house_lord(lagna, 1)
    l10 = safe_house_lord(lagna, 10)
    if not l1 or not l10:
        return False, "Absent", []
    h1 = house_of(pmap, l1)
    h10 = house_of(pmap, l10)
    present = (h1 == 10) or (h1 == h10 and h1 in KENDRA.union(TRIKONA)) or mutual_aspect(l1, l10, pmap)
    return present, "Strong" if present else "Absent", [f"Lagna lord {l1} and 10th lord {l10} associated"] if present else []

_register(YogaRule(
    rule_id="YOGA-RAJA-SAMBANDHA-01",
    version="1.0.0",
    name="Raja Sambandha Yoga",
    category="Raja Yogas",
    description="Lagna lord and 10th lord closely associated in Kendra/Trikona — close ties to governing powers, high public standing.",
    source_reference="BPHS Ch. 41; Phaladeepika Ch. 6, v. 45",
    predicate=_pred_raja_sambandha,
))


def _pred_lakshmi(pmap, lagna, houses):
    l9 = safe_house_lord(lagna, 9)
    l1 = safe_house_lord(lagna, 1)
    if not l9 or not l1:
        return False, "Absent", []
    h9 = house_of(pmap, l9)
    s9 = sign_of(pmap, l9)
    h1 = house_of(pmap, l1)
    # 9th lord in Kendra/Trikona in own or exaltation sign, Lagna lord not in dusthana
    cond1 = (h9 in KENDRA.union(TRIKONA)) and (s9 in OWN_SIGNS.get(l9, []) or s9 == EXALTATION.get(l9))
    cond2 = h1 not in DUSTHANA and h1 != 0
    present = cond1 and cond2
    return present, "Strong" if present else "Absent", [f"9th lord {l9} exalted/own in H{h9}"] if present else []

_register(YogaRule(
    rule_id="YOGA-RAJA-LAKSHMI-01",
    version="1.0.0",
    name="Lakshmi Yoga",
    category="Raja Yogas",
    description="9th lord in Kendra/Trikona in own or exaltation sign while Lagna lord is strong — supreme wealth, nobility, and fortune.",
    source_reference="Phaladeepika Ch. 6, v. 20",
    predicate=_pred_lakshmi,
))


def _pred_saraswati(pmap, lagna, houses):
    hj = house_of(pmap, "Jupiter")
    hv = house_of(pmap, "Venus")
    hm = house_of(pmap, "Mercury")
    sj = sign_of(pmap, "Jupiter")
    eligible_houses = KENDRA.union(TRIKONA).union({2})
    cond1 = (hj in eligible_houses) and (hv in eligible_houses) and (hm in eligible_houses)
    cond2 = (sj != DEBILITATION.get("Jupiter"))
    present = cond1 and cond2
    return present, "Strong" if present else "Absent", ["Jupiter, Venus, and Mercury in Kendra/Trikona/2nd"] if present else []

_register(YogaRule(
    rule_id="YOGA-RAJA-SARASWATI-01",
    version="1.0.0",
    name="Saraswati Yoga",
    category="Raja Yogas",
    description="Jupiter, Venus, and Mercury in Kendra, Trikona, or 2nd house while Jupiter is strong — literary genius, eloquence, and intellectual mastery.",
    source_reference="Phaladeepika Ch. 6, v. 24-25",
    predicate=_pred_saraswati,
))


def _pred_gauri(pmap, lagna, houses):
    ms = sign_of(pmap, "Moon")
    if not ms:
        return False, "Absent", []
    disp = SIGN_LORDS.get(ms)
    if not disp:
        return False, "Absent", []
    dh = house_of(pmap, disp)
    ds = sign_of(pmap, disp)
    if not dh or not ds:
        return False, "Absent", []
    jh = house_of(pmap, "Jupiter")
    if not jh:
        return False, "Absent", []

    # 1. Candrarkṣapa (Moon's sign dispositor) in Kendra or Trikona
    in_k_t = dh in KENDRA.union(TRIKONA)

    # 2. Svoccagata: in own sign or exaltation sign
    is_own = ds in OWN_SIGNS.get(disp, [])
    is_exalt = ds == EXALTATION.get(disp)
    own_exalt = is_own or is_exalt

    # 3. Abhilakṣite jīvena: aspected by Jupiter
    asp_jup = aspects_house("Jupiter", jh, dh)

    # All three classical conditions concurrent per Phaladeepika Ch. 6, v. 21
    present = in_k_t and own_exalt and asp_jup

    strength = "Strong" if (present and is_exalt) else ("Medium" if present else "Absent")
    details = [
        f"Moon in {ms} (dispositor {disp} in {ds} in H{dh}, aspected by Jupiter from H{jh})"
    ] if present else []

    return present, strength, details

_register(YogaRule(
    rule_id="YOGA-RAJA-GAURI-01",
    version="1.0.0",
    name="Gauri Yoga",
    category="Raja Yogas",
    description="Lord of the sign occupied by Moon (candrarkṣapa) in Kendra or Trikona in own or exaltation sign aspected by Jupiter — radiant grace, pure character, and prosperity.",
    source_reference="Phaladeepika Ch. 6, v. 21",
    predicate=_pred_gauri,
))


def _pred_parvata(pmap, lagna, houses):
    l1 = SIGN_LORDS.get(lagna)
    if not l1:
        return False, "Absent", []
    s1 = sign_of(pmap, l1)
    if not s1:
        return False, "Absent", []
    d1 = SIGN_LORDS.get(s1)
    if not d1:
        return False, "Absent", []
    dh = house_of(pmap, d1)
    ds = sign_of(pmap, d1)
    if not dh or not ds:
        return False, "Absent", []

    # 1. D1 in Kendra or Trikona
    in_k_t = dh in KENDRA.union(TRIKONA)

    # 2. D1 in own sign or exaltation sign
    is_own = ds in OWN_SIGNS.get(d1, [])
    is_exalt = ds == EXALTATION.get(d1)
    own_exalt = is_own or is_exalt

    present = in_k_t and own_exalt

    strength = "Strong" if (present and is_exalt) else ("Medium" if present else "Absent")
    details = [
        f"Lagna lord {l1} in {s1}, dispositor {d1} in {ds} in H{dh}"
    ] if present else []

    return present, strength, details

_register(YogaRule(
    rule_id="YOGA-RAJA-PARVATA-01",
    version="1.0.0",
    name="Parvata Yoga",
    category="Raja Yogas",
    description="Dispositor of the Lagna lord (lagnādhipāpta-bha-pati) in Kendra or Trikona in own or exaltation sign — steadfast fortune, durable authority, and noble character.",
    source_reference="Phaladeepika Ch. 6, v. 35",
    predicate=_pred_parvata,
))


def _pred_kahala(pmap, lagna, houses):
    l4 = safe_house_lord(lagna, 4)
    l9 = safe_house_lord(lagna, 9)
    l1 = safe_house_lord(lagna, 1)
    if not l4 or not l9 or not l1:
        return False, "Absent", []
    h4 = house_of(pmap, l4)
    h9 = house_of(pmap, l9)
    h1 = house_of(pmap, l1)
    # 4th and 9th lords in mutual kendra, lagna lord strong
    dist = house_dist(h4, h9)
    present = dist in {1, 4, 7, 10} and h1 not in DUSTHANA and h1 != 0
    return present, "Medium" if present else "Absent", [f"4th lord {l4} and 9th lord {l9} in mutual kendra"] if present else []

_register(YogaRule(
    rule_id="YOGA-RAJA-KAHALA-01",
    version="1.0.0",
    name="Kahala Yoga",
    category="Raja Yogas",
    description="4th lord and 9th lord in mutual Kendra from each other while Lagna lord is strong — courageous character, energetic enterprise.",
    source_reference="Phaladeepika Ch. 6, v. 36",
    predicate=_pred_kahala,
))


def _pred_chamara(pmap, lagna, houses):
    l1 = safe_house_lord(lagna, 1)
    h1 = house_of(pmap, l1)
    s1 = sign_of(pmap, l1)
    jh = house_of(pmap, "Jupiter")
    # Lagna lord exalted in Kendra aspected by Jupiter, or two benefics in 1/7/9/10
    cond1 = (h1 in KENDRA) and (s1 == EXALTATION.get(l1)) and aspects_house("Jupiter", jh, h1)
    benefics_in_good = [b for b in ("Jupiter", "Venus", "Mercury") if house_of(pmap, b) in {1, 7, 9, 10}]
    cond2 = len(benefics_in_good) >= 2
    present = cond1 or cond2
    return present, "Strong" if present else "Absent", ["Benefics in 1/7/9/10 or Lagna lord exalted in Kendra"] if present else []

_register(YogaRule(
    rule_id="YOGA-RAJA-CHAMARA-01",
    version="1.0.0",
    name="Chamara Yoga",
    category="Raja Yogas",
    description="Lagna lord exalted in Kendra aspected by Jupiter, or benefics prominent in 1st/7th/9th/10th — royal insignia, scholarly authority.",
    source_reference="Phaladeepika Ch. 6, v. 44",
    predicate=_pred_chamara,
))


def _pred_sankha(pmap, lagna, houses):
    l5 = safe_house_lord(lagna, 5)
    l6 = safe_house_lord(lagna, 6)
    l1 = safe_house_lord(lagna, 1)
    if not l5 or not l6 or not l1:
        return False, "Absent", []
    h5 = house_of(pmap, l5)
    h6 = house_of(pmap, l6)
    h1 = house_of(pmap, l1)
    # Lagna lord strong in Kendra/Trikona, 5th and 6th lords in mutual Kendra
    dist = house_dist(h5, h6)
    present = (h1 in KENDRA.union(TRIKONA)) and (dist in {1, 4, 7, 10})
    return present, "Medium" if present else "Absent", [f"5th lord {l5} & 6th lord {l6} in mutual Kendra"] if present else []

_register(YogaRule(
    rule_id="YOGA-RAJA-SANKHA-01",
    version="1.0.0",
    name="Sankha Yoga",
    category="Raja Yogas",
    description="Lagna lord strong and 5th and 6th lords in mutual Kendra — profound knowledge, humanitarian generosity, and long life.",
    source_reference="Phaladeepika Ch. 6, v. 37",
    predicate=_pred_sankha,
))


def _pred_bheri(pmap, lagna, houses):
    l9 = safe_house_lord(lagna, 9)
    l1 = safe_house_lord(lagna, 1)
    if not l9 or not l1:
        return False, "Absent", []
    h9 = house_of(pmap, l9)
    s9 = sign_of(pmap, l9)
    # 9th lord strong, Jupiter, Venus, Lagna lord in Kendra
    j_h = house_of(pmap, "Jupiter")
    v_h = house_of(pmap, "Venus")
    l1_h = house_of(pmap, l1)
    cond1 = (s9 in OWN_SIGNS.get(l9, []) or s9 == EXALTATION.get(l9) or h9 in KENDRA.union(TRIKONA))
    cond2 = (j_h in KENDRA) and (v_h in KENDRA) and (l1_h in KENDRA)
    present = cond1 and cond2
    return present, "Strong" if present else "Absent", ["Jupiter, Venus, and Lagna lord in Kendra with strong 9th lord"] if present else []

_register(YogaRule(
    rule_id="YOGA-RAJA-BHERI-01",
    version="1.0.0",
    name="Bheri Yoga",
    category="Raja Yogas",
    description="9th lord strong and Jupiter, Venus, Lagna lord in Kendra — lasting fame, robust health, and command over material fortunes.",
    source_reference="Phaladeepika Ch. 6, v. 39",
    predicate=_pred_bheri,
))


def _pred_amala(pmap, lagna, houses):
    # Benefic in 10th from Lagna or Moon
    m_h = house_of(pmap, "Moon")
    t_lagna = 10
    t_moon = ((m_h + 8) % 12) + 1 if m_h else 0
    found = []
    for b in ("Jupiter", "Venus", "Mercury"):
        bh = house_of(pmap, b)
        if bh == t_lagna or (t_moon and bh == t_moon):
            found.append(b)
    present = len(found) > 0
    return present, "Strong" if present else "Absent", [f"Natural benefic {', '.join(found)} in 10th house"] if present else []

_register(YogaRule(
    rule_id="YOGA-RAJA-AMALA-01",
    version="1.0.0",
    name="Amala Yoga",
    category="Raja Yogas",
    description="Natural benefic (Jupiter, Venus, Mercury) in the 10th house from Lagna or Moon — spotless reputation, virtuous achievements.",
    source_reference="Phaladeepika Ch. 6, v. 19",
    predicate=_pred_amala,
))


# ---------------------------------------------------------------------------
# 9. Dhana Yogas (Wealth Combinations) (6 rules)
# ---------------------------------------------------------------------------

def _pred_dhana_2_11(pmap, lagna, houses):
    l2 = safe_house_lord(lagna, 2)
    l11 = safe_house_lord(lagna, 11)
    if not l2 or not l11:
        return False, "Absent", []
    h2 = house_of(pmap, l2)
    h11 = house_of(pmap, l11)
    if not h2 or not h11:
        return False, "Absent", []
    present = (h2 == h11) or mutual_aspect(l2, l11, pmap)
    return present, "Medium" if present else "Absent", [f"2nd lord {l2} & 11th lord {l11} associated (H{h2}/H{h11})"] if present else []

_register(YogaRule(
    rule_id="YOGA-DHANA-2-11-01",
    dedupe_key="DEDUPE-DHANA-YOGA",
    version="1.0.0",
    name="Dhana Yoga (2nd & 11th Lords)",
    category="Dhana Yogas",
    description="Association of 2nd lord (accumulated wealth) and 11th lord (gains) — substantial wealth accumulation and financial prospering.",
    source_reference="BPHS Ch. 43, v. 1-5",
    predicate=_pred_dhana_2_11,
))


def _pred_dhana_1_2(pmap, lagna, houses):
    l1 = safe_house_lord(lagna, 1)
    l2 = safe_house_lord(lagna, 2)
    if not l1 or not l2 or l1 == l2:
        return False, "Absent", []
    h1 = house_of(pmap, l1)
    h2 = house_of(pmap, l2)
    present = (h1 == h2 and h1 in KENDRA.union(TRIKONA)) or (mutual_aspect(l1, l2, pmap) and h1 in KENDRA.union(TRIKONA))
    return present, "Medium" if present else "Absent", [f"Lagna lord {l1} and 2nd lord {l2} conjunct in Kendra/Trikona"] if present else []

_register(YogaRule(
    rule_id="YOGA-DHANA-1-2-01",
    dedupe_key="DEDUPE-DHANA-YOGA",
    version="1.0.0",
    name="Dhana Yoga (1st & 2nd Lords)",
    category="Dhana Yogas",
    description="Lagna lord and 2nd lord conjoined in Kendra or Trikona — self-earned fortune and continuous financial stability.",
    source_reference="BPHS Ch. 43, v. 6-10",
    predicate=_pred_dhana_1_2,
))


def _pred_dhana_5_9(pmap, lagna, houses):
    l5 = safe_house_lord(lagna, 5)
    l9 = safe_house_lord(lagna, 9)
    if not l5 or not l9 or l5 == l9:
        return False, "Absent", []
    h5 = house_of(pmap, l5)
    h9 = house_of(pmap, l9)
    present = (h5 == h9 and h5 != 0) or mutual_aspect(l5, l9, pmap)
    return present, "Strong" if present else "Absent", [f"5th lord {l5} & 9th lord {l9} associated (H{h5}/H{h9})"] if present else []

_register(YogaRule(
    rule_id="YOGA-DHANA-5-9-01",
    dedupe_key="DEDUPE-DHANA-YOGA",
    version="1.0.0",
    name="Dhana Yoga (5th & 9th Lords)",
    category="Dhana Yogas",
    description="Association of the two Lakshmi Trikona lords (5th and 9th) — sublime divine grace, intellectual wealth, and effortless prosperity.",
    source_reference="BPHS Ch. 43, v. 11-15",
    predicate=_pred_dhana_5_9,
))


def _pred_dhana_2_5(pmap, lagna, houses):
    l2 = safe_house_lord(lagna, 2)
    l5 = safe_house_lord(lagna, 5)
    if not l2 or not l5 or l2 == l5:
        return False, "Absent", []
    h2 = house_of(pmap, l2)
    h5 = house_of(pmap, l5)
    present = (h2 == h5 and h2 != 0) or mutual_aspect(l2, l5, pmap)
    return present, "Medium" if present else "Absent", [f"2nd lord {l2} & 5th lord {l5} associated"] if present else []

_register(YogaRule(
    rule_id="YOGA-DHANA-2-5-01",
    dedupe_key="DEDUPE-DHANA-YOGA",
    version="1.0.0",
    name="Dhana Yoga (2nd & 5th Lords)",
    category="Dhana Yogas",
    description="2nd lord and 5th lord associated — financial rewards through speculative intellect, advisory skills, and accumulated savings.",
    source_reference="BPHS Ch. 43",
    predicate=_pred_dhana_2_5,
))


def _pred_vasumati(pmap, lagna, houses):
    # Benefics in Upachaya houses (3, 6, 10, 11) from Lagna or Moon
    m_h = house_of(pmap, "Moon")
    upachaya_lagna = {3, 6, 10, 11}
    upachaya_moon = {((m_h + off - 1) % 12) + 1 for off in [3, 6, 10, 11]} if m_h else set()
    found = []
    for b in ("Jupiter", "Venus", "Mercury"):
        bh = house_of(pmap, b)
        if bh in upachaya_lagna or bh in upachaya_moon:
            found.append(b)
    present = len(found) >= 2
    strength = "Strong" if len(found) == 3 else ("Medium" if present else "Absent")
    return present, strength, [f"Benefics {', '.join(found)} in Upachaya houses"] if present else []

_register(YogaRule(
    rule_id="YOGA-DHANA-VASUMATI-01",
    version="1.0.0",
    name="Vasumati Yoga",
    category="Dhana Yogas",
    description="Benefics situated in Upachaya houses (3, 6, 10, 11) from Lagna or Moon — commanding independent wealth and perpetual abundance.",
    source_reference="Phaladeepika Ch. 6, v. 23",
    predicate=_pred_vasumati,
))


def _pred_pushkala(pmap, lagna, houses):
    l1 = safe_house_lord(lagna, 1)
    ms = sign_of(pmap, "Moon")
    lm = SIGN_LORDS.get(ms)
    if not l1 or not lm:
        return False, "Absent", []
    h1 = house_of(pmap, l1)
    hm = house_of(pmap, lm)
    # Lagna lord and Moon dispositor in Kendra or friendly sign, Lagna contains or aspected by benefic
    cond1 = (h1 in KENDRA or hm in KENDRA)
    benefics_in_lagna = any(house_of(pmap, b) == 1 for b in ("Jupiter", "Venus", "Mercury"))
    present = cond1 and (benefics_in_lagna or h1 == 1)
    return present, "Medium" if present else "Absent", [f"Lagna lord {l1} in H{h1}, Moon lord {lm} in H{hm}"] if present else []

_register(YogaRule(
    rule_id="YOGA-DHANA-PUSHKALA-01",
    version="1.0.0",
    name="Pushkala Yoga",
    category="Dhana Yogas",
    description="Lagna lord and Moon lord well placed in Kendra with benefic influence on Lagna — sweet-spoken, famous, wealthy and honored by kings.",
    source_reference="Phaladeepika Ch. 6, v. 22",
    predicate=_pred_pushkala,
))


def _pred_dhana_umbrella(pmap, lagna, houses):
    r1 = _pred_dhana_2_11(pmap, lagna, houses)
    r2 = _pred_dhana_1_2(pmap, lagna, houses)
    r3 = _pred_dhana_5_9(pmap, lagna, houses)
    r4 = _pred_dhana_2_5(pmap, lagna, houses)
    present = r1[0] or r2[0] or r3[0] or r4[0]
    details = r1[2] + r2[2] + r3[2] + r4[2]
    return present, "Medium" if present else "Absent", details

_register(YogaRule(
    rule_id="YOGA-DHANA-UMBRELLA-01",
    is_umbrella=True,
    dedupe_key="DEDUPE-DHANA-YOGA",
    version="1.0.0",
    name="Dhana Yoga",
    category="Dhana Yogas",
    description="Umbrella wealth combination formed by mutual associations of wealth lords (2nd, 5th, 9th, 11th).",
    source_reference="BPHS Ch. 43",
    predicate=_pred_dhana_umbrella,
))


# ---------------------------------------------------------------------------
# 10. Special Conjunctions & Character Yogas (5 rules)
# ---------------------------------------------------------------------------

def _pred_guru_mangala(pmap, lagna, houses):
    jh = house_of(pmap, "Jupiter")
    mah = house_of(pmap, "Mars")
    if not jh or not mah:
        return False, "Absent", []
    present = (jh == mah) or mutual_aspect("Jupiter", "Mars", pmap)
    return present, "Medium" if present else "Absent", [f"Jupiter in H{jh}, Mars in H{mah}"] if present else []

_register(YogaRule(
    rule_id="YOGA-GURU-MANGALA-01",
    version="1.0.0",
    name="Guru-Mangala Yoga",
    category="Benefic Conjunctions",
    description="Jupiter and Mars conjoined or in mutual aspect — righteousness coupled with valor, administrative capability, and success.",
    source_reference="Saravali Ch. 15, v. 15",
    predicate=_pred_guru_mangala,
))


def _pred_kalanidhi(pmap, lagna, houses):
    jh = house_of(pmap, "Jupiter")
    if jh not in {2, 5}:
        return False, "Absent", []
    meh = house_of(pmap, "Mercury")
    vh = house_of(pmap, "Venus")
    # Jupiter in 2nd or 5th conjunct/aspected by Mercury or Venus, or in their signs
    js = sign_of(pmap, "Jupiter")
    in_sign = js in ("Mithuna", "Kanya", "Vrishabha", "Tula")
    conj_asp = (meh == jh or vh == jh) or aspects_house("Mercury", meh, jh) or aspects_house("Venus", vh, jh)
    present = in_sign or conj_asp
    return present, "Strong" if present else "Absent", [f"Jupiter in H{jh} with Mercury/Venus influence"] if present else []

_register(YogaRule(
    rule_id="YOGA-KALANIDHI-01",
    version="1.0.0",
    name="Kalanidhi Yoga",
    category="Benefic Conjunctions",
    description="Jupiter in 2nd or 5th house associated with Mercury and Venus — mastery of arts and sciences, virtuous living, and reverence.",
    source_reference="Phaladeepika Ch. 6, v. 32",
    predicate=_pred_kalanidhi,
))


def _pred_bhaskara(pmap, lagna, houses):
    sh = house_of(pmap, "Sun")
    mh = house_of(pmap, "Moon")
    meh = house_of(pmap, "Mercury")
    jh = house_of(pmap, "Jupiter")
    if not (sh and mh and meh and jh):
        return False, "Absent", []
    # Moon in 2nd from Sun, Mercury in 3rd from Moon, Jupiter in 5th or 9th from Mercury
    c1 = (house_dist(sh, mh) == 2)
    c2 = (house_dist(mh, meh) == 3)
    c3 = (house_dist(meh, jh) in {5, 9})
    present = c1 and c2 and c3
    return present, "Strong" if present else "Absent", ["Sun, Moon, Mercury, Jupiter in Bhaskara configuration"] if present else []

_register(YogaRule(
    rule_id="YOGA-BHASKARA-01",
    version="1.0.0",
    name="Bhaskara Yoga",
    category="Benefic Conjunctions",
    description="Moon 2nd from Sun, Mercury 3rd from Moon, Jupiter in trine from Mercury — valorous, scholarly, musical, and wealthy.",
    source_reference="Phaladeepika Ch. 6, v. 33",
    predicate=_pred_bhaskara,
))


def _pred_mriganka(pmap, lagna, houses):
    mh = house_of(pmap, "Moon")
    jh = house_of(pmap, "Jupiter")
    mah = house_of(pmap, "Mars")
    if not (mh and jh and mah):
        return False, "Absent", []
    # Jupiter in Kendra from Moon, Mars in Kendra from Jupiter
    c1 = (house_dist(mh, jh) in {1, 4, 7, 10})
    c2 = (house_dist(jh, mah) in {1, 4, 7, 10})
    present = c1 and c2
    return present, "Medium" if present else "Absent", [f"Jupiter kendra from Moon, Mars kendra from Jupiter"] if present else []

_register(YogaRule(
    rule_id="YOGA-MRIGANKA-01",
    version="1.0.0",
    name="Mriganka Yoga",
    category="Benefic Conjunctions",
    description="Jupiter in Kendra from Moon and Mars in Kendra from Jupiter — courageous, authoritative, and physically robust.",
    source_reference="Phaladeepika Ch. 6",
    predicate=_pred_mriganka,
))


def _pred_shubha(pmap, lagna, houses):
    # Benefics in Lagna and 9th house
    b_lagna = any(house_of(pmap, b) == 1 for b in ("Jupiter", "Venus", "Mercury"))
    b_9 = any(house_of(pmap, b) == 9 for b in ("Jupiter", "Venus", "Mercury"))
    present = b_lagna and b_9
    return present, "Medium" if present else "Absent", ["Benefics occupying both Lagna and 9th house"] if present else []

_register(YogaRule(
    rule_id="YOGA-SHUBHA-01",
    version="1.0.0",
    name="Shubha Yoga",
    category="Benefic Conjunctions",
    description="Natural benefics in Lagna and 9th house — pure demeanor, righteous actions, and blessed life journey.",
    source_reference="Phaladeepika Ch. 6, v. 40",
    predicate=_pred_shubha,
))


# ---------------------------------------------------------------------------
# 11. Parivartana Yogas (Mutual House Exchanges) (3 rules)
# ---------------------------------------------------------------------------

def _find_exchanges(pmap, lagna):
    exchanges = []
    lagna_idx = SIGNS_SK.index(lagna) if lagna in SIGNS_SK else 0
    for h1 in range(1, 13):
        for h2 in range(h1 + 1, 13):
            l1 = safe_house_lord(lagna, h1)
            l2 = safe_house_lord(lagna, h2)
            if l1 and l2 and l1 != l2:
                s1 = sign_of(pmap, l1)
                s2 = sign_of(pmap, l2)
                # Does l1 occupy l2's sign and l2 occupy l1's sign?
                sign_h1 = SIGNS_SK[(lagna_idx + h1 - 1) % 12]
                sign_h2 = SIGNS_SK[(lagna_idx + h2 - 1) % 12]
                if s1 == sign_h2 and s2 == sign_h1:
                    exchanges.append((h1, h2, l1, l2))
    return exchanges


def _pred_maha_parivartana(pmap, lagna, houses):
    auspicious = {1, 2, 4, 5, 7, 9, 10, 11}
    exchanges = _find_exchanges(pmap, lagna)
    maha = [e for e in exchanges if e[0] in auspicious and e[1] in auspicious]
    present = len(maha) > 0
    details = [f"Mutual exchange between H{e[0]} ({e[2]}) and H{e[1]} ({e[3]})" for e in maha]
    return present, "Strong" if present else "Absent", details if present else []

_register(YogaRule(
    rule_id="YOGA-PARIVARTANA-MAHA-01",
    version="1.0.0",
    name="Maha Parivartana Yoga",
    category="Parivartana",
    description="Mutual sign exchange between lords of Kendra, Trikona, or Dhana houses — supreme fortune, high status, and enduring wealth.",
    source_reference="Phaladeepika Ch. 6, v. 32-34",
    predicate=_pred_maha_parivartana,
))


def _pred_dainya_parivartana(pmap, lagna, houses):
    exchanges = _find_exchanges(pmap, lagna)
    dainya = [e for e in exchanges if e[0] in DUSTHANA or e[1] in DUSTHANA]
    present = len(dainya) > 0
    details = [f"Dusthana exchange between H{e[0]} ({e[2]}) and H{e[1]} ({e[3]})" for e in dainya]
    return present, "Medium" if present else "Absent", details if present else []

_register(YogaRule(
    rule_id="YOGA-PARIVARTANA-DAINYA-01",
    version="1.0.0",
    name="Dainya Parivartana Yoga",
    category="Parivartana",
    description="Mutual sign exchange involving a dusthana lord (6th, 8th, or 12th) — periods of struggle, mixed fortune, and karmic lessons.",
    source_reference="Phaladeepika Ch. 6, v. 32-34",
    predicate=_pred_dainya_parivartana,
))


def _pred_khala_parivartana(pmap, lagna, houses):
    exchanges = _find_exchanges(pmap, lagna)
    khala = [e for e in exchanges if (e[0] == 3 or e[1] == 3) and (e[0] not in DUSTHANA and e[1] not in DUSTHANA)]
    present = len(khala) > 0
    details = [f"3rd house exchange between H{e[0]} ({e[2]}) and H{e[1]} ({e[3]})" for e in khala]
    return present, "Medium" if present else "Absent", details if present else []

_register(YogaRule(
    rule_id="YOGA-PARIVARTANA-KHALA-01",
    version="1.0.0",
    name="Khala Parivartana Yoga",
    category="Parivartana",
    description="Mutual sign exchange involving the 3rd house lord — fluctuating fortunes, adventurous courage, and intermittent success.",
    source_reference="Phaladeepika Ch. 6, v. 32-34",
    predicate=_pred_khala_parivartana,
))


# ---------------------------------------------------------------------------
# 12. Kartari Yogas (Flanking Yogas) (2 rules)
# ---------------------------------------------------------------------------

def _pred_shubha_kartari(pmap, lagna, houses):
    # Lagna flanked by benefics in 2nd and 12th
    h2_benefics = [b for b in ("Jupiter", "Venus", "Mercury") if house_of(pmap, b) == 2]
    h12_benefics = [b for b in ("Jupiter", "Venus", "Mercury") if house_of(pmap, b) == 12]
    present = len(h2_benefics) > 0 and len(h12_benefics) > 0
    return present, "Medium" if present else "Absent", ["Lagna flanked by benefics in 2nd and 12th"] if present else []

_register(YogaRule(
    rule_id="YOGA-KARTARI-SHUBHA-01",
    version="1.0.0",
    name="Shubha Kartari Yoga",
    category="Kartari Yogas",
    description="Lagna flanked by natural benefics in 2nd and 12th houses — divine protection, physical vitality, and effortless happiness.",
    source_reference="BPHS Ch. 12; Phaladeepika Ch. 6, v. 11",
    predicate=_pred_shubha_kartari,
))


def _pred_papa_kartari(pmap, lagna, houses):
    # Lagna flanked by malefics in 2nd and 12th
    h2_malefics = [m for m in ("Sun", "Mars", "Saturn", "Rahu", "Ketu") if house_of(pmap, m) == 2]
    h12_malefics = [m for m in ("Sun", "Mars", "Saturn", "Rahu", "Ketu") if house_of(pmap, m) == 12]
    present = len(h2_malefics) > 0 and len(h12_malefics) > 0
    return present, "Medium" if present else "Absent", ["Lagna hemmed by malefics in 2nd and 12th"] if present else []

_register(YogaRule(
    rule_id="YOGA-KARTARI-PAPA-01",
    version="1.0.0",
    name="Papa Kartari Yoga",
    category="Kartari Yogas",
    description="Lagna hemmed between natural malefics in 2nd and 12th houses — feelings of constraint, mental pressure, and health vulnerabilities.",
    source_reference="BPHS Ch. 12; Phaladeepika Ch. 6, v. 12",
    predicate=_pred_papa_kartari,
))


# ---------------------------------------------------------------------------
# 13. Affliction & Modern Yogas (5 rules)
# ---------------------------------------------------------------------------

def _pred_guru_chandal(pmap, lagna, houses):
    jh = house_of(pmap, "Jupiter")
    rh = house_of(pmap, "Rahu")
    kh = house_of(pmap, "Ketu")
    if not jh:
        return False, "Absent", []
    present = (jh == rh or jh == kh)
    return present, "Medium" if present else "Absent", [f"Jupiter conjoined with node in H{jh}"] if present else []

_register(YogaRule(
    rule_id="YOGA-GURU-CHANDALA-01",
    version="1.0.0",
    name="Guru-Chandal Yoga",
    category="Affliction Yogas",
    description="Jupiter conjoined with Rahu or Ketu — unconventional thinking, questioning dogma, and potential spiritual testing.",
    source_reference="Jataka Parijata; classical traditions",
    predicate=_pred_guru_chandal,
))


def _pred_ashubha(pmap, lagna, houses):
    # Malefics in Lagna and 9th house
    m_lagna = any(house_of(pmap, m) == 1 for m in ("Sun", "Mars", "Saturn", "Rahu", "Ketu"))
    m_9 = any(house_of(pmap, m) == 9 for m in ("Sun", "Mars", "Saturn", "Rahu", "Ketu"))
    present = m_lagna and m_9
    return present, "Medium" if present else "Absent", ["Malefics occupying both Lagna and 9th house"] if present else []

_register(YogaRule(
    rule_id="YOGA-ASHUBHA-01",
    version="1.0.0",
    name="Ashubha Yoga",
    category="Affliction Yogas",
    description="Natural malefics occupying Lagna and 9th house — challenges to health and fortune, requiring conscious discipline.",
    source_reference="Phaladeepika Ch. 6, v. 41",
    predicate=_pred_ashubha,
))


def _pred_arishta(pmap, lagna, houses):
    l1 = safe_house_lord(lagna, 1)
    if not l1:
        return False, "Absent", []
    h1 = house_of(pmap, l1)
    # Lagna lord in dusthana and afflicted by malefic
    in_dusthana = h1 in DUSTHANA
    malefic_aspect_or_conj = any(house_of(pmap, m) == h1 for m in ("Sun", "Mars", "Saturn", "Rahu", "Ketu") if m != l1)
    present = in_dusthana and malefic_aspect_or_conj
    return present, "Medium" if present else "Absent", [f"Lagna lord {l1} in dusthana H{h1} under malefic influence"] if present else []

def _cancel_arishta(pmap, lagna, houses):
    # Cancelled if strong Jupiter or Venus in Kendra
    for b in ("Jupiter", "Venus"):
        h = house_of(pmap, b)
        if h in KENDRA and not is_debilitated(pmap, b):
            return True, f"Arishta Bhanga: Strong {b} in Kendra (H{h})"
    return False, ""

_register(YogaRule(
    rule_id="YOGA-ARISHTA-01",
    version="1.0.0",
    name="Arishta Yoga",
    category="Affliction Yogas",
    description="Lagna lord placed in a dusthana house afflicted by malefics — health sensitivity and early vulnerability, mitigated by Arishta Bhanga.",
    source_reference="BPHS Ch. 11",
    predicate=_pred_arishta,
    cancellation_rules=[_cancel_arishta],
))


def _pred_arishta_bhanga(pmap, lagna, houses):
    is_c, reason = _cancel_arishta(pmap, lagna, houses)
    return is_c, "Strong" if is_c else "Absent", [reason] if is_c else []

_register(YogaRule(
    rule_id="YOGA-ARISHTA-BHANGA-01",
    version="1.0.0",
    name="Arishta Bhanga",
    category="Cancellation",
    description="Potent natural benefic (Jupiter or Venus) placed in Kendra from Lagna — nullifies infant vulnerability and restores longevity.",
    source_reference="BPHS Ch. 11, v. 1-10",
    predicate=_pred_arishta_bhanga,
))


def _pred_kaal_sarp(pmap, lagna, houses):
    # Contested modern: all 7 classical planets between Rahu and Ketu
    rh = house_of(pmap, "Rahu")
    kh = house_of(pmap, "Ketu")
    if not rh or not kh:
        return False, "Absent", []
    # Count distance from Rahu to planet clockwise
    all_forward = True
    all_backward = True
    for p in CLASSICAL_7:
        hp = house_of(pmap, p)
        if not hp:
            continue
        dist_rahu = (hp - rh) % 12
        if dist_rahu > 6:
            all_forward = False
        dist_ketu = (hp - kh) % 12
        if dist_ketu > 6:
            all_backward = False
    present = all_forward or all_backward
    return present, "Medium" if present else "Absent", ["All 7 classical planets hemmed on one side of Rahu-Ketu axis"] if present else []

_register(YogaRule(
    rule_id="YOGA-KALA-SARPA-MODERN-01",
    version="1.0.0",
    name="Kaal Sarp Yoga",
    category="Contested Modern",
    description="All 7 classical planets situated on one hemisphere between Rahu and Ketu — contested modern convention, disabled by default in classical Parashari mode.",
    source_reference="Modern Astrological Tradition (Contested)",
    predicate=_pred_kaal_sarp,
    enabled_by_default=False,
    contested_modern=True,
))


# ---------------------------------------------------------------------------
# 14. Nabhasa Yogas (12 classical Parashari Sky Configurations)
# ---------------------------------------------------------------------------

# A. Ashraya Yogas (3 rules)
def _pred_rajju(pmap, lagna, houses):
    # All 7 classical planets in Movable (Chara) signs
    for p in CLASSICAL_7:
        if sign_of(pmap, p) not in MOVABLE_SIGNS:
            return False, "Absent", []
    return True, "Strong", ["All classical planets situated in Movable signs"]

_register(YogaRule(
    rule_id="YOGA-NABHASA-RAJJU-01",
    version="1.0.0",
    name="Rajju Nabhasa Yoga",
    category="Nabhasa Yogas",
    description="All seven classical planets placed in Movable (Chara) signs — itinerant lifestyle, fondness for travel, and dynamic ambition.",
    source_reference="BPHS Ch. 35, v. 3",
    predicate=_pred_rajju,
))


def _pred_musala(pmap, lagna, houses):
    # All 7 classical planets in Fixed (Sthira) signs
    for p in CLASSICAL_7:
        if sign_of(pmap, p) not in FIXED_SIGNS:
            return False, "Absent", []
    return True, "Strong", ["All classical planets situated in Fixed signs"]

_register(YogaRule(
    rule_id="YOGA-NABHASA-MUSALA-01",
    version="1.0.0",
    name="Musala Nabhasa Yoga",
    category="Nabhasa Yogas",
    description="All seven classical planets placed in Fixed (Sthira) signs — steadfast resolution, unwavering loyalty, wealth, and obstinacy.",
    source_reference="BPHS Ch. 35, v. 4",
    predicate=_pred_musala,
))


def _pred_nala(pmap, lagna, houses):
    # All 7 classical planets in Dual (Dvisvabhava) signs
    for p in CLASSICAL_7:
        if sign_of(pmap, p) not in DUAL_SIGNS:
            return False, "Absent", []
    return True, "Strong", ["All classical planets situated in Dual signs"]

_register(YogaRule(
    rule_id="YOGA-NABHASA-NALA-01",
    version="1.0.0",
    name="Nala Nabhasa Yoga",
    category="Nabhasa Yogas",
    description="All seven classical planets placed in Dual (Dvisvabhava) signs — adaptable brilliance, linguistic skill, and artistic versatility.",
    source_reference="BPHS Ch. 35, v. 5",
    predicate=_pred_nala,
))


# B. Dala Yogas (2 rules)
def _pred_sarpa(pmap, lagna, houses):
    # Kendra houses occupied solely by malefics, no benefics in Kendra
    kendra_planets = [p for p in CLASSICAL_7 if house_of(pmap, p) in KENDRA]
    if not kendra_planets:
        return False, "Absent", []
    has_benefic = any(p in NATURAL_BENEFICS for p in kendra_planets)
    only_malefics = all(p in NATURAL_MALEFICS for p in kendra_planets)
    present = only_malefics and not has_benefic
    return present, "Medium" if present else "Absent", ["Kendra houses occupied solely by natural malefics"] if present else []

_register(YogaRule(
    rule_id="YOGA-NABHASA-SARPA-01",
    version="1.0.0",
    name="Sarpa Nabhasa Yoga",
    category="Nabhasa Yogas",
    description="Kendra houses occupied exclusively by natural malefics — stubborn demeanor, initial hardships, and formidable fighting spirit.",
    source_reference="BPHS Ch. 35, v. 6",
    predicate=_pred_sarpa,
))


def _pred_mala(pmap, lagna, houses):
    # Kendra houses occupied solely by benefics, no malefics in Kendra
    kendra_planets = [p for p in CLASSICAL_7 if house_of(pmap, p) in KENDRA]
    if not kendra_planets:
        return False, "Absent", []
    has_malefic = any(p in NATURAL_MALEFICS for p in kendra_planets)
    only_benefics = all(p in NATURAL_BENEFICS for p in kendra_planets)
    present = only_benefics and not has_malefic
    return present, "Strong" if present else "Absent", ["Kendra houses occupied solely by natural benefics"] if present else []

_register(YogaRule(
    rule_id="YOGA-NABHASA-MALA-01",
    version="1.0.0",
    name="Mala Nabhasa Yoga",
    category="Nabhasa Yogas",
    description="Kendra houses occupied exclusively by natural benefics — blessed fortune, comfortable conveyances, and honorable livelihood.",
    source_reference="BPHS Ch. 35, v. 7",
    predicate=_pred_mala,
))


# C. Sankhya Yogas (Planets distributed across N signs) (7 rules)
def _count_distinct_signs(pmap):
    occupied = set()
    for p in CLASSICAL_7:
        s = sign_of(pmap, p)
        if s:
            occupied.add(s)
    return len(occupied)


def _pred_vina(pmap, lagna, houses):
    c = _count_distinct_signs(pmap)
    present = (c == 7)
    return present, "Medium" if present else "Absent", ["All 7 classical planets distributed across 7 distinct signs"] if present else []

_register(YogaRule(
    rule_id="YOGA-NABHASA-VINA-01",
    version="1.0.0",
    name="Vina Nabhasa Yoga",
    category="Nabhasa Yogas",
    description="All 7 classical planets spread across exactly 7 distinct signs — aesthetic refinement, musical inclinations, and broad intellect.",
    source_reference="BPHS Ch. 35, v. 14",
    predicate=_pred_vina,
))


def _pred_dama(pmap, lagna, houses):
    c = _count_distinct_signs(pmap)
    present = (c == 6)
    return present, "Medium" if present else "Absent", ["All 7 classical planets distributed across 6 distinct signs"] if present else []

_register(YogaRule(
    rule_id="YOGA-NABHASA-DAMA-01",
    version="1.0.0",
    name="Dama Nabhasa Yoga",
    category="Nabhasa Yogas",
    description="All 7 classical planets spread across exactly 6 distinct signs — generous, charitable, helping others, and wealthy.",
    source_reference="BPHS Ch. 35, v. 15",
    predicate=_pred_dama,
))


def _pred_pasha(pmap, lagna, houses):
    c = _count_distinct_signs(pmap)
    present = (c == 5)
    return present, "Medium" if present else "Absent", ["All 7 classical planets distributed across 5 distinct signs"] if present else []

_register(YogaRule(
    rule_id="YOGA-NABHASA-PASHA-01",
    version="1.0.0",
    name="Pasha Nabhasa Yoga",
    category="Nabhasa Yogas",
    description="All 7 classical planets spread across exactly 5 distinct signs — bound to family responsibilities, skilled in work, and practical.",
    source_reference="BPHS Ch. 35, v. 16",
    predicate=_pred_pasha,
))


def _pred_kedara(pmap, lagna, houses):
    c = _count_distinct_signs(pmap)
    present = (c == 4)
    return present, "Medium" if present else "Absent", ["All 7 classical planets distributed across 4 distinct signs"] if present else []

_register(YogaRule(
    rule_id="YOGA-NABHASA-KEDARA-01",
    version="1.0.0",
    name="Kedara Nabhasa Yoga",
    category="Nabhasa Yogas",
    description="All 7 classical planets concentrated in exactly 4 distinct signs — agricultural or real-estate fortune, industrious and patient.",
    source_reference="BPHS Ch. 35, v. 17",
    predicate=_pred_kedara,
))


def _pred_shula(pmap, lagna, houses):
    c = _count_distinct_signs(pmap)
    present = (c == 3)
    return present, "Medium" if present else "Absent", ["All 7 classical planets concentrated in exactly 3 distinct signs"] if present else []

_register(YogaRule(
    rule_id="YOGA-NABHASA-SHULA-01",
    version="1.0.0",
    name="Shula Nabhasa Yoga",
    category="Nabhasa Yogas",
    description="All 7 classical planets concentrated in exactly 3 distinct signs — intense drive, potential pugnacity, and focused resolve.",
    source_reference="BPHS Ch. 35, v. 18",
    predicate=_pred_shula,
))


def _pred_yuga(pmap, lagna, houses):
    c = _count_distinct_signs(pmap)
    present = (c == 2)
    return present, "Medium" if present else "Absent", ["All 7 classical planets concentrated in exactly 2 distinct signs"] if present else []

_register(YogaRule(
    rule_id="YOGA-NABHASA-YUGA-01",
    version="1.0.0",
    name="Yuga Nabhasa Yoga",
    category="Nabhasa Yogas",
    description="All 7 classical planets concentrated in exactly 2 distinct signs — unconventional outlook, intense concentration of energy.",
    source_reference="BPHS Ch. 35, v. 19",
    predicate=_pred_yuga,
))


def _pred_gola(pmap, lagna, houses):
    c = _count_distinct_signs(pmap)
    present = (c == 1)
    return present, "Medium" if present else "Absent", ["All 7 classical planets concentrated in a single sign"] if present else []

_register(YogaRule(
    rule_id="YOGA-NABHASA-GOLA-01",
    version="1.0.0",
    name="Gola Nabhasa Yoga",
    category="Nabhasa Yogas",
    description="All 7 classical planets concentrated in a single sign — rare astrological stellium signifying extreme focused karma.",
    source_reference="BPHS Ch. 35, v. 20",
    predicate=_pred_gola,
))


# ---------------------------------------------------------------------------
# Engine Evaluator
# ---------------------------------------------------------------------------

def evaluate_yoga_rule(
    rule: YogaRule,
    pmap: dict[str, dict],
    lagna_sign: str,
    houses: dict,
    include_disabled: bool = False,
) -> dict[str, Any]:
    """Evaluate a single YogaRule against a prepared planet map."""
    if not rule.enabled_by_default and not include_disabled:
        return {
            "rule_id": rule.rule_id,
            "version": rule.version,
            "name": rule.name,
            "category": rule.category,
            "description": rule.description,
            "present": False,
            "strength": "Absent",
            "source_reference": rule.source_reference,
            "cancelled": False,
            "cancellation_reason": None,
            "contested_modern": rule.contested_modern,
            "enabled_by_default": rule.enabled_by_default,
            "is_umbrella": rule.is_umbrella,
            "dedupe_key": rule.dedupe_key,
            "details": [],
        }

    present, strength, details = rule.predicate(pmap, lagna_sign, houses)

    cancelled = False
    cancel_reason = None
    if present and rule.cancellation_rules:
        for c_fn in rule.cancellation_rules:
            is_c, reason = c_fn(pmap, lagna_sign, houses)
            if is_c:
                cancelled = True
                cancel_reason = reason
                present = False
                strength = "Absent"
                break

    return {
        "rule_id": rule.rule_id,
        "version": rule.version,
        "name": rule.name,
        "category": rule.category,
        "description": rule.description,
        "present": bool(present),
        "strength": strength if present else "Absent",
        "source_reference": rule.source_reference,
        "cancelled": cancelled,
        "cancellation_reason": cancel_reason,
        "contested_modern": rule.contested_modern,
        "enabled_by_default": rule.enabled_by_default,
        "is_umbrella": rule.is_umbrella,
        "dedupe_key": rule.dedupe_key,
        "details": details if present else [],
    }


def evaluate_yoga_catalog(
    planets: list[dict],
    lagna_sign: str,
    houses: dict,
    include_disabled: bool = False,
) -> list[dict[str, Any]]:
    """Evaluate all catalog rules on the chart and return structured results."""
    pmap = get_planet_map(planets)
    results = []
    for rule in CATALOG:
        results.append(evaluate_yoga_rule(rule, pmap, lagna_sign, houses, include_disabled=include_disabled))
    return results
