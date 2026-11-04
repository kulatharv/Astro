"""
WP5B Marriage & Relationship Domain Rule Pack Test Suite.

Validates:
- Positive, negative, boundary, and exception conditions for canonical marriage rules
- Venus and Jupiter separate evidence paths
- D1 vs D9 Navamsa frame isolation
- Multi-frame Mangal Dosha integration and classical cancellations
- Multi-frame Chandra Lagna and Venus Frame cross-readings
- Exception ordering and cancellation (Neecha Bhanga, Papa Kartari relief, Mangal cancellations)
- Determinism and explanation provenance
- Missing or incomplete data handling
- Backward compatibility with legacy analyse_marriage() API
- Safety guardrails (no deterministic fatalism, guaranteed divorce, infidelity, or spouse death)
- Pending Jaimini dependencies (Upapada Lagna, Darakaraka)
"""

import pytest
import copy

from shared.veda.marriage import (
    MARRIAGE_RULES_CATALOG,
    evaluate_marriage_rules,
    calculate_d9_navamsa_sign,
    get_planet_aspects_to_house,
)
from modules.prediction.domains.marriage import analyse_marriage


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

    # Default neutral placement
    planet_map = {
        "Sun":     {"sign": "Simha",     "house": 5,  "degree": 12.0, "retrograde": False, "str_score": 2, "strength": "Own Sign"},
        "Moon":    {"sign": "Karka",     "house": 4,  "degree": 14.0, "retrograde": False, "str_score": 2, "strength": "Own Sign"},
        "Mars":    {"sign": "Mesha",     "house": 1,  "degree": 18.0, "retrograde": False, "str_score": 2, "strength": "Own Sign"},
        "Mercury": {"sign": "Mithuna",   "house": 3,  "degree": 8.0,  "retrograde": False, "str_score": 2, "strength": "Own Sign"},
        "Jupiter": {"sign": "Dhanu",     "house": 9,  "degree": 22.0, "retrograde": False, "str_score": 2, "strength": "Own Sign"},
        "Venus":   {"sign": "Vrishabha", "house": 2,  "degree": 6.0,  "retrograde": False, "str_score": 2, "strength": "Own Sign"},
        "Saturn":  {"sign": "Kumbha",    "house": 11, "degree": 15.0, "retrograde": False, "str_score": 2, "strength": "Own Sign"},
        "Rahu":    {"sign": "Vrishabha", "house": 2,  "degree": 4.0,  "retrograde": True,  "str_score": 0, "strength": "Neutral"},
        "Ketu":    {"sign": "Vrischika", "house": 8,  "degree": 4.0,  "retrograde": True,  "str_score": 0, "strength": "Neutral"},
    }

    return {
        "lagna": lagna,
        "lagna_idx": lagna_idx,
        "lagna_degree": 15.0,
        "house_signs": house_signs,
        "house_lords": house_lords,
        "planet_map": planet_map,
        "mahadasha": "Jupiter",
        "antardasha": "Venus",
        "transit_map": {p: {"house": d["house"], "sign": d["sign"]} for p, d in planet_map.items()},
        "yogas": [],
        "doshas": [],
    }


# ---------------------------------------------------------------------------
# Test Rule Catalog Structure & Pending Dependencies
# ---------------------------------------------------------------------------

def test_marriage_rule_catalog_structure():
    """Verify that all rules conform to canonical schema with required fields."""
    assert len(MARRIAGE_RULES_CATALOG) == 26
    rule_ids = set()
    enabled_count = 0
    pending_count = 0

    for rule in MARRIAGE_RULES_CATALOG:
        assert rule.rule_id not in rule_ids, f"Duplicate rule_id: {rule.rule_id}"
        rule_ids.add(rule.rule_id)
        assert rule.domain == "marriage"
        assert rule.profile in ("parashari", "jaimini")
        assert rule.chart_frame in ("D1", "Chandra_Lagna", "Venus_Frame", "D9")
        assert rule.effect in ("SUPPORTS", "OBSTRUCTS", "CONDITIONAL")
        assert callable(rule.predicate)

        if rule.enabled_by_default:
            enabled_count += 1
            assert rule.source_status == "VERIFIED"
            assert rule.review_status == "ACCEPTED"
        else:
            pending_count += 1
            assert rule.review_status == "PENDING_WP7_DEPENDENCY"
            assert rule.source_status == "SOURCE VERIFICATION REQUIRED"

    assert enabled_count == 24
    assert pending_count == 2


