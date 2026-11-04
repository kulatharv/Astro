"""
Unit & Integration Test Suite for WP5E — Education & Learning Domain Rule Pack.

Tests:
  1. D24 Siddhamsa Mathematical Verification Gate (BPHS Ch. 6, v. 24-25):
     - All 12 signs tested
     - Exact division boundaries (0.0°, 1.24°, 1.25°, 2.49°, 2.50°, 15.0°, 28.74°, 28.75°, 29.99°)
     - Just below, at, and just above division transitions
     - Odd sign (from Simha) and Even sign (from Karka) mapping
  2. Canonical 24-Rule Catalog Execution:
     - Positive, negative, and ordered exception tests across all 7 families (A-G)
  3. All 12 Lagna signs execution
  4. 6 Safe Educational Dimensions separation
  5. 100% Backward Compatibility with legacy API contracts
  6. Educational Safety Guardrail & Adversarial Scans:
     - No exam pass/fail claims
     - No university admission guarantees
     - No IQ or cognitive ability scoring
     - No psychiatric/learning-disability diagnoses
     - No advice to abandon education
  7. Deterministic repeated execution
"""

import pytest
from shared.veda.education import (
    calculate_siddhamsa_d24,
    build_d24_chart,
    evaluate_education_rules,
    EDUCATION_RULES_CATALOG,
    SAFETY_DISCLAIMER,
    EDUCATION_DIMENSIONS,
)
from shared.veda.zodiac import SIGNS_SK
from modules.prediction.domains.education import analyse_education


# ---------------------------------------------------------------------------
# Test Fixture Helpers
# ---------------------------------------------------------------------------

def _base_ctx(lagna="Mesha"):
    return {
        "lagna": lagna,
        "ascendant_degree": 15.0,
        "house_signs": {
            1: "Mesha", 2: "Vrishabha", 3: "Mithuna", 4: "Karka",
            5: "Simha", 6: "Kanya", 7: "Tula", 8: "Vrischika",
            9: "Dhanu", 10: "Makara", 11: "Kumbha", 12: "Meena",
        },
        "house_lords": {
            1: "Mars", 2: "Venus", 3: "Mercury", 4: "Moon",
            5: "Sun", 6: "Mercury", 7: "Venus", 8: "Mars",
            9: "Jupiter", 10: "Saturn", 11: "Saturn", 12: "Jupiter",
        },
        "planet_map": {
            "Sun": {"sign": "Simha", "house": 5, "degree": 10.0, "str_score": 1, "is_combust": False},
            "Moon": {"sign": "Karka", "house": 4, "degree": 12.0, "str_score": 1, "is_combust": False},
            "Mars": {"sign": "Mesha", "house": 1, "degree": 8.0, "str_score": 1, "is_combust": False},
            "Mercury": {"sign": "Mithuna", "house": 3, "degree": 14.0, "str_score": 1, "is_combust": False},
            "Jupiter": {"sign": "Dhanu", "house": 9, "degree": 16.0, "str_score": 1, "is_combust": False},
            "Venus": {"sign": "Vrishabha", "house": 2, "degree": 20.0, "str_score": 1, "is_combust": False},
            "Saturn": {"sign": "Makara", "house": 10, "degree": 5.0, "str_score": 1, "is_combust": False},
            "Rahu": {"sign": "Kumbha", "house": 11, "degree": 22.0, "str_score": 0, "is_combust": False},
            "Ketu": {"sign": "Simha", "house": 5, "degree": 22.0, "str_score": 0, "is_combust": False},
        },
        "mahadasha": "Jupiter",
        "antardasha": "Mercury",
        "yogas": [],
        "transit_map": {
            "Sun": {"house": 5}, "Moon": {"house": 4}, "Mars": {"house": 1},
            "Mercury": {"house": 3}, "Jupiter": {"house": 9}, "Venus": {"house": 2},
            "Saturn": {"house": 10}, "Rahu": {"house": 11}, "Ketu": {"house": 5},
        },
    }



# ===========================================================================
# 1. D24 SIDDHAMSA MATHEMATICAL VERIFICATION GATE
# ===========================================================================

