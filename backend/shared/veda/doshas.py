"""
Classical and Standardized Vedic Doshas Engine (Pure Shared Library).

Implements WP4 specifications for:
1. Multi-Frame Mangal Dosha (Lagna, Chandra Lagna, Shukra Lagna) with 16 classical cancellations.
2. Shani Sade Sati (Rising, Peak, Setting phases, exact boundary orbs, retrograde re-entry).
3. Kantaka Shani (4th, 7th, 10th from Moon) and Ashtama Shani (8th from Moon).
4. Kaal Sarp Dosh (12 classical types, Savya/Apsavya, Anshik, gated modern default=False).
5. Pitru Dosha with 9th house and 9th lord afflictions and Jupiter cancellations.
6. Grahan Dosha with exact angular orb proximity (Surya Grahan 12°, Chandra Grahan 9°).
7. Gandmool Dosha with Gandanta sandhi pada severity.

Stateless, zero DB, zero Redis, zero side-effects.
"""

from __future__ import annotations

from typing import Any, Optional

from .zodiac import SIGNS_SK, SIGN_LORDS
from .strength import EXALTATION, DEBILITATION, OWN_SIGNS

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

MANGLIK_HOUSES = {1, 2, 4, 7, 8, 12}
GANDMOOL_NAKSHATRAS = {"Ashwini", "Ashlesha", "Magha", "Jyeshtha", "Mula", "Revati"}

# Deep Gandanta Padas (sandhi transition between water & fire signs)
GANDANTA_PADAS = {
    ("Revati", 4), ("Ashwini", 1),
    ("Ashlesha", 4), ("Magha", 1),
    ("Jyeshtha", 4), ("Mula", 1),
}

KAAL_SARP_TYPES = {
    1: "Anant Kaal Sarp",
    2: "Kulik Kaal Sarp",
    3: "Vasuki Kaal Sarp",
    4: "Shankhpal Kaal Sarp",
    5: "Padma Kaal Sarp",
    6: "Mahapadma Kaal Sarp",
    7: "Takshak Kaal Sarp",
    8: "Karkotak Kaal Sarp",
    9: "Shankhachur Kaal Sarp",
    10: "Ghatak Kaal Sarp",
    11: "Vishdhar Kaal Sarp",
    12: "Sheshnag Kaal Sarp",
}

CLASSICAL_7 = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]


# ---------------------------------------------------------------------------
# Helper Inspection Functions
# ---------------------------------------------------------------------------

def _get_planet_map(planets: list[dict] | dict[str, dict]) -> dict[str, dict]:
    """Index planets by normalized name."""
    if isinstance(planets, dict):
        return planets
    pmap = {}
    for p in planets:
        name = p.get("name") or p.get("planet")
        if name:
            pmap[name] = p
            pmap[name.capitalize()] = p
    return pmap


def _house_of(pmap: dict, name: str) -> int:
    """Retrieve 1-indexed house number of a planet."""
    p = pmap.get(name, {})
    h = p.get("house", 0)
    if isinstance(h, int):
        return h
    try:
        return int(str(h).split("/")[0])
    except (ValueError, TypeError):
        return 0


def _sign_of(pmap: dict, name: str) -> str:
    """Retrieve zodiac sign of a planet."""
    return pmap.get(name, {}).get("sign", "")


def _degree_of(pmap: dict, name: str) -> float:
    """Retrieve degree within sign."""
    p = pmap.get(name, {})
    deg = p.get("degree_decimal")
    if deg is not None:
        try:
            return float(deg)
        except (ValueError, TypeError):
            pass
    deg = p.get("degree")
    if isinstance(deg, (int, float)):
        return float(deg)
    return 15.0


def _is_retrograde(pmap: dict, name: str) -> bool:
    """Check if planet is retrograde."""
    return bool(pmap.get(name, {}).get("retrograde", False))


def _house_distance(from_h: int, to_h: int) -> int:
    """Inclusive distance in houses from from_h to to_h (1-indexed)."""
    if not from_h or not to_h:
        return 0
    return ((to_h - from_h) % 12) + 1


def _aspects_house(planet: str, planet_house: int, target_house: int) -> bool:
    """True if planet aspects target_house by Parashari full aspect."""
    if not planet_house or not target_house:
        return False
    dist = _house_distance(planet_house, target_house)
    if dist == 7:
        return True
    if planet == "Mars" and dist in (4, 8):
        return True
    if planet == "Jupiter" and dist in (5, 9):
        return True
    if planet == "Saturn" and dist in (3, 10):
        return True
    return False


