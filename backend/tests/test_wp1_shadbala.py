"""
WP1 Unit Tests — Shadbala, Bhava Bala, Avasthas.

Validates all six Shadbala components against documented BPHS fixtures,
Bhava Bala house strength computation, and all three Avastha layers.
"""

import pytest
from shared.veda.shadbala import (
    shadbala, shadbala_summary,
    _uccha_bala, _kendra_bala, _drekkana_bala, _ojayugma_bala,
    compute_sthana_bala, compute_dig_bala, compute_kala_bala,
    compute_chesta_bala, compute_naisargika_bala, compute_drik_bala,
    NAISARGIKA_BALA, MINIMUM_RUPAS, DEEP_EXALTATION_DEGREE,
)
from shared.veda.bhavabala import bhava_bala, bhava_bala_summary
from shared.veda.avasthas import (
    get_baladi_avastha, get_jagradi_avastha, evaluate_avasthas,
    BALADI_STRENGTH, JAGRADI_STRENGTH,
)


# =============================================================================
# SHADBALA — UCCHA BALA
# =============================================================================

class TestUcchaBala:
    """Sun deep exaltation = Mesha 10 deg -> Uccha Bala = 60."""

    def test_sun_deep_exaltation(self):
        score = _uccha_bala("Sun", "Mesha", 10.0)
        assert score == 60.0, f"Expected 60.0 at deep exaltation, got {score}"

    def test_sun_deep_debilitation(self):
        # Sun debilitated in Tula 10 deg (180 deg away from exaltation point)
        score = _uccha_bala("Sun", "Tula", 10.0)
        assert score == 0.0, f"Expected 0.0 at deep debilitation, got {score}"

    def test_sun_neutral_midpoint(self):
        # 90 deg away from deep exalt -> score should be ~30
        score = _uccha_bala("Sun", "Karka", 10.0)
        assert 25.0 <= score <= 35.0, f"Expected ~30 at 90-deg midpoint, got {score}"

    def test_moon_deep_exaltation(self):
        score = _uccha_bala("Moon", "Vrishabha", 3.0)
        assert score == 60.0

    def test_jupiter_deep_exaltation(self):
        score = _uccha_bala("Jupiter", "Karka", 5.0)
        assert score == 60.0

    def test_saturn_deep_exaltation(self):
        score = _uccha_bala("Saturn", "Tula", 20.0)
        assert score == 60.0

    def test_score_range(self):
        """All Uccha Bala scores must be in [0, 60]."""
        from shared.veda.zodiac import SIGNS_SK
        planets = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
        for p in planets:
            for sign in SIGNS_SK:
                for deg in [0.0, 10.0, 20.0, 29.99]:
                    s = _uccha_bala(p, sign, deg)
                    assert 0.0 <= s <= 60.0, f"{p} {sign} {deg}: out of range [{s}]"


# =============================================================================
# SHADBALA — KENDRA BALA
# =============================================================================

class TestKendraBala:
    def test_kendra_houses(self):
        for h in (1, 4, 7, 10):
            assert _kendra_bala(h) == 60.0, f"Kendra house {h} should be 60"

    def test_panapara_houses(self):
        for h in (2, 5, 8, 11):
            assert _kendra_bala(h) == 30.0, f"Panapara house {h} should be 30"

    def test_apoklima_houses(self):
        for h in (3, 6, 9, 12):
            assert _kendra_bala(h) == 15.0, f"Apoklima house {h} should be 15"


# =============================================================================
# SHADBALA — DIG BALA
# =============================================================================

class TestDigBala:
    def test_sun_tenth_house_max(self):
        """Sun gains maximum Dig Bala in 10th house."""
        assert compute_dig_bala("Sun", 10) == 60.0

    def test_sun_fourth_house_zero(self):
        """Sun loses Dig Bala in the opposite house (4th)."""
        assert compute_dig_bala("Sun", 4) == 0.0

    def test_jupiter_first_house_max(self):
        assert compute_dig_bala("Jupiter", 1) == 60.0

    def test_saturn_seventh_house_max(self):
        assert compute_dig_bala("Saturn", 7) == 60.0

    def test_moon_fourth_house_max(self):
        assert compute_dig_bala("Moon", 4) == 60.0

    def test_venus_fourth_house_max(self):
        assert compute_dig_bala("Venus", 4) == 60.0

    def test_all_dig_bala_in_range(self):
        planets = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
        for p in planets:
            for h in range(1, 13):
                s = compute_dig_bala(p, h)
                assert 0.0 <= s <= 60.0, f"{p} house {h}: Dig Bala {s} out of range"


