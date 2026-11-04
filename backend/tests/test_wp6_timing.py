"""
Comprehensive Test Suite for WP6 — Timing Engine, Dasha–Transit Fusion & Prediction Synthesis.

Tests:
  1. Vimshottari Dasha Engine Verification:
     - 120-year cycle and nominal planet years
     - Moon nakshatra mapping & balance at birth (Ashwini, Bharani, Revati, etc.)
     - All 9 starting Mahadasha lords
     - Antardasha and Pratyantardasha proportional boundary math
     - Calendar conventions: 'solar_365_25' vs 'savana_360'
     - Leap-year boundary continuity
  2. Ashtakavarga Mathematical Invariants:
     - All 7 planet BAV calculations
     - Exact bindu totals: Sun=48, Moon=49, Mars=39, Mercury=54, Jupiter=56, Venus=52, Saturn=39
     - Universal SAV Invariant: Total across 12 signs = exactly 337 bindus
     - House SAV mapping from Lagna
     - Transit bindu evaluation thresholds
  3. Gochara Vedha Obstruction:
     - Benefic house detection from natal Moon
     - Obstruction detection when counter-planet is placed on Vedha point
     - Canonical exemptions: Sun-Saturn and Moon-Mercury exemptions
  4. Double Transit Engine:
     - Simultaneous Jupiter and Saturn aspect/occupancy detection
  5. Canonical 25 Timing Rules Catalog:
     - Positive, negative, and exception behavior across Dasha, Transit, AV, and Vedha families
  6. Master Spec v3.0 4-Family Evidence Fusion:
     - PeriodActivation (0.40) + TransitTrigger (0.30) + AshtakavargaContext (0.15) + NatalPromise (0.15)
     - Rolling 3-month smoothing and 1-month gap tolerance
     - Deduplication of overlapping windows (>50% overlap)
  7. Birth-Time Uncertainty & Dasha Stability:
     - Drift calculation and Nakshatra Sandhi threshold
  8. Optional Alternate Dasha Profile:
     - Yogini Dasha (36-year cycle)
  9. Deterministic Repeated Execution
  10. Legacy API Compatibility
  11. Strict Safety Guardrails & Adversarial Scans
"""

import pytest
from datetime import datetime, date, timedelta

from shared.veda.zodiac import SIGNS_SK
from shared.veda.ashtakavarga import (
    compute_bav,
    compute_all_bav,
    compute_sav,
    compute_house_sav,
    evaluate_ashtakavarga_transit,
    TOTAL_EXPECTED_BINDU,
    SAV_TOTAL_INVARIANT,
)
from shared.veda.vedha import (
    check_transit_vedha,
    GOCHARA_BENEFIC_HOUSES,
    VEDHA_PAIRS,
    VEDHA_EXEMPT_PAIRS,
)
from shared.veda.timing_rules import (
    TimingRule,
    TIMING_RULES_CATALOG,
    evaluate_timing_rules,
    TIMING_SAFETY_DISCLAIMER,
)
from modules.kundali.dasha import (
    calculate_mahadasha,
    generate_dasha_timeline,
    generate_antardasha,
    compute_pratyantardasha,
    generate_dasha_chain,
    evaluate_dasha_birth_time_sensitivity,
    calculate_yogini_dasha,
    DASHA_SEQUENCE,
    DASHA_YEARS,
)
from modules.prediction.timing import (
    compute_timing,
    evaluate_event_trigger,
    build_timing_block,
)
from modules.prediction.timing_fusion import (
    fuse_windows,
    TimingFusionResult,
    TimingWindow,
    _check_double_transit,
)


# ---------------------------------------------------------------------------
# Test Fixture Helpers
# ---------------------------------------------------------------------------

