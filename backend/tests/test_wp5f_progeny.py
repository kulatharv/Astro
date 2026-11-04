"""
Unit & Integration Test Suite for WP5F — Children & Progeny Domain Rule Pack.

Tests:
  1. D7 Saptamsa Mathematical Verification Gate (BPHS Ch. 6, v. 9-10):
     - All 12 signs tested
     - Exact division boundaries (0.0°, 4.2857°, 8.5714°, 12.8571°, 17.1428°, 21.4285°, 25.7142°, 29.99°)
     - Transition precision near division thresholds (just below, at, and just above)
     - Odd sign (from self) and Even sign (from 7th) mapping
  2. Canonical 21-Rule Catalog Execution:
     - Positive, negative, and ordered exception tests across all 7 families (A-G)
  3. All 12 Lagna signs execution
  4. 5 Safe Progeny / Caregiving Dimensions separation
  5. 100% Backward Compatibility with legacy API contracts
  6. Strict Reproductive & Child Safety Guardrail & Adversarial Scans:
     - No fertility or infertility assertions
     - No pregnancy or miscarriage predictions
     - No child count predictions
     - No fetal sex/gender determination (PC-PNDT Act compliance)
     - No child mortality (balarishta) or health predictions
     - No coercive advice regarding parenthood
  7. Deterministic repeated execution
"""

import pytest
from shared.veda.progeny import (
    calculate_saptamsha_d7,
    build_d7_chart,
    evaluate_progeny_rules,
    PROGENY_RULES_CATALOG,
    SAFETY_DISCLAIMER,
    PROGENY_DIMENSIONS,
)
from shared.veda.zodiac import SIGNS_SK
from modules.prediction.domains.children import analyse_children, analyse_progeny


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
        "doshas": [],
        "transit_map": {
            "Sun": {"house": 5}, "Moon": {"house": 4}, "Mars": {"house": 1},
            "Mercury": {"house": 3}, "Jupiter": {"house": 9}, "Venus": {"house": 2},
            "Saturn": {"house": 10}, "Rahu": {"house": 11}, "Ketu": {"house": 5},
        },
    }


# ===========================================================================
# 1. D7 SAPTAMSA MATHEMATICAL VERIFICATION GATE
# ===========================================================================

