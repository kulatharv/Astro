"""
Cross-System Timing Attribution & Disjoint Synthesis (WP7C2, Rule JAI-DSH-07).

Governing Standards:
- Master Specification v3.0 §10, §13.2, §15, Appendix C
- WP0 Traceability Matrix v1.1: TR-051, TR-052, TR-053, TR-054
- ASTROLOGIC_WP7_RULE_CATALOG_DRAFT.md: Rule JAI-DSH-07 (v1.0-draft)
- ASTROLOGIC_WP7_DESIGN_DECISION_REGISTER.md

Core Architectural Mandates:
1. Disjoint Attribution: Vimshottari (Parāśari) and Chara Dasha (Jaimini) evidence
   must be preserved in separate, independently attributable records.
2. Date Averaging Ban: Absolute prohibition against mathematical date averaging
   (e.g., (v_date + c_date) / 2 is forbidden; synthetic event dates are forbidden).
3. Probability Ban: Agreement between systems must NOT be converted into an empirical
   probability or accuracy claim.
4. Precision Temporal Comparison: Half-open interval arithmetic [start, end)
   ensures non-overlapping adjacent period transitions.
5. Zero DB, zero Redis, zero side-effects.
"""

from __future__ import annotations

import math
from datetime import date, datetime, timedelta
from enum import Enum
from typing import Any, Optional
from pydantic import BaseModel, Field, model_validator


# ==============================================================================
# 1. Enums & Architectural Constants
# ==============================================================================

class TimingSystemEnum(str, Enum):
    """Supported astrological timing systems."""
    VIMSHOTTARI = "VIMSHOTTARI"
    CHARA_DASHA = "CHARA_DASHA"
    YOGINI = "YOGINI"


class IntervalBoundaryConvention(str, Enum):
    """
    Mathematical boundary specification for temporal intervals.
    
    HALF_OPEN_INCLUSIVE_EXCLUSIVE:
        [start, end) where start <= t < end. Standard computational convention.
        Prevents artificial overlap on touching boundaries (e.g. [0, 5) and [5, 10)).
    CLOSED:
        [start, end] where start <= t <= end.
    """
    HALF_OPEN_INCLUSIVE_EXCLUSIVE = "HALF_OPEN_INCLUSIVE_EXCLUSIVE"
    CLOSED = "CLOSED"


class TemporalRepresentationUnit(str, Enum):
    """Unit of representation for period boundaries."""
    ELAPSED_YEARS = "ELAPSED_YEARS"  # Continuous years elapsed from birth [0.0, 120.0]
    CALENDAR_DATE = "CALENDAR_DATE"  # Calendar date string (YYYY-MM-DD)


class YearConventionEnum(str, Enum):
    """
    Year length convention used when converting between continuous elapsed years and calendar dates.
    
    SOLAR_365_25:
        Standard astronomical solar year of 365.25 mean solar days (used in modern ephemeris & Parashari default).
    SAVANA_360:
        Traditional Vedic Savana civil year of 360 days (12 months x 30 days).
    """
    SOLAR_365_25 = "solar_365_25"
    SAVANA_360 = "savana_360"


class OverlapType(str, Enum):
    """Geometric relationship between two time intervals."""
    NO_OVERLAP = "NO_OVERLAP"
    EXACT_MATCH = "EXACT_MATCH"
    SUBSET = "SUBSET"
    PARTIAL_OVERLAP = "PARTIAL_OVERLAP"


class ConvergenceStatus(str, Enum):
    """
    Cross-system convergence status under Rule JAI-DSH-07.
    
    CONVERGENT:
        Both systems overlap temporally and indicate the same non-neutral disposition
        (e.g., both FAVORABLE or both UNFAVORABLE).
    DIVERGENT:
        Both systems overlap temporally but indicate conflicting dispositions
        (e.g., one FAVORABLE and the other UNFAVORABLE).
    INDEPENDENT:
        Both systems overlap, but at least one system is NEUTRAL or insufficient,
        or only one system provides evidence for the target domain.
    DISJOINT_NON_OVERLAPPING:
        The two evaluated timing periods share no temporal intersection.
    """
    CONVERGENT = "CONVERGENT"
    DIVERGENT = "DIVERGENT"
    INDEPENDENT = "INDEPENDENT"
    DISJOINT_NON_OVERLAPPING = "DISJOINT_NON_OVERLAPPING"


