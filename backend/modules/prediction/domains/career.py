"""
Career & Profession Domain Evaluator.
Integrates pure Parashari and Jaimini rule evaluation with legacy compatibility.
"""

from modules.prediction.scoring import (
    _score_planets_in_houses, _score_house_lord, _dasha_activates,
    _yoga_present, _pct, _ordinal
)
from modules.prediction.remedies import _timing_windows, _build_remedies
from shared.veda.career import evaluate_career_rules


def analyse_career(ctx: dict) -> dict:
    """
    Analyse career potential using deterministic Parashari rule pack
    while preserving backward compatibility with legacy API contracts.
    """
    pm  = ctx["planet_map"]
    hl  = ctx["house_lords"]

    sun    = pm.get("Sun", {})
    saturn = pm.get("Saturn", {})
    mars   = pm.get("Mars", {})
    jupiter= pm.get("Jupiter", {})
    mercury= pm.get("Mercury", {})

    lord_10 = hl[10]; lord_10_data = pm.get(lord_10, {})
    lord_6  = hl[6];  lord_6_data  = pm.get(lord_6, {})
    h10_occ = [p for p, d in pm.items() if d["house"] == 10]
    h6_occ  = [p for p, d in pm.items() if d["house"] == 6]

    base   = _score_planets_in_houses(ctx, [10, 6, 11])
    l10s   = _score_house_lord(ctx, 10)
    sun_sc = sun.get("str_score", 0) + (2 if sun.get("house") in (10, 1, 9) else 0)
    total  = base + l10s + sun_sc

    dasha_active = _dasha_activates(ctx, [10, 6, 11])
    pct = _pct(50, total, 12 if dasha_active else 0)

    # Evaluate canonical WP5A career rules
    rule_evidence = evaluate_career_rules(ctx)

    sun_strong  = sun.get("str_score", 0) >= 1 or sun.get("house") in (10, 1)
    saturn_str  = saturn.get("str_score", 0)
    if sun_strong and "Sun" in h10_occ:
        sector = "Government / Authority / IAS / Politics — strong Sun in 10th"
    elif saturn.get("house") in (10, 6, 11):
        sector = "Corporate / Technical / Service sector — Saturn influences career"
    elif mercury.get("house") in (10, 6):
        sector = "Business / Communication / Finance / IT — Mercury drives career"
    elif jupiter.get("house") in (10, 9):
        sector = "Teaching / Law / Finance / Spirituality — Jupiter in career houses"
    elif mars.get("house") in (10, 6):
        sector = "Military / Police / Engineering / Surgery — Mars drives ambition"
    else:
        sector = "Diverse options — multiple planets influence career path"

    sign10 = ctx["house_signs"][10]
    FIELD_MAP = {
        "Mesha": "engineering, military, sports, surgery",
        "Vrishabha": "finance, banking, agriculture, arts, luxury goods",
        "Mithuna": "journalism, IT, marketing, teaching, trading",
        "Karka": "nursing, real estate, catering, hospitality, social work",
        "Simha": "leadership, politics, entertainment, management, medicine",
        "Kanya": "accounting, medicine, analysis, research, editing",
        "Tula": "law, diplomacy, design, fashion, HR, mediation",
        "Vrischika": "research, intelligence, psychology, occult, mining",
        "Dhanu": "education, law, philosophy, export-import, travel",
        "Makara": "administration, engineering, construction, government",
        "Kumbha": "technology, science, social sector, aviation, astrology",
        "Meena": "spirituality, arts, medicine, marine, photography",
    }
    best_fields = FIELD_MAP.get(sign10, "diverse professional fields")

    raj_yogas = _yoga_present(ctx, ["Raj", "Raja", "Budhaditya", "Dharma Karma"])

    h11_lord = hl[11]; h11_data = pm.get(h11_lord, {})
    prom_active = h11_data.get("house") in (1, 10, 11) or "Jupiter" in [ctx["transit_map"].get("Jupiter", {}).get("house")]

    timing   = _timing_windows(ctx, [10, 6, 11], "career")
    weak_p   = [p for p, d in pm.items() if d["house"] == 10 and d["str_score"] < 0]
    if not weak_p and lord_10_data.get("str_score", 0) < 0:
        weak_p = [lord_10]
    remedies = _build_remedies(ctx, weak_p + ["Sun"], "career")

    return {
        "domain": "Career & Profession",
        "icon": "★",
        "score": pct,
        "sector": sector,
        "best_fields": best_fields,
        "tenth_lord": f"{lord_10} in {_ordinal(lord_10_data.get('house', 0))}H — {lord_10_data.get('strength', '')}",
        "h10_planets": h10_occ,
        "raj_yogas": raj_yogas,
        "business_vs_job": "Business favoured" if "Mercury" in h10_occ or mercury.get("house") == 10 else "Service/Job favoured" if saturn.get("house") == 10 else "Both viable — assess 7th for business",
        "foreign_work": "Strong foreign career indicators" if "Rahu" in h10_occ or ctx["transit_map"].get("Rahu", {}).get("house") == 10 else "Domestic career more prominent",
        "dasha_active": dasha_active,
        "timing": timing,
        "remedies": remedies,
        "analysis": _career_narrative(ctx, pct, sector, best_fields, raj_yogas, timing, rule_evidence),
        # WP5A Canonical Rule Evaluation Evidence
        "evidence": rule_evidence,
        "rules_evaluated": len(rule_evidence.get("matched_rules", [])) + len(rule_evidence.get("rejected_rules", [])),
    }


def _career_narrative(ctx, pct, sector, fields, yogas, timing, rule_evidence=None):
    md = ctx["mahadasha"]; ad = ctx["antardasha"]
    hl10 = ctx["house_lords"][10]
    h10d = ctx["planet_map"].get(hl10, {})
    parts = []
    parts.append(f"Your 10th house of career is ruled by {hl10}, placed in the {_ordinal(h10d.get('house', 1))} house — {h10d.get('strength', 'Neutral')}.")
    parts.append(f"Career direction points strongly toward {sector}. Best professional fields for your chart: {fields}.")
    if yogas:
        parts.append(f"Powerful career yogas are present: {', '.join(yogas)} — indicating recognition and rise to authority.")
    
    # Enrich narrative with primary archetypes if present
    if rule_evidence and rule_evidence.get("primary_archetypes"):
        top_arcs = [a["archetype"] for a in rule_evidence["primary_archetypes"][:2]]
        parts.append(f"Dominant vocational archetype alignments: {', '.join(top_arcs)}.")

    parts.append(f"Current {md}/{ad} dasha {'actively fires' if timing['dasha_active'] else 'does not directly trigger'} your career houses. Optimal window: {timing['best_window']}.")
    return " ".join(parts)


_career = analyse_career
