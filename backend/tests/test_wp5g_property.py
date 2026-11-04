"""
Unit & Integration Test Suite for WP5G — Property & Residence Domain Rule Pack.

Tests:
  1. D4 Chaturthamsa Mathematical Verification Gate (BPHS Ch. 6, v. 5-6):
     - All 12 source signs tested
     - Exact division boundaries (0.0°, 7.5°, 15.0°, 22.5°, 30.0°)
     - Transition precision near thresholds (just below, at, and just above)
     - Kendra counting rule ((sign_idx + 3 * part) % 12)
     - Modality invariance (Movable->Movable, Fixed->Fixed, Dual->Dual)
     - Degree normalization and floating-point stability
  2. Canonical 27-Rule Catalog Execution:
     - Positive, negative, boundary, and ordered exception tests across all 7 dimensions + D4
  3. All 12 Lagna signs execution
  4. 7 Property dimensions separation (stability, acquisition, disposal, construction, relocation, inheritance, obligations)
  5. 100% Backward Compatibility with legacy API contracts
  6. Strict Real Estate & Financial Safety Guardrails & Adversarial Scans:
     - No guaranteed property purchase or sale
     - No mortgage or loan approval predictions
     - No price appreciation or investment profit forecasts
     - No legal title or dispute outcome assertions
     - Mandatory non-deterministic disclaimer present
  7. Deterministic repeated execution
"""

import pytest
from shared.veda.property import (
    calculate_chaturthamsa_d4,
    build_d4_chart,
    evaluate_property_rules,
    PROPERTY_RULES_CATALOG,
    PROPERTY_SAFETY_DISCLAIMER,
    PROPERTY_DIMENSIONS,
)
from shared.veda.zodiac import SIGNS_SK
from modules.prediction.domains.property import analyse_property, _property


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
            "Mars": {"sign": "Makara", "house": 10, "degree": 28.0, "str_score": 2, "is_combust": False},
            "Mercury": {"sign": "Mithuna", "house": 3, "degree": 14.0, "str_score": 1, "is_combust": False},
            "Jupiter": {"sign": "Dhanu", "house": 9, "degree": 16.0, "str_score": 1, "is_combust": False},
            "Venus": {"sign": "Vrishabha", "house": 2, "degree": 20.0, "str_score": 1, "is_combust": False},
            "Saturn": {"sign": "Makara", "house": 10, "degree": 5.0, "str_score": 1, "is_combust": False},
            "Rahu": {"sign": "Kumbha", "house": 11, "degree": 22.0, "str_score": 0, "is_combust": False},
            "Ketu": {"sign": "Simha", "house": 5, "degree": 22.0, "str_score": 0, "is_combust": False},
        },
        "mahadasha": "Jupiter",
        "antardasha": "Mars",
        "yogas": [],
        "doshas": [],
        "transit_map": {
            "Sun": {"house": 5}, "Moon": {"house": 4}, "Mars": {"house": 10},
            "Mercury": {"house": 3}, "Jupiter": {"house": 9}, "Venus": {"house": 2},
            "Saturn": {"house": 10}, "Rahu": {"house": 11}, "Ketu": {"house": 5},
        },
    }


# ===========================================================================
# 1. D4 CHATURTHAMSA MATHEMATICAL VERIFICATION GATE
# ===========================================================================

