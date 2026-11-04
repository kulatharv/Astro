"""
Independent Unit & Integration Tests for WP7C2: Cross-System Timing Attribution & Disjoint Synthesis.

Governing Standards:
- Master Specification v3.0 §10, §13.2, §15, Appendix C
- WP0 Traceability Matrix v1.1: TR-051 to TR-054
- ASTROLOGIC_WP7_RULE_CATALOG_DRAFT.md: Rule JAI-DSH-07 (v1.0-draft)
- ASTROLOGIC_WP7_DESIGN_DECISION_REGISTER.md

Scope Under Test:
1. Pure numeric and calendar interval comparison mechanics:
   - Half-open interval [start, end) convention
   - Exact boundary touching (E1 == S2) -> NO_OVERLAP
   - Partial overlap, subset overlap, exact match, disjoint intervals
   - Malformed, inverted, NaN/Inf intervals rejection
2. Disjoint attribution preservation:
   - Vimshottari-only evidence
   - Chara-Dasha-only evidence
   - Both systems evaluated simultaneously
   - Proof that source intervals are NEVER averaged or mutated
3. Convergence classification under Rule JAI-DSH-07:
   - CONVERGENT (both favorable or both unfavorable)
   - DIVERGENT (conflicting indications)
   - INDEPENDENT (neutral or single-tradition)
   - DISJOINT_NON_OVERLAPPING (no temporal overlap)
4. Absolute prohibitions verification:
   - Zero mathematical date averaging ((s1 + s2) / 2 is forbidden)
   - Zero synthetic event dates
   - Zero probability / accuracy claims
5. Orchestrator integration and Pydantic serialization
6. Governance status and regression isolation (WP1-WP6, WP7A-WP7C1)
"""

from __future__ import annotations

import json
import math
from datetime import date, datetime
import pytest

from shared.veda.jaimini_synthesis import (
    TimingSystemEnum,
    IntervalBoundaryConvention,
    TemporalRepresentationUnit,
    YearConventionEnum,
    OverlapType,
    ConvergenceStatus,
    TimingInterval,
    SystemTimingAttribution,
    CrossSystemComparisonRecord,
    CrossSystemSynthesisResponse,
    compare_numeric_intervals,
    compare_calendar_intervals,
    convert_elapsed_years_to_calendar_date,
    convert_calendar_date_to_elapsed_years,
    convert_interval_unit,
    evaluate_convergence_status,
    synthesize_timing_attributions,
)
from modules.kundali.jaimini import (
    synthesize_cross_system_timing,
    compute_jaimini_foundation,
)


# ==============================================================================
# Test Class 1: Interval Comparison Mechanics & Half-Open Boundaries
# ==============================================================================

class TestIntervalComparisonMechanics:
    """Verify precision half-open [start, end) interval arithmetic."""

    def test_exact_match_intervals(self):
        """Identical start and end boundaries yield EXACT_MATCH with ratio 1.0."""
        res = compare_numeric_intervals(10.0, 20.0, 10.0, 20.0)
        assert res["has_overlap"] is True
        assert res["overlap_type"] == OverlapType.EXACT_MATCH.value
        assert res["intersection_start"] == 10.0
        assert res["intersection_end"] == 20.0
        assert res["intersection_duration"] == 10.0
        assert res["overlap_ratio1"] == 1.0
        assert res["overlap_ratio2"] == 1.0

    def test_partial_overlap_intervals(self):
        """Interleaved intervals [10, 20) and [15, 25) yield PARTIAL_OVERLAP."""
        res = compare_numeric_intervals(10.0, 20.0, 15.0, 25.0)
        assert res["has_overlap"] is True
        assert res["overlap_type"] == OverlapType.PARTIAL_OVERLAP.value
        # Intersection is [15.0, 20.0)
        assert res["intersection_start"] == 15.0
        assert res["intersection_end"] == 20.0
        assert res["intersection_duration"] == 5.0
        assert pytest.approx(res["overlap_ratio1"]) == 5.0 / 10.0  # 0.5 of interval 1
        assert pytest.approx(res["overlap_ratio2"]) == 5.0 / 10.0  # 0.5 of interval 2

    def test_subset_intervals(self):
        """Interval [12, 16) fully enclosed within [10, 20) yields SUBSET."""
        res = compare_numeric_intervals(10.0, 20.0, 12.0, 16.0)
        assert res["has_overlap"] is True
        assert res["overlap_type"] == OverlapType.SUBSET.value
        assert res["intersection_start"] == 12.0
        assert res["intersection_end"] == 16.0
        assert res["intersection_duration"] == 4.0
        assert pytest.approx(res["overlap_ratio1"]) == 4.0 / 10.0  # 0.4
        assert pytest.approx(res["overlap_ratio2"]) == 4.0 / 4.0   # 1.0

    def test_exact_boundary_touching_is_not_overlap(self):
        """In half-open [start, end), touching at boundary [0, 5) and [5, 10) does NOT overlap."""
        res = compare_numeric_intervals(0.0, 5.0, 5.0, 10.0)
        assert res["has_overlap"] is False
        assert res["overlap_type"] == OverlapType.NO_OVERLAP.value
        assert res["intersection_duration"] == 0.0
        assert res["intersection_start"] is None
        assert res["intersection_end"] is None

    def test_disjoint_intervals(self):
        """Completely disjoint intervals [0, 5) and [8, 12) have zero overlap."""
        res = compare_numeric_intervals(0.0, 5.0, 8.0, 12.0)
        assert res["has_overlap"] is False
        assert res["overlap_type"] == OverlapType.NO_OVERLAP.value

    def test_calendar_date_interval_comparison(self):
        """Calendar dates in YYYY-MM-DD format are compared with day-level accuracy."""
        res = compare_calendar_intervals("2024-01-01", "2024-07-01", "2024-04-01", "2024-10-01")
        assert res["has_overlap"] is True
        assert res["overlap_type"] == OverlapType.PARTIAL_OVERLAP.value
        assert res["intersection_start"] == "2024-04-01"
        assert res["intersection_end"] == "2024-07-01"


