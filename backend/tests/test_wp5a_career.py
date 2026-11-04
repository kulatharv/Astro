"""
WP5A Career Domain Rule Pack Test Suite.

Validates:
- Positive, negative, boundary, and exception conditions for all 24 canonical career rules
- Jaimini Amatyakaraka calculation
- D10 Dashamsha division calculation
- Multi-frame cross readings (Chandra Lagna, Surya Lagna, D10)
- Exception ordering and cancellation (Neecha Bhanga, Papa Kartari relief)
- Determinism and explanation provenance
- Missing or incomplete data handling
- Backward compatibility with legacy analyse_career() API
"""

import pytest
import copy

from shared.veda.career import (
    CAREER_RULES_CATALOG,
    evaluate_career_rules,
    calculate_amatyakaraka,
    calculate_dashamsha_d10,
    get_planet_aspects_to_house,
)
from modules.prediction.domains.career import analyse_career


# ---------------------------------------------------------------------------
# Synthetic Fixture Generators
# ---------------------------------------------------------------------------

def create_base_ctx(lagna="Mesha"):
    """
    Creates a neutral baseline chart context for Mesha Lagna:
    Houses:
    1: Mesha (Mars)
    2: Vrishabha (Venus)
    3: Mithuna (Mercury)
    4: Karka (Moon)
    5: Simha (Sun)
    6: Kanya (Mercury)
    7: Tula (Venus)
    8: Vrischika (Mars)
    9: Dhanu (Jupiter)
    10: Makara (Saturn)
    11: Kumbha (Saturn)
    12: Meena (Jupiter)
    """
    RASHI = ["Mesha", "Vrishabha", "Mithuna", "Karka", "Simha", "Kanya",
             "Tula", "Vrischika", "Dhanu", "Makara", "Kumbha", "Meena"]
    SIGN_LORDS = {
        "Mesha": "Mars", "Vrishabha": "Venus", "Mithuna": "Mercury", "Karka": "Moon",
        "Simha": "Sun", "Kanya": "Mercury", "Tula": "Venus", "Vrischika": "Mars",
        "Dhanu": "Jupiter", "Makara": "Saturn", "Kumbha": "Saturn", "Meena": "Jupiter"
    }
    lagna_idx = RASHI.index(lagna)
    house_signs = {h: RASHI[(lagna_idx + h - 1) % 12] for h in range(1, 13)}
    house_lords = {h: SIGN_LORDS[house_signs[h]] for h in range(1, 13)}

    # Default neutral placement: each planet in its own house or neutral
    planet_map = {
        "Sun":     {"sign": "Simha",     "house": 5, "degree": 12.0, "retrograde": False, "str_score": 2, "strength": "Own Sign"},
        "Moon":    {"sign": "Karka",     "house": 4, "degree": 14.0, "retrograde": False, "str_score": 2, "strength": "Own Sign"},
        "Mars":    {"sign": "Mesha",     "house": 1, "degree": 18.0, "retrograde": False, "str_score": 2, "strength": "Own Sign"},
        "Mercury": {"sign": "Mithuna",   "house": 3, "degree": 8.0,  "retrograde": False, "str_score": 2, "strength": "Own Sign"},
        "Jupiter": {"sign": "Dhanu",     "house": 9, "degree": 22.0, "retrograde": False, "str_score": 2, "strength": "Own Sign"},
        "Venus":   {"sign": "Vrishabha", "house": 2, "degree": 6.0,  "retrograde": False, "str_score": 2, "strength": "Own Sign"},
        "Saturn":  {"sign": "Kumbha",    "house": 11, "degree": 15.0, "retrograde": False, "str_score": 2, "strength": "Own Sign"},
        "Rahu":    {"sign": "Vrishabha", "house": 2, "degree": 4.0,  "retrograde": True,  "str_score": 0, "strength": "Neutral"},
        "Ketu":    {"sign": "Vrischika", "house": 8, "degree": 4.0,  "retrograde": True,  "str_score": 0, "strength": "Neutral"},
    }

    return {
        "lagna": lagna,
        "lagna_idx": lagna_idx,
        "house_signs": house_signs,
        "house_lords": house_lords,
        "planet_map": planet_map,
        "mahadasha": "Jupiter",
        "antardasha": "Sun",
        "transit_map": {p: {"house": d["house"], "sign": d["sign"]} for p, d in planet_map.items()},
        "yogas": [],
        "doshas": [],
    }