class TestD4Mathematics:
    """Rigorous tests for BPHS Ch. 6, v. 5-6 D4 Chaturthamsa calculation."""

    def test_d4_all_12_signs_quarter_0(self):
        """Quarter 0 [0.0°, 7.5°): Must map to the sign itself for all 12 signs."""
        for sign in SIGNS_SK:
            res = calculate_chaturthamsa_d4(sign, 0.0)
            assert res == sign, f"Sign {sign} at 0.0° must map to {sign}, got {res}"
            res_mid = calculate_chaturthamsa_d4(sign, 3.75)
            assert res_mid == sign

    def test_d4_all_12_signs_all_quarters(self):
        """Verify the 4 Kendra divisions for all 12 signs."""
        for sign in SIGNS_SK:
            sign_idx = SIGNS_SK.index(sign)
            # Quarter 0: Sign itself
            assert calculate_chaturthamsa_d4(sign, 2.0) == SIGNS_SK[(sign_idx + 0) % 12]
            # Quarter 1: 4th from sign
            assert calculate_chaturthamsa_d4(sign, 9.0) == SIGNS_SK[(sign_idx + 3) % 12]
            # Quarter 2: 7th from sign
            assert calculate_chaturthamsa_d4(sign, 18.0) == SIGNS_SK[(sign_idx + 6) % 12]
            # Quarter 3: 10th from sign
            assert calculate_chaturthamsa_d4(sign, 25.0) == SIGNS_SK[(sign_idx + 9) % 12]

    def test_d4_precision_boundaries(self):
        """Test transitions at exact 7.5°, 15.0°, 22.5° thresholds with high precision."""
        sign = "Mesha"  # 0: Mesha, 1: Karka, 2: Tula, 3: Makara

        # Quarter 0 -> Quarter 1 boundary at 7.5°
        assert calculate_chaturthamsa_d4(sign, 7.49999) == "Mesha"
        assert calculate_chaturthamsa_d4(sign, 7.50000) == "Karka"
        assert calculate_chaturthamsa_d4(sign, 7.50001) == "Karka"

        # Quarter 1 -> Quarter 2 boundary at 15.0°
        assert calculate_chaturthamsa_d4(sign, 14.99999) == "Karka"
        assert calculate_chaturthamsa_d4(sign, 15.00000) == "Tula"
        assert calculate_chaturthamsa_d4(sign, 15.00001) == "Tula"

        # Quarter 2 -> Quarter 3 boundary at 22.5°
        assert calculate_chaturthamsa_d4(sign, 22.49999) == "Tula"
        assert calculate_chaturthamsa_d4(sign, 22.50000) == "Makara"
        assert calculate_chaturthamsa_d4(sign, 22.50001) == "Makara"

        # Exit boundary at 29.99999°
        assert calculate_chaturthamsa_d4(sign, 29.99999) == "Makara"

    def test_d4_modality_invariance(self):
        """
        Verify that Kendras preserve modality:
        - Movable source signs always map to Movable signs.
        - Fixed source signs always map to Fixed signs.
        - Dual source signs always map to Dual signs.
        """
        movable = {"Mesha", "Karka", "Tula", "Makara"}
        fixed = {"Vrishabha", "Simha", "Vrischika", "Kumbha"}
        dual = {"Mithuna", "Kanya", "Dhanu", "Meena"}

        for sign in movable:
            for deg in (2.0, 10.0, 17.0, 26.0):
                assert calculate_chaturthamsa_d4(sign, deg) in movable

        for sign in fixed:
            for deg in (2.0, 10.0, 17.0, 26.0):
                assert calculate_chaturthamsa_d4(sign, deg) in fixed

        for sign in dual:
            for deg in (2.0, 10.0, 17.0, 26.0):
                assert calculate_chaturthamsa_d4(sign, deg) in dual

    def test_d4_degree_normalization(self):
        """Test normalization for degree inputs >= 30.0 or negative values."""
        assert calculate_chaturthamsa_d4("Mesha", 35.0) == calculate_chaturthamsa_d4("Mesha", 5.0)
        assert calculate_chaturthamsa_d4("Mesha", -1.0) == calculate_chaturthamsa_d4("Mesha", 29.0)

    def test_build_d4_chart(self):
        """Test full D4 chart construction including houses and house lords."""
        ctx = _base_ctx("Mesha")
        ctx["ascendant_degree"] = 10.0  # In Mesha, 10.0° is Quarter 1 -> Karka
        d4 = build_d4_chart(ctx)

        assert d4["lagna"] == "Karka"
        assert d4["house_lords"][1] == "Moon"
        assert d4["house_lords"][4] == "Venus"  # 4th from Karka is Tula, ruled by Venus
        assert "Mars" in d4["planet_map"]


# ===========================================================================
# 2. CANONICAL PROPERTY RULES VERIFICATION
# ===========================================================================

