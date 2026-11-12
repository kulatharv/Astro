"""
Shared Pure Vedic Astrology Calculation Library (shared.veda).
Stateless, pure mathematical and astrological calculations — zero DB, zero Redis, zero side effects.
"""

from .zodiac import SIGNS_SK, SIGNS_EN, SIGN_LORDS, degree_to_sign, to_dms
from .nakshatra import NAKSHATRAS, NAKSHATRA_LORDS, calculate_nakshatra, get_nakshatra_lord
from .aspects import calculate_vedic_aspects
from .strength import EXALTATION, DEBILITATION, OWN_SIGNS, FRIENDLY_SIGNS, planet_strength_label, calculate_weighted_strength
from .doshas import (
    evaluate_mangal_dosha, evaluate_mangal_dosha_multiframe, check_mangal_cancellations,
    evaluate_pitru_dosha, calculate_sade_sati, calculate_kaal_sarp,
    evaluate_grahan_dosha, evaluate_gandmool_dosha, calculate_doshas,
)
from .yogas import calculate_yogas, calculate_yogas_v2, detect_advanced_yogas
from .yoga_catalog import YogaRule, CATALOG, evaluate_yoga_catalog, evaluate_yoga_rule
from .dignity import PLANET_FRIENDS, MOOLATRIKONA, PLANET_ENEMIES, get_naisargika_dignity, get_positional_strength
from .combustion import (
    COMBUSTION_LIMITS, COMBUSTION_RANGES, CombustionStatus,
    CombustionResult, check_combustion, is_combust,
    calculate_angular_separation, extract_longitude
)
from .neech_bhanga import is_neech_bhanga
from .constants import PUBLIC_PATH_PREFIXES, USER_ROLE, ADMIN_ROLE, ZODIAC_SIGNS, RASHI_NAMES

# WP1 — Shadbala, Bhava Bala, Avasthas
from .shadbala import (
    ShadbalaResult,
    DEEP_EXALTATION_DEGREE, MOOLATRIKONA_SPAN, DIG_BALA_HOUSE, NAISARGIKA_BALA, MINIMUM_RUPAS,
    compute_sthana_bala, compute_dig_bala, compute_kala_bala,
    compute_chesta_bala, compute_naisargika_bala, compute_drik_bala,
    shadbala, shadbala_summary,
)
from .bhavabala import (
    BhavaBalaResult, BHAVA_DIG_BALA_MAX, MINIMUM_BHAVA_RUPAS,
    bhava_bala, bhava_bala_summary,
)
from .avasthas import (
    get_baladi_avastha, baladi_strength_multiplier,
    get_jagradi_avastha, jagradi_strength_multiplier,
    get_lajjitadi_avasthas, evaluate_avasthas,
    BALADI_STATES, BALADI_STRENGTH, JAGRADI_STRENGTH, LAJJITADI_DEFS,
)

# WP2 — Functional Lordship Matrix
from .lordship import (
    LagnaMatrix, PlanetRoleInfo, ALL_LAGNA_MATRICES,
    build_lagna_matrix, get_lagna_matrix,
    get_house_lord, get_planet_roles,
    is_functional_benefic, is_functional_malefic,
    is_yogakaraka, is_badhaka_lord, matrix_to_dict,
)

# WP5A — Career Domain Rule Pack
from .career import (
    CareerRule, CAREER_RULES_CATALOG, evaluate_career_rules,
    calculate_amatyakaraka, calculate_dashamsha_d10,
)

# WP5B — Marriage & Relationship Domain Rule Pack
from .marriage import (
    MarriageRule, MARRIAGE_RULES_CATALOG, evaluate_marriage_rules,
    calculate_d9_navamsa_sign,
)

# WP5C — Wealth & Resources Domain Rule Pack
from .wealth import (
    WealthRule, WEALTH_RULES_CATALOG, evaluate_wealth_rules,
)

# WP5D — Health & Wellbeing Domain Rule Pack
from .health import (
    HealthRule, HEALTH_RULES_CATALOG, evaluate_health_rules,
)

# WP5E — Education & Learning Domain Rule Pack
from .education import (
    EducationRule, EDUCATION_RULES_CATALOG, evaluate_education_rules,
    calculate_siddhamsa_d24,
)

# WP5F — Children & Progeny Domain Rule Pack
from .progeny import (
    ProgenyRule, PROGENY_RULES_CATALOG, evaluate_progeny_rules,
    calculate_saptamsha_d7,
)

# WP5G — Property & Residence Domain Rule Pack
from .property import (
    PropertyRule, PROPERTY_RULES_CATALOG, evaluate_property_rules,
    calculate_chaturthamsa_d4, build_d4_chart,
)