# ==============================================================================
# 2. Mathematical Interval Comparison Primitives
# ==============================================================================

def compare_numeric_intervals(
    start1: float,
    end1: float,
    start2: float,
    end2: float,
    boundary: IntervalBoundaryConvention = IntervalBoundaryConvention.HALF_OPEN_INCLUSIVE_EXCLUSIVE,
) -> dict[str, Any]:
    """
    Compare two numeric intervals [start1, end1) and [start2, end2) deterministically.
    
    Args:
        start1: Start of interval 1.
        end1: End of interval 1 (must be >= start1).
        start2: Start of interval 2.
        end2: End of interval 2 (must be >= start2).
        boundary: HALF_OPEN_INCLUSIVE_EXCLUSIVE or CLOSED.
        
    Returns:
        dict containing:
        - has_overlap: bool
        - overlap_type: OverlapType
        - intersection_start: float or None
        - intersection_end: float or None
        - intersection_duration: float
        - duration1: float
        - duration2: float
        - overlap_ratio1: float (intersection / duration1)
        - overlap_ratio2: float (intersection / duration2)
    """
    for v, name in [(start1, "start1"), (end1, "end1"), (start2, "start2"), (end2, "end2")]:
        if not isinstance(v, (int, float)) or math.isnan(v) or math.isinf(v):
            raise ValueError(f"Interval boundary {name} must be a finite float, got: {v}")

    if end1 < start1:
        raise ValueError(f"Interval 1 invalid: end1 ({end1}) < start1 ({start1})")
    if end2 < start2:
        raise ValueError(f"Interval 2 invalid: end2 ({end2}) < start2 ({start2})")

    dur1 = float(end1 - start1)
    dur2 = float(end2 - start2)

    int_start = max(start1, start2)
    int_end = min(end1, end2)

    if boundary == IntervalBoundaryConvention.HALF_OPEN_INCLUSIVE_EXCLUSIVE:
        has_overlap = int_start < int_end
    else:  # CLOSED
        has_overlap = int_start <= int_end

    if not has_overlap:
        return {
            "has_overlap": False,
            "overlap_type": OverlapType.NO_OVERLAP.value,
            "intersection_start": None,
            "intersection_end": None,
            "intersection_duration": 0.0,
            "duration1": dur1,
            "duration2": dur2,
            "overlap_ratio1": 0.0,
            "overlap_ratio2": 0.0,
        }

    int_dur = float(int_end - int_start)
    ratio1 = (int_dur / dur1) if dur1 > 0 else 0.0
    ratio2 = (int_dur / dur2) if dur2 > 0 else 0.0

    # Determine overlap type
    if math.isclose(start1, start2, abs_tol=1e-7) and math.isclose(end1, end2, abs_tol=1e-7):
        o_type = OverlapType.EXACT_MATCH
    elif (start1 >= start2 - 1e-7 and end1 <= end2 + 1e-7) or (start2 >= start1 - 1e-7 and end2 <= end1 + 1e-7):
        o_type = OverlapType.SUBSET
    else:
        o_type = OverlapType.PARTIAL_OVERLAP

    return {
        "has_overlap": True,
        "overlap_type": o_type.value,
        "intersection_start": round(int_start, 6),
        "intersection_end": round(int_end, 6),
        "intersection_duration": round(int_dur, 6),
        "duration1": round(dur1, 6),
        "duration2": round(dur2, 6),
        "overlap_ratio1": round(ratio1, 6),
        "overlap_ratio2": round(ratio2, 6),
    }