# ==============================================================================
# Test Class 2: Input Validation & Error Handling
# ==============================================================================

class TestIntervalInputValidation:
    """Verify rejection of invalid, non-finite, or malformed intervals."""

    def test_inverted_interval_raises_value_error(self):
        """end < start raises ValueError."""
        with pytest.raises(ValueError, match="end1.*< start1"):
            compare_numeric_intervals(20.0, 10.0, 15.0, 25.0)

    def test_nan_or_inf_interval_raises_value_error(self):
        """NaN or Inf values raise ValueError."""
        with pytest.raises(ValueError, match="must be a finite float"):
            compare_numeric_intervals(float("nan"), 20.0, 15.0, 25.0)

        with pytest.raises(ValueError, match="must be a finite float"):
            compare_numeric_intervals(10.0, float("inf"), 15.0, 25.0)

    def test_invalid_calendar_date_format_raises_value_error(self):
        """Invalid date strings raise ValueError."""
        with pytest.raises(ValueError, match="Invalid calendar date string format"):
            compare_calendar_intervals("not-a-date", "2024-07-01", "2024-04-01", "2024-10-01")

    def test_incompatible_representation_units_raise_value_error(self):
        """Comparing ELAPSED_YEARS directly to CALENDAR_DATE raises ValueError."""
        v = SystemTimingAttribution(
            system=TimingSystemEnum.VIMSHOTTARI,
            profile_id="PARASHARI_DEFAULT",
            period_label="Jup-Sat",
            sub_period_type="ANTARDASHA",
            interval=TimingInterval(start=10.0, end=15.0, unit=TemporalRepresentationUnit.ELAPSED_YEARS),
            formula_version="WP6-v1.0",
        )
        c = SystemTimingAttribution(
            system=TimingSystemEnum.CHARA_DASHA,
            profile_id="KN_RAO_DEFAULT",
            period_label="Dhanu",
            sub_period_type="MAHADASHA",
            interval=TimingInterval(start="2024-01-01", end="2026-01-01", unit=TemporalRepresentationUnit.CALENDAR_DATE),
            formula_version="WP7B-v1.0",
        )
        with pytest.raises(ValueError, match="Incompatible temporal units"):
            synthesize_timing_attributions([v], [c])


# ==============================================================================
# Test Class 3: Disjoint Attribution & Convergence Classification (Rule JAI-DSH-07)
# ==============================================================================

class TestDisjointAttributionAndConvergence:
    """Verify Rule JAI-DSH-07 convergence classification and disjoint attribution."""

    @pytest.fixture
    def sample_v_favorable(self):
        return SystemTimingAttribution(
            system=TimingSystemEnum.VIMSHOTTARI,
            profile_id="VIMSHOTTARI_STANDARD",
            period_label="Jupiter-Venus",
            sub_period_type="ANTARDASHA",
            interval=TimingInterval(start=20.0, end=23.0, unit=TemporalRepresentationUnit.ELAPSED_YEARS),
            domain="career",
            disposition="FAVORABLE",
            rule_ids=["TIME-DSH-01", "TIME-DSH-03"],
            supporting_factors=["Jupiter 10th lord", "Venus exalted in 10th"],
            formula_version="WP6-v1.0",
        )

    @pytest.fixture
    def sample_c_favorable(self):
        return SystemTimingAttribution(
            system=TimingSystemEnum.CHARA_DASHA,
            profile_id="KN_RAO_CHARA",
            period_label="Dhanu-Mesha",
            sub_period_type="ANTARDASHA",
            interval=TimingInterval(start=21.0, end=24.0, unit=TemporalRepresentationUnit.ELAPSED_YEARS),
            domain="career",
            disposition="FAVORABLE",
            rule_ids=["JAI-DSH-01", "JAI-DSH-06"],
            supporting_factors=["Dhanu aspected by AmK", "Active Argala on 10th sign"],
            formula_version="WP7B-v1.0",
        )

    @pytest.fixture
    def sample_c_unfavorable(self):
        return SystemTimingAttribution(
            system=TimingSystemEnum.CHARA_DASHA,
            profile_id="KN_RAO_CHARA",
            period_label="Vrischika-Mithuna",
            sub_period_type="ANTARDASHA",
            interval=TimingInterval(start=21.0, end=24.0, unit=TemporalRepresentationUnit.ELAPSED_YEARS),
            domain="career",
            disposition="UNFAVORABLE",
            rule_ids=["JAI-DSH-01"],
            contrary_factors=["Gnati Karaka aspecting Dasha sign"],
            formula_version="WP7B-v1.0",
        )

    def test_vimshottari_only_evidence_preserves_attribution(self, sample_v_favorable):
        """When only Vimshottari items are present, they are preserved and status is INDEPENDENT."""
        res = synthesize_timing_attributions(
            vimshottari_attributions=[sample_v_favorable],
            chara_attributions=[],
            domain="career",
        )
        assert len(res.vimshottari_attributions) == 1
        assert len(res.chara_attributions) == 0
        assert res.overall_convergence == ConvergenceStatus.INDEPENDENT
        assert len(res.comparisons) == 1
        assert res.comparisons[0].vimshottari_evidence is not None
        assert res.comparisons[0].chara_evidence is None
        assert res.comparisons[0].convergence_status == ConvergenceStatus.INDEPENDENT

    def test_chara_only_evidence_preserves_attribution(self, sample_c_favorable):
        """When only Chara Dasha items are present, they are preserved and status is INDEPENDENT."""
        res = synthesize_timing_attributions(
            vimshottari_attributions=[],
            chara_attributions=[sample_c_favorable],
            domain="career",
        )
        assert len(res.vimshottari_attributions) == 0
        assert len(res.chara_attributions) == 1
        assert res.overall_convergence == ConvergenceStatus.INDEPENDENT
        assert len(res.comparisons) == 1
        assert res.comparisons[0].vimshottari_evidence is None
        assert res.comparisons[0].chara_evidence is not None
        assert res.comparisons[0].convergence_status == ConvergenceStatus.INDEPENDENT

    def test_both_systems_favorable_yields_convergent(self, sample_v_favorable, sample_c_favorable):
        """Both systems supporting same interval with FAVORABLE yield CONVERGENT."""
        res = synthesize_timing_attributions(
            vimshottari_attributions=[sample_v_favorable],
            chara_attributions=[sample_c_favorable],
            domain="career",
        )
        assert res.overall_convergence == ConvergenceStatus.CONVERGENT
        assert len(res.comparisons) == 1
        comp = res.comparisons[0]
        assert comp.convergence_status == ConvergenceStatus.CONVERGENT
        assert comp.overlap_type == OverlapType.PARTIAL_OVERLAP
        # Overlap is [21.0, 23.0)
        assert comp.overlap_interval.start == 21.0
        assert comp.overlap_interval.end == 23.0

    def test_conflicting_dispositions_yields_divergent(self, sample_v_favorable, sample_c_unfavorable):
        """One FAVORABLE and one UNFAVORABLE on overlapping interval yields DIVERGENT."""
        res = synthesize_timing_attributions(
            vimshottari_attributions=[sample_v_favorable],
            chara_attributions=[sample_c_unfavorable],
            domain="career",
        )
        assert res.overall_convergence == ConvergenceStatus.DIVERGENT
        assert len(res.comparisons) == 1
        comp = res.comparisons[0]
        assert comp.convergence_status == ConvergenceStatus.DIVERGENT

    def test_disjoint_non_overlapping_intervals(self, sample_v_favorable):
        """Non-overlapping periods yield DISJOINT_NON_OVERLAPPING."""
        chara_later = SystemTimingAttribution(
            system=TimingSystemEnum.CHARA_DASHA,
            profile_id="KN_RAO_CHARA",
            period_label="Makara",
            sub_period_type="MAHADASHA",
            interval=TimingInterval(start=25.0, end=30.0, unit=TemporalRepresentationUnit.ELAPSED_YEARS),
            domain="career",
            disposition="FAVORABLE",
            formula_version="WP7B-v1.0",
        )
        res = synthesize_timing_attributions(
            vimshottari_attributions=[sample_v_favorable],  # [20.0, 23.0)
            chara_attributions=[chara_later],               # [25.0, 30.0)
            domain="career",
        )
        assert res.overall_convergence == ConvergenceStatus.DISJOINT_NON_OVERLAPPING
        assert len(res.comparisons) == 1
        assert res.comparisons[0].overlap_type == OverlapType.NO_OVERLAP
        assert res.comparisons[0].overlap_interval is None