# ---------------------------------------------------------------------------
# Tests: Rule 1 & 2 — 7th Lord in Kendra & Trikona
# ---------------------------------------------------------------------------

def test_h7_lord_kendra():
    # Mesha Lagna: 7th house is Tula, ruled by Venus
    ctx = create_base_ctx("Mesha")
    # Put Venus in House 4 (Karka - Kendra)
    ctx["planet_map"]["Venus"]["house"] = 4
    ctx["planet_map"]["Venus"]["sign"] = "Karka"
    res = evaluate_marriage_rules(ctx)
    fired_ids = [r["rule_id"] for r in res["matched_rules"]]
    assert "MARRIAGE-H7-LORD-KENDRA-01" in fired_ids


def test_h7_lord_kendra_exception_debilitated():
    # Venus in Kanya (House 6 in Aries Lagna, but let's test a Kendra placement with debility)
    # Mithuna Lagna: 7th house is Dhanu (Jupiter). Put Jupiter in 10th (Meena) vs 8th (Makara)
    # Simha Lagna: 7th house is Kumbha (Saturn). Put Saturn in 10th Taurus vs 1st Leo
    # Karka Lagna: 7th house is Makara (Saturn). Put Saturn in 10th Mesha (Debilitated Kendra!)
    ctx = create_base_ctx("Karka")
    # 7th lord is Saturn. In 10th house (Mesha), Debilitated
    ctx["planet_map"]["Saturn"]["house"] = 10
    ctx["planet_map"]["Saturn"]["sign"] = "Mesha"
    ctx["planet_map"]["Saturn"]["retrograde"] = False
    # No Neecha Bhanga (Dispositor Mars in 6th, Moon in 2nd, Exaltation lord Venus in 3rd)
    ctx["planet_map"]["Mars"]["house"] = 6
    ctx["planet_map"]["Moon"]["house"] = 2
    ctx["planet_map"]["Venus"]["house"] = 3
    res = evaluate_marriage_rules(ctx)
    fired_ids = [r["rule_id"] for r in res["matched_rules"]]
    rejected_ids = [r["rule_id"] for r in res["rejected_rules"]]
    assert "MARRIAGE-H7-LORD-KENDRA-01" in rejected_ids
    assert "MARRIAGE-H7-LORD-KENDRA-01" not in fired_ids


def test_h7_lord_trikona():
    ctx = create_base_ctx("Mesha")
    # Venus in 5th house (Simha - Trikona)
    ctx["planet_map"]["Venus"]["house"] = 5
    ctx["planet_map"]["Venus"]["sign"] = "Simha"
    res = evaluate_marriage_rules(ctx)
    fired_ids = [r["rule_id"] for r in res["matched_rules"]]
    assert "MARRIAGE-H7-LORD-TRIKONA-02" in fired_ids


# ---------------------------------------------------------------------------
# Tests: Rule 3 — 7th Lord in Dusthana & Exceptions
# ---------------------------------------------------------------------------

def test_h7_lord_dusthana():
    ctx = create_base_ctx("Mesha")
    # 7th lord Venus in 6th house (Kanya - Dusthana)
    ctx["planet_map"]["Venus"]["house"] = 6
    ctx["planet_map"]["Venus"]["sign"] = "Kanya"
    res = evaluate_marriage_rules(ctx)
    fired_ids = [r["rule_id"] for r in res["matched_rules"]]
    assert "MARRIAGE-H7-LORD-DUSTHANA-03" in fired_ids


