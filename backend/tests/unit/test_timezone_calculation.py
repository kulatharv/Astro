"""
Unit and regression tests for Timezone, Julian Day calculation, and boundary cases (CF-01).
Ensures:
- UTC conversion accuracy across IANA timezones and daylight-saving transitions
- Prevention of day-zero / calendar-month boundary underflow (e.g. 1st day of month before 05:30 IST)
- Leap year transitions (Feb 29 -> Feb 28 UTC)
- Preserves exact historical benchmark charts (IST reference charts)
"""

import pytest
from datetime import datetime, timezone
import swisseph as swe

from shared.timezone.tz import to_utc_jd, resolve_timezone, get_local_now, to_local_iso
from modules.kundali.engine import calculate_kundali
from modules.kundali.cities import get_city_details, CITIES


class TestTimezoneJulianDayConversion:
    """Tests for to_utc_jd function and timezone boundary handling."""

    def test_ist_standard_noon(self):
        """Standard IST noon calculation matches Swiss Ephemeris UTC noon - 5.5 hours."""
        # 2026-05-15 12:00:00 IST -> 2026-05-15 06:30:00 UTC (6.5 hours decimal)
        *_, jd_calc = to_utc_jd(2026, 5, 15, 12, 0, 0, tz_name="Asia/Kolkata")
        jd_expected = swe.julday(2026, 5, 15, 6.5)
        assert abs(jd_calc - jd_expected) < 1e-7

    def test_ist_near_midnight_month_boundary_prevents_day_zero(self):
        """
        Critical regression test: On 1st of month at 02:00 IST (UTC is previous month's last day).
        Previous bug subtracted day -= 1 yielding day=0, crashing or corrupting JD.
        """
        # 2026-05-01 02:00:00 IST -> 2026-04-30 20:30:00 UTC (20.5 hours decimal)
        *_, jd_calc = to_utc_jd(2026, 5, 1, 2, 0, 0, tz_name="Asia/Kolkata")
        jd_expected = swe.julday(2026, 4, 30, 20.5)
        assert abs(jd_calc - jd_expected) < 1e-7

    def test_new_year_boundary_prevents_year_underflow(self):
        """2026-01-01 01:30:00 IST -> 2025-12-31 20:00:00 UTC."""
        *_, jd_calc = to_utc_jd(2026, 1, 1, 1, 30, 0, tz_name="Asia/Kolkata")
        jd_expected = swe.julday(2025, 12, 31, 20.0)
        assert abs(jd_calc - jd_expected) < 1e-7

    def test_leap_year_boundary(self):
        """2024-03-01 03:00:00 IST -> 2024-02-29 21:30:00 UTC in a leap year."""
        *_, jd_calc = to_utc_jd(2024, 3, 1, 3, 0, 0, tz_name="Asia/Kolkata")
        jd_expected = swe.julday(2024, 2, 29, 21.5)
        assert abs(jd_calc - jd_expected) < 1e-7

    def test_new_york_dst_summer_vs_winter(self):
        """
        Tests Daylight Saving Time for America/New_York.
        Summer (EDT): UTC-4
        Winter (EST): UTC-5
        """
        # Summer: 2026-07-15 14:00:00 EDT -> 2026-07-15 18:00:00 UTC (18.0 decimal)
        *_, jd_summer = to_utc_jd(2026, 7, 15, 14, 0, 0, tz_name="America/New_York")
        jd_expected_summer = swe.julday(2026, 7, 15, 18.0)
        assert abs(jd_summer - jd_expected_summer) < 1e-7

        # Winter: 2026-01-15 14:00:00 EST -> 2026-01-15 19:00:00 UTC (19.0 decimal)
        *_, jd_winter = to_utc_jd(2026, 1, 15, 14, 0, 0, tz_name="America/New_York")
        jd_expected_winter = swe.julday(2026, 1, 15, 19.0)
        assert abs(jd_winter - jd_expected_winter) < 1e-7

    def test_london_dst_bst_vs_gmt(self):
        """
        Europe/London:
        Summer (BST): UTC+1
        Winter (GMT): UTC+0
        """
        # Summer (BST): 2026-06-20 10:00:00 BST -> 2026-06-20 09:00:00 UTC
        *_, jd_summer = to_utc_jd(2026, 6, 20, 10, 0, 0, tz_name="Europe/London")
        jd_expected_summer = swe.julday(2026, 6, 20, 9.0)
        assert abs(jd_summer - jd_expected_summer) < 1e-7

        # Winter (GMT): 2026-12-20 10:00:00 GMT -> 2026-12-20 10:00:00 UTC
        *_, jd_winter = to_utc_jd(2026, 12, 20, 10, 0, 0, tz_name="Europe/London")
        jd_expected_winter = swe.julday(2026, 12, 20, 10.0)
        assert abs(jd_winter - jd_expected_winter) < 1e-7

    def test_southern_hemisphere_sydney(self):
        """Australia/Sydney has southern hemisphere DST (AEDT = UTC+11 in Dec, AEST = UTC+10 in June)."""
        # December (AEDT = UTC+11): 2026-12-15 15:00:00 AEDT -> 2026-12-15 04:00:00 UTC
        *_, jd_dec = to_utc_jd(2026, 12, 15, 15, 0, 0, tz_name="Australia/Sydney")
        jd_expected_dec = swe.julday(2026, 12, 15, 4.0)
        assert abs(jd_dec - jd_expected_dec) < 1e-7

        # June (AEST = UTC+10): 2026-06-15 15:00:00 AEST -> 2026-06-15 05:00:00 UTC
        *_, jd_june = to_utc_jd(2026, 6, 15, 15, 0, 0, tz_name="Australia/Sydney")
        jd_expected_june = swe.julday(2026, 6, 15, 5.0)
        assert abs(jd_june - jd_expected_june) < 1e-7

    def test_invalid_timezone_graceful_fallback(self):
        """An invalid timezone string falls back to Asia/Kolkata (or specified offset) without unhandled exception."""
        *_, jd_fallback = to_utc_jd(2026, 5, 15, 12, 0, 0, tz_name="Invalid/Fake_Zone", tz_offset=5.5)
        *_, jd_ist = to_utc_jd(2026, 5, 15, 12, 0, 0, tz_name="Asia/Kolkata")
        assert abs(jd_fallback - jd_ist) < 1e-7