# ==============================================================================
# Test Class 4: Absolute Prohibitions (Date Averaging & Probability Claims)
# ==============================================================================

class TestProhibitionsEnforcement:
    """Verify strict prohibition of date averaging, synthetic event dates, and probabilities."""

    def test_no_date_averaging_or_synthetic_bounds_introduced(self):
        """
        Period 1: [10.0, 20.0)
        Period 2: [14.0, 26.0)
        Averaged start: (10 + 14)/2 = 12.0
        Averaged end: (20 + 26)/2 = 23.0
        Averaged midpoint: (12 + 23)/2 = 17.5
        Assert that NONE of these synthetic values are emitted as interval boundaries!
        """
        v = SystemTimingAttribution(
            system=TimingSystemEnum.VIMSHOTTARI,
            profile_id="V_PROFILE",
            period_label="V1",
            sub_period_type="MAHADASHA",
            interval=TimingInterval(start=10.0, end=20.0, unit=TemporalRepresentationUnit.ELAPSED_YEARS),
            disposition="FAVORABLE",
            formula_version="WP6-v1.0",
        )
        c = SystemTimingAttribution(
            system=TimingSystemEnum.CHARA_DASHA,
            profile_id="C_PROFILE",
            period_label="C1",
            sub_period_type="MAHADASHA",
            interval=TimingInterval(start=14.0, end=26.0, unit=TemporalRepresentationUnit.ELAPSED_YEARS),
            disposition="FAVORABLE",
            formula_version="WP7B-v1.0",
        )
        res = synthesize_timing_attributions([v], [c])
        comp = res.comparisons[0]

        # The intersection is [14.0, 20.0)
        assert comp.overlap_interval.start == 14.0
        assert comp.overlap_interval.end == 20.0

        # Assert no synthetic average is used
        assert comp.overlap_interval.start != 12.0
        assert comp.overlap_interval.end != 23.0

        # Assert original source items remain completely unaltered
        assert res.vimshottari_attributions[0].interval.start == 10.0
        assert res.vimshottari_attributions[0].interval.end == 20.0
        assert res.chara_attributions[0].interval.start == 14.0
        assert res.chara_attributions[0].interval.end == 26.0

    def test_no_probability_fields_in_output_payload(self):
        """CrossSystemSynthesisResponse contains NO probability or confidence percentage fields."""
        v = SystemTimingAttribution(
            system=TimingSystemEnum.VIMSHOTTARI,
            profile_id="V_PROFILE",
            period_label="V1",
            sub_period_type="MAHADASHA",
            interval=TimingInterval(start=10.0, end=20.0, unit=TemporalRepresentationUnit.ELAPSED_YEARS),
            disposition="FAVORABLE",
            formula_version="WP6-v1.0",
        )
        c = SystemTimingAttribution(
            system=TimingSystemEnum.CHARA_DASHA,
            profile_id="C_PROFILE",
            period_label="C1",
            sub_period_type="MAHADASHA",
            interval=TimingInterval(start=10.0, end=20.0, unit=TemporalRepresentationUnit.ELAPSED_YEARS),
            disposition="FAVORABLE",
            formula_version="WP7B-v1.0",
        )
        res = synthesize_timing_attributions([v], [c])
        raw_dict = res.model_dump()

        forbidden_keys = {"probability", "win_rate", "confidence_percent", "predicted_event_date"}
        for k in forbidden_keys:
            assert k not in raw_dict
            assert k not in raw_dict["comparisons"][0]

        # Convergence status is purely qualitative
        assert res.overall_convergence == ConvergenceStatus.CONVERGENT


# ==============================================================================
# Test Class 5: Serialization, Provenance & Governance
# ==============================================================================

