"""
Independent Unit & Integration Tests for WP7C1: Jaimini Evidence Primitives.

Governing Standards:
- Master Specification v3.0 §10, §9.9, §13.2, §15, Appendix C
- WP0 Traceability Matrix v1.1: TR-051, TR-052, TR-053, TR-054
- ASTROLOGIC_WP7_DESIGN_DECISION_REGISTER.md (DEC-JAI-07, DEC-JAI-08)
- ASTROLOGIC_WP7_RULE_CATALOG_DRAFT.md (Rule JAI-ASP-02, Rule JAI-KAR-01)

Scope Under Test:
1. Pure Navamsha (D9) sign derivation and pada boundary math.
2. Karakamsa framing: NAVAMSHA_IN_RASHI vs KARAKAMSA_KUNDALI_D9.
3. Missing Atmakaraka, invalid inputs, and error handling.
4. Argala & Virodhargala evaluation (Rule JAI-ASP-02):
   - Primary pairs (4 vs 10, 2 vs 12, 11 vs 3)
   - Secondary pair (5 vs 9)
   - Obstruction threshold: N_V >= N_A -> obstructed; N_V < N_A -> active
   - Empty, positive, negative, and conflicting configurations
   - Benefic vs Malefic argala nature (SHUBHA, PAPA, MIXED, NONE)
5. Ketu direction behavior: STANDARD_ARGALA vs REVERSE_KETU_ARGALA (DEC-JAI-08).
6. Deterministic JSON serialization and provenance integrity.
7. Regression isolation for WP7A, WP7B, and WP1-WP6.
"""

from __future__ import annotations

import json
import math
import pytest
from pydantic import ValidationError

from shared.veda.jaimini_rules import (
    KarakaSchemeEnum,
    SIGN_NAMES_SK,
    SIGN_NAMES_EN,
)
from shared.veda.jaimini_evidence import (
    KarakamsaFramingMode,
    KetuArgalaConvention,
    calculate_navamsha_sign,
    evaluate_karakamsa,
    evaluate_argala,
    evaluate_all_house_argalas,
    ARGALA_PAIRS,
    NATURAL_BENEFICS,
    NATURAL_MALEFICS,
)
from modules.kundali.jaimini import (
    JaiminiProfileConfig,
    KarakamsaEvidenceResponse,
    ArgalaPositionEvidence,
    ArgalaEvidenceResponse,
    JaiminiFoundationResponse,
    compute_jaimini_foundation,
    compute_karakamsa,
    compute_argala,
    ApprovalStatus,
    SourceVerificationStatus,
)


@pytest.fixture
def standard_chart_planets():
    """
    Standard test chart longitudes:
    Sun: Aries 15°30' (15.5°)
    Moon: Taurus 12°00' (42.0°)
    Mars: Gemini 20°00' (80.0°)
    Mercury: Leo 5°00' (125.0°)
    Jupiter: Sagittarius 28°45' (268.75°) -> Highest arc in sign = AK (28.75°)
    Venus: Pisces 18°20' (348.3333°)
    Saturn: Libra 8°10' (188.1667°)
    Rahu: Capricorn 10°00' (280.0°)
    Ketu: Cancer 10°00' (100.0°)
    """
    return {
        "Sun": 15.5,
        "Moon": 42.0,
        "Mars": 80.0,
        "Mercury": 125.0,
        "Jupiter": 268.75,
        "Venus": 348.3333333333333,
        "Saturn": 188.16666666666666,
        "Rahu": 280.0,
        "Ketu": 100.0,
    }


# ==============================================================================
# Test Class 1: Pure Navamsha Math & Pada Boundaries
# ==============================================================================

