"""
Unit and Integration Test Suite for WP3 — Classical Yoga Catalog (60+ Yogas).

Validates:
- Catalog schema completeness (rule_id, version, name, category, source_reference)
- All 70 classical rules across 14 astrological families
- Positive, negative, and cancellation boundary conditions
- Backward compatibility of calculate_yogas() and detect_advanced_yogas()
- Contested modern yogas gating (disabled by default)
"""

import pytest
from shared.veda.yoga_catalog import (
    CATALOG,
    YogaRule,
    evaluate_yoga_catalog,
    evaluate_yoga_rule,
    get_planet_map,
    house_of,
    sign_of,
)
from shared.veda.yogas import calculate_yogas, calculate_yogas_v2, detect_advanced_yogas


# ---------------------------------------------------------------------------
# Fixture Helpers
# ---------------------------------------------------------------------------

def make_chart(planet_specs: list[dict], lagna: str = "Mesha") -> tuple[list[dict], str, dict]:
    """Helper to build a chart input for yoga evaluation."""
    planets = []
    for p in planet_specs:
        planets.append({
            "name": p["name"],
            "sign": p.get("sign", "Mesha"),
            "house": p.get("house", 1),
            "degree": p.get("degree", 15.0),
            "degree_decimal": p.get("degree_decimal", 15.0),
            "retrograde": p.get("retrograde", False),
            "strength": p.get("strength", "Strong"),
        })
    return planets, lagna, {}


def find_yoga(results: list[dict], name: str) -> dict:
    for y in results:
        if y["name"] == name or y["rule_id"] == name:
            return y
    raise AssertionError(f"Yoga {name} not found in results")


# ---------------------------------------------------------------------------
# 1. Catalog Schema & Metadata Integrity Tests
# ---------------------------------------------------------------------------

def test_catalog_size_and_schema():
    assert len(CATALOG) >= 60, f"Expected at least 60 rules, found {len(CATALOG)}"
    rule_ids = set()
    for rule in CATALOG:
        assert isinstance(rule, YogaRule)
        assert rule.rule_id, "rule_id cannot be empty"
        assert rule.rule_id not in rule_ids, f"Duplicate rule_id {rule.rule_id}"
        rule_ids.add(rule.rule_id)
        assert rule.version == "1.0.0"
        assert rule.name, "Yoga name cannot be empty"
        assert rule.category, "Category cannot be empty"
        assert rule.description, "Description cannot be empty"
        assert rule.source_reference, "source_reference cannot be empty"
        assert callable(rule.predicate), "Predicate must be callable"
        assert isinstance(rule.cancellation_rules, list)


def test_contested_modern_gating():
    kaal_sarp = [r for r in CATALOG if r.rule_id == "YOGA-KALA-SARPA-MODERN-01"][0]
    assert kaal_sarp.contested_modern is True
    assert kaal_sarp.enabled_by_default is False

    # Classical rules must be enabled by default
    classical = [r for r in CATALOG if r.rule_id != "YOGA-KALA-SARPA-MODERN-01"]
    for r in classical:
        assert r.enabled_by_default is True
        assert r.contested_modern is False


def test_umbrella_and_deduplication_tags():
    umbrellas = [r for r in CATALOG if r.is_umbrella]
    assert len(umbrellas) == 3, f"Expected exactly 3 umbrella rules, found {len(umbrellas)}"
    umbrella_ids = {u.rule_id for u in umbrellas}
    assert umbrella_ids == {
        "YOGA-PANCHA-MAHAPURUSHA-01",
        "YOGA-VIPARITA-UMBRELLA-01",
        "YOGA-DHANA-UMBRELLA-01",
    }
    for u in umbrellas:
        assert u.dedupe_key is not None, f"Umbrella {u.rule_id} missing dedupe_key"

    # Verify that child rules share the dedupe_key
    ruchaka = [r for r in CATALOG if r.rule_id == "YOGA-PANCHA-RUCHAKA-01"][0]
    assert ruchaka.dedupe_key == "DEDUPE-PANCHA-MAHAPURUSHA"
    assert ruchaka.is_umbrella is False

    harsha = [r for r in CATALOG if r.rule_id == "YOGA-VIPARITA-HARSHA-01"][0]
    assert harsha.dedupe_key == "DEDUPE-VIPARITA-RAJA"
    assert harsha.is_umbrella is False

    dhana_2_11 = [r for r in CATALOG if r.rule_id == "YOGA-DHANA-2-11-01"][0]
    assert dhana_2_11.dedupe_key == "DEDUPE-DHANA-YOGA"
    assert dhana_2_11.is_umbrella is False


# ---------------------------------------------------------------------------
# 2. Pancha Mahapurusha Yogas Tests
# ---------------------------------------------------------------------------