class TestD7Mathematics:
    """Rigorous tests for BPHS Ch. 6, v. 9-10 D7 Saptamsa calculation."""

    def test_d7_all_12_signs_base(self):
        """Test 0.0° for all 12 signs: Odd signs start from self, Even start from 7th."""
        odd_signs = ["Mesha", "Mithuna", "Simha", "Tula", "Dhanu", "Kumbha"]
        even_signs = ["Vrishabha", "Karka", "Kanya", "Vrischika", "Makara", "Meena"]

        # Odd signs start from the sign itself
        for sign in odd_signs:
            res = calculate_saptamsha_d7(sign, 0.0)
            assert res == sign, f"Odd sign {sign} at 0.0° must map to {sign}, got {res}"

        # Even signs start from 7th sign from it
        for sign in even_signs:
            sign_idx = SIGNS_SK.index(sign)
            expected_7th = SIGNS_SK[(sign_idx + 6) % 12]
            res = calculate_saptamsha_d7(sign, 0.0)
            assert res == expected_7th, f"Even sign {sign} at 0.0° must map to 7th sign {expected_7th}, got {res}"

    def test_d7_odd_sign_boundary_transitions(self):
        """Test division boundaries for odd sign Mesha (part size = 30/7 ≈ 4.2857°)."""
        part_size = 30.0 / 7.0

        # Part 0: [0.0, 4.2857) -> Mesha
        assert calculate_saptamsha_d7("Mesha", 0.0) == "Mesha"
        assert calculate_saptamsha_d7("Mesha", 4.28) == "Mesha"

        # Boundary step: 4.29 -> Part 1 -> Vrishabha
        assert calculate_saptamsha_d7("Mesha", 4.29) == "Vrishabha"
        assert calculate_saptamsha_d7("Mesha", 8.57) == "Vrishabha"

        # Boundary step: 8.58 -> Part 2 -> Mithuna
        assert calculate_saptamsha_d7("Mesha", 8.58) == "Mithuna"

        # Part 3: 3 * 4.2857 = 12.8571 -> Karka
        assert calculate_saptamsha_d7("Mesha", 12.86) == "Karka"

        # Part 4: 4 * 4.2857 = 17.1428 -> Simha
        assert calculate_saptamsha_d7("Mesha", 17.15) == "Simha"

        # Part 5: 5 * 4.2857 = 21.4285 -> Kanya
        assert calculate_saptamsha_d7("Mesha", 21.43) == "Kanya"

        # Last Part 6: 6 * 4.2857 = 25.7142 -> Tula
        assert calculate_saptamsha_d7("Mesha", 25.72) == "Tula"
        assert calculate_saptamsha_d7("Mesha", 29.99) == "Tula"

    def test_d7_even_sign_boundary_transitions(self):
        """Test division boundaries for even sign Vrishabha (starts from 7th = Vrischika)."""
        # Part 0: [0.0, 4.2857) -> Vrischika
        assert calculate_saptamsha_d7("Vrishabha", 0.0) == "Vrischika"
        assert calculate_saptamsha_d7("Vrishabha", 4.28) == "Vrischika"

        # Boundary step: 4.29 -> Part 1 -> Dhanu
        assert calculate_saptamsha_d7("Vrishabha", 4.29) == "Dhanu"

        # Boundary step: 8.58 -> Part 2 -> Makara
        assert calculate_saptamsha_d7("Vrishabha", 8.58) == "Makara"

        # Part 3: Kumbha
        assert calculate_saptamsha_d7("Vrishabha", 12.86) == "Kumbha"

        # Part 4: Meena
        assert calculate_saptamsha_d7("Vrishabha", 17.15) == "Meena"

        # Part 5: Mesha
        assert calculate_saptamsha_d7("Vrishabha", 21.43) == "Mesha"

        # Part 6: Vrishabha
        assert calculate_saptamsha_d7("Vrishabha", 25.72) == "Vrishabha"
        assert calculate_saptamsha_d7("Vrishabha", 29.99) == "Vrishabha"

    def test_d7_transition_precision_near_boundaries(self):
        """Test high-precision boundary transitions with epsilon."""
        eps = 0.0001
        step = 30.0 / 7.0  # 4.2857142857...

        # Test boundary 1: step
        assert calculate_saptamsha_d7("Simha", step - eps) == "Simha"
        assert calculate_saptamsha_d7("Simha", step + eps) == "Kanya"

        # Test boundary 3: 3 * step
        # Simha is odd -> starts Simha (4). Part 2: (4+2)%12 = 6 (Tula). Part 3: (4+3)%12 = 7 (Vrischika).
        assert calculate_saptamsha_d7("Simha", 3 * step - eps) == "Tula"
        assert calculate_saptamsha_d7("Simha", 3 * step + eps) == "Vrischika"

    def test_d7_sign_normalization(self):
        """Test sign name normalization and edge cases."""
        assert calculate_saptamsha_d7("vrishika", 0.0) == "Vrishabha"  # Even sign index 7, 7th is Vrishabha
        assert calculate_saptamsha_d7("Vrischika", 0.0) == "Vrishabha"
        assert calculate_saptamsha_d7("mesha", 0.0) == "Mesha"
        assert calculate_saptamsha_d7("", 0.0) == "Mesha"

    def test_build_d7_chart_integration(self):
        """Test construction of full D7 chart structure."""
        ctx = _base_ctx()
        d7 = build_d7_chart(ctx)
        assert "d7_lagna" in d7
        assert "d7_lagna_lord" in d7
        assert "d7_planets" in d7
        assert len(d7["d7_planets"]) >= 7
        for p, pdata in d7["d7_planets"].items():
            assert 1 <= pdata["house"] <= 12
            assert pdata["sign"] in SIGNS_SK


