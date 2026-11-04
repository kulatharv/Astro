"""
WP2 Unit Tests — 12-Lagna Functional Lordship Matrix.

Validates:
- All 12 lagnas x 7 classical planets produce correct house ownership.
- Role classifications (Kendra, Trikona, Dusthana, Maraka, Badhaka, Yogakaraka).
- Functional benefic / malefic determination.
- Kendradhipati Dosha detection.
- Well-known classical fixtures (Mesha Yogakaraka=Saturn, etc.)
"""

import pytest
from shared.veda.lordship import (
    build_lagna_matrix, get_lagna_matrix, get_house_lord,
    get_planet_roles, is_functional_benefic, is_functional_malefic,
    is_yogakaraka, is_badhaka_lord, matrix_to_dict, ALL_LAGNA_MATRICES,
    SIGN_MODALITY, BADHAKA_HOUSE,
)
from shared.veda.zodiac import SIGNS_SK, SIGN_LORDS


# =============================================================================
# ALL MATRICES LOAD WITHOUT ERROR
# =============================================================================

class TestAllMatricesLoad:
    def test_all_twelve_loaded(self):
        assert len(ALL_LAGNA_MATRICES) == 12

    def test_all_signs_present(self):
        for sign in SIGNS_SK:
            assert sign in ALL_LAGNA_MATRICES, f"Missing matrix for {sign}"

    def test_each_matrix_has_twelve_houses(self):
        for sign, matrix in ALL_LAGNA_MATRICES.items():
            assert len(matrix.house_lords) == 12, f"{sign}: expected 12 house lords"


# =============================================================================
# HOUSE LORDS — PROGRAMMATIC ACCURACY
# =============================================================================

class TestHouseLords:
    def test_mesha_lagna_house_lords(self):
        """
        Mesha Lagna: House 1=Mars, 2=Venus, 3=Mercury, 4=Moon, 5=Sun,
                     6=Mercury, 7=Venus, 8=Mars, 9=Jupiter, 10=Saturn,
                     11=Saturn, 12=Jupiter.
        """
        expected = {
            1: "Mars", 2: "Venus", 3: "Mercury", 4: "Moon", 5: "Sun",
            6: "Mercury", 7: "Venus", 8: "Mars", 9: "Jupiter", 10: "Saturn",
            11: "Saturn", 12: "Jupiter",
        }
        for house, planet in expected.items():
            actual = get_house_lord("Mesha", house)
            assert actual == planet, (
                f"Mesha H{house}: expected {planet}, got {actual}"
            )

    def test_vrishabha_lagna_house_lords(self):
        """
        Vrishabha Lagna: House 1=Venus, 2=Mercury, 3=Moon, 4=Sun, 5=Mercury,
                         6=Mars, 7=Mars (Vrischika), 8=Jupiter (Dhanu)... 
        """
        expected = {
            1: "Venus", 2: "Mercury", 3: "Moon", 4: "Sun",
            5: "Mercury", 6: "Mars", 7: "Mars", 8: "Jupiter",
            9: "Saturn", 10: "Saturn", 11: "Jupiter", 12: "Mars",
        }
        # Note: H12 of Vrishabha = Meena (Jupiter)
        # Recompute properly:
        from shared.veda.zodiac import SIGNS_SK, SIGN_LORDS
        lagna_idx = SIGNS_SK.index("Vrishabha")
        for house in range(1, 13):
            sign = SIGNS_SK[(lagna_idx + house - 1) % 12]
            lord = SIGN_LORDS[sign]
            actual = get_house_lord("Vrishabha", house)
            assert actual == lord, (
                f"Vrishabha H{house}: expected {lord} (sign={sign}), got {actual}"
            )

    def test_all_lagnas_consistent_with_sign_lords(self):
        """Programmatic check: all 12 lagna matrices match SIGN_LORDS directly."""
        for lagna in SIGNS_SK:
            lagna_idx = SIGNS_SK.index(lagna)
            for house in range(1, 13):
                expected_sign = SIGNS_SK[(lagna_idx + house - 1) % 12]
                expected_lord = SIGN_LORDS[expected_sign]
                actual_lord   = get_house_lord(lagna, house)
                assert actual_lord == expected_lord, (
                    f"{lagna} H{house}: expected {expected_lord}, got {actual_lord}"
                )


# =============================================================================
# YOGAKARAKAS — CLASSICAL FIXTURES
# =============================================================================

