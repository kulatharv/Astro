"""
Jaimini Astrology Foundational Orchestrator & Schemas (WP7A).

Governing Standard: Master Specification v3.0 §10, §9.1, §9.2, §15, Appendix C;
WP0 TR-051 to TR-054; ASTROLOGIC_WP7_DESIGN_DECISION_REGISTER.md.

This module provides:
1. Typed configuration profiles and enums for all lineage decisions (DEC-JAI-01 to DEC-JAI-09).
2. Input validation for finite degrees, valid signs, and required candidate bodies.
3. Provenance metadata tracking, explicitly identifying unapproved provisional defaults.
4. Deterministic computation of Chara Karakas (7-k and 8-k), Arudhas (A1-A12, AL, UL),
   and Rashi Drishti structural sign aspects.
5. Strict isolation from production release and prediction exposure.
"""

from __future__ import annotations

import math
from enum import Enum
from typing import Any, Optional
from pydantic import BaseModel, Field

from shared.veda.jaimini_rules import (
    KarakaSchemeEnum,
    TieBreakerEnum,
    ArudhaExceptionEnum,
    DualLordshipEnum,
    RashiMobilityEnum,
    CHARA_SIGNS,
    STHIRA_SIGNS,
    DVISVABHAVA_SIGNS,
    SIGN_NAMES_SK,
    SIGN_NAMES_EN,
    PARASHARI_SIGN_LORDS,
    parse_sign_index,
    validate_finite_degree,
    calculate_chara_karakas,
    calculate_arudha_pada,
    calculate_upapada_lagna,
    calculate_all_arudhas,
    get_rashi_drishti,
    compute_rahu_traversal_arc,
)
from shared.veda.jaimini_dasha import (
    CharaProgressionTradition,
    DurationClampMode,
    SignCountingConvention,
    AntardashaOrderConvention,
    get_chara_dasha_progression,
    calculate_mahadasha_duration,
    calculate_antardashas,
    calculate_chara_dasha_cycle,
)
from shared.veda.jaimini_evidence import (
    KarakamsaFramingMode,
    KetuArgalaConvention,
    calculate_navamsha_sign,
    evaluate_karakamsa,
    evaluate_argala,
    evaluate_all_house_argalas,
    ARGALA_PAIRS,
    NATURAL_BENEFICS,
    NATURAL_MALEFICS,
)
from shared.veda.jaimini_synthesis import (
    TimingSystemEnum,
    IntervalBoundaryConvention,
    TemporalRepresentationUnit,
    YearConventionEnum,
    OverlapType,
    ConvergenceStatus,
    TimingInterval,
    SystemTimingAttribution,
    CrossSystemComparisonRecord,
    CrossSystemSynthesisResponse,
    compare_numeric_intervals,
    compare_calendar_intervals,
    convert_elapsed_years_to_calendar_date,
    convert_calendar_date_to_elapsed_years,
    convert_interval_unit,
    evaluate_convergence_status,
    synthesize_timing_attributions,
)


# ==============================================================================
# 1. Lineage Decision Enums (DEC-JAI-01 to DEC-JAI-09)
# ==============================================================================

class ApprovalStatus(str, Enum):
    """Governance status of astrological decisions and profiles."""
    PENDING_HUMAN_JYOTISHI = "PENDING_HUMAN_JYOTISHI"
    PROVISIONAL_DEVELOPMENT_ONLY = "PROVISIONAL_DEVELOPMENT_ONLY_UNAPPROVED"
    APPROVED_VERIFIED = "APPROVED_VERIFIED"


class SourceVerificationStatus(str, Enum):
    """Source verification status for classical conventions."""
    CITATION_VERIFIED = "CITATION_VERIFIED"
    EXEGETICAL_DISPUTE = "EXEGETICAL_DISPUTE"
    SOURCE_VERIFICATION_REQUIRED = "SOURCE_VERIFICATION_REQUIRED"


# Aliases to shared.veda enums for backward compatibility and clean API
CharaTraditionEnum = CharaProgressionTradition
DurationClampEnum = DurationClampMode
KarakamsaModeEnum = KarakamsaFramingMode
KetuArgalaEnum = KetuArgalaConvention


# ==============================================================================
# 2. Configuration Profiles & Provenance Schemas
# ==============================================================================

class DecisionProvenance(BaseModel):
    """Audit record for an individual lineage decision."""
    decision_id: str = Field(..., description="DEC-JAI-XX identifier")
    area: str = Field(..., description="Astrological subsystem (Karakas, Arudhas, Timing, etc.)")
    convention_name: str = Field(..., description="Short name of the convention")
    selected_value: str = Field(..., description="Currently active setting")
    approval_status: ApprovalStatus = Field(
        default=ApprovalStatus.PENDING_HUMAN_JYOTISHI,
        description="Approval state by supervising human Jyotishi"
    )
    source_status: SourceVerificationStatus = Field(
        ..., description="Verification state against primary texts"
    )
    is_approved: bool = Field(
        default=False,
        description="True ONLY if formal human Jyotishi sign-off is on file"
    )
    notes: str = Field(default="", description="Exegesis notes or implementation constraints")


