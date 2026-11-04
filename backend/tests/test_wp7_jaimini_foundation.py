"""
Independent Test Suite for WP7A: Jaimini Astrology Foundational Layer.

Governing Standards:
- Master Specification v3.0 §10, §9.1, §9.2, §15, Appendix C
- WP0 Traceability TR-051 to TR-054
- ASTROLOGIC_WP7_DESIGN_DECISION_REGISTER.md
- ASTROLOGIC_WP7_FINAL_EVIDENCE_GATE.md

This suite provides independent verification of:
1. 144 Arudha Pada input combinations against an independently computed truth table.
2. Arudha 1st and 7th exception boundary cases.
3. Upapada Lagna (UL/A12) relative-house invariants ([2, 3, 4, 8, 9, 10]).
4. Rashi Drishti 36 directed pairs, zero self-aspects, zero adjacent aspects.
5. Chara Karakas: 7-karaka and 8-karaka role mappings.
6. Rahu traversal metric bounds (tau in (0.0, 30.0]).
7. Deterministic arcdegree tie-breaking and provenance serialization.
8. Input validation (NaN, Inf, malformed strings, missing planets).
9. Regression verification ensuring WP1–WP6 behavior is unchanged.
"""

import json
import math
import pytest

from shared.veda.jaimini_rules import (
    KarakaSchemeEnum,
    TieBreakerEnum,
    ArudhaExceptionEnum,
    DualLordshipEnum,
    CHARA_SIGNS,
    STHIRA_SIGNS,
    DVISVABHAVA_SIGNS,
    SIGN_NAMES_SK,
    SIGN_NAMES_EN,
    validate_finite_degree,
    normalize_sign_degree,
    parse_sign_index,
    compute_rahu_traversal_arc,
    calculate_chara_karakas,
    calculate_raw_arudha,
    apply_arudha_exception,
    calculate_arudha_pada,
    calculate_upapada_lagna,
    calculate_all_arudhas,
    get_rashi_drishti,
    get_all_rashi_drishti_pairs,
)

from modules.kundali.jaimini import (
    ApprovalStatus,
    SourceVerificationStatus,
    JaiminiProfileConfig,
    JaiminiFoundationResponse,
    compute_jaimini_foundation,
)


# ==============================================================================
# 1. Independent Arudha 144 Truth Table Builder (Pure Arithmetic, No Code Reuse)
# ==============================================================================

def _independent_expected_pada(house_sign: int, lord_sign: int, with_exception: bool = True) -> int:
    """
    Independently calculate expected Arudha Pada from first principles.
    Independent formula:
        count = lord_sign - house_sign
        if count < 0: count += 12
        raw = lord_sign + count
        raw_sign = ((raw - 1) % 12) + 1
    
    Exceptions:
        If raw_sign == house_sign -> shift 9 signs forward (+10th house)
        If raw_sign == 7th from house_sign -> shift 3 signs forward from house (+4th house)
    """
    count = lord_sign - house_sign
    if count < 0:
        count += 12
    raw = lord_sign + count
    raw_sign = ((raw - 1) % 12) + 1

    if not with_exception:
        return raw_sign

    h7 = ((house_sign - 1 + 6) % 12) + 1
    if raw_sign == house_sign:
        # Swastha exception: 10th from H
        return ((house_sign - 1 + 9) % 12) + 1
    elif raw_sign == h7:
        # Saptama exception: 4th from H (= 10th from 7th)
        return ((house_sign - 1 + 3) % 12) + 1
    return raw_sign


# ==============================================================================
# Test Class 1: All 144 Arudha Pada Combinations & Invariants
# ==============================================================================

