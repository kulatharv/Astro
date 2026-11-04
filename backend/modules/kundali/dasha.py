"""Vimshottari Dasha calculation engine."""

from datetime import datetime, timedelta
from shared.veda.nakshatra import NAKSHATRAS, NAKSHATRA_SIZE

DASHA_SEQUENCE = [
    "Ketu", "Venus", "Sun", "Moon",
    "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"
]

DASHA_YEARS = {
    "Ketu": 7,
    "Venus": 20,
    "Sun": 6,
    "Moon": 10,
    "Mars": 7,
    "Rahu": 18,
    "Jupiter": 16,
    "Saturn": 19,
    "Mercury": 17
}


def calculate_mahadasha(moon_longitude: float, nak_name: str) -> tuple[str, float]:
    """
    Calculate the starting Mahadasha lord and remaining balance years at birth.
    Returns: (lord_name, balance_years).
    """
    if nak_name in NAKSHATRAS:
        nak_index = NAKSHATRAS.index(nak_name)
    else:
        nak_index = int((moon_longitude % 360.0) / NAKSHATRA_SIZE) % 27

    lord = DASHA_SEQUENCE[nak_index % 9]
    full_years = DASHA_YEARS[lord]

    remainder = (moon_longitude % 360.0) % NAKSHATRA_SIZE
    balance_fraction = (NAKSHATRA_SIZE - remainder) / NAKSHATRA_SIZE
    balance_years = balance_fraction * full_years

    return lord, round(balance_years, 2)


def generate_dasha_timeline(start_lord: str, balance_years: float) -> list[dict]:
    """Generate the full 120-year Vimshottari Mahadasha progression timeline."""
    timeline = []
    current_index = DASHA_SEQUENCE.index(start_lord) if start_lord in DASHA_SEQUENCE else 0

    timeline.append({
        "lord": start_lord,
        "years": round(balance_years, 2)
    })

    total_years = balance_years
    next_index = (current_index + 1) % 9

    while total_years < 120:
        lord = DASHA_SEQUENCE[next_index]
        years = DASHA_YEARS[lord]

        timeline.append({
            "lord": lord,
            "years": years
        })

        total_years += years
        next_index = (next_index + 1) % 9

    return timeline


def generate_antardasha(mahadasha_lord: str) -> list[dict]:
    """Calculate the 9 Antardasha periods for a given Mahadasha lord."""
    antardashas = []
    start_idx = DASHA_SEQUENCE.index(mahadasha_lord) if mahadasha_lord in DASHA_SEQUENCE else 0
    md_years = DASHA_YEARS.get(mahadasha_lord, 10)

    for i in range(9):
        lord = DASHA_SEQUENCE[(start_idx + i) % 9]
        ad_years = (md_years * DASHA_YEARS[lord]) / 120.0
        antardashas.append({
            "lord": lord,
            "years": round(ad_years, 2)
        })

    return antardashas


DASHA_DEPTH = "PD"


def compute_pratyantardasha(md_lord: str, ad_lord: str, ad_start: datetime, ad_end: datetime) -> list[dict]:
    """Calculate the 9 Pratyantardasha (PD) sub-periods within an Antardasha."""
    pds = []
    ad_duration_days = (ad_end - ad_start).total_seconds() / 86400.0
    start_idx = DASHA_SEQUENCE.index(ad_lord) if ad_lord in DASHA_SEQUENCE else 0

    curr_start = ad_start
    for i in range(9):
        pd_lord = DASHA_SEQUENCE[(start_idx + i) % 9]
        pd_duration_days = ad_duration_days * (DASHA_YEARS[pd_lord] / 120.0)
        curr_end = curr_start + timedelta(days=pd_duration_days)

        pds.append({
            "md_lord": md_lord,
            "ad_lord": ad_lord,
            "pd_lord": pd_lord,
            "start": curr_start.strftime("%Y-%m-%d"),
            "end": curr_end.strftime("%Y-%m-%d"),
            "days": round(pd_duration_days, 1),
        })
        curr_start = curr_end

    return pds


def generate_dasha_chain(
    birth_datetime: datetime,
    timeline: list[dict],
    filter_start: str | None = None,
    filter_end: str | None = None,
    year_convention: str = "solar_365_25",
) -> list[dict]:
    """
    Generate nested MD/AD/PD periods for chart forecast within optional filter date range.
    Supports 'solar_365_25' (default, 365.25 days) and 'savana_360' (360 days) conventions.
    """
    days_per_year = 360.0 if year_convention == "savana_360" else 365.25
    chain = []
    curr_md_start = birth_datetime

    f_start = datetime.strptime(filter_start, "%Y-%m-%d") if filter_start else None
    f_end = datetime.strptime(filter_end, "%Y-%m-%d") if filter_end else None

    for md in timeline:
        md_lord = md["lord"]
        md_duration_days = md["years"] * days_per_year
        curr_md_end = curr_md_start + timedelta(days=md_duration_days)

        # Quick boundary prune
        if f_end and curr_md_start > f_end:
            break
        if f_start and curr_md_end < f_start:
            curr_md_start = curr_md_end
            continue

        # Antardashas
        ads = generate_antardasha(md_lord)
        curr_ad_start = curr_md_start
        for ad in ads:
            ad_lord = ad["lord"]
            ad_duration_days = (md_duration_days * DASHA_YEARS[ad_lord]) / 120.0
            curr_ad_end = curr_ad_start + timedelta(days=ad_duration_days)

            if f_end and curr_ad_start > f_end:
                break
            if f_start and curr_ad_end < f_start:
                curr_ad_start = curr_ad_end
                continue

            # Pratyantardashas
            pds = compute_pratyantardasha(md_lord, ad_lord, curr_ad_start, curr_ad_end)
            for pd in pds:
                pd_s = datetime.strptime(pd["start"], "%Y-%m-%d")
                pd_e = datetime.strptime(pd["end"], "%Y-%m-%d")
                if f_start and pd_e < f_start:
                    continue
                if f_end and pd_s > f_end:
                    continue

                chain.append(pd)

            curr_ad_start = curr_ad_end

        curr_md_start = curr_md_end

    return chain