class TestNavamshaPadaBoundaries:
    """Verify mathematically exact D9 pada derivation across movable, fixed, dual signs."""

    def test_movable_sign_navamsha_starts_from_self(self):
        """Movable signs (Aries=1, Cancer=4, Libra=7, Capricorn=10) start D9 from self."""
        # Aries (1): Pada 0 (0° - 3°20') -> Aries (1)
        assert calculate_navamsha_sign(1, 1.0) == 1
        # Aries (1): Pada 8 (26°40' - 30°) -> Sagittarius (9)
        assert calculate_navamsha_sign(1, 28.5) == 9

        # Cancer (4): Pada 0 -> Cancer (4)
        assert calculate_navamsha_sign(4, 2.0) == 4
        # Cancer (4): Pada 8 -> Pisces (12)
        assert calculate_navamsha_sign(4, 29.0) == 12

    def test_fixed_sign_navamsha_starts_from_ninth(self):
        """Fixed signs (Taurus=2, Leo=5, Scorpio=8, Aquarius=11) start D9 from 9th."""
        # Taurus (2): 9th from Taurus is Capricorn (10)
        # Pada 0 -> Capricorn (10)
        assert calculate_navamsha_sign(2, 1.5) == 10
        # Pada 1 (3°20' - 6°40') -> Aquarius (11)
        assert calculate_navamsha_sign(2, 4.0) == 11
        # Pada 8 -> Virgo (6)
        assert calculate_navamsha_sign(2, 29.5) == 6

        # Leo (5): 9th from Leo is Aries (1)
        # Pada 0 -> Aries (1)
        assert calculate_navamsha_sign(5, 0.5) == 1

    def test_dual_sign_navamsha_starts_from_fifth(self):
        """Dual signs (Gemini=3, Virgo=6, Sagittarius=9, Pisces=12) start D9 from 5th."""
        # Sagittarius (9): 5th from Sagittarius is Aries (1)
        # Jupiter at 28°45' (28.75°) in Sagittarius:
        # Pada index = int(28.75 / (30/9)) = int(28.75 / 3.33333) = int(8.625) = 8
        # Navamsha sign = ((1 - 1 + 8) % 12) + 1 = 9 (Sagittarius)
        assert calculate_navamsha_sign(9, 28.75) == 9

        # Gemini (3): 5th from Gemini is Libra (7)
        # Pada 0 -> Libra (7)
        assert calculate_navamsha_sign(3, 1.0) == 7

    def test_exact_pada_boundary_transitions(self):
        """Ensure boundary values transition monotonically without edge aliasing."""
        pada_deg = 30.0 / 9.0  # 3.3333333333333335
        # Aries Pada 0: [0.0, pada_deg)
        assert calculate_navamsha_sign(1, 0.0) == 1
        assert calculate_navamsha_sign(1, pada_deg - 1e-7) == 1
        assert calculate_navamsha_sign(1, pada_deg + 1e-7) == 2


# ==============================================================================
# Test Class 2: Karakamsa Framing (NAVAMSHA_IN_RASHI vs KARAKAMSA_KUNDALI_D9)
# ==============================================================================