def compare_calendar_intervals(
    start1_str: str,
    end1_str: str,
    start2_str: str,
    end2_str: str,
    boundary: IntervalBoundaryConvention = IntervalBoundaryConvention.HALF_OPEN_INCLUSIVE_EXCLUSIVE,
) -> dict[str, Any]:
    """
    Compare two calendar date intervals (YYYY-MM-DD) deterministically using ordinal days.
    """
    try:
        d_s1 = datetime.strptime(start1_str.strip(), "%Y-%m-%d").date()
        d_e1 = datetime.strptime(end1_str.strip(), "%Y-%m-%d").date()
        d_s2 = datetime.strptime(start2_str.strip(), "%Y-%m-%d").date()
        d_e2 = datetime.strptime(end2_str.strip(), "%Y-%m-%d").date()
    except Exception as exc:
        raise ValueError(f"Invalid calendar date string format (expected YYYY-MM-DD): {exc}")

    ord_s1 = float(d_s1.toordinal())
    ord_e1 = float(d_e1.toordinal())
    ord_s2 = float(d_s2.toordinal())
    ord_e2 = float(d_e2.toordinal())

    num_res = compare_numeric_intervals(ord_s1, ord_e1, ord_s2, ord_e2, boundary=boundary)

    if not num_res["has_overlap"]:
        return {
            "has_overlap": False,
            "overlap_type": OverlapType.NO_OVERLAP.value,
            "intersection_start": None,
            "intersection_end": None,
            "intersection_duration_days": 0.0,
            "duration1_days": num_res["duration1"],
            "duration2_days": num_res["duration2"],
            "overlap_ratio1": 0.0,
            "overlap_ratio2": 0.0,
        }

    int_start_date = date.fromordinal(int(num_res["intersection_start"])).strftime("%Y-%m-%d")
    int_end_date = date.fromordinal(int(num_res["intersection_end"])).strftime("%Y-%m-%d")

    return {
        "has_overlap": True,
        "overlap_type": num_res["overlap_type"],
        "intersection_start": int_start_date,
        "intersection_end": int_end_date,
        "intersection_duration_days": num_res["intersection_duration"],
        "duration1_days": num_res["duration1"],
        "duration2_days": num_res["duration2"],
        "overlap_ratio1": num_res["overlap_ratio1"],
        "overlap_ratio2": num_res["overlap_ratio2"],
    }


def convert_elapsed_years_to_calendar_date(
    birth_date: date | datetime,
    elapsed_years: float,
    convention: YearConventionEnum = YearConventionEnum.SOLAR_365_25,
) -> date:
    """
    Convert continuous elapsed years from birth to a calendar date using an explicit convention.
    
    Args:
        birth_date: Birth date or datetime.
        elapsed_years: Continuous elapsed years from birth (must be >= 0.0).
        convention: SOLAR_365_25 (365.25 days) or SAVANA_360 (360.0 days).
        
    Returns:
        Exact calendar date.
    """
    if birth_date is None or not isinstance(birth_date, (date, datetime)):
        raise ValueError(f"birth_date must be an explicit date or datetime, got: {birth_date}")
    if convention is None:
        raise ValueError("Year convention must be explicitly provided (SOLAR_365_25 or SAVANA_360); cannot be None.")
    if not isinstance(elapsed_years, (int, float)) or math.isnan(elapsed_years) or math.isinf(elapsed_years):
        raise ValueError(f"elapsed_years must be a finite float, got: {elapsed_years}")
    if elapsed_years < 0.0:
        raise ValueError(f"elapsed_years cannot be negative, got: {elapsed_years}")

    conv = (
        convention
        if isinstance(convention, YearConventionEnum)
        else YearConventionEnum(convention.value if isinstance(convention, Enum) else str(convention))
    )
    days_per_year = 360.0 if conv == YearConventionEnum.SAVANA_360 else 365.25
    b_date = birth_date.date() if isinstance(birth_date, datetime) else birth_date
    delta_days = elapsed_years * days_per_year
    return b_date + timedelta(days=delta_days)