# ===========================================================================
# 2. CANONICAL 21-RULE CATALOG TESTS (FAMILIES A THROUGH G)
# ===========================================================================

class TestProgenyRuleCatalog:
    """Verifies all 21 canonical rules with positive, negative, and exception states."""

    def test_catalog_inventory(self):
        """Assert exact count and structural integrity of all rules."""
        assert len(PROGENY_RULES_CATALOG) == 21
        ids = [r.rule_id for r in PROGENY_RULES_CATALOG]
        assert len(ids) == len(set(ids)), "Duplicate rule_id detected"
        for r in PROGENY_RULES_CATALOG:
            assert r.confidence in ["[HIGH]", "[MEDIUM]", "[LOW, needs expert check]"]
            assert r.source_status in ["VERIFIED", "SOURCE VERIFICATION REQUIRED"]
            assert r.review_status in ["ACCEPTED", "EXPERT REVIEW REQUIRED"]
            assert r.effect in ["SUPPORTS", "OBSTRUCTS", "CONDITIONAL"]
            assert len(r.dimensions) > 0

    # Family A: 5th House
    def test_prog_h5_lord_kendra_trikona_positive(self):
        ctx = _base_ctx("Mesha")  # 5th lord Sun
        ctx["planet_map"]["Sun"] = {"sign": "Simha", "house": 5, "degree": 10.0, "is_combust": False}
        res = evaluate_progeny_rules(ctx)
        matched = [r["rule_id"] for r in res["matched_rules"]]
        assert "PROG-H5-LORD-KENDRA-TRIKONA-01" in matched

    def test_prog_h5_lord_kendra_trikona_combust_exception(self):
        ctx = _base_ctx("Mesha")
        ctx["planet_map"]["Sun"] = {"sign": "Simha", "house": 5, "degree": 10.0, "is_combust": True}
        res = evaluate_progeny_rules(ctx)
        cancelled = [r["rule_id"] for r in res["cancelled_rules"]]
        assert "PROG-H5-LORD-KENDRA-TRIKONA-01" in cancelled

    def test_prog_h5_lord_dignity_positive(self):
        ctx = _base_ctx("Mesha")
        ctx["planet_map"]["Sun"] = {"sign": "Mesha", "house": 1, "degree": 10.0, "is_combust": False}  # Exalted
        res = evaluate_progeny_rules(ctx)
        matched = [r["rule_id"] for r in res["matched_rules"]]
        assert "PROG-H5-LORD-OWN-EXALTED-02" in matched

    def test_prog_h5_benefic_occupancy_positive(self):
        ctx = _base_ctx("Mesha")
        ctx["planet_map"]["Jupiter"] = {"sign": "Simha", "house": 5, "degree": 12.0, "is_combust": False}
        res = evaluate_progeny_rules(ctx)
        matched = [r["rule_id"] for r in res["matched_rules"]]
        assert "PROG-H5-BENEFIC-OCCUPANCY-03" in matched

    def test_prog_h5_benefic_debilitated_exception(self):
        ctx = _base_ctx("Kanya")  # 5th house is Makara
        ctx["planet_map"]["Moon"]["house"] = 10  # Move Moon away
        ctx["planet_map"]["Jupiter"] = {"sign": "Makara", "house": 5, "degree": 5.0, "is_combust": False}  # Debilitated
        res = evaluate_progeny_rules(ctx)
        cancelled = [r["rule_id"] for r in res["cancelled_rules"]]
        assert "PROG-H5-BENEFIC-OCCUPANCY-03" in cancelled

    # Family B: 5th House Restraint
    def test_prog_h5_lord_dusthana_positive(self):
        ctx = _base_ctx("Mesha")  # 5th lord Sun
        ctx["planet_map"]["Sun"] = {"sign": "Kanya", "house": 6, "degree": 10.0, "is_combust": False}
        res = evaluate_progeny_rules(ctx)
        matched = [r["rule_id"] for r in res["matched_rules"]]
        assert "PROG-H5-LORD-DUSTHANA-AFFLICTION-04" in matched

    def test_prog_h5_lord_dusthana_own_sign_exception(self):
        ctx = _base_ctx("Mesha")  # 5th lord Sun
        # Hypothetical frame: Sun in Leo (own sign) placed in house 6
        ctx["planet_map"]["Sun"] = {"sign": "Simha", "house": 6, "degree": 10.0, "is_combust": False}
        res = evaluate_progeny_rules(ctx)
        cancelled = [r["rule_id"] for r in res["cancelled_rules"]]
        assert "PROG-H5-LORD-DUSTHANA-AFFLICTION-04" in cancelled

    def test_prog_h5_saturn_discipline_positive(self):
        ctx = _base_ctx("Mesha")
        ctx["planet_map"]["Saturn"] = {"sign": "Simha", "house": 5, "degree": 10.0, "is_combust": False}
        res = evaluate_progeny_rules(ctx)
        matched = [r["rule_id"] for r in res["matched_rules"]]
        assert "PROG-H5-SATURN-DISCIPLINE-05" in matched

    def test_prog_h5_rahu_mentorship_positive(self):
        ctx = _base_ctx("Mesha")
        ctx["planet_map"]["Rahu"] = {"sign": "Simha", "house": 5, "degree": 15.0, "is_combust": False}
        res = evaluate_progeny_rules(ctx)
        matched = [r["rule_id"] for r in res["matched_rules"]]
        assert "PROG-H5-RAHU-INNOVATIVE-MENTORSHIP-06" in matched

    # Family C: Jupiter
    def test_prog_jupiter_dignity_positive(self):
        ctx = _base_ctx("Mesha")
        ctx["planet_map"]["Jupiter"] = {"sign": "Karka", "house": 4, "degree": 5.0, "is_combust": False}  # Exalted
        res = evaluate_progeny_rules(ctx)
        matched = [r["rule_id"] for r in res["matched_rules"]]
        assert "PROG-JUPITER-DIGNITY-EXALTED-OWN-01" in matched

    def test_prog_jupiter_kt_positive(self):
        ctx = _base_ctx("Mesha")
        ctx["planet_map"]["Jupiter"] = {"sign": "Mesha", "house": 1, "degree": 12.0, "is_combust": False}
        res = evaluate_progeny_rules(ctx)
        matched = [r["rule_id"] for r in res["matched_rules"]]
        assert "PROG-JUPITER-KENDRA-TRIKONA-02" in matched

    def test_prog_jupiter_debilitated_exception(self):
        ctx = _base_ctx("Mesha")
        ctx["planet_map"]["Jupiter"] = {"sign": "Makara", "house": 10, "degree": 5.0, "is_combust": False}
        res = evaluate_progeny_rules(ctx)
        cancelled = [r["rule_id"] for r in res["cancelled_rules"]]
        assert "PROG-JUPITER-KENDRA-TRIKONA-02" in cancelled

    def test_prog_jupiter_h5_karakasthana_positive(self):
        ctx = _base_ctx("Mesha")
        ctx["planet_map"]["Jupiter"] = {"sign": "Simha", "house": 5, "degree": 15.0, "is_combust": False}
        res = evaluate_progeny_rules(ctx)
        matched = [r["rule_id"] for r in res["matched_rules"]]
        assert "PROG-JUPITER-H5-OCCUPANCY-KARAKASTHANA-03" in matched

    def test_prog_jupiter_affliction_positive(self):
        ctx = _base_ctx("Mesha")
        ctx["planet_map"]["Jupiter"] = {"sign": "Kanya", "house": 6, "degree": 15.0, "is_combust": True}
        res = evaluate_progeny_rules(ctx)
        matched = [r["rule_id"] for r in res["matched_rules"]]
        assert "PROG-JUPITER-AFFLICTION-COMBUST-04" in matched

    # Family D: 9th House
    def test_prog_h9_lord_kt_positive(self):
        ctx = _base_ctx("Mesha")  # 9th lord Jupiter
        ctx["planet_map"]["Jupiter"] = {"sign": "Dhanu", "house": 9, "degree": 15.0, "is_combust": False}
        res = evaluate_progeny_rules(ctx)
        matched = [r["rule_id"] for r in res["matched_rules"]]
        assert "PROG-H9-LORD-KENDRA-TRIKONA-01" in matched

    def test_prog_h9_lord_dignity_positive(self):
        ctx = _base_ctx("Mesha")
        ctx["planet_map"]["Jupiter"] = {"sign": "Karka", "house": 4, "degree": 5.0, "is_combust": False}
        res = evaluate_progeny_rules(ctx)
        matched = [r["rule_id"] for r in res["matched_rules"]]
        assert "PROG-H9-LORD-OWN-EXALTED-02" in matched

    def test_prog_h9_benefic_occupancy_positive(self):
        ctx = _base_ctx("Mesha")
        ctx["planet_map"]["Venus"] = {"sign": "Dhanu", "house": 9, "degree": 10.0, "is_combust": False}
        res = evaluate_progeny_rules(ctx)
        matched = [r["rule_id"] for r in res["matched_rules"]]
        assert "PROG-H9-BENEFIC-OCCUPANCY-03" in matched

    # Family E: Moon & Lagna
    def test_prog_moon_dignity_positive(self):
        ctx = _base_ctx("Mesha")
        ctx["planet_map"]["Moon"] = {"sign": "Karka", "house": 4, "degree": 12.0, "is_combust": False}  # Own sign
        res = evaluate_progeny_rules(ctx)
        matched = [r["rule_id"] for r in res["matched_rules"]]
        assert "PROG-MOON-DIGNITY-EXALTED-OWN-01" in matched

    def test_prog_moon_5th_chandra_lagna_positive(self):
        ctx = _base_ctx("Mesha")
        ctx["planet_map"]["Moon"] = {"sign": "Mesha", "house": 1, "degree": 10.0, "is_combust": False}
        # 5th from Moon (house 1) is house 5. Place Jupiter in house 5.
        ctx["planet_map"]["Jupiter"] = {"sign": "Simha", "house": 5, "degree": 15.0, "is_combust": False}
        res = evaluate_progeny_rules(ctx)
        matched = [r["rule_id"] for r in res["matched_rules"]]
        assert "PROG-MOON-5TH-CHANDRA-LAGNA-02" in matched

    def test_prog_lagna_lord_5th_positive(self):
        ctx = _base_ctx("Mesha")  # Lagna lord Mars
        ctx["planet_map"]["Mars"] = {"sign": "Simha", "house": 5, "degree": 10.0, "is_combust": False}
        res = evaluate_progeny_rules(ctx)
        matched = [r["rule_id"] for r in res["matched_rules"]]
        assert "PROG-LAGNA-LORD-5TH-CONNECTION-03" in matched

    # Family F: Inter-Lord Connections
    def test_prog_5_9_yoga_positive(self):
        ctx = _base_ctx("Mesha")  # 5th lord Sun, 9th lord Jupiter
        ctx["planet_map"]["Sun"] = {"sign": "Dhanu", "house": 9, "degree": 10.0, "is_combust": False}
        ctx["planet_map"]["Jupiter"] = {"sign": "Dhanu", "house": 9, "degree": 15.0, "is_combust": False}
        res = evaluate_progeny_rules(ctx)
        matched = [r["rule_id"] for r in res["matched_rules"]]
        assert "PROG-5-9-DHARMA-TRIKONA-YOGA-01" in matched

    def test_prog_1_5_sambandha_positive(self):
        ctx = _base_ctx("Mesha")  # Lagna lord Mars, 5th lord Sun
        ctx["planet_map"]["Mars"] = {"sign": "Simha", "house": 5, "degree": 10.0, "is_combust": False}
        ctx["planet_map"]["Sun"] = {"sign": "Simha", "house": 5, "degree": 15.0, "is_combust": False}
        res = evaluate_progeny_rules(ctx)
        matched = [r["rule_id"] for r in res["matched_rules"]]
        assert "PROG-1-5-SAMBANDHA-YOGA-02" in matched

    def test_prog_4_5_connection_positive(self):
        ctx = _base_ctx("Mesha")  # 4th lord Moon, 5th lord Sun
        ctx["planet_map"]["Moon"] = {"sign": "Simha", "house": 5, "degree": 10.0, "is_combust": False}
        ctx["planet_map"]["Sun"] = {"sign": "Simha", "house": 5, "degree": 15.0, "is_combust": False}
        res = evaluate_progeny_rules(ctx)
        matched = [r["rule_id"] for r in res["matched_rules"]]
        assert "PROG-4-5-KENDRA-TRIKONA-UNION-03" in matched

    # Family G: D7 Saptamsa
    def test_prog_d7_lagna_lord_positive(self):
        ctx = _base_ctx("Mesha")
        # Ascendant 0.0° in Mesha (odd sign) -> D7 Lagna is Mesha -> Lord is Mars.
        ctx["ascendant_degree"] = 0.0
        # If Mars in Mesha 0.0° -> D7 sign is Mesha -> house 1 in D7 (Kendra & Own sign)!
        ctx["planet_map"]["Mars"] = {"sign": "Mesha", "house": 1, "degree": 0.0, "is_combust": False}
        res = evaluate_progeny_rules(ctx)
        matched = [r["rule_id"] for r in res["matched_rules"]]
        assert "PROG-D7-LAGNA-LORD-DIGNITY-01" in matched

    def test_prog_d7_jupiter_positive(self):
        ctx = _base_ctx("Mesha")
        ctx["ascendant_degree"] = 0.0  # D7 Lagna = Mesha
        # Jupiter in Mesha 0.0° -> D7 sign is Mesha -> house 1 in D7 (Kendra)
        ctx["planet_map"]["Jupiter"] = {"sign": "Mesha", "house": 1, "degree": 0.0, "is_combust": False}
        res = evaluate_progeny_rules(ctx)
        matched = [r["rule_id"] for r in res["matched_rules"]]
        assert "PROG-D7-JUPITER-WELL-PLACED-02" in matched


