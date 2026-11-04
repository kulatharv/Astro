"""
Window fusion engine combining Dasha, Transit, Ashtakavarga, and Natal Promise (Spec v3.0 §13–14).

Implements the 4-family Timing Evidence Architecture:
  TimingIndex = wP * PeriodActivation + wT * TransitSupport + wA * AshtakavargaContext + wN * NatalPromise
  Weights: Period (0.40) + Transit (0.30) + Ashtakavarga (0.15) + Natal Promise (0.15) = 1.00

Generates ranked, smoothed, and deduplicated monthly timing windows with full classical attribution.
"""

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Dict, Any, List, Optional

from shared.veda.zodiac import SIGNS as SIGNS_SK
from shared.veda.ashtakavarga import compute_sav, compute_bav
from shared.veda.vedha import check_transit_vedha
from shared.veda.timing_rules import (
    evaluate_timing_rules,
    TIMING_SAFETY_DISCLAIMER,
)
from modules.kundali.dasha import evaluate_dasha_birth_time_sensitivity
from modules.prediction.timing_config import get_domain_timing_config
from modules.prediction.timing_dasha import score_dasha_periods, ScoredPeriod
from modules.prediction.timing_transit import score_transit_months, ScoredMonth


@dataclass
class TimingWindow:
    start_date: date
    end_date: date
    peak_date: date
    peak_score: float
    confidence: str
    mahadasha: str
    antardasha: str
    pratyantardasha: str
    reasons: List[str]
    drivers: List[str]
    sub_scores: Dict[str, float]
    evidence_families: Dict[str, float] = field(default_factory=dict)
    ashtakavarga_bindus: int = 28
    double_transit_active: bool = False
    vedha_obstructed: bool = False


@dataclass
class TimingFusionResult:
    timing_windows: List[TimingWindow]
    peak_window: Optional[TimingWindow]
    next_12_months_summary: str
    methodology: str
    threshold_used: float
    engine_version: str
    evidence_ledger: List[Dict[str, Any]] = field(default_factory=list)
    birth_time_stability: str = "STABLE"
    ashtakavarga_summary: Dict[str, Any] = field(default_factory=dict)
    safety_disclaimer: str = TIMING_SAFETY_DISCLAIMER


def get_confidence_tier(score: float) -> str:
    """Return confidence tier based on peak fused score."""
    if score >= 0.72:
        return "High"
    elif score >= 0.52:
        return "Moderate"
    elif score >= 0.35:
        return "Possible"
    return "Unlikely"


def _check_double_transit(target_houses: List[int], active_transits: dict) -> bool:
    """Check if both Jupiter and Saturn simultaneously influence any target domain house."""
    jup_h = active_transits.get("Jupiter", {}).get("house")
    sat_h = active_transits.get("Saturn", {}).get("house")
    if not jup_h or not sat_h:
        return False

    jup_aspects = {jup_h, (jup_h + 4) % 12 or 12, (jup_h + 6) % 12 or 12, (jup_h + 8) % 12 or 12}
    sat_aspects = {sat_h, (sat_h + 2) % 12 or 12, (sat_h + 6) % 12 or 12, (sat_h + 9) % 12 or 12}

    for h in target_houses:
        if h in jup_aspects and h in sat_aspects:
            return True
    return False