def test_h7_lord_dusthana_exception_exalted():
    # Leo Lagna: 7th house is Kumbha (Saturn). Saturn in 6th (Makara - Own Sign!)
    ctx = create_base_ctx("Simha")
    # 7th lord Saturn in 6th Makara (own sign Dusthana)
    ctx["planet_map"]["Saturn"]["house"] = 6
    ctx["planet_map"]["Saturn"]["sign"] = "Makara"
    res = evaluate_marriage_rules(ctx)
    rejected_ids = [r["rule_id"] for r in res["rejected_rules"]]
    assert "MARRIAGE-H7-LORD-DUSTHANA-03" in rejected_ids


# ---------------------------------------------------------------------------
# Tests: Rule 4 & 5 — 7th Lord Exalted / Own / Debilitated
# ---------------------------------------------------------------------------

def test_h7_lord_exalted_own():
    ctx = create_base_ctx("Mesha")
    # 7th lord Venus in Meena (Exalted)
    ctx["planet_map"]["Venus"]["sign"] = "Meena"
    res = evaluate_marriage_rules(ctx)
    fired_ids = [r["rule_id"] for r in res["matched_rules"]]
    assert "MARRIAGE-H7-LORD-EXALTED-OWN-04" in fired_ids


def test_h7_lord_debilitated_and_cancellation():
    ctx = create_base_ctx("Mesha")
    # 7th lord Venus in Kanya (Debilitated)
    ctx["planet_map"]["Venus"]["sign"] = "Kanya"
    ctx["planet_map"]["Venus"]["house"] = 6
    ctx["planet_map"]["Venus"]["retrograde"] = False
    # No Neecha Bhanga
    ctx["planet_map"]["Mercury"]["house"] = 6
    ctx["planet_map"]["Moon"]["house"] = 2  # Moon in 2nd
    # Test A: Uncancelled
    res = evaluate_marriage_rules(ctx)
    fired_ids = [r["rule_id"] for r in res["matched_rules"]]
    assert "MARRIAGE-H7-LORD-DEBILITATED-05" in fired_ids

    # Test B: Debilitation cancelled by Retrograde (Neecha Bhanga)
    ctx["planet_map"]["Venus"]["retrograde"] = True
    res_nb = evaluate_marriage_rules(ctx)
    rejected_ids = [r["rule_id"] for r in res_nb["rejected_rules"]]
    assert "MARRIAGE-H7-LORD-DEBILITATED-05" in rejected_ids


# ---------------------------------------------------------------------------
# Tests: Rule 6 & 7 — Benefics vs Malefics in 7th House
# ---------------------------------------------------------------------------

def test_h7_benefic_occupation():
    ctx = create_base_ctx("Mesha")
    # Jupiter and Mercury in 7th, no malefics
    ctx["planet_map"]["Jupiter"]["house"] = 7
    ctx["planet_map"]["Mercury"]["house"] = 7
    ctx["planet_map"]["Mars"]["house"] = 1
    ctx["planet_map"]["Saturn"]["house"] = 11
    ctx["planet_map"]["Sun"]["house"] = 5
    res = evaluate_marriage_rules(ctx)
    fired_ids = [r["rule_id"] for r in res["matched_rules"]]
    assert "MARRIAGE-H7-BENEFIC-OCCUPATION-06" in fired_ids
    assert "MARRIAGE-H7-MALEFIC-OCCUPATION-07" not in fired_ids


def test_h7_malefic_occupation():
    ctx = create_base_ctx("Mesha")
    # Saturn in 7th house
    ctx["planet_map"]["Saturn"]["house"] = 7
    ctx["planet_map"]["Saturn"]["sign"] = "Kanya"  # Not exalted or own
    res = evaluate_marriage_rules(ctx)
    fired_ids = [r["rule_id"] for r in res["matched_rules"]]
    assert "MARRIAGE-H7-MALEFIC-OCCUPATION-07" in fired_ids


# ---------------------------------------------------------------------------
# Tests: Rule 8 — Papa Kartari to 7th House
# ---------------------------------------------------------------------------

def test_h7_papakartari():
    ctx = create_base_ctx("Mesha")
    # Malefics in 6th and 8th, empty 7th
    ctx["planet_map"]["Mars"]["house"] = 6
    ctx["planet_map"]["Saturn"]["house"] = 8
    # No planets in 7th
    ctx["planet_map"]["Venus"]["house"] = 2
    ctx["planet_map"]["Jupiter"]["house"] = 9
    ctx["planet_map"]["Mercury"]["house"] = 3
    res = evaluate_marriage_rules(ctx)
    fired_ids = [r["rule_id"] for r in res["matched_rules"]]
    assert "MARRIAGE-H7-PAPAKARTARI-08" in fired_ids