class JaiminiProfileConfig(BaseModel):
    """
    Typed configuration profile for Jaimini calculations.
    
    Default profile is explicitly tagged PROVISIONAL_DEVELOPMENT_ONLY_UNAPPROVED
    under governance rule: Never silently substitute lineage without documentation.
    """
    profile_id: str = Field(
        default="PROVISIONAL_KN_RAO_DEFAULT",
        description="Unique profile identifier"
    )
    is_approved: bool = Field(
        default=False,
        description="Whether this profile has signed human approval"
    )
    approval_status: ApprovalStatus = Field(
        default=ApprovalStatus.PROVISIONAL_DEVELOPMENT_ONLY,
        description="Governance status"
    )
    # DEC-JAI-01: 7 vs 8 karakas
    karaka_scheme: KarakaSchemeEnum = Field(
        default=KarakaSchemeEnum.SEVEN_KARAKA,
        description="7-karaka (K.N. Rao) vs 8-karaka (Sanjay Rath)"
    )
    # DEC-JAI-02: Rahu traversal inversion
    rahu_reverse: bool = Field(
        default=True,
        description="True: tau = 30 - deg. False: direct degree."
    )
    # DEC-JAI-03: Arcdegree tie-breaking
    tie_breaker: TieBreakerEnum = Field(
        default=TieBreakerEnum.NATURAL_SPEED,
        description="Deterministic software fallback for identical degrees"
    )
    # DEC-JAI-04: Scorpio/Aquarius dual lordship
    dual_lordship: DualLordshipEnum = Field(
        default=DualLordshipEnum.PARASHARI_SINGLE,
        description="Single rulership vs dual co-rulership"
    )
    # DEC-JAI-05: Chara Dasha progression tradition
    chara_tradition: CharaTraditionEnum = Field(
        default=CharaTraditionEnum.KN_RAO,
        description="Chara Dasha order tradition"
    )
    # DEC-JAI-06: Dasha duration clamping
    duration_clamp: DurationClampEnum = Field(
        default=DurationClampEnum.CLAMPED_1_TO_12,
        description="Clamping dasha length to [1, 12] years"
    )
    # Counting direction from sign to lord
    counting_convention: SignCountingConvention = Field(
        default=SignCountingConvention.KN_RAO_GROUPS,
        description="Sign displacement counting direction convention"
    )
    # Antardasha sub-period progression order
    antardasha_convention: AntardashaOrderConvention = Field(
        default=AntardashaOrderConvention.KN_RAO,
        description="Antardasha sub-period ordering convention"
    )
    # Start sign selection convention
    start_sign_convention: str = Field(
        default="LAGNA",
        description="Start sign selection convention (LAGNA, SEVENTH_HOUSE)"
    )
    # DEC-JAI-07: Karakamsa mode
    karakamsa_mode: KarakamsaModeEnum = Field(
        default=KarakamsaModeEnum.NAVAMSHA_IN_RASHI,
        description="Navamsha sign of AK projected in D1 vs D9 chart"
    )
    # DEC-JAI-08: Ketu Argala direction
    ketu_argala: KetuArgalaEnum = Field(
        default=KetuArgalaEnum.STANDARD_ARGALA,
        description="Standard direct vs reverse Argala for Ketu"
    )
    # DEC-JAI-09: Arudha 1st/7th exceptions
    arudha_exception: ArudhaExceptionEnum = Field(
        default=ArudhaExceptionEnum.STANDARD_EXCEPTION,
        description="BPHS Pada-locus 10th/4th shifts"
    )


class JaiminiProvenanceMetadata(BaseModel):
    """Comprehensive provenance block emitted with all Jaimini outputs."""
    profile_id: str
    profile_approval_status: str
    profile_is_approved: bool
    formula_version: str = "WP7C2-JAIMINI-FOUNDATION-v1.0"
    decisions: list[DecisionProvenance]
    tie_breaker_invoked: bool = False
    tie_broken_planets: list[str] = Field(default_factory=list)
    tie_break_notes: list[str] = Field(default_factory=list)
    exceptions_invoked: list[str] = Field(default_factory=list)
    rahu_traversal_metric_applied: Optional[str] = None


# ==============================================================================
# 3. Output Schemas
# ==============================================================================

class CharaKarakaDetail(BaseModel):
    """Detailed role assignment for a Chara Karaka."""
    role: str = Field(..., description="Karaka abbreviation: AK, AmK, BK, MK, PiK, PK, GK, DK")
    planet: str = Field(..., description="Planetary body name")
    rank: int = Field(..., description="Zero-based ranking index")
    degree_in_sign: float = Field(..., description="Raw degree within sign [0.0, 30.0)")
    traversed_arc: float = Field(..., description="Effective traversed arc [0.0, 30.0]")
    sign_index: int = Field(..., description="1-indexed zodiac sign")
    sign_name: str = Field(..., description="Sanskrit sign name")
    is_tie_broken: bool = Field(default=False, description="Whether rank was decided via tie-breaker")


class ArudhaDetail(BaseModel):
    """Calculation details for an Arudha Pada."""
    house_num: int = Field(..., ge=1, le=12, description="Target source house (1..12)")
    name: str = Field(..., description="Arudha symbol (AL, A2..A11, UL)")
    house_sign: int = Field(..., ge=1, le=12, description="Sign of source house")
    house_sign_name: str = Field(..., description="Sanskrit name of source sign")
    lord_planet: str = Field(..., description="Governing lord of the house")
    lord_sign: int = Field(..., ge=1, le=12, description="Sign occupied by the house lord")
    lord_sign_name: str = Field(..., description="Sanskrit name of lord sign")
    raw_pada: int = Field(..., ge=1, le=12, description="Symmetrical reflection sign before exception")
    final_pada: int = Field(..., ge=1, le=12, description="Final Arudha Pada sign after exception")
    final_sign_name: str = Field(..., description="Sanskrit name of final Arudha sign")
    exception_applied: bool = Field(..., description="True if 1st/7th exception fired")
    exception_type: Optional[str] = Field(None, description="SWASTHA_10TH_SHIFT or SAPTAMA_4TH_SHIFT")
    is_upapada: bool = Field(default=False, description="True if this is Upapada Lagna (A12)")
    house_from_lagna: Optional[int] = Field(None, description="House number relative to natal Lagna")