class TestKarakamsaFraming:
    """Verify both Karakamsa framing modes under DEC-JAI-07."""

    def test_atmakaraka_selection_and_navamsha_sign(self, standard_chart_planets):
        """AK is Jupiter with highest degree in sign (28.75°), Navamsha is Sagittarius."""
        res = evaluate_karakamsa(
            planet_positions=standard_chart_planets,
            lagna_sign=1,  # Aries Lagna
            framing_mode=KarakamsaFramingMode.NAVAMSHA_IN_RASHI,
        )
        assert res["ak_planet"] == "Jupiter"
        assert res["ak_d1_sign"] == 9  # Sagittarius
        assert pytest.approx(res["ak_degree_in_sign"], rel=1e-4) == 28.75
        assert res["karakamsa_sign"] == 9  # Sagittarius
        assert res["karakamsa_sign_name"] == "Dhanu"

    def test_framing_navamsha_in_rashi(self, standard_chart_planets):
        """In NAVAMSHA_IN_RASHI, Karakamsa is projected into D1 chart."""
        res = evaluate_karakamsa(
            planet_positions=standard_chart_planets,
            lagna_sign=1,  # Aries Lagna
            framing_mode=KarakamsaFramingMode.NAVAMSHA_IN_RASHI,
        )
        assert res["framing_mode"] == "NAVAMSHA_IN_RASHI"
        assert res["frame_chart_type"] == "D1_RASHI"
        # Since Lagna is Aries (1) and Karakamsa sign is Sagittarius (9),
        # Karakamsa is in 9th house from natal Lagna in D1.
        assert res["house_from_lagna"] == 9

        # House 1 from Karakamsa is Sagittarius (9)
        assert res["signs_by_house"][1] == 9
        # In D1, Jupiter is in Sagittarius, so House 1 contains Jupiter
        assert "Jupiter" in res["planets_by_house"][1]

        # House 5 from Karakamsa is Aries (1) -> Sun is in Aries in D1
        assert res["signs_by_house"][5] == 1
        assert "Sun" in res["planets_by_house"][5]

    def test_framing_karakamsa_kundali_d9(self, standard_chart_planets):
        """In KARAKAMSA_KUNDALI_D9, Karakamsa sign becomes Lagna of D9 chart."""
        res = evaluate_karakamsa(
            planet_positions=standard_chart_planets,
            lagna_sign=1,
            framing_mode=KarakamsaFramingMode.KARAKAMSA_KUNDALI_D9,
        )
        assert res["framing_mode"] == "KARAKAMSA_KUNDALI_D9"
        assert res["frame_chart_type"] == "D9_NAVAMSHA"
        assert res["house_from_lagna"] is None

        # House 1 from Karakamsa is S_nav = 9 (Sagittarius)
        assert res["signs_by_house"][1] == 9

        # In D9, check where planets land:
        # Sun at 15.5° Aries: pada 4 (13°20' - 16°40') -> Leo (5)
        # Leo is 9th house from Sagittarius (9): ((5 - 9) % 12) + 1 = 9
        assert res["signs_by_house"][9] == 5
        assert "Sun" in res["planets_by_house"][9]

    def test_custom_d9_sign_placements_override(self, standard_chart_planets):
        """Explicit D9 placements override automatic pada derivation when supplied."""
        custom_d9 = {
            "Jupiter": 1,  # Force Jupiter D9 to Aries (1)
            "Sun": 10,     # Force Sun D9 to Capricorn (10)
        }
        res = evaluate_karakamsa(
            planet_positions=standard_chart_planets,
            lagna_sign=1,
            framing_mode=KarakamsaFramingMode.KARAKAMSA_KUNDALI_D9,
            d9_sign_placements=custom_d9,
        )
        assert res["karakamsa_sign"] == 1  # Driven by custom Jupiter D9
        assert res["signs_by_house"][1] == 1
        assert "Jupiter" in res["planets_by_house"][1]


# ==============================================================================
# Test Class 3: Missing Inputs & Error Handling
# ==============================================================================

class TestKarakamsaErrorHandling:
    """Verify robust rejection of invalid or incomplete inputs."""

    def test_missing_required_candidate_planets_raises_error(self):
        """If required planets are missing so AK cannot be found, raise ValueError."""
        incomplete_planets = {"Sun": 15.0, "Moon": 40.0}
        with pytest.raises(ValueError, match="Missing required bodies"):
            evaluate_karakamsa(
                planet_positions=incomplete_planets,
                lagna_sign=1,
            )

    def test_invalid_sign_indices_raise_value_error(self, standard_chart_planets):
        """Invalid Lagna signs raise ValueError."""
        with pytest.raises(ValueError, match="Sign integer must be between 1 and 12"):
            evaluate_karakamsa(
                planet_positions=standard_chart_planets,
                lagna_sign=13,
            )

    def test_nan_or_inf_in_planet_positions_raises_error(self, standard_chart_planets):
        """NaN or Inf degrees raise ValueError."""
        corrupted = dict(standard_chart_planets)
        corrupted["Sun"] = float("nan")
        with pytest.raises(ValueError, match="Planetary degree must be a finite float"):
            evaluate_karakamsa(
                planet_positions=corrupted,
                lagna_sign=1,
            )


# ==============================================================================
# Test Class 4: Argala & Virodhargala Mechanics (Rule JAI-ASP-02)
# ==============================================================================