# WP6 — Timing Engine, Dasha–Transit Fusion & Prediction Synthesis
from .ashtakavarga import (
    compute_bav, compute_all_bav, compute_sav, compute_house_sav,
    evaluate_ashtakavarga_transit, SAV_TOTAL_INVARIANT,
)
from .vedha import (
    check_transit_vedha, GOCHARA_BENEFIC_HOUSES, VEDHA_PAIRS, VEDHA_EXEMPT_PAIRS,
)
from .timing_rules import (
    TimingRule, TIMING_RULES_CATALOG, evaluate_timing_rules,
    TIMING_SAFETY_DISCLAIMER,
)

# WP7 — Jaimini Astrology Layer (Foundational Primitives)
from .jaimini_rules import (
    KarakaScheme, ArudhaExceptionMode, RashiDrishtiMode,
    SevenKarakaRole, EightKarakaRole,
    calculate_rahu_traversal, calculate_chara_karakas,
    calculate_arudha_pada, calculate_upapada_lagna,
    get_rashi_drishti_aspects,
)
from .jaimini_dasha import (
    CharaProgressionTradition, DurationClampMode,
    SignCountingConvention, AntardashaOrderConvention,
    get_chara_dasha_progression, calculate_mahadasha_duration,
    calculate_antardashas, calculate_chara_dasha_cycle,
)
from .jaimini_evidence import (
    KarakamsaFramingMode, KetuArgalaConvention,
    calculate_navamsha_sign, evaluate_karakamsa,
    evaluate_argala, evaluate_all_house_argalas,
    ARGALA_PAIRS, NATURAL_BENEFICS, NATURAL_MALEFICS,
)
from .jaimini_synthesis import (
    TimingSystemEnum, IntervalBoundaryConvention,
    TemporalRepresentationUnit, YearConventionEnum, OverlapType, ConvergenceStatus,
    TimingInterval, SystemTimingAttribution,
    CrossSystemComparisonRecord, CrossSystemSynthesisResponse,
    compare_numeric_intervals, compare_calendar_intervals,
    convert_elapsed_years_to_calendar_date, convert_calendar_date_to_elapsed_years,
    convert_interval_unit,
    evaluate_convergence_status, synthesize_timing_attributions,
)

