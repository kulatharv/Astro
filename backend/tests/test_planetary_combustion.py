"""
AstroLogic AI - Issue 2: Planetary Combustion & Missing-Longitude Verification Test Suite.
Validates circular angular separation, classical combustion limits, missing data tri-state handling,
and immunity from same-house / same-sign fallbacks.
"""

import math
import pytest
from datetime import date

from shared.veda.combustion import (
    COMBUSTION_LIMITS,
    COMBUSTION_RANGES,
    CombustionStatus,
    CombustionResult,
    calculate_angular_separation,
    extract_longitude,
    extract_retrograde,
    check_combustion,
    is_combust,
    set_treat_moon_as_combust,
    get_treat_moon_as_combust,
)
from shared.veda.property import (
    _is_combust as property_is_combust,
    exc_prop_res_01,
    exc_prop_acq_01,
)
from shared.veda.marriage import evaluate_marriage_rules
from shared.veda.wealth import evaluate_wealth_rules, _exc_combust, _exc_jupiter_combust
from shared.veda.education import evaluate_education_rules
from shared.veda.progeny import evaluate_progeny_rules
from shared.veda.property import evaluate_property_rules
from shared.veda.timing_rules import evaluate_timing_rules
from modules.kundali.engine import calculate_kundali
from modules.prediction.engine import analyse_all_domains


# ---------------------------------------------------------------------------
# 1. Planet exactly at the Sun longitude (0° separation)
# ---------------------------------------------------------------------------
def test_planet_exactly_at_sun_longitude():
    """Planet at exact same degree as Sun (0° separation) is combust."""
    sun = {"longitude": 120.0}
    mars = {"longitude": 120.0}
    res = check_combustion("Mars", mars, sun)
    assert res.is_combust is True
    assert res.status == CombustionStatus.COMBUST
    assert res.separation == 0.0
    assert res.limit == 17.0
    assert is_combust("Mars", mars, sun) is True


# ---------------------------------------------------------------------------
# 2. Planet just inside the combustion limit
# ---------------------------------------------------------------------------
def test_planet_just_inside_combustion_limit():
    """Planet at 16.99° from Sun with limit 17.0° is combust."""
    sun = {"longitude": 100.0}
    mars = {"longitude": 116.99}
    res = check_combustion("Mars", mars, sun)
    assert res.is_combust is True
    assert res.status == CombustionStatus.COMBUST
    assert pytest.approx(res.separation, abs=1e-4) == 16.99
    assert is_combust("Mars", mars, sun) is True


# ---------------------------------------------------------------------------
# 3. Planet exactly at the combustion limit (Threshold Inclusivity)
# ---------------------------------------------------------------------------
def test_planet_exactly_at_combustion_limit():
    """Planet at exactly 17.0000° separation is combust (inclusive boundary)."""
    sun = {"longitude": 100.0}
    mars = {"longitude": 117.0}
    res = check_combustion("Mars", mars, sun)
    assert res.is_combust is True
    assert res.status == CombustionStatus.COMBUST
    assert pytest.approx(res.separation, abs=1e-4) == 17.0
    assert is_combust("Mars", mars, sun) is True


# ---------------------------------------------------------------------------
# 4. Planet just outside the combustion limit
# ---------------------------------------------------------------------------
def test_planet_just_outside_combustion_limit():
    """Planet at 17.01° separation with limit 17.0° is NOT combust."""
    sun = {"longitude": 100.0}
    mars = {"longitude": 117.01}
    res = check_combustion("Mars", mars, sun)
    assert res.is_combust is False
    assert res.status == CombustionStatus.NOT_COMBUST
    assert pytest.approx(res.separation, abs=1e-4) == 17.01
    assert is_combust("Mars", mars, sun) is False


# ---------------------------------------------------------------------------
# 5. Angular wraparound near 0°/360°
# ---------------------------------------------------------------------------
def test_angular_wraparound_near_0_360():
    """Sun at 358° Pisces, Planet at 5° Aries -> shortest arc is 7° (<= limit)."""
    sun = {"longitude": 358.0}
    venus = {"longitude": 5.0, "retrograde": False}
    res = check_combustion("Venus", venus, sun)
    assert res.is_combust is True
    assert pytest.approx(res.separation, abs=1e-4) == 7.0
    assert res.limit == 10.0


# ---------------------------------------------------------------------------
# 6. Separation greater than 180° before shortest-distance normalization
# ---------------------------------------------------------------------------
def test_separation_greater_than_180_normalization():
    """Sun at 10°, Jupiter at 300° -> raw diff 290°, shortest circular arc 70°."""
    sun = {"longitude": 10.0}
    jup = {"longitude": 300.0}
    res = check_combustion("Jupiter", jup, sun)
    assert res.is_combust is False
    assert pytest.approx(res.separation, abs=1e-4) == 70.0