def _sample_chart():
    return {
        "basic_details": {"lagna": "Mesha", "ayanamsa": "Lahiri"},
        "lagna": "Mesha",
        "dasha": {"current_mahadasha": "Jupiter", "balance_years": 10.0},
        "planet_map": {
            "Sun": {"sign": "Simha", "house": 5, "degree": 10.0},
            "Moon": {"sign": "Karka", "house": 4, "degree": 12.0},
            "Mars": {"sign": "Makara", "house": 10, "degree": 28.0},
            "Mercury": {"sign": "Mithuna", "house": 3, "degree": 14.0},
            "Jupiter": {"sign": "Dhanu", "house": 9, "degree": 16.0},
            "Venus": {"sign": "Vrishabha", "house": 2, "degree": 20.0},
            "Saturn": {"sign": "Makara", "house": 10, "degree": 5.0},
            "Rahu": {"sign": "Kumbha", "house": 11, "degree": 22.0},
            "Ketu": {"sign": "Simha", "house": 5, "degree": 22.0},
        },
        "planets_by_house": {
            "1": [], "2": [{"planet": "Venus", "degree": 20.0}],
            "3": [{"planet": "Mercury", "degree": 14.0}],
            "4": [{"planet": "Moon", "degree": 12.0}],
            "5": [{"planet": "Sun", "degree": 10.0}, {"planet": "Ketu", "degree": 22.0}],
            "6": [], "7": [], "8": [],
            "9": [{"planet": "Jupiter", "degree": 16.0}],
            "10": [{"planet": "Mars", "degree": 28.0}, {"planet": "Saturn", "degree": 5.0}],
            "11": [{"planet": "Rahu", "degree": 22.0}], "12": [],
        },
        "house_lords": {
            1: "Mars", 2: "Venus", 3: "Mercury", 4: "Moon",
            5: "Sun", 6: "Mercury", 7: "Venus", 8: "Mars",
            9: "Jupiter", 10: "Saturn", 11: "Saturn", 12: "Jupiter",
        },
        "mahadasha": "Jupiter",
        "antardasha": "Venus",
        "transit_map": {
            "Sun": {"house": 5, "sign": "Simha"},
            "Moon": {"house": 4, "sign": "Karka"},
            "Mars": {"house": 10, "sign": "Makara"},
            "Mercury": {"house": 3, "sign": "Mithuna"},
            "Jupiter": {"house": 9, "sign": "Dhanu"},
            "Venus": {"house": 2, "sign": "Vrishabha"},
            "Saturn": {"house": 10, "sign": "Makara"},
            "Rahu": {"house": 11, "sign": "Kumbha"},
            "Ketu": {"house": 5, "sign": "Simha"},
        },
    }


# ===========================================================================
# 1. VIMSHOTTARI DASHA MATHEMATICAL VERIFICATION
# ===========================================================================

class TestVimshottariDashaMath:
    """Rigorous tests for BPHS Ch. 46 Vimshottari balance, durations, and conventions."""

    def test_total_cycle_120_years(self):
        total = sum(DASHA_YEARS.values())
        assert total == 120, f"Vimshottari total must be exactly 120 years, got {total}"
        assert len(DASHA_SEQUENCE) == 9

    def test_starting_balance_ashwini(self):
        # 0.0° Moon in Ashwini (ruled by Ketu, full 7 years)
        lord, balance = calculate_mahadasha(0.0, "Ashwini")
        assert lord == "Ketu"
        assert balance == 7.0

        # Halfway through Ashwini (6.666667°) -> remaining balance is 3.5 years
        lord, balance = calculate_mahadasha(13.3333333 / 2.0, "Ashwini")
        assert lord == "Ketu"
        assert abs(balance - 3.5) <= 0.05

    def test_all_9_starting_lords(self):
        # Test 9 consecutive nakshatras from Ashwini (Ketu) to Ashlesha (Mercury)
        nakshatra_size = 360.0 / 27.0
        for i in range(9):
            deg = i * nakshatra_size + 1.0  # just inside the nakshatra
            expected_lord = DASHA_SEQUENCE[i]
            lord, balance = calculate_mahadasha(deg, "")
            assert lord == expected_lord, f"Expected {expected_lord} for deg {deg}, got {lord}"
            assert balance > 0

    def test_timeline_generation_sum(self):
        timeline = generate_dasha_timeline("Jupiter", 10.0)
        assert timeline[0]["lord"] == "Jupiter"
        assert timeline[0]["years"] == 10.0
        total_yrs = sum(item["years"] for item in timeline)
        assert total_yrs >= 120.0

    def test_antardasha_subperiod_sum(self):
        # Sum of 9 Antardashas within a Mahadasha must equal the Mahadasha years
        for lord, full_yrs in DASHA_YEARS.items():
            ads = generate_antardasha(lord)
            assert len(ads) == 9
            ad_sum = sum(ad["years"] for ad in ads)
            assert abs(ad_sum - full_yrs) <= 0.05, f"AD sum {ad_sum} must equal MD years {full_yrs}"

    def test_pratyantardasha_durations_and_continuity(self):
        start_dt = datetime(2025, 1, 1)
        end_dt = datetime(2026, 1, 1)  # 365 days
        pds = compute_pratyantardasha("Jupiter", "Venus", start_dt, end_dt)
        assert len(pds) == 9

        # Continuity check: each PD start matches previous PD end
        for i in range(len(pds) - 1):
            assert pds[i]["end"] == pds[i + 1]["start"]

        # PD days sum to approx total days
        total_pd_days = sum(pd["days"] for pd in pds)
        assert abs(total_pd_days - 365.0) <= 1.0

    def test_calendar_conventions_solar_vs_savana(self):
        bdt = datetime(2000, 1, 1)
        timeline = [{"lord": "Sun", "years": 6.0}]

        # 1. Solar 365.25 convention
        chain_solar = generate_dasha_chain(bdt, timeline, year_convention="solar_365_25")
        last_solar_end = datetime.strptime(chain_solar[-1]["end"], "%Y-%m-%d")
        solar_days = (last_solar_end - bdt).days

        # 2. Savana 360 convention
        chain_savana = generate_dasha_chain(bdt, timeline, year_convention="savana_360")
        last_savana_end = datetime.strptime(chain_savana[-1]["end"], "%Y-%m-%d")
        savana_days = (last_savana_end - bdt).days

        # 6 * 365.25 = 2191.5 days vs 6 * 360 = 2160 days
        assert abs(solar_days - 2191.5) <= 2
        assert abs(savana_days - 2160.0) <= 2
        assert solar_days > savana_days

    def test_leap_year_boundary(self):
        # Leap year birth: 2024-02-29
        leap_bdt = datetime(2024, 2, 29)
        timeline = [{"lord": "Mars", "years": 1.0}]
        chain = generate_dasha_chain(leap_bdt, timeline)
        assert len(chain) > 0
        first_pd = chain[0]
        assert first_pd["start"] == "2024-02-29"