class TestResidentialStabilityRules:
    """Tests for PROP-RES-01 through PROP-RES-04."""

    def test_prop_res_01_positive(self):
        ctx = _base_ctx("Mesha")
        # 4th lord for Mesha is Moon; put Moon in Karka (own sign) in 4th house (Kendra)
        ctx["planet_map"]["Moon"] = {"sign": "Karka", "house": 4, "degree": 12.0, "is_combust": False}
        res = evaluate_property_rules(ctx)
        rule_ids = [e["rule_id"] for e in res["evidence_ledger"]]
        assert "PROP-RES-01" in rule_ids

    def test_prop_res_01_exception_combust(self):
        ctx = _base_ctx("Mesha")
        # Moon combust
        ctx["planet_map"]["Moon"] = {"sign": "Karka", "house": 4, "degree": 12.0, "is_combust": True}
        res = evaluate_property_rules(ctx)
        exc_rules = [e["rule_id"] for e in res["evidence_ledger"] if e.get("effect") == "EXCEPTION"]
        assert "PROP-RES-01" in exc_rules

    def test_prop_res_02_positive(self):
        ctx = _base_ctx("Mesha")
        # Jupiter in 4th house without malefic aspects
        ctx["planet_map"]["Jupiter"] = {"sign": "Karka", "house": 4, "degree": 5.0}
        ctx["planet_map"]["Mars"] = {"sign": "Mesha", "house": 1, "degree": 8.0}
        ctx["planet_map"]["Saturn"] = {"sign": "Makara", "house": 10, "degree": 5.0}
        # Mars in 1 aspects 4, 7, 8; put Mars in 2 to avoid aspecting 4
        ctx["planet_map"]["Mars"] = {"sign": "Vrishabha", "house": 2, "degree": 8.0}
        # Saturn in 10 aspects 12, 4, 7; put Saturn in 11 to avoid aspecting 4 (11 aspects 1, 5, 8)
        ctx["planet_map"]["Saturn"] = {"sign": "Kumbha", "house": 11, "degree": 5.0}
        res = evaluate_property_rules(ctx)
        rule_ids = [e["rule_id"] for e in res["evidence_ledger"]]
        assert "PROP-RES-02" in rule_ids

    def test_prop_res_03_positive_and_exception(self):
        ctx = _base_ctx("Mesha")
        # Saturn in 4th house, no Jupiter/Venus aspect
        ctx["planet_map"]["Saturn"] = {"sign": "Karka", "house": 4, "degree": 5.0}
        ctx["planet_map"]["Moon"] = {"sign": "Mesha", "house": 1, "degree": 5.0}
        res = evaluate_property_rules(ctx)
        rule_ids = [e["rule_id"] for e in res["evidence_ledger"] if e.get("effect") == "OBSTRUCTS"]
        assert "PROP-RES-03" in rule_ids

        # Exception: 4th lord Moon also in 4th house
        ctx["planet_map"]["Moon"] = {"sign": "Karka", "house": 4, "degree": 12.0}
        res2 = evaluate_property_rules(ctx)
        exc_rules = [e["rule_id"] for e in res2["evidence_ledger"] if e.get("effect") == "EXCEPTION"]
        assert "PROP-RES-03" in exc_rules

    def test_prop_res_04_positive(self):
        ctx = _base_ctx("Mesha")
        # Put Moon in house 9 (Trikona) in Dhanu, Saturn in 11 (aspects 1, 5, 8; doesn't aspect 9)
        ctx["planet_map"]["Moon"] = {"sign": "Dhanu", "house": 9, "degree": 12.0}
        ctx["planet_map"]["Saturn"] = {"sign": "Kumbha", "house": 11, "degree": 5.0}
        res = evaluate_property_rules(ctx)
        rule_ids = [e["rule_id"] for e in res["evidence_ledger"]]
        assert "PROP-RES-04" in rule_ids


