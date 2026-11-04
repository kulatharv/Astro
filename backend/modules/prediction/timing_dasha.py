"""Dasha activation scoring engine for domain timing (Step 5.4)."""

from dataclasses import dataclass
from datetime import date, datetime
from typing import Dict, Any, List, Optional

from shared.veda.zodiac import SIGNS, SIGN_LORDS
from modules.kundali.dasha import generate_dasha_timeline, generate_dasha_chain
from modules.prediction.timing_config import get_domain_timing_config
from modules.prediction.scoring import _build_ctx


@dataclass
class ScoredPeriod:
    start_date: date
    end_date: date
    mahadasha_lord: str
    antardasha_lord: str
    pratyantardasha_lord: str
    score: float           # 0.0 to 1.0
    reasons: List[str]
    sub_scores: Dict[str, float]  # {"md": float, "ad": float, "pd": float}


def is_functional_benefic(lord: str, lagna: str) -> bool:
    """Determine classical functional benefic status based on Lagna (Parashari)."""
    BENEFICS_BY_LAGNA = {
        "Mesha": ["Mars", "Jupiter", "Sun"],
        "Vrishabha": ["Venus", "Saturn", "Mercury"],
        "Mithuna": ["Mercury", "Venus", "Saturn"],
        "Karka": ["Moon", "Mars", "Jupiter"],
        "Simha": ["Sun", "Mars", "Jupiter"],
        "Kanya": ["Mercury", "Venus"],
        "Tula": ["Venus", "Saturn", "Mercury"],
        "Vrischika": ["Mars", "Jupiter", "Moon"],
        "Dhanu": ["Jupiter", "Sun", "Mars"],
        "Makara": ["Saturn", "Venus", "Mercury"],
        "Kumbha": ["Saturn", "Venus"],
        "Meena": ["Jupiter", "Mars", "Moon"],
    }
    return lord in BENEFICS_BY_LAGNA.get(lagna, ["Jupiter", "Venus"])


def is_functional_malefic(lord: str, lagna: str) -> bool:
    """Determine classical functional malefic status based on Lagna."""
    MALEFICS_BY_LAGNA = {
        "Mesha": ["Mercury", "Saturn"],
        "Vrishabha": ["Jupiter", "Mars"],
        "Mithuna": ["Mars", "Jupiter"],
        "Karka": ["Saturn", "Mercury"],
        "Simha": ["Saturn", "Venus"],
        "Kanya": ["Mars", "Jupiter"],
        "Tula": ["Sun", "Jupiter"],
        "Vrischika": ["Mercury", "Venus"],
        "Dhanu": ["Venus", "Mercury"],
        "Makara": ["Mars", "Jupiter"],
        "Kumbha": ["Moon", "Mars"],
        "Meena": ["Sun", "Venus", "Saturn"],
    }
    return lord in MALEFICS_BY_LAGNA.get(lagna, ["Rahu", "Ketu"])


def evaluate_lord_subscore(lord: str, role_name: str, config: Dict[str, Any], ctx: dict) -> tuple[float, List[str]]:
    """
    Evaluate sub-score (0.0 to 1.0) and reasons for a single Dasha lord (MD, AD, or PD).
    """
    raw_points = 0
    reasons = []

    lagna = ctx["lagna"]
    lagna_idx = ctx["lagna_idx"]
    target_houses = config.get("significator_houses", [1, 5, 9])
    primary_k = config.get("primary_karaka")
    secondary_ks = config.get("secondary_karaka", [])
    if isinstance(secondary_ks, str):
        secondary_ks = [secondary_ks]

    # 1. Karaka evaluation
    if lord == primary_k:
        raw_points += 2
        reasons.append(f"{lord} {role_name} is primary karaka for {config['domain']}")
    elif lord in secondary_ks:
        raw_points += 1
        reasons.append(f"{lord} {role_name} is secondary karaka for {config['domain']}")

    # 2. House lordship
    ruled_houses = []
    for h in range(1, 13):
        sign = SIGNS[(lagna_idx + h - 1) % 12]
        if SIGN_LORDS.get(sign) == lord:
            ruled_houses.append(h)

    matched_ruled = [h for h in ruled_houses if h in target_houses]
    if matched_ruled:
        raw_points += 2
        reasons.append(f"{lord} {role_name} is lord of {config['domain']} house(s) {matched_ruled}")

    # 3. Placement
    planet_data = ctx["planet_map"].get(lord, {})
    placement_house = planet_data.get("house", 1)
    if placement_house in target_houses:
        raw_points += 1
        reasons.append(f"{lord} {role_name} is placed in {config['domain']} house {placement_house}")

    # 4. Aspects (simplified 7th aspect / special Parashari aspects)
    aspect_houses = [(placement_house + 6) % 12 or 12]
    if lord == "Jupiter":
        aspect_houses.extend([(placement_house + 4) % 12 or 12, (placement_house + 8) % 12 or 12])
    elif lord == "Saturn":
        aspect_houses.extend([(placement_house + 2) % 12 or 12, (placement_house + 9) % 12 or 12])

    if any(h in target_houses for h in aspect_houses):
        raw_points += 1
        reasons.append(f"{lord} {role_name} aspects {config['domain']} house(s)")

    # 5. Functional Benefic / Malefic
    if is_functional_benefic(lord, lagna):
        raw_points += 1
        reasons.append(f"{lord} {role_name} is functional benefic for {lagna} Lagna")
    elif is_functional_malefic(lord, lagna):
        raw_points -= 2
        reasons.append(f"{lord} {role_name} is functional malefic for {lagna} Lagna")

    # 6. Dignity & Net Strength
    strength_label = planet_data.get("strength", "Neutral")
    if strength_label == "Exalted":
        raw_points += 1
        reasons.append(f"{lord} {role_name} is exalted")
    elif strength_label == "Debilitated":
        raw_points -= 2
        reasons.append(f"{lord} {role_name} is debilitated (penalty)")

    if placement_house in (6, 8, 12) and config["domain"] != "challenges":
        raw_points -= 1
        reasons.append(f"{lord} {role_name} is in dusthana house {placement_house}")

    # Clamp raw_points to [0, 7] and convert to [0.0, 1.0]
    clamped_points = max(0, min(7, raw_points))
    subscore = round(clamped_points / 7.0, 2)

    return subscore, reasons


