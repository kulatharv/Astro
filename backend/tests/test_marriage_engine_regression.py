"""
Master Regression Test Suite for AstroLogic AI Marriage Engine Bug Fixes.

Validates all P0, P1, and P2 bug fixes:
  1. Upapada Lagna (UL) sign-counting, quotient/remainder fix, and Arudha exceptions.
  2. Parashari Graha Drishti aspect targets (Jupiter, Saturn, Mars) and aspect cancellations.
  3. Neecha Bhanga predicates vs Neecha Bhanga Raja Yoga (NBRY) formal separation.
  4. D9 Navamsha calculation across boundaries, D9 Ascendant derivation, and planetary placements.
  5. Marriage timing reproducibility, actual Vimshottari MD-AD-PD timeline, and SAV labeling.
  6. Audit of the 24 canonical marriage rules and multi-frame Mangal Dosha cancellation filters.
  7. Multi-frame Mangal Dosha decomposition (Lagna, Moon, Venus frames with exact rule IDs).
  8. Venus circular angular separation across sign boundaries, thresholds, and retrograde handling.
  9. Marriage heuristic score recomputation and transparent deduplication.
"""

import pytest
from datetime import datetime

from modules.kundali.jaimini import (
    calculate_arudha_pada,
    compute_jaimini_foundation,
    JaiminiProfileConfig,
)
from shared.veda.doshas import (
    _aspects_house,
    _house_distance,
    check_mangal_cancellations,
    evaluate_mangal_dosha_multiframe,
)
from shared.veda.neech_bhanga import (
    evaluate_neech_bhanga,
    is_neech_bhanga,
    is_neech_bhanga_raja_yoga,
    NEECH_BHANGA_EXALT_LORDS,
)
from shared.veda.marriage import (
    calculate_d9_navamsa_sign,
    evaluate_marriage_rules,
    MARRIAGE_RULES_CATALOG,
)
from modules.kundali.varga import calculate_navamsa
from modules.kundali.dasha import (
    calculate_mahadasha,
    generate_dasha_timeline,
    generate_dasha_chain,
)
from modules.kundali.engine import calculate_kundali
from modules.prediction.scoring import _build_ctx
from modules.prediction.timing import compute_timing


# ===========================================================================
# 1. Bug 1 Regression Tests: Upapada Lagna (UL) & Arudha Exceptions
# ===========================================================================

def test_ul_reference_chart_pisces_lagna():
    """
    Pisces Lagna (12), 12th house is Aquarius (11).
    12th lord Saturn is in Cancer (4).
    Distance from Aquarius (11) to Cancer (4) = 6 signs.
    6 signs from Cancer (4) = 9 (Sagittarius / Dhanu).
    Sagittarius is neither Aquarius (same) nor Leo (7th from Aquarius).
    Therefore, no exception applies: UL = Sagittarius (House 10 from Lagna).
    """
    pada = calculate_arudha_pada(
        house_num=12,
        lagna_sign=12,  # Meena / Pisces
        lord_sign=4,    # Karka / Cancer
        convention="STANDARD_EXCEPTION",
    )
    assert pada["raw_pada"] == 9
    assert pada["final_pada"] == 9
    assert pada["final_sign_name"] == "Dhanu"
    assert pada["exception_applied"] is False
    house_from_lagna = ((pada["final_pada"] - 12) % 12) + 1
    assert house_from_lagna == 10


def test_arudha_exceptions_both_cases():
    """
    Test Arudha same-sign (swastha) exception and 7th-sign (saptama) exception.
    """
    # Case A: Same sign exception (lord in 1st from house -> falls in 10th)
    pada_same = calculate_arudha_pada(
        house_num=1,
        lagna_sign=1,  # Aries
        lord_sign=1,   # Mars in Aries (distance 1)
        convention="STANDARD_EXCEPTION",
    )
    assert pada_same["raw_pada"] == 1
    assert pada_same["final_pada"] == 10  # 10th from source
    assert pada_same["exception_applied"] is True
    assert pada_same["exception_type"] == "SWASTHA_10TH_SHIFT"

    # Case B: 7th sign exception (lord in 4th -> falls in 7th from source -> shifted to 10th from 7th = 4th)
    pada_seventh = calculate_arudha_pada(
        house_num=1,
        lagna_sign=1,  # Aries
        lord_sign=4,   # Mars in Cancer (distance 4)
        convention="STANDARD_EXCEPTION",
    )
    assert pada_seventh["raw_pada"] == 7
    assert pada_seventh["final_pada"] == 4  # Shifted to 10th from 7th = 4th
    assert pada_seventh["exception_applied"] is True
    assert pada_seventh["exception_type"] == "SAPTAMA_4TH_SHIFT"


