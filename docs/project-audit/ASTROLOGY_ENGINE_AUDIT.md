# Astrology Engine Technical Audit

**Project:** AstroLogic AI  
**Scope:** In-depth technical review of calculation algorithms, ephemeris bindings, astronomical accuracy, timezone conversions, and known defects.

---

## 1. Ephemeris Configuration & Runtime Execution Mode

### Swiss Ephemeris Binding
- **Library:** `pyswisseph>=2.10.3.2` (C-extension wrapping Astrodienst Swiss Ephemeris).
- **Ephemeris Path Configuration:**
  - [`backend/shared/ephemeris/wrapper.py:6`](file:///c:/Desktop/astro_may_res%20(2)/astro-platform/backend/shared/ephemeris/wrapper.py#L6): `swe.set_ephe_path('.')`
  - [`backend/modules/prediction/scoring.py:15`](file:///c:/Desktop/astro_may_res%20(2)/astro-platform/backend/modules/prediction/scoring.py#L15): `swe.set_ephe_path('.')`
- **File Presence Audit:**
  - A recursive disk scan across the entire project structure reveals **zero (0) `.se1` ephemeris files**.
- **Runtime Mode Impact:**
  - When Swiss Ephemeris cannot locate `.se1` data files in the specified path, it silently falls back to the internal **Moshier semi-analytical model**.
  - *Precision Consequence:* While Moshier precision is sufficient for standard Vedic astrology sign/nakshatra placements (typically within a few arcseconds for modern epochs), it does not provide true sub-arcsecond NASA JPL DE431 numerical accuracy and exhibits slight drift for ancient or far-future epochs.

---

## 2. Astronomical Flags & Calculation Calls

### Flag Combinations
1. **Planetary Longitudes & Speeds:**
   - [`backend/modules/kundali/planets.py:28`](file:///c:/Desktop/astro_may_res%20(2)/astro-platform/backend/modules/kundali/planets.py#L28):
     ```python
     flags = swe.FLG_SIDEREAL | swe.FLG_SPEED
     data = swe.calc_ut(jd, code, flags)
     ```
   - Correctly passes `FLG_SPEED` to derive daily motion for retrograde detection (`speed < 0`).
2. **House Cusps and Ascendant:**
   - [`backend/modules/kundali/houses.py:13-20`](file:///c:/Desktop/astro_may_res%20(2)/astro-platform/backend/modules/kundali/houses.py#L13-L20):
     ```python
     flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
     cusps, ascmc = swe.houses_ex(jd, latitude, longitude, b'W', flags)
     ```
   - Uses `b'W'` for Whole Sign house cusps.
3. **Bhava Chalit House Cusps:**
   - [`backend/modules/kundali/houses.py:44-50`](file:///c:/Desktop/astro_may_res%20(2)/astro-platform/backend/modules/kundali/houses.py#L44-L50):
     ```python
     flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
     cusps, ascmc = swe.houses_ex(jd, latitude, longitude, b'P', flags)
     ```
   - *Architectural Discrepancy:* Uses **Placidus (`b'P'`)**, whereas classical North/South Indian astrology treatises and the original LLD specify **Sripati (`b'S'`)** for Bhava Chalit.

---

## 3. Timezone, Wall-Clock, and UTC Conversion Audit

### Core Defects in Timezone Conversion

#### Defect A: Hardcoded IST Offset in Master Engine
In [`backend/modules/kundali/engine.py:102-108`](file:///c:/Desktop/astro_may_res%20(2)/astro-platform/backend/modules/kundali/engine.py#L102-L108):
```python
ist_offset = 5.5
utc_hours = (hour + minute / 60.0) - ist_offset
calc_day = day
if utc_hours < 0:
    utc_hours += 24.0
    calc_day -= 1

jd = swe.julday(year, month, calc_day, utc_hours)
```
- **Finding:** The master `calculate_kundali()` function does not accept a `timezone` or `tz_offset` parameter. It blindly subtracts `5.5` hours assuming all incoming `(hour, minute)` tuples represent Indian Standard Time.
- **Partial Workaround in API Layer:** [`backend/modules/kundali/api.py:40-47`](file:///c:/Desktop/astro_may_res%20(2)/astro-platform/backend/modules/kundali/api.py#L40-L47) attempts to compensate:
  ```python
  ist_offset = 5.5
  if tz != ist_offset:
      dt_local = datetime(req.year, req.month, req.day, req.hour, req.minute)
      dt_ist = dt_local + timedelta(hours=(ist_offset - tz))
      year, month, day = dt_ist.year, dt_ist.month, dt_ist.day
      hour, minute = dt_ist.hour, dt_ist.minute
  ```
  While this double-conversion converts non-IST time to IST in `api.py` so that `engine.py` can subtract 5.5 back to UTC, it creates major architectural hazards:
  - If `calculate_kundali()` is invoked directly by tests, scripts, or worker tasks without the `api.py` pre-shift, calculations for non-IST birth charts are systematically erroneous by `(5.5 - tz)` hours.
  - In [`backend/modules/kundali/varga.py:146`](file:///c:/Desktop/astro_may_res%20(2)/astro-platform/backend/modules/kundali/varga.py#L146), `generate_full_chart()` similarly hardcodes `timezone_offset = 5.5`.

#### Defect B: Day-Underflow Without Month/Year Decrement in Julian Day Calculation
In [`backend/modules/kundali/engine.py:105-107`](file:///c:/Desktop/astro_may_res%20(2)/astro-platform/backend/modules/kundali/engine.py#L105-L107):
```python
if utc_hours < 0:
    utc_hours += 24.0
    calc_day -= 1

jd = swe.julday(year, month, calc_day, utc_hours)
```
- **Finding:** If a birth occurs between 00:00 and 05:29 AM on the **1st day of any month**, `calc_day` becomes `0`.
- **Impact:** `month` and `year` are not decremented. Calling `swe.julday(year, month, 0, utc_hours)` relies on Swiss Ephemeris internal day-wrapping behavior; in standard calendar math, day 0 is undefined and should wrap to the last day of `month - 1`.

#### Defect C: Timezone Utility Ignores Arguments
In [`backend/shared/timezone/tz.py:58-63`](file:///c:/Desktop/astro_may_res%20(2)/astro-platform/backend/shared/timezone/tz.py#L58-L63):
```python
def get_local_now(tz_name: str = "Asia/Kolkata") -> datetime:
    return now_ist()

def to_local_iso(dt: datetime, tz_name: str = "Asia/Kolkata") -> str:
    return to_ist(dt).isoformat()
```
- **Finding:** `get_local_now()` and `to_local_iso()` accept a `tz_name` parameter but completely ignore it, returning `now_ist()` (+05:30) unconditionally.

---

## 4. Location Resolution & Geocoding

- **Static City Database:** [`backend/modules/kundali/cities.py:7-148`](file:///c:/Desktop/astro_may_res%20(2)/astro-platform/backend/modules/kundali/cities.py#L7-L148) provides 101 hardcoded Indian and major global cities with coordinates, elevation, and standard timezone offset.
- **Dynamic Geocoding Fallback:**
  - [`backend/modules/kundali/cities.py:173`](file:///c:/Desktop/astro_may_res%20(2)/astro-platform/backend/modules/kundali/cities.py#L173): Calls OpenStreetMap Nominatim API (`nominatim.openstreetmap.org/search`) with a `timeout=2.0` seconds.
  - **Risks:**
    1. Unauthenticated external HTTP request on user critical path.
    2. Nominatim rate-limits at 1 request/sec; concurrent user traffic will trigger HTTP 429 errors.
    3. Results are cached only in process memory; restarts clear geocoding memory.

---

## 5. Birth-Time Uncertainty & Sensitivity Analysis

- **Request Schemas:** Neither `KundaliRequest` nor `PredictionRequest` includes an `uncertainty_minutes` or `time_range` parameter.
- **Endpoint Status:** `POST /api/kundali/sensitivity` does **not exist**.
- **Passive Boundary Warnings:**
  - [`backend/modules/kundali/engine.py:207`](file:///c:/Desktop/astro_may_res%20(2)/astro-platform/backend/modules/kundali/engine.py#L207):
    `is_near_boundary = lagna_deg_in_sign < 2.0 or lagna_deg_in_sign > 28.0`
    Emits a static text note warning that Ascendant changes 1° every 4 minutes.
  - [`backend/modules/panchang/personalization.py:450-457`](file:///c:/Desktop/astro_may_res%20(2)/astro-platform/backend/modules/panchang/personalization.py#L450-L457):
    Checks if Moon longitude is within 1° of sign boundary or 0.5° of nakshatra boundary.
- **Conclusion:** There is currently no mathematical engine that perturbs birth time (e.g., ±15 min Monte Carlo simulation) to determine domain score volatility.

---

## 6. Dasha, Vargas, and Timing Engine Details

### Vimshottari Dasha Engine
- Sequence: `["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]`.
- Periods: 7, 20, 6, 10, 7, 18, 16, 19, 17 years (Total = 120 years).
- **Depth:** Computes Mahadasha (MD), Antardasha (AD), and Pratyantardasha (PD) ([`backend/modules/kundali/dasha.py:89`](file:///c:/Desktop/astro_may_res%20(2)/astro-platform/backend/modules/kundali/dasha.py#L89): `DASHA_DEPTH = "PD"`). Sookshma and Prana levels are omitted.

### Divisional Charts (Vargas)
- Implemented: **D1 (Rasi)** and **D9 (Navamsa)**.
- Navamsa Formula ([`backend/modules/kundali/varga.py:18-45`](file:///c:/Desktop/astro_may_res%20(2)/astro-platform/backend/modules/kundali/varga.py#L18-L45)):
  - Fire signs start from Mesha (0)
  - Earth signs start from Makara (9)
  - Air signs start from Tula (6)
  - Water signs start from Karka (3)
  - Pada arc: `30° / 9 = 3°20' (3.3333°)`.
- Missing Vargas: D2 (Hora), D3 (Drekkana), D4 (Chaturthamsa), D7 (Saptamsa), D10 (Dasamsa), D12 (Dwadasamsa), D16 (Shodasamsa), D20 (Vimsamsa), D24 (Chaturvimsamsa), D27 (Saptavimsamsa), D30 (Trimsamsa), D60 (Shashtiamsa).

### Event Timing Fusion
- File: [`backend/modules/prediction/timing_fusion.py:48-150`](file:///c:/Desktop/astro_may_res%20(2)/astro-platform/backend/modules/prediction/timing_fusion.py#L48-L150)
- Horizon: 15 years evaluated in monthly intervals.
- Weighting: `60% Dasha Score + 40% Transit Score`.
- Smoothing: 3-month rolling average: `(S[i-1] + S[i] + S[i+1]) / 3.0`.
- Threshold: `0.45` cutoff for qualifying timing windows.
- Consecutive window clustering merges months with gap tolerance `diff <= 2`.

---

## 7. Reference Validation & Oracle Tolerances

The test suite contains two high-value reference oracle validation suites:

1. **DrikPanchang Reference Validation ([`backend/tests/test_drikpanchang_reference.py`](file:///c:/Desktop/astro_may_res%20(2)/astro-platform/backend/tests/test_drikpanchang_reference.py)):**
   - **Oracle:** Ground truth fetched from DrikPanchang.com.
   - **Tolerances Asserted:**
     - Sunrise & Sunset: `±90 seconds` (`max_tol_mins=2`).
     - Tithi, Nakshatra, Yoga, Karana transition end times: `±2 minutes`.
   - **Cases Verified:**
     - Case 1: Chennai (Sea-level 6m) on Winter Solstice (2026-12-21).
     - Case 2: Leh (High Altitude 3500m) on Winter Solstice (2026-12-21).
     - Case 3: Chennai (2026-01-07) sunrise-proximate tithi transition.
   - **All 3 test cases pass within asserted tolerances.**

2. **Historical Reference Charts ([`backend/tests/test_reference_charts.py`](file:///c:/Desktop/astro_may_res%20(2)/astro-platform/backend/tests/test_reference_charts.py)):**
   - **Oracle:** Published charts for Jawaharlal Nehru, Mahatma Gandhi, and Swami Vivekananda.
   - **Tolerances Asserted:** Exact zodiac sign match for Lagna and 9 planets, plus Mahadasha lord match.
   - **All 3 historical chart tests pass.**

3. **Benchmark Chart Regression ([`backend/tests/test_benchmark_regression.py`](file:///c:/Desktop/astro_may_res%20(2)/astro-platform/backend/tests/test_benchmark_regression.py)):**
   - Evaluates 50 frozen benchmark charts to ensure byte-level output consistency across engine updates.
   - **All 50 regression tests pass.**

---

## 8. Summary of Engine Defects & Corrective Actions

| Defect ID | Description | Severity | File & Line | Corrective Action |
| :---: | :--- | :---: | :--- | :--- |
| **ENG-01** | Hardcoded `ist_offset = 5.5` in core calculation engine | **CRITICAL** | `modules/kundali/engine.py:102` | Pass timezone explicitly to `calculate_kundali` and use `zoneinfo` for UTC offset. |
| **ENG-02** | Day underflow on 1st of month in Julian Day calculation | **HIGH** | `modules/kundali/engine.py:105-109` | Use Python `datetime` with `timezone.utc` to calculate Julian Day via decimal UTC hours. |
| **ENG-03** | Timezone functions ignore `tz_name` argument | **HIGH** | `shared/timezone/tz.py:58-63` | Implement proper `zoneinfo.ZoneInfo(tz_name)` conversion in `get_local_now()`. |
| **ENG-04** | Bhava Chalit uses Placidus (`b'P'`) instead of Sripati (`b'S'`) | **MEDIUM** | `modules/kundali/houses.py:50` | Provide configurable house system parameter; default to Sripati for classical Vedic charts. |
| **ENG-05** | Ephemeris fallback to Moshier mode (no `.se1` files) | **MEDIUM** | `shared/ephemeris/wrapper.py:6` | Bundle Swiss Ephemeris data files (`seas_18.se1`, etc.) in deployment image. |
| **ENG-06** | OpenStreetMap Nominatim geocoding unauthenticated & synchronous | **MEDIUM** | `modules/kundali/cities.py:173` | Replace live HTTP fallback with an offline SQLite database of global cities (Geonames). |
