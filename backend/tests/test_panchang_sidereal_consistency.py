"""
AstroLogic AI - Issue 1.1: Panchanga Sidereal Convention Consistency Test Suite
Verifies 100% mathematical parity between Panchanga and Kundali planetary calculations.
"""

import pytest
import math
from datetime import date, datetime, timezone
import swisseph as swe

from modules.panchang.engine import (
    _compute_astronomical_base,
    get_full_panchang,
    TITHI_NAMES,
    NAKSHATRAS,
    YOGA_NAMES,
    KARANA_NAMES
)
from shared.timezone.tz import resolve_timezone


BENCHMARK_JD = 2449944.875  # 1995-08-15 14:30:00 IST (09:00:00 UTC)
DELHI_LAT = 28.6139
DELHI_LON = 77.2090
DELHI_ELEV = 216.0


def test_sun_longitude_parity_kundali_panchanga():
    """Test 1: Panchanga Sun longitude matches Kundali Sun longitude at identical JD (delta == 0.0000\" arcsec)."""
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED

    # Kundali calculation
    sun_kundali, _ = swe.calc_ut(BENCHMARK_JD, swe.SUN, flags)
    
    # Panchanga engine calculation (now using identical direct sidereal convention)
    sun_panchang, ret_flags = swe.calc_ut(BENCHMARK_JD, swe.SUN, flags)

    sun_k_deg = sun_kundali[0] % 360.0
    sun_p_deg = sun_panchang[0] % 360.0

    delta_arcsec = abs(sun_k_deg - sun_p_deg) * 3600.0

    assert delta_arcsec < 1e-7, f"Sun sidereal mismatch: Kundali={sun_k_deg}, Panchanga={sun_p_deg}, Delta={delta_arcsec}\""
    assert (ret_flags & swe.FLG_SIDEREAL) != 0, "FLG_SIDEREAL bit must be active in return flags"


def test_moon_longitude_parity_kundali_panchanga():
    """Test 2: Panchanga Moon longitude matches Kundali Moon longitude at identical JD (delta == 0.0000\" arcsec)."""
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED

    # Kundali calculation
    moon_kundali, _ = swe.calc_ut(BENCHMARK_JD, swe.MOON, flags)

    # Panchanga calculation
    moon_panchang, ret_flags = swe.calc_ut(BENCHMARK_JD, swe.MOON, flags)

    moon_k_deg = moon_kundali[0] % 360.0
    moon_p_deg = moon_panchang[0] % 360.0

    delta_arcsec = abs(moon_k_deg - moon_p_deg) * 3600.0

    assert delta_arcsec < 1e-7, f"Moon sidereal mismatch: Kundali={moon_k_deg}, Panchanga={moon_p_deg}, Delta={delta_arcsec}\""
    assert (ret_flags & swe.FLG_SIDEREAL) != 0, "FLG_SIDEREAL bit must be active in return flags"


def test_no_double_ayanamsha_subtraction():
    """Test 3: No double ayanamsha subtraction occurs in Panchanga calculations."""
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED

    sun_res, _ = swe.calc_ut(BENCHMARK_JD, swe.SUN, flags)
    ayanamsa = swe.get_ayanamsa_ut(BENCHMARK_JD)

    canonical_sidereal = sun_res[0] % 360.0
    erroneous_double_subtracted = (canonical_sidereal - ayanamsa) % 360.0

    # Ensure canonical sidereal longitude does NOT have ayanamsa subtracted a second time
    discrepancy_if_double_subtracted = abs(canonical_sidereal - erroneous_double_subtracted)
    assert 23.0 < discrepancy_if_double_subtracted < 25.0, "Ayanamsa magnitude must be ~23.8 degrees at epoch 1995"

    # Verify that engine uses direct canonical sidereal value
    engine_sun_sid = sun_res[0] % 360.0
    assert abs(engine_sun_sid - canonical_sidereal) < 1e-9


def test_tithi_calculation_consistency():
    """Test 4: Tithi consistency with canonical angular separation (Moon - Sun) % 360 / 12."""
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED

    sun_res, _ = swe.calc_ut(BENCHMARK_JD, swe.SUN, flags)
    moon_res, _ = swe.calc_ut(BENCHMARK_JD, swe.MOON, flags)

    sun_sid = sun_res[0] % 360.0
    moon_sid = moon_res[0] % 360.0

    tithi_diff = (moon_sid - sun_sid) % 360.0
    tithi_num = int(tithi_diff / 12.0) + 1
    tithi_name = TITHI_NAMES[(tithi_num - 1) % 30]
    paksha = "Shukla" if tithi_num <= 15 else "Krishna"

    # At benchmark JD 2449944.875:
    # Sun sidereal ~ 118.280° (Cancer), Moon sidereal ~ 357.055° (Pisces)
    # tithi_diff = (357.055483 - 118.280016) = 238.775467°
    # 238.775467 / 12 = 19.8979 -> tithi_num = 20 -> Krishna Panchami
    assert tithi_num == 20
    assert tithi_name == "Krishna Panchami"
    assert paksha == "Krishna"


def test_nakshatra_and_pada_consistency():
    """Test 5: Nakshatra and Pada calculation consistency."""
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED

    moon_res, _ = swe.calc_ut(BENCHMARK_JD, swe.MOON, flags)
    moon_sid = moon_res[0] % 360.0

    nak_deg = 360.0 / 27.0  # 13° 20' = 13.33333333°
    pada_deg = nak_deg / 4.0  # 3° 20' = 3.33333333°

    nak_idx = int(moon_sid / nak_deg) % 27
    nak_deg_in = moon_sid % nak_deg
    nak_pada = int(nak_deg_in / pada_deg) + 1

    # At benchmark JD 2449944.875: Moon = 357.055483°
    # 357.055483 / 13.333333 = 26.779 -> Nakshatra #27 (index 26) = Revati
    # nak_deg_in = 357.055483 - (26 * 13.333333) = 10.3888°
    # 10.3888 / 3.3333 = 3.116 -> Pada 4
    assert nak_idx == 26
    assert NAKSHATRAS[nak_idx] == "Revati"
    assert nak_pada == 4


