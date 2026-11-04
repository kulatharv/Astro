"""
Education & Learning Domain Evaluator.
Integrates pure Parashari education rule evaluation with strict educational safety guardrails
and 100% backward compatibility with legacy API contracts.
"""

from modules.prediction.scoring import (
    _score_planets_in_houses, _score_house_lord, _dasha_activates,
    _yoga_present, _pct, _ordinal
)
from modules.prediction.remedies import _timing_windows, _build_remedies
from shared.veda.education import evaluate_education_rules, SAFETY_DISCLAIMER


def analyse_education(ctx: dict) -> dict:
    """
    Analyse education, scholarship, and learning tendencies using deterministic Parashari rule pack.
    Strictly non-deterministic: never predicts exam pass/fail, marks, admissions, or IQ.
    Preserves 100% backward compatibility with legacy API contracts.
    """
    pm = ctx["planet_map"]
    hl = ctx["house_lords"]

    mercury = pm.get("Mercury", {})
    jupiter = pm.get("Jupiter", {})
    sun = pm.get("Sun", {})

    lord_4 = hl[4]
    l4d = pm.get(lord_4, {})
    lord_5 = hl[5]
    l5d = pm.get(lord_5, {})

    h4_occ = [p for p, d in pm.items() if d.get("house") == 4]
    h5_occ = [p for p, d in pm.items() if d.get("house") == 5]

    base = _score_planets_in_houses(ctx, [4, 5, 9])
    l4s = _score_house_lord(ctx, 4)
    l5s = _score_house_lord(ctx, 5)
    m_sc = mercury.get("str_score", 0) + (1 if mercury.get("house") in (4, 5, 9) else 0)
    j_sc = jupiter.get("str_score", 0) + (1 if jupiter.get("house") in (4, 5, 9) else 0)
    total = base + l4s + l5s + m_sc + j_sc

    dasha_active = _dasha_activates(ctx, [4, 5, 9])
    pct = _pct(50, total, 8 if dasha_active else 0)

    # Evaluate canonical WP5E educational rules across 6 dimensions
    rule_evidence = evaluate_education_rules(ctx)

    house_signs = ctx.get("house_signs", {})
    sign4 = house_signs.get(4, "Mesha")
    STUDY_FIELDS = {
        "Mesha": "engineering, sports science, defense, physical therapy",
        "Vrishabha": "commerce, arts, agriculture, banking, architecture",
        "Mithuna": "journalism, languages, IT, mass communication, mathematics",
        "Karka": "nursing, psychology, hospitality, history",
        "Simha": "medicine, management, drama, literature, leadership",
        "Kanya": "medicine, accounting, research, editing, pharmacy",
        "Tula": "law, design, diplomacy, social sciences, fine arts",
        "Vrischika": "research, forensics, psychology, occult sciences",
        "Dhanu": "philosophy, law, education, foreign languages, travel",
        "Makara": "administration, civil services, engineering, finance",
        "Kumbha": "computer science, electronics, astrology, innovation",
        "Meena": "spirituality, medicine, arts, marine, music",
    }
    study_fields = STUDY_FIELDS.get(sign4, "diverse academic fields")

    vidya_yoga = _yoga_present(ctx, ["Saraswati", "Vidya", "Budhaditya"])
    foreign_edu = "Rahu" in h5_occ or pm.get("Rahu", {}).get("house") in (4, 5, 9)

    # Non-deterministic, safe pacing reflection for competitive preparation
    # Strictly avoids promising exam pass/fail or scores
    competitive_success = (
        "Supportive study alignment for competitive preparations"
        if pct > 65
        else "Focused preparation needed for competitive exams"
    )

    timing = _timing_windows(ctx, [4, 5, 9], "education")
    remedies = _build_remedies(ctx, ["Mercury"] if m_sc < 0 else [], "education")

    total_rules = len(rule_evidence.get("matched_rules", [])) + len(rule_evidence.get("rejected_rules", []))

    return {
        "domain": "Education & Skills",
        "icon": "✦",
        "score": pct,
        "study_fields": study_fields,
        "vidya_yoga": vidya_yoga,
        "foreign_education": foreign_edu,
        "competitive_success": competitive_success,
        "mercury_position": f"Mercury in {_ordinal(mercury.get('house', 1))}H — {mercury.get('strength', '')}",
        "dasha_active": dasha_active,
        "timing": timing,
        "remedies": remedies,
        "analysis": _education_narrative(ctx, pct, study_fields, vidya_yoga, foreign_edu, rule_evidence),
        # WP5E Canonical Rule Evaluation Evidence
        "evidence": rule_evidence,
        "dimensions": rule_evidence.get("dimensions", {}),
        "rules_evaluated": total_rules,
        "d24_status": rule_evidence.get("d24_status", "VERIFIED_ACTIVE"),
        "is_diagnostic": False,
        "safety_disclaimer": SAFETY_DISCLAIMER,
    }


def _education_narrative(ctx: dict, pct: int, study_fields: str, vidya_yoga: list, foreign_edu: bool, rule_evidence: dict) -> str:
    pm = ctx["planet_map"]
    mercury = pm.get("Mercury", {})
    jupiter = pm.get("Jupiter", {})
    parts = []

    parts.append(
        f"Within traditional Parashari principles, the 4th and 5th houses govern foundational learning and intellectual reasoning. "
        f"Mercury (analytical intellect) is in the {_ordinal(mercury.get('house', 1))} house — {mercury.get('strength', 'Neutral')}."
    )
    parts.append(f"Traditional symbolic curriculum affinities suggest: {study_fields}.")

    if vidya_yoga:
        parts.append(f"Vidya Yoga alignments noted: {', '.join(vidya_yoga)} — reflecting intellectual and scholastic interest.")

    if foreign_edu:
        parts.append("Alignment with foreign or cross-cultural educational opportunities indicated.")
    else:
        parts.append("Educational pursuits centered within domestic institutional frameworks.")

    dims = rule_evidence.get("dimensions", {})
    analytical_st = dims.get("analytical_communication", {}).get("status", "")
    if analytical_st:
        parts.append(f"Analytical & Communication profile: {analytical_st}.")

    return " ".join(parts)


_education = analyse_education