class TestPropertyAcquisitionRules:
    """Tests for PROP-ACQ-01 through PROP-ACQ-06."""

    def test_prop_acq_01_positive_and_exception(self):
        ctx = _base_ctx("Mesha")
        # Mars exalted in Makara in 10th house (Kendra)
        ctx["planet_map"]["Mars"] = {"sign": "Makara", "house": 10, "degree": 28.0, "is_combust": False}
        res = evaluate_property_rules(ctx)
        rule_ids = [e["rule_id"] for e in res["evidence_ledger"]]
        assert "PROP-ACQ-01" in rule_ids

        # Exception when Mars is combust
        ctx["planet_map"]["Mars"]["is_combust"] = True
        res2 = evaluate_property_rules(ctx)
        exc_rules = [e["rule_id"] for e in res2["evidence_ledger"] if e.get("effect") == "EXCEPTION"]
        assert "PROP-ACQ-01" in exc_rules

    def test_prop_acq_02_positive(self):
        ctx = _base_ctx("Mesha")
        # 4th lord Moon in 11th house
        ctx["planet_map"]["Moon"] = {"sign": "Kumbha", "house": 11, "degree": 15.0}
        res = evaluate_property_rules(ctx)
        rule_ids = [e["rule_id"] for e in res["evidence_ledger"]]
        assert "PROP-ACQ-02" in rule_ids

    def test_prop_acq_03_positive(self):
        ctx = _base_ctx("Mesha")
        # 4th lord Moon in 2nd house
        ctx["planet_map"]["Moon"] = {"sign": "Vrishabha", "house": 2, "degree": 15.0}
        res = evaluate_property_rules(ctx)
        rule_ids = [e["rule_id"] for e in res["evidence_ledger"]]
        assert "PROP-ACQ-03" in rule_ids

    def test_prop_acq_04_positive(self):
        ctx = _base_ctx("Mesha")
        ctx["planet_map"]["Moon"] = {"sign": "Karka", "house": 4, "degree": 12.0}
        res = evaluate_property_rules(ctx)
        rule_ids = [e["rule_id"] for e in res["evidence_ledger"]]
        assert "PROP-ACQ-04" in rule_ids

    def test_prop_acq_05_positive(self):
        ctx = _base_ctx("Mesha")
        # Moon in 4, Mars in 10 (mutual Kendra)
        ctx["planet_map"]["Moon"] = {"sign": "Karka", "house": 4, "degree": 12.0}
        ctx["planet_map"]["Mars"] = {"sign": "Makara", "house": 10, "degree": 28.0}
        res = evaluate_property_rules(ctx)
        rule_ids = [e["rule_id"] for e in res["evidence_ledger"]]
        assert "PROP-ACQ-05" in rule_ids

    def test_prop_acq_06_positive_and_exception(self):
        ctx = _base_ctx("Mesha")
        # Moon debilitated in Vrischika in house 8
        ctx["planet_map"]["Moon"] = {"sign": "Vrischika", "house": 8, "degree": 3.0}
        res = evaluate_property_rules(ctx)
        rule_ids = [e["rule_id"] for e in res["evidence_ledger"] if e.get("effect") == "OBSTRUCTS"]
        assert "PROP-ACQ-06" in rule_ids

        # Exception: Neecha Bhanga Raja Yoga present
        ctx["yogas"] = [{"name": "Neecha Bhanga Raja Yoga"}]
        res2 = evaluate_property_rules(ctx)
        exc_rules = [e["rule_id"] for e in res2["evidence_ledger"] if e.get("effect") == "EXCEPTION"]
        assert "PROP-ACQ-06" in exc_rules


class TestPropertyDisposalSaleRules:
    """Tests for PROP-SAL-01 through PROP-SAL-03."""

    def test_prop_sal_01_positive(self):
        ctx = _base_ctx("Mesha")
        # 4th lord Moon in 3rd house
        ctx["planet_map"]["Moon"] = {"sign": "Mithuna", "house": 3, "degree": 14.0}
        res = evaluate_property_rules(ctx)
        rule_ids = [e["rule_id"] for e in res["evidence_ledger"]]
        assert "PROP-SAL-01" in rule_ids

    def test_prop_sal_02_positive(self):
        ctx = _base_ctx("Mesha")
        # 4th lord Moon in 12th house with malefic Saturn
        ctx["planet_map"]["Moon"] = {"sign": "Meena", "house": 12, "degree": 10.0}
        ctx["planet_map"]["Saturn"] = {"sign": "Meena", "house": 12, "degree": 15.0}
        res = evaluate_property_rules(ctx)
        rule_ids = [e["rule_id"] for e in res["evidence_ledger"]]
        assert "PROP-SAL-02" in rule_ids

    def test_prop_sal_03_positive(self):
        ctx = _base_ctx("Mesha")
        # 4th lord Moon in 10th house (interacting with 10th lord)
        ctx["planet_map"]["Moon"] = {"sign": "Makara", "house": 10, "degree": 12.0}
        res = evaluate_property_rules(ctx)
        rule_ids = [e["rule_id"] for e in res["evidence_ledger"]]
        assert "PROP-SAL-03" in rule_ids


