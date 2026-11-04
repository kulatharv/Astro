"""
Marriage & Relationships Domain Evaluator.
Integrates pure Parashari rule evaluation with legacy compatibility.
"""

from modules.prediction.scoring import (
    _score_planets_in_houses, _score_house_lord, _dasha_activates,
    _transit_influence, _pct, _ordinal, RASHI, RASHI_EN
)
from modules.prediction.remedies import _timing_windows, _build_remedies
from shared.veda.marriage import evaluate_marriage_rules


def analyse_marriage(ctx: dict) -> dict:
    """
    Analyse marriage and partnership potential using deterministic Parashari rule pack
    while preserving backward compatibility with legacy API contracts.
    """
    pm = ctx["planet_map"]
    hl = ctx["house_lords"]

    venus = pm.get("Venus", {})
    jupiter = pm.get("Jupiter", {})
    mars = pm.get("Mars", {})
    moon = pm.get("Moon", {})

    lord_7 = hl[7]
    lord_7_data = pm.get(lord_7, {})
    lord_7_house = lord_7_data.get("house", 0)
    lord_7_sign  = lord_7_data.get("sign", "")
    lord_7_str   = lord_7_data.get("strength", "Neutral")

    h7_occupants = [p for p, d in pm.items() if d["house"] == 7]
    h5_occupants = [p for p, d in pm.items() if d["house"] == 5]
    h2_occupants = [p for p, d in pm.items() if d["house"] == 2]

    base  = _score_planets_in_houses(ctx, [7, 5, 2])
    l7s   = _score_house_lord(ctx, 7)
    venus_score = venus.get("str_score", 0) + (2 if venus.get("house") in (7, 5, 2, 1) else 0)
    total_score = base + l7s + venus_score

    dasha_active = _dasha_activates(ctx, [7, 5, 2])
    transit_sc   = _transit_influence(ctx, [7, 5, 2], ["Jupiter", "Venus"])
    pct = _pct(50, total_score, 10 if dasha_active else 0)

    # Evaluate canonical WP5B marriage rules
    rule_evidence = evaluate_marriage_rules(ctx)

    mangal_dosh = mars.get("house") in (1, 4, 7, 8, 12)
    mangal_txt = (
        f"Mars in {_ordinal(mars.get('house', 0))} house — traditional Mangal considerations present. "
        "Evaluated with multi-frame and classical cancellation factors."
        if mangal_dosh else "No Mangal Dosh detected."
    )

    yogas_data = ctx.get("yogas", [])
    kalatra = "Kalatra Yoga" in str(yogas_data)

    if h5_occupants and "Venus" in h5_occupants:
        marriage_type = "Strong indicators of love marriage — Venus in 5th house of romance."
    elif "Jupiter" in h7_occupants:
        marriage_type = "Arranged marriage favoured — Jupiter blesses the 7th house with wisdom and tradition."
    elif "Rahu" in h7_occupants:
        marriage_type = "Unconventional or inter-cultural marriage possible — Rahu influences 7th."
    elif venus.get("house") == 7:
        marriage_type = "Love or love-cum-arranged marriage — Venus directly occupies partnership house."
    else:
        marriage_type = "Arranged marriage most likely — assess 5th house for romance indicators."

    sign7 = ctx["house_signs"][7]
    PARTNER_TRAITS = {
        "Mesha": "dynamic, ambitious, independent, sometimes impatient",
        "Vrishabha": "loyal, sensual, patient, materialistic, loves comfort",
        "Mithuna": "witty, communicative, versatile, may be dual-natured",
        "Karka": "caring, emotional, home-loving, intuitive, protective",
        "Simha": "confident, generous, dramatic, needs admiration",
        "Kanya": "analytical, health-conscious, critical, service-oriented",
        "Tula": "charming, diplomatic, aesthetic, partnership-oriented",
        "Vrischika": "intense, secretive, transformative, passionate",
        "Dhanu": "philosophical, adventurous, honest, sometimes blunt",
        "Makara": "disciplined, ambitious, traditional, reliable",
        "Kumbha": "independent, humanitarian, unconventional, intellectual",
        "Meena": "spiritual, compassionate, artistic, sometimes escapist",
    }
    partner_traits = PARTNER_TRAITS.get(sign7, "dignified and balanced")
    if h7_occupants:
        planet_modifiers = {
            "Venus": "charming and romantic", "Jupiter": "wise and spiritual",
            "Saturn": "mature and serious", "Mars": "energetic and assertive",
            "Mercury": "intelligent and communicative", "Moon": "emotional and nurturing",
            "Sun": "authoritative and proud", "Rahu": "exotic or foreign connection",
            "Ketu": "spiritual or detached"
        }
        mods = [planet_modifiers[p] for p in h7_occupants if p in planet_modifiers]
        if mods:
            partner_traits += f" — {', '.join(mods)}"

    h8_lord = hl[8]
    h8_data = pm.get(h8_lord, {})
    second_marriage = (
        "Indicators present for second marriage or significant relationship transformation"
        if (h8_data.get("house") in (7, 2) or "Rahu" in h7_occupants)
        else "No strong indicators for second marriage."
    )

    h8_occ = [p for p, d in pm.items() if d["house"] == 8]
    intimacy = (
        "Strong physical chemistry" if "Mars" in h8_occ or "Venus" in h8_occ
        else "Emotional and spiritual connection dominates"
    )

    timing = _timing_windows(ctx, [7, 5, 2], "marriage")
    remedies = _build_remedies(
        ctx,
        [p for p, d in pm.items() if d["house"] in (7,) and d["str_score"] < 0] +
        (["Venus"] if venus.get("str_score", 0) < 0 else []),
        "marriage"
    )

    return {
        "domain": "Marriage & Relationships",
        "icon": "♥",
        "score": pct,
        "marriage_type": marriage_type,
        "partner_traits": partner_traits,
        "partner_sign": f"{sign7} ({RASHI_EN[RASHI.index(sign7)] if sign7 in RASHI else sign7})",
        "mangal_dosh": mangal_dosh,
        "mangal_dosh_txt": mangal_txt,
        "kalatra_yoga": kalatra,
        "second_marriage": second_marriage,
        "intimacy": intimacy,
        "venus_position": f"Venus in {venus.get('house', 0)}H {venus.get('sign', '')} — {venus.get('strength', '')}",
        "seventh_lord": f"{lord_7} in {_ordinal(lord_7_house)} house — {lord_7_str}",
        "h7_planets": h7_occupants,
        "dasha_active": dasha_active,
        "timing": timing,
        "remedies": remedies,
        "analysis": _marriage_narrative(ctx, pct, marriage_type, partner_traits, timing, rule_evidence),
        # WP5B Canonical Rule Evaluation Evidence
        "evidence": rule_evidence,
        "rules_evaluated": len(rule_evidence.get("matched_rules", [])) + len(rule_evidence.get("rejected_rules", [])),
    }