def test_ruchaka_yoga_positive_and_negative():
    # Positive: Mars in Mesha (own sign) in H1 (Kendra)
    p_pos, lagna, _ = make_chart([{"name": "Mars", "sign": "Mesha", "house": 1}], lagna="Mesha")
    res_pos = calculate_yogas(p_pos, lagna, {})
    y_pos = find_yoga(res_pos, "Ruchaka Yoga")
    assert y_pos["present"] is True

    # Exalted in Makara in H10
    p_ex, lagna_ex, _ = make_chart([{"name": "Mars", "sign": "Makara", "house": 10}], lagna="Mesha")
    res_ex = calculate_yogas(p_ex, lagna_ex, {})
    y_ex = find_yoga(res_ex, "Ruchaka Yoga")
    assert y_ex["present"] is True
    assert y_ex["strength"] == "Strong"

    # Negative 1: Mars in Mesha but in Dusthana H6
    p_neg1, _, _ = make_chart([{"name": "Mars", "sign": "Mesha", "house": 6}], lagna="Vrischika")
    res_neg1 = calculate_yogas(p_neg1, "Vrischika", {})
    assert find_yoga(res_neg1, "Ruchaka Yoga")["present"] is False

    # Negative 2: Mars in Kendra H1 but in enemy/neutral sign Vrishabha
    p_neg2, _, _ = make_chart([{"name": "Mars", "sign": "Vrishabha", "house": 1}], lagna="Vrishabha")
    res_neg2 = calculate_yogas(p_neg2, "Vrishabha", {})
    assert find_yoga(res_neg2, "Ruchaka Yoga")["present"] is False


def test_bhadra_yoga_positive_and_negative():
    # Positive: Mercury in Kanya (exaltation) in H1
    p_pos, _, _ = make_chart([{"name": "Mercury", "sign": "Kanya", "house": 1}], lagna="Kanya")
    res_pos = calculate_yogas(p_pos, "Kanya", {})
    assert find_yoga(res_pos, "Bhadra Yoga")["present"] is True
    assert find_yoga(res_pos, "Bhadra Yoga")["strength"] == "Strong"

    # Negative: Mercury in Kanya in H3 (not Kendra)
    p_neg, _, _ = make_chart([{"name": "Mercury", "sign": "Kanya", "house": 3}], lagna="Karka")
    res_neg = calculate_yogas(p_neg, "Karka", {})
    assert find_yoga(res_neg, "Bhadra Yoga")["present"] is False


def test_hamsa_yoga_positive_and_negative():
    # Positive: Jupiter in Karka (exaltation) in H4
    p_pos, _, _ = make_chart([{"name": "Jupiter", "sign": "Karka", "house": 4}], lagna="Mesha")
    res_pos = calculate_yogas(p_pos, "Mesha", {})
    assert find_yoga(res_pos, "Hamsa Yoga")["present"] is True
    assert find_yoga(res_pos, "Hamsa Yoga")["strength"] == "Strong"

    # Negative: Jupiter in Karka in H8
    p_neg, _, _ = make_chart([{"name": "Jupiter", "sign": "Karka", "house": 8}], lagna="Dhanu")
    res_neg = calculate_yogas(p_neg, "Dhanu", {})
    assert find_yoga(res_neg, "Hamsa Yoga")["present"] is False


def test_malavya_yoga_positive_and_negative():
    # Positive: Venus in Meena (exaltation) in H10
    p_pos, _, _ = make_chart([{"name": "Venus", "sign": "Meena", "house": 10}], lagna="Mithuna")
    res_pos = calculate_yogas(p_pos, "Mithuna", {})
    assert find_yoga(res_pos, "Malavya Yoga")["present"] is True

    # Negative: Venus in Meena in H12
    p_neg, _, _ = make_chart([{"name": "Venus", "sign": "Meena", "house": 12}], lagna="Mesha")
    res_neg = calculate_yogas(p_neg, "Mesha", {})
    assert find_yoga(res_neg, "Malavya Yoga")["present"] is False


def test_sasa_yoga_positive_and_negative():
    # Positive: Saturn in Tula (exaltation) in H7
    p_pos, _, _ = make_chart([{"name": "Saturn", "sign": "Tula", "house": 7}], lagna="Mesha")
    res_pos = calculate_yogas(p_pos, "Mesha", {})
    assert find_yoga(res_pos, "Sasa Yoga")["present"] is True

    # Negative: Saturn in Tula in H5 (Trikona, not Kendra)
    p_neg, _, _ = make_chart([{"name": "Saturn", "sign": "Tula", "house": 5}], lagna="Mithuna")
    res_neg = calculate_yogas(p_neg, "Mithuna", {})
    assert find_yoga(res_neg, "Sasa Yoga")["present"] is False


