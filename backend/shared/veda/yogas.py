"""
Classical Vedic Astrology Yogas Detection Engine (Pure Shared Library).

Drives classical yoga detection across the 70-rule Parashari yoga catalog,
providing backward compatibility with existing callers while delivering enriched
rule metadata, cancellation tracking, and classical source references.
"""

from __future__ import annotations

from typing import Any

from .yoga_catalog import (
    CATALOG,
    YogaRule,
    evaluate_yoga_catalog,
    evaluate_yoga_rule,
    get_planet_map,
    house_of,
    sign_of,
)

KENDRA = {1, 4, 7, 10}
TRIKONA = {1, 5, 9}
DUSTHANA = {6, 8, 12}


def calculate_yogas(
    planets: list[dict],
    lagna_sign: str,
    houses: dict,
    include_disabled: bool = False,
) -> list[dict[str, Any]]:
    """
    Detect and score classical Vedic yogas in a natal chart.
    
    Evaluates the full 70-rule catalog. Each returned dict contains:
      - name: str (e.g. 'Gajakesari Yoga')
      - description: str
      - present: bool (True only if predicate holds AND uncancelled)
      - strength: str ('Strong', 'Medium', 'Weak', or 'Absent')
      - rule_id: str
      - category: str
      - source_reference: str
      - cancelled: bool
      - cancellation_reason: str or None
      - contested_modern: bool
      - enabled_by_default: bool
      - details: list[str]
    """
    return evaluate_yoga_catalog(planets, lagna_sign, houses, include_disabled=include_disabled)


def calculate_yogas_v2(
    planets: list[dict],
    lagna_sign: str,
    houses: dict,
    include_disabled: bool = False,
) -> list[dict[str, Any]]:
    """Alias for calculate_yogas with explicit v2 naming."""
    return evaluate_yoga_catalog(planets, lagna_sign, houses, include_disabled=include_disabled)


def detect_advanced_yogas(chart: dict) -> list[str]:
    """Lightweight yogas extractor returning list of active uncancelled yoga names."""
    planets = []
    planets_by_house = chart.get("planets_by_house", {})
    for h, p_list in planets_by_house.items():
        for p in p_list:
            p_copy = dict(p)
            p_copy["house"] = int(h)
            planets.append(p_copy)

    lagna = chart.get("basic_details", {}).get("lagna", "Mesha")
    yogas = calculate_yogas(planets, lagna, {})
    return [y["name"] for y in yogas if y["present"]]