def _marriage_narrative(ctx, pct, mtype, traits, timing, rule_evidence=None):
    md = ctx["mahadasha"]; ad = ctx["antardasha"]
    venus = ctx["planet_map"].get("Venus", {})
    h7 = [p for p, d in ctx["planet_map"].items() if d["house"] == 7]
    parts = []
    parts.append(f"Your 7th house of marriage is ruled by {ctx['house_lords'][7]}, and {mtype.lower()}")
    if h7:
        parts.append(f"With {', '.join(h7)} occupying the 7th house, your partnerships carry their energies — {', '.join([str(p) for p in h7])} shapes the nature of your unions.")
    parts.append(f"Venus, the primary karaka for marriage, is placed in the {_ordinal(venus.get('house', 1))} house in {venus.get('sign', '')} — {venus.get('strength', '')}, indicating {'strong' if venus.get('str_score', 0) >= 0 else 'a challenged'} capacity for love and harmony.")
    parts.append(f"Your partner is likely to be {traits}.")

    # Enrich narrative with primary archetypes if present
    if rule_evidence and rule_evidence.get("primary_archetypes"):
        top_arcs = [a["archetype"] for a in rule_evidence["primary_archetypes"][:2]]
        parts.append(f"Key relationship dynamic themes: {', '.join(top_arcs)}.")

    parts.append(f"Current {md}/{ad} dasha {'actively triggers' if timing['dasha_active'] else 'does not directly activate'} the marriage houses. Best timing window: {timing['best_window']}.")
    return " ".join(parts)


_marriage = analyse_marriage