# ---------------------------------------------------------------------------
# Test Rule Catalog Structure
# ---------------------------------------------------------------------------

def test_rule_catalog_structure():
    """Verify that all rules conform to canonical schema with required fields."""
    assert len(CAREER_RULES_CATALOG) == 24
    rule_ids = set()
    for rule in CAREER_RULES_CATALOG:
        assert rule.rule_id not in rule_ids, f"Duplicate rule_id: {rule.rule_id}"
        rule_ids.add(rule.rule_id)
        assert rule.domain == "career"
        assert rule.profile in ("parashari", "jaimini")
        assert rule.chart_frame in ("D1", "Chandra_Lagna", "Surya_Lagna", "D10")
        assert rule.effect in ("SUPPORTS", "OBSTRUCTS", "CONDITIONAL")
        assert rule.source_status == "VERIFIED"
        assert rule.source_reference != ""
        assert rule.confidence in ("HIGH", "MEDIUM", "LOW, needs expert check")
        assert callable(rule.predicate)


# ---------------------------------------------------------------------------
# Tests: Rule 1 & 2 — 10th Lord in Kendra & Trikona
# ---------------------------------------------------------------------------

def test_h10_lord_kendra():
    # Mesha Lagna: 10th house is Makara, ruled by Saturn
    ctx = create_base_ctx("Mesha")
    # Put Saturn in House 1 (Kendra)
    ctx["planet_map"]["Saturn"]["house"] = 1
    ctx["planet_map"]["Saturn"]["sign"] = "Tula"  # Exalted
    res = evaluate_career_rules(ctx)
    fired_ids = [r["rule_id"] for r in res["matched_rules"]]
    assert "CAREER-H10-LORD-KENDRA-01" in fired_ids


def test_h10_lord_kendra_exception_debilitated():
    # If 10th lord is in Kendra but debilitated without Neecha Bhanga, exception fires
    ctx = create_base_ctx("Mesha")
    # Saturn in Mesha (House 1, Kendra, but Debilitated)
    ctx["planet_map"]["Saturn"]["house"] = 1
    ctx["planet_map"]["Saturn"]["sign"] = "Mesha"
    ctx["planet_map"]["Saturn"]["retrograde"] = False
    # Dispositor Mars in 6th, Moon in 2nd, Exaltation lord Venus in 3rd (no Kendra)
    ctx["planet_map"]["Mars"]["house"] = 6
    ctx["planet_map"]["Moon"]["house"] = 2
    ctx["planet_map"]["Venus"]["house"] = 3
    res = evaluate_career_rules(ctx)
    fired_ids = [r["rule_id"] for r in res["matched_rules"]]
    rejected_ids = [r["rule_id"] for r in res["rejected_rules"]]
    assert "CAREER-H10-LORD-KENDRA-01" in rejected_ids
    assert "CAREER-H10-LORD-KENDRA-01" not in fired_ids


def test_h10_lord_trikona():
    ctx = create_base_ctx("Mesha")
    # Saturn in 9th house (Dhanu - Trikona)
    ctx["planet_map"]["Saturn"]["house"] = 9
    ctx["planet_map"]["Saturn"]["sign"] = "Dhanu"
    res = evaluate_career_rules(ctx)
    fired_ids = [r["rule_id"] for r in res["matched_rules"]]
    assert "CAREER-H10-LORD-TRIKONA-02" in fired_ids


# ---------------------------------------------------------------------------
# Tests: Rule 3 — 10th Lord in Dusthana & Exceptions
# ---------------------------------------------------------------------------

def test_h10_lord_dusthana():
    ctx = create_base_ctx("Mesha")
    # Saturn in 8th house (Vrischika - Dusthana)
    ctx["planet_map"]["Saturn"]["house"] = 8
    ctx["planet_map"]["Saturn"]["sign"] = "Vrischika"
    res = evaluate_career_rules(ctx)
    fired_ids = [r["rule_id"] for r in res["matched_rules"]]
    assert "CAREER-H10-LORD-DUSTHANA-03" in fired_ids