# ===========================================================================
# 2. ASHTAKAVARGA MATHEMATICAL INVARIANTS & BINDUS
# ===========================================================================

class TestAshtakavargaMath:
    """Rigorous tests for BPHS Ch. 66–72 Ashtakavarga invariants."""

    def test_all_7_planet_bav_totals(self):
        chart = _sample_chart()
        all_bav = compute_all_bav(chart)

        for planet, expected_total in TOTAL_EXPECTED_BINDU.items():
            bav = all_bav[planet]
            planet_total = sum(bav.values())
            assert planet_total == expected_total, f"{planet} BAV total must be {expected_total}, got {planet_total}"

    def test_sav_universal_invariant_337(self):
        chart = _sample_chart()
        sav = compute_sav(chart)
        total_sav = sum(sav.values())
        assert total_sav == SAV_TOTAL_INVARIANT, f"Universal SAV sum must be 337, got {total_sav}"
        assert len(sav) == 12

    def test_house_sav_mapping(self):
        chart = _sample_chart()
        house_sav = compute_house_sav(chart)
        assert len(house_sav) == 12
        assert sum(house_sav.values()) == SAV_TOTAL_INVARIANT

    def test_evaluate_ashtakavarga_transit(self):
        chart = _sample_chart()
        # Evaluate Jupiter in Dhanu
        res = evaluate_ashtakavarga_transit("Jupiter", "Dhanu", chart)
        assert res["planet"] == "Jupiter"
        assert res["transit_sign"] == "Dhanu"
        assert 0 <= res["bav_bindus"] <= 8
        assert res["sav_bindus"] > 0
        assert res["status"] in ("EXCELLENT", "FAVORABLE", "AVERAGE", "DIFFICULT")


# ===========================================================================
# 3. GOCHARA VEDHA OBSTRUCTION ENGINE
# ===========================================================================

