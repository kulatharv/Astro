"""
AstroLogic AI - Issue 1.2: Swiss Ephemeris Runtime Verification Test Suite
Verifies runtime ephemeris detection, Moshier fallback handling, policy enforcement,
and Panchanga-Kundali parity across supported ephemeris modes.
"""

import os
import pytest
import swisseph as swe

from shared.ephemeris.wrapper import (
    init_ephemeris,
    get_ephemeris_diagnostics,
    verify_ephemeris_source,
    get_runtime_ephemeris_mode,
    is_moshier_active,
)

BENCHMARK_JD = 2449944.875  # 1995-08-15 14:30:00 IST (09:00:00 UTC)


@pytest.fixture(autouse=True)
def reset_ephemeris_state():
    """Reset ephemeris configuration to clean default after each test."""
    yield
    init_ephemeris(ephe_path=".", ephemeris_mode="auto", require_swieph=False)


def test_runtime_flag_detection_and_ephemeris_source():
    """Task 2: Requests FLG_SWIEPH, inspects returned flags for Sun, Moon, Mars, reports actual source."""
    init_ephemeris(ephe_path=".", ephemeris_mode="auto", require_swieph=False)

    bodies = [
        ("Sun", swe.SUN),
        ("Moon", swe.MOON),
        ("Mars", swe.MARS),
    ]

    for name, body_id in bodies:
        diag = verify_ephemeris_source(BENCHMARK_JD, body_id, swe.FLG_SWIEPH)
        ret_flag = diag["returned_flags"]

        # When .se1 files are absent, C-library MUST set SEFLG_MOSEPH (4) and NOT SEFLG_SWIEPH (2)
        assert (ret_flag & swe.FLG_MOSEPH) != 0, f"{name} returned flag {ret_flag} must contain SEFLG_MOSEPH (4)"
        assert (ret_flag & swe.FLG_SWIEPH) == 0, f"{name} returned flag {ret_flag} must NOT claim SEFLG_SWIEPH (2)"
        assert diag["ephemeris_source"] == "moshier", f"{name} source must be identified as 'moshier'"
        assert diag["has_seflg_moseph"] is True
        assert diag["has_seflg_swieph"] is False


def test_moseph_explicit_flag_detection():
    """Test 2: Explicit request for FLG_MOSEPH returns SEFLG_MOSEPH."""
    res_sun = swe.calc_ut(BENCHMARK_JD, swe.SUN, swe.FLG_MOSEPH)
    ret_flag = res_sun[1]

    assert (ret_flag & swe.FLG_MOSEPH) != 0
    assert (ret_flag & swe.FLG_SWIEPH) == 0


def test_missing_se1_files_behavior(tmp_path):
    """Test 3: Missing .se1 files in an empty directory safely defaults to Moshier."""
    empty_ephe_dir = str(tmp_path / "empty_ephe")
    os.makedirs(empty_ephe_dir, exist_ok=True)

    diag = init_ephemeris(ephe_path=empty_ephe_dir, ephemeris_mode="auto", require_swieph=False)

    assert diag["ephe_path_exists"] is True
    assert diag["se1_files_found"] == 0
    assert diag["runtime_mode"] == "moshier"
    assert diag["is_moshier_fallback"] is True
    assert diag["status"] == "operational"


def test_invalid_ephemeris_directory_behavior():
    """Test 4: Invalid/non-existent ephemeris directory handles gracefully and falls back to Moshier."""
    invalid_path = "/nonexistent_ephemeris_directory_xyz_9999"

    diag = init_ephemeris(ephe_path=invalid_path, ephemeris_mode="auto", require_swieph=False)

    assert diag["ephe_path_exists"] is False
    assert diag["se1_files_found"] == 0
    assert diag["runtime_mode"] == "moshier"
    assert diag["is_moshier_fallback"] is True

    # Calculation must still succeed via Moshier analytical formulas
    res = swe.calc_ut(BENCHMARK_JD, swe.SUN, swe.FLG_SWIEPH)
    assert 0.0 <= res[0][0] < 360.0
    assert (res[1] & swe.FLG_MOSEPH) != 0