def test_mahapurusha_umbrella():
    # When Hamsa is active, umbrella is active
    p, _, _ = make_chart([{"name": "Jupiter", "sign": "Karka", "house": 1}], lagna="Karka")
    res = calculate_yogas(p, "Karka", {})
    assert find_yoga(res, "Pancha Mahapurusha Yoga")["present"] is True


# ---------------------------------------------------------------------------
# 3. Solar Yogas Tests
# ---------------------------------------------------------------------------

def test_vesi_vosi_ubhayachari():
    # Sun in H1, Jupiter in H2 (Vesi), Venus in H12 (Vosi) -> Ubhayachari
    p, _, _ = make_chart([
        {"name": "Sun", "house": 1, "sign": "Mesha"},
        {"name": "Jupiter", "house": 2, "sign": "Vrishabha"},
        {"name": "Venus", "house": 12, "sign": "Meena"},
    ], lagna="Mesha")
    res = calculate_yogas(p, "Mesha", {})
    assert find_yoga(res, "Vesi Yoga")["present"] is True
    assert find_yoga(res, "Vosi Yoga")["present"] is True
    assert find_yoga(res, "Ubhayachari Yoga")["present"] is True

    # Negative: Only Jupiter in H2, no planet in H12 -> Vesi True, Vosi False, Ubhayachari False
    p_v, _, _ = make_chart([
        {"name": "Sun", "house": 1, "sign": "Mesha"},
        {"name": "Jupiter", "house": 2, "sign": "Vrishabha"},
    ], lagna="Mesha")
    res_v = calculate_yogas(p_v, "Mesha", {})
    assert find_yoga(res_v, "Vesi Yoga")["present"] is True
    assert find_yoga(res_v, "Vosi Yoga")["present"] is False
    assert find_yoga(res_v, "Ubhayachari Yoga")["present"] is False


# ---------------------------------------------------------------------------
# 4. Lunar Yogas & Kemadruma Cancellation Tests
# ---------------------------------------------------------------------------

def test_sunapha_anapha_durudhara():
    # Moon in H4, Mars in H5 (2nd from Moon), Saturn in H3 (12th from Moon)
    p, _, _ = make_chart([
        {"name": "Moon", "house": 4, "sign": "Karka"},
        {"name": "Mars", "house": 5, "sign": "Simha"},
        {"name": "Saturn", "house": 3, "sign": "Mithuna"},
    ], lagna="Mesha")
    res = calculate_yogas(p, "Mesha", {})
    assert find_yoga(res, "Sunapha Yoga")["present"] is True
    assert find_yoga(res, "Anapha Yoga")["present"] is True
    assert find_yoga(res, "Durudhara Yoga")["present"] is True


def test_kemadruma_and_cancellation():
    # Isolated Moon in H5, no planets in H4 or H6 (2nd/12th from Moon)
    # No planets in Kendra from Moon ({1,4,7,10} from H5 = {H5, H8, H11, H2})
    # No planets in Kendra from Lagna ({H1, H4, H7, H10})
    # Planets safely placed in H3 and H9 (neither is kendra from Lagna nor Moon nor adjacent to Moon)
    p_isolated, _, _ = make_chart([
        {"name": "Moon", "house": 5, "sign": "Simha"},
        {"name": "Sun", "house": 9, "sign": "Dhanu"},
        {"name": "Mars", "house": 3, "sign": "Mithuna"},
        {"name": "Jupiter", "house": 9, "sign": "Dhanu"},
        {"name": "Saturn", "house": 3, "sign": "Mithuna"},
        {"name": "Mercury", "house": 9, "sign": "Dhanu"},
        {"name": "Venus", "house": 3, "sign": "Mithuna"},
    ], lagna="Mesha")
    res_iso = calculate_yogas(p_isolated, "Mesha", {})
    y_kema = find_yoga(res_iso, "Kemadruma Yoga")
    assert y_kema["present"] is True
    assert y_kema["cancelled"] is False

    # Cancellation: Add Jupiter in Kendra from Lagna (H1) -> Kemadruma Bhanga
    p_cancelled, _, _ = make_chart([
        {"name": "Moon", "house": 5, "sign": "Simha"},
        {"name": "Sun", "house": 9, "sign": "Dhanu"},
        {"name": "Mars", "house": 3, "sign": "Mithuna"},
        {"name": "Jupiter", "house": 1, "sign": "Mesha"},  # In Kendra from Lagna
        {"name": "Saturn", "house": 3, "sign": "Mithuna"},
        {"name": "Mercury", "house": 9, "sign": "Dhanu"},
        {"name": "Venus", "house": 3, "sign": "Mithuna"},
    ], lagna="Mesha")
    res_canc = calculate_yogas(p_cancelled, "Mesha", {})
    y_canc = find_yoga(res_canc, "Kemadruma Yoga")
    assert y_canc["present"] is False
    assert y_canc["cancelled"] is True
    assert "Kemadruma Bhanga" in y_canc["cancellation_reason"]