# ---------------------------------------------------------------------------
# 7 & 8. Direct vs Retrograde Mercury limits (14° vs 12°)
# ---------------------------------------------------------------------------
def test_mercury_direct_limit():
    """Mercury direct has limit 14°: at 13° combust, at 15° not combust."""
    sun = {"longitude": 50.0}
    # Direct at 13° separation (combust)
    m_direct_in = {"longitude": 63.0, "retrograde": False}
    res_in = check_combustion("Mercury", m_direct_in, sun)
    assert res_in.is_combust is True
    assert res_in.limit == 14.0

    # Direct at 14.5° separation (not combust)
    m_direct_out = {"longitude": 64.5, "retrograde": False}
    res_out = check_combustion("Mercury", m_direct_out, sun)
    assert res_out.is_combust is False
    assert res_out.limit == 14.0


def test_mercury_retrograde_limit():
    """Mercury retrograde has narrower limit 12°: at 13° NOT combust, at 11° combust."""
    sun = {"longitude": 50.0}
    # Retrograde at 13° separation (in direct orb but outside retro orb -> NOT combust)
    m_retro_out = {"longitude": 63.0, "retrograde": True}
    res_out = check_combustion("Mercury", m_retro_out, sun)
    assert res_out.is_combust is False
    assert res_out.limit == 12.0

    # Retrograde at 11° separation (combust)
    m_retro_in = {"longitude": 61.0, "retrograde": True}
    res_in = check_combustion("Mercury", m_retro_in, sun)
    assert res_in.is_combust is True
    assert res_in.limit == 12.0


# ---------------------------------------------------------------------------
# 9 & 10. Direct vs Retrograde Venus limits (10° vs 8°)
# ---------------------------------------------------------------------------
def test_venus_direct_limit():
    """Venus direct has limit 10°: at 9° combust, at 11° not combust."""
    sun = {"longitude": 200.0}
    v_dir_in = {"longitude": 209.0, "retrograde": False}
    assert check_combustion("Venus", v_dir_in, sun).is_combust is True

    v_dir_out = {"longitude": 211.0, "retrograde": False}
    assert check_combustion("Venus", v_dir_out, sun).is_combust is False


def test_venus_retrograde_limit():
    """Venus retrograde has narrower limit 8°: at 9° NOT combust, at 7° combust."""
    sun = {"longitude": 200.0}
    # 9° separation is combust if direct, but NOT combust if retrograde
    v_ret_out = {"longitude": 209.0, "retrograde": True}
    res_out = check_combustion("Venus", v_ret_out, sun)
    assert res_out.is_combust is False
    assert res_out.limit == 8.0

    # 7° separation is combust
    v_ret_in = {"longitude": 207.0, "retrograde": True}
    res_in = check_combustion("Venus", v_ret_in, sun)
    assert res_in.is_combust is True
    assert res_in.limit == 8.0


# ---------------------------------------------------------------------------
# 11. Missing Sun longitude handling
# ---------------------------------------------------------------------------
def test_missing_sun_longitude():
    """When Sun longitude is missing/empty/None, result must be Unknown (None). Never False."""
    pdata = {"longitude": 45.0}

    assert is_combust("Mars", pdata, None) is None
    assert is_combust("Mars", pdata, {}) is None
    assert is_combust("Mars", pdata, {"longitude": None}) is None

    res = check_combustion("Mars", pdata, {})
    assert res.is_combust is None
    assert res.status == CombustionStatus.UNKNOWN
    assert "Sun longitude is missing" in res.reason


# ---------------------------------------------------------------------------
# 12. Missing planet longitude handling
# ---------------------------------------------------------------------------
def test_missing_planet_longitude():
    """When planet longitude is missing/empty/None, result must be Unknown (None). Never False."""
    sun = {"longitude": 45.0}

    assert is_combust("Jupiter", None, sun) is None
    assert is_combust("Jupiter", {}, sun) is None
    assert is_combust("Jupiter", {"longitude": None}, sun) is None

    res = check_combustion("Jupiter", {}, sun)
    assert res.is_combust is None
    assert res.status == CombustionStatus.UNKNOWN
    assert "Jupiter longitude is missing" in res.reason


# ---------------------------------------------------------------------------
# 13. Missing retrograde state handling
# ---------------------------------------------------------------------------
def test_missing_retrograde_state_policy():
    """
    For Mercury/Venus, if retrograde is unknown:
    - Below min_orb: Combust (True)
    - Above max_orb: Not Combust (False)
    - Between min_orb and max_orb: Unknown (None)
    """
    sun = {"longitude": 100.0}

    # Case A: Venus at 6° separation (<= 8° min orb) -> Combust True even with unknown retrograde
    v_close = {"longitude": 106.0}  # No retrograde key
    res_close = check_combustion("Venus", v_close, sun)
    assert res_close.is_combust is True
    assert res_close.status == CombustionStatus.COMBUST

    # Case B: Venus at 15° separation (> 10° max orb) -> Not Combust False
    v_far = {"longitude": 115.0}
    res_far = check_combustion("Venus", v_far, sun)
    assert res_far.is_combust is False
    assert res_far.status == CombustionStatus.NOT_COMBUST

    # Case C: Venus at 9° separation (between 8° and 10°) -> Unknown None!
    v_ambiguous = {"longitude": 109.0}
    res_amb = check_combustion("Venus", v_ambiguous, sun)
    assert res_amb.is_combust is None
    assert res_amb.status == CombustionStatus.UNKNOWN
    assert "Retrograde state is unknown" in res_amb.reason