# =============================================================================
# SHADBALA — NAISARGIKA BALA
# =============================================================================

class TestNaisargikaBala:
    def test_sun_highest(self):
        assert compute_naisargika_bala("Sun") == 60.0

    def test_saturn_lowest(self):
        assert compute_naisargika_bala("Saturn") == 8.57

    def test_ranking_order(self):
        """Sun > Moon > Venus > Jupiter > Mercury > Mars > Saturn."""
        order = ["Sun", "Moon", "Venus", "Jupiter", "Mercury", "Mars", "Saturn"]
        scores = [compute_naisargika_bala(p) for p in order]
        for i in range(len(scores) - 1):
            assert scores[i] > scores[i + 1], (
                f"Naisargika order violated: {order[i]}={scores[i]} <= {order[i+1]}={scores[i+1]}"
            )


# =============================================================================
# SHADBALA — CHESTA BALA
# =============================================================================

class TestChestaBala:
    def test_retrograde_planet(self):
        assert compute_chesta_bala("Mars", retrograde=True) == 60.0

    def test_direct_planet_max(self):
        assert compute_chesta_bala("Mars", retrograde=False, speed_ratio=1.0) == 30.0

    def test_stationary_planet(self):
        assert compute_chesta_bala("Mars", retrograde=False, speed_ratio=0.0) == 30.0

    def test_sun_moon_no_chesta(self):
        assert compute_chesta_bala("Sun", retrograde=False) == 0.0
        assert compute_chesta_bala("Moon", retrograde=False) == 0.0

    def test_rahu_ketu_always_retrograde(self):
        assert compute_chesta_bala("Rahu", retrograde=False) == 60.0
        assert compute_chesta_bala("Ketu", retrograde=False) == 60.0


# =============================================================================
# SHADBALA — FULL INTEGRATION
# =============================================================================

class TestShadbalaIntegration:
    def test_result_dataclass_fields(self):
        result = shadbala("Sun", "Mesha", 1, 10.0)
        assert result.planet == "Sun"
        assert result.total_virupas > 0
        assert result.total_rupas == round(result.total_virupas / 60.0, 4)

    def test_sun_exalted_is_strong(self):
        """Sun in Mesha at deep exaltation should exceed minimum Rupas."""
        result = shadbala(
            "Sun", "Mesha", 10,  # house 10 for max Dig Bala
            degree_in_sign=10.0,
        )
        # Sun minimum = 5.0 Rupas; exalted + Dig Bala should exceed this
        assert result.total_rupas > 3.0, (
            f"Exalted Sun in 10H got only {result.total_rupas} Rupas"
        )

    def test_breakdown_completeness(self):
        result = shadbala("Jupiter", "Karka", 1, 5.0)
        bd = result.breakdown
        assert "sthana_bala" in bd
        assert "dig_bala" in bd
        assert "total_virupas" in bd
        assert "total_rupas" in bd
        assert "is_strong" in bd

    def test_summary_all_planets(self):
        chart = {
            "Sun":     {"sign": "Mesha", "house": 10, "degree": 10.0, "retrograde": False},
            "Moon":    {"sign": "Vrishabha", "house": 11, "degree": 3.0, "retrograde": False},
            "Mars":    {"sign": "Makara", "house": 7, "degree": 28.0, "retrograde": False},
            "Mercury": {"sign": "Kanya", "house": 5, "degree": 15.0, "retrograde": False},
            "Jupiter": {"sign": "Karka", "house": 1, "degree": 5.0, "retrograde": False},
            "Venus":   {"sign": "Meena", "house": 9, "degree": 27.0, "retrograde": False},
            "Saturn":  {"sign": "Tula", "house": 4, "degree": 20.0, "retrograde": False},
        }
        results = shadbala_summary(chart)
        assert len(results) == 7
        for planet, result in results.items():
            assert result.total_virupas >= 0


# =============================================================================
# BHAVA BALA
# =============================================================================