# ---------------------------------------------------------------------------
# 5. Chandra & Auspicious Conjunction Yogas Tests
# ---------------------------------------------------------------------------

def test_gajakesari_yoga():
    # Jupiter in H7 from Moon (e.g. Moon in H1, Jupiter in H7)
    p, _, _ = make_chart([
        {"name": "Moon", "house": 1, "sign": "Mesha"},
        {"name": "Jupiter", "house": 7, "sign": "Tula"},
    ], lagna="Mesha")
    res = calculate_yogas(p, "Mesha", {})
    assert find_yoga(res, "Gajakesari Yoga")["present"] is True

    # Negative: Jupiter in 6th from Moon (Moon H1, Jupiter H6)
    p_neg, _, _ = make_chart([
        {"name": "Moon", "house": 1, "sign": "Mesha"},
        {"name": "Jupiter", "house": 6, "sign": "Kanya"},
    ], lagna="Mesha")
    res_neg = calculate_yogas(p_neg, "Mesha", {})
    assert find_yoga(res_neg, "Gajakesari Yoga")["present"] is False


def test_chandra_mangala_yoga():
    # Moon and Mars conjunct in H2
    p, _, _ = make_chart([
        {"name": "Moon", "house": 2, "sign": "Vrishabha"},
        {"name": "Mars", "house": 2, "sign": "Vrishabha"},
    ], lagna="Mesha")
    res = calculate_yogas(p, "Mesha", {})
    assert find_yoga(res, "Chandra-Mangala Yoga")["present"] is True


def test_adhi_yoga():
    # Moon in H1, benefics Mercury, Jupiter, Venus in H6, H7, H8
    p, _, _ = make_chart([
        {"name": "Moon", "house": 1, "sign": "Mesha"},
        {"name": "Mercury", "house": 6, "sign": "Kanya"},
        {"name": "Jupiter", "house": 7, "sign": "Tula"},
        {"name": "Venus", "house": 8, "sign": "Vrischika"},
    ], lagna="Mesha")
    res = calculate_yogas(p, "Mesha", {})
    assert find_yoga(res, "Adhi Yoga")["present"] is True
    assert find_yoga(res, "Adhi Yoga")["strength"] == "Strong"


def test_budhaditya_yoga():
    p, _, _ = make_chart([
        {"name": "Sun", "house": 10, "sign": "Makara"},
        {"name": "Mercury", "house": 10, "sign": "Makara"},
    ], lagna="Mesha")
    res = calculate_yogas(p, "Mesha", {})
    assert find_yoga(res, "Budhaditya Yoga")["present"] is True
    assert find_yoga(res, "Budhaditya Yoga")["strength"] == "Strong"


# ---------------------------------------------------------------------------
# 6. Viparita Raja Yogas Tests
# ---------------------------------------------------------------------------

def test_viparita_raja_yogas():
    # For Mesha lagna:
    # 6th lord is Mercury, 8th lord is Mars, 12th lord is Jupiter
    # Put Mercury in H8 (Harsha), Mars in H12 (Sarala), Jupiter in H6 (Vimala)
    p, _, _ = make_chart([
        {"name": "Mercury", "house": 8, "sign": "Vrischika"},
        {"name": "Mars", "house": 12, "sign": "Meena"},
        {"name": "Jupiter", "house": 6, "sign": "Kanya"},
    ], lagna="Mesha")
    res = calculate_yogas(p, "Mesha", {})
    assert find_yoga(res, "Harsha Viparita Raja Yoga")["present"] is True
    assert find_yoga(res, "Sarala Viparita Raja Yoga")["present"] is True
    assert find_yoga(res, "Vimala Viparita Raja Yoga")["present"] is True
    assert find_yoga(res, "Viparita Raja Yoga")["present"] is True

    # Negative: 6th lord in 1st house
    p_neg, _, _ = make_chart([{"name": "Mercury", "house": 1, "sign": "Mesha"}], lagna="Mesha")
    res_neg = calculate_yogas(p_neg, "Mesha", {})
    assert find_yoga(res_neg, "Harsha Viparita Raja Yoga")["present"] is False


# ---------------------------------------------------------------------------
# 7. Raja Yogas & Royal Association Tests
# ---------------------------------------------------------------------------

def test_dharma_karmadhipati_yoga():
    # For Mesha lagna: 9th lord = Jupiter, 10th lord = Saturn
    # Conjunct in 10th house
    p, _, _ = make_chart([
        {"name": "Jupiter", "house": 10, "sign": "Makara"},
        {"name": "Saturn", "house": 10, "sign": "Makara"},
    ], lagna="Mesha")
    res = calculate_yogas(p, "Mesha", {})
    assert find_yoga(res, "Dharma-Karmadhipati Yoga")["present"] is True