# ---------------------------------------------------------------------------
# 14. NaN and Infinity inputs
# ---------------------------------------------------------------------------
def test_nan_and_infinity_inputs():
    """NaN and Inf in Sun or planet coordinates must return Unknown (None)."""
    sun_good = {"longitude": 150.0}
    p_good = {"longitude": 155.0}

    # Planet has NaN
    assert is_combust("Saturn", {"longitude": float("nan")}, sun_good) is None
    # Sun has NaN
    assert is_combust("Saturn", p_good, {"longitude": float("nan")}) is None

    # Planet has Infinity
    assert is_combust("Saturn", {"longitude": float("inf")}, sun_good) is None
    # Sun has -Infinity
    assert is_combust("Saturn", p_good, {"longitude": float("-inf")}) is None


# ---------------------------------------------------------------------------
# 15. Invalid longitude strings
# ---------------------------------------------------------------------------
def test_invalid_longitude_strings():
    """Invalid string coordinates return Unknown (None). Valid DMS strings parse correctly."""
    sun = {"longitude": "150.0"}
    p_bad_str = {"longitude": "unknown_coordinate"}

    assert is_combust("Jupiter", p_bad_str, sun) is None
    assert is_combust("Jupiter", {"longitude": ""}, sun) is None

    # Valid DMS string parses cleanly
    p_dms = {"longitude": "152°30'"}
    res = check_combustion("Jupiter", p_dms, sun)
    assert res.is_combust is True
    assert pytest.approx(res.separation, abs=1e-3) == 2.5


# ---------------------------------------------------------------------------
# 16. Longitudes outside the expected range [0, 360)
# ---------------------------------------------------------------------------
def test_longitudes_outside_expected_range():
    """Unnormalized negative or > 360 values return Unknown (None) under strict range check."""
    sun = {"longitude": 100.0}

    assert is_combust("Mars", {"longitude": -15.0}, sun) is None
    assert is_combust("Mars", {"longitude": 385.0}, sun) is None
    assert is_combust("Mars", {"longitude": 999.0}, sun) is None
    assert is_combust("Mars", {"longitude": 105.0}, {"longitude": -5.0}) is None


# ---------------------------------------------------------------------------
# 17. No same-house fallback
# ---------------------------------------------------------------------------
def test_no_same_house_fallback():
    """
    CRITICAL: When coordinates are missing, sharing the same house MUST NOT
    silently cause the planet to be marked combust. It must return Unknown (None).
    """
    sun_house_only = {"house": 5}
    mercury_house_only = {"house": 5, "retrograde": False}

    res = check_combustion("Mercury", mercury_house_only, sun_house_only)
    assert res.is_combust is None
    assert res.status == CombustionStatus.UNKNOWN
    assert is_combust("Mercury", mercury_house_only, sun_house_only) is None


# ---------------------------------------------------------------------------
# 18. No same-sign fallback / Across-sign boundary combustion
# ---------------------------------------------------------------------------
def test_no_same_sign_fallback_and_cross_sign_combustion():
    """
    Planets in adjacent signs with small angular distance ARE combust.
    Sun at 29° Leo (149°), Mars at 1° Virgo (151°) -> separation 2° -> Combust!
    """
    sun_leo = {"sign": "Simha", "degree_decimal": 29.0}  # 149°
    mars_virgo = {"sign": "Kanya", "degree_decimal": 1.0}  # 151°

    res = check_combustion("Mars", mars_virgo, sun_leo)
    assert res.is_combust is True
    assert pytest.approx(res.separation, abs=1e-4) == 2.0
    assert res.limit == 17.0