class TestArgalaMechanics:
    """Verify Argala positions, obstruction thresholds, and benefic/malefic nature."""

    def test_primary_argala_pair_4th_vs_10th_unobstructed(self):
        """Planet in 4th house from target sign produces active Argala if 10th is empty."""
        target_sign = 1  # Aries
        # 4th from Aries is Cancer (4); 10th from Aries is Capricorn (10)
        placements = {
            "Jupiter": 4,  # In Cancer (4th)
        }
        res = evaluate_argala(target_sign=target_sign, planet_placements=placements)
        pos4 = res["positions"][4]
        assert pos4["has_argala"] is True
        assert pos4["is_active"] is True
        assert pos4["is_obstructed"] is False
        assert pos4["argala_planets"] == ["Jupiter"]
        assert pos4["virodha_planets"] == []
        assert 4 in res["active_argalas"]
        assert res["net_status"] == "ACTIVE_ARGALA"
        assert pos4["argala_nature"] == "SHUBHA"

    def test_primary_argala_pair_4th_vs_10th_obstructed(self):
        """Planet in 4th house is obstructed by planet in 10th house (N_V >= N_A)."""
        target_sign = 1  # Aries
        placements = {
            "Jupiter": 4,   # 4th house
            "Saturn": 10,   # 10th house (Virodha)
        }
        res = evaluate_argala(target_sign=target_sign, planet_placements=placements)
        pos4 = res["positions"][4]
        assert pos4["has_argala"] is True
        assert pos4["is_obstructed"] is True
        assert pos4["is_active"] is False
        assert 4 in res["obstructed_argalas"]
        assert res["net_status"] == "OBSTRUCTED_ARGALA"

    def test_primary_argala_pair_2nd_vs_12th(self):
        """2nd house Argala obstructed by 12th house."""
        target_sign = 5  # Leo
        # 2nd from Leo is Virgo (6); 12th from Leo is Cancer (4)
        placements = {
            "Venus": 6,   # In Virgo (2nd)
            "Mars": 4,    # In Cancer (12th)
        }
        res = evaluate_argala(target_sign=target_sign, planet_placements=placements)
        pos2 = res["positions"][2]
        assert pos2["has_argala"] is True
        assert pos2["is_obstructed"] is True
        assert pos2["is_active"] is False
        assert pos2["argala_planets"] == ["Venus"]
        assert pos2["virodha_planets"] == ["Mars"]

    def test_primary_argala_pair_11th_vs_3rd(self):
        """11th house Argala obstructed by 3rd house."""
        target_sign = 1  # Aries
        # 11th from Aries is Aquarius (11); 3rd from Aries is Gemini (3)
        placements = {
            "Mercury": 11,  # In Aquarius (11th)
            "Sun": 11,      # Another in 11th (N_A = 2)
            "Mars": 3,      # In Gemini (3rd) (N_V = 1)
        }
        res = evaluate_argala(target_sign=target_sign, planet_placements=placements)
        pos11 = res["positions"][11]
        # N_A = 2 > N_V = 1 -> Active Argala overcomes single obstruction!
        assert pos11["has_argala"] is True
        assert pos11["is_obstructed"] is False
        assert pos11["is_active"] is True
        assert pos11["argala_count"] == 2
        assert pos11["virodha_count"] == 1
        assert 11 in res["active_argalas"]

    def test_secondary_argala_pair_5th_vs_9th(self):
        """5th house secondary Argala obstructed by 9th house."""
        target_sign = 1  # Aries
        # 5th from Aries is Leo (5); 9th from Aries is Sagittarius (9)
        placements = {
            "Jupiter": 5,  # 5th
        }
        res = evaluate_argala(target_sign=target_sign, planet_placements=placements)
        pos5 = res["positions"][5]
        assert pos5["has_argala"] is True
        assert pos5["is_active"] is True
        assert pos5["is_obstructed"] is False
        assert 5 in res["active_argalas"]

    def test_empty_argala_and_virodha_positions(self):
        """When no planets occupy Argala positions, has_argala is False and is_active is False."""
        target_sign = 1  # Aries
        placements = {
            "Sun": 1,   # Occupying target sign itself (1st)
            "Moon": 7,  # Occupying 7th sign
        }
        res = evaluate_argala(target_sign=target_sign, planet_placements=placements)
        for offset in [2, 4, 11, 5]:
            pos = res["positions"][offset]
            assert pos["has_argala"] is False
            assert pos["is_active"] is False
            assert pos["is_obstructed"] is False
        assert res["net_status"] == "NO_ARGALA"
        assert res["active_argalas"] == []
        assert res["obstructed_argalas"] == []

    def test_papa_argala_malefic_nature(self):
        """Malefics (Sun, Mars, Saturn) in Argala without benefics yield PAPA nature."""
        target_sign = 1  # Aries
        placements = {
            "Saturn": 4,  # Cancer (4th)
            "Mars": 4,    # Cancer (4th)
        }
        res = evaluate_argala(target_sign=target_sign, planet_placements=placements)
        pos4 = res["positions"][4]
        assert pos4["argala_nature"] == "PAPA"
        assert pos4["benefic_planets"] == []
        assert sorted(pos4["malefic_planets"]) == ["Mars", "Saturn"]