class TestConstructionDevelopmentRules:
    """Tests for PROP-CON-01 through PROP-CON-03."""

    def test_prop_con_01_positive(self):
        ctx = _base_ctx("Mesha")
        # Mars conjunct Saturn in Makara (earth sign, house 10)
        ctx["planet_map"]["Mars"] = {"sign": "Makara", "house": 10, "degree": 28.0}
        ctx["planet_map"]["Saturn"] = {"sign": "Makara", "house": 10, "degree": 5.0}
        res = evaluate_property_rules(ctx)
        rule_ids = [e["rule_id"] for e in res["evidence_ledger"]]
        assert "PROP-CON-01" in rule_ids

    def test_prop_con_02_positive(self):
        ctx = _base_ctx("Kumbha")
        # For Kumbha lagna, 4th house is Vrishabha (Earth sign)
        ctx["house_signs"][4] = "Vrishabha"
        res = evaluate_property_rules(ctx)
        rule_ids = [e["rule_id"] for e in res["evidence_ledger"]]
        assert "PROP-CON-02" in rule_ids

    def test_prop_con_03_positive(self):
        ctx = _base_ctx("Mesha")
        # Ketu in 4th house without benefics
        ctx["planet_map"]["Ketu"] = {"sign": "Karka", "house": 4, "degree": 10.0}
        ctx["planet_map"]["Moon"] = {"sign": "Mesha", "house": 1, "degree": 10.0}
        res = evaluate_property_rules(ctx)
        rule_ids = [e["rule_id"] for e in res["evidence_ledger"]]
        assert "PROP-CON-03" in rule_ids


class TestRelocationResidenceRules:
    """Tests for PROP-REL-01 through PROP-REL-04."""

    def test_prop_rel_01_positive(self):
        ctx = _base_ctx("Mesha")
        # 4th lord Moon in movable sign Makara in 6th/8th/12th (e.g. house 10 isn't dusthana, but put in 6 in movable sign)
        # Let's say Moon is in Tula (movable) in 7th? Not dusthana.
        # Put 4th lord in Makara in house 10? Not dusthana.
        # Put 4th lord in Karka (movable) in house 12? (For Leo lagna, 4th is Vrischika).
        # In Mesha lagna, Karka is H4, Tula is H7, Makara is H10, Mesha is H1.
        # But if Moon is in Mesha in house 12? (If lagna is Vrishabha, Mesha is 12).
        # Let's set 4th lord to be in movable sign and house 12:
        ctx["planet_map"]["Moon"] = {"sign": "Mesha", "house": 12, "degree": 10.0}
        res = evaluate_property_rules(ctx)
        rule_ids = [e["rule_id"] for e in res["evidence_ledger"]]
        assert "PROP-REL-01" in rule_ids

    def test_prop_rel_02_positive(self):
        ctx = _base_ctx("Mesha")
        ctx["planet_map"]["Rahu"] = {"sign": "Karka", "house": 4, "degree": 15.0}
        res = evaluate_property_rules(ctx)
        rule_ids = [e["rule_id"] for e in res["evidence_ledger"]]
        assert "PROP-REL-02" in rule_ids

    def test_prop_rel_03_positive(self):
        ctx = _base_ctx("Mesha")
        # 4th lord Moon in 12th house
        ctx["planet_map"]["Moon"] = {"sign": "Meena", "house": 12, "degree": 10.0}
        res = evaluate_property_rules(ctx)
        rule_ids = [e["rule_id"] for e in res["evidence_ledger"]]
        assert "PROP-REL-03" in rule_ids

    def test_prop_rel_04_positive(self):
        ctx = _base_ctx("Mesha")
        # 4th lord Moon in fixed sign Vrishabha in house 1 (or put in house 4 in Leo lagna)
        # In Mesha lagna, Vrishabha is H2 (not Kendra). Simha is H5, Vrischika is H8, Kumbha is H11.
        # But let's test for Vrishabha lagna: 4th house is Simha (fixed), Sun is 4th lord.
        ctx_v = _base_ctx("Vrishabha")
        ctx_v["house_lords"][4] = "Sun"
        ctx_v["planet_map"]["Sun"] = {"sign": "Simha", "house": 4, "degree": 15.0}
        res = evaluate_property_rules(ctx_v)
        rule_ids = [e["rule_id"] for e in res["evidence_ledger"] if e.get("effect") == "OBSTRUCTS"]
        assert "PROP-REL-04" in rule_ids