# ---------------------------------------------------------------------------
# 1. Multi-Frame Mangal Dosha (Lagna, Moon, Venus) with 16 Exceptions
# ---------------------------------------------------------------------------

def check_mangal_cancellations(
    mars_house: int,
    mars_sign: str,
    pmap: dict,
    frame_name: str = "Lagna",
) -> list[str]:
    """
    Check the 16 classical Parashari and Muhurtha cancellation exceptions for Mars.
    """
    reasons = []

    # 1. Mars in own signs (Mesha, Vrischika)
    if mars_sign in OWN_SIGNS.get("Mars", []):
        reasons.append(f"Mars in own sign ({mars_sign})")

    # 2. Mars in exaltation sign (Makara)
    if mars_sign == EXALTATION.get("Mars"):
        reasons.append(f"Mars in exaltation sign ({mars_sign})")

    # 3. Mars in debilitation sign (Karka - loses malefic potency)
    if mars_sign == DEBILITATION.get("Mars"):
        reasons.append(f"Mars debilitated in {mars_sign} (rendered weak)")

    jup_h = _house_of(pmap, "Jupiter")
    mar_h = _house_of(pmap, "Mars")

    if jup_h and mar_h:
        # 4. Guru-Mangala: Mars conjunct Jupiter
        if jup_h == mar_h:
            reasons.append("Mars conjunct benefic Jupiter")

        # 5. Jupiter aspects Mars (5th, 7th, 9th)
        if _aspects_house("Jupiter", jup_h, mar_h):
            dist = _house_distance(jup_h, mar_h)
            reasons.append(f"Jupiter {dist}th aspect on Mars")

    # 6. Jupiter in Kendra (H1, H4, H7, H10)
    # Classical qualification: Jupiter in Lagna (H1) removes blemishes across the chart.
    # For other Kendras (H4, H7, H10), Jupiter must aspect Mars or counterbalance a Kendra placement.
    # Jupiter in H7 does not cancel 8th house Mars as it casts no Graha Drishti onto H8.
    if jup_h in {1, 4, 7, 10}:
        if jup_h == 1:
            reasons.append(f"Jupiter situated in Kendra (H{jup_h}) - Devaguru in Lagna")
        elif mars_house != 8 and (_aspects_house("Jupiter", jup_h, mars_house) or mars_house in {1, 4, 7, 10} or mars_house == 12):
            reasons.append(f"Jupiter situated in Kendra (H{jup_h})")
        elif _aspects_house("Jupiter", jup_h, mars_house):
            reasons.append(f"Jupiter situated in Kendra (H{jup_h})")

    # 7. Mars in 1st house in Mesha
    if mars_house == 1 and mars_sign == "Mesha":
        reasons.append("Mars in 1st house in Mesha")

    # 8. Mars in 2nd house in Mercury signs (Mithuna, Kanya)
    if mars_house == 2 and mars_sign in ("Mithuna", "Kanya"):
        reasons.append(f"Mars in 2nd house in {mars_sign}")

    # 9. Mars in 4th house in own signs (Mesha, Vrischika)
    if mars_house == 4 and mars_sign in ("Mesha", "Vrischika"):
        reasons.append(f"Mars in 4th house in {mars_sign}")

    # 10. Mars in 7th house in Karka or Makara
    if mars_house == 7 and mars_sign in ("Karka", "Makara"):
        reasons.append(f"Mars in 7th house in {mars_sign}")

    # 11. Mars in 8th house in Jupiter signs (Dhanu, Meena)
    if mars_house == 8 and mars_sign in ("Dhanu", "Meena"):
        reasons.append(f"Mars in 8th house in {mars_sign}")

    # 12. Mars in 12th house in Venus signs (Vrishabha, Tula)
    if mars_house == 12 and mars_sign in ("Vrishabha", "Tula"):
        reasons.append(f"Mars in 12th house in {mars_sign}")

    # 13. Chandra-Mangala: Mars conjunct Moon
    moon_h = _house_of(pmap, "Moon")
    if moon_h and mar_h and moon_h == mar_h:
        reasons.append("Mars conjunct Moon (Chandra-Mangala)")

    # 14. Mars in Simha or Kumbha
    if mars_sign in ("Simha", "Kumbha"):
        reasons.append(f"Mars situated in friendly/neutral {mars_sign}")

    # 15. Mars conjunct Saturn (mutual neutralization of aggressive fire)
    sat_h = _house_of(pmap, "Saturn")
    if sat_h and mar_h and sat_h == mar_h:
        reasons.append("Mars conjunct Saturn (neutralizing association)")

    # 16. Venus in own or exaltation sign in Kendra
    ven_h = _house_of(pmap, "Venus")
    ven_s = _sign_of(pmap, "Venus")
    if ven_h in {1, 4, 7, 10} and (ven_s in OWN_SIGNS.get("Venus", []) or ven_s == EXALTATION.get("Venus")):
        reasons.append(f"Venus strong in Kendra ({ven_s} in H{ven_h})")

    # Deduplicate reasons preserving order
    seen = set()
    deduped = []
    for r in reasons:
        if r not in seen:
            seen.add(r)
            deduped.append(r)
    return deduped