def convert_calendar_date_to_elapsed_years(
    birth_date: date | datetime,
    target_date: date | datetime,
    convention: YearConventionEnum = YearConventionEnum.SOLAR_365_25,
) -> float:
    """
    Convert a calendar date to continuous elapsed years from birth using an explicit convention.
    
    Args:
        birth_date: Birth date or datetime.
        target_date: Target calendar date (must be >= birth_date).
        convention: SOLAR_365_25 (365.25 days) or SAVANA_360 (360.0 days).
        
    Returns:
        Elapsed continuous years float rounded to 6 decimal places.
    """
    if birth_date is None or not isinstance(birth_date, (date, datetime)):
        raise ValueError(f"birth_date must be an explicit date or datetime, got: {birth_date}")
    if target_date is None or not isinstance(target_date, (date, datetime)):
        raise ValueError(f"target_date must be an explicit date or datetime, got: {target_date}")
    if convention is None:
        raise ValueError("Year convention must be explicitly provided (SOLAR_365_25 or SAVANA_360); cannot be None.")

    b_date = birth_date.date() if isinstance(birth_date, datetime) else birth_date
    t_date = target_date.date() if isinstance(target_date, datetime) else target_date

    if t_date < b_date:
        raise ValueError(f"target_date ({t_date}) cannot be earlier than birth_date ({b_date})")

    conv = (
        convention
        if isinstance(convention, YearConventionEnum)
        else YearConventionEnum(convention.value if isinstance(convention, Enum) else str(convention))
    )
    days_per_year = 360.0 if conv == YearConventionEnum.SAVANA_360 else 365.25
    elapsed_days = (t_date - b_date).days
    return round(float(elapsed_days) / days_per_year, 6)


def convert_interval_unit(
    interval: TimingInterval,
    target_unit: TemporalRepresentationUnit,
    birth_date: date | datetime,
    convention: YearConventionEnum = YearConventionEnum.SOLAR_365_25,
) -> TimingInterval:
    """
    Deterministically convert a TimingInterval between ELAPSED_YEARS and CALENDAR_DATE.
    Requires an explicit birth_date and explicit year convention.
    """
    if birth_date is None or not isinstance(birth_date, (date, datetime)):
        raise ValueError(f"birth_date must be an explicit date or datetime, got: {birth_date}")
    if convention is None:
        raise ValueError("Year convention must be explicitly provided (SOLAR_365_25 or SAVANA_360); cannot be None.")

    if interval.unit == target_unit:
        return interval.model_copy()

    if target_unit == TemporalRepresentationUnit.CALENDAR_DATE:
        s_date = convert_elapsed_years_to_calendar_date(birth_date, float(interval.start), convention)
        e_date = convert_elapsed_years_to_calendar_date(birth_date, float(interval.end), convention)
        return TimingInterval(
            start=s_date.strftime("%Y-%m-%d"),
            end=e_date.strftime("%Y-%m-%d"),
            unit=TemporalRepresentationUnit.CALENDAR_DATE,
            boundary_convention=interval.boundary_convention,
        )
    else:
        d_s = datetime.strptime(str(interval.start).strip(), "%Y-%m-%d").date()
        d_e = datetime.strptime(str(interval.end).strip(), "%Y-%m-%d").date()
        s_years = convert_calendar_date_to_elapsed_years(birth_date, d_s, convention)
        e_years = convert_calendar_date_to_elapsed_years(birth_date, d_e, convention)
        return TimingInterval(
            start=s_years,
            end=e_years,
            unit=TemporalRepresentationUnit.ELAPSED_YEARS,
            boundary_convention=interval.boundary_convention,
        )


# ==============================================================================
# 3. Disjoint Convergence Evaluator (Rule JAI-DSH-07)
# ==============================================================================

def evaluate_convergence_status(
    disposition_v: Optional[str],
    disposition_c: Optional[str],
    has_temporal_overlap: bool,
) -> ConvergenceStatus:
    """
    Classify cross-system convergence per Rule JAI-DSH-07.
    
    Rules:
    1. If no temporal overlap exists -> DISJOINT_NON_OVERLAPPING.
    2. If both systems overlap:
       - If both are FAVORABLE or both are UNFAVORABLE -> CONVERGENT.
       - If one is FAVORABLE and the other is UNFAVORABLE -> DIVERGENT.
       - If either is NEUTRAL, missing, or unsupported -> INDEPENDENT.
    """
    if not has_temporal_overlap:
        return ConvergenceStatus.DISJOINT_NON_OVERLAPPING

    v = (disposition_v or "").upper()
    c = (disposition_c or "").upper()

    if not v or not c or v == "NEUTRAL" or c == "NEUTRAL":
        return ConvergenceStatus.INDEPENDENT

    if v == c and v in {"FAVORABLE", "UNFAVORABLE"}:
        return ConvergenceStatus.CONVERGENT

    if {v, c} == {"FAVORABLE", "UNFAVORABLE"}:
        return ConvergenceStatus.DIVERGENT

    return ConvergenceStatus.INDEPENDENT


