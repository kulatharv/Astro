"""
Classical Vedic Astrology Timing & Dasha–Transit Fusion Rule Pack (Pure Shared Library).

Implements 25 canonical, deterministic Parāśari timing rules across 4 evidence families:
  1. Dasha Period Activation (10 rules)
  2. Planetary Transit Triggers & Double Transit (10 rules)
  3. Ashtakavarga Bindu Support (4 rules)
  4. Gochara Vedha Obstruction (1 rule)

Strictly adheres to Master Specification v3.0 §13, §14 & §21 (Timing & Safety Architecture).
ABSOLUTE PROHIBITION: Never predicts fixed, guaranteed event dates or probabilities.
All evaluations are qualitative, explainable evidence clustering.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Any, Optional, Dict, List

from .zodiac import SIGNS_SK, SIGN_LORDS
from .strength import EXALTATION, DEBILITATION, OWN_SIGNS
from .lordship import get_house_lord, is_yogakaraka, is_functional_benefic, is_functional_malefic
from .ashtakavarga import compute_sav, compute_bav
from .vedha import check_transit_vedha

TIMING_SAFETY_DISCLAIMER = (
    "AstroLogic AI provides non-deterministic cultural, philosophical, and astrological reflections only. "
    "Astrological timing windows indicate traditional symbolic alignments and clustering of conditions, "
    "NEVER guaranteed event dates, deterministic life occurrences, or statistical probabilities. "
    "Important life decisions must always be guided by rational judgment, practical preparation, and professional counsel."
)

KENDRA = {1, 4, 7, 10}
TRIKONA = {1, 5, 9}
DUSTHANA = {6, 8, 12}
UPACHAYA = {3, 6, 10, 11}


@dataclass
class TimingRule:
    rule_id: str
    version: str
    family: str  # 'dasha', 'transit', 'ashtakavarga', 'vedha', 'double_transit'
    domain: str  # 'all' or domain name
    profile: str
    chart_frame: str
    predicate: Callable[[dict, dict], tuple[bool, str, list[str]]]
    ordered_exceptions: list[Callable[[dict, dict], tuple[bool, str]]] = field(default_factory=list)
    dedupe_key: Optional[str] = None
    effect: str = "SUPPORTS"  # SUPPORTS, OBSTRUCTS, CONDITIONAL
    birth_time_sensitive: bool = False
    explanation_template: str = ""
    source_family: str = "Parashari"
    source_reference: str = ""
    source_status: str = "VERIFIED"
    review_status: str = "ACCEPTED"
    confidence: str = "[HIGH]"
    tests: list[str] = field(default_factory=list)
    enabled: bool = True


TIMING_RULES_CATALOG: list[TimingRule] = []


def _reg(r: TimingRule) -> None:
    TIMING_RULES_CATALOG.append(r)


# ===========================================================================
# 1. DASHA ACTIVATION RULES (TIME-DSH-01 to TIME-DSH-10)
# ===========================================================================

def pred_time_dsh_01(ctx: dict, timing_ctx: dict) -> tuple[bool, str, list[str]]:
    md = timing_ctx.get("md_lord", ctx.get("mahadasha", "Jupiter"))
    ad = timing_ctx.get("ad_lord", ctx.get("antardasha", "Venus"))
    pm = ctx.get("planet_map", {})
    md_h = pm.get(md, {}).get("house", 0)
    ad_h = pm.get(ad, {}).get("house", 0)
    if md_h > 0 and ad_h > 0:
        diff = (ad_h - md_h) % 12
        if diff in (0, 3, 4, 6, 8, 9):  # 1, 4, 5, 7, 9, 10 mutual positions
            return True, f"Mahadasha lord {md} and Antardasha lord {ad} form harmonious mutual Kendra/Trikona placement ({diff+1}th from MD).", [md, ad]
    return False, "", []

_reg(TimingRule(
    rule_id="TIME-DSH-01",
    version="1.0.0",
    family="dasha",
    domain="all",
    profile="parashari",
    chart_frame="D1",
    predicate=pred_time_dsh_01,
    dedupe_key="md_ad_kendra_trikona",
    effect="SUPPORTS",
    birth_time_sensitive=True,
    explanation_template="Mutual Kendra or Trikona placement between MD and AD lords promotes cooperative period activation.",
    source_reference="BPHS Ch. 47, v. 2-5",
))


def pred_time_dsh_02(ctx: dict, timing_ctx: dict) -> tuple[bool, str, list[str]]:
    md = timing_ctx.get("md_lord", ctx.get("mahadasha", "Jupiter"))
    ad = timing_ctx.get("ad_lord", ctx.get("antardasha", "Venus"))
    pm = ctx.get("planet_map", {})
    md_h = pm.get(md, {}).get("house", 0)
    ad_h = pm.get(ad, {}).get("house", 0)
    if md_h > 0 and ad_h > 0:
        diff = (ad_h - md_h) % 12
        if diff in (5, 7):  # 6th or 8th (Shadashtaka)
            return True, f"MD lord {md} and AD lord {ad} are in 6/8 (Shadashtaka) mutual placement, indicating frictional adjustments.", [md, ad]
        if diff in (1, 11):  # 2nd or 12th (Dwirdwadasha)
            return True, f"MD lord {md} and AD lord {ad} are in 2/12 (Dwirdwadasha) mutual placement, indicating resource reassessment.", [md, ad]
    return False, "", []

def exc_time_dsh_02(ctx: dict, timing_ctx: dict) -> tuple[bool, str]:
    # Exception: if both planets are natural benefics or friends
    md = timing_ctx.get("md_lord", ctx.get("mahadasha", "Jupiter"))
    ad = timing_ctx.get("ad_lord", ctx.get("antardasha", "Venus"))
    if md in ("Jupiter", "Venus", "Mercury") and ad in ("Jupiter", "Venus", "Mercury"):
        return True, f"Both {md} and {ad} are natural benefics, mitigating adverse 6/8 or 2/12 friction."
    return False, ""

_reg(TimingRule(
    rule_id="TIME-DSH-02",
    version="1.0.0",
    family="dasha",
    domain="all",
    profile="parashari",
    chart_frame="D1",
    predicate=pred_time_dsh_02,
    ordered_exceptions=[exc_time_dsh_02],
    dedupe_key="md_ad_shadashtaka",
    effect="OBSTRUCTS",
    birth_time_sensitive=True,
    explanation_template="Shadashtaka (6/8) or Dwirdwadasha (2/12) mutual placements between subperiod lords create testing circumstances.",
    source_reference="Phaladeepika Ch. 20, v. 12-14",
))


def pred_time_dsh_03(ctx: dict, timing_ctx: dict) -> tuple[bool, str, list[str]]:
    md = timing_ctx.get("md_lord", ctx.get("mahadasha", "Jupiter"))
    lagna = ctx.get("lagna", "Mesha")
    if is_yogakaraka(lagna, md):
        return True, f"Active Mahadasha lord {md} is Yogakaraka for {lagna} Lagna, providing powerful directional momentum.", [md]
    return False, "", []

_reg(TimingRule(
    rule_id="TIME-DSH-03",
    version="1.0.0",
    family="dasha",
    domain="all",
    profile="parashari",
    chart_frame="D1",
    predicate=pred_time_dsh_03,
    dedupe_key="md_yogakaraka",
    effect="SUPPORTS",
    birth_time_sensitive=True,
    explanation_template="Yogakaraka Dasha provides structural auspiciousness and favorable execution capacity.",
    source_reference="BPHS Ch. 34, v. 25-27",
))


def pred_time_dsh_04(ctx: dict, timing_ctx: dict) -> tuple[bool, str, list[str]]:
    md = timing_ctx.get("md_lord", ctx.get("mahadasha", "Jupiter"))
    pm = ctx.get("planet_map", {})
    sign = pm.get(md, {}).get("sign", "")
    is_ex = (sign == EXALTATION.get(md, ""))
    is_own = (sign in OWN_SIGNS.get(md, set()))
    if is_ex or is_own:
        return True, f"Dasha lord {md} is in dignified condition ({'exalted' if is_ex else 'own sign'} in {sign}).", [md]
    return False, "", []

_reg(TimingRule(
    rule_id="TIME-DSH-04",
    version="1.0.0",
    family="dasha",
    domain="all",
    profile="parashari",
    chart_frame="D1",
    predicate=pred_time_dsh_04,
    dedupe_key="md_dignity",
    effect="SUPPORTS",
    birth_time_sensitive=False,
    explanation_template="Dignified Dasha lord operates with high clarity and resilience.",
    source_reference="Saravali Ch. 41",
))


def pred_time_dsh_05(ctx: dict, timing_ctx: dict) -> tuple[bool, str, list[str]]:
    md = timing_ctx.get("md_lord", ctx.get("mahadasha", "Jupiter"))
    pm = ctx.get("planet_map", {})
    pdata = pm.get(md, {})
    sign = pdata.get("sign", "")
    is_deb = (sign == DEBILITATION.get(md, ""))
    is_comb = pdata.get("is_combust", False)
    if is_deb or is_comb:
        return True, f"Dasha lord {md} is {'debilitated in ' + sign if is_deb else 'combust'}, requiring greater patience.", [md]
    return False, "", []

_reg(TimingRule(
    rule_id="TIME-DSH-05",
    version="1.0.0",
    family="dasha",
    domain="all",
    profile="parashari",
    chart_frame="D1",
    predicate=pred_time_dsh_05,
    dedupe_key="md_debilitated_combust",
    effect="OBSTRUCTS",
    birth_time_sensitive=False,
    explanation_template="Debilitated or combust Dasha lord indicates procedural delays or subdued outer expression.",
    source_reference="Phaladeepika Ch. 20",
))


def pred_time_dsh_06(ctx: dict, timing_ctx: dict) -> tuple[bool, str, list[str]]:
    # Dasha Sandhi: Within first or last 6 months of a Mahadasha
    months_from_start = timing_ctx.get("months_into_md", 12)
    months_to_end = timing_ctx.get("months_to_md_end", 12)
    if months_from_start <= 6 or months_to_end <= 6:
        return True, "Active period coincides with Dasha Sandhi (transition boundary), signaling transitional restructuring.", []
    return False, "", []

_reg(TimingRule(
    rule_id="TIME-DSH-06",
    version="1.0.0",
    family="dasha",
    domain="all",
    profile="parashari",
    chart_frame="D1",
    predicate=pred_time_dsh_06,
    dedupe_key="dasha_sandhi",
    effect="CONDITIONAL",
    birth_time_sensitive=True,
    explanation_template="Dasha Sandhi (cusp between major periods) represents transitional reorganization.",
    source_reference="Phaladeepika Ch. 19, v. 28",
    source_status="SOURCE VERIFICATION REQUIRED",
    review_status="PENDING_EXPERT_REVIEW",
    confidence="[MEDIUM]",
))


def pred_time_dsh_07(ctx: dict, timing_ctx: dict) -> tuple[bool, str, list[str]]:
    # Domain house lordship or occupancy
    domain_houses = timing_ctx.get("domain_houses", [10, 6, 11])
    md = timing_ctx.get("md_lord", ctx.get("mahadasha", "Jupiter"))
    ad = timing_ctx.get("ad_lord", ctx.get("antardasha", "Venus"))
    pm = ctx.get("planet_map", {})
    hl = ctx.get("house_lords", {})

    activated_by = []
    for h in domain_houses:
        lord = hl.get(h)
        if lord in (md, ad):
            activated_by.append(f"{lord} (rules H{h})")
        if pm.get(md, {}).get("house") == h:
            activated_by.append(f"{md} (in H{h})")
        if pm.get(ad, {}).get("house") == h:
            activated_by.append(f"{ad} (in H{h})")

    if activated_by:
        return True, f"Active period activates domain significators: {', '.join(set(activated_by))}.", [md, ad]
    return False, "", []

_reg(TimingRule(
    rule_id="TIME-DSH-07",
    version="1.0.0",
    family="dasha",
    domain="all",
    profile="parashari",
    chart_frame="D1",
    predicate=pred_time_dsh_07,
    dedupe_key="dasha_domain_significator",
    effect="SUPPORTS",
    birth_time_sensitive=True,
    explanation_template="Dasha or Antardasha lord ruling or occupying domain houses triggers life domain themes.",
    source_reference="BPHS Ch. 47",
    source_status="SOURCE VERIFICATION REQUIRED",
    review_status="PENDING_EXPERT_REVIEW",
    confidence="[MEDIUM]",
))


def pred_time_dsh_08(ctx: dict, timing_ctx: dict) -> tuple[bool, str, list[str]]:
    md = timing_ctx.get("md_lord", ctx.get("mahadasha", "Jupiter"))
    ad = timing_ctx.get("ad_lord", ctx.get("antardasha", "Venus"))
    lagna = ctx.get("lagna", "Mesha")
    if is_functional_benefic(lagna, md) and is_functional_benefic(lagna, ad):
        return True, f"Both MD ({md}) and AD ({ad}) are functional benefics for {lagna} Lagna.", [md, ad]
    return False, "", []

_reg(TimingRule(
    rule_id="TIME-DSH-08",
    version="1.0.0",
    family="dasha",
    domain="all",
    profile="parashari",
    chart_frame="D1",
    predicate=pred_time_dsh_08,
    dedupe_key="md_ad_both_benefic",
    effect="SUPPORTS",
    birth_time_sensitive=True,
    explanation_template="Both subperiod lords functioning beneficially for the ascendant provide harmonious timing.",
    source_reference="BPHS Ch. 47",
))


def pred_time_dsh_09(ctx: dict, timing_ctx: dict) -> tuple[bool, str, list[str]]:
    pd = timing_ctx.get("pd_lord", "Jupiter")
    ad = timing_ctx.get("ad_lord", "Venus")
    if pd == ad or pd in ("Jupiter", "Venus"):
        return True, f"Pratyantardasha lord {pd} harmonizes with Antardasha lord {ad}.", [pd]
    return False, "", []

_reg(TimingRule(
    rule_id="TIME-DSH-09",
    version="1.0.0",
    family="dasha",
    domain="all",
    profile="parashari",
    chart_frame="D1",
    predicate=pred_time_dsh_09,
    dedupe_key="pd_favorable_alignment",
    effect="SUPPORTS",
    birth_time_sensitive=True,
    explanation_template="Supportive Pratyantardasha lord refines timing window alignment.",
    source_reference="Phaladeepika Ch. 21",
    source_status="SOURCE VERIFICATION REQUIRED",
    review_status="PENDING_EXPERT_REVIEW",
    confidence="[MEDIUM]",
))


def pred_time_dsh_10(ctx: dict, timing_ctx: dict) -> tuple[bool, str, list[str]]:
    md = timing_ctx.get("md_lord", ctx.get("mahadasha", "Jupiter"))
    ad = timing_ctx.get("ad_lord", ctx.get("antardasha", "Venus"))
    lagna = ctx.get("lagna", "Mesha")
    if is_functional_malefic(lagna, md) and is_functional_malefic(lagna, ad):
        return True, f"Both MD ({md}) and AD ({ad}) are functional malefics for {lagna} Lagna, urging disciplined caution.", [md, ad]
    return False, "", []

_reg(TimingRule(
    rule_id="TIME-DSH-10",
    version="1.0.0",
    family="dasha",
    domain="all",
    profile="parashari",
    chart_frame="D1",
    predicate=pred_time_dsh_10,
    dedupe_key="md_ad_both_malefic",
    effect="OBSTRUCTS",
    birth_time_sensitive=True,
    explanation_template="Dual functional malefic subperiods require conservative management.",
    source_reference="BPHS Ch. 47",
))


# ===========================================================================
# 2. TRANSIT & DOUBLE TRANSIT RULES (TIME-TRN-01 to TIME-TRN-10)
# ===========================================================================

def pred_time_trn_01(ctx: dict, timing_ctx: dict) -> tuple[bool, str, list[str]]:
    # Double Transit: Jupiter and Saturn simultaneous influence on key domain house
    target_houses = timing_ctx.get("domain_houses", [10, 7, 5, 2])
    t_map = timing_ctx.get("transit_map", ctx.get("transit_map", {}))
    jup_h = t_map.get("Jupiter", {}).get("house", 0)
    sat_h = t_map.get("Saturn", {}).get("house", 0)

    # Aspects: Jupiter 1, 5, 7, 9; Saturn 1, 3, 7, 10
    jup_aspects = {jup_h, (jup_h + 4) % 12 or 12, (jup_h + 6) % 12 or 12, (jup_h + 8) % 12 or 12} if jup_h else set()
    sat_aspects = {sat_h, (sat_h + 2) % 12 or 12, (sat_h + 6) % 12 or 12, (sat_h + 9) % 12 or 12} if sat_h else set()

    for h in target_houses:
        if h in jup_aspects and h in sat_aspects:
            return True, f"Double Transit confirmed: Jupiter and Saturn simultaneously influence house {h}, establishing major event activation.", ["Jupiter", "Saturn"]
    return False, "", []

_reg(TimingRule(
    rule_id="TIME-TRN-01",
    version="1.0.0",
    family="double_transit",
    domain="all",
    profile="parashari",
    chart_frame="D1",
    predicate=pred_time_trn_01,
    dedupe_key="double_transit_active",
    effect="SUPPORTS",
    birth_time_sensitive=True,
    explanation_template="Classical Double Transit: Simultaneous activation by Jupiter and Saturn indicates realization of natal potential.",
    source_reference="Classical Tradition; BPHS & Phaladeepika Ch. 26",
    source_status="SOURCE VERIFICATION REQUIRED",
    review_status="PENDING_EXPERT_REVIEW",
    confidence="[MEDIUM]",
))


def pred_time_trn_02(ctx: dict, timing_ctx: dict) -> tuple[bool, str, list[str]]:
    # Jupiter transiting 1, 5, or 9 from natal Moon (Trine Gochara)
    pm = ctx.get("planet_map", {})
    moon_h = pm.get("Moon", {}).get("house", 1)
    t_map = timing_ctx.get("transit_map", ctx.get("transit_map", {}))
    jup_h = t_map.get("Jupiter", {}).get("house", 0)
    if jup_h > 0 and moon_h > 0:
        diff = (jup_h - moon_h) % 12
        if diff in (0, 4, 8):  # 1st, 5th, 9th from Moon
            return True, f"Jupiter transiting house {diff+1} from natal Moon provides broad auspicious blessings.", ["Jupiter"]
    return False, "", []

_reg(TimingRule(
    rule_id="TIME-TRN-02",
    version="1.0.0",
    family="transit",
    domain="all",
    profile="parashari",
    chart_frame="D1",
    predicate=pred_time_trn_02,
    dedupe_key="jupiter_trine_moon",
    effect="SUPPORTS",
    birth_time_sensitive=False,
    explanation_template="Jupiter transiting 1st, 5th, or 9th from Janma Rashi bestows general auspiciousness and vitality.",
    source_reference="Phaladeepika Ch. 26, v. 13-14",
))


def pred_time_trn_03(ctx: dict, timing_ctx: dict) -> tuple[bool, str, list[str]]:
    # Saturn in 8th from Moon (Ashtama Shani)
    pm = ctx.get("planet_map", {})
    moon_h = pm.get("Moon", {}).get("house", 1)
    t_map = timing_ctx.get("transit_map", ctx.get("transit_map", {}))
    sat_h = t_map.get("Saturn", {}).get("house", 0)
    if sat_h > 0 and moon_h > 0:
        diff = (sat_h - moon_h) % 12
        if diff == 7:  # 8th from Moon
            return True, "Saturn transiting 8th from natal Moon (Ashtama Shani) introduces serious consolidation and patience.", ["Saturn"]
    return False, "", []

_reg(TimingRule(
    rule_id="TIME-TRN-03",
    version="1.0.0",
    family="transit",
    domain="all",
    profile="parashari",
    chart_frame="D1",
    predicate=pred_time_trn_03,
    dedupe_key="ashtama_shani",
    effect="OBSTRUCTS",
    birth_time_sensitive=False,
    explanation_template="Ashtama Shani (Saturn in 8th from Moon) tests endurance and demands meticulous attention.",
    source_reference="Phaladeepika Ch. 26, v. 18",
))


def pred_time_trn_04(ctx: dict, timing_ctx: dict) -> tuple[bool, str, list[str]]:
    # Sade Sati: Saturn in 12, 1, 2 from Moon
    pm = ctx.get("planet_map", {})
    moon_h = pm.get("Moon", {}).get("house", 1)
    t_map = timing_ctx.get("transit_map", ctx.get("transit_map", {}))
    sat_h = t_map.get("Saturn", {}).get("house", 0)
    if sat_h > 0 and moon_h > 0:
        diff = (sat_h - moon_h) % 12
        if diff in (11, 0, 1):  # 12th, 1st, 2nd
            phase = "Setting (2nd)" if diff == 1 else ("Peak (1st)" if diff == 0 else "Rising (12th)")
            return True, f"Saturn is transiting in Sade Sati ({phase} phase), emphasizing emotional discipline and foundational maturity.", ["Saturn"]
    return False, "", []

_reg(TimingRule(
    rule_id="TIME-TRN-04",
    version="1.0.0",
    family="transit",
    domain="all",
    profile="parashari",
    chart_frame="D1",
    predicate=pred_time_trn_04,
    dedupe_key="sade_sati_phase",
    effect="CONDITIONAL",
    birth_time_sensitive=False,
    explanation_template="Sade Sati transit of Saturn fosters internal maturation through responsibility.",
    source_reference="Classical Gochara Tradition",
    source_status="SOURCE VERIFICATION REQUIRED",
    review_status="PENDING_EXPERT_REVIEW",
    confidence="[MEDIUM]",
))


def pred_time_trn_05(ctx: dict, timing_ctx: dict) -> tuple[bool, str, list[str]]:
    # Jupiter transiting directly in domain significator house
    target_houses = timing_ctx.get("domain_houses", [10, 7, 5, 2])
    t_map = timing_ctx.get("transit_map", ctx.get("transit_map", {}))
    jup_h = t_map.get("Jupiter", {}).get("house", 0)
    if jup_h in target_houses:
        return True, f"Jupiter directly transits domain house {jup_h}, expanding opportunities.", ["Jupiter"]
    return False, "", []

_reg(TimingRule(
    rule_id="TIME-TRN-05",
    version="1.0.0",
    family="transit",
    domain="all",
    profile="parashari",
    chart_frame="D1",
    predicate=pred_time_trn_05,
    dedupe_key="jupiter_in_domain_house",
    effect="SUPPORTS",
    birth_time_sensitive=True,
    explanation_template="Benefic Jupiter transiting a key domain house provides supportive expansion.",
    source_reference="Phaladeepika Ch. 26",
))


def pred_time_trn_06(ctx: dict, timing_ctx: dict) -> tuple[bool, str, list[str]]:
    # Saturn transiting domain house
    target_houses = timing_ctx.get("domain_houses", [10, 7, 5, 2])
    t_map = timing_ctx.get("transit_map", ctx.get("transit_map", {}))
    sat_h = t_map.get("Saturn", {}).get("house", 0)
    if sat_h in target_houses:
        return True, f"Saturn transits domain house {sat_h}, imposing structure, patience, and realistic assessment.", ["Saturn"]
    return False, "", []

_reg(TimingRule(
    rule_id="TIME-TRN-06",
    version="1.0.0",
    family="transit",
    domain="all",
    profile="parashari",
    chart_frame="D1",
    predicate=pred_time_trn_06,
    dedupe_key="saturn_in_domain_house",
    effect="CONDITIONAL",
    birth_time_sensitive=True,
    explanation_template="Saturn transiting a key domain house demands rigorous discipline and methodical effort.",
    source_reference="Phaladeepika Ch. 26",
    source_status="SOURCE VERIFICATION REQUIRED",
    review_status="PENDING_EXPERT_REVIEW",
    confidence="[MEDIUM]",
))


def pred_time_trn_07(ctx: dict, timing_ctx: dict) -> tuple[bool, str, list[str]]:
    # Rahu-Ketu nodal axis in key houses (1/7 or 4/10)
    t_map = timing_ctx.get("transit_map", ctx.get("transit_map", {}))
    rahu_h = t_map.get("Rahu", {}).get("house", 0)
    if rahu_h in (1, 7, 4, 10):
        return True, f"Rahu-Ketu transit axis falls across Kendra houses {rahu_h}/{(rahu_h+6)%12 or 12}, accelerating transformative changes.", ["Rahu", "Ketu"]
    return False, "", []

_reg(TimingRule(
    rule_id="TIME-TRN-07",
    version="1.0.0",
    family="transit",
    domain="all",
    profile="parashari",
    chart_frame="D1",
    predicate=pred_time_trn_07,
    dedupe_key="nodal_axis_kendra",
    effect="CONDITIONAL",
    birth_time_sensitive=True,
    explanation_template="Nodal transit through Kendras stimulates evolutionary changes and shifts in focus.",
    source_reference="Saravali Ch. 34",
    source_status="SOURCE VERIFICATION REQUIRED",
    review_status="PENDING_EXPERT_REVIEW",
    confidence="[MEDIUM]",
))


def pred_time_trn_08(ctx: dict, timing_ctx: dict) -> tuple[bool, str, list[str]]:
    # Mars transiting in Upachaya houses (3, 6, 10, 11) from natal Moon
    pm = ctx.get("planet_map", {})
    moon_h = pm.get("Moon", {}).get("house", 1)
    t_map = timing_ctx.get("transit_map", ctx.get("transit_map", {}))
    mars_h = t_map.get("Mars", {}).get("house", 0)
    if mars_h > 0 and moon_h > 0:
        diff = (mars_h - moon_h) % 12
        if diff in (2, 5, 9, 10):  # 3, 6, 10, 11 from Moon
            return True, f"Mars transiting house {diff+1} from natal Moon provides vitality and competitive momentum.", ["Mars"]
    return False, "", []

_reg(TimingRule(
    rule_id="TIME-TRN-08",
    version="1.0.0",
    family="transit",
    domain="all",
    profile="parashari",
    chart_frame="D1",
    predicate=pred_time_trn_08,
    dedupe_key="mars_upachaya_transit",
    effect="SUPPORTS",
    birth_time_sensitive=False,
    explanation_template="Mars transiting in Upachaya houses from Janma Rashi provides energy and overcomes obstacles.",
    source_reference="Phaladeepika Ch. 26, v. 9-10",
))


def pred_time_trn_09(ctx: dict, timing_ctx: dict) -> tuple[bool, str, list[str]]:
    # Transit retrograde planet in domain house
    target_houses = timing_ctx.get("domain_houses", [10, 7, 5, 2])
    t_map = timing_ctx.get("transit_map", ctx.get("transit_map", {}))
    for p in ("Mercury", "Venus", "Mars", "Jupiter", "Saturn"):
        pdata = t_map.get(p, {})
        if pdata.get("is_retrograde", False) and pdata.get("house") in target_houses:
            return True, f"Retrograde transiting planet {p} in domain house {pdata.get('house')} invites review and refinement.", [p]
    return False, "", []

_reg(TimingRule(
    rule_id="TIME-TRN-09",
    version="1.0.0",
    family="transit",
    domain="all",
    profile="parashari",
    chart_frame="D1",
    predicate=pred_time_trn_09,
    dedupe_key="retrograde_transit_in_house",
    effect="CONDITIONAL",
    birth_time_sensitive=True,
    explanation_template="Retrograde planetary transits in relevant houses emphasize revision and internal reflection.",
    source_reference="Saravali Ch. 5",
    source_status="SOURCE VERIFICATION REQUIRED",
    review_status="PENDING_EXPERT_REVIEW",
    confidence="[MEDIUM]",
))


def pred_time_trn_10(ctx: dict, timing_ctx: dict) -> tuple[bool, str, list[str]]:
    # Transiting Jupiter in Kendra or Trikona to natal Dasha lord
    md = timing_ctx.get("md_lord", ctx.get("mahadasha", "Jupiter"))
    pm = ctx.get("planet_map", {})
    t_map = timing_ctx.get("transit_map", ctx.get("transit_map", {}))
    md_h = pm.get(md, {}).get("house", 0)
    jup_h = t_map.get("Jupiter", {}).get("house", 0)
    if md_h > 0 and jup_h > 0:
        diff = (jup_h - md_h) % 12
        if diff in (0, 3, 4, 6, 8, 9):  # 1, 4, 5, 7, 9, 10 from natal MD lord
            return True, f"Transiting Jupiter is in Kendra/Trikona ({diff+1}th) to natal Dasha lord {md}, harmonizing transit and period cycles.", ["Jupiter", md]
    return False, "", []

_reg(TimingRule(
    rule_id="TIME-TRN-10",
    version="1.0.0",
    family="transit",
    domain="all",
    profile="parashari",
    chart_frame="D1",
    predicate=pred_time_trn_10,
    dedupe_key="jupiter_kendra_to_md",
    effect="SUPPORTS",
    birth_time_sensitive=True,
    explanation_template="Transiting Jupiter forming Kendra/Trikona to natal Dasha lord aligns external opportunities with internal timing.",
    source_reference="BPHS Ch. 47",
    source_status="SOURCE VERIFICATION REQUIRED",
    review_status="PENDING_EXPERT_REVIEW",
    confidence="[MEDIUM]",
))


# ===========================================================================
# 3. ASHTAKAVARGA & VEDHA RULES (TIME-AV-01 to TIME-AV-05)
# ===========================================================================

def pred_time_av_01(ctx: dict, timing_ctx: dict) -> tuple[bool, str, list[str]]:
    sav = compute_sav(ctx)
    t_map = timing_ctx.get("transit_map", ctx.get("transit_map", {}))
    jup_sign = t_map.get("Jupiter", {}).get("sign", "")
    if jup_sign and sav.get(jup_sign, 0) >= 28:
        bindus = sav[jup_sign]
        return True, f"Transiting Jupiter occupies high-SAV sign {jup_sign} ({bindus} bindus), providing strong environmental backing.", ["Jupiter"]
    return False, "", []

_reg(TimingRule(
    rule_id="TIME-AV-01",
    version="1.0.0",
    family="ashtakavarga",
    domain="all",
    profile="parashari",
    chart_frame="D1",
    predicate=pred_time_av_01,
    dedupe_key="jupiter_high_sav",
    effect="SUPPORTS",
    birth_time_sensitive=False,
    explanation_template="Transiting Jupiter in high Sarva Ashtakavarga sign (>= 28 bindus) enhances beneficial manifestation.",
    source_reference="BPHS Ch. 66",
))


def pred_time_av_02(ctx: dict, timing_ctx: dict) -> tuple[bool, str, list[str]]:
    sav = compute_sav(ctx)
    t_map = timing_ctx.get("transit_map", ctx.get("transit_map", {}))
    sat_sign = t_map.get("Saturn", {}).get("sign", "")
    if sat_sign and sav.get(sat_sign, 28) < 25:
        bindus = sav[sat_sign]
        return True, f"Transiting Saturn occupies low-SAV sign {sat_sign} ({bindus} bindus), indicating reduced environmental support.", ["Saturn"]
    return False, "", []

_reg(TimingRule(
    rule_id="TIME-AV-02",
    version="1.0.0",
    family="ashtakavarga",
    domain="all",
    profile="parashari",
    chart_frame="D1",
    predicate=pred_time_av_02,
    dedupe_key="saturn_low_sav",
    effect="OBSTRUCTS",
    birth_time_sensitive=False,
    explanation_template="Transiting Saturn in low-SAV sign (< 25 bindus) intensifies pressure and requires patience.",
    source_reference="BPHS Ch. 66",
))


def pred_time_av_03(ctx: dict, timing_ctx: dict) -> tuple[bool, str, list[str]]:
    bav_jup = compute_bav("Jupiter", ctx)
    t_map = timing_ctx.get("transit_map", ctx.get("transit_map", {}))
    jup_sign = t_map.get("Jupiter", {}).get("sign", "")
    if jup_sign and bav_jup.get(jup_sign, 0) >= 5:
        bindus = bav_jup[jup_sign]
        return True, f"Jupiter has high personal BAV strength in {jup_sign} ({bindus}/8 bindus).", ["Jupiter"]
    return False, "", []

_reg(TimingRule(
    rule_id="TIME-AV-03",
    version="1.0.0",
    family="ashtakavarga",
    domain="all",
    profile="parashari",
    chart_frame="D1",
    predicate=pred_time_av_03,
    dedupe_key="jupiter_high_bav",
    effect="SUPPORTS",
    birth_time_sensitive=False,
    explanation_template="High Bhinna Ashtakavarga bindus (>= 5) ensure the planet delivers robust personal results.",
    source_reference="BPHS Ch. 66",
))


def pred_time_av_04(ctx: dict, timing_ctx: dict) -> tuple[bool, str, list[str]]:
    bav_sat = compute_bav("Saturn", ctx)
    t_map = timing_ctx.get("transit_map", ctx.get("transit_map", {}))
    sat_sign = t_map.get("Saturn", {}).get("sign", "")
    if sat_sign and bav_sat.get(sat_sign, 4) < 3:
        bindus = bav_sat[sat_sign]
        return True, f"Saturn has low personal BAV strength in {sat_sign} ({bindus}/8 bindus).", ["Saturn"]
    return False, "", []

_reg(TimingRule(
    rule_id="TIME-AV-04",
    version="1.0.0",
    family="ashtakavarga",
    domain="all",
    profile="parashari",
    chart_frame="D1",
    predicate=pred_time_av_04,
    dedupe_key="saturn_low_bav",
    effect="OBSTRUCTS",
    birth_time_sensitive=False,
    explanation_template="Low BAV bindus (< 3) diminish the planet's capacity to yield smooth outcomes.",
    source_reference="BPHS Ch. 66",
))


def pred_time_ved_01(ctx: dict, timing_ctx: dict) -> tuple[bool, str, list[str]]:
    # Check Vedha obstruction on Jupiter transit from Moon
    pm = ctx.get("planet_map", {})
    moon_h = pm.get("Moon", {}).get("house", 1)
    t_map = timing_ctx.get("transit_map", ctx.get("transit_map", {}))

    # Compute positions from Moon
    transit_from_moon: Dict[str, int] = {}
    for p, pdata in t_map.items():
        p_house = pdata.get("house", 1)
        transit_from_moon[p] = (p_house - moon_h) % 12 + 1

    jup_from_moon = transit_from_moon.get("Jupiter", 1)
    vedha_res = check_transit_vedha("Jupiter", jup_from_moon, transit_from_moon)

    if vedha_res.get("is_obstructed", False):
        obs = vedha_res.get("obstructing_planets", [])
        return True, f"Jupiter's benefic transit in house {jup_from_moon} from Moon is obstructed (Vedha) by {', '.join(obs)}.", ["Jupiter"] + obs
    return False, "", []

_reg(TimingRule(
    rule_id="TIME-VED-01",
    version="1.0.0",
    family="vedha",
    domain="all",
    profile="parashari",
    chart_frame="D1",
    predicate=pred_time_ved_01,
    dedupe_key="jupiter_vedha_obstructed",
    effect="OBSTRUCTS",
    birth_time_sensitive=False,
    explanation_template="Classical Gochara Vedha: Benefic transit influence is obstructed by a counter-placed planet from Janma Rashi.",
    source_reference="Phaladeepika Ch. 26",
))


# ---------------------------------------------------------------------------
# Evaluator Engine
# ---------------------------------------------------------------------------

def evaluate_timing_rules(
    ctx: dict,
    timing_ctx: dict,
    profile: str = "parashari",
) -> Dict[str, Any]:
    """
    Evaluate timing rules across Dasha, Transit, Ashtakavarga, and Vedha families.

    Returns:
        Structured evidence ledger, family scores, and contributing rule IDs.
    """
    evidence_ledger: List[Dict[str, Any]] = []
    seen_dedupe_keys: set[str] = set()

    family_scores = {
        "dasha": 0.50,
        "transit": 0.50,
        "ashtakavarga": 0.50,
        "vedha": 0.50,
        "double_transit": 0.50,
    }

    for rule in TIMING_RULES_CATALOG:
        if not rule.enabled:
            continue
        if rule.dedupe_key and rule.dedupe_key in seen_dedupe_keys:
            continue

        passed, reason, planets = rule.predicate(ctx, timing_ctx)
        if not passed:
            continue

        # Check ordered exceptions
        exc_triggered = False
        exc_reason = ""
        for exc in rule.ordered_exceptions:
            exc_hit, exc_msg = exc(ctx, timing_ctx)
            if exc_hit:
                exc_triggered = True
                exc_reason = exc_msg
                break

        if exc_triggered:
            evidence_ledger.append({
                "rule_id": rule.rule_id,
                "version": rule.version,
                "family": rule.family,
                "effect": "EXCEPTION",
                "exception_reason": exc_reason,
                "confidence": rule.confidence,
                "source_reference": rule.source_reference,
            })
            if rule.dedupe_key:
                seen_dedupe_keys.add(rule.dedupe_key)
            continue

        if rule.dedupe_key:
            seen_dedupe_keys.add(rule.dedupe_key)

        evidence_ledger.append({
            "rule_id": rule.rule_id,
            "version": rule.version,
            "family": rule.family,
            "effect": rule.effect,
            "reason": reason,
            "planets": planets,
            "confidence": rule.confidence,
            "birth_time_sensitive": rule.birth_time_sensitive,
            "source_reference": rule.source_reference,
        })

        delta = 0.12 if rule.effect == "SUPPORTS" else (-0.12 if rule.effect == "OBSTRUCTS" else 0.05)
        fam = rule.family
        if fam in family_scores:
            family_scores[fam] = max(0.10, min(0.95, family_scores[fam] + delta))

    return {
        "evidence_ledger": evidence_ledger,
        "family_scores": family_scores,
        "active_rules_count": len([e for e in evidence_ledger if e["effect"] in ("SUPPORTS", "OBSTRUCTS", "CONDITIONAL")]),
        "safety_disclaimer": TIMING_SAFETY_DISCLAIMER,
    }