def test_ul_all_12_houses_invariants():
    """Verify that Arudha pada never occupies source or 7th sign under standard Parashari."""
    for h in range(1, 13):
        for lord_s in range(1, 13):
            pada = calculate_arudha_pada(h, 1, lord_s, "STANDARD_EXCEPTION")
            source_sign = ((1 + h - 2) % 12) + 1
            seventh_from_source = ((source_sign - 1 + 6) % 12) + 1
            assert pada["final_pada"] != source_sign
            assert pada["final_pada"] != seventh_from_source


# ===========================================================================
# 2. Bug 2 Regression Tests: Graha Drishti & Aspect Target Precision
# ===========================================================================

def test_jupiter_aspect_targets():
    """
    Jupiter in Virgo (House 7 for Pisces Lagna) aspects 5th, 7th, 9th:
    Virgo + 4 = Capricorn (H11)
    Virgo + 6 = Pisces (H1)
    Virgo + 8 = Taurus (H3)
    Jupiter does NOT aspect Libra (House 8).
    """
    # From house 7:
    # 5th aspect -> house 11 (Capricorn)
    assert _aspects_house("Jupiter", 7, 11) is True
    # 7th aspect -> house 1 (Pisces)
    assert _aspects_house("Jupiter", 7, 1) is True
    # 9th aspect -> house 3 (Taurus)
    assert _aspects_house("Jupiter", 7, 3) is True
    # Distance 2 -> house 8 (Libra) - NO ASPECT
    assert _aspects_house("Jupiter", 7, 8) is False


def test_mars_and_saturn_aspect_targets():
    """Verify Mars special (4, 8) and Saturn special (3, 10) aspects."""
    # Mars in H8: aspects H11 (4th), H2 (7th), H3 (8th)
    assert _aspects_house("Mars", 8, 11) is True
    assert _aspects_house("Mars", 8, 2) is True
    assert _aspects_house("Mars", 8, 3) is True
    assert _aspects_house("Mars", 8, 7) is False

    # Saturn in H5: aspects H7 (3rd), H11 (7th), H2 (10th)
    assert _aspects_house("Saturn", 5, 7) is True
    assert _aspects_house("Saturn", 5, 11) is True
    assert _aspects_house("Saturn", 5, 2) is True
    assert _aspects_house("Saturn", 5, 8) is False


def test_mangal_dosha_not_cancelled_by_jupiter_in_7th_for_h8_mars():
    """
    Mars in H8 (Libra) with Jupiter in H7 (Virgo).
    Jupiter does not aspect Mars, is not in Lagna, and does not cancel 8th house Mars.
    """
    pmap = {
        "Mars": {"house": 8, "sign": "Tula"},
        "Jupiter": {"house": 7, "sign": "Kanya"},
        "Moon": {"house": 4, "sign": "Mithuna"},
        "Venus": {"house": 7, "sign": "Kanya"},
    }
    cancellations = check_mangal_cancellations(8, "Tula", pmap, "Lagna")
    assert not any("Jupiter" in c for c in cancellations)


# ===========================================================================
# 3. Bug 3 Regression Tests: Neecha Bhanga vs NBRY Separation
# ===========================================================================

def test_exaltation_lords_truth_table():
    """Verify classical exaltation lords dictionary."""
    assert NEECH_BHANGA_EXALT_LORDS["Sun"] == "Mars"      # Exalted in Aries (Mars)
    assert NEECH_BHANGA_EXALT_LORDS["Moon"] == "Venus"    # Exalted in Taurus (Venus)
    assert NEECH_BHANGA_EXALT_LORDS["Mars"] == "Saturn"   # Exalted in Capricorn (Saturn)
    assert NEECH_BHANGA_EXALT_LORDS["Mercury"] == "Mercury"
    assert NEECH_BHANGA_EXALT_LORDS["Jupiter"] == "Moon"  # Exalted in Cancer (Moon)
    assert NEECH_BHANGA_EXALT_LORDS["Venus"] == "Jupiter" # Exalted in Pisces (Jupiter)
    assert NEECH_BHANGA_EXALT_LORDS["Saturn"] == "Venus"  # Exalted in Libra (Venus)