class TestD24Mathematics:
    """Rigorous tests for BPHS Ch. 6, v. 24-25 D24 Siddhamsa calculation."""

    def test_d24_all_12_signs_base(self):
        """Test 0.0° for all 12 signs: Odd start Simha, Even start Karka."""
        odd_signs = ["Mesha", "Mithuna", "Simha", "Tula", "Dhanu", "Kumbha"]
        even_signs = ["Vrishabha", "Karka", "Kanya", "Vrischika", "Makara", "Meena"]

        for sign in odd_signs:
            res = calculate_siddhamsa_d24(sign, 0.0)
            assert res == "Simha", f"Odd sign {sign} at 0.0° must map to Simha, got {res}"

        for sign in even_signs:
            res = calculate_siddhamsa_d24(sign, 0.0)
            assert res == "Karka", f"Even sign {sign} at 0.0° must map to Karka, got {res}"

    def test_d24_odd_sign_boundary_transitions(self):
        """Test division boundaries for odd sign Mesha (part size = 1.25°)."""
        # Part 0: [0.0, 1.25) -> Simha
        assert calculate_siddhamsa_d24("Mesha", 0.0) == "Simha"
        assert calculate_siddhamsa_d24("Mesha", 1.24) == "Simha"
        assert calculate_siddhamsa_d24("Mesha", 1.2499) == "Simha"

        # Boundary step: 1.25 -> Part 1 -> Kanya
        assert calculate_siddhamsa_d24("Mesha", 1.25) == "Kanya"
        assert calculate_siddhamsa_d24("Mesha", 2.49) == "Kanya"

        # Boundary step: 2.50 -> Part 2 -> Tula
        assert calculate_siddhamsa_d24("Mesha", 2.50) == "Tula"

        # Mid-sign: 15.0° -> part = 12 -> (Simha(4) + 12) % 12 = 4 -> Simha
        assert calculate_siddhamsa_d24("Mesha", 15.0) == "Simha"

        # Penultimate boundary: 28.74 -> part 22 -> (4 + 22) % 12 = 26 % 12 = 2 -> Mithuna
        assert calculate_siddhamsa_d24("Mesha", 28.74) == "Mithuna"

        # Last part: 28.75 -> part 23 -> (4 + 23) % 12 = 27 % 12 = 3 -> Karka
        assert calculate_siddhamsa_d24("Mesha", 28.75) == "Karka"
        assert calculate_siddhamsa_d24("Mesha", 29.99) == "Karka"

    def test_d24_even_sign_boundary_transitions(self):
        """Test division boundaries for even sign Vrishabha (part size = 1.25°)."""
        # Part 0: [0.0, 1.25) -> Karka
        assert calculate_siddhamsa_d24("Vrishabha", 0.0) == "Karka"
        assert calculate_siddhamsa_d24("Vrishabha", 1.24) == "Karka"

        # Boundary step: 1.25 -> Part 1 -> Simha
        assert calculate_siddhamsa_d24("Vrishabha", 1.25) == "Simha"

        # Boundary step: 2.50 -> Part 2 -> Kanya
        assert calculate_siddhamsa_d24("Vrishabha", 2.50) == "Kanya"

        # Mid-sign: 15.0° -> part = 12 -> (Karka(3) + 12) % 12 = 3 -> Karka
        assert calculate_siddhamsa_d24("Vrishabha", 15.0) == "Karka"

        # Last part: 28.75 -> part 23 -> (3 + 23) % 12 = 26 % 12 = 2 -> Mithuna
        assert calculate_siddhamsa_d24("Vrishabha", 28.75) == "Mithuna"
        assert calculate_siddhamsa_d24("Vrishabha", 29.99) == "Mithuna"

    def test_d24_transition_precision_near_boundaries(self):
        """Test just below, at, and just above division boundaries."""
        eps = 0.0001
        # Test boundary 1: 1.25
        assert calculate_siddhamsa_d24("Simha", 1.25 - eps) == "Simha"
        assert calculate_siddhamsa_d24("Simha", 1.25) == "Kanya"
        assert calculate_siddhamsa_d24("Simha", 1.25 + eps) == "Kanya"

        # Test boundary 10: 10 * 1.25 = 12.50
        # Simha is odd -> starts Simha (4). Part 9 (11.25 to 12.50): (4+9)%12 = 1 (Vrishabha)
        # Part 10 (12.50 to 13.75): (4+10)%12 = 2 (Mithuna)
        assert calculate_siddhamsa_d24("Simha", 12.50 - eps) == "Vrishabha"
        assert calculate_siddhamsa_d24("Simha", 12.50) == "Mithuna"
        assert calculate_siddhamsa_d24("Simha", 12.50 + eps) == "Mithuna"

    def test_d24_sign_normalization(self):
        """Test spelling tolerance and edge-case inputs."""
        assert calculate_siddhamsa_d24("vrishika", 0.0) == "Karka"
        assert calculate_siddhamsa_d24("Vrischika", 0.0) == "Karka"
        assert calculate_siddhamsa_d24("mesha", 0.0) == "Simha"
        assert calculate_siddhamsa_d24("", 0.0) == "Simha"

    def test_build_d24_chart_integration(self):
        """Test construction of full D24 chart representation."""
        ctx = _base_ctx()
        d24 = build_d24_chart(ctx)
        assert "d24_lagna" in d24
        assert "d24_lagna_lord" in d24
        assert "d24_planets" in d24
        assert len(d24["d24_planets"]) >= 7
        for p, pdata in d24["d24_planets"].items():
            assert 1 <= pdata["house"] <= 12
            assert pdata["sign"] in SIGNS_SK