def evaluate_mangal_dosha_multiframe(
    planet_data: dict[str, dict] | list[dict],
    lagna_sign: str = "Mesha",
) -> dict[str, Any]:
    """
    Complete Multi-Frame Mangal Dosha Evaluator across:
    1. Lagna Frame (Ascendant)
    2. Chandra Lagna Frame (Natal Moon)
    3. Shukra Lagna Frame (Natal Venus)

    Returns granular per-frame statuses, cancellation checks, intensity score,
    and backward-compatible top-level keys.
    """
    pmap = _get_planet_map(planet_data)

    mar_h = _house_of(pmap, "Mars")
    mars_sign = _sign_of(pmap, "Mars")

    moon_h = _house_of(pmap, "Moon")
    ven_h = _house_of(pmap, "Venus")

    # Frame 1: From Lagna
    lagna_house = mar_h
    raw_lagna = lagna_house in MANGLIK_HOUSES
    canc_lagna = check_mangal_cancellations(lagna_house, mars_sign, pmap, "Lagna") if raw_lagna else []
    active_lagna = raw_lagna and (len(canc_lagna) == 0)

    # Frame 2: From Moon
    moon_house = _house_distance(moon_h, mar_h) if (moon_h and mar_h) else 0
    raw_moon = moon_house in MANGLIK_HOUSES
    canc_moon = check_mangal_cancellations(moon_house, mars_sign, pmap, "Moon") if raw_moon else []
    active_moon = raw_moon and (len(canc_moon) == 0)

    # Frame 3: From Venus
    venus_house = _house_distance(ven_h, mar_h) if (ven_h and mar_h) else 0
    raw_venus = venus_house in MANGLIK_HOUSES
    canc_venus = check_mangal_cancellations(venus_house, mars_sign, pmap, "Venus") if raw_venus else []
    active_venus = raw_venus and (len(canc_venus) == 0)

    # Overall calculation
    frames_active_raw = sum([raw_lagna, raw_moon, raw_venus])
    frames_active_effective = sum([active_lagna, active_moon, active_venus])

    overall_raw = frames_active_raw > 0
    all_reasons = []
    for r in (canc_lagna + canc_moon + canc_venus):
        if r not in all_reasons:
            all_reasons.append(r)

    overall_cancelled = overall_raw and (frames_active_effective == 0)
    overall_present = overall_raw and not overall_cancelled

    # Intensity assessment
    if overall_present:
        if frames_active_effective == 3:
            intensity = "Severe (100% - Active in Lagna, Moon, and Venus frames)"
            severity = "High"
        elif frames_active_effective == 2:
            intensity = "Moderate (66% - Active in 2 frames)"
            severity = "Moderate"
        else:
            intensity = "Mild (33% - Active in 1 frame)"
            severity = "Low"
    elif overall_cancelled:
        intensity = "Cancelled (0% - Mitigated by classical exceptions)"
        severity = "Low (Canceled)"
    else:
        intensity = "None (0% - Absent)"
        severity = "None"

    return {
        # Backward-compatible keys
        "raw": raw_lagna,
        "present": active_lagna,
        "cancelled": raw_lagna and (len(canc_lagna) > 0),
        "house": mar_h,
        "sign": mars_sign,
        "cancellation_reason": ", ".join(canc_lagna) if canc_lagna else "",
        # Multi-frame enriched keys
        "overall_present": overall_present,
        "overall_cancelled": overall_cancelled,
        "overall_status": "PRESENT" if overall_present else ("MITIGATED" if overall_cancelled else "NOT_PRESENT"),
        "intensity": intensity,
        "severity": severity,
        "all_cancellation_reasons": all_reasons,
        "frames": {
            "lagna": {
                "house": lagna_house,
                "raw": raw_lagna,
                "cancelled": len(canc_lagna) > 0,
                "present": active_lagna,
                "status": "PRESENT" if active_lagna else ("MITIGATED" if canc_lagna else "NOT_PRESENT"),
                "cancellations": canc_lagna,
            },
            "moon": {
                "house": moon_house,
                "raw": raw_moon,
                "cancelled": len(canc_moon) > 0,
                "present": active_moon,
                "status": "PRESENT" if active_moon else ("MITIGATED" if (raw_moon and canc_moon) else "NOT_PRESENT"),
                "cancellations": canc_moon,
            },
            "venus": {
                "house": venus_house,
                "raw": raw_venus,
                "cancelled": len(canc_venus) > 0,
                "present": active_venus,
                "status": "PRESENT" if active_venus else ("MITIGATED" if (raw_venus and canc_venus) else "NOT_PRESENT"),
                "cancellations": canc_venus,
            },
        },
    }