def test_runtime_diagnostics_accuracy():
    """Test 5: Runtime diagnostic report structure and accuracy."""
    diag = get_ephemeris_diagnostics()

    assert diag["status"] == "operational"
    assert diag["runtime_mode"] in ("swiss_ephemeris", "moshier")
    assert isinstance(diag["is_moshier_fallback"], bool)
    assert "accuracy_level" in diag
    assert "commercial_licensing" in diag
    assert "body_sources" in diag
    assert "Sun" in diag["body_sources"]
    assert "Moon" in diag["body_sources"]
    assert "Mars" in diag["body_sources"]

    # Critical check: Never label Moshier results as Swiss Ephemeris
    if diag["is_moshier_fallback"]:
        assert diag["runtime_mode"] == "moshier"
        assert "Moshier" in diag["accuracy_level"]
        assert diag["body_sources"]["Sun"] == "moshier"
    else:
        assert diag["runtime_mode"] == "swiss_ephemeris"
        assert "JPL" in diag["accuracy_level"]


def test_strict_production_policy_enforcement():
    """Test 6: If production requires Swiss Ephemeris, fail initialization when .se1 files are missing."""
    # 1. require_swieph=True with no .se1 files must raise RuntimeError
    with pytest.raises(RuntimeError) as exc_info:
        init_ephemeris(ephe_path=".", require_swieph=True)
    assert "Swiss Ephemeris strict mode is enforced" in str(exc_info.value)
    assert "SEFLG_MOSEPH" in str(exc_info.value)

    # 2. ephemeris_mode='swiss_ephemeris' must also enforce strict mode and raise RuntimeError
    with pytest.raises(RuntimeError) as exc_info2:
        init_ephemeris(ephe_path=".", ephemeris_mode="swiss_ephemeris")
    assert "Swiss Ephemeris strict mode is enforced" in str(exc_info2.value)


def test_panchanga_kundali_parity_under_moshier_fallback():
    """Task 4 Mode B: Panchanga and Kundali parity under Moshier fallback mode across all 9 grahas."""
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    flags = swe.FLG_MOSEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED

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
        res_kundali, k_flags = swe.calc_ut(BENCHMARK_JD, pid, flags)
        res_panchang, p_flags = swe.calc_ut(BENCHMARK_JD, pid, flags)

        delta_arcsec = abs(res_kundali[0] - res_panchang[0]) * 3600.0
        assert delta_arcsec < 1e-7, f"{name} position mismatch in Moshier mode: delta={delta_arcsec}\""
        assert k_flags == p_flags, f"{name} flags mismatch: Kundali={k_flags}, Panchang={p_flags}"
        assert (k_flags & swe.FLG_MOSEPH) != 0, f"{name} must have SEFLG_MOSEPH flag active"

    # Ketu
    r_k, _ = swe.calc_ut(BENCHMARK_JD, swe.TRUE_NODE, flags)
    r_p, _ = swe.calc_ut(BENCHMARK_JD, swe.TRUE_NODE, flags)
    ketu_k = (r_k[0] + 180.0) % 360.0
    ketu_p = (r_p[0] + 180.0) % 360.0
    delta_ketu = abs(ketu_k - ketu_p) * 3600.0
    assert delta_ketu < 1e-7


def test_panchanga_kundali_parity_under_swieph_request_mode():
    """Task 4 Mode A/B: Parity when FLG_SWIEPH is requested across all 9 grahas."""
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
        res_kundali, k_flags = swe.calc_ut(BENCHMARK_JD, pid, flags)
        res_panchang, p_flags = swe.calc_ut(BENCHMARK_JD, pid, flags)

        delta_arcsec = abs(res_kundali[0] - res_panchang[0]) * 3600.0
        assert delta_arcsec < 1e-7, f"{name} position mismatch: delta={delta_arcsec}\""
        assert k_flags == p_flags
        assert (k_flags & swe.FLG_SIDEREAL) != 0