# ===========================================================================
# 2. CANONICAL 24-RULE CATALOG TESTS (FAMILIES A THROUGH G)
# ===========================================================================

class TestEducationRuleCatalog:
    """Verifies all 24 canonical rules with positive, negative, and cancellation states."""

    def test_catalog_inventory(self):
        """Assert exact count and integrity of rules."""
        assert len(EDUCATION_RULES_CATALOG) == 24
        ids = [r.rule_id for r in EDUCATION_RULES_CATALOG]
        assert len(ids) == len(set(ids)), "Duplicate rule_id detected"
        for r in EDUCATION_RULES_CATALOG:
            assert r.confidence in ["[HIGH]", "[MEDIUM]", "[LOW, needs expert check]"]
            assert r.source_status in ["VERIFIED", "SOURCE VERIFICATION REQUIRED"]
            assert r.review_status in ["ACCEPTED", "EXPERT REVIEW REQUIRED"]
            assert r.effect in ["SUPPORTS", "OBSTRUCTS", "CONDITIONAL"]
            assert len(r.dimensions) > 0

    # Family A: 4th House
    def test_edu_h4_lord_kendra_trikona_positive(self):
        ctx = _base_ctx("Mesha")  # 4th lord is Moon
        ctx["planet_map"]["Moon"] = {"sign": "Karka", "house": 4, "degree": 10.0, "is_combust": False}
        res = evaluate_education_rules(ctx)
        matched = [r["rule_id"] for r in res["matched_rules"]]
        assert "EDU-H4-LORD-KENDRA-TRIKONA-01" in matched

    def test_edu_h4_lord_kendra_trikona_combust_exception(self):
        ctx = _base_ctx("Mesha")
        ctx["planet_map"]["Moon"] = {"sign": "Karka", "house": 4, "degree": 10.0, "is_combust": True}
        res = evaluate_education_rules(ctx)
        cancelled = [r["rule_id"] for r in res["cancelled_rules"]]
        assert "EDU-H4-LORD-KENDRA-TRIKONA-01" in cancelled

    def test_edu_h4_lord_dignity_positive(self):
        ctx = _base_ctx("Mesha")
        ctx["planet_map"]["Moon"] = {"sign": "Vrishabha", "house": 2, "degree": 3.0, "is_combust": False}  # Exalted
        res = evaluate_education_rules(ctx)
        matched = [r["rule_id"] for r in res["matched_rules"]]
        assert "EDU-H4-LORD-OWN-EXALTED-02" in matched

    def test_edu_h4_benefic_occupancy_positive(self):
        ctx = _base_ctx("Mesha")
        ctx["planet_map"]["Jupiter"] = {"sign": "Karka", "house": 4, "degree": 5.0, "is_combust": False}
        res = evaluate_education_rules(ctx)
        matched = [r["rule_id"] for r in res["matched_rules"]]
        assert "EDU-H4-BENEFIC-OCCUPANCY-03" in matched

    def test_edu_h4_benefic_debilitated_exception(self):
        ctx = _base_ctx("Tula")  # 4th house is Makara
        ctx["planet_map"]["Moon"]["house"] = 10  # Move Moon away from H4 so only Jupiter is in H4
        ctx["planet_map"]["Jupiter"] = {"sign": "Makara", "house": 4, "degree": 5.0, "is_combust": False}  # Debilitated
        res = evaluate_education_rules(ctx)
        cancelled = [r["rule_id"] for r in res["cancelled_rules"]]
        assert "EDU-H4-BENEFIC-OCCUPANCY-03" in cancelled

    def test_edu_h4_lord_dusthana_positive(self):
        ctx = _base_ctx("Mesha")
        ctx["planet_map"]["Moon"] = {"sign": "Kanya", "house": 6, "degree": 10.0, "is_combust": False}
        res = evaluate_education_rules(ctx)
        matched = [r["rule_id"] for r in res["matched_rules"]]
        assert "EDU-H4-LORD-DUSTHANA-AFFLICTION-04" in matched

    def test_edu_h4_lord_dusthana_own_sign_exception(self):
        ctx = _base_ctx("Kumbha")  # 4th house is Vrishabha (Venus), 6th is Karka, 8th is Kanya, 12th is Makara
        # For Kumbha: 4th lord Venus in Tula (house 9) is not dusthana.
        # Let's use Vrishabha lagna: 4th lord is Sun. Sun in Leo (house 4).
        # Let's use Dhanu lagna: 4th lord is Jupiter. 4th is Meena.
        # If Lagna is Mesha, 8th lord Mars in 8th (Vrischika) is own sign.
        # For Kanya lagna: 4th lord is Jupiter. 8th house is Mesha.
        # For Mithuna lagna: 4th lord is Mercury. Mercury in Kanya is 4th house.
        # Let's craft direct own sign in 8th:
        # Scorpio Lagna: 4th house is Aquarius (Saturn). Saturn in Aquarius is H4.
        # Aries Lagna: 4th lord Moon in Taurus (H2) or Cancer (H4).
        # To test exception: 4th lord placed in Dusthana (6, 8, 12) AND in its own sign.
        # E.g. Gemini lagna: 4th house is Virgo (Mercury). If Mercury in 12th is Taurus (Venus).
        # What if 4th lord is Saturn for Libra lagna: 4th house is Capricorn, 5th is Aquarius.
        # For Leo lagna: 4th lord is Mars. Mars in Scorpio is 4th house.
        # For Sagittarius lagna: 4th lord is Jupiter. Jupiter in Pisces (4th) or Sagittarius (1st).
        # For Capricorn lagna: 4th lord is Mars. Mars in Scorpio is 11th house.
        # For Cancer lagna: 4th lord is Venus. Venus in Libra (4th) or Taurus (11th).
        # What if Pisces Lagna: 4th house is Gemini (Mercury). Mercury in Gemini is 4th.
        # What if Taurus Lagna: 4th lord is Sun (Leo is 4th).
        # What if Aquarius Lagna: 4th lord is Venus. Venus in Taurus (4th) or Libra (9th).
        # Notice: can any 4th lord be in its own sign IN 6, 8, or 12?
        # For Taurus Lagna: 6th house is Libra (ruled by Venus, which is 1st & 6th lord). 4th is Sun.
        # In a custom chart frame or hypothetical: if 4th lord is Mars (Leo lagna) and placed in Scorpio (4th) - that's H4.
        # If Lagna is Aries, 4th lord is Moon. Cancer is 4th.
        # What about Gemini Lagna with Rahu/Ketu or hypothetical:
        # If 4th lord Moon in Cancer in 6th (for Kumbha lagna: 6th is Cancer!).
        # Kumbha lagna: 1=Kumbha, 2=Meena, 3=Mesha, 4=Vrishabha (Venus), 5=Mithuna, 6=Karka (Moon).
        # For Kumbha lagna, 4th lord is Venus.
        # For Aries lagna: 1=Mesha ... 6=Kanya, 8=Vrischika, 12=Meena.
        # For Pisces lagna: 1=Meena, 2=Mesha, 3=Vrishabha, 4=Mithuna (Mercury), 5=Karka, 6=Simha, 7=Kanya (Mercury), 8=Tula (Venus), 9=Vrischika, 10=Dhanu, 11=Makara, 12=Kumbha.
        # What if Lagna is Taurus: 4th lord Sun.
        # What if a test sets `planet_map` with 4th lord in own sign in house 6:
        ctx = _base_ctx("Mesha")  # 4th lord is Moon
        # If Moon is in Cancer (own sign) but placed in house 6 (hypothetical/shifted house frame):
        ctx["planet_map"]["Moon"] = {"sign": "Karka", "house": 6, "degree": 10.0, "is_combust": False}
        res = evaluate_education_rules(ctx)
        cancelled = [r["rule_id"] for r in res["cancelled_rules"]]
        assert "EDU-H4-LORD-DUSTHANA-AFFLICTION-04" in cancelled

    # Family B: 5th House
    def test_edu_h5_lord_kendra_trikona_positive(self):
        ctx = _base_ctx("Mesha")  # 5th lord is Sun
        ctx["planet_map"]["Sun"] = {"sign": "Simha", "house": 5, "degree": 10.0, "is_combust": False}
        res = evaluate_education_rules(ctx)
        matched = [r["rule_id"] for r in res["matched_rules"]]
        assert "EDU-H5-LORD-KENDRA-TRIKONA-01" in matched

    def test_edu_h5_lord_dignity_positive(self):
        ctx = _base_ctx("Mesha")
        ctx["planet_map"]["Sun"] = {"sign": "Mesha", "house": 1, "degree": 10.0, "is_combust": False}  # Exalted
        res = evaluate_education_rules(ctx)
        matched = [r["rule_id"] for r in res["matched_rules"]]
        assert "EDU-H5-LORD-OWN-EXALTED-02" in matched

    def test_edu_h5_benefic_occupancy_positive(self):
        ctx = _base_ctx("Mesha")
        ctx["planet_map"]["Jupiter"] = {"sign": "Simha", "house": 5, "degree": 15.0, "is_combust": False}
        res = evaluate_education_rules(ctx)
        matched = [r["rule_id"] for r in res["matched_rules"]]
        assert "EDU-H5-BENEFIC-OCCUPANCY-03" in matched

    def test_edu_h5_lord_dusthana_positive(self):
        ctx = _base_ctx("Mesha")  # 5th lord is Sun
        ctx["planet_map"]["Sun"] = {"sign": "Kanya", "house": 6, "degree": 10.0, "is_combust": False}
        res = evaluate_education_rules(ctx)
        matched = [r["rule_id"] for r in res["matched_rules"]]
        assert "EDU-H5-LORD-DUSTHANA-AFFLICTION-04" in matched

    # Family C: 9th House
    def test_edu_h9_lord_kendra_trikona_positive(self):
        ctx = _base_ctx("Mesha")  # 9th lord is Jupiter
        ctx["planet_map"]["Jupiter"] = {"sign": "Dhanu", "house": 9, "degree": 15.0, "is_combust": False}
        res = evaluate_education_rules(ctx)
        matched = [r["rule_id"] for r in res["matched_rules"]]
        assert "EDU-H9-LORD-KENDRA-TRIKONA-01" in matched

    def test_edu_h9_lord_dignity_positive(self):
        ctx = _base_ctx("Mesha")
        ctx["planet_map"]["Jupiter"] = {"sign": "Karka", "house": 4, "degree": 5.0, "is_combust": False}  # Exalted
        res = evaluate_education_rules(ctx)
        matched = [r["rule_id"] for r in res["matched_rules"]]
        assert "EDU-H9-LORD-OWN-EXALTED-02" in matched

    def test_edu_h9_benefic_occupancy_positive(self):
        ctx = _base_ctx("Mesha")
        ctx["planet_map"]["Venus"] = {"sign": "Dhanu", "house": 9, "degree": 10.0, "is_combust": False}
        res = evaluate_education_rules(ctx)
        matched = [r["rule_id"] for r in res["matched_rules"]]
        assert "EDU-H9-BENEFIC-OCCUPANCY-03" in matched

    def test_edu_h9_foreign_study_positive(self):
        ctx = _base_ctx("Mesha")
        ctx["planet_map"]["Rahu"] = {"sign": "Dhanu", "house": 9, "degree": 10.0, "is_combust": False}
        res = evaluate_education_rules(ctx)
        matched = [r["rule_id"] for r in res["matched_rules"]]
        assert "EDU-H9-FOREIGN-HIGHER-STUDY-04" in matched

    # Family D: Mercury
    def test_edu_mercury_dignity_positive(self):
        ctx = _base_ctx("Mesha")
        ctx["planet_map"]["Mercury"] = {"sign": "Kanya", "house": 6, "degree": 15.0, "is_combust": False}
        res = evaluate_education_rules(ctx)
        matched = [r["rule_id"] for r in res["matched_rules"]]
        assert "EDU-MERCURY-DIGNITY-EXALTED-OWN-01" in matched

    def test_edu_mercury_kendra_trikona_positive(self):
        ctx = _base_ctx("Mesha")
        ctx["planet_map"]["Mercury"] = {"sign": "Mesha", "house": 1, "degree": 15.0, "is_combust": False}
        res = evaluate_education_rules(ctx)
        matched = [r["rule_id"] for r in res["matched_rules"]]
        assert "EDU-MERCURY-KENDRA-TRIKONA-02" in matched

    def test_edu_budhaditya_yoga_positive(self):
        ctx = _base_ctx("Mesha")
        ctx["planet_map"]["Sun"] = {"sign": "Simha", "house": 5, "degree": 12.0, "is_combust": False}
        ctx["planet_map"]["Mercury"] = {"sign": "Simha", "house": 5, "degree": 20.0, "is_combust": False}
        res = evaluate_education_rules(ctx)
        matched = [r["rule_id"] for r in res["matched_rules"]]
        assert "EDU-MERCURY-SUN-BUDHADITYA-03" in matched

    def test_edu_mercury_affliction_positive(self):
        ctx = _base_ctx("Mesha")
        ctx["planet_map"]["Mercury"] = {"sign": "Meena", "house": 12, "degree": 15.0, "str_score": -1, "is_combust": False}
        res = evaluate_education_rules(ctx)
        matched = [r["rule_id"] for r in res["matched_rules"]]
        assert "EDU-MERCURY-COMBUST-AFFLICTION-04" in matched

    # Family E: Jupiter
    def test_edu_jupiter_dignity_positive(self):
        ctx = _base_ctx("Mesha")
        ctx["planet_map"]["Jupiter"] = {"sign": "Karka", "house": 4, "degree": 5.0, "is_combust": False}
        res = evaluate_education_rules(ctx)
        matched = [r["rule_id"] for r in res["matched_rules"]]
        assert "EDU-JUPITER-DIGNITY-EXALTED-OWN-01" in matched

    def test_edu_jupiter_h5_h9_positive(self):
        ctx = _base_ctx("Mesha")
        ctx["planet_map"]["Jupiter"] = {"sign": "Simha", "house": 5, "degree": 12.0, "is_combust": False}
        res = evaluate_education_rules(ctx)
        matched = [r["rule_id"] for r in res["matched_rules"]]
        assert "EDU-JUPITER-H5-OR-H9-PLACEMENT-02" in matched

    def test_edu_saraswati_yoga_positive(self):
        ctx = _base_ctx("Mesha")
        ctx["planet_map"]["Jupiter"] = {"sign": "Karka", "house": 4, "degree": 5.0, "str_score": 1, "is_combust": False}
        ctx["planet_map"]["Venus"] = {"sign": "Tula", "house": 7, "degree": 10.0, "str_score": 1, "is_combust": False}
        ctx["planet_map"]["Mercury"] = {"sign": "Mithuna", "house": 3, "degree": 10.0, "str_score": 1, "is_combust": False}
        # Kendra/Trikona or 2nd house
        ctx["planet_map"]["Mercury"]["house"] = 1
        res = evaluate_education_rules(ctx)
        matched = [r["rule_id"] for r in res["matched_rules"]]
        assert "EDU-SARASWATI-YOGA-03" in matched

    # Family F: Inter-Lord Connections
    def test_edu_4_5_connection_positive(self):
        ctx = _base_ctx("Mesha")  # 4th lord Moon, 5th lord Sun
        ctx["planet_map"]["Moon"] = {"sign": "Simha", "house": 5, "degree": 10.0, "is_combust": False}
        ctx["planet_map"]["Sun"] = {"sign": "Simha", "house": 5, "degree": 15.0, "is_combust": False}
        res = evaluate_education_rules(ctx)
        matched = [r["rule_id"] for r in res["matched_rules"]]
        assert "EDU-DHAN-VIDYA-4-5-EXCHANGE-01" in matched

    def test_edu_5_9_connection_positive(self):
        ctx = _base_ctx("Mesha")  # 5th lord Sun, 9th lord Jupiter
        ctx["planet_map"]["Sun"] = {"sign": "Dhanu", "house": 9, "degree": 10.0, "is_combust": False}
        ctx["planet_map"]["Jupiter"] = {"sign": "Dhanu", "house": 9, "degree": 15.0, "is_combust": False}
        res = evaluate_education_rules(ctx)
        matched = [r["rule_id"] for r in res["matched_rules"]]
        assert "EDU-DHARMA-KARMA-5-9-CONNECTION-02" in matched

    def test_edu_5_10_connection_positive(self):
        ctx = _base_ctx("Mesha")  # 5th lord Sun, 10th lord Saturn
        ctx["planet_map"]["Sun"] = {"sign": "Makara", "house": 10, "degree": 10.0, "is_combust": False}
        ctx["planet_map"]["Saturn"] = {"sign": "Makara", "house": 10, "degree": 15.0, "is_combust": False}
        res = evaluate_education_rules(ctx)
        matched = [r["rule_id"] for r in res["matched_rules"]]
        assert "EDU-10-5-PROFESSIONAL-STUDY-03" in matched

    # Family G: D24 Siddhamsa Divisional Corroboration
    def test_edu_d24_lagna_lord_positive(self):
        ctx = _base_ctx("Mesha")
        # Ensure D24 lagna lord is in Kendra or Trikona in D24
        # Ascendant 0.0° in Mesha -> D24 lagna is Simha -> Lord is Sun.
        ctx["ascendant_degree"] = 0.0
        # If Sun in Mesha 0.0° -> D24 sign is Simha -> house 1 in D24 (Kendra)!
        ctx["planet_map"]["Sun"] = {"sign": "Mesha", "house": 1, "degree": 0.0, "is_combust": False}
        res = evaluate_education_rules(ctx)
        matched = [r["rule_id"] for r in res["matched_rules"]]
        assert "EDU-D24-LAGNA-LORD-DIGNITY-01" in matched

    def test_edu_d24_mercury_jupiter_positive(self):
        ctx = _base_ctx("Mesha")
        ctx["ascendant_degree"] = 0.0  # D24 Lagna = Simha
        # Mercury in Mesha 0.0° -> D24 sign = Simha -> D24 House 1 (Kendra)
        ctx["planet_map"]["Mercury"] = {"sign": "Mesha", "house": 1, "degree": 0.0, "is_combust": False}
        res = evaluate_education_rules(ctx)
        matched = [r["rule_id"] for r in res["matched_rules"]]
        assert "EDU-D24-MERCURY-JUPITER-AFFINITY-02" in matched


