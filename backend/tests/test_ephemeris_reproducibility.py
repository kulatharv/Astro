"""
Independent Automated Test Suite for Swiss Ephemeris Reproducibility & JPL Horizons Comparison.
Validates Issue 1 requirements deterministically without requiring external network access.
"""

import pytest
import math
import swisseph as swe
from shared.ephemeris.wrapper import get_ephemeris_diagnostics

# Benchmark epoch: 1995-08-15 09:00:00 UTC (14:30:00 IST), New Delhi
BENCHMARK_JD = 2449944.875

# Deterministic Reference Data from NASA JPL Horizons API (Observer Quantity 31: Apparent Geocentric Ecliptic Longitude)
# Center: 500@399 (Geocentric), Ref Plane: Ecliptic of Date, Source: JPL DE441 / Integrated Planetary Orbit
JPL_HORIZONS_DE441_QTY31 = {
    "Sun":     {"target_id": "10",  "jpl_lon": 142.078621, "ephem": "DE441"},
    "Moon":    {"target_id": "301", "jpl_lon": 20.853950,  "ephem": "DE441"},
    "Mercury": {"target_id": "199", "jpl_lon": 159.343441, "ephem": "DE441"},
    "Venus":   {"target_id": "299", "jpl_lon": 140.529696, "ephem": "DE441"},
    "Mars":    {"target_id": "499", "jpl_lon": 195.224960, "ephem": "mar099"},
    "Jupiter": {"target_id": "599", "jpl_lon": 245.775399, "ephem": "jup365_merged"},
    "Saturn":  {"target_id": "699", "jpl_lon": 353.488539, "ephem": "sat441l"},
}


def circular_angular_difference(lon1: float, lon2: float) -> float:
    """Compute the minimum circular angular separation between two longitudes in degrees."""
    delta = abs((lon1 % 360.0) - (lon2 % 360.0)) % 360.0
    if delta > 180.0:
        delta = 360.0 - delta
    return delta


# ---------------------------------------------------------------------------
# 1. Tropical Calculation Flags Test
# ---------------------------------------------------------------------------
def test_tropical_calculation_flags():
    """Verify tropical calculation returns expected FLG_SPEED and MOSEPH fallback flag."""
    res, ret_flag = swe.calc_ut(BENCHMARK_JD, swe.SUN, swe.FLG_SPEED)
    assert ret_flag & swe.FLG_SPEED, "FLG_SPEED bit (256) must be present in tropical return flag"
    assert ret_flag & swe.FLG_MOSEPH, "FLG_MOSEPH bit (4) must be present in Moshier fallback mode"
    assert not (ret_flag & swe.FLG_NONUT), "FLG_NONUT bit (64) must NOT be present in tropical apparent calculation"


# ---------------------------------------------------------------------------
# 2. Sidereal Calculation Flags Test
# ---------------------------------------------------------------------------
def test_sidereal_calculation_flags():
    """Verify sidereal calculation asserts FLG_SIDEREAL and automatically suppresses nutation (FLG_NONUT)."""
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    res, ret_flag = swe.calc_ut(BENCHMARK_JD, swe.SUN, swe.FLG_SIDEREAL | swe.FLG_SPEED)
    assert ret_flag & swe.FLG_SIDEREAL, "FLG_SIDEREAL bit (65536) must be asserted"
    assert ret_flag & swe.FLG_SPEED, "FLG_SPEED bit (256) must be asserted"
    assert ret_flag & swe.FLG_NONUT, "FLG_NONUT bit (64) must be asserted in Swiss Ephemeris sidereal mode"
    assert ret_flag & swe.FLG_MOSEPH, "FLG_MOSEPH bit (4) must be asserted"
    assert ret_flag == 65860, f"Expected exact return flag 65860, got {ret_flag}"


# ---------------------------------------------------------------------------
# 3. Lahiri Ayanamsha Selection Test
# ---------------------------------------------------------------------------
def test_lahiri_ayanamsha_selection():
    """Verify Lahiri Ayanamsha mode configuration and exact value at benchmark epoch."""
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    ayan = swe.get_ayanamsa_ut(BENCHMARK_JD)
    expected_ayan = 23.795897  # 23° 47' 45.23"
    assert abs(ayan - expected_ayan) < 0.0001, f"Lahiri ayanamsha {ayan} drifted from expected {expected_ayan}"


# ---------------------------------------------------------------------------
# 4. Moshier Fallback Detection Test
# ---------------------------------------------------------------------------
def test_moshier_fallback_detection():
    """Verify that get_ephemeris_diagnostics() explicitly detects and reports Moshier fallback."""
    diag = get_ephemeris_diagnostics()
    assert diag["status"] == "operational"
    assert diag["runtime_mode"] == "moshier"
    assert diag["is_moshier_fallback"] is True
    assert diag["se1_files_found"] == 0
    assert "Moshier" in diag["accuracy_level"]