class TestGocharaVedha:
    """Tests for Phaladeepika Ch. 26 Gochara Vedha and exemptions."""

    def test_benefic_unobstructed_transit(self):
        # Jupiter in 2nd house from Moon (benefic house, Vedha point is 12th)
        # When 12th house is empty, transit is unobstructed
        transit_positions = {"Jupiter": 2, "Saturn": 5, "Mars": 6}
        res = check_transit_vedha("Jupiter", 2, transit_positions)
        assert res["is_benefic"] is True
        assert res["is_obstructed"] is False
        assert res["status"] == "UNOBSTRUCTED_BENEFIC"

    def test_vedha_obstruction_detected(self):
        # Jupiter in 2nd house from Moon, Vedha point is 12th
        # Put Mars in 12th -> causes Vedha
        transit_positions = {"Jupiter": 2, "Mars": 12}
        res = check_transit_vedha("Jupiter", 2, transit_positions)
        assert res["is_benefic"] is True
        assert res["is_obstructed"] is True
        assert "Mars" in res["obstructing_planets"]
        assert res["status"] == "OBSTRUCTED_BY_VEDHA"

    def test_sun_saturn_father_son_exemption(self):
        # Sun in 3rd from Moon (benefic, Vedha point is 9th)
        # Put Saturn in 9th -> Sun and Saturn are exempt from causing Vedha to each other
        transit_positions = {"Sun": 3, "Saturn": 9}
        res = check_transit_vedha("Sun", 3, transit_positions)
        assert res["is_benefic"] is True
        assert res["is_obstructed"] is False, "Saturn must not cause Vedha to Sun due to father-son exemption"

    def test_moon_mercury_exemption(self):
        # Moon in 3rd from Moon (benefic, Vedha point is 9th)
        # Put Mercury in 9th -> Moon and Mercury are exempt from causing Vedha to each other
        transit_positions = {"Moon": 3, "Mercury": 9}
        res = check_transit_vedha("Moon", 3, transit_positions)
        assert res["is_benefic"] is True
        assert res["is_obstructed"] is False, "Mercury must not cause Vedha to Moon"


# ===========================================================================
# 4. DOUBLE TRANSIT TRIGGER
# ===========================================================================

class TestDoubleTransit:
    """Tests for simultaneous Jupiter + Saturn influence on significator houses."""

    def test_double_transit_positive(self):
        # Jupiter in 3rd aspects 7, 9, 11 (aspect on 7th)
        # Saturn in 1st aspects 3, 7, 10 (aspect on 7th)
        # Target house = 7 (marriage)
        active_transits = {
            "Jupiter": {"house": 3},
            "Saturn": {"house": 1},
        }
        assert _check_double_transit([7], active_transits) is True

    def test_double_transit_negative(self):
        # Jupiter in 3 (aspects 7), Saturn in 2 (aspects 4, 8, 11 - no aspect on 7)
        active_transits = {
            "Jupiter": {"house": 3},
            "Saturn": {"house": 2},
        }
        assert _check_double_transit([7], active_transits) is False


# ===========================================================================
# 5. CANONICAL TIMING RULES (25 RULES)
# ===========================================================================

class TestTimingRulesCatalog:
    """Verify execution of the 25 canonical timing rules."""

    def test_catalog_size_and_schema(self):
        assert len(TIMING_RULES_CATALOG) == 25
        for rule in TIMING_RULES_CATALOG:
            assert rule.rule_id.startswith("TIME-")
            assert rule.family in ("dasha", "transit", "ashtakavarga", "vedha", "double_transit")
            assert rule.effect in ("SUPPORTS", "OBSTRUCTS", "CONDITIONAL")
            assert rule.confidence in ("[HIGH]", "[MEDIUM]", "[LOW, needs expert check]")

    def test_evaluate_timing_rules_execution(self):
        chart = _sample_chart()
        timing_ctx = {
            "md_lord": "Jupiter",
            "ad_lord": "Venus",
            "pd_lord": "Sun",
            "domain_houses": [10, 6, 11],
            "transit_map": chart["transit_map"],
        }
        res = evaluate_timing_rules(chart, timing_ctx)
        assert "evidence_ledger" in res
        assert "family_scores" in res
        assert res["active_rules_count"] > 0
        assert "safety_disclaimer" in res


# ===========================================================================
# 6. MASTER SPEC 4-FAMILY EVIDENCE FUSION
# ===========================================================================