# ==============================================================================
# Test Class 5: Ketu Reverse Argala Direction (DEC-JAI-08)
# ==============================================================================

class TestKetuArgalaDirection:
    """Verify standard vs reverse Ketu direction behavior under DEC-JAI-08."""

    def test_standard_ketu_argala_direction(self):
        """In STANDARD_ARGALA, Ketu in 4th sign forms 4th house Argala normally."""
        target_sign = 1  # Aries
        # 4th from Aries is Cancer (4)
        placements = {"Ketu": 4}
        res = evaluate_argala(
            target_sign=target_sign,
            planet_placements=placements,
            ketu_mode=KetuArgalaConvention.STANDARD_ARGALA,
        )
        pos4 = res["positions"][4]
        assert pos4["has_argala"] is True
        assert pos4["argala_planets"] == ["Ketu"]
        assert 4 in res["active_argalas"]

    def test_reverse_ketu_argala_direction(self):
        """
        In REVERSE_KETU_ARGALA:
        Argala positions are evaluated in reverse:
        For Argala offset 4: reverse sign is ((1 - 1 - (4 - 1)) % 12) + 1 = 10 (Capricorn).
        If Ketu is in Capricorn (10), it forms reverse 4th Argala on Aries!
        """
        target_sign = 1  # Aries
        placements = {"Ketu": 10}  # Capricorn
        res = evaluate_argala(
            target_sign=target_sign,
            planet_placements=placements,
            ketu_mode=KetuArgalaConvention.REVERSE_KETU_ARGALA,
        )
        pos4 = res["positions"][4]
        assert pos4["has_argala"] is True
        assert pos4["argala_planets"] == ["Ketu"]
        assert 4 in res["active_argalas"]

    def test_reverse_ketu_does_not_fire_on_forward_sign(self):
        """In REVERSE_KETU_ARGALA, Ketu in direct forward 4th sign (Cancer) does NOT form forward 4th Argala."""
        target_sign = 1  # Aries
        placements = {"Ketu": 4}  # Cancer (forward 4th)
        res = evaluate_argala(
            target_sign=target_sign,
            planet_placements=placements,
            ketu_mode=KetuArgalaConvention.REVERSE_KETU_ARGALA,
        )
        pos4 = res["positions"][4]
        # In reverse mode, forward 4th (Cancer) is reverse 10th (Virodha of 4th)!
        # So Ketu acts as Virodha for 4th!
        assert pos4["argala_planets"] == []
        assert pos4["virodha_planets"] == ["Ketu"]


# ==============================================================================
# Test Class 6: All House Argalas & Orchestrator Integration
# ==============================================================================

class TestAllHouseArgalasAndOrchestrator:
    """Verify whole-chart Argala evaluation and JaiminiFoundationResponse integration."""

    def test_evaluate_all_house_argalas_returns_all_12_houses(self):
        """All 12 houses are computed with correct target signs."""
        lagna = 1  # Aries
        placements = {"Jupiter": 4, "Saturn": 10}
        all_houses = evaluate_all_house_argalas(lagna_sign=lagna, planet_placements=placements)
        assert len(all_houses) == 12
        for h in range(1, 13):
            assert h in all_houses
            assert all_houses[h]["target_house"] == h
            assert all_houses[h]["target_sign"] == h

    def test_compute_jaimini_foundation_includes_karakamsa_and_argalas(self, standard_chart_planets):
        """compute_jaimini_foundation returns karakamsa and argalas in response."""
        res = compute_jaimini_foundation(
            planet_positions=standard_chart_planets,
            lagna_sign=1,
        )
        assert res.karakamsa is not None
        assert res.karakamsa.ak_planet == "Jupiter"
        assert res.karakamsa.karakamsa_sign == 9
        assert res.karakamsa.framing_mode == "NAVAMSHA_IN_RASHI"

        assert res.argalas is not None
        assert len(res.argalas) == 12
        assert 1 in res.argalas
        assert res.argalas[1].target_house == 1

        assert res.provenance.formula_version in [
            "WP7C1-JAIMINI-FOUNDATION-v1.0",
            "WP7C2-JAIMINI-FOUNDATION-v1.0",
        ]

    def test_standalone_compute_karakamsa(self, standard_chart_planets):
        """Standalone compute_karakamsa returns validated Pydantic model."""
        res = compute_karakamsa(
            planet_positions=standard_chart_planets,
            lagna_sign=1,
        )
        assert isinstance(res, KarakamsaEvidenceResponse)
        assert res.ak_planet == "Jupiter"

    def test_standalone_compute_argala(self):
        """Standalone compute_argala returns validated Pydantic model."""
        res = compute_argala(
            target_sign=1,
            planet_placements={"Jupiter": 4},
        )
        assert isinstance(res, ArgalaEvidenceResponse)
        assert res.net_status == "ACTIVE_ARGALA"
        assert 4 in res.active_argalas