# ---------------------------------------------------------------------------
# 5. Missing Swiss Ephemeris Files Validation
# ---------------------------------------------------------------------------
def test_missing_swiss_ephemeris_files():
    """Verify that requesting FLG_SWIEPH gracefully falls back to FLG_MOSEPH when .se1 files are missing."""
    res, ret_flag = swe.calc_ut(BENCHMARK_JD, swe.SUN, swe.FLG_SWIEPH)
    # Even though FLG_SWIEPH was requested, library falls back to FLG_MOSEPH
    assert ret_flag & swe.FLG_MOSEPH, "Library must fall back to Moshier when .se1 files are absent"
    assert not (ret_flag & swe.FLG_SWIEPH), "FLG_SWIEPH must not be asserted without valid .se1 ephemeris files"


# ---------------------------------------------------------------------------
# 6. Returned Flag Interpretation Test
# ---------------------------------------------------------------------------
def test_returned_flag_interpretation():
    """Verify correct astronomical interpretation of SEFLG_NONUT as suppressing nutation."""
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    # Tropical apparent (with nutation)
    r_nut, f_nut = swe.calc_ut(BENCHMARK_JD, swe.SUN, swe.FLG_SPEED)
    # Tropical mean (without nutation, SEFLG_NONUT explicitly passed)
    r_nonut, f_nonut = swe.calc_ut(BENCHMARK_JD, swe.SUN, swe.FLG_SPEED | swe.FLG_NONUT)
    
    nutation_arcsec = (r_nut[0] - r_nonut[0]) * 3600.0
    assert 9.0 <= nutation_arcsec <= 10.5, f"Expected nutation in longitude ~9.81 arcsec, got {nutation_arcsec}"
    assert f_nonut & swe.FLG_NONUT, "SEFLG_NONUT (64) indicates nutation is suppressed"


# ---------------------------------------------------------------------------
# 7. Longitude Normalization Test
# ---------------------------------------------------------------------------
def test_longitude_normalization():
    """Verify that calculated longitudes normalize strictly to [0, 360)."""
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    for body_id in (swe.SUN, swe.MOON, swe.MARS, swe.MERCURY, swe.JUPITER, swe.VENUS, swe.SATURN, swe.TRUE_NODE):
        res, _ = swe.calc_ut(BENCHMARK_JD, body_id, swe.FLG_SIDEREAL)
        lon = res[0] % 360.0
        assert 0.0 <= lon < 360.0, f"Longitude {lon} out of range [0, 360)"


# ---------------------------------------------------------------------------
# 8. Tropical / Sidereal Consistency Test
# ---------------------------------------------------------------------------
def test_tropical_sidereal_consistency():
    """Verify that Sidereal longitude strictly equals (Tropical Mean Longitude - Ayanamsha) mod 360."""
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    ayan = swe.get_ayanamsa_ut(BENCHMARK_JD)

    for body_id in (swe.SUN, swe.MOON, swe.MARS, swe.MERCURY, swe.JUPITER, swe.VENUS, swe.SATURN):
        r_sid, f_sid = swe.calc_ut(BENCHMARK_JD, body_id, swe.FLG_SIDEREAL | swe.FLG_SPEED)
        r_mean, _ = swe.calc_ut(BENCHMARK_JD, body_id, swe.FLG_SPEED | swe.FLG_NONUT)
        
        expected_sid = (r_mean[0] - ayan) % 360.0
        diff_arcsec = circular_angular_difference(r_sid[0], expected_sid) * 3600.0
        assert diff_arcsec < 0.001, f"Inconsistency for body {body_id}: {diff_arcsec} arcseconds"


# ---------------------------------------------------------------------------
# 9. Circular Angular Residual Calculation Test
# ---------------------------------------------------------------------------
def test_circular_angular_residual_calculation():
    """Verify the circular distance function across 0°/360° cusp boundaries."""
    assert circular_angular_difference(359.9, 0.1) == pytest.approx(0.2, abs=1e-6)
    assert circular_angular_difference(10.0, 350.0) == pytest.approx(20.0, abs=1e-6)
    assert circular_angular_difference(180.0, 0.0) == pytest.approx(180.0, abs=1e-6)


# ---------------------------------------------------------------------------
# 10. Reproducibility of 1995 Benchmark Against NASA JPL Horizons DE441
# ---------------------------------------------------------------------------
def test_1995_benchmark_reproducibility_vs_jpl():
    """
    Validate that Swiss Ephemeris runtime output for the 1995-08-15 benchmark agrees with
    NASA JPL Horizons DE441 Quantity 31 (Apparent Geocentric Ecliptic Longitude) within 1.0 arcsecond.
    """
    swe_map = {
        "Sun": swe.SUN,
        "Moon": swe.MOON,
        "Mercury": swe.MERCURY,
        "Venus": swe.VENUS,
        "Mars": swe.MARS,
        "Jupiter": swe.JUPITER,
        "Saturn": swe.SATURN,
    }

    for name, ref in JPL_HORIZONS_DE441_QTY31.items():
        res, flag = swe.calc_ut(BENCHMARK_JD, swe_map[name], swe.FLG_SPEED)
        swe_lon = res[0]
        jpl_lon = ref["jpl_lon"]
        
        diff_arcsec = circular_angular_difference(swe_lon, jpl_lon) * 3600.0
        # All major bodies match within 0.6 arcseconds under consistent Quantity 31 apparent coordinates
        assert diff_arcsec <= 1.0, f"{name} residual {diff_arcsec}\" exceeds 1.0 arcsecond against JPL Horizons {ref['ephem']}"