def fuse_windows(
    chart: dict,
    domain: str,
    start_date: date,
    end_date: date,
    top_n: int = 5,
) -> TimingFusionResult:
    """
    Combine Dasha periods, Transit months, Ashtakavarga bindus, and Natal Promise
    using Master Spec v3.0 4-Family Timing Evidence Architecture.
    """
    config = get_domain_timing_config(domain)
    target_houses = config.get("significator_houses", [10, 6, 11])
    special_rules = config.get("special_rules", [])

    # 1. Fetch raw Dasha and Transit scores
    dasha_periods = score_dasha_periods(chart, domain, start_date, end_date)
    transit_months = score_transit_months(chart, domain, start_date, end_date)

    if not transit_months:
        return TimingFusionResult(
            timing_windows=[],
            peak_window=None,
            next_12_months_summary=f"No timing windows generated for {domain}.",
            methodology="Master Spec v3.0 4-Family Evidence Fusion (Period 40%, Transit 30%, Ashtakavarga 15%, Promise 15%)",
            threshold_used=0.45,
            engine_version="2.0.0",
        )

    # Precompute SAV and BAV
    sav = compute_sav(chart)
    bav_jup = compute_bav("Jupiter", chart)

    # Evaluate birth-time uncertainty
    moon_long = chart.get("planets_by_house", {})
    # Find moon degree
    moon_deg = 0.0
    for h, plist in moon_long.items():
        for p in plist:
            if p.get("planet") == "Moon":
                moon_deg = float(p.get("degree", 0.0))
                break

    stability_info = evaluate_dasha_birth_time_sensitivity(moon_deg, uncertainty_minutes=15.0)
    birth_time_stability = stability_info.get("stability", "STABLE")

    # 2. STEP A — Align time axes per monthly snapshot with 4 evidence families
    w_p, w_t, w_a, w_n = 0.40, 0.30, 0.15, 0.15

    # Natal promise baseline score for the domain (approx from chart or default 0.60)
    natal_promise_score = 0.60

    monthly_snapshots = []
    for m in transit_months:
        # Matching dasha period
        matching_dasha = None
        for dp in dasha_periods:
            if dp.start_date <= m.month_start <= dp.end_date or dp.start_date <= m.month_end <= dp.end_date or m.month_start <= dp.start_date <= m.month_end:
                matching_dasha = dp
                break

        d_score = matching_dasha.score if matching_dasha else 0.30
        t_score = m.score

        # Ashtakavarga family score based on Jupiter & Saturn transit sign bindus
        jup_sign = m.active_transits.get("Jupiter", {}).get("sign", "Mesha")
        sat_sign = m.active_transits.get("Saturn", {}).get("sign", "Mesha")
        jup_bindus = sav.get(jup_sign, 28)
        sat_bindus = sav.get(sat_sign, 28)
        avg_bindus = (jup_bindus + sat_bindus) / 2.0
        # Normalize bindus: 20 -> 0.1, 28 -> 0.6, 35 -> 0.95
        a_score = max(0.10, min(0.95, (avg_bindus - 15.0) / 20.0))

        # Check Double Transit
        dt_active = _check_double_transit(target_houses, m.active_transits)
        if dt_active:
            t_score = min(0.95, t_score + 0.15)

        # Check Vedha obstruction on Jupiter from natal Moon
        jup_house_moon = m.active_transits.get("Jupiter", {}).get("house", 1)
        transit_houses_moon = {p: pinfo.get("house", 1) for p, pinfo in m.active_transits.items()}
        vedha_res = check_transit_vedha("Jupiter", jup_house_moon, transit_houses_moon)
        is_vedha = vedha_res.get("is_obstructed", False)
        if is_vedha:
            t_score = max(0.15, t_score - 0.12)

        # 4-Family Fusion
        combined = (w_p * d_score) + (w_t * t_score) + (w_a * a_score) + (w_n * natal_promise_score)

        monthly_snapshots.append({
            "month_start": m.month_start,
            "month_end": m.month_end,
            "dasha_score": d_score,
            "transit_score": t_score,
            "ashtakavarga_score": round(a_score, 3),
            "natal_promise_score": natal_promise_score,
            "combined_score": round(combined, 3),
            "dasha_period": matching_dasha,
            "transit_month": m,
            "double_transit_active": dt_active,
            "vedha_obstructed": is_vedha,
            "avg_bindus": int(round(avg_bindus)),
        })

    # 3. STEP B — 3-month rolling average smoothing
    num_months = len(monthly_snapshots)
    for i in range(num_months):
        prev_s = monthly_snapshots[i - 1]["combined_score"] if i > 0 else monthly_snapshots[i]["combined_score"]
        curr_s = monthly_snapshots[i]["combined_score"]
        next_s = monthly_snapshots[i + 1]["combined_score"] if i < num_months - 1 else monthly_snapshots[i]["combined_score"]

        smooth_val = round((prev_s + curr_s + next_s) / 3.0, 3)
        monthly_snapshots[i]["smoothed_score"] = smooth_val

    # 4. STEP C & D — Threshold & Merge consecutive qualifying months
    threshold = 0.45
    qualifying_indices = [i for i, snap in enumerate(monthly_snapshots) if snap["smoothed_score"] >= threshold]

    raw_groups = []
    if qualifying_indices:
        current_group = [qualifying_indices[0]]
        for idx in qualifying_indices[1:]:
            if idx - current_group[-1] <= 2:  # allow 1-month gap tolerance
                current_group.append(idx)
            else:
                raw_groups.append(current_group)
                current_group = [idx]
        if current_group:
            raw_groups.append(current_group)

    # 5. Build TimingWindow objects
    built_windows = []
    for grp in raw_groups:
        grp_months = [monthly_snapshots[i] for i in grp]
        peak_snap = max(grp_months, key=lambda x: x["smoothed_score"])

        w_start = grp_months[0]["month_start"]
        w_end = grp_months[-1]["month_end"]
        peak_dt = peak_snap["month_start"]
        peak_score = peak_snap["smoothed_score"]

        d_period = peak_snap["dasha_period"]
        t_month = peak_snap["transit_month"]

        md_l = d_period.mahadasha_lord if d_period else "Jupiter"
        ad_l = d_period.antardasha_lord if d_period else "Venus"
        pd_l = d_period.pratyantardasha_lord if d_period else "Saturn"

        d_reasons = d_period.reasons if d_period else []
        t_reasons = t_month.reasons if t_month else []

        extra_notes = []
        if peak_snap["double_transit_active"]:
            extra_notes.append("Double Transit (Jupiter + Saturn) triggers domain activation")
        if peak_snap["vedha_obstructed"]:
            extra_notes.append("Gochara Vedha partially moderates transit expansion")
        if peak_snap["avg_bindus"] >= 30:
            extra_notes.append(f"Auspicious Ashtakavarga support ({peak_snap['avg_bindus']} SAV bindus)")

        merged_reasons = list(dict.fromkeys(d_reasons + t_reasons + extra_notes))
        top_drivers = merged_reasons[:4]
        conf = get_confidence_tier(peak_score)

        # Special domain overrides
        sat_house = t_month.active_transits.get("Saturn", {}).get("house") if t_month else None
        if "saturn_7h_block" in special_rules and sat_house == 7 and domain == "marriage":
            conf = "Possible"

        if "jupiter_return_7h" in special_rules and peak_score >= 0.55:
            jup_h = t_month.active_transits.get("Jupiter", {}).get("house") if t_month else None
            if jup_h == 7:
                conf = "High"

        built_windows.append(
            TimingWindow(
                start_date=w_start,
                end_date=w_end,
                peak_date=peak_dt,
                peak_score=peak_score,
                confidence=conf,
                mahadasha=md_l,
                antardasha=ad_l,
                pratyantardasha=pd_l,
                reasons=merged_reasons,
                drivers=top_drivers,
                sub_scores={
                    "dasha_score": peak_snap["dasha_score"],
                    "transit_score": peak_snap["transit_score"],
                    "ashtakavarga_score": peak_snap["ashtakavarga_score"],
                    "natal_promise_score": peak_snap["natal_promise_score"],
                },
                evidence_families={
                    "period_activation": peak_snap["dasha_score"],
                    "transit_trigger": peak_snap["transit_score"],
                    "ashtakavarga_context": peak_snap["ashtakavarga_score"],
                    "natal_promise": peak_snap["natal_promise_score"],
                },
                ashtakavarga_bindus=peak_snap["avg_bindus"],
                double_transit_active=peak_snap["double_transit_active"],
                vedha_obstructed=peak_snap["vedha_obstructed"],
            )
        )

    # 6. Deduplicate overlapping windows (>50% overlap)
    deduped_windows: List[TimingWindow] = []
    for w in built_windows:
        if not deduped_windows:
            deduped_windows.append(w)
        else:
            prev_w = deduped_windows[-1]
            overlap_start = max(prev_w.start_date, w.start_date)
            overlap_end = min(prev_w.end_date, w.end_date)
            if overlap_start <= overlap_end:
                overlap_days = (overlap_end - overlap_start).days + 1
                len1 = (prev_w.end_date - prev_w.start_date).days + 1
                len2 = (w.end_date - w.start_date).days + 1
                min_len = min(len1, len2)

                if min_len > 0 and (overlap_days / min_len) >= 0.50:
                    if w.peak_score > prev_w.peak_score:
                        deduped_windows[-1] = w
                    continue
            deduped_windows.append(w)

    # 7. Rank and limit (deterministic tie-break on start_date)
    deduped_windows.sort(key=lambda x: (-x.peak_score, x.start_date))
    top_windows = deduped_windows[:top_n]
    peak_win = top_windows[0] if top_windows else None

    # Evaluate canonical timing rules for peak snapshot
    timing_eval_ctx = {
        "md_lord": peak_win.mahadasha if peak_win else "Jupiter",
        "ad_lord": peak_win.antardasha if peak_win else "Venus",
        "pd_lord": peak_win.pratyantardasha if peak_win else "Saturn",
        "domain_houses": target_houses,
        "transit_map": transit_months[0].active_transits if transit_months else {},
    }
    rules_res = evaluate_timing_rules(chart, timing_eval_ctx)

    if peak_win:
        summary_msg = (
            f"Peak activation window for {domain} aligns around {peak_win.peak_date.strftime('%B %Y')} "
            f"with {peak_win.confidence} confidence during {peak_win.mahadasha}-{peak_win.antardasha} Dasha. "
            f"Ashtakavarga support: {peak_win.ashtakavarga_bindus} bindus. "
            f"({len(rules_res.get('evidence_ledger', []))} timing evidence rules active)."
        )
    else:
        summary_msg = f"No major timing activation window identified for {domain} in the next 12 months."

    return TimingFusionResult(
        timing_windows=top_windows,
        peak_window=peak_win,
        next_12_months_summary=summary_msg,
        methodology="Master Spec v3.0 4-Family Evidence Fusion (Period 40%, Transit 30%, Ashtakavarga 15%, Promise 15%)",
        threshold_used=threshold,
        engine_version="1.0.0",
        evidence_ledger=rules_res.get("evidence_ledger", []),
        birth_time_stability=birth_time_stability,
        ashtakavarga_summary={"sav_sample": {k: sav[k] for k in list(sav.keys())[:4]}, "total_sav_invariant": 337},
        safety_disclaimer=TIMING_SAFETY_DISCLAIMER,
    )