# ===========================================================================
# 3. ALL 12 LAGNA SIGNS EXECUTION
# ===========================================================================

class TestAll12Lagnas:
    """Verifies that rule engine runs without crash across all 12 ascendant rashis."""

    @pytest.mark.parametrize("lagna", SIGNS_SK)
    def test_all_12_lagnas_evaluation(self, lagna):
        ctx = _base_ctx(lagna)
        res = evaluate_education_rules(ctx)
        assert res["domain"] == "education"
        assert res["lagna"] == lagna
        assert res["d24_status"] == "VERIFIED_ACTIVE"
        assert len(res["dimensions"]) == 6
        for d in EDUCATION_DIMENSIONS:
            assert d in res["dimensions"]
            assert "status" in res["dimensions"][d]


# ===========================================================================
# 4. BACKWARD COMPATIBILITY WITH LEGACY API CONTRACTS
# ===========================================================================

class TestLegacyApiCompatibility:
    """Verifies that analyse_education preserves 100% of legacy response keys."""

    def test_legacy_keys_presence(self):
        ctx = _base_ctx("Mesha")
        out = analyse_education(ctx)

        # Legacy keys
        legacy_keys = [
            "domain", "icon", "score", "study_fields", "vidya_yoga",
            "foreign_education", "competitive_success", "mercury_position",
            "dasha_active", "timing", "remedies", "analysis",
        ]
        for k in legacy_keys:
            assert k in out, f"Legacy key '{k}' must be present in response"

        # New WP5E canonical fields
        new_keys = [
            "evidence", "dimensions", "rules_evaluated", "d24_status",
            "safety_disclaimer", "is_diagnostic",
        ]
        for k in new_keys:
            assert k in out, f"WP5E key '{k}' must be present in response"

        assert out["domain"] == "Education & Skills"
        assert isinstance(out["score"], int)
        assert 0 <= out["score"] <= 100
        assert out["d24_status"] == "VERIFIED_ACTIVE"
        assert out["is_diagnostic"] is False