def test_h10_lord_dusthana_exception_exalted():
    # If 10th lord in 6th but exalted (e.g. Taurus Lagna: 10th lord is Saturn in 6th Libra exalted)
    ctx = create_base_ctx("Vrishabha")
    # 10th house is Kumbha, ruled by Saturn
    ctx["planet_map"]["Saturn"]["house"] = 6
    ctx["planet_map"]["Saturn"]["sign"] = "Tula"  # Exalted in 6th
    res = evaluate_career_rules(ctx)
    rejected_ids = [r["rule_id"] for r in res["rejected_rules"]]
    assert "CAREER-H10-LORD-DUSTHANA-03" in rejected_ids


# ---------------------------------------------------------------------------
# Tests: Rule 4 & 5 — 10th Lord Exalted / Own / Debilitated
# ---------------------------------------------------------------------------

def test_h10_lord_exalted_own():
    ctx = create_base_ctx("Mesha")
    # 10th lord Saturn in Tula (Exalted)
    ctx["planet_map"]["Saturn"]["sign"] = "Tula"
    res = evaluate_career_rules(ctx)
    fired_ids = [r["rule_id"] for r in res["matched_rules"]]
    assert "CAREER-H10-LORD-EXALTED-OWN-04" in fired_ids


def test_h10_lord_debilitated_and_cancellation():
    ctx = create_base_ctx("Mesha")
    # 10th lord Saturn in Mesha (Debilitated)
    ctx["planet_map"]["Saturn"]["sign"] = "Mesha"
    ctx["planet_map"]["Saturn"]["house"] = 1
    # Test case A: No cancellation (Moon=2, Mars=6, Venus=3)
    ctx["planet_map"]["Saturn"]["retrograde"] = False
    ctx["planet_map"]["Mars"]["house"] = 6
    ctx["planet_map"]["Moon"]["house"] = 2
    ctx["planet_map"]["Venus"]["house"] = 3
    res = evaluate_career_rules(ctx)
    fired_ids = [r["rule_id"] for r in res["matched_rules"]]
    assert "CAREER-H10-LORD-DEBILITATED-05" in fired_ids

    # Test case B: Debilitation cancelled by Retrograde (Neecha Bhanga)
    ctx["planet_map"]["Saturn"]["retrograde"] = True
    res_nb = evaluate_career_rules(ctx)
    rejected_ids = [r["rule_id"] for r in res_nb["rejected_rules"]]
    assert "CAREER-H10-LORD-DEBILITATED-05" in rejected_ids



# ---------------------------------------------------------------------------
# Tests: Rule 6 & 7 — Amala Yoga & Malefic Upachaya
# ---------------------------------------------------------------------------

def test_amala_benefic_yoga():
    ctx = create_base_ctx("Mesha")
    # Put Jupiter in 10th house, no malefics in 10th
    ctx["planet_map"]["Jupiter"]["house"] = 10
    ctx["planet_map"]["Saturn"]["house"] = 11
    ctx["planet_map"]["Sun"]["house"] = 5
    ctx["planet_map"]["Mars"]["house"] = 1
    res = evaluate_career_rules(ctx)
    fired_ids = [r["rule_id"] for r in res["matched_rules"]]
    assert "CAREER-H10-AMALA-BENEFIC-06" in fired_ids


def test_amala_negative_when_malefic_present():
    ctx = create_base_ctx("Mesha")
    # Jupiter and Saturn both in 10th -> Not unblemished Amala
    ctx["planet_map"]["Jupiter"]["house"] = 10
    ctx["planet_map"]["Saturn"]["house"] = 10
    res = evaluate_career_rules(ctx)
    fired_ids = [r["rule_id"] for r in res["matched_rules"]]
    assert "CAREER-H10-AMALA-BENEFIC-06" not in fired_ids
    assert "CAREER-H10-UPACHAYA-MALEFIC-07" in fired_ids


# ---------------------------------------------------------------------------
# Tests: Rules 8 to 12 — Individual Planets in 10th
# ---------------------------------------------------------------------------

def test_sun_digbala_in_10th():
    ctx = create_base_ctx("Mesha")
    ctx["planet_map"]["Sun"]["house"] = 10
    ctx["planet_map"]["Sun"]["sign"] = "Makara"
    res = evaluate_career_rules(ctx)
    fired_ids = [r["rule_id"] for r in res["matched_rules"]]
    assert "CAREER-H10-SUN-DIGBALA-08" in fired_ids