class TestArudha144Combinations:
    """Independent verification of all 144 Arudha (House x Lord) combinations."""

    def test_all_144_combinations_match_independent_truth_table(self):
        """Verify all 144 combinations match the independently calculated truth table."""
        tested_count = 0
        for h in range(1, 13):
            for l in range(1, 13):
                expected_pada = _independent_expected_pada(h, l, with_exception=True)
                actual_res = calculate_arudha_pada(
                    house_num=h,
                    lagna_sign=1,  # If lagna=1, house h has sign h
                    lord_sign=l,
                    convention=ArudhaExceptionEnum.STANDARD_EXCEPTION,
                )
                actual_pada = actual_res["final_pada"]
                assert actual_pada == expected_pada, (
                    f"Mismatch at House={h}, Lord={l}: Expected={expected_pada}, Got={actual_pada}"
                )
                tested_count += 1
        assert tested_count == 144

    def test_arudha_pada_never_occupies_source_or_seventh_house(self):
        """
        Mathematical Invariant:
        Under standard BPHS 1st/7th exceptions, final Pada P can NEVER equal
        source house sign H or 7th sign from H (H7).
        """
        for h in range(1, 13):
            h7 = ((h - 1 + 6) % 12) + 1
            for l in range(1, 13):
                res = calculate_arudha_pada(h, 1, l, ArudhaExceptionEnum.STANDARD_EXCEPTION)
                final_p = res["final_pada"]
                assert final_p != h, f"Violation: Final pada {final_p} equals house sign {h} (Lord={l})"
                assert final_p != h7, f"Violation: Final pada {final_p} equals 7th sign {h7} (House={h}, Lord={l})"

    def test_no_exception_mode_retains_raw_projections(self):
        """When NO_EXCEPTION is configured, raw pada is returned directly without shifting."""
        for h in range(1, 13):
            for l in range(1, 13):
                expected_raw = _independent_expected_pada(h, l, with_exception=False)
                res = calculate_arudha_pada(h, 1, l, ArudhaExceptionEnum.NO_EXCEPTION)
                assert res["final_pada"] == expected_raw
                assert res["exception_applied"] is False


# ==============================================================================
# Test Class 2: Specific Exception Boundary Cases
# ==============================================================================

class TestArudhaBoundaryExceptions:
    """Explicit tests for classical 1st/7th boundary cases."""

    def test_lord_in_1st_swastha_exception(self):
        """Lord in 1st house: raw pada is in 1st -> shifts to 10th."""
        # Aries Lagna, 1st Lord (Mars) in Aries (1)
        res = calculate_arudha_pada(1, 1, 1, ArudhaExceptionEnum.STANDARD_EXCEPTION)
        assert res["raw_pada"] == 1
        assert res["final_pada"] == 10  # Capricorn
        assert res["exception_applied"] is True
        assert res["exception_type"] == "SWASTHA_10TH_SHIFT"

    def test_lord_in_7th_swastha_exception(self):
        """Lord in 7th house: raw pada is in 1st -> shifts to 10th."""
        # Aries Lagna, 1st Lord (Mars) in Libra (7)
        # Distance = 7 signs. 7 signs from Libra is Aries (1).
        # Raw pada is 1 -> Swastha exception -> 10th (Capricorn).
        res = calculate_arudha_pada(1, 1, 7, ArudhaExceptionEnum.STANDARD_EXCEPTION)
        assert res["raw_pada"] == 1
        assert res["final_pada"] == 10
        assert res["exception_applied"] is True
        assert res["exception_type"] == "SWASTHA_10TH_SHIFT"

    def test_lord_in_4th_saptama_exception(self):
        """Lord in 4th house: raw pada is in 7th -> shifts to 4th (10th from 7th)."""
        # Aries Lagna, 1st Lord (Mars) in Cancer (4)
        # Distance = 4 signs. 4 signs from Cancer is Libra (7).
        # Raw pada is 7 -> Saptama exception -> 4th from House 1 = Cancer (4).
        res = calculate_arudha_pada(1, 1, 4, ArudhaExceptionEnum.STANDARD_EXCEPTION)
        assert res["raw_pada"] == 7
        assert res["final_pada"] == 4
        assert res["exception_applied"] is True
        assert res["exception_type"] == "SAPTAMA_4TH_SHIFT"

    def test_lord_in_10th_saptama_exception(self):
        """Lord in 10th house: raw pada is in 7th -> shifts to 4th."""
        # Aries Lagna, 1st Lord (Mars) in Capricorn (10)
        # Distance = 10 signs. 10 signs from Capricorn is Libra (7).
        # Raw pada is 7 -> Saptama exception -> 4th from House 1 = Cancer (4).
        res = calculate_arudha_pada(1, 1, 10, ArudhaExceptionEnum.STANDARD_EXCEPTION)
        assert res["raw_pada"] == 7
        assert res["final_pada"] == 4
        assert res["exception_applied"] is True
        assert res["exception_type"] == "SAPTAMA_4TH_SHIFT"

    def test_lord_in_2nd_no_exception(self):
        """Lord in 2nd house: raw pada is in 3rd -> no exception fires."""
        # Aries Lagna, 1st Lord in Taurus (2) -> Gemini (3)
        res = calculate_arudha_pada(1, 1, 2, ArudhaExceptionEnum.STANDARD_EXCEPTION)
        assert res["raw_pada"] == 3
        assert res["final_pada"] == 3
        assert res["exception_applied"] is False
        assert res["exception_type"] is None


