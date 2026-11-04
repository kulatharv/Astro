"""Event timing and Dasha-Gochara fusion timing engine."""

from datetime import datetime
from typing import Dict, Any

from shared.veda.zodiac import SIGNS as SIGNS_SK, SIGN_LORDS
from modules.kundali.dasha import generate_dasha_timeline, generate_dasha_chain
from modules.prediction.timing_config import get_domain_timing_config
from modules.prediction.transit_forecast import compute_transit_forecast
from modules.prediction.timing_dasha import score_dasha_periods
from modules.prediction.timing_transit import score_transit_months
from modules.prediction.timing_fusion import fuse_windows
from shared.veda.timing_rules import TIMING_SAFETY_DISCLAIMER
from shared.logging.logger import get_logger

logger = get_logger("modules.prediction.timing")


def evaluate_event_trigger(chart: dict, event_type: str) -> dict:
    """
    Legacy 3-label event trigger evaluator preserved for backwards compatibility.
    """
    if not isinstance(chart, dict):
        chart = {}
    dasha_info = chart.get("dasha", {})
    current_md = dasha_info.get("current_mahadasha", "Jupiter")
    lagna = chart.get("basic_details", {}).get("lagna", "Mesha")
    lagna_idx = SIGNS_SK.index(lagna) if lagna in SIGNS_SK else 0

    target_houses = {
        "marriage": [7, 5, 2, 11],
        "career": [10, 6, 11, 1],
        "wealth": [2, 11, 9, 1],
        "foreign": [12, 9, 3],
    }.get(event_type, [1, 5, 9])

    ruled_houses = []
    for h in range(1, 13):
        sign = SIGNS_SK[(lagna_idx + h - 1) % 12]
        if SIGN_LORDS.get(sign) == current_md:
            ruled_houses.append(h)

    md_placement = 1
    planets_by_house = chart.get("planets_by_house", {})
    for h_str, p_list in planets_by_house.items():
        for p in p_list:
            if p.get("planet") == current_md:
                try:
                    md_placement = int(h_str)
                except ValueError:
                    md_placement = 1

    is_activated = md_placement in target_houses or any(rh in target_houses for rh in ruled_houses)

    return {
        "event": event_type,
        "mahadasha_lord": current_md,
        "activated": is_activated,
        "active_houses": [md_placement] + ruled_houses,
        "intensity": "High" if is_activated else "Moderate",
    }