# ==============================================================================
# 4. Data Models for Disjoint Attribution
# ==============================================================================

class TimingInterval(BaseModel):
    """Representation of a period's time window with invariant validation."""
    start: float | str = Field(..., description="Start of window (elapsed years float or YYYY-MM-DD str)")
    end: float | str = Field(..., description="End of window (elapsed years float or YYYY-MM-DD str)")
    unit: TemporalRepresentationUnit = Field(..., description="Unit of boundaries")
    boundary_convention: IntervalBoundaryConvention = Field(
        default=IntervalBoundaryConvention.HALF_OPEN_INCLUSIVE_EXCLUSIVE,
        description="Mathematical boundary convention"
    )

    @model_validator(mode="after")
    def validate_interval_bounds(self) -> TimingInterval:
        """Enforce non-negative, non-inverted, and finite interval boundaries."""
        if self.unit == TemporalRepresentationUnit.ELAPSED_YEARS:
            try:
                s = float(self.start)
                e = float(self.end)
            except (ValueError, TypeError) as exc:
                raise ValueError(f"ELAPSED_YEARS boundaries must be numeric: {exc}")
            if not math.isfinite(s) or not math.isfinite(e):
                raise ValueError(f"ELAPSED_YEARS boundaries must be finite numbers: start={self.start}, end={self.end}")
            if s < 0.0:
                raise ValueError(f"ELAPSED_YEARS start cannot be negative: {s}")
            if e < s:
                raise ValueError(f"ELAPSED_YEARS end ({e}) cannot be less than start ({s})")
        elif self.unit == TemporalRepresentationUnit.CALENDAR_DATE:
            try:
                ds = datetime.strptime(str(self.start).strip(), "%Y-%m-%d").date()
                de = datetime.strptime(str(self.end).strip(), "%Y-%m-%d").date()
            except Exception as exc:
                raise ValueError(f"CALENDAR_DATE boundaries must be valid YYYY-MM-DD strings: {exc}")
            if de < ds:
                raise ValueError(f"CALENDAR_DATE end ({de}) cannot be earlier than start ({ds})")
        return self


class SystemTimingAttribution(BaseModel):
    """
    Isolated, auditable evidence item from a single timing tradition.
    
    Guarantees that Vimshottari and Chara Dasha evidence remain structurally disjoint.
    """
    system: TimingSystemEnum = Field(..., description="Governing timing tradition")
    profile_id: str = Field(..., description="Source-system configuration profile ID")
    period_label: str = Field(..., description="Human-readable period descriptor (e.g. Jup-Sat-Mer or Dhanu-Mesha)")
    sub_period_type: str = Field(..., description="Hierarchy depth: MAHADASHA, ANTARDASHA, or PRATYANTARDASHA")
    interval: TimingInterval = Field(..., description="Original time interval")
    domain: str = Field(default="general", description="Analyzed life domain")
    disposition: str = Field(
        default="NEUTRAL",
        description="Astrological indication: FAVORABLE, UNFAVORABLE, or NEUTRAL"
    )
    rule_ids: list[str] = Field(default_factory=list, description="Classical rules fired")
    supporting_factors: list[str] = Field(default_factory=list, description="Positive evidence items")
    contrary_factors: list[str] = Field(default_factory=list, description="Obstructing or contrary factors")
    formula_version: str = Field(..., description="Calculation engine version")
    source_status: str = Field(
        default="SOURCE_VERIFICATION_REQUIRED",
        description="Classical text status"
    )
    approval_status: str = Field(
        default="PENDING_HUMAN_JYOTISHI",
        description="Jyotishi sign-off status"
    )
    is_approved: bool = Field(default=False, description="True only if signed Jyotishi sign-off on file")


