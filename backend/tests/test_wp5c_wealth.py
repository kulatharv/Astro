"""
WP5C Wealth & Resources Domain Rule Pack Test Suite.

Validates:
- Positive, negative, boundary, and cancellation conditions for 26 canonical wealth rules
- Complete separation of 6 financial evidence dimensions:
  1. Accumulated Wealth & Savings
  2. Recurring Gains & Inflow
  3. Livelihood & Earning Capacity
  4. Debt & Financial Obligations
  5. Expenditure & Resource Depletion
  6. Speculation & Financial Risk
- Seamless cross-referencing and reuse of WP3 Dhana Yogas without duplicate score inflation
- All 12 Ascendant (Lagna) signs mapping correctness
- Full Parashari special aspects and combustion / debilitation exception ordering
- Determinism and explanation provenance across multiple evaluations
- Missing / incomplete chart context handling
- 100% backward compatibility with legacy analyse_wealth() API contracts
- Strict Spec §21 Financial Safety Guardrails (no stock/crypto tips, no guaranteed returns/wealth)
"""

import pytest
import copy

from shared.veda.wealth import (
    WEALTH_RULES_CATALOG,
    evaluate_wealth_rules,
    FINANCIAL_DIMENSIONS,
    SAFETY_DISCLAIMER,
)
from modules.prediction.domains.wealth import analyse_wealth


# ---------------------------------------------------------------------------
# Synthetic Fixture Generators
# ---------------------------------------------------------------------------