# ==============================================================================
# Test Class 3: Upapada Lagna (UL / A12) Relative-House Invariants
# ==============================================================================

class TestUpapadaLagnaInvariants:
    """
    Upapada Lagna (UL / A12) relative-house invariant tests.
    
    NOTE ON GOVERNANCE:
    These invariant tests verify software mathematical consistency with the BPHS
    Pada-locus formula; they do NOT assert or test classical interpretive authority.
    """

    def test_ul_relative_house_invariant_set(self):
        """
        Across all 144 possible combinations (12 Lagnas x 12 12th lord placements),
        Upapada Lagna can strictly land ONLY in houses [2, 3, 4, 8, 9, 10] relative
        to the natal Lagna under whole-sign houses and standard BPHS exceptions.
        
        Houses [1, 5, 6, 7, 11, 12] are mathematically impossible.
        """
        allowed_relative_houses = {2, 3, 4, 8, 9, 10}
        observed_relative_houses = set()

        for lagna in range(1, 13):
            for l12 in range(1, 13):
                ul = calculate_upapada_lagna(
                    lagna_sign=lagna,
                    twelfth_lord_sign=l12,
                    convention=ArudhaExceptionEnum.STANDARD_EXCEPTION,
                )
                rel_h = ul["house_from_lagna"]
                observed_relative_houses.add(rel_h)
                assert rel_h in allowed_relative_houses, (
                    f"Invariant violated: Lagna={lagna}, 12thLord={l12} produced UL in relative house {rel_h}"
                )

        assert observed_relative_houses == allowed_relative_houses, (
            f"Expected full coverage of {allowed_relative_houses}, got {observed_relative_houses}"
        )


# ==============================================================================
# Test Class 4: Rashi Drishti Sign-Aspect Mapping
# ==============================================================================