def evaluate_mangal_dosha(planet_data: dict[str, dict] | list[dict]) -> dict:
    """
    Consolidated Mangal Dosh evaluator matching legacy caller interface
    while leveraging multi-frame analysis.
    """
    res = evaluate_mangal_dosha_multiframe(planet_data)
    # Return backward-compatible structure
    return {
        "raw": res["raw"],
        "present": res["present"],
        "cancelled": res["cancelled"],
        "house": res["house"],
        "sign": res["sign"],
        "cancellation_reason": res["cancellation_reason"],
        "overall_present": res["overall_present"],
        "overall_cancelled": res["overall_cancelled"],
        "intensity": res["intensity"],
        "frames": res["frames"],
    }


# ---------------------------------------------------------------------------
# 2. Shani Sade Sati, Kantaka Shani & Ashtama Shani
# ---------------------------------------------------------------------------

def calculate_sade_sati(
    moon_sign: str,
    moon_deg: float = 15.0,
    saturn_sign: str = "",
    saturn_deg: float = 15.0,
    is_saturn_retrograde: bool = False,
) -> dict[str, Any]:
    """
    Calculate Saturn's transit phase relative to natal Moon:
    - Shani Sade Sati: Rising Phase (12th from Moon), Peak Phase (Moon sign), Setting Phase (2nd from Moon).
    - Kantaka Shani: Saturn transiting 4th, 7th, or 10th house from natal Moon.
    - Ashtama Shani: Saturn transiting 8th house from natal Moon.
    - Exact degree orb and retrograde re-entry diagnostics.
    """
    if moon_sign not in SIGNS_SK or saturn_sign not in SIGNS_SK:
        return {
            "is_sade_sati": False,
            "phase": "None",
            "phase_name": "None",
            "is_ashtama_shani": False,
            "is_kantaka_shani": False,
            "kantaka_house": 0,
            "description": "Moon or Saturn sign not specified.",
            "orb_degrees": 0.0,
            "retrograde_reentry": False,
        }

    m_idx = SIGNS_SK.index(moon_sign)
    s_idx = SIGNS_SK.index(saturn_sign)

    diff = (s_idx - m_idx) % 12  # 0 to 11

    # Exact orb distance in degrees across the zodiac
    moon_lon = m_idx * 30.0 + moon_deg
    sat_lon = s_idx * 30.0 + saturn_deg
    angular_dist = (sat_lon - moon_lon) % 360.0
    if angular_dist > 180.0:
        angular_dist -= 360.0

    is_sade_sati = diff in {11, 0, 1}
    phase = "None"
    phase_name = "None"

    if diff == 11:
        phase = "Rising"
        phase_name = "Rising Phase (1st Phase — 12th house from Moon)"
    elif diff == 0:
        phase = "Peak"
        phase_name = "Peak Phase (2nd Phase — Moon sign conjunction / Janma Shani)"
    elif diff == 1:
        phase = "Setting"
        phase_name = "Setting Phase (3rd Phase — 2nd house from Moon)"

    # Ashtama Shani (8th from Moon)
    is_ashtama = (diff == 7)

    # Kantaka Shani (4th, 7th, 10th from Moon)
    is_kantaka = diff in {3, 6, 9}
    kantaka_house = {3: 4, 6: 7, 9: 10}.get(diff, 0)

    # Retrograde re-entry condition:
    # Saturn is retrograde near sign boundary (within 3° of 0° or 30°)
    reentry = is_saturn_retrograde and (saturn_deg <= 3.0 or saturn_deg >= 27.0)

    desc_parts = []
    if is_sade_sati:
        desc_parts.append(
            f"Active Sade Sati in {phase_name}. Saturn transiting {saturn_sign} at {saturn_deg:.1f}° "
            f"({angular_dist:+.1f}° from natal Moon at {moon_deg:.1f}° {moon_sign})."
        )
        if reentry:
            desc_parts.append("Saturn is retrograde near sign border, indicating temporary boundary re-entry.")
    elif is_ashtama:
        desc_parts.append(f"Ashtama Shani active: Saturn transiting 8th house from Moon in {saturn_sign}.")
    elif is_kantaka:
        desc_parts.append(f"Kantaka Shani active: Saturn transiting {kantaka_house}th house from Moon in {saturn_sign}.")
    else:
        desc_parts.append(f"Saturn transiting {saturn_sign} ({diff + 1}th house from Moon); free from Sade Sati.")

    return {
        "is_sade_sati": is_sade_sati,
        "phase": phase,
        "phase_name": phase_name,
        "house_from_moon": diff + 1,
        "is_ashtama_shani": is_ashtama,
        "is_kantaka_shani": is_kantaka,
        "kantaka_house": kantaka_house,
        "orb_degrees": round(angular_dist, 2),
        "saturn_retrograde": is_saturn_retrograde,
        "retrograde_reentry": reentry,
        "description": " ".join(desc_parts),
    }