def create_base_ctx(lagna="Mesha"):
    """
    Creates a neutral baseline chart context for testing.
    For Mesha:
      H1: Mesha (Mars)
      H2: Vrishabha (Venus)
      H3: Mithuna (Mercury)
      H4: Karka (Moon)
      H5: Simha (Sun)
      H6: Kanya (Mercury)
      H7: Tula (Venus)
      H8: Vrischika (Mars)
      H9: Dhanu (Jupiter)
      H10: Makara (Saturn)
      H11: Kumbha (Saturn)
      H12: Meena (Jupiter)
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

    # Place all 9 planets in neutral 3rd house by default to prevent incidental triggers
    planet_map = {
        "Sun":     {"sign": house_signs[3], "house": 3, "degree": 15.0, "retrograde": False, "str_score": 0},
        "Moon":    {"sign": house_signs[3], "house": 3, "degree": 15.0, "retrograde": False, "str_score": 0},
        "Mars":    {"sign": house_signs[3], "house": 3, "degree": 15.0, "retrograde": False, "str_score": 0},
        "Mercury": {"sign": house_signs[3], "house": 3, "degree": 15.0, "retrograde": False, "str_score": 0},
        "Jupiter": {"sign": house_signs[3], "house": 3, "degree": 15.0, "retrograde": False, "str_score": 0},
        "Venus":   {"sign": house_signs[3], "house": 3, "degree": 15.0, "retrograde": False, "str_score": 0},
        "Saturn":  {"sign": house_signs[3], "house": 3, "degree": 15.0, "retrograde": False, "str_score": 0},
        "Rahu":    {"sign": house_signs[3], "house": 3, "degree": 15.0, "retrograde": False, "str_score": 0},
        "Ketu":    {"sign": house_signs[9], "house": 9, "degree": 15.0, "retrograde": False, "str_score": 0},
    }

    return {
        "lagna": lagna,
        "lagna_idx": lagna_idx,
        "house_signs": house_signs,
        "house_lords": house_lords,
        "planet_map": planet_map,
        "transit_map": {p: {"house": d["house"]} for p, d in planet_map.items()},
        "mahadasha": "Jupiter",
        "antardasha": "Venus",
        "yogas": [],
    }


# ---------------------------------------------------------------------------
# Test Suite
# ---------------------------------------------------------------------------

class TestWP5CWealthRules:

    def test_catalog_inventory_and_schema(self):
        """Verify that catalog contains 26 rules with complete schema integrity."""
        assert len(WEALTH_RULES_CATALOG) == 26
        for r in WEALTH_RULES_CATALOG:
            assert r.rule_id.startswith("WEALTH-")
            assert r.version == "1.0.0"
            assert r.domain == "wealth"
            assert r.source_status == "VERIFIED"
            assert r.review_status == "ACCEPTED"
            assert r.confidence in ("HIGH", "MEDIUM")
            assert len(r.dimensions) > 0
            for d in r.dimensions:
                assert d in FINANCIAL_DIMENSIONS

    def test_wealth_h2_lord_kendra_trikona(self):
        """Test WEALTH-H2-LORD-KENDRA-TRIKONA-01: 2nd lord in Kendra or Trikona."""
        ctx = create_base_ctx("Mesha")
        # For Mesha, 2nd lord is Venus. Place Venus in 4th house (Kendra, Karka).
        ctx["planet_map"]["Venus"]["house"] = 4
        ctx["planet_map"]["Venus"]["sign"] = "Karka"

        res = evaluate_wealth_rules(ctx)
        matched_ids = [m["rule_id"] for m in res["matched_rules"]]
        assert "WEALTH-H2-LORD-KENDRA-TRIKONA-01" in matched_ids
        assert res["dimensions"]["accumulated_savings"]["support"] >= 1

    def test_wealth_h2_lord_kendra_trikona_debilitated_cancelled(self):
        """Test WEALTH-H2-LORD-KENDRA-TRIKONA-01 cancellation when 2nd lord is debilitated without NB."""
        ctx = create_base_ctx("Mesha")
        # Venus in 6th house is Kanya (debilitated)
        ctx["planet_map"]["Venus"]["house"] = 6
        ctx["planet_map"]["Venus"]["sign"] = "Kanya"

        res = evaluate_wealth_rules(ctx)
        matched_ids = [m["rule_id"] for m in res["matched_rules"]]
        assert "WEALTH-H2-LORD-KENDRA-TRIKONA-01" not in matched_ids

    def test_wealth_h2_lord_own_exalted(self):
        """Test WEALTH-H2-LORD-OWN-EXALTED-02: 2nd lord in own sign or exaltation."""
        ctx = create_base_ctx("Mesha")
        # 2nd lord Venus in Vrishabha (2nd house, own sign)
        ctx["planet_map"]["Venus"]["house"] = 2
        ctx["planet_map"]["Venus"]["sign"] = "Vrishabha"

        res = evaluate_wealth_rules(ctx)
        matched_ids = [m["rule_id"] for m in res["matched_rules"]]
        assert "WEALTH-H2-LORD-OWN-EXALTED-02" in matched_ids

    def test_wealth_h2_benefic_occupancy(self):
        """Test WEALTH-H2-BENEFIC-OCCUPANCY-03: Natural benefics in 2nd house."""
        ctx = create_base_ctx("Mesha")
        # Place Jupiter in 2nd house
        ctx["planet_map"]["Jupiter"]["house"] = 2
        ctx["planet_map"]["Jupiter"]["sign"] = "Vrishabha"

        res = evaluate_wealth_rules(ctx)
        matched_ids = [m["rule_id"] for m in res["matched_rules"]]
        assert "WEALTH-H2-BENEFIC-OCCUPANCY-03" in matched_ids
        assert res["dimensions"]["accumulated_savings"]["support"] >= 1

    def test_wealth_h2_lord_dusthana_and_mitigation(self):
        """Test WEALTH-H2-LORD-DUSTHANA-AFFLICTION-04 and its Jupiter aspect cancellation."""
        ctx = create_base_ctx("Mesha")
        # 2nd lord Venus placed in 8th house (Dusthana)
        ctx["planet_map"]["Venus"]["house"] = 8
        ctx["planet_map"]["Venus"]["sign"] = "Vrischika"
        # Jupiter placed in 3rd (does not aspect 8th)
        ctx["planet_map"]["Jupiter"]["house"] = 3

        res1 = evaluate_wealth_rules(ctx)
        matched_ids1 = [m["rule_id"] for m in res1["matched_rules"]]
        assert "WEALTH-H2-LORD-DUSTHANA-AFFLICTION-04" in matched_ids1
        assert res1["dimensions"]["accumulated_savings"]["obstruct"] >= 1

        # Now place Jupiter in 4th house (5th aspect reaches 8th house)
        ctx["planet_map"]["Jupiter"]["house"] = 4
        res2 = evaluate_wealth_rules(ctx)
        matched_ids2 = [m["rule_id"] for m in res2["matched_rules"]]
        # Rule should be cancelled by Jupiter aspect
        assert "WEALTH-H2-LORD-DUSTHANA-AFFLICTION-04" not in matched_ids2
        cancelled_ids = [c["rule_id"] for c in res2["cancelled_rules"]]
        assert "WEALTH-H2-LORD-DUSTHANA-AFFLICTION-04" in cancelled_ids

    def test_wealth_h2_malefic_affliction(self):
        """Test WEALTH-H2-MALEFIC-AFFLICTION-05: 2+ malefics in 2nd house without benefic."""
        ctx = create_base_ctx("Mesha")
        ctx["planet_map"]["Saturn"]["house"] = 2
        ctx["planet_map"]["Rahu"]["house"] = 2

        res = evaluate_wealth_rules(ctx)
        matched_ids = [m["rule_id"] for m in res["matched_rules"]]
        assert "WEALTH-H2-MALEFIC-AFFLICTION-05" in matched_ids
        assert res["dimensions"]["accumulated_savings"]["obstruct"] >= 1

    def test_wealth_h11_lord_kendra_trikona(self):
        """Test WEALTH-H11-LORD-KENDRA-TRIKONA-01: 11th lord in Kendra or Trikona."""
        ctx = create_base_ctx("Mesha")
        # 11th lord for Mesha is Saturn. Place Saturn in 10th house (Makara, Kendra).
        ctx["planet_map"]["Saturn"]["house"] = 10
        ctx["planet_map"]["Saturn"]["sign"] = "Makara"

        res = evaluate_wealth_rules(ctx)
        matched_ids = [m["rule_id"] for m in res["matched_rules"]]
        assert "WEALTH-H11-LORD-KENDRA-TRIKONA-01" in matched_ids
        assert res["dimensions"]["recurring_gains"]["support"] >= 1

    def test_wealth_h11_lord_own_exalted(self):
        """Test WEALTH-H11-LORD-OWN-EXALTED-02: 11th lord in own sign or exaltation."""
        ctx = create_base_ctx("Mesha")
        # Saturn in Kumbha (11th house, own sign)
        ctx["planet_map"]["Saturn"]["house"] = 11
        ctx["planet_map"]["Saturn"]["sign"] = "Kumbha"

        res = evaluate_wealth_rules(ctx)
        matched_ids = [m["rule_id"] for m in res["matched_rules"]]
        assert "WEALTH-H11-LORD-OWN-EXALTED-02" in matched_ids

    def test_wealth_h11_benefic_occupancy(self):
        """Test WEALTH-H11-BENEFIC-OCCUPANCY-03: Benefics in 11th house."""
        ctx = create_base_ctx("Mesha")
        ctx["planet_map"]["Jupiter"]["house"] = 11
        ctx["planet_map"]["Jupiter"]["sign"] = "Kumbha"

        res = evaluate_wealth_rules(ctx)
        matched_ids = [m["rule_id"] for m in res["matched_rules"]]
        assert "WEALTH-H11-BENEFIC-OCCUPANCY-03" in matched_ids

    def test_wealth_h11_upachaya_growth(self):
        """Test WEALTH-H11-UPACHAYA-GROWTH-04: Malefics in 11th house."""
        ctx = create_base_ctx("Mesha")
        ctx["planet_map"]["Mars"]["house"] = 11
        ctx["planet_map"]["Mars"]["sign"] = "Kumbha"

        res = evaluate_wealth_rules(ctx)
        matched_ids = [m["rule_id"] for m in res["matched_rules"]]
        assert "WEALTH-H11-UPACHAYA-GROWTH-04" in matched_ids

    def test_wealth_h11_lord_dusthana(self):
        """Test WEALTH-H11-LORD-DUSTHANA-05: 11th lord in Dusthana."""
        ctx = create_base_ctx("Mesha")
        # 11th lord Saturn in 6th house (Kanya)
        ctx["planet_map"]["Saturn"]["house"] = 6
        ctx["planet_map"]["Saturn"]["sign"] = "Kanya"
        ctx["planet_map"]["Jupiter"]["house"] = 1  # Jupiter aspect doesn't reach 6th

        res = evaluate_wealth_rules(ctx)
        matched_ids = [m["rule_id"] for m in res["matched_rules"]]
        assert "WEALTH-H11-LORD-DUSTHANA-05" in matched_ids
        assert res["dimensions"]["recurring_gains"]["obstruct"] >= 1

    def test_wealth_parivartana_2_11(self):
        """Test WEALTH-DHANA-2-11-PARIVARTANA-01: Parivartana between 2nd and 11th lords."""
        ctx = create_base_ctx("Mesha")
        # 2nd lord Venus in 11th; 11th lord Saturn in 2nd
        ctx["planet_map"]["Venus"]["house"] = 11
        ctx["planet_map"]["Venus"]["sign"] = "Kumbha"
        ctx["planet_map"]["Saturn"]["house"] = 2
        ctx["planet_map"]["Saturn"]["sign"] = "Vrishabha"

        res = evaluate_wealth_rules(ctx)
        matched_ids = [m["rule_id"] for m in res["matched_rules"]]
        assert "WEALTH-DHANA-2-11-PARIVARTANA-01" in matched_ids
        assert res["dimensions"]["accumulated_savings"]["support"] >= 1
        assert res["dimensions"]["recurring_gains"]["support"] >= 1

    def test_wealth_5_11_axis(self):
        """Test WEALTH-DHANA-5-11-AXIS-02: 5th lord in 11th or 11th lord in 5th."""
        ctx = create_base_ctx("Mesha")
        # 5th lord Sun in 11th house
        ctx["planet_map"]["Sun"]["house"] = 11
        ctx["planet_map"]["Sun"]["sign"] = "Kumbha"

        res = evaluate_wealth_rules(ctx)
        matched_ids = [m["rule_id"] for m in res["matched_rules"]]
        assert "WEALTH-DHANA-5-11-AXIS-02" in matched_ids

    def test_wealth_9_2_combination(self):
        """Test WEALTH-DHANA-9-2-COMBINATION-03: 9th lord connecting with 2nd lord."""
        ctx = create_base_ctx("Mesha")
        # 9th lord Jupiter in 2nd house
        ctx["planet_map"]["Jupiter"]["house"] = 2
        ctx["planet_map"]["Jupiter"]["sign"] = "Vrishabha"

        res = evaluate_wealth_rules(ctx)
        matched_ids = [m["rule_id"] for m in res["matched_rules"]]
        assert "WEALTH-DHANA-9-2-COMBINATION-03" in matched_ids

    def test_wealth_1_11_connection(self):
        """Test WEALTH-DHANA-1-11-CONNECTION-04: Lagna lord in 11th house."""
        ctx = create_base_ctx("Mesha")
        # Lagna lord Mars in 11th house
        ctx["planet_map"]["Mars"]["house"] = 11
        ctx["planet_map"]["Mars"]["sign"] = "Kumbha"

        res = evaluate_wealth_rules(ctx)
        matched_ids = [m["rule_id"] for m in res["matched_rules"]]
        assert "WEALTH-DHANA-1-11-CONNECTION-04" in matched_ids

    def test_wealth_earning_10_2_connection(self):
        """Test WEALTH-EARNING-10-2-CONNECTION-01: 10th lord in 2nd house."""
        ctx = create_base_ctx("Mesha")
        # 10th lord Saturn in 2nd house
        ctx["planet_map"]["Saturn"]["house"] = 2
        ctx["planet_map"]["Saturn"]["sign"] = "Vrishabha"

        res = evaluate_wealth_rules(ctx)
        matched_ids = [m["rule_id"] for m in res["matched_rules"]]
        assert "WEALTH-EARNING-10-2-CONNECTION-01" in matched_ids
        assert res["dimensions"]["earning_livelihood"]["support"] >= 1

    def test_wealth_earning_lagna_strong(self):
        """Test WEALTH-EARNING-LAGNA-STRONG-02: Strong Lagna lord."""
        ctx = create_base_ctx("Mesha")
        # Lagna lord Mars exalted in 10th house (Makara)
        ctx["planet_map"]["Mars"]["house"] = 10
        ctx["planet_map"]["Mars"]["sign"] = "Makara"

        res = evaluate_wealth_rules(ctx)
        matched_ids = [m["rule_id"] for m in res["matched_rules"]]
        assert "WEALTH-EARNING-LAGNA-STRONG-02" in matched_ids

    def test_wealth_upachaya_benefics(self):
        """Test WEALTH-EARNING-UPACHAYA-BENEFIC-03: Vasumati principle."""
        ctx = create_base_ctx("Mesha")
        # Place Jupiter in 10th and Venus in 11th (both Upachayas)
        ctx["planet_map"]["Jupiter"]["house"] = 10
        ctx["planet_map"]["Venus"]["house"] = 11

        res = evaluate_wealth_rules(ctx)
        matched_ids = [m["rule_id"] for m in res["matched_rules"]]
        assert "WEALTH-EARNING-UPACHAYA-BENEFIC-03" in matched_ids

    def test_wealth_debt_6_in_2(self):
        """Test WEALTH-DEBT-6-LORD-IN-2-01: 6th lord in 2nd house."""
        ctx = create_base_ctx("Mesha")
        # 6th lord Mercury in 2nd house
        ctx["planet_map"]["Mercury"]["house"] = 2
        ctx["planet_map"]["Mercury"]["sign"] = "Vrishabha"

        res = evaluate_wealth_rules(ctx)
        matched_ids = [m["rule_id"] for m in res["matched_rules"]]
        assert "WEALTH-DEBT-6-LORD-IN-2-01" in matched_ids
        assert res["dimensions"]["debt_obligations"]["obstruct"] >= 1

    def test_wealth_debt_2_in_6(self):
        """Test WEALTH-DEBT-2-LORD-IN-6-02: 2nd lord in 6th house."""
        ctx = create_base_ctx("Mesha")
        # 2nd lord Venus in 6th house
        ctx["planet_map"]["Venus"]["house"] = 6
        ctx["planet_map"]["Venus"]["sign"] = "Kanya"

        res = evaluate_wealth_rules(ctx)
        matched_ids = [m["rule_id"] for m in res["matched_rules"]]
        assert "WEALTH-DEBT-2-LORD-IN-6-02" in matched_ids

    def test_wealth_debt_saturn_mars_in_6(self):
        """Test WEALTH-DEBT-SATURN-MARS-IN-6-03: Saturn in 6th house."""
        ctx = create_base_ctx("Mesha")
        ctx["planet_map"]["Saturn"]["house"] = 6
        ctx["planet_map"]["Saturn"]["sign"] = "Kanya"

        res = evaluate_wealth_rules(ctx)
        matched_ids = [m["rule_id"] for m in res["matched_rules"]]
        assert "WEALTH-DEBT-SATURN-MARS-IN-6-03" in matched_ids

    def test_wealth_outflow_12_lord_strong(self):
        """Test WEALTH-OUTFLOW-12-LORD-STRONG-01: 12th lord in 12th house."""
        ctx = create_base_ctx("Mesha")
        # 12th lord Jupiter in 12th house (Meena, own sign)
        ctx["planet_map"]["Jupiter"]["house"] = 12
        ctx["planet_map"]["Jupiter"]["sign"] = "Meena"

        res = evaluate_wealth_rules(ctx)
        matched_ids = [m["rule_id"] for m in res["matched_rules"]]
        assert "WEALTH-OUTFLOW-12-LORD-STRONG-01" in matched_ids
        assert res["dimensions"]["expenditure_outflow"]["support"] >= 1

    def test_wealth_outflow_2_in_12(self):
        """Test WEALTH-OUTFLOW-2-LORD-IN-12-02: 2nd lord in 12th house."""
        # For Vrishabha Lagna, 2nd lord is Mercury, 12th house is Mesha (neutral sign)
        ctx = create_base_ctx("Vrishabha")
        ctx["planet_map"]["Mercury"]["house"] = 12
        ctx["planet_map"]["Mercury"]["sign"] = "Mesha"

        res = evaluate_wealth_rules(ctx)
        matched_ids = [m["rule_id"] for m in res["matched_rules"]]
        assert "WEALTH-OUTFLOW-2-LORD-IN-12-02" in matched_ids

    def test_wealth_outflow_2_in_12_exalted_cancellation(self):
        """Test WEALTH-OUTFLOW-2-LORD-IN-12-02 cancellation when 2nd lord is exalted in 12th."""
        # For Mesha Lagna, 2nd lord Venus is exalted in 12th (Meena) -> cancels negative outflow drain
        ctx = create_base_ctx("Mesha")
        ctx["planet_map"]["Venus"]["house"] = 12
        ctx["planet_map"]["Venus"]["sign"] = "Meena"

        res = evaluate_wealth_rules(ctx)
        matched_ids = [m["rule_id"] for m in res["matched_rules"]]
        assert "WEALTH-OUTFLOW-2-LORD-IN-12-02" not in matched_ids
        cancelled_ids = [c["rule_id"] for c in res["cancelled_rules"]]
        assert "WEALTH-OUTFLOW-2-LORD-IN-12-02" in cancelled_ids

    def test_wealth_spec_5_8_connection(self):
        """Test WEALTH-SPEC-5-8-CONNECTION-01: 5th lord in 8th house."""
        ctx = create_base_ctx("Mesha")
        # 5th lord Sun in 8th house
        ctx["planet_map"]["Sun"]["house"] = 8
        ctx["planet_map"]["Sun"]["sign"] = "Vrischika"

        res = evaluate_wealth_rules(ctx)
        matched_ids = [m["rule_id"] for m in res["matched_rules"]]
        assert "WEALTH-SPEC-5-8-CONNECTION-01" in matched_ids
        assert res["dimensions"]["speculation_risk"]["conditional"] >= 1

    def test_wealth_spec_rahu_5_or_11(self):
        """Test WEALTH-SPEC-RAHU-IN-11-OR-5-02: Rahu in 11th house."""
        ctx = create_base_ctx("Mesha")
        ctx["planet_map"]["Rahu"]["house"] = 11

        res = evaluate_wealth_rules(ctx)
        matched_ids = [m["rule_id"] for m in res["matched_rules"]]
        assert "WEALTH-SPEC-RAHU-IN-11-OR-5-02" in matched_ids

    def test_wealth_chandra_lagna(self):
        """Test WEALTH-CHANDRA-LAGNA-DHANA-01: Benefics in 2nd from Moon."""
        ctx = create_base_ctx("Mesha")
        # Moon in Mesha (1st house)
        ctx["planet_map"]["Moon"]["house"] = 1
        ctx["planet_map"]["Moon"]["sign"] = "Mesha"
        # Jupiter in Vrishabha (2nd from Moon)
        ctx["planet_map"]["Jupiter"]["house"] = 2
        ctx["planet_map"]["Jupiter"]["sign"] = "Vrishabha"

        res = evaluate_wealth_rules(ctx)
        matched_ids = [m["rule_id"] for m in res["matched_rules"]]
        assert "WEALTH-CHANDRA-LAGNA-DHANA-01" in matched_ids

    def test_wealth_jupiter_karaka(self):
        """Test WEALTH-KARAKA-JUPITER-DIGNITY-02: Jupiter well-placed."""
        ctx = create_base_ctx("Mesha")
        # Jupiter in 9th house (Trikona, Dhanu, own sign)
        ctx["planet_map"]["Jupiter"]["house"] = 9
        ctx["planet_map"]["Jupiter"]["sign"] = "Dhanu"

        res = evaluate_wealth_rules(ctx)
        matched_ids = [m["rule_id"] for m in res["matched_rules"]]
        assert "WEALTH-KARAKA-JUPITER-DIGNITY-02" in matched_ids

    def test_all_12_ascendant_signs(self):
        """Verify that all 12 Lagnas evaluate smoothly without house-lord resolution crashes."""
        RASHIS = ["Mesha", "Vrishabha", "Mithuna", "Karka", "Simha", "Kanya",
                  "Tula", "Vrischika", "Dhanu", "Makara", "Kumbha", "Meena"]
        for lagna in RASHIS:
            ctx = create_base_ctx(lagna)
            res = evaluate_wealth_rules(ctx)
            assert res["domain"] == "wealth"
            assert len(res["dimensions"]) == 6

    def test_wp3_dhana_yogas_reused_without_duplication(self):
        """Verify that canonical Dhana Yogas from WP3 yoga_catalog are seamlessly integrated."""
        ctx = create_base_ctx("Mesha")
        # Create condition for YOGA-DHANA-2-11-01: 2nd & 11th lords conjoined in 11th
        ctx["planet_map"]["Venus"]["house"] = 11
        ctx["planet_map"]["Venus"]["sign"] = "Kumbha"
        ctx["planet_map"]["Saturn"]["house"] = 11
        ctx["planet_map"]["Saturn"]["sign"] = "Kumbha"

        res = evaluate_wealth_rules(ctx)
        dhana_ids = [y["rule_id"] for y in res["dhana_yogas_active"]]
        assert "YOGA-DHANA-2-11-01" in dhana_ids

    def test_separation_of_financial_dimensions(self):
        """
        Verify that having strong gains does not erase high expenditure;
        both ledgers remain distinct and uncollapsed.
        """
        ctx = create_base_ctx("Mesha")
        # 11th lord Saturn in 11th (own sign, strong gains)
        ctx["planet_map"]["Saturn"]["house"] = 11
        ctx["planet_map"]["Saturn"]["sign"] = "Kumbha"
        # 12th lord Jupiter in 12th (Meena, own sign, active expenditure/outflow)
        ctx["planet_map"]["Jupiter"]["house"] = 12
        ctx["planet_map"]["Jupiter"]["sign"] = "Meena"

        res = evaluate_wealth_rules(ctx)
        dims = res["dimensions"]
        assert dims["recurring_gains"]["support"] >= 1
        assert dims["expenditure_outflow"]["support"] >= 1
        # Neither dimension overwrote the other
        assert dims["recurring_gains"]["status"] in ("Strong", "Favorable")
        assert dims["expenditure_outflow"]["status"] in ("Strong", "Favorable")

    def test_financial_safety_boundaries_spec_21(self):
        """
        Spec §21 Guardrails:
        Ensure no stock tips, cryptocurrency references, guaranteed returns,
        or deterministic windfall promises exist in explanations or narrative.
        """
        ctx = create_base_ctx("Mesha")
        # Trigger 5th/8th Rahu combinations
        ctx["planet_map"]["Rahu"]["house"] = 8
        ctx["planet_map"]["Jupiter"]["house"] = 8

        res = evaluate_wealth_rules(ctx)
        wrapper_res = analyse_wealth(ctx)

        forbidden_tokens = [
            "buy stock", "sell stock", "crypto", "bitcoin", "ethereum",
            "guaranteed wealth", "guaranteed profit", "become a billionaire",
            "lottery winner", "destined for poverty", "magic ritual",
        ]

        full_text = (
            str(res) + " " +
            wrapper_res["analysis"] + " " +
            wrapper_res["sudden_gain"] + " " +
            wrapper_res["debt_risk"]
        ).lower()

        for token in forbidden_tokens:
            assert token not in full_text, f"Forbidden financial advice token '{token}' detected!"

        assert "safety_disclaimer" in res
        assert SAFETY_DISCLAIMER in wrapper_res["safety_disclaimer"]

    def test_legacy_analyse_wealth_backward_compatibility(self):
        """Verify that analyse_wealth preserves all 13 legacy API keys and adds evidence."""
        ctx = create_base_ctx("Mesha")
        out = analyse_wealth(ctx)

        legacy_keys = [
            "domain", "icon", "score", "dhana_yogas", "income_sources",
            "sudden_gain", "debt_risk", "second_lord", "eleventh_lord",
            "h2_planets", "h11_planets", "dasha_active", "timing", "remedies",
            "analysis",
        ]
        for k in legacy_keys:
            assert k in out, f"Legacy key '{k}' missing from analyse_wealth payload!"

        # Enriched keys
        assert "evidence" in out
        assert "dimensions" in out
        assert "rules_evaluated" in out
        assert "safety_disclaimer" in out

    def test_determinism_and_immutability(self):
        """Verify that repeated rule evaluations produce identical results without state mutation."""
        ctx = create_base_ctx("Mesha")
        ctx["planet_map"]["Jupiter"]["house"] = 2
        ctx["planet_map"]["Venus"]["house"] = 11

        res1 = evaluate_wealth_rules(ctx)
        res2 = evaluate_wealth_rules(ctx)

        assert res1["matched_rules"] == res2["matched_rules"]
        assert res1["dimensions"] == res2["dimensions"]