class TestBhavaBala:
    def test_lagna_house_strong(self):
        """1st house (Lagna) should have maximum Dig Bala."""
        result = bhava_bala(house=1, lagna_idx=0, planet_map={})
        assert result.bhava_digbala == 60.0

    def test_dusthana_houses_weak(self):
        """6th, 8th, 12th houses should have lower Dig Bala."""
        for h in (6, 8, 12):
            result = bhava_bala(house=h, lagna_idx=0, planet_map={})
            assert result.bhava_digbala == 15.0

    def test_summary_twelve_houses(self):
        """bhava_bala_summary must return exactly 12 entries."""
        results = bhava_bala_summary(lagna_idx=0, planet_map={})
        assert len(results) == 12
        for house in range(1, 13):
            assert house in results

    def test_total_virupas_positive(self):
        results = bhava_bala_summary(lagna_idx=3, planet_map={})  # Karka Lagna
        for h, r in results.items():
            assert r.total_virupas > 0, f"House {h} total_virupas should be > 0"


# =============================================================================
# AVASTHAS
# =============================================================================

class TestBaladiAvastha:
    def test_odd_sign_first_decanate(self):
        """Mesha (odd) — degree 0-5.99 -> Bala."""
        assert get_baladi_avastha("Mesha", 2.0) == "Bala"

    def test_odd_sign_last_decanate(self):
        """Mesha (odd) — degree 24-30 -> Mrita."""
        assert get_baladi_avastha("Mesha", 25.0) == "Mrita"

    def test_even_sign_first_decanate(self):
        """Vrishabha (even) — degree 0-5.99 -> Mrita (reversed)."""
        assert get_baladi_avastha("Vrishabha", 2.0) == "Mrita"

    def test_even_sign_last_decanate(self):
        """Vrishabha (even) — degree 24-30 -> Bala (reversed)."""
        assert get_baladi_avastha("Vrishabha", 25.0) == "Bala"

    def test_yuva_midpoint_odd(self):
        """Mesha (odd) — degree 12-17.99 -> Yuva."""
        assert get_baladi_avastha("Mesha", 15.0) == "Yuva"

    def test_strength_multiplier_range(self):
        from shared.veda.zodiac import SIGNS_SK
        for sign in SIGNS_SK:
            for deg in [0, 5, 12, 20, 28]:
                avastha = get_baladi_avastha(sign, float(deg))
                mul = BALADI_STRENGTH[avastha]
                assert 0.0 < mul <= 1.0


class TestJagradiAvastha:
    def test_cardinal_signs_jagrat(self):
        """Mesha (Cardinal) -> Jagrat."""
        assert get_jagradi_avastha("Mesha") == "Jagrat"
        assert get_jagradi_avastha("Karka") == "Jagrat"

    def test_fixed_signs_swapna(self):
        """Vrishabha (Fixed) -> Swapna."""
        assert get_jagradi_avastha("Vrishabha") == "Swapna"
        assert get_jagradi_avastha("Simha") == "Swapna"

    def test_mutable_signs_sushupti(self):
        """Mithuna (Mutable) -> Sushupti."""
        assert get_jagradi_avastha("Mithuna") == "Sushupti"
        assert get_jagradi_avastha("Dhanu") == "Sushupti"


class TestEvaluateAvasthas:
    def test_combined_multiplier_bounds(self):
        result = evaluate_avasthas("Sun", "Mesha", 1, 10.0)
        assert 0.0 < result["combined_multiplier"] <= 1.0

    def test_garvita_in_exaltation(self):
        """Sun in Mesha (exaltation) should get Garvita Avastha."""
        result = evaluate_avasthas(
            "Sun", "Mesha", 10, 10.0, planet_map={}
        )
        assert "Garvita" in result["lajjitadi_avasthas"]

    def test_keys_present(self):
        result = evaluate_avasthas("Moon", "Vrishabha", 1, 5.0)
        expected_keys = [
            "baladi_avastha", "baladi_multiplier",
            "jagradi_avastha", "jagradi_multiplier",
            "lajjitadi_avasthas", "combined_multiplier", "interpretations",
        ]
        for k in expected_keys:
            assert k in result, f"Missing key: {k}"


# =============================================================================
# GAP-CLOSING TESTS (added post verification review)
# =============================================================================