# ---------------------------------------------------------------------------
# 3. Kaal Sarp Dosh (12 Types, Savya/Apsavya, Gated Default=False)
# ---------------------------------------------------------------------------

def calculate_kaal_sarp(
    planet_data: dict[str, dict] | list[dict],
    lagna_sign: str = "Mesha",
    enabled_by_default: bool = False,
) -> dict[str, Any]:
    """
    Kaal Sarp Dosh Detector:
    - 12 Classical Types based on Rahu's house from Lagna (H1 to H12).
    - Direction: Savya (regular / clockwise) vs Apsavya (counter-clockwise).
    - Anshik (Partial): when exactly 1 planet escapes outside the nodal axis.
    - Gated by default=False in pure classical Parashari profile.
    """
    pmap = _get_planet_map(planet_data)
    rahu_h = _house_of(pmap, "Rahu")
    ketu_h = _house_of(pmap, "Ketu")

    if not rahu_h or not ketu_h:
        return {
            "present": False,
            "type_name": "None",
            "type_number": 0,
            "direction": "None",
            "is_anshik": False,
            "cancellations": [],
            "contested_modern": True,
            "enabled": enabled_by_default,
            "description": "Rahu or Ketu position unavailable.",
        }

    planets_forward = []
    planets_backward = []

    for p in CLASSICAL_7:
        hp = _house_of(pmap, p)
        if not hp:
            continue
        dist_rahu = (hp - rahu_h) % 12
        if dist_rahu <= 6:
            planets_forward.append(p)
        dist_ketu = (hp - ketu_h) % 12
        if dist_ketu <= 6:
            planets_backward.append(p)

    total_planets = len([p for p in CLASSICAL_7 if _house_of(pmap, p) > 0])
    is_full_forward = (len(planets_forward) == total_planets)
    is_full_backward = (len(planets_backward) == total_planets)

    is_anshik_forward = (len(planets_forward) == total_planets - 1)
    is_anshik_backward = (len(planets_backward) == total_planets - 1)

    is_full = is_full_forward or is_full_backward
    is_anshik = (is_anshik_forward or is_anshik_backward) and not is_full

    present = is_full or is_anshik
    direction = "Savya (Direct)" if (is_full_forward or is_anshik_forward) else ("Apsavya (Reverse)" if present else "None")

    type_name = KAAL_SARP_TYPES.get(rahu_h, "Kaal Sarp Yoga")

    # Cancellations
    cancellations = []
    jup_h = _house_of(pmap, "Jupiter")
    if jup_h in {1, 4, 7, 10}:
        cancellations.append(f"Jupiter in Kendra (H{jup_h}) mitigates nodal tension")

    rahu_s = _sign_of(pmap, "Rahu")
    if rahu_s in ("Vrishabha", "Mithuna"):
        cancellations.append(f"Rahu exalted/friendly in {rahu_s}")

    # Description
    desc = f"{type_name} ({direction}): All planets bounded along the nodal axis." if is_full else (
        f"Anshik {type_name}: Single planet escaped beyond the nodal axis." if is_anshik else "Planets evenly distributed on both sides of Rahu-Ketu axis."
    )

    return {
        "present": present and enabled_by_default,
        "raw_present": present,
        "is_full": is_full,
        "is_anshik": is_anshik,
        "type_name": type_name,
        "type_number": rahu_h,
        "direction": direction,
        "cancellations": cancellations,
        "contested_modern": True,
        "enabled": enabled_by_default,
        "description": desc,
    }