# ==============================================================================
# Test Class 7: Deterministic Output & Provenance Tracking
# ==============================================================================

class TestProvenanceAndDeterminism:
    """Verify deterministic repeatability, provenance tracking, and JSON serialization."""

    def test_json_serialization_round_trip(self, standard_chart_planets):
        """Verify full round-trip JSON serialization without data loss."""
        response = compute_jaimini_foundation(
            planet_positions=standard_chart_planets,
            lagna_sign=1,
        )
        raw_json = response.model_dump_json()
        parsed = json.loads(raw_json)

        assert "karakamsa" in parsed
        assert parsed["karakamsa"]["ak_planet"] == "Jupiter"
        assert "argalas" in parsed
        assert len(parsed["argalas"]) == 12
        assert parsed["provenance"]["formula_version"] in [
            "WP7C1-JAIMINI-FOUNDATION-v1.0",
            "WP7C2-JAIMINI-FOUNDATION-v1.0",
        ]

        # Check DEC-JAI-07 and DEC-JAI-08 in decisions
        dec_map = {d["decision_id"]: d for d in parsed["provenance"]["decisions"]}
        assert "DEC-JAI-07" in dec_map
        assert dec_map["DEC-JAI-07"]["approval_status"] == ApprovalStatus.PENDING_HUMAN_JYOTISHI.value
        assert dec_map["DEC-JAI-07"]["is_approved"] is False

        assert "DEC-JAI-08" in dec_map
        assert dec_map["DEC-JAI-08"]["approval_status"] == ApprovalStatus.PENDING_HUMAN_JYOTISHI.value
        assert dec_map["DEC-JAI-08"]["is_approved"] is False

    def test_deterministic_repeatability(self, standard_chart_planets):
        """Two identical calls produce bit-for-bit identical JSON dumps."""
        run1 = compute_jaimini_foundation(planet_positions=standard_chart_planets, lagna_sign=1)
        run2 = compute_jaimini_foundation(planet_positions=standard_chart_planets, lagna_sign=1)
        assert run1.model_dump_json() == run2.model_dump_json()


# ==============================================================================
# Test Class 8: Regression Isolation (WP1–WP6, WP7A, WP7B)
# ==============================================================================

class TestRegressionIsolation:
    """Ensure existing WP1-WP6, WP7A, and WP7B modules remain functional."""

    def test_wp1_shadbala_intact(self):
        from shared.veda import shadbala
        assert callable(shadbala)

    def test_wp2_lordship_intact(self):
        from shared.veda import build_lagna_matrix
        m = build_lagna_matrix("Mesha")
        assert m.lagna == "Mesha"
        assert m.house_lords[1] == "Mars"

    def test_wp6_transit_vedha_intact(self):
        from shared.veda import check_transit_vedha
        assert callable(check_transit_vedha)

    def test_wp7a_arudha_truth_table_intact(self):
        from shared.veda.jaimini_rules import calculate_arudha_pada
        res = calculate_arudha_pada(house_num=1, lagna_sign=1, lord_sign=1)
        # Svastha exception: lord in 1st -> A1 is in 10th
        assert res["final_pada"] == 10
        assert res["exception_applied"] is True

    def test_wp7b_chara_dasha_intact(self):
        from shared.veda.jaimini_dasha import calculate_mahadasha_duration
        # Sun in Aries (1), lord Mars in Leo (5): forward count = 5, duration = 4 years
        dur = calculate_mahadasha_duration(
            sign=1,
            lord_sign=5,
            lord_planet="Mars",
        )
        assert dur["final_years"] == 4