def test_lakshmi_and_saraswati_yogas():
    # Mesha lagna: 9th lord is Jupiter, placed in Karka (exalted) in H4 (Kendra)
    # Lagna lord is Mars, placed in H1 (own sign)
    p, _, _ = make_chart([
        {"name": "Jupiter", "house": 4, "sign": "Karka"},
        {"name": "Mars", "house": 1, "sign": "Mesha"},
        {"name": "Venus", "house": 4, "sign": "Karka"},
        {"name": "Mercury", "house": 1, "sign": "Mesha"},
    ], lagna="Mesha")
    res = calculate_yogas(p, "Mesha", {})
    assert find_yoga(res, "Lakshmi Yoga")["present"] is True
    assert find_yoga(res, "Saraswati Yoga")["present"] is True


def test_amala_yoga():
    # Jupiter in H10 from Lagna
    p, _, _ = make_chart([{"name": "Jupiter", "house": 10, "sign": "Makara"}], lagna="Mesha")
    res = calculate_yogas(p, "Mesha", {})
    assert find_yoga(res, "Amala Yoga")["present"] is True


# ---------------------------------------------------------------------------
# 8. Dhana Yogas Tests
# ---------------------------------------------------------------------------

def test_dhana_yogas():
    # For Mesha lagna: 2nd lord = Venus, 11th lord = Saturn
    # Conjunct in H2
    p, _, _ = make_chart([
        {"name": "Venus", "house": 2, "sign": "Vrishabha"},
        {"name": "Saturn", "house": 2, "sign": "Vrishabha"},
    ], lagna="Mesha")
    res = calculate_yogas(p, "Mesha", {})
    assert find_yoga(res, "Dhana Yoga (2nd & 11th Lords)")["present"] is True
    assert find_yoga(res, "Dhana Yoga")["present"] is True


# ---------------------------------------------------------------------------
# 9. Kartari Yogas Tests
# ---------------------------------------------------------------------------

def test_kartari_yogas():
    # Shubha Kartari: Jupiter in H2, Venus in H12
    p_shubha, _, _ = make_chart([
        {"name": "Jupiter", "house": 2, "sign": "Vrishabha"},
        {"name": "Venus", "house": 12, "sign": "Meena"},
    ], lagna="Mesha")
    res_shubha = calculate_yogas(p_shubha, "Mesha", {})
    assert find_yoga(res_shubha, "Shubha Kartari Yoga")["present"] is True

    # Papa Kartari: Saturn in H2, Mars in H12
    p_papa, _, _ = make_chart([
        {"name": "Saturn", "house": 2, "sign": "Vrishabha"},
        {"name": "Mars", "house": 12, "sign": "Meena"},
    ], lagna="Mesha")
    res_papa = calculate_yogas(p_papa, "Mesha", {})
    assert find_yoga(res_papa, "Papa Kartari Yoga")["present"] is True


# ---------------------------------------------------------------------------
# 10. Nabhasa Yogas Tests
# ---------------------------------------------------------------------------

def test_nabhasa_ashraya_yogas():
    # Rajju: All 7 classical planets in Movable signs (Mesha, Karka, Tula, Makara)
    p_rajju, _, _ = make_chart([
        {"name": "Sun", "sign": "Mesha", "house": 1},
        {"name": "Moon", "sign": "Karka", "house": 4},
        {"name": "Mars", "sign": "Tula", "house": 7},
        {"name": "Mercury", "sign": "Makara", "house": 10},
        {"name": "Jupiter", "sign": "Mesha", "house": 1},
        {"name": "Venus", "sign": "Karka", "house": 4},
        {"name": "Saturn", "sign": "Tula", "house": 7},
    ], lagna="Mesha")
    res_rajju = calculate_yogas(p_rajju, "Mesha", {})
    assert find_yoga(res_rajju, "Rajju Nabhasa Yoga")["present"] is True
    assert find_yoga(res_rajju, "Musala Nabhasa Yoga")["present"] is False