class RashiDrishtiDetail(BaseModel):
    """Sign-aspect relationship for a zodiac sign."""
    sign_index: int = Field(..., ge=1, le=12, description="Source sign index")
    sign_name: str = Field(..., description="Sanskrit sign name")
    sign_type: str = Field(..., description="CHARA, STHIRA, or DVISVABHAVA")
    aspects_signs: list[int] = Field(..., description="List of 3 aspected sign indices")
    aspects_sign_names: list[str] = Field(..., description="Sanskrit names of aspected signs")


class AntardashaDetail(BaseModel):
    """Sub-period details for a Mahadasha."""
    antardasha_index: int = Field(..., ge=1, le=12, description="1-indexed rank within Mahadasha")
    sign: int = Field(..., ge=1, le=12, description="Sign index")
    sign_name: str = Field(..., description="Sanskrit sign name")
    duration_years_fractional: float = Field(..., description="Fractional years (D / 12.0)")
    duration_months: float = Field(..., description="Duration in months (D months)")
    parent_mahadasha_sign: int = Field(..., ge=1, le=12, description="Governing Mahadasha sign")


class MahadashaCalculationDetail(BaseModel):
    """Detailed calculation trace for a Mahadasha sign."""
    sign: int
    sign_name: str
    lord_planet: str
    lord_sign: int
    lord_sign_name: str
    is_forward_counting: bool
    displacement_count: int
    is_own_sign: bool
    base_years: int
    dignity: str
    dignity_modifier: int
    raw_years: int
    final_years: int
    clamp_mode: str
    is_clamped: bool
    rule_note: str


class MahadashaDetail(BaseModel):
    """Full Mahadasha period specification."""
    order_index: int = Field(..., ge=1, le=12, description="Sequential rank in progression")
    sign: int = Field(..., ge=1, le=12, description="Mahadasha sign index")
    sign_name: str = Field(..., description="Sanskrit sign name")
    sign_name_en: str = Field(..., description="English sign name")
    duration_years: int = Field(..., ge=0, le=12, description="Final duration in years")
    elapsed_start_years: float = Field(..., description="Cumulative elapsed start years")
    elapsed_end_years: float = Field(..., description="Cumulative elapsed end years")
    calculation_details: MahadashaCalculationDetail
    antardashas: list[AntardashaDetail] = Field(..., description="All 12 sub-periods")


class CharaDashaCycleResponse(BaseModel):
    """Complete 12-sign Chara Dasha cycle with all 144 Antardashas."""
    start_sign: int = Field(..., ge=1, le=12)
    start_sign_name: str
    lagna_sign: int = Field(..., ge=1, le=12)
    lagna_sign_name: str
    tradition: str
    direction_description: str
    is_progression_forward: bool
    clamp_mode: str
    counting_convention: str
    antardasha_convention: str
    total_cycle_years: float
    mahadasha_count: int = 12
    total_antardasha_count: int = 144
    mahadashas: list[MahadashaDetail]


class KarakamsaEvidenceResponse(BaseModel):
    """Detailed evidence for Karakamsa framing (WP7C1, DEC-JAI-07)."""
    ak_planet: str = Field(..., description="Planetary body acting as Atmakaraka (AK)")
    ak_d1_sign: int = Field(..., ge=1, le=12, description="D1 sign of Atmakaraka")
    ak_d1_sign_name: str = Field(..., description="Sanskrit name of D1 sign")
    ak_degree_in_sign: float = Field(..., description="AK degree within sign [0, 30)")
    karakamsa_sign: int = Field(..., ge=1, le=12, description="Navamsha sign of AK (Karakamsa)")
    karakamsa_sign_name: str = Field(..., description="Sanskrit name of Karakamsa sign")
    karakamsa_sign_name_en: str = Field(..., description="English name of Karakamsa sign")
    framing_mode: str = Field(..., description="NAVAMSHA_IN_RASHI or KARAKAMSA_KUNDALI_D9")
    frame_chart_type: str = Field(..., description="D1_RASHI or D9_NAVAMSHA")
    house_from_lagna: Optional[int] = Field(None, description="House offset from Lagna in D1 (if D1 frame)")
    description: str = Field(..., description="Human-readable framing description")
    signs_by_house: dict[int, int] = Field(..., description="House 1..12 from Karakamsa -> Sign index")
    planets_by_house: dict[int, list[str]] = Field(..., description="House 1..12 from Karakamsa -> Occupants")
    active_planet_signs: dict[str, int] = Field(..., description="Planets and their signs in active reference chart")


class ArgalaPositionEvidence(BaseModel):
    """Evidence for an individual Argala and Virodhargala offset pair (WP7C1, Rule JAI-ASP-02)."""
    argala_offset: int = Field(..., description="Intervention house offset (2, 4, 11, 5)")
    argala_sign: int = Field(..., ge=1, le=12, description="Sign index of Argala house")
    argala_sign_name: str = Field(..., description="Sanskrit name of Argala sign")
    argala_planets: list[str] = Field(..., description="Planetary bodies causing Argala")
    argala_count: int = Field(..., description="Count of planets in Argala position")
    virodha_offset: int = Field(..., description="Obstruction house offset (12, 10, 3, 9)")
    virodha_sign: int = Field(..., ge=1, le=12, description="Sign index of Virodha house")
    virodha_sign_name: str = Field(..., description="Sanskrit name of Virodha sign")
    virodha_planets: list[str] = Field(..., description="Planetary bodies causing obstruction")
    virodha_count: int = Field(..., description="Count of planets in Virodha position")
    has_argala: bool = Field(..., description="True if argala_count > 0")
    is_obstructed: bool = Field(..., description="True if virodha_count >= argala_count > 0")
    is_active: bool = Field(..., description="True if argala_count > virodha_count")
    benefic_planets: list[str] = Field(..., description="Natural benefics in Argala position")
    malefic_planets: list[str] = Field(..., description="Natural malefics in Argala position")
    argala_nature: str = Field(..., description="SHUBHA, PAPA, MIXED, or NONE")


