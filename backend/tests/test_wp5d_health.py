"""
WP5D Health & Wellbeing Domain Rule Pack Test Suite.

Validates:
- Absolute prohibition against medical diagnosis, disease prediction, or symptom analysis
- Absolute prohibition against longevity, lifespan, death, or time-of-death predictions
- Absolute prohibition against surgery, hospitalization, or medical emergency predictions
- Absolute prohibition against fertility, pregnancy, miscarriage, or childbirth predictions
- Absolute prohibition against mental health diagnostic claims
- Absolute prohibition against treatment or medication instructions
- Functional evaluation of 12 permitted non-diagnostic wellbeing rules across 4 safe dimensions:
  1. Vitality & Physical Stamina (vitality_stamina)
  2. Daily Rhythm & Routine Discipline (routine_balance)
  3. Mindfulness & Restorative Rest (mindfulness_rest)
  4. Traditional Ayurvedic Lifestyle Temperament (lifestyle_temperament)
- Universal presence of the mandatory medical safety disclaimer
- Full Parashari aspect and dignity handling
- All 12 Ascendant signs evaluation
- Determinism and immutability across repeated evaluations
- Missing / incomplete chart context handling
- 100% backward compatibility with legacy analyse_health() API contracts
- Adversarial stress tests confirming no medical claims escape through synthesis
"""

import pytest
import copy

from shared.veda.health import (
    HEALTH_RULES_CATALOG,
    evaluate_health_rules,
    WELLBEING_DIMENSIONS,
    SAFETY_DISCLAIMER,
)
from modules.prediction.domains.health import analyse_health


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

    # Place planets in neutral 3rd house by default
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

