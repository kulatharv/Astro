"""
Unit and Integration Test Suite for WP4 — Dosha Catalog & Boundary Conditions.

Validates:
- Multi-Frame Mangal Dosha (Lagna, Moon, Venus frames) with all 16 classical cancellations.
- Shani Sade Sati calculation (Rising, Peak, Setting phases, exact degree orb).
- Kantaka Shani (4th, 7th, 10th from Moon) and Ashtama Shani (8th from Moon).
- Retrograde boundary re-entry handling.
- Kaal Sarp Dosh (12 types, Savya/Apsavya, Anshik, modern default=False gating).
- Pitru Dosha & Grahan Dosha with exact angular orbs and cancellations.
- Gandmool Dosha with deep Gandanta sandhi padas.
- Backward compatibility of calculate_doshas(), evaluate_mangal_dosha(), evaluate_pitru_dosha().
"""

import pytest
from shared.veda.doshas import (
    evaluate_mangal_dosha,
    evaluate_mangal_dosha_multiframe,
    check_mangal_cancellations,
    calculate_sade_sati,
    calculate_kaal_sarp,
    evaluate_pitru_dosha,
    evaluate_grahan_dosha,
    evaluate_gandmool_dosha,
    calculate_doshas,
    MANGLIK_HOUSES,
    GANDMOOL_NAKSHATRAS,
    KAAL_SARP_TYPES,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_pmap(planet_specs: list[dict]) -> dict[str, dict]:
    pmap = {}
    for p in planet_specs:
        name = p["name"]
        deg_val = p.get("degree", p.get("degree_decimal", 15.0))
        entry = {
            "name": name,
            "sign": p.get("sign", "Mesha"),
            "house": p.get("house", 1),
            "degree": deg_val,
            "degree_decimal": deg_val,
            "retrograde": p.get("retrograde", False),
            "nakshatra": p.get("nakshatra", ""),
            "pada": p.get("pada", 1),
        }
        pmap[name] = entry
        pmap[name.capitalize()] = entry
    return pmap


def find_dosha(results: list[dict], name: str) -> dict:
    for d in results:
        if d["name"] == name:
            return d
    raise AssertionError(f"Dosha '{name}' not found in results: {[d['name'] for d in results]}")


# ---------------------------------------------------------------------------
# 1. Multi-Frame Mangal Dosha Tests
# ---------------------------------------------------------------------------

def test_mangal_dosha_raw_and_multi_frame():
    # Mars in H7 from Lagna, H1 from Moon (Moon in H7), H4 from Venus (Venus in H4)
    # Active in all 3 frames (Lagna H7, Moon H1, Venus H4)
    pmap = make_pmap([
        {"name": "Mars", "house": 7, "sign": "Tula"},
        {"name": "Moon", "house": 7, "sign": "Tula"},  # Chandra Lagna: Mars in H1
        {"name": "Venus", "house": 4, "sign": "Karka"}, # Shukra Lagna: Mars in H4 from Venus
    ])
    res = evaluate_mangal_dosha_multiframe(pmap)
    assert res["frames"]["lagna"]["raw"] is True
    assert res["frames"]["moon"]["raw"] is True
    assert res["frames"]["venus"]["raw"] is True
    assert any("Mars conjunct Moon" in c for c in res["frames"]["lagna"]["cancellations"])

    # Mars in neutral house H3 (not Manglik in Lagna frame)
    pmap_non = make_pmap([
        {"name": "Mars", "house": 3, "sign": "Mithuna"},
        {"name": "Moon", "house": 1, "sign": "Mesha"},
        {"name": "Venus", "house": 1, "sign": "Mesha"},
    ])
    res_non = evaluate_mangal_dosha_multiframe(pmap_non)
    assert res_non["raw"] is False
    assert res_non["frames"]["lagna"]["raw"] is False


def test_mangal_dosha_all_16_cancellations():
    # 1. Own sign (Mesha / Vrischika)
    canc1 = check_mangal_cancellations(1, "Mesha", make_pmap([{"name": "Mars", "house": 1, "sign": "Mesha"}]))
    assert any("own sign" in c for c in canc1)

    # 2. Exaltation (Makara)
    canc2 = check_mangal_cancellations(7, "Makara", make_pmap([{"name": "Mars", "house": 7, "sign": "Makara"}]))
    assert any("exaltation" in c for c in canc2)

    # 3. Debilitation (Karka)
    canc3 = check_mangal_cancellations(4, "Karka", make_pmap([{"name": "Mars", "house": 4, "sign": "Karka"}]))
    assert any("debilitated" in c for c in canc3)

    # 4. Guru-Mangala (Mars conjunct Jupiter)
    canc4 = check_mangal_cancellations(7, "Tula", make_pmap([
        {"name": "Mars", "house": 7, "sign": "Tula"},
        {"name": "Jupiter", "house": 7, "sign": "Tula"},
    ]))
    assert any("conjunct benefic Jupiter" in c for c in canc4)

    # 5. Jupiter aspects Mars (Jupiter in H1 aspects H7)
    canc5 = check_mangal_cancellations(7, "Tula", make_pmap([
        {"name": "Mars", "house": 7, "sign": "Tula"},
        {"name": "Jupiter", "house": 1, "sign": "Mesha"},
    ]))
    assert any("Jupiter" in c and "aspect" in c for c in canc5)

    # 6. Jupiter in Kendra (H4)
    canc6 = check_mangal_cancellations(12, "Dhanu", make_pmap([
        {"name": "Mars", "house": 12, "sign": "Dhanu"},
        {"name": "Jupiter", "house": 4, "sign": "Karka"},
    ]))
    assert any("Jupiter situated in Kendra" in c for c in canc6)

    # 7. Mars in 1st house in Mesha
    canc7 = check_mangal_cancellations(1, "Mesha", make_pmap([{"name": "Mars", "house": 1, "sign": "Mesha"}]))
    assert any("1st house in Mesha" in c for c in canc7)

    # 8. Mars in 2nd house in Mithuna/Kanya
    canc8 = check_mangal_cancellations(2, "Mithuna", make_pmap([{"name": "Mars", "house": 2, "sign": "Mithuna"}]))
    assert any("2nd house in Mithuna" in c for c in canc8)

    # 9. Mars in 4th house in Mesha/Vrischika
    canc9 = check_mangal_cancellations(4, "Vrischika", make_pmap([{"name": "Mars", "house": 4, "sign": "Vrischika"}]))
    assert any("4th house in Vrischika" in c for c in canc9)

    # 10. Mars in 7th house in Karka/Makara
    canc10 = check_mangal_cancellations(7, "Makara", make_pmap([{"name": "Mars", "house": 7, "sign": "Makara"}]))
    assert any("7th house in Makara" in c for c in canc10)

    # 11. Mars in 8th house in Dhanu/Meena
    canc11 = check_mangal_cancellations(8, "Dhanu", make_pmap([{"name": "Mars", "house": 8, "sign": "Dhanu"}]))
    assert any("8th house in Dhanu" in c for c in canc11)

    # 12. Mars in 12th house in Vrishabha/Tula
    canc12 = check_mangal_cancellations(12, "Tula", make_pmap([{"name": "Mars", "house": 12, "sign": "Tula"}]))
    assert any("12th house in Tula" in c for c in canc12)

    # 13. Mars conjunct Moon (Chandra-Mangala)
    canc13 = check_mangal_cancellations(8, "Simha", make_pmap([
        {"name": "Mars", "house": 8, "sign": "Simha"},
        {"name": "Moon", "house": 8, "sign": "Simha"},
    ]))
    assert any("Chandra-Mangala" in c for c in canc13)

    # 14. Mars in Simha or Kumbha
    canc14 = check_mangal_cancellations(7, "Simha", make_pmap([{"name": "Mars", "house": 7, "sign": "Simha"}]))
    assert any("Simha" in c for c in canc14)

    # 15. Mars conjunct Saturn
    canc15 = check_mangal_cancellations(7, "Kanya", make_pmap([
        {"name": "Mars", "house": 7, "sign": "Kanya"},
        {"name": "Saturn", "house": 7, "sign": "Kanya"},
    ]))
    assert any("Saturn" in c for c in canc15)

    # 16. Venus strong in Kendra
    canc16 = check_mangal_cancellations(8, "Kanya", make_pmap([
        {"name": "Mars", "house": 8, "sign": "Kanya"},
        {"name": "Venus", "house": 4, "sign": "Meena"},  # Exalted in Kendra
    ]))
    assert any("Venus strong in Kendra" in c for c in canc16)


# ---------------------------------------------------------------------------
# 2. Shani Sade Sati, Kantaka Shani & Ashtama Shani Tests
# ---------------------------------------------------------------------------

def test_sade_sati_phases():
    # Natal Moon in Mesha
    # 1. Rising Phase: Saturn in Meena (12th from Moon)
    r1 = calculate_sade_sati(moon_sign="Mesha", moon_deg=10.0, saturn_sign="Meena", saturn_deg=20.0)
    assert r1["is_sade_sati"] is True
    assert r1["phase"] == "Rising"
    assert "Rising Phase" in r1["phase_name"]

    # 2. Peak Phase: Saturn in Mesha (Moon sign)
    r2 = calculate_sade_sati(moon_sign="Mesha", moon_deg=10.0, saturn_sign="Mesha", saturn_deg=12.0)
    assert r2["is_sade_sati"] is True
    assert r2["phase"] == "Peak"
    assert "Peak Phase" in r2["phase_name"]
    assert abs(r2["orb_degrees"] - 2.0) < 0.1

    # 3. Setting Phase: Saturn in Vrishabha (2nd from Moon)
    r3 = calculate_sade_sati(moon_sign="Mesha", moon_deg=10.0, saturn_sign="Vrishabha", saturn_deg=5.0)
    assert r3["is_sade_sati"] is True
    assert r3["phase"] == "Setting"
    assert "Setting Phase" in r3["phase_name"]

    # 4. Out of Sade Sati: Saturn in Mithuna (3rd from Moon)
    r4 = calculate_sade_sati(moon_sign="Mesha", moon_deg=10.0, saturn_sign="Mithuna", saturn_deg=5.0)
    assert r4["is_sade_sati"] is False
    assert r4["phase"] == "None"


def test_kantaka_and_ashtama_shani():
    # Moon in Mesha
    # Kantaka Shani: 4th (Karka), 7th (Tula), 10th (Makara) from Moon
    k4 = calculate_sade_sati(moon_sign="Mesha", saturn_sign="Karka")
    assert k4["is_kantaka_shani"] is True
    assert k4["kantaka_house"] == 4

    k7 = calculate_sade_sati(moon_sign="Mesha", saturn_sign="Tula")
    assert k7["is_kantaka_shani"] is True
    assert k7["kantaka_house"] == 7

    k10 = calculate_sade_sati(moon_sign="Mesha", saturn_sign="Makara")
    assert k10["is_kantaka_shani"] is True
    assert k10["kantaka_house"] == 10

    # Ashtama Shani: 8th (Vrischika) from Moon
    a8 = calculate_sade_sati(moon_sign="Mesha", saturn_sign="Vrischika")
    assert a8["is_ashtama_shani"] is True
    assert a8["is_sade_sati"] is False


def test_sade_sati_retrograde_boundary_reentry():
    # Saturn at 1.5° Vrishabha (Setting Phase) but retrograde -> boundary re-entry into Mesha (Peak)
    res = calculate_sade_sati(
        moon_sign="Mesha",
        moon_deg=28.0,
        saturn_sign="Vrishabha",
        saturn_deg=1.5,
        is_saturn_retrograde=True,
    )
    assert res["is_sade_sati"] is True
    assert res["saturn_retrograde"] is True
    assert res["retrograde_reentry"] is True
    assert "retrograde near sign border" in res["description"]


# ---------------------------------------------------------------------------
# 3. Kaal Sarp Dosh (12 Types, Modern Gating) Tests
# ---------------------------------------------------------------------------

def test_kaal_sarp_12_types_and_gating():
    # Rahu in H1, Ketu in H7 -> Type 1: Anant Kaal Sarp
    pmap_anant = make_pmap([
        {"name": "Rahu", "house": 1, "sign": "Mesha"},
        {"name": "Ketu", "house": 7, "sign": "Tula"},
        {"name": "Sun", "house": 2, "sign": "Vrishabha"},
        {"name": "Moon", "house": 3, "sign": "Mithuna"},
        {"name": "Mars", "house": 4, "sign": "Karka"},
        {"name": "Mercury", "house": 5, "sign": "Simha"},
        {"name": "Jupiter", "house": 6, "sign": "Kanya"},
        {"name": "Venus", "house": 2, "sign": "Vrishabha"},
        {"name": "Saturn", "house": 3, "sign": "Mithuna"},
    ])

    # Gated by default: enabled_by_default=False
    ks_off = calculate_kaal_sarp(pmap_anant, enabled_by_default=False)
    assert ks_off["present"] is False
    assert ks_off["raw_present"] is True
    assert ks_off["type_name"] == "Anant Kaal Sarp"

    # Explicitly enabled:
    ks_on = calculate_kaal_sarp(pmap_anant, enabled_by_default=True)
    assert ks_on["present"] is True
    assert ks_on["is_full"] is True
    assert ks_on["type_name"] == "Anant Kaal Sarp"

    # Rahu in H5, Ketu in H11 -> Type 5: Padma Kaal Sarp
    pmap_padma = make_pmap([
        {"name": "Rahu", "house": 5, "sign": "Simha"},
        {"name": "Ketu", "house": 11, "sign": "Kumbha"},
        {"name": "Sun", "house": 6, "sign": "Kanya"},
        {"name": "Moon", "house": 7, "sign": "Tula"},
        {"name": "Mars", "house": 8, "sign": "Vrischika"},
        {"name": "Mercury", "house": 9, "sign": "Dhanu"},
        {"name": "Jupiter", "house": 10, "sign": "Makara"},
        {"name": "Venus", "house": 7, "sign": "Tula"},
        {"name": "Saturn", "house": 8, "sign": "Vrischika"},
    ])
    ks_padma = calculate_kaal_sarp(pmap_padma, enabled_by_default=True)
    assert ks_padma["type_name"] == "Padma Kaal Sarp"


def test_anshik_kaal_sarp():
    # Exactly one planet escapes beyond the nodal axis (e.g. Jupiter in H9 while others in H1..H6)
    pmap_anshik = make_pmap([
        {"name": "Rahu", "house": 1, "sign": "Mesha"},
        {"name": "Ketu", "house": 7, "sign": "Tula"},
        {"name": "Sun", "house": 2, "sign": "Vrishabha"},
        {"name": "Moon", "house": 3, "sign": "Mithuna"},
        {"name": "Mars", "house": 4, "sign": "Karka"},
        {"name": "Mercury", "house": 5, "sign": "Simha"},
        {"name": "Venus", "house": 6, "sign": "Kanya"},
        {"name": "Saturn", "house": 2, "sign": "Vrishabha"},
        {"name": "Jupiter", "house": 9, "sign": "Dhanu"},  # Escapes outside axis!
    ])
    res = calculate_kaal_sarp(pmap_anshik, enabled_by_default=True)
    assert res["is_anshik"] is True
    assert res["is_full"] is False
    assert "Anshik" in res["description"]


# ---------------------------------------------------------------------------
# 4. Pitru Dosha & Grahan Dosha Tests
# ---------------------------------------------------------------------------

def test_pitru_dosha_and_cancellations():
    # Positive: Rahu in 9th house
    pmap_pos = make_pmap([
        {"name": "Rahu", "house": 9, "sign": "Dhanu"},
        {"name": "Sun", "house": 2, "sign": "Vrishabha"},
    ])
    res_pos = evaluate_pitru_dosha(pmap_pos)
    assert res_pos["present"] is True
    assert "Rahu in 9th house" in res_pos["reason"]

    # Cancelled: Sun in 9th house in Simha (own sign)
    pmap_canc = make_pmap([
        {"name": "Sun", "house": 9, "sign": "Simha"},
        {"name": "Rahu", "house": 9, "sign": "Simha"},
    ])
    res_canc = evaluate_pitru_dosha(pmap_canc)
    assert res_canc["present"] is False
    assert res_canc["cancelled"] is True
    assert "own sign" in res_canc["cancellation_reason"]


def test_grahan_dosha_angular_orbs():
    # Sun and Rahu conjunct within 5° (< 12°) -> Active Surya Grahan
    pmap_active = make_pmap([
        {"name": "Sun", "house": 1, "sign": "Mesha", "degree": 10.0},
        {"name": "Rahu", "house": 1, "sign": "Mesha", "degree": 14.5},
    ])
    res_active = evaluate_grahan_dosha(pmap_active)
    assert res_active["present"] is True
    assert "Sun" in res_active["eclipsed_luminaries"]

    # Sun and Rahu in same house but separated by 20° (> 12°) -> Outside orb limit
    pmap_wide = make_pmap([
        {"name": "Sun", "house": 1, "sign": "Mesha", "degree": 2.0},
        {"name": "Rahu", "house": 1, "sign": "Mesha", "degree": 25.0},
    ])
    res_wide = evaluate_grahan_dosha(pmap_wide)
    assert res_wide["present"] is False


# ---------------------------------------------------------------------------
# 5. Gandmool Dosha & Sandhi Padas Tests
# ---------------------------------------------------------------------------

def test_gandmool_and_sandhi_padas():
    # Deep Gandanta: Ashwini Pada 1
    pmap_deep = make_pmap([
        {"name": "Moon", "house": 1, "sign": "Mesha", "nakshatra": "Ashwini", "pada": 1},
    ])
    res_deep = evaluate_gandmool_dosha(pmap_deep)
    assert res_deep["present"] is True
    assert res_deep["is_deep_gandanta"] is True
    assert res_deep["severity"] == "High"

    # Regular Gandmool: Ashwini Pada 2 (not sandhi boundary)
    pmap_reg = make_pmap([
        {"name": "Moon", "house": 1, "sign": "Mesha", "nakshatra": "Ashwini", "pada": 2},
    ])
    res_reg = evaluate_gandmool_dosha(pmap_reg)
    assert res_reg["present"] is True
    assert res_reg["is_deep_gandanta"] is False
    assert res_reg["severity"] == "Moderate"

    # Non-Gandmool: Rohini
    pmap_non = make_pmap([
        {"name": "Moon", "house": 2, "sign": "Vrishabha", "nakshatra": "Rohini", "pada": 1},
    ])
    res_non = evaluate_gandmool_dosha(pmap_non)
    assert res_non["present"] is False


# ---------------------------------------------------------------------------
# 6. Engine Entry Point (calculate_doshas) Tests
# ---------------------------------------------------------------------------

def test_calculate_doshas_full_run():
    planets = [
        {"name": "Mars", "house": 7, "sign": "Tula"},
        {"name": "Moon", "house": 1, "sign": "Mesha", "degree": 10.0, "nakshatra": "Ashwini", "pada": 1},
        {"name": "Saturn", "house": 1, "sign": "Mesha", "degree": 12.0, "retrograde": False},
        {"name": "Sun", "house": 9, "sign": "Dhanu", "degree": 15.0},
        {"name": "Rahu", "house": 9, "sign": "Dhanu", "degree": 18.0},
        {"name": "Ketu", "house": 3, "sign": "Mithuna", "degree": 18.0},
        {"name": "Jupiter", "house": 5, "sign": "Simha"},
        {"name": "Venus", "house": 2, "sign": "Vrishabha"},
        {"name": "Mercury", "house": 10, "sign": "Makara"},
    ]
    res = calculate_doshas(planets, "Mesha", {})
    assert isinstance(res, list)

    # Check that all doshas are returned with proper structure
    names = [d["name"] for d in res]
    assert "Mangal Dosha (Manglik)" in names
    assert "Shani Sade Sati" in names
    assert "Kaal Sarp Dosha" in names
    assert "Pitru Dosha" in names
    assert "Grahan Dosha" in names
    assert "Gandmool Dosha" in names

    # Sade Sati should be present (Saturn in Mesha conjunct Moon in Mesha)
    ss = find_dosha(res, "Shani Sade Sati")
    assert ss["present"] is True
    assert ss["metadata"]["phase"] == "Peak"

    # Kaal Sarp should be False by default
    ks = find_dosha(res, "Kaal Sarp Dosha")
    assert ks["present"] is False

    # Gandmool should be True (Ashwini Pada 1)
    gm = find_dosha(res, "Gandmool Dosha")
    assert gm["present"] is True
    assert gm["severity"] == "High"


# ---------------------------------------------------------------------------
# 7. Granular Tests for All 12 Kaal Sarp Types & Direction
# ---------------------------------------------------------------------------

def test_all_12_kaal_sarp_types():
    # Test each Rahu house from 1 to 12
    for h in range(1, 13):
        ketu_h = ((h + 5) % 12) + 1
        pmap = make_pmap([
            {"name": "Rahu", "house": h, "sign": "Mesha"},
            {"name": "Ketu", "house": ketu_h, "sign": "Tula"},
            {"name": "Sun", "house": h, "sign": "Mesha"},
            {"name": "Moon", "house": h, "sign": "Mesha"},
            {"name": "Mars", "house": h, "sign": "Mesha"},
            {"name": "Mercury", "house": h, "sign": "Mesha"},
            {"name": "Jupiter", "house": h, "sign": "Mesha"},
            {"name": "Venus", "house": h, "sign": "Mesha"},
            {"name": "Saturn", "house": h, "sign": "Mesha"},
        ])
        res = calculate_kaal_sarp(pmap, enabled_by_default=True)
        assert res["type_number"] == h
        assert res["type_name"] == KAAL_SARP_TYPES[h]
        assert res["is_full"] is True


def test_isolated_frame_mangal_dosha():
    # 1. Moon frame only: Mars in H3 from Lagna, but in H7 from Moon (Moon in H9, Mars in H3 -> (3-9)%12+1 = 7)
    pmap_moon = make_pmap([
        {"name": "Mars", "house": 3, "sign": "Mithuna"},
        {"name": "Moon", "house": 9, "sign": "Dhanu"},
        {"name": "Venus", "house": 1, "sign": "Mesha"},
    ])
    res_moon = evaluate_mangal_dosha_multiframe(pmap_moon)
    assert res_moon["frames"]["lagna"]["raw"] is False
    assert res_moon["frames"]["moon"]["raw"] is True
    assert res_moon["frames"]["venus"]["raw"] is False
    assert res_moon["overall_present"] is True

    # 2. Venus frame only: Mars in H3 from Lagna, Moon in H1, Venus in H8 (Mars in H8 from Venus: (3-8)%12+1 = 8)
    pmap_ven = make_pmap([
        {"name": "Mars", "house": 3, "sign": "Mithuna"},
        {"name": "Moon", "house": 1, "sign": "Mesha"},
        {"name": "Venus", "house": 8, "sign": "Vrischika"},
    ])
    res_ven = evaluate_mangal_dosha_multiframe(pmap_ven)
    assert res_ven["frames"]["lagna"]["raw"] is False
    assert res_ven["frames"]["moon"]["raw"] is False
    assert res_ven["frames"]["venus"]["raw"] is True
    assert res_ven["overall_present"] is True


def test_sade_sati_all_12_moon_houses():
    # Exhaustive verification of Saturn's house relative to natal Moon
    # Natal Moon in Mesha
    expected_phases = {
        "Meena": ("Rising", True, False, False),       # 12th from Moon
        "Mesha": ("Peak", True, False, False),         # 1st from Moon
        "Vrishabha": ("Setting", True, False, False),   # 2nd from Moon
        "Mithuna": ("None", False, False, False),      # 3rd from Moon
        "Karka": ("None", False, True, False),         # 4th from Moon -> Kantaka H4
        "Simha": ("None", False, False, False),        # 5th from Moon
        "Kanya": ("None", False, False, False),        # 6th from Moon
        "Tula": ("None", False, True, False),          # 7th from Moon -> Kantaka H7
        "Vrischika": ("None", False, False, True),     # 8th from Moon -> Ashtama
        "Dhanu": ("None", False, False, False),        # 9th from Moon
        "Makara": ("None", False, True, False),        # 10th from Moon -> Kantaka H10
        "Kumbha": ("None", False, False, False),       # 11th from Moon
    }

    for sat_sign, (exp_phase, exp_ss, exp_kantaka, exp_ashtama) in expected_phases.items():
        res = calculate_sade_sati(moon_sign="Mesha", saturn_sign=sat_sign)
        assert res["phase"] == exp_phase, f"Failed for {sat_sign}: expected phase {exp_phase}, got {res['phase']}"
        assert res["is_sade_sati"] == exp_ss, f"Failed for {sat_sign}: expected is_sade_sati={exp_ss}"
        assert res["is_kantaka_shani"] == exp_kantaka, f"Failed for {sat_sign}: expected kantaka={exp_kantaka}"
        assert res["is_ashtama_shani"] == exp_ashtama, f"Failed for {sat_sign}: expected ashtama={exp_ashtama}"


def test_chandra_grahan_orb_boundaries():
    # Moon and Ketu within 8° (< 9°) -> Chandra Grahan active
    pmap_moon_active = make_pmap([
        {"name": "Moon", "house": 4, "sign": "Karka", "degree": 10.0},
        {"name": "Ketu", "house": 4, "sign": "Karka", "degree": 17.5},
    ])
    res_active = evaluate_grahan_dosha(pmap_moon_active)
    assert res_active["present"] is True
    assert "Moon" in res_active["eclipsed_luminaries"]
    assert "Chandra Grahan" in res_active["description"]

    # Moon and Ketu separated by 15° (> 9°) -> Not active
    pmap_moon_wide = make_pmap([
        {"name": "Moon", "house": 4, "sign": "Karka", "degree": 5.0},
        {"name": "Ketu", "house": 4, "sign": "Karka", "degree": 22.0},
    ])
    res_wide = evaluate_grahan_dosha(pmap_moon_wide)
    assert res_wide["present"] is False


def test_challenges_domain_compatibility():
    # Verify that challenges.py expectations work seamlessly
    from modules.prediction.domains.challenges import analyse_challenges
    ctx = {
        "planet_map": {
            "Sun": {"house": 1, "sign": "Mesha"},
            "Moon": {"house": 2, "sign": "Vrishabha"},
            "Mars": {"house": 7, "sign": "Tula"},
            "Mercury": {"house": 1, "sign": "Mesha"},
            "Jupiter": {"house": 4, "sign": "Karka"},
            "Venus": {"house": 2, "sign": "Vrishabha"},
            "Saturn": {"house": 10, "sign": "Makara"},
            "Rahu": {"house": 1, "sign": "Mesha"},
            "Ketu": {"house": 7, "sign": "Tula"},
        },
        "house_lords": {i: "Mars" for i in range(1, 13)},
    }
    result = analyse_challenges(ctx)
    assert "domain" in result
    assert result["domain"] == "Challenges & Doshas"
    assert "score" in result
    assert "mangal_dosh" in result
    assert "sade_sati" in result