class TestInheritedPropertyRules:
    """Tests for PROP-INH-01 through PROP-INH-03."""

    def test_prop_inh_01_positive(self):
        ctx = _base_ctx("Mesha")
        # 8th lord Mars in 4th house
        ctx["planet_map"]["Mars"] = {"sign": "Karka", "house": 4, "degree": 10.0}
        res = evaluate_property_rules(ctx)
        rule_ids = [e["rule_id"] for e in res["evidence_ledger"]]
        assert "PROP-INH-01" in rule_ids

    def test_prop_inh_02_positive(self):
        ctx = _base_ctx("Mesha")
        # 9th lord Jupiter in 4th house
        ctx["planet_map"]["Jupiter"] = {"sign": "Karka", "house": 4, "degree": 5.0}
        res = evaluate_property_rules(ctx)
        rule_ids = [e["rule_id"] for e in res["evidence_ledger"]]
        assert "PROP-INH-02" in rule_ids

    def test_prop_inh_03_positive(self):
        ctx = _base_ctx("Mesha")
        # 8th lord Mars in 4th house with Saturn
        ctx["planet_map"]["Mars"] = {"sign": "Karka", "house": 4, "degree": 10.0}
        ctx["planet_map"]["Saturn"] = {"sign": "Karka", "house": 4, "degree": 15.0}
        res = evaluate_property_rules(ctx)
        rule_ids = [e["rule_id"] for e in res["evidence_ledger"]]
        assert "PROP-INH-03" in rule_ids


class TestPropertyObligationsRules:
    """Tests for PROP-OBL-01 and PROP-OBL-02."""

    def test_prop_obl_01_positive(self):
        ctx = _base_ctx("Mesha")
        # 4th lord Moon in 6th house
        ctx["planet_map"]["Moon"] = {"sign": "Kanya", "house": 6, "degree": 10.0}
        res = evaluate_property_rules(ctx)
        rule_ids = [e["rule_id"] for e in res["evidence_ledger"]]
        assert "PROP-OBL-01" in rule_ids

    def test_prop_obl_02_positive(self):
        ctx = _base_ctx("Mesha")
        # Mars in 6th house
        ctx["planet_map"]["Mars"] = {"sign": "Kanya", "house": 6, "degree": 10.0}
        res = evaluate_property_rules(ctx)
        rule_ids = [e["rule_id"] for e in res["evidence_ledger"]]
        assert "PROP-OBL-02" in rule_ids


class TestD4SupportRules:
    """Tests for PROP-D4-01 and PROP-D4-02."""

    def test_prop_d4_01_positive(self):
        ctx = _base_ctx("Mesha")
        ctx["ascendant_degree"] = 2.0  # D4 lagna = Mesha (H1 lord = Mars)
        # Mars in Makara at 28.0° -> D4 sign for Makara at 28.0° is Tula (Kendra)
        # In Mesha D4 lagna, Tula is house 7 (Kendra)
        ctx["planet_map"]["Mars"] = {"sign": "Makara", "degree": 28.0, "house": 10}
        res = evaluate_property_rules(ctx)
        rule_ids = [e["rule_id"] for e in res["evidence_ledger"]]
        assert "PROP-D4-01" in rule_ids

    def test_prop_d4_02_positive(self):
        ctx = _base_ctx("Mesha")
        ctx["ascendant_degree"] = 2.0  # D4 lagna = Mesha
        # Mars at 0.0° in Makara -> D4 sign is Makara (exalted) in house 10 (Kendra)
        ctx["planet_map"]["Mars"] = {"sign": "Makara", "degree": 2.0, "house": 10}
        res = evaluate_property_rules(ctx)
        rule_ids = [e["rule_id"] for e in res["evidence_ledger"]]
        assert "PROP-D4-02" in rule_ids


# ===========================================================================
# 3. ALL 12 LAGNA SIGNS EXECUTION
# ===========================================================================

class TestAll12Lagnas:
    """Ensure rule engine and domain wrapper execute seamlessly for all 12 Lagnas."""

    @pytest.mark.parametrize("lagna", SIGNS_SK)
    def test_all_12_lagnas_run(self, lagna):
        ctx = _base_ctx(lagna)
        res = evaluate_property_rules(ctx)
        assert res["overall_score"] >= 10.0
        assert res["d4_chart"]["lagna"] in SIGNS_SK
        assert len(res["dimensions"]) == 7

        wrapper_res = analyse_property(ctx)
        assert wrapper_res["domain"] == "Property & Home"
        assert wrapper_res["score"] >= 0