class TestSynthesisSerializationAndGovernance:
    """Verify deterministic serialization, provenance metadata, and unapproved state."""

    def test_json_round_trip_serialization(self):
        """Verify model_dump_json() serializes cleanly and parses back to identical dict."""
        v = SystemTimingAttribution(
            system=TimingSystemEnum.VIMSHOTTARI,
            profile_id="V_PROFILE",
            period_label="Jupiter-Saturn",
            sub_period_type="ANTARDASHA",
            interval=TimingInterval(start=5.0, end=8.0, unit=TemporalRepresentationUnit.ELAPSED_YEARS),
            domain="wealth",
            disposition="FAVORABLE",
            formula_version="WP6-v1.0",
        )
        c = SystemTimingAttribution(
            system=TimingSystemEnum.CHARA_DASHA,
            profile_id="C_PROFILE",
            period_label="Dhanu-Vrishabha",
            sub_period_type="ANTARDASHA",
            interval=TimingInterval(start=6.0, end=9.0, unit=TemporalRepresentationUnit.ELAPSED_YEARS),
            domain="wealth",
            disposition="FAVORABLE",
            formula_version="WP7B-v1.0",
        )
        res = synthesize_cross_system_timing([v], [c], domain="wealth")
        json_str = res.model_dump_json()
        data = json.loads(json_str)

        assert data["domain"] == "wealth"
        assert data["formula_version"] == "WP7C2-SYNTHESIS-v1.0"
        assert data["approval_status"] == "PENDING_HUMAN_JYOTISHI"
        assert data["is_approved"] is False
        assert "disclaimer" in data
        assert len(data["limitations"]) >= 3
        assert len(data["comparisons"]) == 1

    def test_deterministic_repeatability(self):
        """Two identical calls yield bit-for-bit identical outputs."""
        v = SystemTimingAttribution(
            system=TimingSystemEnum.VIMSHOTTARI,
            profile_id="V_PROFILE",
            period_label="Mars-Rahu",
            sub_period_type="ANTARDASHA",
            interval=TimingInterval(start=1.0, end=2.0, unit=TemporalRepresentationUnit.ELAPSED_YEARS),
            formula_version="WP6-v1.0",
        )
        c = SystemTimingAttribution(
            system=TimingSystemEnum.CHARA_DASHA,
            profile_id="C_PROFILE",
            period_label="Aries-Taurus",
            sub_period_type="ANTARDASHA",
            interval=TimingInterval(start=1.5, end=3.0, unit=TemporalRepresentationUnit.ELAPSED_YEARS),
            formula_version="WP7B-v1.0",
        )
        run1 = synthesize_cross_system_timing([v], [c])
        run2 = synthesize_cross_system_timing([v], [c])
        assert run1.model_dump_json() == run2.model_dump_json()


# ==============================================================================
# Test Class 6: Regression Isolation (WP1–WP6, WP7A, WP7B, WP7C1)
# ==============================================================================

class TestRegressionIsolation:
    """Ensure existing WP1-WP6, WP7A, WP7B, and WP7C1 modules remain functional."""

    def test_wp1_shadbala_intact(self):
        from shared.veda import shadbala
        assert callable(shadbala)

    def test_wp2_lordship_intact(self):
        from shared.veda import build_lagna_matrix
        m = build_lagna_matrix("Mesha")
        assert m.lagna == "Mesha"

    def test_wp6_transit_vedha_intact(self):
        from shared.veda import check_transit_vedha
        assert callable(check_transit_vedha)

    def test_wp7a_arudha_truth_table_intact(self):
        from shared.veda.jaimini_rules import calculate_arudha_pada
        res = calculate_arudha_pada(house_num=1, lagna_sign=1, lord_sign=1)
        assert res["final_pada"] == 10

    def test_wp7b_chara_dasha_intact(self):
        from shared.veda.jaimini_dasha import calculate_mahadasha_duration
        dur = calculate_mahadasha_duration(sign=1, lord_sign=5, lord_planet="Mars")
        assert dur["final_years"] == 4

    def test_wp7c1_karakamsa_framing_intact(self):
        from shared.veda.jaimini_evidence import evaluate_karakamsa, KarakamsaFramingMode
        planets = {
            "Sun": 15.5, "Moon": 42.0, "Mars": 80.0, "Mercury": 125.0,
            "Jupiter": 268.75, "Venus": 348.33, "Saturn": 188.16, "Rahu": 280.0
        }
        res = evaluate_karakamsa(planets, lagna_sign=1, framing_mode=KarakamsaFramingMode.NAVAMSHA_IN_RASHI)
        assert res["ak_planet"] == "Jupiter"
        assert res["karakamsa_sign"] == 9


# ==============================================================================
# Test Class 7: Temporal Representation & Explicit Unit Conversion
# ==============================================================================