class ArgalaEvidenceResponse(BaseModel):
    """Evidence for Argala and Virodhargala acting on a target sign/house (WP7C1, Rule JAI-ASP-02)."""
    target_sign: int = Field(..., ge=1, le=12, description="Target sign evaluated")
    target_sign_name: str = Field(..., description="Sanskrit name of target sign")
    target_sign_name_en: str = Field(..., description="English name of target sign")
    target_house: Optional[int] = Field(None, description="Target house relative to Lagna (if applicable)")
    ketu_mode: str = Field(..., description="STANDARD_ARGALA or REVERSE_KETU_ARGALA")
    net_status: str = Field(..., description="ACTIVE_ARGALA, OBSTRUCTED_ARGALA, or NO_ARGALA")
    active_argalas: list[int] = Field(..., description="List of unobstructed Argala house offsets")
    obstructed_argalas: list[int] = Field(..., description="List of obstructed Argala house offsets")
    supporting_planets: list[str] = Field(..., description="Planets delivering active Argala support")
    obstructing_planets: list[str] = Field(..., description="Planets causing Argala obstruction")
    positions: dict[int, ArgalaPositionEvidence] = Field(..., description="Argala offset (2, 4, 11, 5) -> Position evidence")


class JaiminiFoundationResponse(BaseModel):
    """Complete, deterministic output payload for WP7 foundation layer."""
    karakas: dict[str, CharaKarakaDetail] = Field(..., description="Role -> Chara Karaka detail")
    arudhas: dict[str, ArudhaDetail] = Field(..., description="Arudha name -> Pada detail")
    upapada_lagna: ArudhaDetail = Field(..., description="Explicit Upapada Lagna (UL/A12)")
    rashi_drishti: dict[int, RashiDrishtiDetail] = Field(..., description="Sign 1..12 -> Drishti detail")
    chara_dasha: Optional[CharaDashaCycleResponse] = Field(None, description="Complete Chara Dasha cycle")
    karakamsa: Optional[KarakamsaEvidenceResponse] = Field(None, description="Karakamsa framing evidence (WP7C1)")
    argalas: Optional[dict[int, ArgalaEvidenceResponse]] = Field(None, description="Argala evidence by natal house 1..12 (WP7C1)")
    provenance: JaiminiProvenanceMetadata = Field(..., description="Auditable lineage and metadata")


# ==============================================================================
# 4. Provenance Builder
# ==============================================================================