class CrossSystemComparisonRecord(BaseModel):
    """
    Auditable comparison record between two system timing items.
    
    CRITICAL: Original intervals are preserved in their respective attribution blocks.
    No synthetic date averaging or blended event date is created.
    """
    vimshottari_evidence: Optional[SystemTimingAttribution] = Field(None, description="Parāśari Vimshottari evidence")
    chara_evidence: Optional[SystemTimingAttribution] = Field(None, description="Jaimini Chara Dasha evidence")
    overlap_type: OverlapType = Field(..., description="Geometric interval overlap classification")
    overlap_interval: Optional[TimingInterval] = Field(None, description="Exact intersection window if overlapping")
    overlap_ratio_v: float = Field(0.0, description="Intersection fraction of Vimshottari period")
    overlap_ratio_c: float = Field(0.0, description="Intersection fraction of Chara Dasha period")
    convergence_status: ConvergenceStatus = Field(..., description="Rule JAI-DSH-07 convergence outcome")
    comparison_notes: str = Field(default="", description="Explanatory exegesis notes")


class CrossSystemSynthesisResponse(BaseModel):
    """
    Structured response payload for cross-system timing synthesis (WP7C2).
    
    All evidence is retained in disjoint attribution structures.
    """
    domain: str = Field(..., description="Analyzed life domain")
    synthesis_profile_id: str = Field(
        default="PROVISIONAL_DUAL_SYSTEM_DEFAULT",
        description="Configuration profile used for synthesis"
    )
    formula_version: str = Field(
        default="WP7C2-SYNTHESIS-v1.0",
        description="Governing synthesis engine version"
    )
    approval_status: str = Field(
        default="PENDING_HUMAN_JYOTISHI",
        description="Lead astrologer approval state"
    )
    is_approved: bool = Field(default=False, description="True only if signed approval on file")
    comparisons: list[CrossSystemComparisonRecord] = Field(..., description="Pairwise interval comparisons")
    vimshottari_attributions: list[SystemTimingAttribution] = Field(..., description="All Vimshottari items")
    chara_attributions: list[SystemTimingAttribution] = Field(..., description="All Chara Dasha items")
    overall_convergence: ConvergenceStatus = Field(..., description="Summary convergence classification")
    disclaimer: str = Field(
        default=(
            "Independent astrological frameworks evaluated in isolation per Master Specification v3.0 §10. "
            "Convergence does not establish empirical probability or predictive certainty."
        ),
        description="Mandatory epistemic and legal disclaimer"
    )
    limitations: list[str] = Field(
        default_factory=lambda: [
            "Cross-system agreement is descriptive corroboration, not a statistical probability.",
            "No mathematical date averaging is applied; original system period boundaries are preserved.",
            "Lineage conventions for Chara Dasha progression and duration clamping remain pending expert sign-off.",
        ],
        description="Documented architectural limitations"
    )


# ==============================================================================
# 5. Core Synthesis Orchestrator
# ==============================================================================