# ---------------------------------------------------------------------------
# 19. All domain rule callers handle unknown results gracefully
# ---------------------------------------------------------------------------
def test_domain_rule_callers_handle_unknown_without_false_cancellation():
    """
    Verify that domain rule exceptions do NOT fire when combustion is Unknown.
    """
    # Base chart with Sun longitude missing in planet_map
    ctx_unknown = {
        "lagna": "Mesha",
        "planet_map": {
            "Sun": {"house": 4},  # No longitude
            "Moon": {"sign": "Karka", "house": 4, "degree": 10.0},  # 4th lord
            "Mercury": {"sign": "Kanya", "house": 6, "degree": 15.0},
            "Jupiter": {"sign": "Karka", "house": 4, "degree": 5.0},
            "Venus": {"sign": "Meena", "house": 12, "degree": 2.0},
            "Mars": {"sign": "Makara", "house": 10, "degree": 28.0},
            "Saturn": {"sign": "Tula", "house": 7, "degree": 20.0},
        },
        "house_lords": {4: "Moon", 5: "Sun", 7: "Venus", 9: "Jupiter"},
    }

    # Education: H4 lord Kendra rule must NOT be cancelled when combustion is unknown
    edu_res = evaluate_education_rules(ctx_unknown)
    matched_edu = [r["rule_id"] for r in edu_res["matched_rules"]]
    cancelled_edu = [r["rule_id"] for r in edu_res["cancelled_rules"]]
    assert "EDU-H4-LORD-KENDRA-TRIKONA-01" in matched_edu
    assert "EDU-H4-LORD-KENDRA-TRIKONA-01" not in cancelled_edu

    # Wealth: H2 lord or Jupiter rules must NOT fire deep combustion exception on missing data
    wealth_res = evaluate_wealth_rules(ctx_unknown)
    cancelled_wealth = [r["rule_id"] for r in wealth_res["cancelled_rules"]]
    assert "WEALTH-H2-LORD-KENDRA-TRIKONA-01" not in cancelled_wealth


# ---------------------------------------------------------------------------
# 20. Regression test for complete Kundali and Prediction outputs
# ---------------------------------------------------------------------------
def test_kundali_and_prediction_output_regression():
    """
    Full end-to-end calculation of reference benchmark chart (New Delhi 1995-08-15 14:30 IST).
    Sun is in Leo (Simha ~22°04'). Venus is at ~20°31' Leo -> combust within 1.5°!
    """
    chart = calculate_kundali(
        year=1995,
        month=8,
        day=15,
        hour=14,
        minute=30,
        lat=28.6139,
        lon=77.2090,
    )

    planets = {p["name"]: p for p in chart["planets"]}
    sun = planets["Sun"]
    venus = planets["Venus"]
    mars = planets["Mars"]

    # Venus and Sun are both in Simha separated by ~1.5° -> Venus is combust
    assert venus["is_combust"] is True
    # Mars is in Libra (~195°) while Sun is in Leo (~142°) -> ~53° separation -> Mars is NOT combust
    assert mars["is_combust"] is False
    # Sun and Rahu/Ketu are not combust
    assert sun["is_combust"] is False
    assert planets["Rahu"]["is_combust"] is False
    assert planets["Ketu"]["is_combust"] is False

    # Run domain predictions
    prediction_result = analyse_all_domains(chart)
    assert "domains" in prediction_result
    assert "marriage" in prediction_result["domains"]
    assert "career" in prediction_result["domains"]
    assert "wealth" in prediction_result["domains"]


# ---------------------------------------------------------------------------
# 21. Moon 12° setting/Amavasya toggle (Issue 2.1)
# ---------------------------------------------------------------------------
def test_moon_combustion_toggle():
    """
    Verify Moon combustion handling under both TREAT_MOON_AS_COMBUST settings:
    - When True: Moon <= 12° from Sun is combust (Surya Siddhanta Ch. X, v. 1).
    - When False: Moon <= 12° is reported as non-combust with Amavasya explanation.
    """
    sun = {"longitude": 100.0}
    moon_close = {"longitude": 108.0}  # 8° separation (<= 12°)
    moon_far = {"longitude": 120.0}    # 20° separation (> 12°)

    try:
        # 1. Toggle ENABLED (default)
        set_treat_moon_as_combust(True)
        assert get_treat_moon_as_combust() is True

        res_close = check_combustion("Moon", moon_close, sun)
        assert res_close.is_combust is True
        assert res_close.status == CombustionStatus.COMBUST
        assert res_close.separation == 8.0
        assert res_close.limit == 12.0
        assert "Amavasya" in res_close.reason

        res_far = check_combustion("Moon", moon_far, sun)
        assert res_far.is_combust is False
        assert res_far.status == CombustionStatus.NOT_COMBUST
        assert res_far.separation == 20.0

        # 2. Toggle DISABLED
        set_treat_moon_as_combust(False)
        assert get_treat_moon_as_combust() is False

        res_close_disabled = check_combustion("Moon", moon_close, sun)
        assert res_close_disabled.is_combust is False
        assert res_close_disabled.status == CombustionStatus.NOT_COMBUST
        assert res_close_disabled.separation == 8.0
        assert "Amavasya / Kshina Chandra" in res_close_disabled.reason
        assert "TREAT_MOON_AS_COMBUST=False" in res_close_disabled.reason

    finally:
        # Always restore default
        set_treat_moon_as_combust(True)