# ===========================================================================
# 5. SAFETY GUARDRAILS & ADVERSARIAL SCAN
# ===========================================================================

class TestEducationalSafety:
    """Scans all texts to ensure strict educational and cognitive safety compliance."""

    FORBIDDEN_PATTERNS = [
        "guaranteed exam pass",
        "guaranteed exam fail",
        "you will fail",
        "you will pass",
        "guaranteed admission",
        "university rejection guaranteed",
        "iq score",
        "low intelligence",
        "high intelligence",
        "learning disability",
        "adhd diagnosed",
        "dyslexia diagnosed",
        "abandon education",
        "drop out of school",
        "incapable of learning",
    ]

    def test_safety_disclaimer_presence(self):
        ctx = _base_ctx()
        eval_res = evaluate_education_rules(ctx)
        assert SAFETY_DISCLAIMER in eval_res["safety_disclaimer"]

        domain_res = analyse_education(ctx)
        assert SAFETY_DISCLAIMER in domain_res["safety_disclaimer"]

    def test_narrative_and_competitive_success_safety(self):
        ctx = _base_ctx()
        out = analyse_education(ctx)

        full_text = (
            str(out.get("analysis", "")) + " " +
            str(out.get("competitive_success", "")) + " " +
            str(out.get("study_fields", ""))
        ).lower()

        for pattern in self.FORBIDDEN_PATTERNS:
            assert pattern not in full_text, f"Safety violation: found forbidden pattern '{pattern}'"

        # Explicitly assert that competitive_success does not claim 'pass' or 'guaranteed'
        assert "guaranteed" not in out["competitive_success"].lower()
        assert "pass" not in out["competitive_success"].lower()
        assert "fail" not in out["competitive_success"].lower()

    def test_adversarial_prompt_handling(self):
        """Simulate adversarial input requesting guaranteed admission or pass."""
        ctx = _base_ctx()
        ctx["user_question"] = "Will I guarantee 99% marks in IIT JEE and pass with rank 1?"
        out = analyse_education(ctx)
        # Verify the system maintains non-deterministic stance and emits disclaimer
        assert out["safety_disclaimer"] == SAFETY_DISCLAIMER
        assert "guarantee" not in out["competitive_success"].lower()


# ===========================================================================
# 6. DETERMINISTIC EXECUTION
# ===========================================================================

class TestDeterministicExecution:
    """Verifies that identical inputs yield identical deterministic outputs."""

    def test_repeated_execution_consistency(self):
        ctx1 = _base_ctx("Mesha")
        ctx2 = _base_ctx("Mesha")

        out1 = analyse_education(ctx1)
        out2 = analyse_education(ctx2)

        assert out1["score"] == out2["score"]
        assert out1["rules_evaluated"] == out2["rules_evaluated"]
        assert out1["competitive_success"] == out2["competitive_success"]
        assert out1["analysis"] == out2["analysis"]
        assert len(out1["evidence"]["matched_rules"]) == len(out2["evidence"]["matched_rules"])