class TestRashiDrishti:
    """Tests for Jaimini Rashi Drishti (sign-based structural aspects)."""

    def test_movable_signs_aspect_fixed_except_adjacent(self):
        """
        Movable signs (1, 4, 7, 10) aspect Fixed signs (2, 5, 8, 11)
        EXCEPT the adjacent next sign (S + 1).
        """
        # Aries (1) -> Leo (5), Scorpio (8), Aquarius (11) [Excludes Taurus (2)]
        assert get_rashi_drishti(1) == [5, 8, 11]
        # Cancer (4) -> Taurus (2), Scorpio (8), Aquarius (11) [Excludes Leo (5)]
        assert get_rashi_drishti(4) == [2, 8, 11]
        # Libra (7) -> Taurus (2), Leo (5), Aquarius (11) [Excludes Scorpio (8)]
        assert get_rashi_drishti(7) == [2, 5, 11]
        # Capricorn (10) -> Taurus (2), Leo (5), Scorpio (8) [Excludes Aquarius (11)]
        assert get_rashi_drishti(10) == [2, 5, 8]

    def test_fixed_signs_aspect_movable_except_adjacent(self):
        """
        Fixed signs (2, 5, 8, 11) aspect Movable signs (1, 4, 7, 10)
        EXCEPT the adjacent preceding sign (S - 1).
        """
        # Taurus (2) -> Cancer (4), Libra (7), Capricorn (10) [Excludes Aries (1)]
        assert get_rashi_drishti(2) == [4, 7, 10]
        # Leo (5) -> Aries (1), Libra (7), Capricorn (10) [Excludes Cancer (4)]
        assert get_rashi_drishti(5) == [1, 7, 10]
        # Scorpio (8) -> Aries (1), Cancer (4), Capricorn (10) [Excludes Libra (7)]
        assert get_rashi_drishti(8) == [1, 4, 10]
        # Aquarius (11) -> Aries (1), Cancer (4), Libra (7) [Excludes Capricorn (10)]
        assert get_rashi_drishti(11) == [1, 4, 7]

    def test_dual_signs_aspect_other_dual_signs(self):
        """
        Dual signs (3, 6, 9, 12) aspect all other Dual signs.
        """
        # Gemini (3) -> Virgo (6), Sagittarius (9), Pisces (12)
        assert get_rashi_drishti(3) == [6, 9, 12]
        # Virgo (6) -> Gemini (3), Sagittarius (9), Pisces (12)
        assert get_rashi_drishti(6) == [3, 9, 12]
        # Sagittarius (9) -> Gemini (3), Virgo (6), Pisces (12)
        assert get_rashi_drishti(9) == [3, 6, 12]
        # Pisces (12) -> Gemini (3), Virgo (6), Sagittarius (9)
        assert get_rashi_drishti(12) == [3, 6, 9]

    def test_rashi_drishti_global_invariants(self):
        """All 36 directed pairs, zero self-aspects, zero adjacent aspects."""
        pairs = get_all_rashi_drishti_pairs()
        assert len(pairs) == 12

        total_pairs = sum(len(aspects) for aspects in pairs.values())
        assert total_pairs == 36

        for sign, aspects in pairs.items():
            assert len(aspects) == 3
            # Zero self-aspects
            assert sign not in aspects, f"Sign {sign} aspects itself!"
            # Zero adjacent aspects
            next_adj = (sign % 12) + 1
            prev_adj = ((sign - 2) % 12) + 1
            assert next_adj not in aspects, f"Sign {sign} aspects next adjacent {next_adj}"
            assert prev_adj not in aspects, f"Sign {sign} aspects previous adjacent {prev_adj}"


# ==============================================================================
# Test Class 5: Chara Karakas (7-k vs 8-k Schemes, Rahu Bounds & Ties)
# ==============================================================================