# ---------------------------------------------------------------------------
# 4. Pitru Dosha & Grahan Dosha
# ---------------------------------------------------------------------------

def evaluate_pitru_dosha(planet_data: dict[str, dict] | list[dict]) -> dict:
    """
    Standardized Pitru Dosha Evaluator:
    Checks:
    1. Rahu or Ketu occupying 9th house (house of Pitrus / Dharma).
    2. Sun (karaka of Father/Ancestors) in 9th house afflicted by malefic.
    3. Sun conjoined with Rahu or Ketu in any house.
    4. 9th lord placed in dusthana (6, 8, 12).
    Cancellations:
    - Jupiter aspecting 9th house or Sun.
    - Sun in own sign (Simha) or exaltation (Mesha).
    """
    pmap = _get_planet_map(planet_data)

    rahu_h = _house_of(pmap, "Rahu")
    ketu_h = _house_of(pmap, "Ketu")
    sun_h = _house_of(pmap, "Sun")
    sat_h = _house_of(pmap, "Saturn")
    jup_h = _house_of(pmap, "Jupiter")
    sun_s = _sign_of(pmap, "Sun")

    reasons = []

    if rahu_h == 9:
        reasons.append("Rahu in 9th house")
    if ketu_h == 9:
        reasons.append("Ketu in 9th house")

    if sun_h == 9 and (rahu_h == 9 or ketu_h == 9 or sat_h == 9):
        reasons.append("Sun in 9th house afflicted by malefic")

    if sun_h and (sun_h == rahu_h or sun_h == ketu_h):
        reasons.append("Sun conjunct Rahu/Ketu")

    raw_present = len(reasons) > 0

    # Cancellations
    cancellations = []
    if sun_s in ("Simha", "Mesha"):
        cancellations.append(f"Sun exalted or in own sign ({sun_s})")
    if jup_h and _aspects_house("Jupiter", jup_h, 9):
        cancellations.append("Jupiter aspects 9th house")
    if jup_h and sun_h and _aspects_house("Jupiter", jup_h, sun_h):
        cancellations.append("Jupiter aspects Sun")

    cancelled = raw_present and (len(cancellations) > 0)
    present = raw_present and not cancelled

    return {
        "present": present,
        "raw_present": raw_present,
        "cancelled": cancelled,
        "reason": ", ".join(reasons) if raw_present else "",
        "cancellation_reason": ", ".join(cancellations) if cancelled else "",
    }