class TestTemporalRepresentationAndConversion:
    """Verify explicit conversion contracts and edge case handling."""

    def test_solar_365_25_conversion(self):
        """Solar 365.25 days/year conversion maps accurately to calendar dates."""
        # Non-leap year: 2001 (365 days) -> 365.25 days lands on 2002-01-01
        b_date_non_leap = date(2001, 1, 1)
        target_non_leap = convert_elapsed_years_to_calendar_date(b_date_non_leap, 1.0, YearConventionEnum.SOLAR_365_25)
        assert target_non_leap == date(2002, 1, 1)

        # Leap year: 2000 (366 days) -> 365.25 days lands on 2000-12-31
        b_date_leap = date(2000, 1, 1)
        target_leap = convert_elapsed_years_to_calendar_date(b_date_leap, 1.0, YearConventionEnum.SOLAR_365_25)
        assert target_leap == date(2000, 12, 31)

        # Reverse conversion
        elapsed = convert_calendar_date_to_elapsed_years(b_date_non_leap, date(2002, 1, 1), YearConventionEnum.SOLAR_365_25)
        assert math.isclose(elapsed, 1.0, abs_tol=0.01)

    def test_savana_360_conversion(self):
        """Savana 360 days/year conversion maps accurately."""
        b_date = date(2000, 1, 1)
        target = convert_elapsed_years_to_calendar_date(b_date, 1.0, YearConventionEnum.SAVANA_360)
        from datetime import timedelta
        assert target == b_date + timedelta(days=360)

        elapsed = convert_calendar_date_to_elapsed_years(b_date, target, YearConventionEnum.SAVANA_360)
        assert math.isclose(elapsed, 1.0, abs_tol=1e-5)

    def test_convert_interval_unit_both_directions(self):
        """TimingInterval unit conversion operates cleanly in both directions."""
        b_date = date(1990, 6, 15)
        # 1. Elapsed -> Calendar
        int_years = TimingInterval(start=10.0, end=15.0, unit=TemporalRepresentationUnit.ELAPSED_YEARS)
        int_cal = convert_interval_unit(int_years, TemporalRepresentationUnit.CALENDAR_DATE, b_date)
        assert int_cal.unit == TemporalRepresentationUnit.CALENDAR_DATE
        assert isinstance(int_cal.start, str)
        assert isinstance(int_cal.end, str)

        # 2. Calendar -> Elapsed
        int_roundtrip = convert_interval_unit(int_cal, TemporalRepresentationUnit.ELAPSED_YEARS, b_date)
        assert int_roundtrip.unit == TemporalRepresentationUnit.ELAPSED_YEARS
        assert math.isclose(float(int_roundtrip.start), 10.0, abs_tol=0.01)
        assert math.isclose(float(int_roundtrip.end), 15.0, abs_tol=0.01)

    def test_conversion_negative_elapsed_years_raises_value_error(self):
        """Negative elapsed years raise ValueError."""
        b_date = date(2000, 1, 1)
        with pytest.raises(ValueError, match="elapsed_years cannot be negative"):
            convert_elapsed_years_to_calendar_date(b_date, -2.5)

    def test_conversion_target_before_birth_raises_value_error(self):
        """Target date earlier than birth date raises ValueError."""
        b_date = date(2000, 1, 1)
        with pytest.raises(ValueError, match="cannot be earlier than birth_date"):
            convert_calendar_date_to_elapsed_years(b_date, date(1999, 1, 1))

    def test_zero_length_interval_half_open_no_overlap(self):
        """Under half-open [S, S), a zero-length interval has measure zero and NO_OVERLAP."""
        res = compare_numeric_intervals(10.0, 10.0, 10.0, 20.0, boundary=IntervalBoundaryConvention.HALF_OPEN_INCLUSIVE_EXCLUSIVE)
        assert res["has_overlap"] is False
        assert res["overlap_type"] == OverlapType.NO_OVERLAP.value
        assert res["intersection_duration"] == 0.0

    def test_zero_length_interval_closed_single_point(self):
        """Under closed [S, S], touching a single point yields intersection."""
        res = compare_numeric_intervals(10.0, 10.0, 10.0, 20.0, boundary=IntervalBoundaryConvention.CLOSED)
        assert res["has_overlap"] is True
        assert res["intersection_start"] == 10.0
        assert res["intersection_end"] == 10.0
        assert res["intersection_duration"] == 0.0

    def test_timing_interval_validator_negative_years(self):
        """TimingInterval rejects negative elapsed years at creation time."""
        with pytest.raises(ValueError, match="ELAPSED_YEARS start cannot be negative"):
            TimingInterval(start=-1.0, end=5.0, unit=TemporalRepresentationUnit.ELAPSED_YEARS)

    def test_timing_interval_validator_inverted_years(self):
        """TimingInterval rejects end < start for elapsed years."""
        with pytest.raises(ValueError, match="cannot be less than start"):
            TimingInterval(start=10.0, end=5.0, unit=TemporalRepresentationUnit.ELAPSED_YEARS)

    def test_timing_interval_validator_inverted_dates(self):
        """TimingInterval rejects end < start for calendar dates."""
        with pytest.raises(ValueError, match="cannot be earlier than start"):
            TimingInterval(start="2025-01-01", end="2024-01-01", unit=TemporalRepresentationUnit.CALENDAR_DATE)

    def test_calendar_whitespace_handling(self):
        """Calendar date parser strips whitespace cleanly."""
        res = compare_calendar_intervals(" 2024-01-01 ", "2024-06-01\n", "\t2024-03-01 ", " 2024-09-01 ")
        assert res["has_overlap"] is True
        assert res["intersection_start"] == "2024-03-01"
        assert res["intersection_end"] == "2024-06-01"

    def test_leap_day_birth_date(self):
        """Birth on leap day Feb 29, 2000 behaves deterministically across solar and savana conventions."""
        b_date = date(2000, 2, 29)
        # 1.0 Solar year: 365.25 days from Feb 29, 2000 -> 306 days in 2000 + 59.25 days in 2001 = Feb 28, 2001
        t_solar_1 = convert_elapsed_years_to_calendar_date(b_date, 1.0, YearConventionEnum.SOLAR_365_25)
        assert t_solar_1 == date(2001, 2, 28)

        # 4.0 Solar years: exactly 4 * 365.25 = 1461.0 days -> lands on Feb 29, 2004 (next leap year!)
        t_solar_4 = convert_elapsed_years_to_calendar_date(b_date, 4.0, YearConventionEnum.SOLAR_365_25)
        assert t_solar_4 == date(2004, 2, 29)

        # 1.0 Savana year: 360 days from Feb 29, 2000 -> 306 days in 2000 + 54 days in 2001 = Feb 23, 2001
        t_savana_1 = convert_elapsed_years_to_calendar_date(b_date, 1.0, YearConventionEnum.SAVANA_360)
        assert t_savana_1 == date(2001, 2, 23)

    def test_month_end_and_year_end_boundaries(self):
        """Test transitions across calendar year-end (Dec 31) and month-end boundaries."""
        b_date_dec31 = date(1999, 12, 31)
        # 1.0 Solar year (365.25 days) across leap year 2000 (366 days)
        t_dec31 = convert_elapsed_years_to_calendar_date(b_date_dec31, 1.0, YearConventionEnum.SOLAR_365_25)
        assert t_dec31 == date(2000, 12, 30)

        # 0.5 Solar year (182.625 days) across first half of 2000
        t_half = convert_elapsed_years_to_calendar_date(b_date_dec31, 0.5, YearConventionEnum.SOLAR_365_25)
        assert t_half == date(2000, 6, 30)

    def test_fractional_elapsed_years_precision(self):
        """Verify fine-grained fractional year calculations (e.g. Antardasha 1/12th year = 0.08333333)."""
        b_date = date(2020, 1, 1)
        ad_fraction = 1.0 / 12.0
        t_solar = convert_elapsed_years_to_calendar_date(b_date, ad_fraction, YearConventionEnum.SOLAR_365_25)
        # 365.25 / 12 = 30.4375 days -> Jan 1 + 30 days = Jan 31
        assert t_solar == date(2020, 1, 31)

        t_savana = convert_elapsed_years_to_calendar_date(b_date, ad_fraction, YearConventionEnum.SAVANA_360)
        # 360 / 12 = exactly 30.0 days -> Jan 1 + 30 days = Jan 31
        assert t_savana == date(2020, 1, 31)

        # Arbitrary float precision: 1.2345678 years
        t_arb = convert_elapsed_years_to_calendar_date(b_date, 1.2345678, YearConventionEnum.SOLAR_365_25)
        assert isinstance(t_arb, date)

    def test_explicit_missing_birth_date_or_convention_rejected(self):
        """Verify that passing None for birth_date or convention raises explicit ValueError."""
        with pytest.raises(ValueError, match="birth_date must be an explicit date or datetime"):
            convert_elapsed_years_to_calendar_date(None, 1.0)

        with pytest.raises(ValueError, match="Year convention must be explicitly provided"):
            convert_elapsed_years_to_calendar_date(date(2000, 1, 1), 1.0, convention=None)

        with pytest.raises(ValueError, match="birth_date must be an explicit date or datetime"):
            convert_calendar_date_to_elapsed_years(None, date(2001, 1, 1))

        with pytest.raises(ValueError, match="target_date must be an explicit date or datetime"):
            convert_calendar_date_to_elapsed_years(date(2000, 1, 1), None)

        with pytest.raises(ValueError, match="Year convention must be explicitly provided"):
            convert_calendar_date_to_elapsed_years(date(2000, 1, 1), date(2001, 1, 1), convention=None)

        int_years = TimingInterval(start=0.0, end=5.0, unit=TemporalRepresentationUnit.ELAPSED_YEARS)
        with pytest.raises(ValueError, match="birth_date must be an explicit date or datetime"):
            convert_interval_unit(int_years, TemporalRepresentationUnit.CALENDAR_DATE, birth_date=None)

        with pytest.raises(ValueError, match="Year convention must be explicitly provided"):
            convert_interval_unit(int_years, TemporalRepresentationUnit.CALENDAR_DATE, birth_date=date(2000, 1, 1), convention=None)

    def test_invalid_and_impossible_calendar_dates(self):
        """Verify rejection of non-existent calendar dates (e.g. Feb 30, month 13, non-leap Feb 29)."""
        impossible_dates = [
            ("2024-02-30", "2024-06-01"),  # Feb 30 does not exist
            ("2023-02-29", "2023-06-01"),  # 2023 is not a leap year
            ("2024-13-01", "2024-14-01"),  # Month 13
            ("2024-00-10", "2024-05-10"),  # Month 0
            ("2024-04-31", "2024-05-01"),  # April has only 30 days
        ]
        for s, e in impossible_dates:
            with pytest.raises(ValueError, match="Invalid calendar date string format"):
                compare_calendar_intervals(s, e, "2024-01-01", "2024-12-31")

            with pytest.raises(ValueError, match="CALENDAR_DATE boundaries must be valid YYYY-MM-DD"):
                TimingInterval(start=s, end=e, unit=TemporalRepresentationUnit.CALENDAR_DATE)

    def test_touching_calendar_boundaries_no_overlap(self):
        """Consecutive calendar intervals [2024-01-01, 2024-06-01) and [2024-06-01, 2024-12-31) have NO_OVERLAP."""
        res = compare_calendar_intervals("2024-01-01", "2024-06-01", "2024-06-01", "2024-12-31")
        assert res["has_overlap"] is False
        assert res["overlap_type"] == OverlapType.NO_OVERLAP.value
        assert res["intersection_duration_days"] == 0.0
        assert res["intersection_start"] is None

    def test_conversion_round_trip_quantization_tolerance(self):
        """
        Document and test unavoidable date-only quantization tolerance:
        Continuous elapsed years (float) -> Discrete calendar date (day integer) -> Re-converted elapsed years.
        Expected tolerance: <= 1.0 day / 360.0 ~= 0.0028 years.
        """
        b_date = date(1985, 8, 20)
        original_years = 12.345678

        # 1. Float years -> Calendar date (discards fractional day)
        c_date = convert_elapsed_years_to_calendar_date(b_date, original_years, YearConventionEnum.SOLAR_365_25)
        # 2. Calendar date -> Float years
        reconstructed_years = convert_calendar_date_to_elapsed_years(b_date, c_date, YearConventionEnum.SOLAR_365_25)

        # Difference must not exceed the width of one day
        one_day_tolerance = 1.0 / 365.25  # ~0.002738 years
        assert abs(reconstructed_years - original_years) <= one_day_tolerance

    def test_repeated_calls_and_serialization_determinism(self):
        """100 repeated calls produce bit-for-bit identical JSON and identical hashes."""
        b_date = date(1995, 4, 12)
        int_years = TimingInterval(start=5.25, end=11.75, unit=TemporalRepresentationUnit.ELAPSED_YEARS)

        json_snapshots = set()
        for _ in range(100):
            int_cal = convert_interval_unit(int_years, TemporalRepresentationUnit.CALENDAR_DATE, b_date, YearConventionEnum.SOLAR_365_25)
            json_snapshots.add(int_cal.model_dump_json())

        assert len(json_snapshots) == 1, "Non-deterministic serialization observed across 100 runs!"


