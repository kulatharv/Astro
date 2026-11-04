"""Thin wrapper over pyswisseph (Swiss Ephemeris) for planetary math."""

import os
from typing import Any, Dict, Optional
import swisseph as swe

# Initialize configuration
_ACTIVE_EPHE_PATH: str = "."

def init_ephemeris(ephe_path: Optional[str] = None) -> None:
    """Initialize Swiss Ephemeris path and default sidereal mode."""
    global _ACTIVE_EPHE_PATH
    if ephe_path:
        _ACTIVE_EPHE_PATH = ephe_path
    else:
        try:
            from shared.config.settings import settings
            _ACTIVE_EPHE_PATH = settings.EPHE_PATH or "."
        except Exception:
            _ACTIVE_EPHE_PATH = os.environ.get("EPHE_PATH", ".")

    swe.set_ephe_path(_ACTIVE_EPHE_PATH)
    swe.set_sid_mode(swe.SIDM_LAHIRI)

# Run initialization
init_ephemeris()


def get_ephemeris_diagnostics() -> Dict[str, Any]:
    """
    Return observable diagnostics about the active Swiss Ephemeris runtime.
    Validates whether high-precision JPL .se1 files are loaded or if the engine
    is operating in Moshier semi-analytical fallback mode.
    """
    # Sample calculation to observe actual runtime flag used by C library
    # J2000.0 epoch: 2000-01-01 12:00:00 UTC = JD 2451545.0
    res = swe.calc_ut(2451545.0, swe.SUN, swe.FLG_SWIEPH)
    actual_flag = res[1] if isinstance(res, (tuple, list)) and len(res) > 1 else 0

    is_swieph = bool(actual_flag & swe.FLG_SWIEPH)
    is_moshier = bool(actual_flag & swe.FLG_MOSEPH)

    mode = "swiss_ephemeris" if is_swieph else "moshier"

    # Check for .se1 files on disk
    se1_files_count = 0
    if os.path.exists(_ACTIVE_EPHE_PATH) and os.path.isdir(_ACTIVE_EPHE_PATH):
        try:
            se1_files_count = len([f for f in os.listdir(_ACTIVE_EPHE_PATH) if f.lower().endswith(".se1")])
        except Exception:
            se1_files_count = 0

    return {
        "status": "operational",
        "runtime_mode": mode,
        "is_moshier_fallback": is_moshier or not is_swieph,
        "swe_c_version": getattr(swe, "version", "unknown"),
        "pyswisseph_version": getattr(swe, "__version__", "unknown"),
        "ephe_path": _ACTIVE_EPHE_PATH,
        "se1_files_found": se1_files_count,
        "sidereal_mode": "Lahiri (SIDM_LAHIRI)",
        "accuracy_level": (
            "High-precision JPL DE431 (~0.001 arcsecond)"
            if is_swieph
            else "Standard analytical Moshier (~0.1 arcsecond, 1800-2050 CE)"
        ),
        "commercial_licensing": (
            "Requires Astrodienst Commercial License for closed-source SaaS or GNU GPL v2 for open-source."
            if is_swieph
            else "Open-source Moshier model. Safe for commercial SaaS distribution without .se1 license obligations."
        ),
    }


def calc_ut(julian_day: float, body: int, flags: int = swe.FLG_SIDEREAL) -> tuple:
    """Calculate sidereal longitude and speed for a celestial body."""
    return swe.calc_ut(julian_day, body, flags)


def get_ayanamsa_ut(julian_day: float) -> float:
    """Return Lahiri ayanamsa value for a given Julian Day."""
    return swe.get_ayanamsa_ut(julian_day)


def julday(year: int, month: int, day: int, hour: float) -> float:
    """Convert UT date and decimal hour to Julian Day number."""
    return swe.julday(year, month, day, hour)


def houses(julian_day: float, lat: float, lon: float, hsys: bytes = b'E') -> tuple:
    """Calculate house cusps and Ascendant/MC (Equal system b'E' or Placidus b'P')."""
    return swe.houses(julian_day, lat, lon, hsys)