def test_h7_papakartari_benefic_relief():
    ctx = create_base_ctx("Mesha")
    # Malefics in 6th and 8th, but Jupiter also in 6th relieving it
    ctx["planet_map"]["Mars"]["house"] = 6
    ctx["planet_map"]["Jupiter"]["house"] = 6
    ctx["planet_map"]["Saturn"]["house"] = 8
    res = evaluate_marriage_rules(ctx)
    rejected_ids = [r["rule_id"] for r in res["rejected_rules"]]
    assert "MARRIAGE-H7-PAPAKARTARI-08" in rejected_ids


# ---------------------------------------------------------------------------
# Tests: Rules 9 to 13 — Venus and Jupiter Separate Evidence
# ---------------------------------------------------------------------------

def test_venus_dignity_and_debility():
    ctx = create_base_ctx("Mesha")
    # Exalted Venus
    ctx["planet_map"]["Venus"]["sign"] = "Meena"
    res = evaluate_marriage_rules(ctx)
    fired_ids = [r["rule_id"] for r in res["matched_rules"]]
    assert "MARRIAGE-KARAKA-VENUS-DIGNITY-09" in fired_ids
    assert "MARRIAGE-KARAKA-VENUS-DEBILITATED-10" not in fired_ids


def test_venus_combustion():
    ctx = create_base_ctx("Mesha")
    # Sun and Venus in same sign within 5°
    ctx["planet_map"]["Sun"]["sign"] = "Simha"
    ctx["planet_map"]["Sun"]["degree"] = 10.0
    ctx["planet_map"]["Venus"]["sign"] = "Simha"
    ctx["planet_map"]["Venus"]["degree"] = 13.5
    res = evaluate_marriage_rules(ctx)
    fired_ids = [r["rule_id"] for r in res["matched_rules"]]
    assert "MARRIAGE-KARAKA-VENUS-COMBUST-11" in fired_ids


def test_jupiter_benefic_influence():
    ctx = create_base_ctx("Mesha")
    # Jupiter in 9th casting 9th aspect or in 7th
    ctx["planet_map"]["Jupiter"]["house"] = 7
    res = evaluate_marriage_rules(ctx)
    fired_ids = [r["rule_id"] for r in res["matched_rules"]]
    assert "MARRIAGE-KARAKA-JUPITER-BENEFIC-12" in fired_ids


# ---------------------------------------------------------------------------
# Tests: Rules 14 to 17 — Supporting Houses (2nd, 5th, 11th, Lagna Lord)
# ---------------------------------------------------------------------------

def test_h2_kutumba_connection():
    ctx = create_base_ctx("Mesha")
    # 7th lord Venus in 2nd house
    ctx["planet_map"]["Venus"]["house"] = 2
    res = evaluate_marriage_rules(ctx)
    fired_ids = [r["rule_id"] for r in res["matched_rules"]]
    assert "MARRIAGE-H2-KUTUMBA-CONNECTION-14" in fired_ids


def test_h5_romance_alignment():
    ctx = create_base_ctx("Mesha")
    # 5th lord Sun in 7th house
    ctx["planet_map"]["Sun"]["house"] = 7
    res = evaluate_marriage_rules(ctx)
    fired_ids = [r["rule_id"] for r in res["matched_rules"]]
    assert "MARRIAGE-H5-ROMANCE-ALIGNMENT-15" in fired_ids


def test_h11_fulfillment_alignment():
    ctx = create_base_ctx("Mesha")
    # 11th lord Saturn in 7th house
    ctx["planet_map"]["Saturn"]["house"] = 7
    res = evaluate_marriage_rules(ctx)
    fired_ids = [r["rule_id"] for r in res["matched_rules"]]
    assert "MARRIAGE-H11-FULFILLMENT-ALIGNMENT-16" in fired_ids