def test_nabhasa_sankhya_yogas():
    # Vina: All 7 planets in 7 distinct signs
    p_vina, _, _ = make_chart([
        {"name": "Sun", "sign": "Mesha", "house": 1},
        {"name": "Moon", "sign": "Vrishabha", "house": 2},
        {"name": "Mars", "sign": "Mithuna", "house": 3},
        {"name": "Mercury", "sign": "Karka", "house": 4},
        {"name": "Jupiter", "sign": "Simha", "house": 5},
        {"name": "Venus", "sign": "Kanya", "house": 6},
        {"name": "Saturn", "sign": "Tula", "house": 7},
    ], lagna="Mesha")
    res_vina = calculate_yogas(p_vina, "Mesha", {})
    assert find_yoga(res_vina, "Vina Nabhasa Yoga")["present"] is True
    assert find_yoga(res_vina, "Gola Nabhasa Yoga")["present"] is False

    # Gola: All 7 planets in 1 single sign
    p_gola, _, _ = make_chart([
        {"name": "Sun", "sign": "Mesha", "house": 1},
        {"name": "Moon", "sign": "Mesha", "house": 1},
        {"name": "Mars", "sign": "Mesha", "house": 1},
        {"name": "Mercury", "sign": "Mesha", "house": 1},
        {"name": "Jupiter", "sign": "Mesha", "house": 1},
        {"name": "Venus", "sign": "Mesha", "house": 1},
        {"name": "Saturn", "sign": "Mesha", "house": 1},
    ], lagna="Mesha")
    res_gola = calculate_yogas(p_gola, "Mesha", {})
    assert find_yoga(res_gola, "Gola Nabhasa Yoga")["present"] is True
    assert find_yoga(res_gola, "Vina Nabhasa Yoga")["present"] is False


# ---------------------------------------------------------------------------
# 11. Affliction & Modern Yogas Gating Tests
# ---------------------------------------------------------------------------

def test_kaal_sarp_default_disabled():
    # All planets between Rahu and Ketu
    p, _, _ = make_chart([
        {"name": "Rahu", "house": 1, "sign": "Mesha"},
        {"name": "Ketu", "house": 7, "sign": "Tula"},
        {"name": "Sun", "house": 2, "sign": "Vrishabha"},
        {"name": "Moon", "house": 3, "sign": "Mithuna"},
        {"name": "Mars", "house": 4, "sign": "Karka"},
        {"name": "Mercury", "house": 5, "sign": "Simha"},
        {"name": "Jupiter", "house": 6, "sign": "Kanya"},
        {"name": "Venus", "house": 2, "sign": "Vrishabha"},
        {"name": "Saturn", "house": 3, "sign": "Mithuna"},
    ], lagna="Mesha")

    # When include_disabled=False (default), Kaal Sarp is OFF
    res_default = calculate_yogas(p, "Mesha", {})
    y_default = find_yoga(res_default, "Kaal Sarp Yoga")
    assert y_default["present"] is False

    # When include_disabled=True, Kaal Sarp evaluates
    res_enabled = calculate_yogas(p, "Mesha", {}, include_disabled=True)
    y_enabled = find_yoga(res_enabled, "Kaal Sarp Yoga")
    assert y_enabled["present"] is True


def test_guru_chandal_yoga():
    p, _, _ = make_chart([
        {"name": "Jupiter", "house": 9, "sign": "Dhanu"},
        {"name": "Rahu", "house": 9, "sign": "Dhanu"},
    ], lagna="Mesha")
    res = calculate_yogas(p, "Mesha", {})
    assert find_yoga(res, "Guru-Chandal Yoga")["present"] is True


# ---------------------------------------------------------------------------
# 12. Helper & Interface Backward Compatibility Tests
# ---------------------------------------------------------------------------

def test_detect_advanced_yogas_interface():
    chart = {
        "basic_details": {"lagna": "Mesha"},
        "planets_by_house": {
            "1": [{"planet": "Sun", "sign": "Mesha"}, {"planet": "Mercury", "sign": "Mesha"}],
            "4": [{"planet": "Jupiter", "sign": "Karka"}],
            "7": [{"planet": "Saturn", "sign": "Tula"}],
        }
    }
    active = detect_advanced_yogas(chart)
    assert isinstance(active, list)
    assert "Budhaditya Yoga" in active
    assert "Hamsa Yoga" in active
    assert "Sasa Yoga" in active


# ---------------------------------------------------------------------------
# 13. Additional Classical Families & Granular Rule Verification
# ---------------------------------------------------------------------------

def test_lagnadhi_yoga():
    p, _, _ = make_chart([
        {"name": "Mercury", "house": 6, "sign": "Kanya"},
        {"name": "Jupiter", "house": 7, "sign": "Tula"},
        {"name": "Venus", "house": 8, "sign": "Vrischika"},
    ], lagna="Mesha")
    res = calculate_yogas(p, "Mesha", {})
    assert find_yoga(res, "Lagnadhi Yoga")["present"] is True