class TestCharaKarakas:
    """Tests for Chara Karaka rankings, Rahu traversal metric, and tie-breaking."""

    def test_seven_karaka_scheme_mapping(self):
        """7-karaka scheme maps Sun-Saturn into 7 roles; ignores Rahu."""
        planets = {
            "Sun": 28.5,       # Arc: 28.5 -> AK
            "Moon": 24.0,      # Arc: 24.0 -> AmK
            "Mars": 19.2,      # Arc: 19.2 -> BK
            "Mercury": 15.0,   # Arc: 15.0 -> MK
            "Jupiter": 11.5,   # Arc: 11.5 -> PK
            "Venus": 8.0,      # Arc: 8.0  -> GK
            "Saturn": 2.1,     # Arc: 2.1  -> DK
            "Rahu": 29.9,      # Ignored in 7-k scheme
        }
        res = calculate_chara_karakas(planets, scheme=KarakaSchemeEnum.SEVEN_KARAKA)
        karakas = res["karakas"]

        assert len(karakas) == 7
        assert karakas["AK"]["planet"] == "Sun"
        assert karakas["AmK"]["planet"] == "Moon"
        assert karakas["BK"]["planet"] == "Mars"
        assert karakas["MK"]["planet"] == "Mercury"
        assert karakas["PK"]["planet"] == "Jupiter"
        assert karakas["GK"]["planet"] == "Venus"
        assert karakas["DK"]["planet"] == "Saturn"
        assert "PiK" not in karakas
        assert res["tie_broken"] is False

    def test_eight_karaka_scheme_with_rahu_inversion(self):
        """
        8-karaka scheme includes Rahu with inverted traversed arc tau = 30 - deg.
        Rahu at raw longitude 1.0° in sign:
            Traversed arc tau = 30.0 - 1.0 = 29.0°.
            Becomes AK if all other planets have arc < 29.0°.
        """
        planets = {
            "Sun": 25.0,
            "Moon": 22.0,
            "Mars": 18.0,
            "Mercury": 14.0,
            "Jupiter": 10.0,
            "Venus": 7.0,
            "Saturn": 3.0,
            "Rahu": 31.0,  # Sign 2 (Taurus), 1.0° in sign. Traversed arc = 29.0°
        }
        res = calculate_chara_karakas(
            planets,
            scheme=KarakaSchemeEnum.EIGHT_KARAKA,
            rahu_reverse=True
        )
        karakas = res["karakas"]

        assert len(karakas) == 8
        assert karakas["AK"]["planet"] == "Rahu"
        assert karakas["AK"]["traversed_arc"] == 29.0
        assert karakas["AmK"]["planet"] == "Sun"
        assert karakas["BK"]["planet"] == "Moon"
        assert karakas["MK"]["planet"] == "Mars"
        assert karakas["PiK"]["planet"] == "Mercury"  # Pitrikaraka at rank 4
        assert karakas["PK"]["planet"] == "Jupiter"   # Putrakaraka at rank 5
        assert karakas["GK"]["planet"] == "Venus"
        assert karakas["DK"]["planet"] == "Saturn"

    def test_rahu_traversal_boundary_values(self):
        """
        Rahu traversal arc domain: tau in (0.0, 30.0].
        At 0.0° in sign, tau = 30.0°.
        At 29.999999° in sign, tau = 0.000001°.
        """
        # Node entering sign at 29.999°
        tau_entry = compute_rahu_traversal_arc(29.999, rahu_reverse=True)
        assert math.isclose(tau_entry, 0.001, abs_tol=1e-4)

        # Node exiting sign at 0.0°
        tau_exit = compute_rahu_traversal_arc(0.0, rahu_reverse=True)
        assert math.isclose(tau_exit, 30.0, abs_tol=1e-4)

        # Node at exact midpoint 15.0°
        tau_mid = compute_rahu_traversal_arc(15.0, rahu_reverse=True)
        assert math.isclose(tau_mid, 15.0, abs_tol=1e-4)

    def test_equal_degree_tie_breaker_uses_natural_speed(self):
        """
        When two planets have identical degrees down to 1e-5°,
        NATURAL_SPEED secondary key breaks tie deterministically:
        Sun (1) > Moon (2) > Mars (3) > Mercury (4) > Jupiter (5) > Venus (6) > Saturn (7) > Rahu (8).
        """
        planets = {
            "Sun": 20.0,
            "Moon": 18.0,
            "Mars": 15.00000,     # Identical degree to Jupiter
            "Jupiter": 15.00000,  # Identical degree to Mars
            "Mercury": 10.0,
            "Venus": 5.0,
            "Saturn": 1.0,
        }
        res = calculate_chara_karakas(
            planets,
            scheme=KarakaSchemeEnum.SEVEN_KARAKA,
            tie_breaker=TieBreakerEnum.NATURAL_SPEED,
        )
        assert res["tie_broken"] is True
        assert len(res["tie_break_details"]) == 1

        # Mars (speed rank 3) must rank ahead of Jupiter (speed rank 5)
        karakas = res["karakas"]
        assert karakas["BK"]["planet"] == "Mars"
        assert karakas["MK"]["planet"] == "Jupiter"