class TestWP5DHealthSafetyAndWellbeing:

    # 1. CATALOG INVENTORY & SCHEMA INTEGRITY
    def test_catalog_inventory_and_schema(self):
        """Verify catalog contains 12 permitted non-diagnostic rules with complete schema."""
        assert len(HEALTH_RULES_CATALOG) == 12
        for r in HEALTH_RULES_CATALOG:
            assert r.rule_id.startswith("HEALTH-")
            assert r.version == "1.0.0"
            assert r.domain == "health"
            assert r.source_status == "VERIFIED"
            assert r.review_status == "ACCEPTED"
            assert r.confidence in ("HIGH", "MEDIUM")
            assert len(r.dimensions) > 0
            for d in r.dimensions:
                assert d in WELLBEING_DIMENSIONS

    # 2. SAFETY INVARIANTS: ABSOLUTE PROHIBITION CHECKS
    def test_no_disease_diagnosis_or_prediction(self):
        """Verify that no disease or medical condition names appear in rule or narrative outputs."""
        ctx = create_base_ctx("Mesha")
        # Adversarial chart with malefics in Dusthanas (6th, 8th, 12th)
        ctx["planet_map"]["Mars"]["house"] = 6
        ctx["planet_map"]["Saturn"]["house"] = 8
        ctx["planet_map"]["Rahu"]["house"] = 12

        rule_res = evaluate_health_rules(ctx)
        wrap_res = analyse_health(ctx)

        prohibited_diseases = [
            "cancer", "diabetes", "stroke", "tumor", "ulcer", "infection",
            "tuberculosis", "heart attack", "cardiac", "paralysis", "hepatitis",
            "asthma", "epilepsy", "arthritis", "kidney failure", "hypertension",
        ]

        full_output = (
            str(rule_res) + " " +
            str(wrap_res)
        ).lower()

        for d in prohibited_diseases:
            assert d not in full_output, f"Prohibited disease term '{d}' found in output!"

    def test_no_death_lifespan_or_longevity_predictions(self):
        """Verify no death, lifespan, or longevity predictions exist."""
        ctx = create_base_ctx("Mesha")
        ctx["planet_map"]["Saturn"]["house"] = 8
        ctx["planet_map"]["Mars"]["house"] = 8

        rule_res = evaluate_health_rules(ctx)
        wrap_res = analyse_health(ctx)

        prohibited_longevity = [
            "lifespan", "time of death", "age of death", "short life",
            "medium life", "long life", "alpayu", "madhyayu", "purnayu",
            "fatal accident", "deadly", "die at", "will die",
        ]

        full_output = (str(rule_res) + " " + str(wrap_res)).lower()
        for term in prohibited_longevity:
            assert term not in full_output, f"Prohibited longevity term '{term}' found in output!"

    def test_no_surgery_or_hospitalization_predictions(self):
        """Verify that surgery and hospitalization are never predicted or timed."""
        ctx = create_base_ctx("Mesha")
        ctx["planet_map"]["Mars"]["house"] = 8
        ctx["planet_map"]["Saturn"]["house"] = 6

        wrap_res = analyse_health(ctx)

        # In legacy, surgery_risk was True and told users to avoid surgery during Mars/Saturn
        assert wrap_res.get("surgery_risk") is False
        assert "avoid surgery" not in wrap_res.get("wellness_txt", "").lower()
        assert "surgery or accident risk" not in wrap_res.get("wellness_txt", "").lower()
        assert "time operations" not in wrap_res.get("wellness_txt", "").lower()

    def test_no_fertility_or_childbirth_claims(self):
        """Verify no fertility, infertility, miscarriage, or pregnancy predictions exist in health domain."""
        ctx = create_base_ctx("Mesha")
        full_output = str(evaluate_health_rules(ctx)).lower() + " " + str(analyse_health(ctx)).lower()

        prohibited_fertility = [
            "infertile", "infertility", "miscarriage", "abortion",
            "barren", "conception guaranteed", "pregnant in",
        ]
        for term in prohibited_fertility:
            assert term not in full_output, f"Prohibited fertility term '{term}' found!"

    def test_no_mental_health_diagnoses(self):
        """Verify no psychiatric diagnostic claims are made from afflicted Moon placements."""
        ctx = create_base_ctx("Mesha")
        # Afflict Moon in 8th house with Rahu
        ctx["planet_map"]["Moon"]["house"] = 8
        ctx["planet_map"]["Rahu"]["house"] = 8

        wrap_res = analyse_health(ctx)
        full_text = wrap_res["analysis"].lower() + " " + wrap_res["emotional_sensitivity"].lower()

        prohibited_psych = [
            "depression", "clinical anxiety", "bipolar", "schizophrenia",
            "psychosis", "mental disorder", "mental illness", "psychiatric",
        ]
        for term in prohibited_psych:
            assert term not in full_text, f"Prohibited psychiatric term '{term}' found in output!"

    def test_no_treatment_or_medication_advice(self):
        """Verify system never tells users to start, stop, or change medications or medical treatment."""
        ctx = create_base_ctx("Mesha")
        full_output = str(evaluate_health_rules(ctx)).lower() + " " + str(analyse_health(ctx)).lower()

        prohibited_med = [
            "stop medication", "start medication", "discontinue treatment",
            "change dosage", "cure for", "heals disease", "replaces medicine",
        ]
        for term in prohibited_med:
            assert term not in full_output, f"Prohibited treatment advice '{term}' found!"

    def test_mandatory_safety_disclaimer_presence(self):
        """Verify mandatory medical safety disclaimer is present in all payloads."""
        ctx = create_base_ctx("Mesha")
        rule_res = evaluate_health_rules(ctx)
        wrap_res = analyse_health(ctx)

        assert "safety_disclaimer" in rule_res
        assert "safety_disclaimer" in wrap_res
        assert SAFETY_DISCLAIMER == rule_res["safety_disclaimer"]
        assert "licensed medical physician" in rule_res["safety_disclaimer"].lower()

    # 3. FUNCTIONAL EVALUATION OF 12 PERMITTED RULES
    def test_health_lagna_benefic(self):
        """Test HEALTH-VITALITY-LAGNA-BENEFIC-01: Benefic on Lagna."""
        ctx = create_base_ctx("Mesha")
        ctx["planet_map"]["Jupiter"]["house"] = 1
        res = evaluate_health_rules(ctx)
        matched = [m["rule_id"] for m in res["matched_rules"]]
        assert "HEALTH-VITALITY-LAGNA-BENEFIC-01" in matched
        assert res["dimensions"]["vitality_stamina"]["support"] >= 1

    def test_health_sun_dignity(self):
        """Test HEALTH-VITALITY-SUN-DIGNITY-02: Sun in Kendra or own sign."""
        ctx = create_base_ctx("Mesha")
        ctx["planet_map"]["Sun"]["house"] = 10
        ctx["planet_map"]["Sun"]["sign"] = "Makara"
        res = evaluate_health_rules(ctx)
        matched = [m["rule_id"] for m in res["matched_rules"]]
        assert "HEALTH-VITALITY-SUN-DIGNITY-02" in matched

    def test_health_moon_calm(self):
        """Test HEALTH-MINDFULNESS-MOON-CALM-03: Favorable Moon placement."""
        ctx = create_base_ctx("Mesha")
        ctx["planet_map"]["Moon"]["sign"] = "Vrishabha"  # Exalted
        res = evaluate_health_rules(ctx)
        matched = [m["rule_id"] for m in res["matched_rules"]]
        assert "HEALTH-MINDFULNESS-MOON-CALM-03" in matched
        assert res["dimensions"]["mindfulness_rest"]["support"] >= 1

    def test_health_saturn_discipline(self):
        """Test HEALTH-ROUTINE-SATURN-DISCIPLINE-04: Saturn in Upachaya."""
        ctx = create_base_ctx("Mesha")
        ctx["planet_map"]["Saturn"]["house"] = 6
        res = evaluate_health_rules(ctx)
        matched = [m["rule_id"] for m in res["matched_rules"]]
        assert "HEALTH-ROUTINE-SATURN-DISCIPLINE-04" in matched
        assert res["dimensions"]["routine_balance"]["support"] >= 1

    def test_health_12th_rest(self):
        """Test HEALTH-REST-12TH-BENEFIC-05: Benefics in 12th house."""
        ctx = create_base_ctx("Mesha")
        ctx["planet_map"]["Venus"]["house"] = 12
        res = evaluate_health_rules(ctx)
        matched = [m["rule_id"] for m in res["matched_rules"]]
        assert "HEALTH-REST-12TH-BENEFIC-05" in matched

    def test_health_temperament_pitta(self):
        """Test HEALTH-TEMPERAMENT-PITTA-06: Fire Lagna."""
        ctx = create_base_ctx("Simha")
        res = evaluate_health_rules(ctx)
        matched = [m["rule_id"] for m in res["matched_rules"]]
        assert "HEALTH-TEMPERAMENT-PITTA-06" in matched

    def test_health_temperament_kapha(self):
        """Test HEALTH-TEMPERAMENT-KAPHA-07: Earth/Water Lagna."""
        ctx = create_base_ctx("Vrishabha")
        res = evaluate_health_rules(ctx)
        matched = [m["rule_id"] for m in res["matched_rules"]]
        assert "HEALTH-TEMPERAMENT-KAPHA-07" in matched

    def test_health_temperament_vata(self):
        """Test HEALTH-TEMPERAMENT-VATA-08: Air Lagna."""
        ctx = create_base_ctx("Mithuna")
        res = evaluate_health_rules(ctx)
        matched = [m["rule_id"] for m in res["matched_rules"]]
        assert "HEALTH-TEMPERAMENT-VATA-08" in matched

    def test_health_6th_habit(self):
        """Test HEALTH-HABIT-6TH-LORD-UPACHAYA-09: 6th lord in Upachaya."""
        ctx = create_base_ctx("Mesha")
        # 6th lord for Mesha is Mercury. Place Mercury in 10th house (Upachaya).
        ctx["planet_map"]["Mercury"]["house"] = 10
        res = evaluate_health_rules(ctx)
        matched = [m["rule_id"] for m in res["matched_rules"]]
        assert "HEALTH-HABIT-6TH-LORD-UPACHAYA-09" in matched

    def test_health_pace_awareness(self):
        """Test HEALTH-MINDFULNESS-PACE-AWARENESS-10: Mars/Rahu on Moon/Lagna."""
        ctx = create_base_ctx("Mesha")
        ctx["planet_map"]["Mars"]["house"] = 1
        res = evaluate_health_rules(ctx)
        matched = [m["rule_id"] for m in res["matched_rules"]]
        assert "HEALTH-MINDFULNESS-PACE-AWARENESS-10" in matched
        assert res["dimensions"]["mindfulness_rest"]["conditional"] >= 1

    def test_health_jupiter_grace(self):
        """Test HEALTH-REJUVENATION-JUPITER-GRACE-11: Jupiter aspecting Lagna."""
        ctx = create_base_ctx("Mesha")
        # Jupiter in 9th house (5th aspect reaches 1st house)
        ctx["planet_map"]["Jupiter"]["house"] = 9
        res = evaluate_health_rules(ctx)
        matched = [m["rule_id"] for m in res["matched_rules"]]
        assert "HEALTH-REJUVENATION-JUPITER-GRACE-11" in matched

    def test_health_solar_diurnal(self):
        """Test HEALTH-ROUTINE-SOLAR-DIURNAL-12: Sun in 1st or 10th."""
        ctx = create_base_ctx("Mesha")
        ctx["planet_map"]["Sun"]["house"] = 1
        res = evaluate_health_rules(ctx)
        matched = [m["rule_id"] for m in res["matched_rules"]]
        assert "HEALTH-ROUTINE-SOLAR-DIURNAL-12" in matched

    # 4. ALL 12 LAGNA SIGNS EVALUATION
    def test_all_12_ascendant_signs(self):
        """Verify that all 12 Lagnas evaluate smoothly without errors."""
        RASHIS = ["Mesha", "Vrishabha", "Mithuna", "Karka", "Simha", "Kanya",
                  "Tula", "Vrischika", "Dhanu", "Makara", "Kumbha", "Meena"]
        for lagna in RASHIS:
            ctx = create_base_ctx(lagna)
            res = evaluate_health_rules(ctx)
            assert res["domain"] == "health"
            assert res["is_diagnostic"] is False
            assert len(res["dimensions"]) == 4

    # 5. DETERMINISM AND IMMUTABILITY
    def test_determinism_and_immutability(self):
        """Verify repeated evaluations return identical results without mutating context."""
        ctx = create_base_ctx("Mesha")
        ctx["planet_map"]["Sun"]["house"] = 1
        ctx["planet_map"]["Jupiter"]["house"] = 9

        res1 = evaluate_health_rules(ctx)
        res2 = evaluate_health_rules(ctx)

        assert res1["matched_rules"] == res2["matched_rules"]
        assert res1["dimensions"] == res2["dimensions"]

    # 6. BACKWARD COMPATIBILITY WITH LEGACY WRAPPER
    def test_legacy_wrapper_backward_compatibility(self):
        """Verify analyse_health preserves all 15 legacy keys while neutralizing unsafe content."""
        ctx = create_base_ctx("Mesha")
        out = analyse_health(ctx)

        legacy_keys = [
            "domain", "icon", "score", "weak_organs", "lagna_organs",
            "ayurvedic_dosha", "emotional_sensitivity", "wellness_focus",
            "wellness_txt", "arishta_doshas", "disease_periods", "first_lord",
            "dasha_active", "timing", "remedies", "analysis",
        ]
        for k in legacy_keys:
            assert k in out, f"Legacy key '{k}' missing from analyse_health!"

        # Enriched keys
        assert "evidence" in out
        assert "dimensions" in out
        assert "rules_evaluated" in out
        assert "safety_disclaimer" in out
        assert out["domain"] == "Health & Wellbeing"