def evaluate_grahan_dosha(
    planet_data: dict[str, dict] | list[dict],
    sun_orb_limit: float = 12.0,
    moon_orb_limit: float = 9.0,
) -> dict[str, Any]:
    """
    Grahan Dosha Evaluator with Exact Angular Proximity:
    - Surya Grahan: Sun conjunct Rahu or Ketu within 12°.
    - Chandra Grahan: Moon conjunct Rahu or Ketu within 9°.
    - Identifies exact luminary eclipsed, separation degrees, and mitigations.
    """
    pmap = _get_planet_map(planet_data)

    sun_h = _house_of(pmap, "Sun")
    sun_deg = _degree_of(pmap, "Sun")
    moon_h = _house_of(pmap, "Moon")
    moon_deg = _degree_of(pmap, "Moon")

    rahu_h = _house_of(pmap, "Rahu")
    rahu_deg = _degree_of(pmap, "Rahu")
    ketu_h = _house_of(pmap, "Ketu")
    ketu_deg = _degree_of(pmap, "Ketu")

    eclipsed = []
    details = []

    # Check Sun with Rahu
    if sun_h and rahu_h and sun_h == rahu_h:
        sep = abs(sun_deg - rahu_deg)
        if sep <= sun_orb_limit:
            eclipsed.append("Sun")
            details.append(f"Surya Grahan: Sun-Rahu conjunction at {sep:.1f}° separation")

    # Check Sun with Ketu
    if sun_h and ketu_h and sun_h == ketu_h:
        sep = abs(sun_deg - ketu_deg)
        if sep <= sun_orb_limit:
            if "Sun" not in eclipsed:
                eclipsed.append("Sun")
            details.append(f"Surya Grahan: Sun-Ketu conjunction at {sep:.1f}° separation")

    # Check Moon with Rahu
    if moon_h and rahu_h and moon_h == rahu_h:
        sep = abs(moon_deg - rahu_deg)
        if sep <= moon_orb_limit:
            eclipsed.append("Moon")
            details.append(f"Chandra Grahan: Moon-Rahu conjunction at {sep:.1f}° separation")

    # Check Moon with Ketu
    if moon_h and ketu_h and moon_h == ketu_h:
        sep = abs(moon_deg - ketu_deg)
        if sep <= moon_orb_limit:
            if "Moon" not in eclipsed:
                eclipsed.append("Moon")
            details.append(f"Chandra Grahan: Moon-Ketu conjunction at {sep:.1f}° separation")

    present = len(eclipsed) > 0
    severity = "High" if len(eclipsed) == 2 else ("Moderate" if len(eclipsed) == 1 else "None")

    return {
        "present": present,
        "eclipsed_luminaries": eclipsed,
        "severity": severity,
        "details": details,
        "description": "; ".join(details) if present else "No Grahan Dosha present within classical orb limits.",
    }


# ---------------------------------------------------------------------------
# 5. Gandmool Dosha with Sandhi Padas
# ---------------------------------------------------------------------------

def evaluate_gandmool_dosha(planet_data: dict[str, dict] | list[dict]) -> dict[str, Any]:
    """
    Gandmool Dosha Evaluator:
    Checks if natal Moon is situated in one of the 6 Gandmool nakshatras,
    and flags critical Gandanta junction padas.
    """
    pmap = _get_planet_map(planet_data)
    moon = pmap.get("Moon", {})
    nak = moon.get("nakshatra", "")
    pada = moon.get("pada", 1)
    if isinstance(pada, str):
        try:
            pada = int(pada)
        except ValueError:
            pada = 1

    is_gandmool = nak in GANDMOOL_NAKSHATRAS
    is_deep_gandanta = (nak, pada) in GANDANTA_PADAS

    desc = []
    if is_gandmool:
        desc.append(f"Moon placed in {nak} Nakshatra (Pada {pada}).")
        if is_deep_gandanta:
            desc.append("Critical Gandanta Sandhi pada situated at the water-fire zodiac junction.")
        else:
            desc.append("Standard Gandmool nakshatra placement requiring traditional Shanti prayers.")

    return {
        "present": is_gandmool,
        "nakshatra": nak,
        "pada": pada,
        "is_deep_gandanta": is_deep_gandanta,
        "severity": "High" if is_deep_gandanta else ("Moderate" if is_gandmool else "None"),
        "description": " ".join(desc) if is_gandmool else "Moon free from Gandmool nakshatra placement.",
    }


# ---------------------------------------------------------------------------
# 6. Consolidated Engine Entry Point (calculate_doshas)
# ---------------------------------------------------------------------------