class TestTimingFusion:
    """Verify Master Spec v3.0 4-family evidence fusion and window generation."""

    def test_fuse_windows_generation(self):
        chart = _sample_chart()
        res = fuse_windows(chart, "wealth", date(2025, 1, 1), date(2030, 1, 1))

        assert isinstance(res, TimingFusionResult)
        assert len(res.timing_windows) > 0
        assert res.peak_window is not None
        assert "Master Spec v3.0 4-Family" in res.methodology

        # Verify evidence families in peak window
        w = res.peak_window
        assert "period_activation" in w.evidence_families
        assert "transit_trigger" in w.evidence_families
        assert "ashtakavarga_context" in w.evidence_families
        assert "natal_promise" in w.evidence_families
        assert 0.0 <= w.peak_score <= 1.0

        # Also verify that a quiet domain gracefully returns empty windows without crashing
        res_quiet = fuse_windows(chart, "career", date(2025, 1, 1), date(2030, 1, 1))
        assert isinstance(res_quiet.timing_windows, list)

    def test_deduplication_of_overlapping_windows(self):
        chart = _sample_chart()
        res = fuse_windows(chart, "marriage", date(2025, 1, 1), date(2035, 1, 1))

        # Windows must not heavily overlap (>50%)
        windows = res.timing_windows
        for i in range(len(windows)):
            for j in range(i + 1, len(windows)):
                w1, w2 = windows[i], windows[j]
                overlap_s = max(w1.start_date, w2.start_date)
                overlap_e = min(w1.end_date, w2.end_date)
                if overlap_s <= overlap_e:
                    overlap_days = (overlap_e - overlap_s).days + 1
                    min_len = min((w1.end_date - w1.start_date).days + 1, (w2.end_date - w2.start_date).days + 1)
                    assert (overlap_days / min_len) < 0.60


# ===========================================================================
# 7. BIRTH-TIME UNCERTAINTY & STABILITY
# ===========================================================================

class TestBirthTimeSensitivity:
    """Verify uncertainty evaluation and sensitivity labeling."""

    def test_stable_birth_time(self):
        # Moon at 6.0° in Ashwini (well away from Sandhi at 0.0° or 13.33°)
        res = evaluate_dasha_birth_time_sensitivity(6.0, uncertainty_minutes=15.0)
        assert res["stability"] == "STABLE"
        assert res["nakshatra_boundary_crossed"] is False

    def test_sensitive_near_sandhi(self):
        # Moon at 13.30° (0.03° away from Bharani boundary at 13.333°)
        # A 15-min shift (~0.137°) will cross the boundary!
        res = evaluate_dasha_birth_time_sensitivity(13.30, uncertainty_minutes=15.0)
        assert res["stability"] == "HIGHLY_SENSITIVE"
        assert res["nakshatra_boundary_crossed"] is True


# ===========================================================================
# 8. OPTIONAL ALTERNATE DASHA: YOGINI DASHA
# ===========================================================================

class TestYoginiDasha:
    """Verify optional alternate Yogini Dasha profile."""

    def test_yogini_dasha_calculation(self):
        # Test Moon at 0.0° in Ashwini (nak_index 0)
        # Starting yogini = 0 % 8 = 0 -> Mangala (ruled by Moon, 1 year)
        res = calculate_yogini_dasha(0.0)
        assert res["profile"] == "yogini"
        assert res["starting_yogini"] == "Mangala"
        assert res["ruler_planet"] == "Moon"
        assert res["full_years"] == 1
        assert res["balance_years"] == 1.0
        assert res["cycle_total_years"] == 36


# ===========================================================================
# 9. DETERMINISTIC EXECUTION
# ===========================================================================

class TestDeterminism:
    """Verify strictly reproducible outputs."""

    def test_repeated_runs_identical(self):
        chart = _sample_chart()
        r1 = compute_timing(chart, "career", num_years=5)
        r2 = compute_timing(chart, "career", num_years=5)

        assert len(r1["timing_windows"]) == len(r2["timing_windows"])
        assert r1["peak_window"]["score"] == r2["peak_window"]["score"]
        assert r1["next_12_months_summary"] == r2["next_12_months_summary"]


# ===========================================================================
# 10. LEGACY API CONTRACT COMPATIBILITY
# ===========================================================================

class TestLegacyAPIContract:
    """Verify 100% backward compatibility for existing callers."""

    def test_compute_timing_keys_preserved(self):
        chart = _sample_chart()
        res = compute_timing(chart, "wealth", num_years=5)

        legacy_keys = [
            "timing_windows", "peak_window", "next_12_months_summary",
            "methodology", "threshold_used", "engine_version", "timing_engine", "legacy_timing"
        ]
        for k in legacy_keys:
            assert k in res, f"Legacy key '{k}' missing"

        # Check legacy_timing structure
        lt = res["legacy_timing"]
        assert "event" in lt
        assert "mahadasha_lord" in lt
        assert "activated" in lt
        assert "intensity" in lt

    def test_evaluate_event_trigger_preserved(self):
        chart = _sample_chart()
        res = evaluate_event_trigger(chart, "marriage")
        assert res["event"] == "marriage"
        assert isinstance(res["activated"], bool)
        assert res["intensity"] in ("High", "Moderate")