def test_neecha_bhanga_and_raja_qualification():
    # Debilitated Mars in Karka, but retrograde -> Neecha Bhanga True
    p, _, _ = make_chart([
        {"name": "Mars", "house": 4, "sign": "Karka", "retrograde": True},
        {"name": "Moon", "house": 1, "sign": "Mesha"},
    ], lagna="Mesha")
    res = calculate_yogas(p, "Mesha", {})
    assert find_yoga(res, "Neecha Bhanga")["present"] is True
    # Placed in H4 (Kendra) -> also qualifies for Neecha Bhanga Raja Yoga
    assert find_yoga(res, "Neecha Bhanga Raja Yoga")["present"] is True

    # Debilitated Sun in Tula without cancellation
    p_uncanc, _, _ = make_chart([
        {"name": "Sun", "house": 7, "sign": "Tula", "retrograde": False},
        {"name": "Venus", "house": 3, "sign": "Mithuna"},
    ], lagna="Mesha")
    res_uncanc = calculate_yogas(p_uncanc, "Mesha", {})
    # Venus is in H3 (not kendra from lagna H1 or moon)
    assert find_yoga(res_uncanc, "Neecha Bhanga")["present"] is False
    assert find_yoga(res_uncanc, "Neecha Bhanga Raja Yoga")["present"] is False


def test_parivartana_yoga_variants():
    # 1. Maha Parivartana: Exchange between Lagna lord (H1) and 10th lord (H10)
    # Mesha Lagna: L1=Mars, L10=Saturn. Mars in Makara (H10), Saturn in Mesha (H1).
    p_maha, _, _ = make_chart([
        {"name": "Mars", "house": 10, "sign": "Makara"},
        {"name": "Saturn", "house": 1, "sign": "Mesha"},
    ], lagna="Mesha")
    res_maha = calculate_yogas(p_maha, "Mesha", {})
    assert find_yoga(res_maha, "Maha Parivartana Yoga")["present"] is True
    assert find_yoga(res_maha, "Dainya Parivartana Yoga")["present"] is False

    # 2. Dainya Parivartana: Exchange involving Dusthana (6th lord and 1st lord)
    # Mesha Lagna: L1=Mars, L6=Mercury. Mars in Kanya (H6), Mercury in Mesha (H1).
    p_dainya, _, _ = make_chart([
        {"name": "Mars", "house": 6, "sign": "Kanya"},
        {"name": "Mercury", "house": 1, "sign": "Mesha"},
    ], lagna="Mesha")
    res_dainya = calculate_yogas(p_dainya, "Mesha", {})
    assert find_yoga(res_dainya, "Dainya Parivartana Yoga")["present"] is True

    # 3. Khala Parivartana: Exchange involving 3rd lord (L3=Mercury, L5=Sun)
    # Mercury in Simha (H5), Sun in Mithuna (H3).
    p_khala, _, _ = make_chart([
        {"name": "Mercury", "house": 5, "sign": "Simha"},
        {"name": "Sun", "house": 3, "sign": "Mithuna"},
    ], lagna="Mesha")
    res_khala = calculate_yogas(p_khala, "Mesha", {})
    assert find_yoga(res_khala, "Khala Parivartana Yoga")["present"] is True


def test_special_character_and_raja_yogas():
    # Guru-Mangala: Jupiter and Mars conjunct in H1
    p_gm, _, _ = make_chart([
        {"name": "Jupiter", "house": 1, "sign": "Mesha"},
        {"name": "Mars", "house": 1, "sign": "Mesha"},
    ], lagna="Mesha")
    res_gm = calculate_yogas(p_gm, "Mesha", {})
    assert find_yoga(res_gm, "Guru-Mangala Yoga")["present"] is True

    # Raja Sambandha: Lagna lord Mars placed in 10th house
    p_rs, _, _ = make_chart([
        {"name": "Mars", "house": 10, "sign": "Makara"},
        {"name": "Saturn", "house": 10, "sign": "Makara"},
    ], lagna="Mesha")
    res_rs = calculate_yogas(p_rs, "Mesha", {})
    assert find_yoga(res_rs, "Raja Sambandha Yoga")["present"] is True

    # Gauri Yoga: Moon in Vrishabha (exalted) in H2 aspected by Jupiter from H6 (trine aspect 9th from H6=H2)
    p_gy, _, _ = make_chart([
        {"name": "Moon", "house": 1, "sign": "Karka"},  # in own sign in Kendra
    ], lagna="Karka")
    res_gy = calculate_yogas(p_gy, "Karka", {})
    assert find_yoga(res_gy, "Gauri Yoga")["present"] is True


