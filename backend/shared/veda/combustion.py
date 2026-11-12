"""
Sun Combustion (Asta) Detection Engine (Pure Shared Library).

Implements classical Jyotish planetary combustion principles from primary astronomical
and astrological treatises:

1. Surya Siddhanta (Ed. K.S. Shukla, 1957; transl. Rev. E. Burgess & W.D. Whitney, 1860):
   - Chapter IX (Udayastadhikara - On Heliacal Rising and Setting), verses 6-8:
     * Mars (Avaninandana): 17 degrees.
     * Mercury (Budha): 14 degrees when direct (rju); 12 degrees when retrograde (vakri).
     * Jupiter (Brihaspati): 11 degrees.
     * Venus (Sukra): 10 degrees when direct (rju); 8 degrees when retrograde (vakri).
     * Saturn (Manda / Sauri): 15 degrees.
   - Chapter X (Candragrahayutyadhikara - Moon Conjunction and Phases), verse 1:
     * Moon (Candrama): 12 degrees distance from Sun defines heliacal setting / visibility limit (Kalamsha).

2. Brihat Parashara Hora Shastra (BPHS, transl. R. Santhanam, 1984, Ch. 3, Ch. 27, Ch. 45):
   - Establishes the astrological status of combust planets (Asta / Kopa Avastha), resulting
     in loss of ray strength (Kiranahina) and depletion of Chesta Bala (motional strength).
     Note: BPHS relies on Siddhantic astronomical treatises (Surya Siddhanta) for specific
     numerical heliacal setting degrees (Asta-bhagas).

3. Phaladeepika (Mantreswara, transl. Gopesh Kumar Ojha / V.S. Sastri, Ch. 4, v. 8; Ch. 20, v. 20):
   - Affirms that planets in combustion (Asta) act like debilitated planets (Nichasama).

Physical Astronomical Basis for Retrograde Limit Narrowing (Mercury & Venus):
- Inferior planets undergo two distinct conjunctions with the Sun:
  a. Superior Conjunction (Direct Motion): The planet is at apogee (far side of the Sun, ~1 + r AU).
     Its apparent disk is minimal (~5-10 arcsec) and dim against the solar corona, requiring a wider
     angular separation (Mercury 14°, Venus 10°) to emerge from solar glare.
  b. Inferior Conjunction (Retrograde Motion): The planet passes between Earth and the Sun at perigee
     (~1 - r AU). At closest approach, its apparent angular diameter is significantly enlarged
     (Venus reaches ~60 arcsec). This enlarged crescent and proximity allow it to remain discernible
     closer to the solar limb, narrowing the heliacal setting orb to Mercury 12° and Venus 8°.
- Superior planets (Mars, Jupiter, Saturn) are retrograde only at opposition (180° away from the Sun),
  where combustion is mathematically impossible; hence their combustion limits are invariant to motion.

Rules & Mathematical Principles:
1. Combustion is strictly determined by shortest circular angular separation between Sun and planet:
   separation = abs((planet_longitude - sun_longitude + 180.0) % 360.0 - 180.0)
2. Inclusivity: A planet is combust when separation <= applicable_combustion_limit.
3. No same-house or same-sign occupancy approximations are permitted.
4. Tri-state output: Combust (True), Not Combust (False), Unknown/Unverifiable (None).
5. Missing or invalid longitudes (None, NaN, Inf, invalid strings, out-of-range) return Unknown.
"""

from dataclasses import dataclass
from enum import Enum
import math
import os
from typing import Any, Optional, Union

# Classical Planetary Combustion Limits (in degrees)
# Primary Authority: Surya Siddhanta Ch. IX, vv. 6-8 (Planets) and Ch. X, v. 1 (Moon).
COMBUSTION_LIMITS: dict[str, dict[str, float]] = {
    "Mars": {"direct": 17.0, "retrograde": 17.0},
    "Mercury": {"direct": 14.0, "retrograde": 12.0},
    "Jupiter": {"direct": 11.0, "retrograde": 11.0},
    "Venus": {"direct": 10.0, "retrograde": 8.0},
    "Saturn": {"direct": 15.0, "retrograde": 15.0},
    "Moon": {"direct": 12.0, "retrograde": 12.0},  # Surya Siddhanta Ch. X, v. 1 Kalamsha limit
}

# Backward compatibility alias mapping each planet to its default direct orb
COMBUSTION_RANGES: dict[str, float] = {
    p: limits["direct"] for p, limits in COMBUSTION_LIMITS.items()
}

# Configurable Moon combustion behavior:
# If True: Moon within 12° of Sun is flagged as combust (Surya Siddhanta Ch. X, v. 1).
# If False: Moon within 12° is classified under Amavasya / Kshina Chandra rather than planetary Asta.
_TREAT_MOON_AS_COMBUST: Optional[bool] = None