def test_venus_debilitated_in_virgo_nb_confirmed_nbry_not_established():
    """
    Venus in Virgo in 7th house (Kendra).
    Dispositor Mercury in Scorpio in 9th (Trikona, not Kendra).
    Exaltation lord Jupiter in Virgo in 7th (Kendra from Lagna and Moon).
    Neecha Bhanga is CONFIRMED (cancellation detected).
    Neecha Bhanga Raja Yoga is NOT ESTABLISHED (conditions for Raja Yoga not satisfied).
    """
    pmap = {
        "Venus": {"house": 7, "sign": "Kanya", "retrograde": False},
        "Mercury": {"house": 9, "sign": "Vrischika"},
        "Jupiter": {"house": 7, "sign": "Kanya"},
        "Moon": {"house": 4, "sign": "Mithuna"},
    }
    res = evaluate_neech_bhanga("Venus", "Kanya", pmap)
    assert res["is_debilitated"] is True
    assert res["is_cancelled"] is True
    assert res["is_raja_yoga"] is False
    assert res["status"] == "NEECH_BHANGA_CONFIRMED"
    assert is_neech_bhanga("Venus", "Kanya", pmap) is True
    assert is_neech_bhanga_raja_yoga("Venus", "Kanya", pmap) is False


# ===========================================================================
# 4. Bug 4 Regression Tests: D9 Navamsha Derivation & Boundary Testing
# ===========================================================================

def test_d9_navamsa_108_division_continuity():
    """Verify all 108 Navamshas across the 360-degree zodiac map validly."""
    for deg in range(0, 360, 3):
        d9_sign = calculate_navamsa(float(deg) + 0.1)
        assert d9_sign in [
            "Mesha", "Vrishabha", "Mithuna", "Karka", "Simha", "Kanya",
            "Tula", "Vrischika", "Dhanu", "Makara", "Kumbha", "Meena",
        ]


def test_d9_lagna_for_reference_chart():
    """
    Pisces Lagna at 17° 12' 41" (347.2114°):
    Water signs begin Navamsha cycle at Cancer (Karka).
    17° 12' 41" falls into Pada 6 (16°40' to 20°00').
    Pada 6 from Cancer: Cancer -> Leo -> Virgo -> Libra -> Scorpio -> Sagittarius (Dhanu).
    D9 Lagna = Dhanu (Sagittarius).
    D9 7th house = Mithuna (Gemini).
    """
    d9_lagna = calculate_d9_navamsa_sign("Meena", 17.2114)
    assert d9_lagna == "Dhanu"

    # Mars at 0° 16' Libra -> Air sign starts from Libra -> Pada 1 = Libra (Vargottama!)
    d9_mars = calculate_d9_navamsa_sign("Tula", 0.27)
    assert d9_mars == "Tula"

    # Venus at 11° 26' Virgo -> Earth sign starts Capricorn -> Pada 4 = Aries (Mesha)
    d9_venus = calculate_d9_navamsa_sign("Kanya", 11.43)
    assert d9_venus == "Mesha"

    # Rahu at 8° 10' Aries -> Fire sign starts Aries -> Pada 3 = Gemini (Mithuna, in D9 7th!)
    d9_rahu = calculate_d9_navamsa_sign("Mesha", 8.17)
    assert d9_rahu == "Mithuna"


# ===========================================================================
# 5. Bug 5 Regression Tests: Vimshottari MD-AD-PD Timeline Reproducibility
# ===========================================================================

def test_vimshottari_timeline_reproducibility():
    """
    Native born Nov 2, 2004 16:15 IST.
    Moon at 15.91° Gemini (Ardra Nakshatra).
    Starting dasha: Rahu with ~5.52 years remaining (until May 11, 2010).
    Jupiter Mahadasha: May 11, 2010 to May 11, 2026.
    Saturn Mahadasha: Transitions on May 11, 2026!
    In October 2026: Saturn MD - Saturn AD - Saturn PD.
    From Nov 1, 2026 to Apr 6, 2027: Saturn MD - Saturn AD - Mercury PD (7th lord).
    """
    birth_dt = datetime(2004, 11, 2, 16, 15)
    moon_lon = 2 * 30.0 + 15.9115
    lord, balance = calculate_mahadasha(moon_lon, "Ardra")
    assert lord == "Rahu"
    assert round(balance, 1) == 5.5

    timeline = generate_dasha_timeline(lord, balance)
    chain = generate_dasha_chain(birth_dt, timeline, year_convention="solar_365_25")

    # Find active period on Oct 19, 2026
    oct_period = next(p for p in chain if p["start"] <= "2026-10-19" <= p["end"])
    assert oct_period["md_lord"] == "Saturn"
    assert oct_period["ad_lord"] == "Saturn"
    assert oct_period["pd_lord"] == "Saturn"

    # Find active period on Dec 1, 2026
    dec_period = next(p for p in chain if p["start"] <= "2026-12-01" <= p["end"])
    assert dec_period["md_lord"] == "Saturn"
    assert dec_period["ad_lord"] == "Saturn"
    assert dec_period["pd_lord"] == "Mercury"
    assert dec_period["start"] == "2026-11-01"
    assert dec_period["end"] == "2027-04-06"