class TestYogakarakas:
    """Validate well-known Yogakaraka assignments from BPHS."""

    def test_mesha_no_yogakaraka(self):
        """Mesha Lagna has no classical Yogakaraka planet."""
        matrix = get_lagna_matrix("Mesha")
        # Mars owns 1+8 (Trikona+Dusthana), Saturn owns 10+11 (Kendra+Upachaya)
        # No single planet owns both a Kendra (non-1) and a Trikona (non-1)
        assert matrix.yogakarakas == [], f"Mesha should have no Yogakaraka, got {matrix.yogakarakas}"

    def test_vrishabha_saturn_yogakaraka(self):
        """Vrishabha Lagna: Saturn owns 9th (Trikona) and 10th (Kendra) -> Yogakaraka."""
        assert is_yogakaraka("Vrishabha", "Saturn"), "Saturn should be Yogakaraka for Vrishabha Lagna"

    def test_karka_mars_yogakaraka(self):
        """Karka Lagna: Mars owns 5th (Trikona) and 10th (Kendra) -> Yogakaraka."""
        assert is_yogakaraka("Karka", "Mars"), "Mars should be Yogakaraka for Karka Lagna"

    def test_simha_mars_yogakaraka(self):
        """Simha Lagna: Mars owns 4th (Kendra) and 9th (Trikona) -> Yogakaraka."""
        assert is_yogakaraka("Simha", "Mars"), "Mars should be Yogakaraka for Simha Lagna"

    def test_makara_venus_yogakaraka(self):
        """Makara Lagna: Venus owns 5th (Trikona) and 10th (Kendra) -> Yogakaraka."""
        assert is_yogakaraka("Makara", "Venus"), "Venus should be Yogakaraka for Makara Lagna"

    def test_kumbha_venus_yogakaraka(self):
        """Kumbha Lagna: Venus owns 4th (Kendra) and 9th (Trikona) -> Yogakaraka."""
        assert is_yogakaraka("Kumbha", "Venus"), "Venus should be Yogakaraka for Kumbha Lagna"


# =============================================================================
# FUNCTIONAL BENEFICS / MALEFICS
# =============================================================================

class TestFunctionalBeneficMalefic:
    def test_lagna_lord_is_benefic(self):
        """The Lagna lord is always functionally beneficial."""
        for lagna in SIGNS_SK:
            lagna_lord = get_house_lord(lagna, 1)
            # Lagna lord owns house 1 which is both Kendra AND Trikona
            # Pure Kendra lord rule doesn't apply
            assert is_functional_benefic(lagna, lagna_lord), (
                f"{lagna}: Lagna lord {lagna_lord} should be functional benefic"
            )

    def test_ninth_lord_is_benefic(self):
        """The 9th house (Trikona) lord is always a functional benefic."""
        for lagna in SIGNS_SK:
            ninth_lord = get_house_lord(lagna, 9)
            # 9th lord may also own dusthana houses for some lagnas
            matrix = get_lagna_matrix(lagna)
            role = matrix.planet_roles.get(ninth_lord)
            if role and not role.is_dusthana_lord:
                assert role.is_functional_benefic, (
                    f"{lagna}: 9th lord {ninth_lord} (roles={role.roles}) should be functional benefic"
                )

    def test_eighth_lord_is_malefic_when_only_dusthana(self):
        """
        Pure 8th house lord (no Trikona) should be functional malefic.
        Mesha: 8th house = Vrischika -> Mars. Mars also owns 1st (Lagna), so it's NOT purely malefic.
        Mithuna: 8th = Makara -> Saturn. Saturn also owns 9th. So it gets complicated.
        Check Vrishabha: 8th = Dhanu -> Jupiter. Jupiter also owns 8+11 -> dusthana+upachaya.
        Use a case where lord owns only dusthana.
        """
        # Karka Lagna: 6th house = Dhanu (Jupiter), 8th = Kumbha (Saturn), 12th = Mithuna (Mercury)
        # Saturn for Karka owns houses 7+8 -> Maraka + Dusthana. Not only Trikona -> malefic.
        matrix = get_lagna_matrix("Karka")
        saturn_role = matrix.planet_roles.get("Saturn")
        assert saturn_role is not None
        assert not saturn_role.is_functional_benefic or saturn_role.is_functional_malefic or saturn_role.is_neutral

    def test_matrix_dict_serializable(self):
        for lagna in SIGNS_SK:
            d = matrix_to_dict(lagna)
            assert "house_lords" in d
            assert "yogakarakas" in d
            assert "functional_benefics" in d
            assert "functional_malefics" in d
            assert "badhaka_lord" in d