# ---------------------------------------------------------------------------
# Birth-Time Uncertainty & Dasha Stability Evaluation
# ---------------------------------------------------------------------------

def evaluate_dasha_birth_time_sensitivity(
    moon_longitude: float,
    uncertainty_minutes: float = 15.0,
) -> dict:
    """
    Quantify Dasha balance drift and Nakshatra Sandhi risk over a given birth-time error window.
    Average Moon speed is ~13.1763° / 24 hours ≈ 0.00915° per minute.
    """
    delta_deg = uncertainty_minutes * (13.1763 / 1440.0)  # ~0.137° per 15 min
    curr_nak_idx = int((moon_longitude % 360.0) / NAKSHATRA_SIZE) % 27
    lower_nak_idx = int(((moon_longitude - delta_deg) % 360.0) / NAKSHATRA_SIZE) % 27
    upper_nak_idx = int(((moon_longitude + delta_deg) % 360.0) / NAKSHATRA_SIZE) % 27

    nak_cross = (curr_nak_idx != lower_nak_idx) or (curr_nak_idx != upper_nak_idx)
    rem_in_nak = (moon_longitude % 360.0) % NAKSHATRA_SIZE
    dist_to_sandhi = min(rem_in_nak, NAKSHATRA_SIZE - rem_in_nak)

    # Shift in balance years
    curr_lord = DASHA_SEQUENCE[curr_nak_idx % 9]
    lord_total_years = DASHA_YEARS[curr_lord]
    drift_years = round((delta_deg / NAKSHATRA_SIZE) * lord_total_years, 2)

    if nak_cross:
        stability = "HIGHLY_SENSITIVE"
        description = f"Birth-time uncertainty of ±{uncertainty_minutes}m crosses Nakshatra boundary, altering starting Mahadasha lord."
    elif drift_years >= 0.5:
        stability = "MODERATELY_SENSITIVE"
        description = f"Birth-time uncertainty of ±{uncertainty_minutes}m shifts Dasha timeline by ±{drift_years} years ({int(drift_years*12)} months)."
    else:
        stability = "STABLE"
        description = f"Dasha timeline is stable within ±{drift_years} years ({int(drift_years*12)} months) for ±{uncertainty_minutes}m window."

    return {
        "stability": stability,
        "uncertainty_minutes": uncertainty_minutes,
        "moon_drift_degrees": round(delta_deg, 3),
        "dasha_drift_years": drift_years,
        "dist_to_sandhi_degrees": round(dist_to_sandhi, 3),
        "nakshatra_boundary_crossed": nak_cross,
        "description": description,
    }


# ---------------------------------------------------------------------------
# Optional Alternate Dasha Profile: Yogini Dasha (36-year cycle)
# ---------------------------------------------------------------------------

YOGINI_LORDS = [
    ("Mangala", "Moon", 1),
    ("Pingala", "Sun", 2),
    ("Dhanya", "Jupiter", 3),
    ("Bhramari", "Mars", 4),
    ("Bhadrika", "Mercury", 5),
    ("Ulka", "Saturn", 6),
    ("Siddha", "Venus", 7),
    ("Sankata", "Rahu", 8),
]
TOTAL_YOGINI_YEARS = 36


def calculate_yogini_dasha(moon_longitude: float) -> dict:
    """
    Calculate starting Yogini Dasha balance as an explicit alternate profile (Phaladeepika Ch. 20).
    Cycle = 36 years. Nakshatra index (0..26) + 3 mod 8 determines starting Yogini.
    """
    nak_index = int((moon_longitude % 360.0) / NAKSHATRA_SIZE) % 27
    yogini_idx = nak_index % 8
    name, planet, full_years = YOGINI_LORDS[yogini_idx]

    remainder = (moon_longitude % 360.0) % NAKSHATRA_SIZE
    balance_frac = (NAKSHATRA_SIZE - remainder) / NAKSHATRA_SIZE
    balance_years = round(balance_frac * full_years, 2)

    return {
        "profile": "yogini",
        "starting_yogini": name,
        "ruler_planet": planet,
        "full_years": full_years,
        "balance_years": balance_years,
        "cycle_total_years": TOTAL_YOGINI_YEARS,
    }

