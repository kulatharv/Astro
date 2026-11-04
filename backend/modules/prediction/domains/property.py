"""Property & Home Domain Evaluator."""

from modules.prediction.scoring import (
    _score_planets_in_houses, _score_house_lord, _dasha_activates,
    _pct, _ordinal
)
from modules.prediction.remedies import _timing_windows, _build_remedies
from shared.veda.property import evaluate_property_rules, PROPERTY_SAFETY_DISCLAIMER


def analyse_property(ctx: dict) -> dict:
    """
    Analyse traditional cultural and astrological symbolism regarding property,
    domestic residence, real estate, relocation, and construction themes using
    the canonical Parashari rule pack.

    Strictly non-deterministic: NEVER guarantees property purchases, sales, prices,
    appreciation, mortgage/loan approvals, or legal ownership/dispute outcomes.
    Preserves 100% backward compatibility with legacy API contracts.
    """
    pm = ctx["planet_map"]
    hl = ctx["house_lords"]

    mars = pm.get("Mars", {})
    moon = pm.get("Moon", {})
    saturn = pm.get("Saturn", {})
    lord_4 = hl[4]
    l4d = pm.get(lord_4, {})
    h4_occ = [p for p, d in pm.items() if d.get("house") == 4]

    base = _score_planets_in_houses(ctx, [4, 2, 12])
    l4s = _score_house_lord(ctx, 4)
    m_sc = mars.get("str_score", 0) + (2 if mars.get("house") in (4, 2) else 0)
    total = base + l4s + m_sc

    dasha_active = _dasha_activates(ctx, [4, 12, 2])
    pct = _pct(50, total, 8 if dasha_active else 0)

    # Evaluate canonical WP5G property rules across 7 dimensions + D4 Chaturthamsa
    rule_evidence = evaluate_property_rules(ctx)

    sign4 = ctx.get("house_signs", {}).get(4, "Mesha")
    PROP_TYPE = {
        "Mesha": "independent house / active environment preferred",
        "Vrishabha": "fertile land, luxurious property, garden",
        "Mithuna": "apartment in busy area, multi-story building",
        "Karka": "near water body, ancestral property",
        "Simha": "large prestigious property, prominent location",
        "Kanya": "clean, hygienic, well-organized living space",
        "Tula": "beautiful, artistically designed home",
        "Vrischika": "old or hidden property, secretive location",
        "Dhanu": "property near temples, open land, hills",
        "Makara": "durable construction, traditional or stone buildings",
        "Kumbha": "modern housing society, tech-enabled home",
        "Meena": "near sea, spiritual property, irregular shape",
    }
    prop_type = PROP_TYPE.get(sign4, "varied property types")

    multiple_props = mars.get("str_score", 0) >= 2 or (mars.get("house") == 4 and "Mars" in h4_occ)
    domestic_happiness = "Moon" in h4_occ or moon.get("house") == 4 or moon.get("str_score", 0) >= 1

    timing = _timing_windows(ctx, [4, 2, 12], "property")
    remedies = _build_remedies(ctx, ["Mars"] if m_sc < 0 else [], "property")

    active_rules = rule_evidence.get("active_rules_count", 0)
    analysis_text = (
        f"4th house (property) ruled by {lord_4} in {_ordinal(l4d.get('house', 1))} house — {l4d.get('strength', '')}. "
        f"Property type: {prop_type}. Mars (real estate karaka) in {_ordinal(mars.get('house', 1))} house. "
        f"{('Multiple property indicators present in chart.' if multiple_props else '')} "
        f"Timing window for real estate focus: {timing.get('best_window', 'N/A')}. "
        f"({active_rules} canonical property rules evaluated across 7 dimensions)."
    )

    return {
        # Legacy contract keys (100% backward compatible)
        "domain": "Property & Home",
        "icon": "⌂",
        "score": pct,
        "property_type": prop_type,
        "multiple_properties": multiple_props,
        "domestic_happiness": domestic_happiness,
        "vastu": "4th house in earthy signs — vastu compliance highly beneficial" if sign4 in ("Vrishabha", "Kanya", "Makara") else "Standard vastu principles apply",
        "fourth_lord": f"{lord_4} in {_ordinal(l4d.get('house', 0))}H — {l4d.get('strength', '')}",
        "mars_position": f"Mars in {_ordinal(mars.get('house', 1))}H — {mars.get('strength', '')}",
        "dasha_active": dasha_active,
        "timing": timing,
        "remedies": remedies,
        "analysis": analysis_text,

        # WP5G Canonical Rule Evidence & Dimensions
        "evidence": rule_evidence,
        "evidence_ledger": rule_evidence.get("evidence_ledger", []),
        "dimensions": rule_evidence.get("dimensions", {}),
        "overall_dimension_score": rule_evidence.get("overall_score", 50.0),
        "active_rules_count": active_rules,
        "d4_chart": rule_evidence.get("d4_chart", {}),
        "d4_status": "VERIFIED_ACTIVE",
        "safety_disclaimer": PROPERTY_SAFETY_DISCLAIMER,
        "is_predictive": False,
        "is_financial_advice": False,
    }


_property = analyse_property