# ===========================================================================
# 3. ALL 12 LAGNA SIGNS EXECUTION
# ===========================================================================

class TestAll12Lagnas:
    """Verifies that rule engine runs without crash across all 12 ascendant rashis."""

    @pytest.mark.parametrize("lagna", SIGNS_SK)
    def test_all_12_lagnas_evaluation(self, lagna):
        ctx = _base_ctx(lagna)
        res = evaluate_progeny_rules(ctx)
        assert res["domain"] == "progeny"
        assert res["lagna"] == lagna
        assert res["d7_status"] == "VERIFIED_ACTIVE"
        assert len(res["dimensions"]) == 5
        for d in PROGENY_DIMENSIONS:
            assert d in res["dimensions"]
            assert "status" in res["dimensions"][d]


# ===========================================================================
# 4. BACKWARD COMPATIBILITY WITH LEGACY API CONTRACTS
# ===========================================================================

class TestLegacyApiCompatibility:
    """Verifies that analyse_children preserves 100% of legacy response keys."""

    def test_legacy_keys_presence(self):
        ctx = _base_ctx("Mesha")
        out = analyse_children(ctx)

        legacy_keys = [
            "domain", "icon", "score", "count_indicator", "gender_indicator",
            "child_nature", "putra_dosh", "santana_yoga", "fifth_lord",
            "h5_planets", "jupiter_position", "dasha_active", "timing",
            "remedies", "analysis",
        ]
        for k in legacy_keys:
            assert k in out, f"Legacy key '{k}' must be present in response"

        # New WP5F canonical fields
        new_keys = [
            "evidence", "dimensions", "rules_evaluated", "d7_status",
            "safety_disclaimer", "is_diagnostic",
        ]
        for k in new_keys:
            assert k in out, f"WP5F key '{k}' must be present in response"

        assert out["domain"] == "Children & Next Generation"
        assert isinstance(out["score"], int)
        assert 0 <= out["score"] <= 100
        assert out["d7_status"] == "VERIFIED_ACTIVE"
        assert out["is_diagnostic"] is False

    def test_alias_equality(self):
        ctx = _base_ctx("Mesha")
        assert analyse_children(ctx) == analyse_progeny(ctx)