def set_treat_moon_as_combust(enabled: bool) -> None:
    """Set whether Moon within 12° of Sun is classified as combust."""
    global _TREAT_MOON_AS_COMBUST
    _TREAT_MOON_AS_COMBUST = bool(enabled)
    try:
        from shared.config.settings import settings
        setattr(settings, "TREAT_MOON_AS_COMBUST", _TREAT_MOON_AS_COMBUST)
    except Exception:
        pass


def get_treat_moon_as_combust() -> bool:
    """Resolve active policy for Moon combustion handling."""
    if _TREAT_MOON_AS_COMBUST is not None:
        return _TREAT_MOON_AS_COMBUST
    env_val = os.environ.get("TREAT_MOON_AS_COMBUST")
    if env_val is not None:
        return env_val.lower() in ("true", "1", "yes")
    try:
        from shared.config.settings import settings
        return getattr(settings, "TREAT_MOON_AS_COMBUST", True)
    except Exception:
        return True

# Sign name mappings for sign+degree coordinate resolution
SIGNS_SK = [
    "Mesha", "Vrishabha", "Mithuna", "Karka", "Simha", "Kanya",
    "Tula", "Vrischika", "Dhanu", "Makara", "Kumbha", "Meena"
]

SIGNS_EN = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]


class CombustionStatus(str, Enum):
    COMBUST = "combust"
    NOT_COMBUST = "not_combust"
    UNKNOWN = "unknown"


@dataclass
class CombustionResult:
    """
    Observable, strongly-typed result of planetary combustion evaluation.
    """
    planet: str
    is_combust: Optional[bool]  # True: combust, False: not combust, None: unknown/unverifiable
    status: CombustionStatus
    separation: Optional[float]
    limit: Optional[float]
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "planet": self.planet,
            "is_combust": self.is_combust,
            "status": self.status.value,
            "separation": round(self.separation, 4) if self.separation is not None else None,
            "limit": round(self.limit, 2) if self.limit is not None else None,
            "reason": self.reason,
        }


def calculate_angular_separation(lon1: float, lon2: float) -> float:
    """
    Compute the shortest circular angular separation between two ecliptic longitudes in degrees.
    Formula: abs((lon1 - lon2 + 180.0) % 360.0 - 180.0)
    Result is guaranteed to lie in the closed interval [0.0, 180.0].
    """
    diff = abs((lon1 - lon2 + 180.0) % 360.0 - 180.0)
    return float(diff)


def _parse_dms_or_float(val: Union[int, float, str]) -> Optional[float]:
    """Parse numeric, float string, or DMS string ('22°04\'') into a float degree."""
    if isinstance(val, (int, float)):
        fval = float(val)
        if math.isnan(fval) or math.isinf(fval):
            return None
        return fval
    if isinstance(val, str):
        cleaned = val.strip()
        if not cleaned:
            return None
        # Handle DMS format like "22°04'" or "2°57'"
        if "°" in cleaned or "'" in cleaned:
            parts = cleaned.replace("°", " ").replace("'", " ").replace('"', " ").split()
            try:
                deg = float(parts[0])
                minute = float(parts[1]) if len(parts) > 1 else 0.0
                second = float(parts[2]) if len(parts) > 2 else 0.0
                total = deg + (minute / 60.0) + (second / 3600.0)
                if math.isnan(total) or math.isinf(total):
                    return None
                return total
            except Exception:
                return None
        try:
            fval = float(cleaned)
            if math.isnan(fval) or math.isinf(fval):
                return None
            return fval
        except (ValueError, TypeError):
            return None
    return None