def build_default_provenance(profile: JaiminiProfileConfig) -> list[DecisionProvenance]:
    """Compile the decision provenance list for DEC-JAI-01 to DEC-JAI-09."""
    return [
        DecisionProvenance(
            decision_id="DEC-JAI-01",
            area="Karakas",
            convention_name="7-Karaka vs 8-Karaka Scheme",
            selected_value=profile.karaka_scheme.value,
            approval_status=ApprovalStatus.PENDING_HUMAN_JYOTISHI,
            source_status=SourceVerificationStatus.EXEGETICAL_DISPUTE,
            is_approved=False,
            notes="BPHS Ch. 29 mentions both. K.N. Rao advocates 7; Rath advocates 8."
        ),
        DecisionProvenance(
            decision_id="DEC-JAI-02",
            area="Karakas",
            convention_name="Rahu Longitude Inversion",
            selected_value="INVERT_RAHU" if profile.rahu_reverse else "DIRECT_LONGITUDE",
            approval_status=ApprovalStatus.PENDING_HUMAN_JYOTISHI,
            source_status=SourceVerificationStatus.CITATION_VERIFIED,
            is_approved=False,
            notes="Traversed arc tau = 30 - deg. Jaimini Sutra 1.1.13-17 retrograde traversal."
        ),
        DecisionProvenance(
            decision_id="DEC-JAI-03",
            area="Karakas",
            convention_name="Planetary Arcdegree Tie-Breaking",
            selected_value=profile.tie_breaker.value,
            approval_status=ApprovalStatus.PENDING_HUMAN_JYOTISHI,
            source_status=SourceVerificationStatus.EXEGETICAL_DISPUTE,
            is_approved=False,
            notes="Deterministic software fallback: Sun > Moon > Mars > Mer > Jup > Ven > Sat > Rahu."
        ),
        DecisionProvenance(
            decision_id="DEC-JAI-04",
            area="Arudhas",
            convention_name="Scorpio & Aquarius Dual Lordship",
            selected_value=profile.dual_lordship.value,
            approval_status=ApprovalStatus.PENDING_HUMAN_JYOTISHI,
            source_status=SourceVerificationStatus.EXEGETICAL_DISPUTE,
            is_approved=False,
            notes="Parāśari single lordship (Mars for Scorpio, Saturn for Aquarius) used for determinism."
        ),
        DecisionProvenance(
            decision_id="DEC-JAI-05",
            area="Timing",
            convention_name="Chara Dasha Progression Direction",
            selected_value=profile.chara_tradition.value,
            approval_status=ApprovalStatus.PENDING_HUMAN_JYOTISHI,
            source_status=SourceVerificationStatus.EXEGETICAL_DISPUTE,
            is_approved=False,
            notes="K.N. Rao tradition provisional default. Chara Dasha engine implemented in WP7B."
        ),
        DecisionProvenance(
            decision_id="DEC-JAI-06",
            area="Timing",
            convention_name="Dasha Duration Clamping",
            selected_value=profile.duration_clamp.value,
            approval_status=ApprovalStatus.PENDING_HUMAN_JYOTISHI,
            source_status=SourceVerificationStatus.SOURCE_VERIFICATION_REQUIRED,
            is_approved=False,
            notes="Clamped to [1, 12] years. Implemented in WP7B."
        ),
        DecisionProvenance(
            decision_id="DEC-JAI-07",
            area="Analysis",
            convention_name="Karakamsa Framing (D1 vs D9)",
            selected_value=profile.karakamsa_mode.value,
            approval_status=ApprovalStatus.PENDING_HUMAN_JYOTISHI,
            source_status=SourceVerificationStatus.EXEGETICAL_DISPUTE,
            is_approved=False,
            notes="Navamsha sign of AK projected in D1 (NAVAMSHA_IN_RASHI) or as D9 Lagna (KARAKAMSA_KUNDALI_D9). Implemented in WP7C1."
        ),
        DecisionProvenance(
            decision_id="DEC-JAI-08",
            area="Aspects",
            convention_name="Ketu Argala Direction",
            selected_value=profile.ketu_argala.value,
            approval_status=ApprovalStatus.PENDING_HUMAN_JYOTISHI,
            source_status=SourceVerificationStatus.SOURCE_VERIFICATION_REQUIRED,
            is_approved=False,
            notes="Standard forward Argala (STANDARD_ARGALA) or reverse for Ketu (REVERSE_KETU_ARGALA). Implemented in WP7C1 under Rule JAI-ASP-02."
        ),
        DecisionProvenance(
            decision_id="DEC-JAI-09",
            area="Arudhas",
            convention_name="Arudha 1st/7th Exception Rules",
            selected_value=profile.arudha_exception.value,
            approval_status=ApprovalStatus.PENDING_HUMAN_JYOTISHI,
            source_status=SourceVerificationStatus.CITATION_VERIFIED,
            is_approved=False,
            notes="BPHS Ch. 30, v. 5-7 Pada-locus rule: raw in 1st -> 10th; raw in 7th -> 4th."
        ),
    ]


# ==============================================================================
# 5. Core Orchestrator Function
# ==============================================================================