__all__ = [
    # Zodiac & Nakshatra
    "SIGNS_SK", "SIGNS_EN", "SIGN_LORDS", "degree_to_sign", "to_dms",
    "NAKSHATRAS", "NAKSHATRA_LORDS", "calculate_nakshatra", "get_nakshatra_lord",
    # Aspects
    "calculate_vedic_aspects",
    # Strength / Dignity (pre-WP1)
    "EXALTATION", "DEBILITATION", "OWN_SIGNS", "FRIENDLY_SIGNS",
    "planet_strength_label", "calculate_weighted_strength",
    # Doshas & Yogas
    "evaluate_mangal_dosha", "evaluate_mangal_dosha_multiframe", "check_mangal_cancellations",
    "evaluate_pitru_dosha", "calculate_sade_sati", "calculate_kaal_sarp",
    "evaluate_grahan_dosha", "evaluate_gandmool_dosha", "calculate_doshas",
    "calculate_yogas", "calculate_yogas_v2", "detect_advanced_yogas",
    "YogaRule", "CATALOG", "evaluate_yoga_catalog", "evaluate_yoga_rule",
    # Dignity
    "PLANET_FRIENDS", "MOOLATRIKONA", "PLANET_ENEMIES", "get_naisargika_dignity", "get_positional_strength",
    # Combustion & Neecha Bhanga
    "COMBUSTION_LIMITS", "COMBUSTION_RANGES", "CombustionStatus", "CombustionResult",
    "check_combustion", "is_combust", "calculate_angular_separation", "extract_longitude",
    "is_neech_bhanga",
    # Constants
    "PUBLIC_PATH_PREFIXES", "USER_ROLE", "ADMIN_ROLE", "ZODIAC_SIGNS", "RASHI_NAMES",
    # WP1 — Shadbala
    "ShadbalaResult",
    "DEEP_EXALTATION_DEGREE", "MOOLATRIKONA_SPAN", "DIG_BALA_HOUSE", "NAISARGIKA_BALA", "MINIMUM_RUPAS",
    "compute_sthana_bala", "compute_dig_bala", "compute_kala_bala",
    "compute_chesta_bala", "compute_naisargika_bala", "compute_drik_bala",
    "shadbala", "shadbala_summary",
    # WP1 — Bhava Bala
    "BhavaBalaResult", "BHAVA_DIG_BALA_MAX", "MINIMUM_BHAVA_RUPAS",
    "bhava_bala", "bhava_bala_summary",
    # WP1 — Avasthas
    "get_baladi_avastha", "baladi_strength_multiplier",
    "get_jagradi_avastha", "jagradi_strength_multiplier",
    "get_lajjitadi_avasthas", "evaluate_avasthas",
    "BALADI_STATES", "BALADI_STRENGTH", "JAGRADI_STRENGTH", "LAJJITADI_DEFS",
    # WP2 — Lordship Matrix
    "LagnaMatrix", "PlanetRoleInfo", "ALL_LAGNA_MATRICES",
    "build_lagna_matrix", "get_lagna_matrix",
    "get_house_lord", "get_planet_roles",
    "is_functional_benefic", "is_functional_malefic",
    "is_yogakaraka", "is_badhaka_lord", "matrix_to_dict",
    # WP5A — Career Domain Rule Pack
    "CareerRule", "CAREER_RULES_CATALOG", "evaluate_career_rules",
    "calculate_amatyakaraka", "calculate_dashamsha_d10",
    # WP5B — Marriage & Relationship Domain Rule Pack
    "MarriageRule", "MARRIAGE_RULES_CATALOG", "evaluate_marriage_rules",
    "calculate_d9_navamsa_sign",
    # WP5C — Wealth & Resources Domain Rule Pack
    "WealthRule", "WEALTH_RULES_CATALOG", "evaluate_wealth_rules",
    # WP5D — Health & Wellbeing Domain Rule Pack
    "HealthRule", "HEALTH_RULES_CATALOG", "evaluate_health_rules",
    # WP5E — Education & Learning Domain Rule Pack
    "EducationRule", "EDUCATION_RULES_CATALOG", "evaluate_education_rules",
    "calculate_siddhamsa_d24",
    # WP5F — Children & Progeny Domain Rule Pack
    "ProgenyRule", "PROGENY_RULES_CATALOG", "evaluate_progeny_rules",
    "calculate_saptamsha_d7",
    # WP5G — Property & Residence Domain Rule Pack
    "PropertyRule", "PROPERTY_RULES_CATALOG", "evaluate_property_rules",
    "calculate_chaturthamsa_d4", "build_d4_chart",
    # WP6 — Timing Engine, Dasha–Transit Fusion & Prediction Synthesis
    "compute_bav", "compute_all_bav", "compute_sav", "compute_house_sav",
    "evaluate_ashtakavarga_transit", "SAV_TOTAL_INVARIANT",
    "check_transit_vedha", "GOCHARA_BENEFIC_HOUSES", "VEDHA_PAIRS", "VEDHA_EXEMPT_PAIRS",
    "TimingRule", "TIMING_RULES_CATALOG", "evaluate_timing_rules",
    "TIMING_SAFETY_DISCLAIMER",
    # WP7 — Jaimini Astrology Layer (Foundational Primitives)
    "KarakaScheme", "ArudhaExceptionMode", "RashiDrishtiMode",
    "SevenKarakaRole", "EightKarakaRole",
    "calculate_rahu_traversal", "calculate_chara_karakas",
    "calculate_arudha_pada", "calculate_upapada_lagna",
    "get_rashi_drishti_aspects",
    # WP7B — Chara Dasha Engine Foundation
    "CharaProgressionTradition", "DurationClampMode",
    "SignCountingConvention", "AntardashaOrderConvention",
    "get_chara_dasha_progression", "calculate_mahadasha_duration",
    "calculate_antardashas", "calculate_chara_dasha_cycle",
    # WP7C1 — Jaimini Evidence Primitives (Karakamsa & Argala)
    "KarakamsaFramingMode", "KetuArgalaConvention",
    "calculate_navamsha_sign", "evaluate_karakamsa",
    "evaluate_argala", "evaluate_all_house_argalas",
    "ARGALA_PAIRS", "NATURAL_BENEFICS", "NATURAL_MALEFICS",
    # WP7C2 — Cross-System Timing Attribution & Disjoint Synthesis
    "TimingSystemEnum", "IntervalBoundaryConvention",
    "TemporalRepresentationUnit", "YearConventionEnum", "OverlapType", "ConvergenceStatus",
    "TimingInterval", "SystemTimingAttribution",
    "CrossSystemComparisonRecord", "CrossSystemSynthesisResponse",
    "compare_numeric_intervals", "compare_calendar_intervals",
    "convert_elapsed_years_to_calendar_date", "convert_calendar_date_to_elapsed_years",
    "convert_interval_unit",
    "evaluate_convergence_status", "synthesize_timing_attributions",
]