# ==============================================================================
# Test Class 8: Comprehensive Attribution Matrix & Exegesis Verification
# ==============================================================================

class TestComprehensiveAttributionMatrix:
    """Verify the full 9-combination disposition truth table and multi-rule attribution."""

    @pytest.mark.parametrize(
        "disp_v,disp_c,expected_status",
        [
            ("FAVORABLE", "FAVORABLE", ConvergenceStatus.CONVERGENT),
            ("FAVORABLE", "UNFAVORABLE", ConvergenceStatus.DIVERGENT),
            ("FAVORABLE", "NEUTRAL", ConvergenceStatus.INDEPENDENT),
            ("UNFAVORABLE", "FAVORABLE", ConvergenceStatus.DIVERGENT),
            ("UNFAVORABLE", "UNFAVORABLE", ConvergenceStatus.CONVERGENT),
            ("UNFAVORABLE", "NEUTRAL", ConvergenceStatus.INDEPENDENT),
            ("NEUTRAL", "FAVORABLE", ConvergenceStatus.INDEPENDENT),
            ("NEUTRAL", "UNFAVORABLE", ConvergenceStatus.INDEPENDENT),
            ("NEUTRAL", "NEUTRAL", ConvergenceStatus.INDEPENDENT),
            ("", "FAVORABLE", ConvergenceStatus.INDEPENDENT),
            ("FAVORABLE", None, ConvergenceStatus.INDEPENDENT),
        ]
    )
    def test_all_disposition_combinations_with_overlap(self, disp_v, disp_c, expected_status):
        """Verify disposition comparison truth table when temporal overlap is True."""
        status = evaluate_convergence_status(disp_v, disp_c, has_temporal_overlap=True)
        assert status == expected_status

    @pytest.mark.parametrize(
        "disp_v,disp_c",
        [
            ("FAVORABLE", "FAVORABLE"),
            ("FAVORABLE", "UNFAVORABLE"),
            ("UNFAVORABLE", "UNFAVORABLE"),
            ("NEUTRAL", "NEUTRAL"),
        ]
    )
    def test_all_dispositions_without_overlap_are_disjoint(self, disp_v, disp_c):
        """When temporal overlap is False, disposition is irrelevant: always DISJOINT_NON_OVERLAPPING."""
        status = evaluate_convergence_status(disp_v, disp_c, has_temporal_overlap=False)
        assert status == ConvergenceStatus.DISJOINT_NON_OVERLAPPING

    def test_multiple_rules_per_period_preservation(self):
        """Multiple classical rules per period are preserved completely and deterministically."""
        v = SystemTimingAttribution(
            system=TimingSystemEnum.VIMSHOTTARI,
            profile_id="PARASHARI_V1",
            period_label="Jupiter-Venus",
            sub_period_type="ANTARDASHA",
            interval=TimingInterval(start=10.0, end=13.0, unit=TemporalRepresentationUnit.ELAPSED_YEARS),
            disposition="FAVORABLE",
            rule_ids=["TIME-DSH-01", "TIME-DSH-03", "PAR-DSH-YOGA-01"],
            supporting_factors=["10th lord activation", "Trine lord association"],
            formula_version="WP6-v1.0",
        )
        c = SystemTimingAttribution(
            system=TimingSystemEnum.CHARA_DASHA,
            profile_id="KN_RAO_V1",
            period_label="Dhanu-Mesha",
            sub_period_type="ANTARDASHA",
            interval=TimingInterval(start=11.0, end=14.0, unit=TemporalRepresentationUnit.ELAPSED_YEARS),
            disposition="FAVORABLE",
            rule_ids=["JAI-DSH-01", "JAI-DSH-06", "JAI-ASP-02"],
            supporting_factors=["AK aspect on 10th", "Benefic Argala from 2nd"],
            formula_version="WP7B-v1.0",
        )
        res = synthesize_timing_attributions([v], [c])
        comp = res.comparisons[0]

        assert comp.vimshottari_evidence.rule_ids == ["TIME-DSH-01", "TIME-DSH-03", "PAR-DSH-YOGA-01"]
        assert comp.chara_evidence.rule_ids == ["JAI-DSH-01", "JAI-DSH-06", "JAI-ASP-02"]
        assert len(comp.vimshottari_evidence.supporting_factors) == 2
        assert len(comp.chara_evidence.supporting_factors) == 2

    def test_multi_period_timeline_synthesis(self):
        """Synthesize 2 Vimshottari periods against 3 Chara Dasha periods (6 pairwise comparisons)."""
        v_periods = [
            SystemTimingAttribution(
                system=TimingSystemEnum.VIMSHOTTARI,
                profile_id="V_PROFILE",
                period_label="Jup-Sat",
                sub_period_type="ANTARDASHA",
                interval=TimingInterval(start=0.0, end=5.0, unit=TemporalRepresentationUnit.ELAPSED_YEARS),
                disposition="FAVORABLE",
                formula_version="WP6-v1.0",
            ),
            SystemTimingAttribution(
                system=TimingSystemEnum.VIMSHOTTARI,
                profile_id="V_PROFILE",
                period_label="Jup-Mer",
                sub_period_type="ANTARDASHA",
                interval=TimingInterval(start=5.0, end=10.0, unit=TemporalRepresentationUnit.ELAPSED_YEARS),
                disposition="UNFAVORABLE",
                formula_version="WP6-v1.0",
            ),
        ]
        c_periods = [
            SystemTimingAttribution(
                system=TimingSystemEnum.CHARA_DASHA,
                profile_id="C_PROFILE",
                period_label="Mesha",
                sub_period_type="MAHADASHA",
                interval=TimingInterval(start=0.0, end=4.0, unit=TemporalRepresentationUnit.ELAPSED_YEARS),
                disposition="FAVORABLE",
                formula_version="WP7B-v1.0",
            ),
            SystemTimingAttribution(
                system=TimingSystemEnum.CHARA_DASHA,
                profile_id="C_PROFILE",
                period_label="Vrishabha",
                sub_period_type="MAHADASHA",
                interval=TimingInterval(start=4.0, end=8.0, unit=TemporalRepresentationUnit.ELAPSED_YEARS),
                disposition="FAVORABLE",
                formula_version="WP7B-v1.0",
            ),
            SystemTimingAttribution(
                system=TimingSystemEnum.CHARA_DASHA,
                profile_id="C_PROFILE",
                period_label="Mithuna",
                sub_period_type="MAHADASHA",
                interval=TimingInterval(start=8.0, end=12.0, unit=TemporalRepresentationUnit.ELAPSED_YEARS),
                disposition="UNFAVORABLE",
                formula_version="WP7B-v1.0",
            ),
        ]
        res = synthesize_timing_attributions(v_periods, c_periods)
        assert len(res.comparisons) == 6
        assert res.overall_convergence == ConvergenceStatus.DIVERGENT