def test_lagna_lord_7th_lord_sambhandha():
    ctx = create_base_ctx("Mesha")
    # Lagna lord Mars and 7th lord Venus conjoined in 1st house
    ctx["planet_map"]["Mars"]["house"] = 1
    ctx["planet_map"]["Venus"]["house"] = 1
    res = evaluate_marriage_rules(ctx)
    fired_ids = [r["rule_id"] for r in res["matched_rules"]]
    assert "MARRIAGE-LAGNA-LORD-7TH-LORD-17" in fired_ids


# ---------------------------------------------------------------------------
# Tests: Rules 18 to 20 — Multi-Frame Cross-Readings (Moon & Venus)
# ---------------------------------------------------------------------------

def test_chandra_lagna_h7_benefic():
    ctx = create_base_ctx("Mesha")
    # Moon in house 1. 7th from Moon is house 7. Put Jupiter in house 7.
    ctx["planet_map"]["Moon"]["house"] = 1
    ctx["planet_map"]["Jupiter"]["house"] = 7
    res = evaluate_marriage_rules(ctx)
    fired_ids = [r["rule_id"] for r in res["matched_rules"]]
    assert "MARRIAGE-CHANDRA-LAGNA-H7-18" in fired_ids


def test_venus_frame_h7():
    ctx = create_base_ctx("Mesha")
    # Venus in house 2. 7th from Venus is house 8. Put Jupiter in house 8.
    ctx["planet_map"]["Venus"]["house"] = 2
    ctx["planet_map"]["Jupiter"]["house"] = 8
    res = evaluate_marriage_rules(ctx)
    fired_ids = [r["rule_id"] for r in res["matched_rules"]]
    assert "MARRIAGE-VENUS-FRAME-H7-20" in fired_ids


# ---------------------------------------------------------------------------
# Tests: Rules 21 & 22 — D9 Navamsa Calculations and Rules
# ---------------------------------------------------------------------------

def test_calculate_d9_navamsa_sign():
    # Mesha 10° -> Karka (Pada 3 = index 3)
    assert calculate_d9_navamsa_sign("Mesha", 10.0) == "Karka"
    # Vrishabha 1° -> Makara (starts from Makara = 9)
    assert calculate_d9_navamsa_sign("Vrishabha", 1.0) == "Makara"
    # Tula 28° -> Mithuna
    assert calculate_d9_navamsa_sign("Tula", 28.0) == "Mithuna"


def test_d9_7th_lord_dignity_rule():
    ctx = create_base_ctx("Mesha")
    # 7th lord Venus in Vrishabha at 1.0 deg -> D9 is Makara
    # In Vrishabha at 25.0 deg -> D9 is Kanya (Debilitated)
    # In Meena at 2.0 deg -> Water sign starts Karka. 2 deg = Pada 0 = Karka.
    # In Meena at 28.0 deg -> Pada 8 = Meena (Vargottama / Own sign in D9!)
    ctx["planet_map"]["Venus"]["sign"] = "Meena"
    ctx["planet_map"]["Venus"]["degree"] = 28.0
    res = evaluate_marriage_rules(ctx)
    fired_ids = [r["rule_id"] for r in res["matched_rules"]]
    assert "MARRIAGE-D9-7TH-LORD-DIGNITY-21" in fired_ids


# ---------------------------------------------------------------------------
# Tests: Rule 23 — Multi-Frame Mangal Dosha & Cancellations
# ---------------------------------------------------------------------------