def compute_timing(chart: dict, domain: str, num_years: int = 15) -> Dict[str, Any]:
    """
    Orchestrate concrete date windows for a life domain using Dasha 60% + Gochara 40% fusion.
    Preserves legacy_timing field for backwards compatibility.
    """
    try:
        config = get_domain_timing_config(domain)

        # 1. Generate 15-year Dasha chain (MD/AD/PD)
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
            birth_dt = datetime.utcnow()

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

        now_dt = datetime.utcnow()
        end_dt = datetime(now_dt.year + num_years, now_dt.month, now_dt.day)

        dasha_chain = generate_dasha_chain(
            birth_datetime=birth_dt,
            timeline=timeline,
            filter_start=now_dt.strftime("%Y-%m-%d"),
            filter_end=end_dt.strftime("%Y-%m-%d"),
        )

        # 2. Score Dasha periods
        dasha_scores = score_dasha_periods(chart, domain, now_dt.date(), end_dt.date())

        # 3. Compute Transit forecast & scores
        transit_scores = score_transit_months(chart, domain, now_dt.date(), end_dt.date())

        # 4. Fuse windows
        fusion_res = fuse_windows(chart, domain, now_dt.date(), end_dt.date())
        res = {
            "timing_windows": [
                {
                    "start": w.start_date.strftime("%Y-%m-%d"),
                    "end": w.end_date.strftime("%Y-%m-%d"),
                    "peak_date": w.peak_date.strftime("%Y-%m-%d"),
                    "score": w.peak_score,
                    "confidence": w.confidence,
                    "mahadasha": w.mahadasha,
                    "antardasha": w.antardasha,
                    "pratyantardasha": w.pratyantardasha,
                    "drivers": w.drivers,
                    "reasons": w.reasons,
                    "sub_scores": w.sub_scores,
                    "evidence_families": w.evidence_families,
                    "ashtakavarga_bindus": w.ashtakavarga_bindus,
                    "double_transit_active": w.double_transit_active,
                    "vedha_obstructed": w.vedha_obstructed,
                    "transit_notes": ", ".join(w.drivers) if w.drivers else "Gochara alignment",
                }
                for w in fusion_res.timing_windows
            ],
            "peak_window": {
                "start": fusion_res.peak_window.start_date.strftime("%Y-%m-%d"),
                "end": fusion_res.peak_window.end_date.strftime("%Y-%m-%d"),
                "peak_date": fusion_res.peak_window.peak_date.strftime("%Y-%m-%d"),
                "score": fusion_res.peak_window.peak_score,
                "confidence": fusion_res.peak_window.confidence,
                "mahadasha": fusion_res.peak_window.mahadasha,
                "antardasha": fusion_res.peak_window.antardasha,
                "pratyantardasha": fusion_res.peak_window.pratyantardasha,
                "evidence_families": fusion_res.peak_window.evidence_families,
                "ashtakavarga_bindus": fusion_res.peak_window.ashtakavarga_bindus,
                "double_transit_active": fusion_res.peak_window.double_transit_active,
            } if fusion_res.peak_window else {"start": "N/A", "end": "N/A", "score": 0.0, "confidence": "Unlikely"},
            "next_12_months_summary": fusion_res.next_12_months_summary,
            "methodology": fusion_res.methodology,
            "threshold_used": fusion_res.threshold_used,
            "engine_version": fusion_res.engine_version,
            "timing_engine": fusion_res.engine_version,
            "legacy_timing": evaluate_event_trigger(chart, domain),
            "evidence_ledger": fusion_res.evidence_ledger,
            "birth_time_stability": fusion_res.birth_time_stability,
            "ashtakavarga_summary": fusion_res.ashtakavarga_summary,
            "safety_disclaimer": fusion_res.safety_disclaimer,
            "is_predictive": False,
        }
        return res
    except Exception as exc:
        logger.error(f"Timing computation error for {domain} (failing open): {exc}", exc_info=True)
        return {
            "timing_windows": [],
            "peak_window": None,
            "next_12_months_summary": f"Timing analysis unavailable for {domain}.",
            "methodology": "Master Spec v3.0 4-Family Evidence Fusion (Period 40%, Transit 30%, Ashtakavarga 15%, Promise 15%)",
            "timing_engine": "1.0.0",
            "legacy_timing": evaluate_event_trigger(chart, domain),
            "safety_disclaimer": TIMING_SAFETY_DISCLAIMER,
            "is_predictive": False,
        }


def build_timing_block(
    chart: dict,
    domain: str,
    horizon_years: int = 15,
    top_n: int = 5,
) -> Dict[str, Any]:
    """
    Helper function returning a dict matching the TimingBlock schema.
    Fails open gracefully on any exception.
    """
    try:
        return compute_timing(chart, domain, num_years=horizon_years)
    except Exception as exc:
        logger.error(f"build_timing_block fail-open for {domain}: {exc}", exc_info=True)
        return {
            "timing_windows": [],
            "peak_window": None,
            "next_12_months_summary": f"Timing analysis unavailable for {domain}.",
            "methodology": "Master Spec v3.0 4-Family Evidence Fusion (Period 40%, Transit 30%, Ashtakavarga 15%, Promise 15%)",
            "engine_version": "1.0.0",
            "legacy_timing": evaluate_event_trigger(chart, domain),
            "safety_disclaimer": TIMING_SAFETY_DISCLAIMER,
            "is_predictive": False,
        }
