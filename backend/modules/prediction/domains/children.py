"""
Children & Progeny Domain Evaluator (Non-Diagnostic & Culturally Framed).
Integrates pure Parashari children/progeny rule evaluation with strict reproductive safety guardrails
and 100% backward compatibility with legacy API contracts.
"""

from modules.prediction.scoring import (
    _score_planets_in_houses, _score_house_lord, _dasha_activates,
    _dosha_present, _yoga_present, _pct, _ordinal
)
from modules.prediction.remedies import _timing_windows, _build_remedies
from shared.veda.progeny import evaluate_progeny_rules, SAFETY_DISCLAIMER


def analyse_children(ctx: dict) -> dict:
    """
    Analyse traditional cultural and astrological symbolism regarding family caregiving,
    youth mentorship, and generational continuity using deterministic Parashari rule pack.
    Strictly non-diagnostic: NEVER predicts conception, pregnancy, infertility, child count,
    fetal gender/sex (PC-PNDT Act compliance), or child mortality/health.
    Preserves 100% backward compatibility with legacy API contracts.
    """
    pm = ctx["planet_map"]
    hl = ctx["house_lords"]

    jupiter = pm.get("Jupiter", {})
    sun = pm.get("Sun", {})
    moon = pm.get("Moon", {})

    lord_5 = hl[5]
    l5d = pm.get(lord_5, {})
    h5_occ = [p for p, d in pm.items() if d.get("house") == 5]
    h9_occ = [p for p, d in pm.items() if d.get("house") == 9]

    base = _score_planets_in_houses(ctx, [5, 9, 1])
    l5s = _score_house_lord(ctx, 5)
    j_sc = jupiter.get("str_score", 0) + (2 if jupiter.get("house") in (5, 9, 1) else 0)
    total = base + l5s + j_sc

    dasha_active = _dasha_activates(ctx, [5, 9])
    pct = _pct(50, total, 10 if dasha_active else 0)

    # Evaluate canonical WP5F non-diagnostic progeny rules across 5 safe dimensions
    rule_evidence = evaluate_progeny_rules(ctx)

    putra_dosh = _dosha_present(ctx, ["Putra", "Santana"])
    santana_yoga = _yoga_present(ctx, ["Santana", "Putra"])

    # Non-deterministic, safe reflections replacing child count and medical speculation
    # Strictly avoids counting children or predicting reproductive difficulty
    count_indicator = (
        "Supportive orientation for family caregiving and youth guidance"
        if pct >= 55
        else "Balanced, mindful pacing advised for family life"
    )

    # Neutral cultural reflection replacing illegal and unscientific fetal sex prediction
    gender_indicator = "Balanced cultural and lineage reflection"

    # Creative / mentorship inclination reflection
    if "Jupiter" in h5_occ or "Mercury" in h5_occ:
        nature_desc = "creative, scholarly, and inquisitive"
    elif "Mars" in h5_occ:
        nature_desc = "energetic, determined, and dynamic"
    elif "Venus" in h5_occ or "Moon" in h5_occ:
        nature_desc = "artistic, empathetic, and sensitive"
    elif "Saturn" in h5_occ:
        nature_desc = "disciplined, thoughtful, and mature"
    else:
        nature_desc = "independent and intellectually bright"

    child_nature = f"Mentorship themes reflect {nature_desc} inclinations"

    timing = _timing_windows(ctx, [5, 9], "children")
    remedies = _build_remedies(ctx, ["Jupiter"] if j_sc < 0 else [], "children")

    total_rules = len(rule_evidence.get("matched_rules", [])) + len(rule_evidence.get("rejected_rules", []))

    return {
        "domain": "Children & Next Generation",
        "icon": "❋",
        "score": pct,
        "count_indicator": count_indicator,
        "gender_indicator": gender_indicator,
        "child_nature": child_nature,
        "putra_dosh": putra_dosh,
        "santana_yoga": santana_yoga,
        "fifth_lord": f"{lord_5} in {_ordinal(l5d.get('house', 0))}H — {l5d.get('strength', '')}",
        "h5_planets": h5_occ,
        "jupiter_position": f"Jupiter in {_ordinal(jupiter.get('house', 1))}H — {jupiter.get('strength', '')}",
        "dasha_active": dasha_active,
        "timing": timing,
        "remedies": remedies,
        "analysis": _children_narrative(ctx, pct, lord_5, l5d, jupiter, rule_evidence),
        # WP5F Canonical Rule Evaluation Evidence
        "evidence": rule_evidence,
        "dimensions": rule_evidence.get("dimensions", {}),
        "rules_evaluated": total_rules,
        "d7_status": rule_evidence.get("d7_status", "VERIFIED_ACTIVE"),
        "is_diagnostic": False,
        "safety_disclaimer": SAFETY_DISCLAIMER,
    }


def _children_narrative(ctx: dict, pct: int, lord_5: str, l5d: dict, jupiter: dict, rule_evidence: dict) -> str:
    parts = []
    parts.append(
        f"Within traditional Parashari principles, the 5th house and Jupiter represent youth mentorship, intellectual creativity, and family caregiving. "
        f"Jupiter (wisdom karaka) is in the {_ordinal(jupiter.get('house', 1))} house ({jupiter.get('strength', 'Neutral')}). "
        f"5th lord {lord_5} is placed in the {_ordinal(l5d.get('house', 1))} house."
    )

    dims = rule_evidence.get("dimensions", {})
    caregiving_st = dims.get("family_caregiving_values", {}).get("status", "")
    if caregiving_st:
        parts.append(f"Family Caregiving Alignment: {caregiving_st}.")

    mentorship_st = dims.get("intellectual_mentorship", {}).get("status", "")
    if mentorship_st:
        parts.append(f"Intellectual Mentorship Profile: {mentorship_st}.")

    continuity_st = dims.get("next_gen_continuity", {}).get("status", "")
    if continuity_st:
        parts.append(f"Generational Continuity: {continuity_st}.")

    return " ".join(parts)


_children = analyse_children
analyse_progeny = analyse_children