def test_mangal_dosha_multiframe_and_cancellation():
    # Test A: Uncancelled Mangal Dosha
    # Tula Lagna, Mars in 8th (Vrishabha), Moon & Venus in 3rd, Jupiter in 6th (no aspect, no friendly sign)
    ctx_tula = create_base_ctx("Tula")
    ctx_tula["planet_map"]["Mars"]["house"] = 8
    ctx_tula["planet_map"]["Mars"]["sign"] = "Vrishabha"
    ctx_tula["planet_map"]["Moon"]["house"] = 3
    ctx_tula["planet_map"]["Venus"]["house"] = 3
    ctx_tula["planet_map"]["Jupiter"]["house"] = 6  # 3rd from Mars -> no aspect

    res = evaluate_marriage_rules(ctx_tula)
    fired_ids = [r["rule_id"] for r in res["matched_rules"]]
    assert "MARRIAGE-MANGAL-DOSHA-MULTIFRAME-23" in fired_ids

    # Test B: Cancelled Mangal Dosha (Mars in 7th in Makara is classically cancelled by exaltation)
    ctx_canc = create_base_ctx("Karka")
    ctx_canc["planet_map"]["Mars"]["house"] = 7
    ctx_canc["planet_map"]["Mars"]["sign"] = "Makara"
    ctx_canc["planet_map"]["Moon"]["house"] = 3
    ctx_canc["planet_map"]["Venus"]["house"] = 3
    res_canc = evaluate_marriage_rules(ctx_canc)
    rejected_ids = [r["rule_id"] for r in res_canc["rejected_rules"]]
    assert "MARRIAGE-MANGAL-DOSHA-MULTIFRAME-23" in rejected_ids




# ---------------------------------------------------------------------------
# Tests: Rule 24 — Timing / Dasha Activation
# ---------------------------------------------------------------------------

def test_marriage_timing_dasha_activation():
    ctx = create_base_ctx("Mesha")
    # 7th lord is Venus. Set Mahadasha to Venus.
    ctx["mahadasha"] = "Venus"
    ctx["antardasha"] = "Jupiter"
    res = evaluate_marriage_rules(ctx)
    fired_ids = [r["rule_id"] for r in res["matched_rules"]]
    assert "MARRIAGE-TIMING-DASHA-ACTIVATION-24" in fired_ids


# ---------------------------------------------------------------------------
# Tests: Safety Guardrails (Non-Fatalistic Language)
# ---------------------------------------------------------------------------

def test_safety_non_fatalistic_language():
    """Verify that no fatalistic, coercive, or defamatory claims are emitted."""
    ctx = create_base_ctx("Mesha")
    res = analyse_marriage(ctx)

    analysis_text = res["analysis"].lower()
    prohibited_terms = [
        "guaranteed divorce",
        "will divorce",
        "will separate permanently",
        "adultery",
        "unfaithful",
        "infidelity guaranteed",
        "death of spouse",
        "infertile",
        "barren",
    ]
    for term in prohibited_terms:
        assert term not in analysis_text, f"Prohibited deterministic term '{term}' found in narrative!"


# ---------------------------------------------------------------------------
# Tests: Missing Data, Determinism & API Compatibility
# ---------------------------------------------------------------------------

def test_missing_and_incomplete_chart_data():
    """Engine should handle empty or partially populated contexts safely."""
    empty_ctx = {}
    res = evaluate_marriage_rules(empty_ctx)
    assert res["domain"] == "marriage"
    assert res["score"] >= 25
    assert isinstance(res["matched_rules"], list)
    assert isinstance(res["rejected_rules"], list)


def test_deterministic_reproducibility():
    """Repeated runs on identical inputs must yield strictly identical results."""
    ctx = create_base_ctx("Mesha")
    res1 = evaluate_marriage_rules(ctx)
    res2 = evaluate_marriage_rules(ctx)
    assert res1 == res2


def test_backward_compatibility_analyse_marriage():
    """Ensure legacy analyse_marriage() returns all legacy keys plus enriched evidence."""
    ctx = create_base_ctx("Mesha")
    res = analyse_marriage(ctx)

    expected_legacy_keys = [
        "domain", "icon", "score", "marriage_type", "partner_traits",
        "partner_sign", "mangal_dosh", "mangal_dosh_txt", "kalatra_yoga",
        "second_marriage", "intimacy", "venus_position", "seventh_lord",
        "h7_planets", "dasha_active", "timing", "remedies", "analysis"
    ]
    for key in expected_legacy_keys:
        assert key in res, f"Missing legacy key: {key}"

    # New WP5B evidence keys
    assert "evidence" in res
    assert "rules_evaluated" in res
    assert res["rules_evaluated"] >= 0
    assert "matched_rules" in res["evidence"]
    assert "primary_archetypes" in res["evidence"]