# ==============================================================================
# Test Class 9: Invariant Verification & Boundary Traceability Proof
# ==============================================================================

class TestBoundaryTraceabilityProof:
    """Mathematical proof that overlap bounds equal exact intersection and never average."""

    @pytest.mark.parametrize(
        "s1,e1,s2,e2",
        [
            (10.0, 20.0, 15.0, 25.0),
            (0.0, 12.0, 4.0, 8.0),
            (5.5, 14.25, 2.0, 10.0),
            (1.125, 9.875, 7.5, 18.0),
            (20.0, 30.0, 20.0, 25.0),
            (14.0, 28.0, 18.0, 28.0),
        ]
    )
    def test_overlap_boundaries_match_exact_min_max_never_averages(self, s1, e1, s2, e2):
        """
        Prove:
        intersection_start == max(s1, s2)
        intersection_end == min(e1, e2)
        intersection_start != (s1 + s2) / 2 (when s1 != s2)
        intersection_end != (e1 + e2) / 2 (when e1 != e2)
        """
        res = compare_numeric_intervals(s1, e1, s2, e2)
        assert res["has_overlap"] is True
        exp_start = max(s1, s2)
        exp_end = min(e1, e2)
        assert res["intersection_start"] == exp_start
        assert res["intersection_end"] == exp_end

        # Averaging prohibition
        avg_start = (s1 + s2) / 2.0
        avg_end = (e1 + e2) / 2.0
        if not math.isclose(s1, s2, abs_tol=1e-7):
            assert res["intersection_start"] != avg_start
        if not math.isclose(e1, e2, abs_tol=1e-7):
            assert res["intersection_end"] != avg_end