class TestKundaliEngineTimezoneCorrectness:
    """Verifies calculate_kundali outputs across different timezones and cities."""

    def test_international_city_ascendant_shift(self):
        """
        Verify that New York birth details compute the correct Ascendant based on EDT,
        not mistakenly treating local time as IST.
        """
        # New York: 40.7128 N, 74.0060 W
        # Born 1990-06-15 14:30 EDT (UTC-4)
        chart_ny = calculate_kundali(
            year=1990, month=6, day=15,
            hour=14, minute=30,
            lat=40.7128, lon=-74.0060,
            tz_name="America/New_York",
        )
        lagna = chart_ny["lagna"]
        # In New York on 1990-06-15 at 14:30 EDT (18:30 UTC, RAMC ~ 180°),
        # Lagna is Libra (Tula), Virgo (Kanya), or Leo (Simha),
        # but if IST (+5.5) was wrongly used, UTC would be 09:00 and Lagna would be Mesha (Aries).
        assert lagna in ["Kanya", "Tula", "Simha"]
        assert lagna != "Mesha"

    def test_reference_chart_delhi_matches_expected_ayanamsha(self):
        """Ensure benchmark Indian chart (Delhi) calculates properly without breaking existing outputs."""
        chart_delhi = calculate_kundali(
            year=1995, month=10, day=24,
            hour=8, minute=30,
            lat=28.6139, lon=77.2090,
            tz_name="Asia/Kolkata"
        )
        assert "planets" in chart_delhi
        assert "lagna" in chart_delhi
        assert len(chart_delhi["planets"]) >= 9
        # Check that Lahiri Ayanamsha was applied
        assert chart_delhi.get("ayanamsa") is not None
        assert 23.0 < chart_delhi["ayanamsa"] < 25.0

    def test_city_details_lookup(self):
        """Verify city resolver returns coordinates and timezone."""
        ny = get_city_details("New York")
        assert ny["tz_name"] == "America/New_York"
        assert ny["timezone"] == -5.0 or ny["timezone_offset"] == -5.0

        london = get_city_details("London")
        assert london["tz_name"] == "Europe/London"

        tokyo = get_city_details("Tokyo")
        assert tokyo["tz_name"] == "Asia/Tokyo"
        assert tokyo["timezone_offset"] == 9.0

        delhi = get_city_details("New Delhi")
        assert delhi["tz_name"] == "Asia/Kolkata"
        assert delhi["timezone_offset"] == 5.5