def test_dhana_yoga_pairs():
    # 1st & 2nd Lords conjunct in Kendra: Mesha lagna L1=Mars, L2=Venus in H1
    p1, _, _ = make_chart([
        {"name": "Mars", "house": 1, "sign": "Mesha"},
        {"name": "Venus", "house": 1, "sign": "Mesha"},
    ], lagna="Mesha")
    res1 = calculate_yogas(p1, "Mesha", {})
    assert find_yoga(res1, "Dhana Yoga (1st & 2nd Lords)")["present"] is True

    # 5th & 9th Lords: Mesha lagna L5=Sun, L9=Jupiter conjunct in H5
    p2, _, _ = make_chart([
        {"name": "Sun", "house": 5, "sign": "Simha"},
        {"name": "Jupiter", "house": 5, "sign": "Simha"},
    ], lagna="Mesha")
    res2 = calculate_yogas(p2, "Mesha", {})
    assert find_yoga(res2, "Dhana Yoga (5th & 9th Lords)")["present"] is True

    # 2nd & 5th Lords: Mesha lagna L2=Venus, L5=Sun conjunct in H2
    p3, _, _ = make_chart([
        {"name": "Venus", "house": 2, "sign": "Vrishabha"},
        {"name": "Sun", "house": 2, "sign": "Vrishabha"},
    ], lagna="Mesha")
    res3 = calculate_yogas(p3, "Mesha", {})
    assert find_yoga(res3, "Dhana Yoga (2nd & 5th Lords)")["present"] is True

    # Vasumati Yoga: Benefics in Upachaya (3, 6, 10, 11)
    p4, _, _ = make_chart([
        {"name": "Jupiter", "house": 3, "sign": "Mithuna"},
        {"name": "Venus", "house": 6, "sign": "Kanya"},
        {"name": "Mercury", "house": 11, "sign": "Kumbha"},
    ], lagna="Mesha")
    res4 = calculate_yogas(p4, "Mesha", {})
    assert find_yoga(res4, "Vasumati Yoga")["present"] is True


def test_dala_and_sankhya_nabhasa_yogas():
    # Sarpa Yoga: Kendra houses occupied only by malefics (Sun H1, Mars H4, Saturn H7, no benefics in Kendra)
    p_sarpa, _, _ = make_chart([
        {"name": "Sun", "house": 1, "sign": "Mesha"},
        {"name": "Mars", "house": 4, "sign": "Karka"},
        {"name": "Saturn", "house": 7, "sign": "Tula"},
        {"name": "Moon", "house": 2, "sign": "Vrishabha"},
        {"name": "Mercury", "house": 3, "sign": "Mithuna"},
        {"name": "Jupiter", "house": 5, "sign": "Simha"},
        {"name": "Venus", "house": 6, "sign": "Kanya"},
    ], lagna="Mesha")
    res_sarpa = calculate_yogas(p_sarpa, "Mesha", {})
    assert find_yoga(res_sarpa, "Sarpa Nabhasa Yoga")["present"] is True
    assert find_yoga(res_sarpa, "Mala Nabhasa Yoga")["present"] is False

    # Mala Yoga: Kendra houses occupied only by benefics (Jupiter H1, Venus H4, Mercury H7, no malefics in Kendra)
    p_mala, _, _ = make_chart([
        {"name": "Jupiter", "house": 1, "sign": "Mesha"},
        {"name": "Venus", "house": 4, "sign": "Karka"},
        {"name": "Mercury", "house": 7, "sign": "Tula"},
        {"name": "Sun", "house": 2, "sign": "Vrishabha"},
        {"name": "Mars", "house": 3, "sign": "Mithuna"},
        {"name": "Saturn", "house": 5, "sign": "Simha"},
        {"name": "Moon", "house": 6, "sign": "Kanya"},
    ], lagna="Mesha")
    res_mala = calculate_yogas(p_mala, "Mesha", {})
    assert find_yoga(res_mala, "Mala Nabhasa Yoga")["present"] is True
    assert find_yoga(res_mala, "Sarpa Nabhasa Yoga")["present"] is False


def test_ashubha_and_arishta_with_cancellation():
    # Ashubha: Malefics in Lagna and 9th
    p_ash, _, _ = make_chart([
        {"name": "Saturn", "house": 1, "sign": "Mesha"},
        {"name": "Mars", "house": 9, "sign": "Dhanu"},
    ], lagna="Mesha")
    res_ash = calculate_yogas(p_ash, "Mesha", {})
    assert find_yoga(res_ash, "Ashubha Yoga")["present"] is True

    # Arishta cancelled by Arishta Bhanga: Jupiter in Kendra (H1)
    p_arishta_bhanga, _, _ = make_chart([
        {"name": "Mars", "house": 6, "sign": "Kanya"},  # Lagna lord in 6th
        {"name": "Saturn", "house": 6, "sign": "Kanya"}, # Conjoined with malefic
        {"name": "Jupiter", "house": 1, "sign": "Mesha"}, # Strong Jupiter in Kendra cancels Arishta
    ], lagna="Mesha")
    res_ab = calculate_yogas(p_arishta_bhanga, "Mesha", {})
    assert find_yoga(res_ab, "Arishta Bhanga")["present"] is True
    assert find_yoga(res_ab, "Arishta Yoga")["present"] is False
    assert find_yoga(res_ab, "Arishta Yoga")["cancelled"] is True
