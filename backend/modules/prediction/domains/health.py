"""
Health & Wellbeing Domain Evaluator (Non-Diagnostic).
Integrates pure Parashari wellbeing rule evaluation with strict medical safety guardrails
and 100% backward compatibility with legacy API contracts.
"""

from modules.prediction.scoring import (
    _score_planets_in_houses, _score_house_lord, _dasha_activates,
    _pct, _ordinal
)
from modules.prediction.remedies import _timing_windows, _build_remedies
from shared.veda.health import evaluate_health_rules, SAFETY_DISCLAIMER


def analyse_health(ctx: dict) -> dict:
    """
    Analyse general wellbeing and lifestyle habits using deterministic Parashari rule pack.
    Strictly non-diagnostic: never predicts disease, death, surgeries, or medical treatments.
    Preserves 100% backward compatibility with legacy API contracts.
    """
    pm  = ctx["planet_map"]
    hl  = ctx["house_lords"]

    sun    = pm.get("Sun", {})
    moon   = pm.get("Moon", {})
    saturn = pm.get("Saturn", {})
    mars   = pm.get("Mars", {})

    lord_1 = hl[1]; l1d = pm.get(lord_1, {})

    base   = _score_planets_in_houses(ctx, [1, 5, 9])
    l1s    = _score_house_lord(ctx, 1)
    sun_sc = sun.get("str_score", 0)
    total  = base + l1s + sun_sc

    dasha_active = _dasha_activates(ctx, [1, 5, 9])
    # Positive vitality and routine alignment index (0-100), not a medical disease risk score
    pct = _pct(65, total, 5 if dasha_active else 0)

    # Evaluate canonical WP5D non-diagnostic wellbeing rules across 4 dimensions
    rule_evidence = evaluate_health_rules(ctx)

    lagna_sign = ctx.get("lagna", "Mesha")
    DOSHA_MAP = {
        "Mesha": "Pitta", "Vrishabha": "Kapha", "Mithuna": "Vata", "Karka": "Kapha",
        "Simha": "Pitta", "Kanya": "Vata", "Tula": "Vata", "Vrischika": "Pitta",
        "Dhanu": "Pitta", "Makara": "Vata", "Kumbha": "Vata", "Meena": "Kapha",
    }
    ayurvedic_dosha = DOSHA_MAP.get(lagna_sign, "Tridoshic")

    # Safe, non-diagnostic lifestyle and routine areas (replacing anatomical organ vulnerability)
    weak_organs = "digestive rhythm and hydration balance"
    lagna_organs = "overall constitutional vitality and daily stamina"

    # Non-diagnostic stress pacing reflection (replacing psychiatric diagnosis)
    moon_h = moon.get("house", 1)
    moon_calm = moon.get("str_score", 0) >= 0 and moon_h not in (6, 8, 12)
    emotional_sensitivity = "balanced" if moon_calm else "mindful pacing advised"

    # Preventive healthcare focus (replacing surgical event predictions)
    wellness_focus = False
    wellness_txt = (
        "Planetary alignment reminds to maintain balanced daily sleep hygiene, wholesome nutrition, "
        "and routine checkups with licensed medical professionals."
    )

    disease_periods = (
        "General wellbeing focus: prioritize regular rest, hydration, and steady daily routines "
        "during demanding work phases."
    )

    timing   = _timing_windows(ctx, [1, 5, 9], "health")
    remedies = _build_remedies(
        ctx,
        ["Sun"] if sun.get("str_score", 0) < 0 else (["Mars"] if mars.get("str_score", 0) < 0 else ["Saturn"]),
        "health",
    )

    return {
        "domain": "Health & Wellbeing",
        "icon": "✚",
        "score": pct,
        "weak_organs": weak_organs,
        "lagna_organs": lagna_organs,
        "ayurvedic_dosha": ayurvedic_dosha,
        "emotional_sensitivity": emotional_sensitivity,
        "wellness_focus": wellness_focus,
        "surgery_risk": False,
        "wellness_txt": wellness_txt,
        "arishta_doshas": [],  # Neutralized: exclude fatalistic mortality predictions
        "disease_periods": disease_periods,
        "first_lord": f"{lord_1} in {_ordinal(l1d.get('house', 0))}H — {l1d.get('strength', '')}",
        "dasha_active": dasha_active,
        "timing": timing,
        "remedies": remedies,
        "analysis": _health_narrative(ctx, pct, ayurvedic_dosha, moon_calm, rule_evidence),
        # WP5D Canonical Rule Evaluation Evidence
        "evidence": rule_evidence,
        "dimensions": rule_evidence.get("dimensions", {}),
        "rules_evaluated": len(rule_evidence.get("matched_rules", [])) + len(rule_evidence.get("rejected_rules", [])),
        "safety_disclaimer": SAFETY_DISCLAIMER,
    }


def _health_narrative(ctx, pct, dosha, moon_calm, rule_evidence=None):
    lagna = ctx.get("lagna", "")
    sun = ctx["planet_map"].get("Sun", {})
    parts = []
    parts.append(
        f"Your Ascendant in {lagna} reflects a traditional Ayurvedic {dosha} temperament — "
        f"focus on aligning daily routines, wholesome nourishment, and seasonal balance."
    )
    parts.append(
        f"Sun (vitality indicator) is in the {_ordinal(sun.get('house', 1))} house — "
        f"{sun.get('strength', 'Neutral')}."
    )
    if moon_calm:
        parts.append("Lunar placement supports emotional equilibrium and steady sleep hygiene.")
    else:
        parts.append("Active mental pace suggests prioritizing screen-free relaxation and mindful breathing pauses.")

    if rule_evidence and "dimensions" in rule_evidence:
        dims = rule_evidence["dimensions"]
        vit_st = dims.get("vitality_stamina", {}).get("status", "Supportive")
        rout_st = dims.get("routine_balance", {}).get("status", "Supportive")
        parts.append(f"Lifestyle dimensions indicate: vitality stamina is {vit_st}; routine balance is {rout_st}.")

    parts.append(
        "Important: Astrological interpretations are cultural lifestyle reflections only and do not constitute "
        "medical diagnosis or treatment. For all health and medical questions, always consult a licensed healthcare professional."
    )
    return " ".join(parts)


_health = analyse_health