# ---------------------------------------------------------------------------
# 22. Tri-state consumer safety (Issue 2.1)
# ---------------------------------------------------------------------------
def test_consumer_safety_unknown_handling():
    """
    Verify that consumers never interpret Unknown (None) as False or True.
    A missing longitude must return None, and caller checks:
    - 'is True' -> False
    - 'is False' -> False
    - 'is None' -> True
    """
    sun_missing = {"sign": "Mesha"}  # No degree or longitude
    mars_valid = {"longitude": 15.0}

    res = check_combustion("Mars", mars_valid, sun_missing)
    assert res.is_combust is None
    assert res.status == CombustionStatus.UNKNOWN

    raw_cb = is_combust("Mars", mars_valid, sun_missing)
    assert raw_cb is None

    # Consumer safety checks:
    # 1. Must NOT trigger combustion branch
    assert (raw_cb is True) is False
    # 2. Must NOT trigger non-combustion branch
    assert (raw_cb is False) is False
    # 3. Must be identifiable as unknown/unverifiable
    assert (raw_cb is None) is True


# ---------------------------------------------------------------------------
# 23. Property module tri-state consumer safety (Issue 2.1)
# ---------------------------------------------------------------------------
def test_property_module_consumer_safety():
    """
    Verify property module _is_combust returns Optional[bool] and exceptions
    never fire when longitude data is missing/invalid.
    """
    # Context with Sun missing longitude
    ctx_missing_sun = {
        "lagna": "Mesha",
        "planet_map": {
            "Sun": {"house": 1},  # Missing longitude
            "Mars": {"house": 4, "longitude": 100.0, "sign": "Karka"},
            "Moon": {"house": 4, "longitude": 105.0, "sign": "Karka"},
        },
        "house_lords": {4: "Moon"},
    }

    # _is_combust must return None, not True and not False
    cb_result = property_is_combust(ctx_missing_sun, "Mars")
    assert cb_result is None

    # Exception rules return None when coordinates are missing, preserving unknown state
    fired_res, msg = exc_prop_res_01(ctx_missing_sun, {})
    assert fired_res is None
    assert "unknown" in msg
    assert (fired_res is True) is False

    fired_acq, msg = exc_prop_acq_01(ctx_missing_sun, {})
    assert fired_acq is None
    assert "unknown" in msg
    assert (fired_acq is True) is False

    # When Sun has valid longitude and Mars is combust
    ctx_combust = {
        "lagna": "Mesha",
        "planet_map": {
            "Sun": {"house": 4, "longitude": 102.0},
            "Mars": {"house": 4, "longitude": 105.0, "sign": "Karka"},
            "Moon": {"house": 4, "longitude": 103.0, "sign": "Karka"},
        },
        "house_lords": {4: "Moon"},
    }
    assert property_is_combust(ctx_combust, "Mars") is True
    fired_res, msg = exc_prop_res_01(ctx_combust, {})
    assert fired_res is True
    assert "combust" in msg

    fired_acq, msg = exc_prop_acq_01(ctx_combust, {})
    assert fired_acq is True
    assert "Mars is combust" in msg


# ---------------------------------------------------------------------------
# 24. Wealth combustion exception with missing Sun longitude (Issue 2.2)
# ---------------------------------------------------------------------------
def test_wealth_combustion_exception_missing_sun_longitude():
    """
    1. Wealth combustion exception with missing Sun longitude returns None,
    preserving tri-state unknown instead of converting to False.
    """
    ctx = {"lagna": "Mesha"}
    pmap = {
        "Sun": {"sign": "Mesha"},  # Missing degree and longitude
        "Venus": {"sign": "Vrishabha", "degree": 15.0, "longitude": 45.0},
    }
    c_fired, c_reason = _exc_combust(ctx, pmap, "Venus", orb=3.0)
    assert c_fired is None
    assert "Missing or invalid longitude coordinates for Sun" in c_reason


# ---------------------------------------------------------------------------
# 25. Wealth combustion exception with missing planet longitude (Issue 2.2)
# ---------------------------------------------------------------------------
def test_wealth_combustion_exception_missing_planet_longitude():
    """
    2. Wealth combustion exception with missing planet longitude returns None,
    preserving tri-state unknown instead of converting to False.
    """
    ctx = {"lagna": "Mesha"}
    pmap = {
        "Sun": {"sign": "Mesha", "degree": 10.0, "longitude": 10.0},
        "Venus": {"sign": "Vrishabha"},  # Missing degree and longitude
    }
    c_fired, c_reason = _exc_combust(ctx, pmap, "Venus", orb=3.0)
    assert c_fired is None
    assert "Missing or invalid longitude coordinates for Venus" in c_reason