def extract_longitude(data: Any, strict_range: bool = True) -> Optional[float]:
    """
    Extract and validate absolute sidereal/tropical longitude [0.0, 360.0) from planetary data.

    Accepts:
    1. Raw float / int / valid numeric string.
    2. Dict containing absolute longitude keys: '_raw_lon', 'longitude', 'lon', 'total_degree', 'abs_degree'.
    3. Dict containing sign ('Mesha', 'Aries', etc.) + degree offset ('degree_decimal' or 'degree').

    Returns:
    - Float degree in [0.0, 360.0) upon successful validation.
    - None if data is missing, empty, NaN, Inf, invalid string, or outside [0.0, 360.0].
    """
    if data is None:
        return None

    # 1. Direct scalar float/int/str
    if isinstance(data, (int, float, str)):
        parsed = _parse_dms_or_float(data)
        if parsed is None:
            return None
        if strict_range and (parsed < 0.0 or parsed > 360.0):
            return None
        # Normalize 360.0 to 0.0
        return parsed % 360.0 if parsed == 360.0 else parsed

    # 2. Dictionary structure
    if isinstance(data, dict):
        # 2a. Check direct absolute longitude keys
        for key in ("_raw_lon", "longitude", "lon", "total_degree", "abs_degree"):
            if key in data and data[key] is not None:
                val = data[key]
                parsed = _parse_dms_or_float(val)
                if parsed is not None:
                    if strict_range and (parsed < 0.0 or parsed > 360.0):
                        return None
                    return parsed % 360.0 if parsed == 360.0 else parsed

        # 2b. Check sign + degree within sign
        sign = data.get("sign")
        deg_raw = data.get("degree_decimal", data.get("degree"))
        if sign and deg_raw is not None:
            sign_idx = None
            if sign in SIGNS_SK:
                sign_idx = SIGNS_SK.index(sign)
            elif sign in SIGNS_EN:
                sign_idx = SIGNS_EN.index(sign)

            if sign_idx is not None:
                deg_offset = _parse_dms_or_float(deg_raw)
                if deg_offset is not None and 0.0 <= deg_offset <= 30.0:
                    total_lon = (sign_idx * 30.0 + (deg_offset % 30.0)) % 360.0
                    return total_lon

    return None


def extract_retrograde(data: Any) -> Optional[bool]:
    """
    Extract boolean retrograde state from planet dictionary.
    Returns True, False, or None if unknown/unspecified.
    """
    if isinstance(data, dict):
        if "retrograde" in data and data["retrograde"] is not None:
            val = data["retrograde"]
            if isinstance(val, bool):
                return val
            if isinstance(val, (int, float)):
                return bool(val)
            if isinstance(val, str):
                cleaned = val.strip().lower()
                if cleaned in ("true", "1", "yes", "r", "retrograde"):
                    return True
                if cleaned in ("false", "0", "no", "d", "direct"):
                    return False
        if "is_retrograde" in data and data["is_retrograde"] is not None:
            return bool(data["is_retrograde"])
        # Check speed if available: negative speed indicates retrograde motion
        speed = data.get("speed")
        if isinstance(speed, (int, float)) and not math.isnan(speed):
            return speed < 0.0
    return None