# ==============================================================================
# Test Class 6: Input Validation, NaN, Inf, and Malformed Inputs
# ==============================================================================

class TestInputValidation:
    """Robust error handling for non-finite, missing, or malformed data."""

    def test_nan_degree_raises_value_error(self):
        """NaN degree raises ValueError."""
        with pytest.raises(ValueError, match="finite float"):
            validate_finite_degree(float("nan"))

    def test_infinite_degree_raises_value_error(self):
        """Inf and -Inf raise ValueError."""
        with pytest.raises(ValueError, match="finite float"):
            validate_finite_degree(float("inf"))
        with pytest.raises(ValueError, match="finite float"):
            validate_finite_degree(float("-inf"))

    def test_missing_planet_in_7_karaka_scheme_raises_value_error(self):
        """Missing required body in 7-karaka scheme raises clear ValueError."""
        incomplete_planets = {
            "Sun": 10.0,
            "Moon": 12.0,
            # Saturn missing
            "Mars": 14.0,
            "Mercury": 16.0,
            "Jupiter": 18.0,
            "Venus": 20.0,
        }
        with pytest.raises(ValueError, match="Missing required bodies"):
            calculate_chara_karakas(incomplete_planets, scheme=KarakaSchemeEnum.SEVEN_KARAKA)

    def test_missing_rahu_in_8_karaka_scheme_raises_value_error(self):
        """Missing Rahu in 8-karaka scheme raises clear ValueError."""
        planets_without_rahu = {
            "Sun": 10.0, "Moon": 12.0, "Mars": 14.0,
            "Mercury": 16.0, "Jupiter": 18.0, "Venus": 20.0, "Saturn": 22.0,
        }
        with pytest.raises(ValueError, match="Rahu"):
            calculate_chara_karakas(planets_without_rahu, scheme=KarakaSchemeEnum.EIGHT_KARAKA)

    def test_invalid_sign_indices_raise_value_error(self):
        """Out of bounds sign integers or unrecognized names raise ValueError."""
        for invalid_sign in [0, 13, -1, 99, "Atlantis", ""]:
            with pytest.raises(ValueError):
                parse_sign_index(invalid_sign)


# ==============================================================================
# Test Class 7: Foundation Orchestrator & Provenance Serialization
# ==============================================================================