# ---------------------------------------------------------------------------
# 26. Wealth combustion exception with invalid coordinates (Issue 2.2)
# ---------------------------------------------------------------------------
def test_wealth_combustion_exception_invalid_coordinates():
    """
    3. Wealth combustion exception with invalid coordinates (out-of-range, NaN, empty string)
    returns None.
    """
    ctx = {"lagna": "Mesha"}
    pmap_nan = {
        "Sun": {"longitude": float("nan")},
        "Jupiter": {"longitude": 100.0},
    }
    c_fired, c_reason = _exc_jupiter_combust(ctx, pmap_nan)
    assert c_fired is None
    assert "Missing or invalid longitude coordinates" in c_reason

    pmap_bad_str = {
        "Sun": {"longitude": 50.0},
        "Jupiter": {"longitude": "invalid_deg"},
    }
    c_fired2, c_reason2 = _exc_jupiter_combust(ctx, pmap_bad_str)
    assert c_fired2 is None
    assert "Missing or invalid longitude coordinates" in c_reason2


# ---------------------------------------------------------------------------
# 27. Confirmed combust behavior remains unchanged (Issue 2.2)
# ---------------------------------------------------------------------------
def test_wealth_combustion_confirmed_combust_unchanged():
    """
    4. Confirmed combust behavior remains unchanged: returns True and provides explanation.
    """
    ctx = {"lagna": "Mesha"}
    # Sun at 40°, Venus at 42° -> sep 2.0° <= 3.0°
    pmap = {
        "Sun": {"longitude": 40.0, "sign": "Vrishabha", "house": 2},
        "Venus": {"longitude": 42.0, "sign": "Vrishabha", "house": 2, "degree": 12.0},
    }
    c_fired, c_reason = _exc_combust(ctx, pmap, "Venus", orb=3.0)
    assert c_fired is True
    assert "deeply combust by Sun within 3.0°" in c_reason

    # Jupiter exception with orb 11.0:
    # Sun at 100°, Jupiter at 105° -> sep 5.0° <= 11.0°
    pmap_jup = {
        "Sun": {"longitude": 100.0},
        "Jupiter": {"longitude": 105.0},
    }
    jup_fired, jup_reason = _exc_jupiter_combust(ctx, pmap_jup)
    assert jup_fired is True
    assert "deeply combust" in jup_reason


# ---------------------------------------------------------------------------
# 28. Confirmed non-combust behavior remains unchanged (Issue 2.2)
# ---------------------------------------------------------------------------
def test_wealth_combustion_confirmed_non_combust_unchanged():
    """
    5. Confirmed non-combust behavior remains unchanged: returns False.
    """
    ctx = {"lagna": "Mesha"}
    # Sun at 40°, Venus at 70° -> sep 30.0° > 3.0°
    pmap = {
        "Sun": {"longitude": 40.0, "sign": "Vrishabha", "house": 2},
        "Venus": {"longitude": 70.0, "sign": "Mithuna", "house": 3, "degree": 10.0},
    }
    c_fired, c_reason = _exc_combust(ctx, pmap, "Venus", orb=3.0)
    assert c_fired is False
    assert "free from deep combustion" in c_reason

    # Non-combustible bodies (Sun, Rahu, Ketu)
    c_sun, _ = _exc_combust(ctx, pmap, "Sun", orb=3.0)
    assert c_sun is False
    c_rahu, _ = _exc_combust(ctx, pmap, "Rahu", orb=3.0)
    assert c_rahu is False


# ---------------------------------------------------------------------------
# 29. Unknown combustion does not cancel an otherwise valid wealth rule (Issue 2.2)
# ---------------------------------------------------------------------------
def test_wealth_unknown_combustion_does_not_cancel_rule():
    """
    6. Unknown combustion does not cancel an otherwise valid wealth rule.
    2nd lord in Kendra/Trikona (WEALTH-H2-LORD-KENDRA-TRIKONA-01) matches and is NOT cancelled.
    """
    ctx = {
        "lagna": "Mesha",
        "planet_map": {
            "Sun": {"house": 1},  # Missing longitude
            "Venus": {"sign": "Karka", "house": 4, "degree": 15.0},  # 2nd lord in 4th house Kendra
            "Moon": {"sign": "Karka", "house": 4, "degree": 10.0},
            "Mars": {"sign": "Makara", "house": 10, "degree": 28.0},
            "Mercury": {"sign": "Mithuna", "house": 3, "degree": 14.0},
            "Jupiter": {"sign": "Dhanu", "house": 9, "degree": 16.0},
            "Saturn": {"sign": "Makara", "house": 10, "degree": 5.0},
            "Rahu": {"sign": "Kumbha", "house": 11, "degree": 22.0},
            "Ketu": {"sign": "Simha", "house": 5, "degree": 22.0},
        },
        "house_signs": {1: "Mesha", 2: "Vrishabha", 3: "Mithuna", 4: "Karka", 5: "Simha", 6: "Kanya",
                        7: "Tula", 8: "Vrischika", 9: "Dhanu", 10: "Makara", 11: "Kumbha", 12: "Meena"},
        "house_lords": {1: "Mars", 2: "Venus", 3: "Mercury", 4: "Moon", 5: "Sun", 6: "Mercury",
                        7: "Venus", 8: "Mars", 9: "Jupiter", 10: "Saturn", 11: "Saturn", 12: "Jupiter"},
    }
    res = evaluate_wealth_rules(ctx)
    matched_ids = [m["rule_id"] for m in res["matched_rules"]]
    cancelled_ids = [c["rule_id"] for c in res["cancelled_rules"]]

    # Positive rule must be MATCHED, not cancelled
    assert "WEALTH-H2-LORD-KENDRA-TRIKONA-01" in matched_ids
    assert "WEALTH-H2-LORD-KENDRA-TRIKONA-01" not in cancelled_ids