# ==============================================================================
# Test Class 10: Security Boundary & Gateway Isolation Audit
# ==============================================================================

class TestSecurityBoundariesAndIsolation:
    """Verify that WP7C2 remains strictly internal with zero public exposure."""

    def test_gateway_routes_contain_no_unapproved_synthesis_endpoints(self):
        """Gateway router must register zero public or private synthesis endpoints."""
        from gateway.main import app
        route_paths = [route.path for route in app.routes]

        forbidden_prefixes = [
            "/api/synthesis",
            "/api/jaimini/timing",
            "/api/timing/synthesis",
            "/api/cross-system",
        ]
        for f in forbidden_prefixes:
            for path in route_paths:
                assert not path.startswith(f), f"Forbidden route exposed: {path}"

    def test_prediction_timing_independent_of_jaimini_synthesis(self):
        """WP6 prediction timing module does not import or depend on jaimini_synthesis."""
        import modules.prediction.timing
        import modules.prediction.timing_fusion
        
        assert not hasattr(modules.prediction.timing, "synthesize_timing_attributions")
        assert not hasattr(modules.prediction.timing_fusion, "synthesize_timing_attributions")


# ==============================================================================
# Test Class 11: Governance Integrity & Unresolved Design Decisions
# ==============================================================================

class TestGovernanceIntegrityAndUnresolvedDecisions:
    """Verify that all lineage profiles, approval states, and disclaimers remain unapproved & transparent."""

    def test_response_disclaimer_and_limitations_always_present(self):
        """CrossSystemSynthesisResponse contains mandatory disclaimer and 3+ documented limitations."""
        v = SystemTimingAttribution(
            system=TimingSystemEnum.VIMSHOTTARI,
            profile_id="V_DEFAULT",
            period_label="Mars-Jupiter",
            sub_period_type="ANTARDASHA",
            interval=TimingInterval(start=1.0, end=2.0, unit=TemporalRepresentationUnit.ELAPSED_YEARS),
            formula_version="WP6-v1.0",
        )
        c = SystemTimingAttribution(
            system=TimingSystemEnum.CHARA_DASHA,
            profile_id="C_DEFAULT",
            period_label="Aries",
            sub_period_type="MAHADASHA",
            interval=TimingInterval(start=1.0, end=3.0, unit=TemporalRepresentationUnit.ELAPSED_YEARS),
            formula_version="WP7B-v1.0",
        )
        res = synthesize_timing_attributions([v], [c])
        assert len(res.disclaimer) > 20
        assert "Independent astrological frameworks" in res.disclaimer
        assert len(res.limitations) >= 3
        assert res.approval_status == "PENDING_HUMAN_JYOTISHI"
        assert res.is_approved is False

    def test_no_universal_calendar_convention_silently_selected(self):
        """System requires explicit YearConventionEnum; does not silently guess or convert without caller directive."""
        v = SystemTimingAttribution(
            system=TimingSystemEnum.VIMSHOTTARI,
            profile_id="V_DEFAULT",
            period_label="Mars-Jupiter",
            sub_period_type="ANTARDASHA",
            interval=TimingInterval(start=1.0, end=2.0, unit=TemporalRepresentationUnit.ELAPSED_YEARS),
            formula_version="WP6-v1.0",
        )
        c = SystemTimingAttribution(
            system=TimingSystemEnum.CHARA_DASHA,
            profile_id="C_DEFAULT",
            period_label="Aries",
            sub_period_type="MAHADASHA",
            interval=TimingInterval(start="2024-01-01", end="2025-01-01", unit=TemporalRepresentationUnit.CALENDAR_DATE),
            formula_version="WP7B-v1.0",
        )
        with pytest.raises(ValueError, match="Incompatible temporal units"):
            synthesize_timing_attributions([v], [c])