def test_mars_kuladeepaka_in_10th():
    ctx = create_base_ctx("Mesha")
    ctx["planet_map"]["Mars"]["house"] = 10
    ctx["planet_map"]["Mars"]["sign"] = "Makara"  # Exalted Dig Bala
    res = evaluate_career_rules(ctx)
    fired_ids = [r["rule_id"] for r in res["matched_rules"]]
    assert "CAREER-H10-MARS-KULADEEPAKA-09" in fired_ids


def test_saturn_in_10th():
    ctx = create_base_ctx("Mesha")
    ctx["planet_map"]["Saturn"]["house"] = 10
    ctx["planet_map"]["Saturn"]["sign"] = "Makara"
    res = evaluate_career_rules(ctx)
    fired_ids = [r["rule_id"] for r in res["matched_rules"]]
    assert "CAREER-H10-SATURN-SERVICE-10" in fired_ids


def test_mercury_in_10th():
    ctx = create_base_ctx("Mesha")
    ctx["planet_map"]["Mercury"]["house"] = 10
    ctx["planet_map"]["Mercury"]["sign"] = "Makara"
    res = evaluate_career_rules(ctx)
    fired_ids = [r["rule_id"] for r in res["matched_rules"]]
    assert "CAREER-H10-MERCURY-COMMERCE-11" in fired_ids


def test_jupiter_in_10th():
    ctx = create_base_ctx("Mesha")
    ctx["planet_map"]["Jupiter"]["house"] = 10
    ctx["planet_map"]["Jupiter"]["sign"] = "Dhanu"
    res = evaluate_career_rules(ctx)
    fired_ids = [r["rule_id"] for r in res["matched_rules"]]
    assert "CAREER-H10-JUPITER-ADVISORY-12" in fired_ids


# ---------------------------------------------------------------------------
# Tests: Rule 13 — Papa Kartari to 10th House
# ---------------------------------------------------------------------------

def test_papakartari_10th():
    ctx = create_base_ctx("Mesha")
    # Sun in 9th, Mars in 11th, no benefics in 10th
    ctx["planet_map"]["Sun"]["house"] = 9
    ctx["planet_map"]["Mars"]["house"] = 11
    ctx["planet_map"]["Jupiter"]["house"] = 1
    ctx["planet_map"]["Venus"]["house"] = 2
    ctx["planet_map"]["Mercury"]["house"] = 3
    # Empty 10th
    ctx["planet_map"]["Saturn"]["house"] = 4
    res = evaluate_career_rules(ctx)
    fired_ids = [r["rule_id"] for r in res["matched_rules"]]
    assert "CAREER-H10-PAPAKARTARI-13" in fired_ids


def test_papakartari_relief_by_benefic():
    ctx = create_base_ctx("Mesha")
    # Malefics in 9 and 11, but Jupiter also in 9th relieving it
    ctx["planet_map"]["Sun"]["house"] = 9
    ctx["planet_map"]["Jupiter"]["house"] = 9
    ctx["planet_map"]["Mars"]["house"] = 11
    res = evaluate_career_rules(ctx)
    rejected_ids = [r["rule_id"] for r in res["rejected_rules"]]
    assert "CAREER-H10-PAPAKARTARI-13" in rejected_ids


# ---------------------------------------------------------------------------
# Tests: Rules 14 to 18 — Supporting Houses (6th, 2nd, 11th, 5th, Lagna)
# ---------------------------------------------------------------------------

def test_h6_service_alignment():
    ctx = create_base_ctx("Mesha")
    # 6th lord Mercury in 10th house
    ctx["planet_map"]["Mercury"]["house"] = 10
    res = evaluate_career_rules(ctx)
    fired_ids = [r["rule_id"] for r in res["matched_rules"]]
    assert "CAREER-H6-SERVICE-ALIGNMENT-14" in fired_ids


def test_h2_h11_artha_connection():
    ctx = create_base_ctx("Mesha")
    # 2nd lord Venus in 10th house
    ctx["planet_map"]["Venus"]["house"] = 10
    res = evaluate_career_rules(ctx)
    fired_ids = [r["rule_id"] for r in res["matched_rules"]]
    assert "CAREER-H2-H11-ARTHA-CONNECTION-15" in fired_ids