# ---------------------------------------------------------------------------
# 30. Unknown combustion remains distinguishable from confirmed non-combust (Issue 2.2)
# ---------------------------------------------------------------------------
def test_wealth_unknown_combustion_distinguishable_in_result_and_context():
    """
    7. Unknown combustion remains distinguishable from confirmed non-combust
    in the returned result and context via 'unverified_exceptions'.
    """
    # Context A: Sun missing longitude -> unknown combustion
    ctx_unknown = {
        "lagna": "Mesha",
        "planet_map": {
            "Sun": {"house": 1},  # Missing longitude
            "Venus": {"sign": "Karka", "house": 4, "degree": 15.0},
            "Moon": {"sign": "Karka", "house": 4, "degree": 10.0},
            "Mars": {"sign": "Makara", "house": 10, "degree": 28.0},
            "Mercury": {"sign": "Mithuna", "house": 3, "degree": 14.0},
            "Jupiter": {"sign": "Dhanu", "house": 9, "degree": 16.0},
            "Saturn": {"sign": "Makara", "house": 10, "degree": 5.0},
            "Rahu": {"sign": "Kumbha", "house": 11, "degree": 22.0},
            "Ketu": {"sign": "Simha", "house": 5, "degree": 22.0},
        },
        "house_signs": {1: "Mesha", 2: "Vrishabha", 3: "Mithuna", 4: "Karka", 5: "Simha", 6: "Kanya",
                        7: "Tula", 8: "Vrischika", 9: "Dhanu", 10: "Makara", 11: "Kumbha", 12: "Meena"},
        "house_lords": {1: "Mars", 2: "Venus", 3: "Mercury", 4: "Moon", 5: "Sun", 6: "Mercury",
                        7: "Venus", 8: "Mars", 9: "Jupiter", 10: "Saturn", 11: "Saturn", 12: "Jupiter"},
    }
    res_unknown = evaluate_wealth_rules(ctx_unknown)
    assert "unverified_exceptions" in res_unknown
    assert len(res_unknown["unverified_exceptions"]) > 0
    assert any("Sun" in u["reason"] for u in res_unknown["unverified_exceptions"])
    assert "unverified_exceptions" in ctx_unknown

    # Context B: Sun with confirmed separated longitude -> confirmed non-combust
    ctx_confirmed = {
        "lagna": "Mesha",
        "planet_map": {
            "Sun": {"house": 1, "longitude": 10.0},  # Confirmed longitude (65° away from Venus 75°)
            "Venus": {"sign": "Karka", "house": 4, "degree": 15.0, "longitude": 105.0},
            "Moon": {"sign": "Karka", "house": 4, "degree": 10.0},
            "Mars": {"sign": "Makara", "house": 10, "degree": 28.0},
            "Mercury": {"sign": "Mithuna", "house": 3, "degree": 14.0},
            "Jupiter": {"sign": "Dhanu", "house": 9, "degree": 16.0, "longitude": 256.0},
            "Saturn": {"sign": "Makara", "house": 10, "degree": 5.0},
            "Rahu": {"sign": "Kumbha", "house": 11, "degree": 22.0},
            "Ketu": {"sign": "Simha", "house": 5, "degree": 22.0},
        },
        "house_signs": {1: "Mesha", 2: "Vrishabha", 3: "Mithuna", 4: "Karka", 5: "Simha", 6: "Kanya",
                        7: "Tula", 8: "Vrischika", 9: "Dhanu", 10: "Makara", 11: "Kumbha", 12: "Meena"},
        "house_lords": {1: "Mars", 2: "Venus", 3: "Mercury", 4: "Moon", 5: "Sun", 6: "Mercury",
                        7: "Venus", 8: "Mars", 9: "Jupiter", 10: "Saturn", 11: "Saturn", 12: "Jupiter"},
    }
    res_confirmed = evaluate_wealth_rules(ctx_confirmed)
    assert res_confirmed["unverified_exceptions"] == []