def compute_jaimini_foundation(
    planet_positions: dict[str, Any] | list[dict[str, Any]],
    lagna_sign: int | str,
    profile: Optional[JaiminiProfileConfig] = None,
) -> JaiminiFoundationResponse:
    """
    Calculate the foundational Jaimini layer (WP7A).
    
    Args:
        planet_positions: Mapping or list of planet longitudes (Sun..Saturn, Rahu).
        lagna_sign: Natal Lagna sign (1..12 or name).
        profile: Typed lineage profile. If None, default unapproved provisional profile is used.
        
    Returns:
        JaiminiFoundationResponse with deterministic calculations and full provenance.
        
    Raises:
        ValueError: On missing/invalid planets, invalid sign, or NaN/Inf inputs.
    """
    if profile is None:
        profile = JaiminiProfileConfig()

    lagna_idx = parse_sign_index(lagna_sign)

    # 1. Input Validation: Extract & validate planet longitudes
    raw_planet_map: dict[str, float] = {}
    if isinstance(planet_positions, dict):
        for k, v in planet_positions.items():
            if isinstance(v, dict):
                pname = v.get("name") or v.get("planet") or k
                deg = v.get("degree") if "degree" in v else v.get("longitude")
            else:
                pname = k
                deg = v
            if pname and deg is not None:
                deg_f = validate_finite_degree(deg)
                raw_planet_map[str(pname)] = deg_f
    elif isinstance(planet_positions, list):
        for p in planet_positions:
            if not isinstance(p, dict):
                continue
            pname = p.get("name") or p.get("planet")
            deg = p.get("degree") if "degree" in p else p.get("longitude")
            if pname and deg is not None:
                deg_f = validate_finite_degree(deg)
                raw_planet_map[str(pname)] = deg_f
    else:
        raise ValueError("planet_positions must be a dict or list of dicts")

    # 2. Chara Karaka Calculation
    karaka_res = calculate_chara_karakas(
        planets=raw_planet_map,
        scheme=profile.karaka_scheme,
        rahu_reverse=profile.rahu_reverse,
        tie_breaker=profile.tie_breaker,
    )

    karaka_details: dict[str, CharaKarakaDetail] = {}
    for role, kinfo in karaka_res["karakas"].items():
        karaka_details[role] = CharaKarakaDetail(
            role=role,
            planet=kinfo["planet"],
            rank=kinfo["rank"],
            degree_in_sign=kinfo["degree_in_sign"],
            traversed_arc=kinfo["traversed_arc"],
            sign_index=kinfo["sign_index"],
            sign_name=kinfo["sign_name"],
            is_tie_broken=karaka_res["tie_broken"],
        )

    # 3. Determine Lord Placements for Arudha Calculation
    # For WP7A foundation, Parashari single lordship or dual co-lordship fallback
    lord_placements: dict[int, int] = {}
    lord_planets: dict[int, str] = {}
    for h in range(1, 13):
        # House sign in whole-sign system
        h_sign = ((lagna_idx - 1 + (h - 1)) % 12) + 1
        lord_p = PARASHARI_SIGN_LORDS[h_sign]
        lord_planets[h] = lord_p
        
        if lord_p not in raw_planet_map:
            raise ValueError(
                f"Cannot compute Arudha for house {h}: Lord '{lord_p}' missing from planet positions."
            )
            
        lord_deg = raw_planet_map[lord_p]
        lord_sign_idx = (int(lord_deg // 30) % 12) + 1  # 1-indexed sign [1..12]
        lord_placements[h] = lord_sign_idx

    # 4. Arudha Pada Calculations (A1 to A12)
    arudha_details: dict[str, ArudhaDetail] = {}
    exceptions_fired: list[str] = []
    
    for h in range(1, 13):
        pada_calc = calculate_arudha_pada(
            house_num=h,
            lagna_sign=lagna_idx,
            lord_sign=lord_placements[h],
            convention=profile.arudha_exception,
        )
        pname = pada_calc["name"]
        exc_app = pada_calc["exception_applied"]
        exc_type = pada_calc["exception_type"]
        if exc_app:
            exceptions_fired.append(f"{pname}: {exc_type}")

        is_ul = (h == 12)
        rel_from_lagna = ((pada_calc["final_pada"] - lagna_idx) % 12) + 1

        arudha_details[pname] = ArudhaDetail(
            house_num=h,
            name=pname,
            house_sign=pada_calc["house_sign"],
            house_sign_name=pada_calc["house_sign_name"],
            lord_planet=lord_planets[h],
            lord_sign=pada_calc["lord_sign"],
            lord_sign_name=pada_calc["lord_sign_name"],
            raw_pada=pada_calc["raw_pada"],
            final_pada=pada_calc["final_pada"],
            final_sign_name=pada_calc["final_sign_name"],
            exception_applied=exc_app,
            exception_type=exc_type,
            is_upapada=is_ul,
            house_from_lagna=rel_from_lagna,
        )

    upapada_detail = arudha_details["UL"]

    # 5. Rashi Drishti (All 12 Signs)
    drishti_details: dict[int, RashiDrishtiDetail] = {}
    for s in range(1, 13):
        aspected_signs = get_rashi_drishti(s)
        if s in CHARA_SIGNS:
            m_type = "CHARA"
        elif s in STHIRA_SIGNS:
            m_type = "STHIRA"
        else:
            m_type = "DVISVABHAVA"

        drishti_details[s] = RashiDrishtiDetail(
            sign_index=s,
            sign_name=SIGN_NAMES_SK[s],
            sign_type=m_type,
            aspects_signs=aspected_signs,
            aspects_sign_names=[SIGN_NAMES_SK[a] for a in aspected_signs],
        )

    # 6. Provenance Metadata Assembly
    rahu_metric_str = (
        "traversed_arc_30_minus_degree" if profile.rahu_reverse else "direct_sign_degree"
    )
    
    # Identify planets affected by ties if any
    tie_planets: list[str] = []
    if karaka_res["tie_broken"]:
        for item in karaka_res["candidate_rankings"]:
            tie_planets.append(item["name"])

    # 7. Chara Dasha Calculation (WP7B)
    chara_dasha_res = compute_chara_dasha(
        planet_positions=raw_planet_map,
        lagna_sign=lagna_idx,
        profile=profile,
    )

    # 8. Karakamsa Evaluation (WP7C1, DEC-JAI-07)
    karakamsa_res = compute_karakamsa(
        planet_positions=raw_planet_map,
        lagna_sign=lagna_idx,
        profile=profile,
    )

    # 9. Argala Evaluation (WP7C1, Rule JAI-ASP-02, DEC-JAI-08)
    d1_signs = {p: int(deg // 30) % 12 + 1 for p, deg in raw_planet_map.items()}
    argala_raw_houses = evaluate_all_house_argalas(
        lagna_sign=lagna_idx,
        planet_placements=d1_signs,
        ketu_mode=profile.ketu_argala,
    )
    argala_details: dict[int, ArgalaEvidenceResponse] = {}
    for h, h_res in argala_raw_houses.items():
        pos_models: dict[int, ArgalaPositionEvidence] = {}
        for off, p_dat in h_res["positions"].items():
            pos_models[off] = ArgalaPositionEvidence(
                argala_offset=p_dat["argala_offset"],
                argala_sign=p_dat["argala_sign"],
                argala_sign_name=p_dat["argala_sign_name"],
                argala_planets=p_dat["argala_planets"],
                argala_count=p_dat["argala_count"],
                virodha_offset=p_dat["virodha_offset"],
                virodha_sign=p_dat["virodha_sign"],
                virodha_sign_name=p_dat["virodha_sign_name"],
                virodha_planets=p_dat["virodha_planets"],
                virodha_count=p_dat["virodha_count"],
                has_argala=p_dat["has_argala"],
                is_obstructed=p_dat["is_obstructed"],
                is_active=p_dat["is_active"],
                benefic_planets=p_dat["benefic_planets"],
                malefic_planets=p_dat["malefic_planets"],
                argala_nature=p_dat["argala_nature"],
            )
        argala_details[h] = ArgalaEvidenceResponse(
            target_sign=h_res["target_sign"],
            target_sign_name=h_res["target_sign_name"],
            target_sign_name_en=h_res["target_sign_name_en"],
            target_house=h_res["target_house"],
            ketu_mode=h_res["ketu_mode"],
            net_status=h_res["net_status"],
            active_argalas=h_res["active_argalas"],
            obstructed_argalas=h_res["obstructed_argalas"],
            supporting_planets=h_res["supporting_planets"],
            obstructing_planets=h_res["obstructing_planets"],
            positions=pos_models,
        )

    provenance = JaiminiProvenanceMetadata(
        profile_id=profile.profile_id,
        profile_approval_status=profile.approval_status.value,
        profile_is_approved=profile.is_approved,
        formula_version="WP7C2-JAIMINI-FOUNDATION-v1.0",
        decisions=build_default_provenance(profile),
        tie_breaker_invoked=karaka_res["tie_broken"],
        tie_broken_planets=tie_planets,
        tie_break_notes=karaka_res["tie_break_details"],
        exceptions_invoked=exceptions_fired,
        rahu_traversal_metric_applied=rahu_metric_str,
    )

    return JaiminiFoundationResponse(
        karakas=karaka_details,
        arudhas=arudha_details,
        upapada_lagna=upapada_detail,
        rashi_drishti=drishti_details,
        chara_dasha=chara_dasha_res,
        karakamsa=karakamsa_res,
        argalas=argala_details,
        provenance=provenance,
    )


def compute_chara_dasha(
    planet_positions: dict[str, Any] | list[dict[str, Any]],
    lagna_sign: int | str,
    profile: Optional[JaiminiProfileConfig] = None,
) -> CharaDashaCycleResponse:
    """
    Calculate the complete 12-sign Chara Dasha cycle and 144 Antardashas (WP7B).
    
    Args:
        planet_positions: Planetary longitudes mapping or list of dicts.
        lagna_sign: Natal Lagna sign (1..12 or name).
        profile: Typed lineage profile config.
        
    Returns:
        CharaDashaCycleResponse with 12 Mahadashas and 144 Antardashas.
    """
    if profile is None:
        profile = JaiminiProfileConfig()
        
    lagna_idx = parse_sign_index(lagna_sign)
    
    # 1. Normalize planet positions
    raw_planet_map: dict[str, float] = {}
    if isinstance(planet_positions, dict):
        for k, v in planet_positions.items():
            if isinstance(v, dict):
                pname = v.get("name") or v.get("planet") or k
                deg = v.get("degree") if "degree" in v else v.get("longitude")
            else:
                pname = k
                deg = v
            if pname and deg is not None:
                deg_f = validate_finite_degree(deg)
                raw_planet_map[str(pname)] = deg_f
    elif isinstance(planet_positions, list):
        for p in planet_positions:
            if not isinstance(p, dict):
                continue
            pname = p.get("name") or p.get("planet")
            deg = p.get("degree") if "degree" in p else p.get("longitude")
            if pname and deg is not None:
                deg_f = validate_finite_degree(deg)
                raw_planet_map[str(pname)] = deg_f
    else:
        raise ValueError("planet_positions must be a dict or list of dicts")

    # 2. Determine sign lord placements for all 12 signs
    sign_lord_placements: dict[int, int] = {}
    for s in range(1, 13):
        lord_p = PARASHARI_SIGN_LORDS[s]
        if lord_p not in raw_planet_map:
            raise ValueError(
                f"Cannot compute Chara Dasha for sign {s}: Lord '{lord_p}' missing from planet positions."
            )
        lord_deg = raw_planet_map[lord_p]
        lord_sign_idx = (int(lord_deg // 30) % 12) + 1  # 1-indexed sign [1..12]
        sign_lord_placements[s] = lord_sign_idx

    # 3. Determine start sign
    if profile.start_sign_convention == "SEVENTH_HOUSE":
        start_sign = ((lagna_idx - 1 + 6) % 12) + 1
    else:
        start_sign = lagna_idx

    # 4. Execute pure cycle calculation
    cycle_raw = calculate_chara_dasha_cycle(
        start_sign=start_sign,
        lord_placements=sign_lord_placements,
        tradition=profile.chara_tradition,
        clamp_mode=profile.duration_clamp,
        counting_convention=profile.counting_convention,
        antardasha_convention=profile.antardasha_convention,
        lagna_sign=lagna_idx,
    )

    # 5. Build structured Pydantic models
    mahadashas: list[MahadashaDetail] = []
    for m in cycle_raw["mahadashas"]:
        cdet = m["calculation_details"]
        calc_detail = MahadashaCalculationDetail(
            sign=cdet["sign"],
            sign_name=cdet["sign_name"],
            lord_planet=cdet["lord_planet"],
            lord_sign=cdet["lord_sign"],
            lord_sign_name=cdet["lord_sign_name"],
            is_forward_counting=cdet["is_forward_counting"],
            displacement_count=cdet["displacement_count"],
            is_own_sign=cdet["is_own_sign"],
            base_years=cdet["base_years"],
            dignity=cdet["dignity"],
            dignity_modifier=cdet["dignity_modifier"],
            raw_years=cdet["raw_years"],
            final_years=cdet["final_years"],
            clamp_mode=cdet["clamp_mode"],
            is_clamped=cdet["is_clamped"],
            rule_note=cdet["rule_note"],
        )

        sub_list = [
            AntardashaDetail(
                antardasha_index=sp["antardasha_index"],
                sign=sp["sign"],
                sign_name=sp["sign_name"],
                duration_years_fractional=sp["duration_years_fractional"],
                duration_months=sp["duration_months"],
                parent_mahadasha_sign=sp["parent_mahadasha_sign"],
            )
            for sp in m["antardashas"]
        ]

        mahadashas.append(
            MahadashaDetail(
                order_index=m["order_index"],
                sign=m["sign"],
                sign_name=m["sign_name"],
                sign_name_en=m["sign_name_en"],
                duration_years=m["duration_years"],
                elapsed_start_years=m["elapsed_start_years"],
                elapsed_end_years=m["elapsed_end_years"],
                calculation_details=calc_detail,
                antardashas=sub_list,
            )
        )

    return CharaDashaCycleResponse(
        start_sign=cycle_raw["start_sign"],
        start_sign_name=cycle_raw["start_sign_name"],
        lagna_sign=cycle_raw["lagna_sign"],
        lagna_sign_name=cycle_raw["lagna_sign_name"],
        tradition=cycle_raw["tradition"],
        direction_description=cycle_raw["direction_description"],
        is_progression_forward=cycle_raw["is_progression_forward"],
        clamp_mode=cycle_raw["clamp_mode"],
        counting_convention=cycle_raw["counting_convention"],
        antardasha_convention=cycle_raw["antardasha_convention"],
        total_cycle_years=cycle_raw["total_cycle_years"],
        mahadasha_count=cycle_raw["mahadasha_count"],
        total_antardasha_count=cycle_raw["total_antardasha_count"],
        mahadashas=mahadashas,
    )


def compute_karakamsa(
    planet_positions: dict[str, Any] | list[dict[str, Any]],
    lagna_sign: int | str,
    profile: Optional[JaiminiProfileConfig] = None,
    d9_sign_placements: Optional[dict[str, int | str]] = None,
) -> KarakamsaEvidenceResponse:
    """
    Calculate Karakamsa framing evidence deterministically (WP7C1, DEC-JAI-07).
    
    Args:
        planet_positions: Planetary longitudes mapping or list of dicts.
        lagna_sign: Natal Lagna sign (1..12 or name).
        profile: Typed lineage profile config (controls karaka_scheme & karakamsa_mode).
        d9_sign_placements: Optional explicit D9 sign placements for planets.
        
    Returns:
        KarakamsaEvidenceResponse with D1 or D9 house mapping and occupants.
    """
    if profile is None:
        profile = JaiminiProfileConfig()

    raw = evaluate_karakamsa(
        planet_positions=planet_positions,
        lagna_sign=lagna_sign,
        karaka_scheme=profile.karaka_scheme,
        framing_mode=profile.karakamsa_mode,
        d9_sign_placements=d9_sign_placements,
    )
    return KarakamsaEvidenceResponse(**raw)


def compute_argala(
    target_sign: int | str,
    planet_placements: dict[str, int | str],
    ketu_mode: KetuArgalaEnum = KetuArgalaEnum.STANDARD_ARGALA,
    target_house: Optional[int] = None,
) -> ArgalaEvidenceResponse:
    """
    Calculate Jaimini Argala and Virodhargala evidence for a sign or house (WP7C1, Rule JAI-ASP-02).
    
    Args:
        target_sign: Target zodiac sign (1..12 or name).
        planet_placements: Mapping of planet name to occupied sign (1..12 or name).
        ketu_mode: STANDARD_ARGALA or REVERSE_KETU_ARGALA.
        target_house: Optional house number relative to Lagna (1..12).
        
    Returns:
        ArgalaEvidenceResponse detailing active and obstructed interventions.
    """
    k_mode = (
        ketu_mode
        if isinstance(ketu_mode, KetuArgalaConvention)
        else KetuArgalaConvention(ketu_mode.value if isinstance(ketu_mode, Enum) else str(ketu_mode))
    )
    raw = evaluate_argala(
        target_sign=target_sign,
        planet_placements=planet_placements,
        ketu_mode=k_mode,
        target_house=target_house,
    )
    pos_models = {
        off: ArgalaPositionEvidence(**p_dat)
        for off, p_dat in raw["positions"].items()
    }
    raw_copy = dict(raw)
    raw_copy["positions"] = pos_models
    return ArgalaEvidenceResponse(**raw_copy)


def synthesize_cross_system_timing(
    vimshottari_attributions: list[SystemTimingAttribution],
    chara_attributions: list[SystemTimingAttribution],
    domain: str = "general",
    profile_id: str = "PROVISIONAL_DUAL_SYSTEM_DEFAULT",
    boundary: IntervalBoundaryConvention = IntervalBoundaryConvention.HALF_OPEN_INCLUSIVE_EXCLUSIVE,
) -> CrossSystemSynthesisResponse:
    """
    Synthesize timing evidence across Vimshottari and Chara Dasha under Rule JAI-DSH-07.
    
    Guarantees:
    1. Disjoint Attribution: Vimshottari and Chara Dasha items are preserved separately.
    2. Zero Date Averaging: Original boundaries are never averaged or merged into synthetic event dates.
    3. Qualitative Convergence: Agreement is reported as CONVERGENT, DIVERGENT, or INDEPENDENT; never a probability.
    
    Args:
        vimshottari_attributions: List of isolated Parāśari Vimshottari evidence records.
        chara_attributions: List of isolated Jaimini Chara Dasha evidence records.
        domain: Target life domain under evaluation.
        profile_id: Synthesis configuration profile identifier.
        boundary: Mathematical interval boundary convention (default: HALF_OPEN_INCLUSIVE_EXCLUSIVE).
        
    Returns:
        CrossSystemSynthesisResponse containing pairwise comparisons and disjoint attributions.
    """
    return synthesize_timing_attributions(
        vimshottari_attributions=vimshottari_attributions,
        chara_attributions=chara_attributions,
        domain=domain,
        profile_id=profile_id,
        boundary=boundary,
    )