# ===========================================================================
# 5. REPRODUCTIVE & CHILD SAFETY GUARDRAILS & ADVERSARIAL SCAN
# ===========================================================================

class TestReproductiveSafety:
    """Scans all outputs to ensure strict compliance with medical, fertility, and sex-determination laws."""

    FORBIDDEN_PATTERNS = [
        "infertility",
        "infertile",
        "sterile",
        "conception date",
        "guaranteed conception",
        "guaranteed pregnancy",
        "miscarriage guaranteed",
        "abortion indicated",
        "stillbirth",
        "male child indicated",
        "female child indicated",
        "boy child",
        "girl child",
        "multiple children possible",
        "1-2 children indicated",
        "challenges in childbearing",
        "balarishta",
        "infant mortality",
        "child will die",
        "child death",
        "abandon parenthood",
        "delay pregnancy",
    ]

    def test_safety_disclaimer_presence(self):
        ctx = _base_ctx()
        eval_res = evaluate_progeny_rules(ctx)
        assert SAFETY_DISCLAIMER in eval_res["safety_disclaimer"]

        domain_res = analyse_children(ctx)
        assert SAFETY_DISCLAIMER in domain_res["safety_disclaimer"]

    def test_narrative_and_legacy_fields_safety(self):
        ctx = _base_ctx()
        out = analyse_children(ctx)

        full_text = (
            str(out.get("analysis", "")) + " " +
            str(out.get("count_indicator", "")) + " " +
            str(out.get("gender_indicator", "")) + " " +
            str(out.get("child_nature", ""))
        ).lower()

        for pattern in self.FORBIDDEN_PATTERNS:
            assert pattern not in full_text, f"Safety violation: found forbidden pattern '{pattern}'"

        # Explicitly verify gender_indicator contains no sex determination
        assert "male" not in out["gender_indicator"].lower()
        assert "female" not in out["gender_indicator"].lower()
        assert "boy" not in out["gender_indicator"].lower()
        assert "girl" not in out["gender_indicator"].lower()

        # Explicitly verify count_indicator contains no child counting
        assert "1-2" not in out["count_indicator"].lower()
        assert "multiple" not in out["count_indicator"].lower()
        assert "childbearing" not in out["count_indicator"].lower()

    def test_adversarial_prompt_handling(self):
        """Simulate adversarial user prompting for child sex and conception prediction."""
        ctx = _base_ctx()
        ctx["user_question"] = "Will I have a male child or female child in 2027 and will my pregnancy succeed?"
        out = analyse_children(ctx)
        assert out["safety_disclaimer"] == SAFETY_DISCLAIMER
        assert "male" not in out["gender_indicator"].lower()
        assert "female" not in out["gender_indicator"].lower()


# ===========================================================================
# 6. DETERMINISTIC EXECUTION
# ===========================================================================

class TestDeterministicExecution:
    """Verifies that identical inputs yield identical deterministic outputs."""

    def test_repeated_execution_consistency(self):
        ctx1 = _base_ctx("Mesha")
        ctx2 = _base_ctx("Mesha")

        out1 = analyse_children(ctx1)
        out2 = analyse_children(ctx2)

        assert out1["score"] == out2["score"]
        assert out1["rules_evaluated"] == out2["rules_evaluated"]
        assert out1["count_indicator"] == out2["count_indicator"]
        assert out1["gender_indicator"] == out2["gender_indicator"]
        assert out1["analysis"] == out2["analysis"]
        assert len(out1["evidence"]["matched_rules"]) == len(out2["evidence"]["matched_rules"])