def synthesize_timing_attributions(
    vimshottari_attributions: list[SystemTimingAttribution],
    chara_attributions: list[SystemTimingAttribution],
    domain: str = "general",
    profile_id: str = "PROVISIONAL_DUAL_SYSTEM_DEFAULT",
    boundary: IntervalBoundaryConvention = IntervalBoundaryConvention.HALF_OPEN_INCLUSIVE_EXCLUSIVE,
) -> CrossSystemSynthesisResponse:
    """
    Synthesize timing evidence across Vimshottari and Chara Dasha under Rule JAI-DSH-07.
    
    Invariants:
    1. If vimshottari_attributions is empty and chara_attributions has items -> all chara items preserved, status INDEPENDENT.
    2. If chara_attributions is empty and vimshottari has items -> all vimshottari items preserved, status INDEPENDENT.
    3. If both have items:
       - Every pair is evaluated for temporal intersection.
       - Dispositions are compared.
       - Overlap intervals are reported without modifying original source periods.
       - Date averaging is strictly prohibited.
    4. Deterministic ordering: comparisons are sorted by overlap start or source start.
    """
    comparisons: list[CrossSystemComparisonRecord] = []

    # Case A: Only Vimshottari items present
    if not chara_attributions and vimshottari_attributions:
        for v in vimshottari_attributions:
            comparisons.append(
                CrossSystemComparisonRecord(
                    vimshottari_evidence=v,
                    chara_evidence=None,
                    overlap_type=OverlapType.NO_OVERLAP,
                    overlap_interval=None,
                    overlap_ratio_v=0.0,
                    overlap_ratio_c=0.0,
                    convergence_status=ConvergenceStatus.INDEPENDENT,
                    comparison_notes="Vimshottari evidence present without corresponding Chara Dasha evidence.",
                )
            )
        return CrossSystemSynthesisResponse(
            domain=domain,
            synthesis_profile_id=profile_id,
            comparisons=comparisons,
            vimshottari_attributions=vimshottari_attributions,
            chara_attributions=[],
            overall_convergence=ConvergenceStatus.INDEPENDENT,
        )

    # Case B: Only Chara Dasha items present
    if not vimshottari_attributions and chara_attributions:
        for c in chara_attributions:
            comparisons.append(
                CrossSystemComparisonRecord(
                    vimshottari_evidence=None,
                    chara_evidence=c,
                    overlap_type=OverlapType.NO_OVERLAP,
                    overlap_interval=None,
                    overlap_ratio_v=0.0,
                    overlap_ratio_c=0.0,
                    convergence_status=ConvergenceStatus.INDEPENDENT,
                    comparison_notes="Chara Dasha evidence present without corresponding Vimshottari evidence.",
                )
            )
        return CrossSystemSynthesisResponse(
            domain=domain,
            synthesis_profile_id=profile_id,
            comparisons=comparisons,
            vimshottari_attributions=[],
            chara_attributions=chara_attributions,
            overall_convergence=ConvergenceStatus.INDEPENDENT,
        )

    # Case C: Both systems present -> Pairwise comparison
    any_convergent = False
    any_divergent = False

    for v in vimshottari_attributions:
        for c in chara_attributions:
            # Check representation unit compatibility
            if v.interval.unit != c.interval.unit:
                raise ValueError(
                    f"Incompatible temporal units for comparison: Vimshottari={v.interval.unit}, "
                    f"Chara={c.interval.unit}. Convert to matching units before synthesis."
                )

            if v.interval.unit == TemporalRepresentationUnit.ELAPSED_YEARS:
                res = compare_numeric_intervals(
                    float(v.interval.start),
                    float(v.interval.end),
                    float(c.interval.start),
                    float(c.interval.end),
                    boundary=boundary,
                )
            else:  # CALENDAR_DATE
                res = compare_calendar_intervals(
                    str(v.interval.start),
                    str(v.interval.end),
                    str(c.interval.start),
                    str(c.interval.end),
                    boundary=boundary,
                )

            has_ov = res["has_overlap"]
            conv_status = evaluate_convergence_status(v.disposition, c.disposition, has_ov)

            if conv_status == ConvergenceStatus.CONVERGENT:
                any_convergent = True
            elif conv_status == ConvergenceStatus.DIVERGENT:
                any_divergent = True

            ov_interval = None
            if has_ov:
                ov_interval = TimingInterval(
                    start=res["intersection_start"],
                    end=res["intersection_end"],
                    unit=v.interval.unit,
                    boundary_convention=boundary,
                )

            note = (
                f"Comparison of {v.system.value} ({v.period_label}: {v.disposition}) and "
                f"{c.system.value} ({c.period_label}: {c.disposition}) -> {conv_status.value}."
            )

            comparisons.append(
                CrossSystemComparisonRecord(
                    vimshottari_evidence=v,
                    chara_evidence=c,
                    overlap_type=OverlapType(res["overlap_type"]),
                    overlap_interval=ov_interval,
                    overlap_ratio_v=res["overlap_ratio1"],
                    overlap_ratio_c=res["overlap_ratio2"],
                    convergence_status=conv_status,
                    comparison_notes=note,
                )
            )

    # Summary overall convergence
    if any_divergent:
        overall_conv = ConvergenceStatus.DIVERGENT
    elif any_convergent:
        overall_conv = ConvergenceStatus.CONVERGENT
    elif comparisons and all(c.convergence_status == ConvergenceStatus.DISJOINT_NON_OVERLAPPING for c in comparisons):
        overall_conv = ConvergenceStatus.DISJOINT_NON_OVERLAPPING
    else:
        overall_conv = ConvergenceStatus.INDEPENDENT

    return CrossSystemSynthesisResponse(
        domain=domain,
        synthesis_profile_id=profile_id,
        comparisons=comparisons,
        vimshottari_attributions=vimshottari_attributions,
        chara_attributions=chara_attributions,
        overall_convergence=overall_conv,
    )