# ---------------------------------------------------------------------------
# 31. Education unknown-state visibility (Issue 2.3)
# ---------------------------------------------------------------------------
def test_education_unknown_combustion_visibility():
    """
    Verify that education evaluation exposes unverified_exceptions when Sun longitude is missing,
    and positive rules match without being cancelled.
    """
    ctx = {
        "lagna": "Mesha",
        "planet_map": {
            "Sun": {"house": 1},  # Missing longitude
            "Moon": {"sign": "Karka", "house": 4, "degree": 10.0},  # 4th lord
            "Mercury": {"sign": "Kanya", "house": 6, "degree": 15.0},
            "Jupiter": {"sign": "Karka", "house": 4, "degree": 5.0},
            "Venus": {"sign": "Meena", "house": 12, "degree": 2.0},
            "Mars": {"sign": "Makara", "house": 10, "degree": 28.0},
            "Saturn": {"sign": "Tula", "house": 7, "degree": 20.0},
        },
        "house_lords": {4: "Moon", 5: "Sun", 7: "Venus", 9: "Jupiter"},
    }
    res = evaluate_education_rules(ctx)
    assert "unverified_exceptions" in res
    assert len(res["unverified_exceptions"]) > 0
    matched_ids = [r["rule_id"] for r in res["matched_rules"]]
    assert "EDU-H4-LORD-KENDRA-TRIKONA-01" in matched_ids
    # Rule record preserves unverified_exceptions annotation
    h4_rec = next(r for r in res["matched_rules"] if r["rule_id"] == "EDU-H4-LORD-KENDRA-TRIKONA-01")
    assert "unverified_exceptions" in h4_rec


# ---------------------------------------------------------------------------
# 32. Progeny unknown-state visibility (Issue 2.3)
# ---------------------------------------------------------------------------
def test_progeny_unknown_combustion_visibility():
    """
    Verify that progeny evaluation exposes unverified_exceptions when Sun longitude is missing,
    and positive rules match without being cancelled.
    """
    ctx = {
        "lagna": "Mesha",
        "planet_map": {
            "Sun": {"house": 1},  # Missing longitude
            "Jupiter": {"sign": "Dhanu", "house": 9, "degree": 16.0},
            "Mars": {"sign": "Simha", "house": 5, "degree": 12.0},
            "Moon": {"sign": "Karka", "house": 4, "degree": 10.0},
            "Venus": {"sign": "Meena", "house": 12, "degree": 2.0},
            "Saturn": {"sign": "Makara", "house": 10, "degree": 5.0},
            "Mercury": {"sign": "Mithuna", "house": 3, "degree": 14.0},
        },
        "house_lords": {1: "Mars", 5: "Sun", 9: "Jupiter"},
    }
    res = evaluate_progeny_rules(ctx)
    assert "unverified_exceptions" in res


# ---------------------------------------------------------------------------
# 33. Property unknown-state visibility (Issue 2.3)
# ---------------------------------------------------------------------------
def test_property_unknown_combustion_visibility():
    """
    Verify that property evaluation exposes unverified_exceptions when Sun longitude is missing,
    and positive rules match without being cancelled.
    """
    ctx = {
        "lagna": "Mesha",
        "planet_map": {
            "Sun": {"house": 1},  # Missing longitude
            "Mars": {"sign": "Makara", "house": 10, "degree": 28.0},  # Exalted in Kendra (H10)
            "Moon": {"sign": "Karka", "house": 4, "degree": 12.0},   # 4th lord in own sign (H4)
            "Mercury": {"sign": "Mithuna", "house": 3, "degree": 14.0},
            "Jupiter": {"sign": "Dhanu", "house": 9, "degree": 16.0},
            "Venus": {"sign": "Vrishabha", "house": 2, "degree": 20.0},
            "Saturn": {"sign": "Makara", "house": 10, "degree": 5.0},
            "Rahu": {"sign": "Kumbha", "house": 11, "degree": 22.0},
            "Ketu": {"sign": "Simha", "house": 5, "degree": 22.0},
        },
        "house_signs": {1: "Mesha", 2: "Vrishabha", 3: "Mithuna", 4: "Karka", 5: "Simha", 6: "Kanya",
                        7: "Tula", 8: "Vrischika", 9: "Dhanu", 10: "Makara", 11: "Kumbha", 12: "Meena"},
        "house_lords": {1: "Mars", 2: "Venus", 3: "Mercury", 4: "Moon", 5: "Sun", 6: "Mercury",
                        7: "Venus", 8: "Mars", 9: "Jupiter", 10: "Saturn", 11: "Saturn", 12: "Jupiter"},
    }
    res = evaluate_property_rules(ctx)
    assert "unverified_exceptions" in res
    assert len(res["unverified_exceptions"]) > 0
    # PROP-RES-01 (4th lord Moon in own sign) must match
    active_ids = [e["rule_id"] for e in res["evidence_ledger"] if e.get("effect") == "SUPPORTS"]
    assert "PROP-RES-01" in active_ids