def score_dasha_periods(
    chart: dict,
    domain: str,
    start_date: date,
    end_date: date,
) -> List[ScoredPeriod]:
    """
    Score Vimshottari Dasha periods (MD/AD/PD) for a domain over a given date range.
    """
    config = get_domain_timing_config(domain)
    ctx = _build_ctx(chart)

    # Convert date to string format for dasha chain filter
    f_start = start_date.strftime("%Y-%m-%d")
    f_end = end_date.strftime("%Y-%m-%d")

    birth_dt = chart.get("birth_datetime")
    if not isinstance(birth_dt, datetime):
        d_info = chart.get("dasha", {})
        birth_dt = d_info.get("birth_datetime")
    if not isinstance(birth_dt, datetime) and "birth_year" in chart:
        birth_dt = datetime(
            int(chart["birth_year"]),
            int(chart.get("birth_month", 1)),
            int(chart.get("birth_day", 1)),
            int(chart.get("birth_hour", 12)),
            int(chart.get("birth_minute", 0)),
        )
    if not isinstance(birth_dt, datetime):
        raw_b = chart.get("basic_details", {})
        date_str = raw_b.get("date") or chart.get("birth_date") or chart.get("date")
        time_val = raw_b.get("time") or chart.get("time", 12.0)
        if date_str:
            for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%Y/%m/%d"):
                try:
                    parsed_d = datetime.strptime(str(date_str).strip(), fmt)
                    if isinstance(time_val, (int, float)):
                        hour = int(time_val)
                        minute = int(round((time_val - hour) * 60))
                        birth_dt = parsed_d.replace(hour=hour, minute=minute)
                    else:
                        birth_dt = parsed_d
                    break
                except ValueError:
                    pass
    if not isinstance(birth_dt, datetime):
        birth_dt = datetime(start_date.year, start_date.month, start_date.day)

    timeline = chart.get("dasha", {}).get("timeline")
    if not timeline:
        dasha_info = chart.get("dasha", {})
        md_lord = dasha_info.get("current_mahadasha") or chart.get("mahadasha", "Jupiter")
        bal = dasha_info.get("balance_years")
        if bal is None:
            raw_bal = chart.get("dasha_balance", "10.0")
            try:
                bal = float(str(raw_bal).split()[0])
            except Exception:
                bal = 10.0
        timeline = generate_dasha_timeline(md_lord, float(bal))

    dasha_chain = generate_dasha_chain(
        birth_datetime=birth_dt,
        timeline=timeline,
        filter_start=f_start,
        filter_end=f_end,
    )

    scored_periods = []
    # Cap total returned periods at 200 to prevent performance bottlenecks
    for p in dasha_chain[:200]:
        p_s = datetime.strptime(p["start"], "%Y-%m-%d").date()
        p_e = datetime.strptime(p["end"], "%Y-%m-%d").date()

        # Clip dates to range boundary
        effective_start = max(p_s, start_date)
        effective_end = min(p_e, end_date)

        if effective_start >= effective_end:
            continue

        md_l = p["md_lord"]
        ad_l = p["ad_lord"]
        pd_l = p.get("pd_lord", ad_l)

        md_sub, md_reasons = evaluate_lord_subscore(md_l, "MD", config, ctx)
        ad_sub, ad_reasons = evaluate_lord_subscore(ad_l, "AD", config, ctx)
        pd_sub, pd_reasons = evaluate_lord_subscore(pd_l, "PD", config, ctx) if "pd_lord" in p else (ad_sub, ["PD not available, fallback to AD"])

        combined_score = (0.30 * md_sub) + (0.45 * ad_sub) + (0.25 * pd_sub)

        # Apply domain-specific special rules overrides
        special_rules = config.get("special_rules", [])
        if "saturn_7h_block" in special_rules and (md_l == "Saturn" or ad_l == "Saturn"):
            combined_score *= 0.70
            md_reasons.append("Saturn MD/AD applies 7H block multiplier (0.7)")

        if "venus_md_activates" in special_rules and md_l == "Venus":
            combined_score *= 1.20
            md_reasons.append("Venus MD universally activates marriage (1.2 multiplier)")

        final_score = round(max(0.0, min(1.0, combined_score)), 2)
        all_reasons = list(dict.fromkeys(md_reasons + ad_reasons + pd_reasons))

        scored_periods.append(
            ScoredPeriod(
                start_date=effective_start,
                end_date=effective_end,
                mahadasha_lord=md_l,
                antardasha_lord=ad_l,
                pratyantardasha_lord=pd_l,
                score=final_score,
                reasons=all_reasons,
                sub_scores={"md": md_sub, "ad": ad_sub, "pd": pd_sub},
            )
        )

    return scored_periods