def check_combustion(name: str, pdata: Any, sun_data: Any) -> CombustionResult:
    """
    Perform rigorous astronomical and classical Jyotish combustion evaluation for a given planet.

    Parameters:
        name: Name of the celestial body (e.g., 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn', 'Moon').
        pdata: Planetary data dictionary, longitude float, or degree record.
        sun_data: Sun data dictionary, longitude float, or degree record.

    Returns:
        CombustionResult indicating combust (True), not combust (False), or unknown (None).
    """
    # 1. Non-combustible bodies
    if name == "Sun":
        return CombustionResult(
            planet="Sun",
            is_combust=False,
            status=CombustionStatus.NOT_COMBUST,
            separation=0.0,
            limit=None,
            reason="Sun is the illuminating source and cannot combust itself.",
        )

    if name in ("Rahu", "Ketu"):
        return CombustionResult(
            planet=name,
            is_combust=False,
            status=CombustionStatus.NOT_COMBUST,
            separation=None,
            limit=None,
            reason=f"{name} is a lunar node (Chhaya Graha / shadow planet) and not subject to planetary combustion.",
        )

    # 2. Extract and validate Sun longitude
    sun_lon = extract_longitude(sun_data)
    if sun_lon is None:
        return CombustionResult(
            planet=name,
            is_combust=None,
            status=CombustionStatus.UNKNOWN,
            separation=None,
            limit=None,
            reason="Sun longitude is missing, invalid, or out of range [0, 360); combustion cannot be verified.",
        )

    # 3. Extract and validate Planet longitude (no house-based or sign-based fallback permitted)
    p_lon = extract_longitude(pdata)
    if p_lon is None:
        return CombustionResult(
            planet=name,
            is_combust=None,
            status=CombustionStatus.UNKNOWN,
            separation=None,
            limit=None,
            reason=f"{name} longitude is missing, invalid, or out of range [0, 360); combustion cannot be verified.",
        )

    # 4. Compute shortest circular angular separation
    separation = calculate_angular_separation(sun_lon, p_lon)

    # 5. Resolve applicable combustion limit and handle retrograde ambiguity
    limits = COMBUSTION_LIMITS.get(name)
    if not limits:
        return CombustionResult(
            planet=name,
            is_combust=None,
            status=CombustionStatus.UNKNOWN,
            separation=separation,
            limit=None,
            reason=f"No combustion limits configured for celestial body '{name}'.",
        )

    direct_limit = limits["direct"]
    retro_limit = limits["retrograde"]
    retro_state = extract_retrograde(pdata)

    # For planets with identical direct and retrograde limits (Mars, Jupiter, Saturn, Moon)
    if direct_limit == retro_limit:
        applicable_limit = direct_limit

        # Special classical handling for Moon:
        # Surya Siddhanta Ch. X, v. 1 defines the Moon's 12° setting distance (Amavasya / Kshina Chandra).
        # A configurable toggle allows downstream consumers to report this as combustion or Amavasya solar proximity.
        if name == "Moon":
            if not get_treat_moon_as_combust():
                return CombustionResult(
                    planet="Moon",
                    is_combust=False,
                    status=CombustionStatus.NOT_COMBUST,
                    separation=separation,
                    limit=applicable_limit,
                    reason=(
                        f"Moon solar proximity ({separation:.4f}°) is classified as Amavasya / Kshina Chandra "
                        "rather than planetary combustion per active configuration (TREAT_MOON_AS_COMBUST=False)."
                    ),
                )
            is_cb = separation <= applicable_limit
            status = CombustionStatus.COMBUST if is_cb else CombustionStatus.NOT_COMBUST
            reason = (
                f"Moon is combust within {separation:.4f}° of Sun (threshold {applicable_limit}° / Amavasya setting arc)."
                if is_cb
                else f"Moon is free from combustion at {separation:.4f}° from Sun (threshold {applicable_limit}°)."
            )
            return CombustionResult(
                planet="Moon",
                is_combust=is_cb,
                status=status,
                separation=separation,
                limit=applicable_limit,
                reason=reason,
            )

        is_cb = separation <= applicable_limit
        status = CombustionStatus.COMBUST if is_cb else CombustionStatus.NOT_COMBUST
        motion_note = "retrograde" if retro_state is True else "direct"
        reason = (
            f"{name} is combust within {separation:.4f}° of Sun (threshold {applicable_limit}°)."
            if is_cb
            else f"{name} is free from combustion at {separation:.4f}° from Sun (threshold {applicable_limit}°)."
        )
        return CombustionResult(
            planet=name,
            is_combust=is_cb,
            status=status,
            separation=separation,
            limit=applicable_limit,
            reason=reason,
        )

    # For inferior planets where retrograde narrows the combustion limit (Mercury: 14°/12°, Venus: 10°/8°)
    min_orb = min(direct_limit, retro_limit)
    max_orb = max(direct_limit, retro_limit)

    # Scenario A: Definitively combust regardless of retrograde state
    if separation <= min_orb:
        applicable_limit = retro_limit if retro_state is True else direct_limit
        return CombustionResult(
            planet=name,
            is_combust=True,
            status=CombustionStatus.COMBUST,
            separation=separation,
            limit=applicable_limit,
            reason=f"{name} is combust within {separation:.4f}° of Sun (separation <= minimum threshold {min_orb}°).",
        )

    # Scenario B: Definitively not combust regardless of retrograde state
    if separation > max_orb:
        applicable_limit = direct_limit if retro_state is False else retro_limit
        return CombustionResult(
            planet=name,
            is_combust=False,
            status=CombustionStatus.NOT_COMBUST,
            separation=separation,
            limit=applicable_limit,
            reason=f"{name} is free from combustion at {separation:.4f}° from Sun (separation > maximum threshold {max_orb}°).",
        )

    # Scenario C: Separation is in ambiguous window (min_orb < separation <= max_orb)
    if retro_state is None:
        return CombustionResult(
            planet=name,
            is_combust=None,
            status=CombustionStatus.UNKNOWN,
            separation=separation,
            limit=None,
            reason=(
                f"Retrograde state is unknown for {name} and angular separation {separation:.4f}° "
                f"falls in the boundary window ({min_orb}° - {max_orb}°); combustion cannot be verified."
            ),
        )

    # Scenario D: Retrograde state is definitively known
    applicable_limit = retro_limit if retro_state else direct_limit
    is_cb = separation <= applicable_limit
    status = CombustionStatus.COMBUST if is_cb else CombustionStatus.NOT_COMBUST
    state_str = "retrograde" if retro_state else "direct"
    reason = (
        f"{name} ({state_str}) is combust within {separation:.4f}° of Sun (threshold {applicable_limit}°)."
        if is_cb
        else f"{name} ({state_str}) is free from combustion at {separation:.4f}° from Sun (threshold {applicable_limit}°)."
    )
    return CombustionResult(
        planet=name,
        is_combust=is_cb,
        status=status,
        separation=separation,
        limit=applicable_limit,
        reason=reason,
    )


def is_combust(name: str, pdata: Any, sun_data: Any) -> Optional[bool]:
    """
    Convenience predicate returning:
    - True: Confirmed combust.
    - False: Confirmed not combust.
    - None: Unknown / unverifiable due to missing or invalid data.
    """
    result = check_combustion(name, pdata, sun_data)
    return result.is_combust