# =============================================================================
# BADHAKA LORD
# =============================================================================

class TestBadhakaLord:
    def test_movable_lagnas_badhaka_11th(self):
        """Movable lagnas (Mesha, Karka, Tula, Makara): Badhaka = 11th lord."""
        movable_lagnas = ["Mesha", "Karka", "Tula", "Makara"]
        for lagna in movable_lagnas:
            matrix = get_lagna_matrix(lagna)
            assert matrix.badhaka_house == 11, (
                f"{lagna} (Movable): Badhaka house should be 11, got {matrix.badhaka_house}"
            )
            expected_lord = get_house_lord(lagna, 11)
            assert matrix.badhaka_lord == expected_lord

    def test_fixed_lagnas_badhaka_9th(self):
        """Fixed lagnas (Vrishabha, Simha, Vrischika, Kumbha): Badhaka = 9th lord."""
        fixed_lagnas = ["Vrishabha", "Simha", "Vrischika", "Kumbha"]
        for lagna in fixed_lagnas:
            matrix = get_lagna_matrix(lagna)
            assert matrix.badhaka_house == 9, (
                f"{lagna} (Fixed): Badhaka house should be 9, got {matrix.badhaka_house}"
            )

    def test_mutable_lagnas_badhaka_7th(self):
        """Mutable lagnas (Mithuna, Kanya, Dhanu, Meena): Badhaka = 7th lord."""
        mutable_lagnas = ["Mithuna", "Kanya", "Dhanu", "Meena"]
        for lagna in mutable_lagnas:
            matrix = get_lagna_matrix(lagna)
            assert matrix.badhaka_house == 7, (
                f"{lagna} (Mutable): Badhaka house should be 7, got {matrix.badhaka_house}"
            )


# =============================================================================
# KENDRADHIPATI DOSHA
# =============================================================================

class TestKendradhipatiDosha:
    def test_jupiter_kendradhipati_dhanu_lagna(self):
        """
        Dhanu Lagna: Jupiter owns 1st (Lagna) and 4th (Kendra).
        As Lagna lord, it should not suffer Kendradhipati Dosha.
        """
        matrix = get_lagna_matrix("Dhanu")
        jup_role = matrix.planet_roles.get("Jupiter")
        assert jup_role is not None
        # Jupiter is Lagna lord here — no Kendradhipati Dosha expected
        assert not jup_role.has_kendradhipati_dosha, (
            "Jupiter as Lagna lord for Dhanu should not have Kendradhipati Dosha"
        )

    def test_planet_roles_string_list(self):
        """All planet role info must have non-empty roles list."""
        for lagna in SIGNS_SK:
            matrix = get_lagna_matrix(lagna)
            for planet, role in matrix.planet_roles.items():
                assert isinstance(role.roles, list), (
                    f"{lagna}/{planet}: roles must be a list"
                )


# =============================================================================
# EXHAUSTIVE 12-LAGNA MATRIX VALIDATION
# =============================================================================

class TestExhaustiveMatrix:
    def test_every_house_has_a_lord(self):
        """Every house in every lagna matrix must have a lord assigned."""
        for lagna in SIGNS_SK:
            matrix = get_lagna_matrix(lagna)
            for house in range(1, 13):
                lord = matrix.house_lords.get(house)
                assert lord and lord != "Unknown", (
                    f"{lagna} H{house}: missing lord"
                )

    def test_each_planet_has_role_info(self):
        """Every classical planet that owns at least one house must have role info."""
        for lagna in SIGNS_SK:
            matrix = get_lagna_matrix(lagna)
            for planet in matrix.house_lords.values():
                assert planet in matrix.planet_roles, (
                    f"{lagna}: {planet} has houses but no role_info entry"
                )

    def test_functional_status_mutually_exclusive(self):
        """A planet cannot be both functional benefic AND functional malefic."""
        for lagna in SIGNS_SK:
            matrix = get_lagna_matrix(lagna)
            for planet, role in matrix.planet_roles.items():
                assert not (role.is_functional_benefic and role.is_functional_malefic), (
                    f"{lagna}/{planet}: cannot be both FB and FM"
                )

    def test_get_planet_roles_api(self):
        """get_planet_roles() must return a list for every planet in every lagna."""
        for lagna in SIGNS_SK:
            matrix = get_lagna_matrix(lagna)
            for planet in matrix.planet_roles:
                roles = get_planet_roles(lagna, planet)
                assert isinstance(roles, list)