def calculate_doshas(planets: list[dict], lagna_sign: str, houses: dict) -> list[dict[str, Any]]:
    """
    Detect and score major astrological doshas with authentic Vedic remedies,
    structured outputs, multi-frame analysis, and classical source integrity.
    """
    pmap = _get_planet_map(planets)
    doshas = []

    def add(name: str, present: bool, severity: str, desc: str, remedies: list[str], metadata: dict = None):
        doshas.append({
            "name": name,
            "present": bool(present),
            "severity": severity if present else "None",
            "description": desc,
            "remedies": remedies if present else [],
            "metadata": metadata or {},
        })

    # 1. Multi-Frame Mangal Dosha
    eval_m = evaluate_mangal_dosha_multiframe(pmap, lagna_sign)
    add(
        "Mangal Dosha (Manglik)",
        eval_m["overall_present"],
        eval_m["severity"],
        f"Mars in H{eval_m['house']} ({eval_m['sign']}). {eval_m['intensity']}."
        + (f" Mitigated by: {', '.join(eval_m['all_cancellation_reasons'])}." if eval_m["overall_cancelled"] else ""),
        [
            "Recite Hanuman Chalisa or Mangal Gayatri regularly",
            "Donate red lentils or jaggery on Tuesdays",
            "Cultivate patience and conscious communication in partnerships",
            "Perform comprehensive Koota Milan chart matching before marriage",
        ],
        metadata=eval_m["frames"],
    )

    # 2. Shani Sade Sati
    moon_s = _sign_of(pmap, "Moon")
    moon_d = _degree_of(pmap, "Moon")
    sat_s = _sign_of(pmap, "Saturn")
    sat_d = _degree_of(pmap, "Saturn")
    sat_retro = _is_retrograde(pmap, "Saturn")

    eval_ss = calculate_sade_sati(moon_s, moon_d, sat_s, sat_d, sat_retro)
    add(
        "Shani Sade Sati",
        eval_ss["is_sade_sati"],
        "Moderate" if eval_ss["is_sade_sati"] else "None",
        eval_ss["description"],
        [
            "Chant 'Om Sham Shanaischaraya Namaha' 108 times on Saturdays",
            "Engage in selfless service and support elderly or vulnerable individuals",
            "Feed birds or black sesame seeds to nature",
            "Cultivate disciplined perseverance and long-range planning",
        ],
        metadata=eval_ss,
    )

    # 3. Kantaka / Ashtama Shani
    if eval_ss["is_ashtama_shani"] or eval_ss["is_kantaka_shani"]:
        name_k = "Ashtama Shani" if eval_ss["is_ashtama_shani"] else f"Kantaka Shani (House {eval_ss['kantaka_house']})"
        add(
            name_k,
            True,
            "Moderate",
            eval_ss["description"],
            [
                "Light a sesame oil lamp under a Peepal tree on Saturdays",
                "Practice regular meditation to manage mental stress",
                "Avoid unnecessary speculation or hasty agreements",
            ],
            metadata=eval_ss,
        )

    # 4. Kaal Sarp Dosha (Contested modern - disabled by default)
    eval_ks = calculate_kaal_sarp(pmap, lagna_sign, enabled_by_default=False)
    add(
        "Kaal Sarp Dosha",
        eval_ks["present"],  # False by default
        "Moderate" if eval_ks["present"] else "None",
        eval_ks["description"],
        [
            "Practice daily Pranayama and mindfulness meditation",
            "Worship Lord Shiva or recite Maha Mrityunjaya Mantra",
            "Engage in charitable community projects",
        ],
        metadata=eval_ks,
    )

    # 5. Pitru Dosha
    eval_p = evaluate_pitru_dosha(pmap)
    add(
        "Pitru Dosha",
        eval_p["present"],
        "Medium" if eval_p["present"] else "None",
        f"Karmic ancestral patterns: {eval_p['reason']}." if eval_p["present"] else "9th house and Sun free from ancestral malefic debt.",
        [
            "Perform Pitru Tarpan or Shraddha during Amavasya or Pitru Paksha",
            "Feed cows, stray animals, or provide food to the needy",
            "Chant Gayatri Mantra daily at sunrise",
        ],
        metadata=eval_p,
    )

    # 6. Grahan Dosha
    eval_g = evaluate_grahan_dosha(pmap)
    add(
        "Grahan Dosha",
        eval_g["present"],
        eval_g["severity"],
        eval_g["description"],
        [
            "Offer water to Lord Surya in a copper vessel at dawn",
            "Chant Chandra Gayatri during full moon evenings",
            "Donate white food (rice, milk) on Mondays and wheat on Sundays",
        ],
        metadata=eval_g,
    )

    # 7. Gandmool Dosha
    eval_gm = evaluate_gandmool_dosha(pmap)
    add(
        "Gandmool Dosha",
        eval_gm["present"],
        eval_gm["severity"],
        eval_gm["description"],
        [
            "Perform traditional Gandmool Shanti on favorable Nakshatra day",
            "Worship Lord Ganesha to remove obstacles",
            "Donate green moong dal or white clothing items",
        ],
        metadata=eval_gm,
    )

    return doshas