class TestFoundationOrchestrator:
    """End-to-end foundation orchestrator tests and provenance serialization."""

    @pytest.fixture
    def sample_chart_planets(self):
        """Standard valid sample chart longitudes."""
        return {
            "Sun": 15.5,        # Aries (Sign 1), 15.5°
            "Moon": 42.0,       # Taurus (Sign 2), 12.0°
            "Mars": 80.0,       # Gemini (Sign 3), 20.0°
            "Mercury": 125.0,   # Leo (Sign 5), 5.0°
            "Jupiter": 195.0,   # Libra (Sign 7), 15.0°
            "Venus": 240.0,     # Sagittarius (Sign 9), 0.0°
            "Saturn": 310.0,    # Aquarius (Sign 11), 10.0°
            "Rahu": 350.0,      # Pisces (Sign 12), 20.0°
        }

    def test_compute_jaimini_foundation_output_contract(self, sample_chart_planets):
        """Verify the full response contract and deterministic output."""
        response = compute_jaimini_foundation(
            planet_positions=sample_chart_planets,
            lagna_sign=1,  # Aries Lagna
        )

        assert isinstance(response, JaiminiFoundationResponse)
        assert len(response.karakas) == 7
        assert len(response.arudhas) == 12
        assert len(response.rashi_drishti) == 12

        # Check explicit Upapada Lagna
        assert response.upapada_lagna.is_upapada is True
        assert response.upapada_lagna.house_num == 12
        assert response.upapada_lagna.house_from_lagna in [2, 3, 4, 8, 9, 10]

    def test_provenance_records_all_nine_decisions_as_pending(self, sample_chart_planets):
        """
        Verify that all 9 decisions (DEC-JAI-01 to DEC-JAI-09) are serialized
        in provenance metadata and marked PENDING_HUMAN_JYOTISHI / unapproved.
        """
        response = compute_jaimini_foundation(
            planet_positions=sample_chart_planets,
            lagna_sign=1,
        )
        prov = response.provenance

        assert prov.profile_id == "PROVISIONAL_KN_RAO_DEFAULT"
        assert prov.profile_is_approved is False
        assert prov.profile_approval_status == ApprovalStatus.PROVISIONAL_DEVELOPMENT_ONLY.value

        decision_ids = [d.decision_id for d in prov.decisions]
        expected_ids = [f"DEC-JAI-0{i}" for i in range(1, 10)]
        assert decision_ids == expected_ids

        for d in prov.decisions:
            assert d.is_approved is False
            assert d.approval_status == ApprovalStatus.PENDING_HUMAN_JYOTISHI

    def test_provenance_json_serializability(self, sample_chart_planets):
        """Verify the entire response serializes to valid JSON without error."""
        response = compute_jaimini_foundation(
            planet_positions=sample_chart_planets,
            lagna_sign=1,
        )
        raw_json = response.model_dump_json()
        parsed = json.loads(raw_json)

        assert "karakas" in parsed
        assert "arudhas" in parsed
        assert "upapada_lagna" in parsed
        assert "rashi_drishti" in parsed
        assert parsed["provenance"]["formula_version"] in [
            "WP7A-JAIMINI-FOUNDATION-v1.0",
            "WP7B-JAIMINI-FOUNDATION-v1.0",
            "WP7C1-JAIMINI-FOUNDATION-v1.0",
            "WP7C2-JAIMINI-FOUNDATION-v1.0",
        ]


# ==============================================================================
# Test Class 8: Regression Isolation (WP1–WP6 Integrity)
# ==============================================================================

class TestRegressionIsolation:
    """Ensure WP1–WP6 modules and imports remain untouched and functional."""

    def test_wp1_shadbala_import_and_integrity(self):
        """WP1 Shadbala calculations remain functional."""
        from shared.veda import shadbala, compute_sthana_bala
        assert callable(shadbala)
        assert callable(compute_sthana_bala)

    def test_wp2_lordship_matrix_integrity(self):
        """WP2 Lordship Matrix remains functional."""
        from shared.veda import build_lagna_matrix, get_lagna_matrix
        m = build_lagna_matrix("Mesha")
        assert m.lagna == "Mesha"
        assert m.house_lords[1] == "Mars"

    def test_wp5_domain_catalogs_integrity(self):
        """WP5 domain rule packs remain intact."""
        from shared.veda import (
            CAREER_RULES_CATALOG,
            MARRIAGE_RULES_CATALOG,
            WEALTH_RULES_CATALOG,
            HEALTH_RULES_CATALOG,
            EDUCATION_RULES_CATALOG,
            PROGENY_RULES_CATALOG,
            PROPERTY_RULES_CATALOG,
        )
        assert len(CAREER_RULES_CATALOG) == 24
        assert len(MARRIAGE_RULES_CATALOG) == 26
        assert len(WEALTH_RULES_CATALOG) == 26
        assert len(HEALTH_RULES_CATALOG) == 12
        assert len(EDUCATION_RULES_CATALOG) == 24
        assert len(PROGENY_RULES_CATALOG) == 21
        assert len(PROPERTY_RULES_CATALOG) == 27

    def test_wp6_timing_and_vedha_integrity(self):
        """WP6 Timing engine, Ashtakavarga and Vedha remain intact."""
        from shared.veda import (
            compute_bav,
            compute_sav,
            check_transit_vedha,
            TIMING_RULES_CATALOG,
            SAV_TOTAL_INVARIANT,
        )
        assert SAV_TOTAL_INVARIANT == 337
        assert len(TIMING_RULES_CATALOG) == 25