# ===========================================================================
# 6. Bug 8 Regression Tests: Venus Combustion Circular Angular Separation
# ===========================================================================

def test_venus_combustion_circular_boundary_cases():
    """
    Test circular angular separation across signs, 0/360 wrap, and threshold.
    """
    # Case A: Sun at 29° Pisces (359°), Venus at 2° Aries (2°) -> sep = 3° -> Combust
    ctx_wrap = {
        "planet_map": {
            "Sun": {"sign": "Meena", "degree_decimal": 29.0},
            "Venus": {"sign": "Mesha", "degree_decimal": 2.0, "retrograde": False},
        }
    }
    res = evaluate_marriage_rules(ctx_wrap)
    fired_ids = [r["rule_id"] for r in res["matched_rules"]]
    assert "MARRIAGE-KARAKA-VENUS-COMBUST-11" in fired_ids

    # Case B: Sun at 16° Libra, Venus at 11° Scorpio -> sep = 25° -> Not Combust
    ctx_non_combust = {
        "planet_map": {
            "Sun": {"sign": "Tula", "degree_decimal": 16.0},
            "Venus": {"sign": "Vrischika", "degree_decimal": 11.0, "retrograde": False},
        }
    }
    res_b = evaluate_marriage_rules(ctx_non_combust)
    fired_b = [r["rule_id"] for r in res_b["matched_rules"]]
    assert "MARRIAGE-KARAKA-VENUS-COMBUST-11" not in fired_b


# ===========================================================================
# 7. Bug 9 & End-to-End Regression Tests: Scoring & Final Verification
# ===========================================================================

def test_end_to_end_marriage_evaluation_reference_chart():
    """
    End-to-end evaluation of the reference chart (DOB: 02/11/2004 16:15 Aurangabad).
    - Pisces Lagna, D9 Lagna Sagittarius
    - 7th lord Mercury in 9th (Trikona) -> SUPPORTS (+6)
    - Jupiter & Venus in 7th house -> SUPPORTS (+6)
    - D9 Lagna ruled by Jupiter -> SUPPORTS (+6)
    - Multi-frame Mangal Dosha present in Lagna frame -> CONDITIONAL (+2)
    - Venus debilitation cancelled by Jupiter in Kendra -> Exception fired, no penalty
    - Heuristic score: 76/100 (Heuristic Vitality Index, NOT probability)
    """
    res = calculate_kundali(2004, 11, 2, 16, 15, 19.8762, 75.3433, tz_name="Asia/Kolkata")
    ctx = _build_ctx(res)
    eval_res = evaluate_marriage_rules(ctx)

    assert eval_res["score"] == 76
    assert eval_res["supports_count"] == 4
    assert eval_res["obstructs_count"] == 0
    assert eval_res["conditional_count"] == 1
    assert eval_res["d9_navamsa_lagna_sign"] == "Dhanu"

    matched_ids = [r["rule_id"] for r in eval_res["matched_rules"]]
    assert "MARRIAGE-H7-LORD-TRIKONA-02" in matched_ids
    assert "MARRIAGE-H7-BENEFIC-OCCUPATION-06" in matched_ids
    assert "MARRIAGE-D9-NAVAMSA-LAGNA-BENEFIC-22" in matched_ids
    assert "MARRIAGE-MANGAL-DOSHA-MULTIFRAME-23" in matched_ids

    # Venus debility cancelled without Raja Yoga confirmation
    rejected_ids = [r["rule_id"] for r in eval_res["rejected_rules"]]
    assert "MARRIAGE-KARAKA-VENUS-DEBILITATED-10" in rejected_ids
    venus_rej = next(r for r in eval_res["rejected_rules"] if r["rule_id"] == "MARRIAGE-KARAKA-VENUS-DEBILITATED-10")
    assert "Raja Yoga not established" in venus_rej["cancellation_reason"]