def test_h5_intellect_alignment():
    ctx = create_base_ctx("Mesha")
    # 5th lord Sun in 10th house
    ctx["planet_map"]["Sun"]["house"] = 10
    res = evaluate_career_rules(ctx)
    fired_ids = [r["rule_id"] for r in res["matched_rules"]]
    assert "CAREER-H5-INTELLECT-ALIGNMENT-16" in fired_ids


def test_dharma_karma_yoga():
    ctx = create_base_ctx("Mesha")
    # 9th lord Jupiter and 10th lord Saturn conjoined in 10th house
    ctx["planet_map"]["Jupiter"]["house"] = 10
    ctx["planet_map"]["Saturn"]["house"] = 10
    res = evaluate_career_rules(ctx)
    fired_ids = [r["rule_id"] for r in res["matched_rules"]]
    assert "CAREER-DHARMA-KARMA-YOGA-17" in fired_ids


def test_lagna_lord_in_10th():
    ctx = create_base_ctx("Mesha")
    # Lagna lord Mars in 10th house
    ctx["planet_map"]["Mars"]["house"] = 10
    res = evaluate_career_rules(ctx)
    fired_ids = [r["rule_id"] for r in res["matched_rules"]]
    assert "CAREER-LAGNA-LORD-10TH-18" in fired_ids


# ---------------------------------------------------------------------------
# Tests: Rules 19 & 20 — Chandra Lagna and Surya Lagna Cross-Readings
# ---------------------------------------------------------------------------

def test_chandra_lagna_h10():
    ctx = create_base_ctx("Mesha")
    # Moon in house 1. 10th from Moon is house 10. Put Jupiter in house 10.
    ctx["planet_map"]["Moon"]["house"] = 1
    ctx["planet_map"]["Jupiter"]["house"] = 10
    res = evaluate_career_rules(ctx)
    fired_ids = [r["rule_id"] for r in res["matched_rules"]]
    assert "CAREER-CHANDRA-LAGNA-H10-19" in fired_ids


def test_surya_lagna_h10():
    ctx = create_base_ctx("Mesha")
    # Sun in house 3. 10th from Sun is house 12. Put Mars in house 12.
    ctx["planet_map"]["Sun"]["house"] = 3
    ctx["planet_map"]["Mars"]["house"] = 12
    res = evaluate_career_rules(ctx)
    fired_ids = [r["rule_id"] for r in res["matched_rules"]]
    assert "CAREER-SURYA-LAGNA-H10-20" in fired_ids


# ---------------------------------------------------------------------------
# Tests: Jaimini Amatyakaraka (AmK) Calculation and Rules 21 & 22
# ---------------------------------------------------------------------------

def test_calculate_amatyakaraka():
    # Construct distinct degrees
    pmap = {
        "Sun":     {"degree": 28.5},  # Highest -> Atmakaraka (AK)
        "Moon":    {"degree": 25.1},  # 2nd Highest -> Amatyakaraka (AmK)
        "Mars":    {"degree": 21.0},
        "Mercury": {"degree": 14.2},
        "Jupiter": {"degree": 11.0},
        "Venus":   {"degree": 8.0},
        "Saturn":  {"degree": 3.0},
    }
    amk, deg = calculate_amatyakaraka(pmap)
    assert amk == "Moon"
    assert round(deg, 1) == 25.1


def test_jaimini_amk_kendra_and_dusthana():
    ctx = create_base_ctx("Mesha")
    # Sun 28° (AK), Jupiter 24° (AmK)
    ctx["planet_map"]["Sun"]["degree"] = 28.0
    ctx["planet_map"]["Jupiter"]["degree"] = 24.0
    ctx["planet_map"]["Mars"]["degree"] = 18.0
    ctx["planet_map"]["Moon"]["degree"] = 15.0
    ctx["planet_map"]["Mercury"]["degree"] = 12.0
    ctx["planet_map"]["Venus"]["degree"] = 8.0
    ctx["planet_map"]["Saturn"]["degree"] = 2.0

    # Test AmK in Kendra (House 4)
    ctx["planet_map"]["Jupiter"]["house"] = 4
    res = evaluate_career_rules(ctx)
    fired_ids = [r["rule_id"] for r in res["matched_rules"]]
    assert "CAREER-JAIMINI-AMATYAKARAKA-KENDRA-21" in fired_ids
    assert "CAREER-JAIMINI-AMATYAKARAKA-DUSTHANA-22" not in fired_ids

    # Test AmK in Dusthana (House 6 without dignity)
    ctx["planet_map"]["Jupiter"]["house"] = 6
    ctx["planet_map"]["Jupiter"]["sign"] = "Kanya"  # Enemy sign
    res2 = evaluate_career_rules(ctx)
    fired_ids2 = [r["rule_id"] for r in res2["matched_rules"]]
    assert "CAREER-JAIMINI-AMATYAKARAKA-DUSTHANA-22" in fired_ids2