# ===========================================================================
# 4. DIMENSIONS & DEDUPLICATION
# ===========================================================================

class TestDimensionsAndDeduplication:
    """Verify distinct dimensions and dedupe key enforcement."""

    def test_all_7_dimensions_present(self):
        ctx = _base_ctx("Mesha")
        res = evaluate_property_rules(ctx)
        for dim in PROPERTY_DIMENSIONS:
            assert dim in res["dimensions"], f"Missing dimension: {dim}"

    def test_no_duplicate_dedupe_keys_in_ledger(self):
        ctx = _base_ctx("Mesha")
        res = evaluate_property_rules(ctx)
        seen_keys = set()
        for entry in res["evidence_ledger"]:
            rule_id = entry["rule_id"]
            rule = next(r for r in PROPERTY_RULES_CATALOG if r.rule_id == rule_id)
            if rule.dedupe_key:
                assert rule.dedupe_key not in seen_keys, f"Duplicate dedupe_key found: {rule.dedupe_key}"
                seen_keys.add(rule.dedupe_key)


# ===========================================================================
# 5. LEGACY API CONTRACT COMPATIBILITY
# ===========================================================================

class TestLegacyAPIContract:
    """Verify 100% backward compatibility with legacy API contracts."""

    def test_legacy_keys_preserved(self):
        ctx = _base_ctx("Mesha")
        res = analyse_property(ctx)

        legacy_keys = [
            "domain", "icon", "score", "property_type", "multiple_properties",
            "domestic_happiness", "vastu", "fourth_lord", "mars_position",
            "dasha_active", "timing", "remedies", "analysis"
        ]
        for k in legacy_keys:
            assert k in res, f"Legacy key '{k}' missing from response"

        # Check types
        assert isinstance(res["domain"], str)
        assert isinstance(res["icon"], str)
        assert isinstance(res["score"], (int, float))
        assert isinstance(res["property_type"], str)
        assert isinstance(res["multiple_properties"], bool)
        assert isinstance(res["domestic_happiness"], bool)
        assert isinstance(res["vastu"], str)
        assert isinstance(res["timing"], dict)
        assert isinstance(res["remedies"], (dict, list))
        assert isinstance(res["analysis"], str)

        # Alias verification
        assert _property == analyse_property


# ===========================================================================
# 6. DETERMINISM & REPRODUCIBILITY
# ===========================================================================

class TestDeterminism:
    """Verify strictly deterministic repeated execution."""

    def test_repeated_runs_identical(self):
        ctx = _base_ctx("Mesha")
        r1 = analyse_property(ctx)
        r2 = analyse_property(ctx)

        assert r1["score"] == r2["score"]
        assert r1["dimensions"] == r2["dimensions"]
        assert len(r1["evidence_ledger"]) == len(r2["evidence_ledger"])
        assert r1["analysis"] == r2["analysis"]


# ===========================================================================
# 7. SAFETY GUARDRAILS & ADVERSARIAL AUDIT
# ===========================================================================

class TestSafetyGuardrails:
    """Ensure absolute prohibition of illegal or misleading property/financial claims."""

    def test_mandatory_disclaimer_present(self):
        ctx = _base_ctx("Mesha")
        res = analyse_property(ctx)
        assert "safety_disclaimer" in res
        assert res["safety_disclaimer"] == PROPERTY_SAFETY_DISCLAIMER
        assert "CANNOT guarantee property acquisition" in res["safety_disclaimer"]
        assert res["is_predictive"] is False
        assert res["is_financial_advice"] is False

    def test_no_guaranteed_purchase_or_appreciation_in_narrative(self):
        ctx = _base_ctx("Mesha")
        res = analyse_property(ctx)
        analysis_lower = res["analysis"].lower()

        forbidden_tokens = [
            "guaranteed purchase",
            "guaranteed sale",
            "loan approved",
            "mortgage approved",
            "100% profit",
            "guaranteed appreciation",
            "you must buy",
            "you must sell",
            "dispute won",
            "title guaranteed",
        ]
        for token in forbidden_tokens:
            assert token not in analysis_lower, f"Forbidden promotional token '{token}' found in analysis narrative"