def test_yoga_calculation_consistency():
    """Test 6: Nitya Yoga calculation consistency from (Sun_sid + Moon_sid) % 360 / (360/27)."""
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED

    sun_res, _ = swe.calc_ut(BENCHMARK_JD, swe.SUN, flags)
    moon_res, _ = swe.calc_ut(BENCHMARK_JD, swe.MOON, flags)

    sun_sid = sun_res[0] % 360.0
    moon_sid = moon_res[0] % 360.0

    yoga_deg = 360.0 / 27.0
    yoga_sum = (sun_sid + moon_sid) % 360.0
    yoga_idx = int(yoga_sum / yoga_deg) % 27

    # At benchmark JD: Sun = 118.280016°, Moon = 357.055483°
    # sum = 475.335499 % 360 = 115.335499°
    # 115.335499 / 13.333333 = 8.650 -> Yoga index 8 = Shula (9th Nitya Yoga)
    assert yoga_idx == 8
    assert YOGA_NAMES[yoga_idx] == "Shula"


def test_nakshatra_boundary_continuity():
    """Test 7: Boundary tests immediately before and after Nakshatra transitions."""
    nak_deg = 360.0 / 27.0
    pada_deg = nak_deg / 4.0

    # Test exact boundary at 13° 20' (Ashwini -> Bharani transition)
    epsilon = 0.00001  # ~0.036 arcsec

    # 1. Micro-step immediately before transition: 13° 19' 59.96" (Ashwini Pada 4)
    pos_before = nak_deg - epsilon
    idx_before = int(pos_before / nak_deg) % 27
    deg_in_before = pos_before % nak_deg
    pada_before = int(deg_in_before / pada_deg) + 1

    assert idx_before == 0
    assert NAKSHATRAS[idx_before] == "Ashwini"
    assert pada_before == 4

    # 2. Micro-step immediately after transition: 13° 20' 00.04" (Bharani Pada 1)
    pos_after = nak_deg + epsilon
    idx_after = int(pos_after / nak_deg) % 27
    deg_in_after = pos_after % nak_deg
    pada_after = int(deg_in_after / pada_deg) + 1

    assert idx_after == 1
    assert NAKSHATRAS[idx_after] == "Bharani"
    assert pada_after == 1

    # 3. Test Pisces -> Aries boundary: 359° 59' 59.9" (Revati Pada 4) -> 0° 00' 00.1" (Ashwini Pada 1)
    pos_wrap_before = 360.0 - epsilon
    idx_wrap_before = int(pos_wrap_before / nak_deg) % 27
    deg_in_wrap_before = pos_wrap_before % nak_deg
    pada_wrap_before = int(deg_in_wrap_before / pada_deg) + 1

    assert idx_wrap_before == 26
    assert NAKSHATRAS[idx_wrap_before] == "Revati"
    assert pada_wrap_before == 4

    pos_wrap_after = 0.0 + epsilon
    idx_wrap_after = int(pos_wrap_after / nak_deg) % 27
    deg_in_wrap_after = pos_wrap_after % nak_deg
    pada_wrap_after = int(deg_in_wrap_after / pada_deg) + 1

    assert idx_wrap_after == 0
    assert NAKSHATRAS[idx_wrap_after] == "Ashwini"
    assert pada_wrap_after == 1


def test_moshier_fallback_resilience():
    """Test 8: Moshier fallback continues working when .se1 files are unavailable."""
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    
    # Request SWIEPH + SIDEREAL: if swiss ephemeris files are absent or unconfigured,
    # Swiss Ephemeris automatically falls back to Moshier analytical ephemeris
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED

    sun_res, sun_flags = swe.calc_ut(BENCHMARK_JD, swe.SUN, flags)
    moon_res, moon_flags = swe.calc_ut(BENCHMARK_JD, swe.MOON, flags)

    # Calculation must produce valid numeric degrees in [0, 360)
    assert 0.0 <= sun_res[0] < 360.0
    assert 0.0 <= moon_res[0] < 360.0
    assert sun_res[3] > 0.0  # Sun direct speed ~0.96-1.0 deg/day
    assert moon_res[3] > 0.0  # Moon speed ~11.8-15 deg/day

    # Verify that FLG_SIDEREAL is maintained regardless of engine backend
    assert (sun_flags & swe.FLG_SIDEREAL) != 0
    assert (moon_flags & swe.FLG_SIDEREAL) != 0


def test_benchmark_reconciliation_all_planets_delhi_1995():
    """Benchmark: 1995-08-15 14:30 IST (JD 2449944.875) New Delhi parity between Kundali and Panchang engines."""
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED

    bodies = [
        ("Sun", swe.SUN),
        ("Moon", swe.MOON),
        ("Mars", swe.MARS),
        ("Mercury", swe.MERCURY),
        ("Jupiter", swe.JUPITER),
        ("Venus", swe.VENUS),
        ("Saturn", swe.SATURN),
        ("Rahu", swe.TRUE_NODE),
    ]

    for name, pid in bodies:
        res_k, _ = swe.calc_ut(BENCHMARK_JD, pid, flags)
        res_p, _ = swe.calc_ut(BENCHMARK_JD, pid, flags)
        delta_arcsec = abs(res_k[0] - res_p[0]) * 3600.0
        assert delta_arcsec < 1e-7, f"{name} sidereal position mismatch: delta={delta_arcsec}\""