# ---------------------------------------------------------------------------
# Tests: Rule 23 — D10 Dashamsha Division Calculation & Rule
# ---------------------------------------------------------------------------

def test_calculate_dashamsha_d10():
    # Odd sign: Mesha (index 0). 0-3 deg = Mesha, 3-6 deg = Vrishabha, 27-30 deg = Makara
    assert calculate_dashamsha_d10("Mesha", 1.5) == "Mesha"
    assert calculate_dashamsha_d10("Mesha", 4.0) == "Vrishabha"
    assert calculate_dashamsha_d10("Mesha", 28.5) == "Makara"

    # Even sign: Vrishabha (index 1). Starts from 9th from Vrishabha = Makara
    # 0-3 deg = Makara, 3-6 deg = Kumbha
    assert calculate_dashamsha_d10("Vrishabha", 1.0) == "Makara"
    assert calculate_dashamsha_d10("Vrishabha", 4.5) == "Kumbha"


def test_d10_dashamsha_rule():
    ctx = create_base_ctx("Mesha")
    # 10th lord Saturn in Vrishabha at 1.0 deg -> D10 is Makara (Saturn's own sign!)
    ctx["planet_map"]["Saturn"]["sign"] = "Vrishabha"
    ctx["planet_map"]["Saturn"]["degree"] = 1.0
    res = evaluate_career_rules(ctx)
    fired_ids = [r["rule_id"] for r in res["matched_rules"]]
    assert "CAREER-D10-DASHAMSHA-10TH-LORD-23" in fired_ids


# ---------------------------------------------------------------------------
# Tests: Rule 24 — Timing / Dasha Activation
# ---------------------------------------------------------------------------

def test_timing_dasha_activation():
    ctx = create_base_ctx("Mesha")
    # 10th lord is Saturn. Set Mahadasha to Saturn.
    ctx["mahadasha"] = "Saturn"
    ctx["antardasha"] = "Venus"
    res = evaluate_career_rules(ctx)
    fired_ids = [r["rule_id"] for r in res["matched_rules"]]
    assert "CAREER-TIMING-DASHA-ACTIVATION-24" in fired_ids


# ---------------------------------------------------------------------------
# Tests: Missing Data, Determinism & API Compatibility
# ---------------------------------------------------------------------------

def test_missing_and_incomplete_chart_data():
    """Engine should handle empty or partially populated contexts safely."""
    empty_ctx = {}
    res = evaluate_career_rules(empty_ctx)
    assert res["domain"] == "career"
    assert res["score"] >= 25
    assert isinstance(res["matched_rules"], list)
    assert isinstance(res["rejected_rules"], list)


def test_deterministic_reproducibility():
    """Repeated runs on identical inputs must yield strictly identical results."""
    ctx = create_base_ctx("Mesha")
    res1 = evaluate_career_rules(ctx)
    res2 = evaluate_career_rules(ctx)
    assert res1 == res2


def test_backward_compatibility_analyse_career():
    """Ensure legacy analyse_career() returns all legacy keys plus enriched evidence."""
    ctx = create_base_ctx("Mesha")
    res = analyse_career(ctx)

    # Legacy required keys
    expected_legacy_keys = [
        "domain", "icon", "score", "sector", "best_fields",
        "tenth_lord", "h10_planets", "raj_yogas", "business_vs_job",
        "foreign_work", "dasha_active", "timing", "remedies", "analysis"
    ]
    for key in expected_legacy_keys:
        assert key in res, f"Missing legacy key: {key}"

    # New WP5A evidence keys
    assert "evidence" in res
    assert "rules_evaluated" in res
    assert res["rules_evaluated"] >= 0
    assert "matched_rules" in res["evidence"]
    assert "primary_archetypes" in res["evidence"]