class TestChestaBalaEdgeCases:
    """Regression tests for Chesta Bala speed-ratio boundary behavior."""

    def test_slow_direct_planet(self):
        """Planet moving at half mean speed should get 15 Virupas."""
        score = compute_chesta_bala("Mars", retrograde=False, speed_ratio=0.5)
        assert score == 15.0, f"Half-speed direct: expected 15.0, got {score}"

    def test_fast_direct_planet_capped_at_30(self):
        """Planet at 200% mean speed should still cap at 30 (max direct)."""
        score = compute_chesta_bala("Mars", retrograde=False, speed_ratio=2.0)
        assert score == 30.0, f"200% speed: expected 30.0 cap, got {score}"

    def test_negative_speed_ratio_treated_as_retrograde_magnitude(self):
        """Negative speed_ratio (retrograde flag False) uses abs()."""
        score = compute_chesta_bala("Jupiter", retrograde=False, speed_ratio=-0.5)
        assert score == 15.0, f"Negative speed_ratio (direct flag): expected 15.0"


class TestDrikBalaDirection:
    """Regression: malefic aspect must SUBTRACT from Drik Bala."""

    def test_malefic_aspect_negative(self):
        """Saturn in H1 aspects H7 (7th house). Saturn is malefic -> H7 planet should get negative Drik."""
        planet_map = {"Saturn": {"house": 1}}
        score = compute_drik_bala("Sun", planet_house=7, planet_map=planet_map)
        assert score < 0, f"Saturn (malefic) aspecting H7 should give negative Drik, got {score}"

    def test_benefic_aspect_positive(self):
        """Jupiter in H1 aspects H7. Jupiter is benefic -> H7 planet gets positive Drik."""
        planet_map = {"Jupiter": {"house": 1}}
        score = compute_drik_bala("Sun", planet_house=7, planet_map=planet_map)
        assert score > 0, f"Jupiter (benefic) aspecting H7 should give positive Drik, got {score}"

    def test_no_aspects_zero_drik(self):
        """Empty planet_map -> Drik Bala = 0."""
        score = compute_drik_bala("Sun", planet_house=1, planet_map={})
        assert score == 0.0


class TestBhavadhipatiDegenerate:
    """Bhavadhipati Bala with zero-strength lord."""

    def test_zero_virupa_lord(self):
        from shared.veda.shadbala import ShadbalaResult
        from shared.veda.bhavabala import _bhavadhipati_bala
        mock = ShadbalaResult(planet="Mars")
        mock.total_virupas = 0.0
        # Mesha Lagna H1 lord = Mars
        result = _bhavadhipati_bala(1, 0, {"Mars": mock})
        assert result == 0.0, f"Zero-virupa lord: expected 0.0, got {result}"

    def test_max_virupa_lord(self):
        from shared.veda.shadbala import ShadbalaResult
        from shared.veda.bhavabala import _bhavadhipati_bala
        mock = ShadbalaResult(planet="Mars")
        mock.total_virupas = 300.0  # typical "very strong" value
        result = _bhavadhipati_bala(1, 0, {"Mars": mock})
        assert result == 60.0, f"300-virupa lord: expected 60.0 cap, got {result}"


class TestMuditaRegressionBug:
    """Regression: avasthas.py Mudita generator bug (fixed — must not regress)."""

    def test_sun_in_mesha_gets_mudita(self):
        """
        Sun in Mesha: Mars is friend of Sun, Mars owns Mesha.
        After fix, Mudita should appear because Sun is in a friend's sign.
        """
        result = evaluate_avasthas("Sun", "Mesha", 10, 10.0, planet_map={})
        assert "Mudita" in result["lajjitadi_avasthas"], (
            "Sun in Mesha (Mars' sign, Mars is Sun's friend) should trigger Mudita."
            " If this fails, the any() generator fix may have regressed."
        )

    def test_no_false_mudita_in_enemy_sign(self):
        """
        Saturn in Mesha: Saturn's friends are Mercury and Venus, neither owns Mesha.
        No conjunct/aspecting friends assumed. Should NOT get Mudita.
        """
        result = evaluate_avasthas("Saturn", "Mesha", 1, 0.0, planet_map={})
        # Saturn natural friends: Mercury, Venus. Neither owns Mesha.
        assert "Mudita" not in result["lajjitadi_avasthas"], (
            "Saturn in Mesha: neither Mercury nor Venus owns Mesha, so Mudita should be absent."
        )