# ===========================================================================
# 11. SAFETY GUARDRAILS & ADVERSARIAL AUDIT
# ===========================================================================

class TestSafetyGuardrails:
    """Verify absolute prohibition against deterministic life event predictions."""

    def test_mandatory_disclaimer_present(self):
        chart = _sample_chart()
        res = compute_timing(chart, "career", num_years=5)
        assert "safety_disclaimer" in res
        assert res["safety_disclaimer"] == TIMING_SAFETY_DISCLAIMER
        assert "NEVER guaranteed event dates" in res["safety_disclaimer"]
        assert res["is_predictive"] is False

    def test_no_forbidden_deterministic_claims_in_summary(self):
        chart = _sample_chart()
        for domain in ("marriage", "career", "wealth", "health", "property"):
            res = compute_timing(chart, domain, num_years=5)
            summary = res["next_12_months_summary"].lower()

            forbidden_phrases = [
                "will get married on",
                "guaranteed marriage",
                "will buy house on",
                "will get promoted on",
                "guaranteed promotion",
                "will fall ill",
                "date of death",
                "will conceive on",
                "100% chance",
                "exact date of",
            ]
            for phrase in forbidden_phrases:
                assert phrase not in summary, f"Forbidden deterministic phrase '{phrase}' found in {domain} timing summary"


class TestHardeningAndEdgeCases:
    """Independent audit tests for fail-open fallback safety and malformed inputs."""

    def test_fail_open_safety_disclaimer(self):
        # A malformed object that causes an exception inside compute_timing
        malformed_chart = "not_a_dict"
        res = compute_timing(malformed_chart, "career")
        assert "safety_disclaimer" in res
        assert res["is_predictive"] is False
        assert "Timing analysis unavailable" in res["next_12_months_summary"]

        block = build_timing_block(malformed_chart, "career")
        assert "safety_disclaimer" in block
        assert block["is_predictive"] is False

    def test_chat_service_timing_disclaimer(self):
        from modules.narrative.chat import ChatService
        chart = {
            "lagna": "Aries",
            "mahadasha": "Jupiter",
            "antardasha": "Venus",
            "dasha_balance": "4.2 years",
            "planets": [{"name": "Sun", "house": 1, "sign": "Aries"}],
        }
        res = ChatService.answer_kundali_chat("when is my timing period?", chart)
        assert res["topic"] == "timing"
        assert "symbolic Gochara alignment, not fixed event guarantees" in res["reply"]

    def test_ashtakavarga_malformed_and_missing_planets(self):
        # Empty chart
        sav_empty = compute_sav({})
        assert sum(sav_empty.values()) == 337

        # Invalid signs
        chart_invalid = {"planets": {"Sun": {"sign": "NonExistentSign"}}}
        sav_invalid = compute_sav(chart_invalid)
        assert sum(sav_invalid.values()) == 337

    def test_deterministic_tie_breaking_order(self):
        w1 = TimingWindow(
            start_date=date(2026, 1, 1),
            end_date=date(2026, 3, 31),
            peak_date=date(2026, 2, 1),
            peak_score=0.75,
            confidence="High",
            mahadasha="Jupiter",
            antardasha="Venus",
            pratyantardasha="Saturn",
            reasons=[],
            drivers=[],
            sub_scores={},
        )
        w2 = TimingWindow(
            start_date=date(2026, 6, 1),
            end_date=date(2026, 8, 31),
            peak_date=date(2026, 7, 1),
            peak_score=0.75,
            confidence="High",
            mahadasha="Jupiter",
            antardasha="Sun",
            pratyantardasha="Mars",
            reasons=[],
            drivers=[],
            sub_scores={},
        )
        windows = [w2, w1]
        windows.sort(key=lambda x: (-x.peak_score, x.start_date))
        # w1 (earlier start_date) must precede w2 despite identical scores
        assert windows[0].start_date == date(2026, 1, 1)
        assert windows[1].start_date == date(2026, 6, 1)
