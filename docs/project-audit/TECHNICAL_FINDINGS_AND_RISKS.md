# Technical Findings, Defects, and Risk Register

**Project:** AstroLogic AI  
**Scope:** Prioritized register of confirmed defects, architectural gaps, security vulnerabilities, and operational risks.

---

## 1. Prioritized Findings Register

| ID | Title & Subsystem | Severity | Confidence | Blocks Next Phase? |
| :---: | :--- | :---: | :---: | :---: |
| **F-01** | Hardcoded IST Offset in Calculation Engine | **CRITICAL** | Confirmed | **YES** |
| **F-02** | Month-Underflow Defect in Julian Day Conversion | **HIGH** | Confirmed | **YES** |
| **F-03** | Timezone Conversion Functions Ignore Arguments | **HIGH** | Confirmed | **YES** |
| **F-04** | Missing Database Persistence for User Charts | **HIGH** | Confirmed | **YES** |
| **F-05** | Fallback to Moshier Ephemeris Mode (No `.se1` Files) | **MEDIUM** | Confirmed | No |
| **F-06** | Absence of Birth-Time Sensitivity Endpoint | **MEDIUM** | Confirmed | No |
| **F-07** | Incomplete Divisional Charts (Only D9 Implemented) | **MEDIUM** | Confirmed | No |
| **F-08** | Synchronous Unauthenticated Geocoding Dependency | **MEDIUM** | Confirmed | No |
| **F-09** | Lack of CSRF Protection on Session Mutating Forms | **MEDIUM** | Confirmed | No |
| **F-10** | Dasha Engine Terminates at Pratyantardasha (PD) | **LOW** | Confirmed | No |
| **F-11** | Bhava Chalit Uses Placidus Instead of Classical Sripati | **LOW** | Confirmed | No |
| **F-12** | Deprecated `.dict()` Call in Narrative Job Handler | **LOW** | Confirmed | No |
| **F-13** | 16 Zero-Byte Stub Files in Legacy App Directory | **LOW** | Confirmed | No |
| **F-14** | Absence of Rate Limiting on Heavy AI / Chart Endpoints | **MEDIUM** | Confirmed | No |
| **F-15** | Absence of Automated CI/CD Workflow Configurations | **MEDIUM** | Confirmed | No |

---

## 2. Detailed Findings & Corrective Action Plans

### Finding F-01: Hardcoded IST Offset in Calculation Engine
- **Description:** `calculate_kundali()` hardcodes `ist_offset = 5.5` to convert local wall-clock hours to UTC Julian Day.
- **Evidence:** [`backend/modules/kundali/engine.py:102-103`](file:///c:/Desktop/astro_may_res%20(2)/astro-platform/backend/modules/kundali/engine.py#L102-L103)
- **Impact:** Any chart calculation invoked directly without `api.py` preprocessing generates erroneous planetary positions and Ascendant degrees for non-IST birth locations (e.g., US, Europe).
- **Severity:** **CRITICAL** | **Confidence:** Confirmed
- **Dependencies:** `modules/kundali/api.py`, `modules/prediction/api.py`, `modules/kundali/varga.py`
- **Blocks Next Phase:** **YES**
- **Recommended Action:** Refactor `calculate_kundali(year, month, day, hour, minute, lat, lon, tz_name="Asia/Kolkata")` to use Python 3.9+ `zoneinfo.ZoneInfo(tz_name)` to determine the exact UTC datetime before computing Julian Day.
- **Acceptance Criteria:** A chart born in New York (`America/New_York`, UTC-5/UTC-4 EDT) calculates identical planetary longitudes whether passed via API or directly to `calculate_kundali()`.

---

### Finding F-02: Month-Underflow Defect in Julian Day Conversion
- **Description:** When `hour + minute/60 < 5.5`, the calculation decrements `calc_day -= 1`. On the 1st of a month, `calc_day` becomes `0`, but `month` and `year` remain unchanged.
- **Evidence:** [`backend/modules/kundali/engine.py:105-109`](file:///c:/Desktop/astro_may_res%20(2)/astro-platform/backend/modules/kundali/engine.py#L105-L109)
- **Impact:** Births occurring between 00:00 and 05:29 AM on the 1st of any month pass `day=0` to `swe.julday()`, causing subtle or severe calendar date miscalculations.
- **Severity:** **HIGH** | **Confidence:** Confirmed
- **Dependencies:** None
- **Blocks Next Phase:** **YES**
- **Recommended Action:** Replace manual day subtraction arithmetic with standard `datetime.datetime` arithmetic:
  ```python
  dt_local = datetime(year, month, day, hour, minute, tzinfo=zone)
  dt_utc = dt_local.astimezone(timezone.utc)
  decimal_utc_hour = dt_utc.hour + dt_utc.minute / 60.0 + dt_utc.second / 3600.0
  jd = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day, decimal_utc_hour)
  ```
- **Acceptance Criteria:** Unit test for birth on `2026-01-01 02:00 AM IST` yields UTC date `2025-12-31 20:30 UTC` and verified planetary positions.

---

### Finding F-03: Timezone Conversion Functions Ignore Arguments
- **Description:** `get_local_now()` and `to_local_iso()` accept a `tz_name` argument but return hardcoded IST conversions.
- **Evidence:** [`backend/shared/timezone/tz.py:58-63`](file:///c:/Desktop/astro_may_res%20(2)/astro-platform/backend/shared/timezone/tz.py#L58-L63)
- **Impact:** Misleads calling modules into assuming localized timestamps are being formatted, while all output remains fixed to Indian Standard Time.
- **Severity:** **HIGH** | **Confidence:** Confirmed
- **Dependencies:** `shared/timezone/`
- **Blocks Next Phase:** **YES**
- **Recommended Action:** Use `zoneinfo.ZoneInfo(tz_name)` to format localized timestamps.
- **Acceptance Criteria:** `get_local_now("America/New_York")` returns current time with offset `-04:00` or `-05:00`.

---

### Finding F-04: Missing Database Persistence for User Charts
- **Description:** Alembic database migrations define tables for `users`, `user_profiles`, `blogs`, and `feedback`, but no table exists for saving and managing multiple birth charts.
- **Evidence:** [`backend/alembic/versions/20260526_0001_initial_postgresql_schema.py`](file:///c:/Desktop/astro_may_res%20(2)/astro-platform/backend/alembic/versions/20260526_0001_initial_postgresql_schema.py)
- **Impact:** Users cannot save charts, revisit past predictions, or manage a roster of family/client charts. The system currently functions as an ephemeral calculator.
- **Severity:** **HIGH** | **Confidence:** Confirmed
- **Dependencies:** PostgreSQL / SQLite, SQLAlchemy ORM
- **Blocks Next Phase:** **YES**
- **Recommended Action:** Add Alembic migration `0004_create_user_charts_table.py` defining:
  - `id`, `user_id` (FK), `name`, `gender`, `birth_date`, `birth_time`, `city`, `latitude`, `longitude`, `timezone`, `chart_data` (JSONB), `created_at`, `updated_at`.
- **Acceptance Criteria:** Authenticated user can `POST /api/user/charts` to persist a chart and `GET /api/user/charts` to reload it.

---

### Finding F-05: Fallback to Moshier Ephemeris Mode
- **Description:** No `.se1` compressed ephemeris data files are bundled in the repository or deployment filesystem.
- **Evidence:** [`backend/shared/ephemeris/wrapper.py:6`](file:///c:/Desktop/astro_may_res%20(2)/astro-platform/backend/shared/ephemeris/wrapper.py#L6)
- **Impact:** Swiss Ephemeris operates in analytical Moshier mode, falling short of NASA JPL DE431 sub-arcsecond accuracy.
- **Severity:** **MEDIUM** | **Confidence:** Confirmed
- **Dependencies:** Docker build / package bundle
- **Blocks Next Phase:** No
- **Recommended Action:** Download `seas_18.se1`, `semo_18.se1`, and `sepl_18.se1` from Astrodienst into `backend/ephe/` and set `swe.set_ephe_path(settings.ephe_path)`.
- **Acceptance Criteria:** `swe.calc_ut()` executes without Moshier fallback warnings for dates 1800–2100 CE.

---

### Finding F-06: Absence of Birth-Time Sensitivity Endpoint
- **Description:** LLD describes birth-time sensitivity analysis, but no endpoint `POST /api/kundali/sensitivity` exists.
- **Evidence:** [`backend/modules/kundali/api.py`](file:///c:/Desktop/astro_may_res%20(2)/astro-platform/backend/modules/kundali/api.py)
- **Impact:** Users uncertain of their exact birth minute cannot evaluate chart volatility or Ascendant shifts.
- **Severity:** **MEDIUM** | **Confidence:** Confirmed
- **Dependencies:** `modules/kundali/engine.py`
- **Blocks Next Phase:** No
- **Recommended Action:** Implement `POST /api/kundali/sensitivity` testing the chart at `t - 15m`, `t`, and `t + 15m` and reporting Ascendant or Navamsa sign transitions.
- **Acceptance Criteria:** Returns volatility score and flags boundary risk when Ascendant crosses sign within window.

---

### Finding F-07: Incomplete Divisional Charts
- **Description:** Only D1 and D9 are implemented; D2 through D60 are absent.
- **Evidence:** [`backend/modules/kundali/varga.py:32`](file:///c:/Desktop/astro_may_res%20(2)/astro-platform/backend/modules/kundali/varga.py#L32)
- **Impact:** Advanced Vedic predictive methods requiring D10 (Career) or D7 (Children) cannot inspect specialized divisional charts.
- **Severity:** **MEDIUM** | **Confidence:** Confirmed
- **Dependencies:** `modules/kundali/varga.py`
- **Blocks Next Phase:** No
- **Recommended Action:** Add mathematical algorithms for D10 (Dasamsa), D7 (Saptamsa), and D60 (Shashtiamsa).
- **Acceptance Criteria:** Endpoint `/api/kundali/varga/D10` returns validated Dasamsa planet signs.

---

### Finding F-08: Synchronous Unauthenticated Geocoding Dependency
- **Description:** Unknown cities trigger a synchronous HTTP call to Nominatim with a 2-second timeout.
- **Evidence:** [`backend/modules/kundali/cities.py:173`](file:///c:/Desktop/astro_may_res%20(2)/astro-platform/backend/modules/kundali/cities.py#L173)
- **Impact:** API latency spikes under load; risk of IP bans from OpenStreetMap under concurrent traffic.
- **Severity:** **MEDIUM** | **Confidence:** Confirmed
- **Dependencies:** None
- **Blocks Next Phase:** No
- **Recommended Action:** Embed an offline SQLite database of global cities (e.g., GeoNames dataset of 150,000+ cities) locally.
- **Acceptance Criteria:** Zero external HTTP requests during city resolution.

---

### Finding F-09: Lack of CSRF Protection on Session Mutating Forms
- **Description:** Authentication uses `SessionMiddleware` cookies with `SameSite=Lax`, but forms do not validate anti-CSRF tokens.
- **Evidence:** [`backend/gateway/main.py:179-183`](file:///c:/Desktop/astro_may_res%20(2)/astro-platform/backend/gateway/main.py#L179-L183)
- **Impact:** Vulnerability to cross-site request forgery if third-party web content initiates state changes.
- **Severity:** **MEDIUM** | **Confidence:** Confirmed
- **Dependencies:** FastAPI Gateway
- **Blocks Next Phase:** No
- **Recommended Action:** Implement double-submit cookie or header-based CSRF validation for all state-mutating requests (`POST`, `PUT`, `DELETE`).
- **Acceptance Criteria:** Requests lacking matching `X-CSRF-Token` header rejected with HTTP 403.

---

### Finding F-10: Dasha Engine Terminates at Pratyantardasha (PD)
- **Description:** Vimshottari calculations terminate at level 3 (PD).
- **Evidence:** [`backend/modules/kundali/dasha.py:89`](file:///c:/Desktop/astro_may_res%20(2)/astro-platform/backend/modules/kundali/dasha.py#L89)
- **Impact:** Cannot compute minute-by-minute or daily timing (Sookshma Dasha).
- **Severity:** **LOW** | **Confidence:** Confirmed
- **Dependencies:** `modules/kundali/dasha.py`
- **Blocks Next Phase:** No
- **Recommended Action:** Extend algorithm optionally to compute Sookshma Dasha for current active window.
- **Acceptance Criteria:** Dasha timeline contains SD periods when requested.

---

### Finding F-11: Bhava Chalit Uses Placidus Instead of Classical Sripati
- **Description:** Bhava Chalit calls `swe.houses_ex(..., b'P')` (Placidus) instead of `b'S'` (Sripati).
- **Evidence:** [`backend/modules/kundali/houses.py:50`](file:///c:/Desktop/astro_may_res%20(2)/astro-platform/backend/modules/kundali/houses.py#L50)
- **Impact:** Vedic purists will notice cusp discrepancies between AstroLogic and traditional desktop software (e.g., Jagannatha Hora).
- **Severity:** **LOW** | **Confidence:** Confirmed
- **Dependencies:** None
- **Blocks Next Phase:** No
- **Recommended Action:** Provide `house_system` parameter allowing user to select between Sripati (`b'S'`), Placidus (`b'P'`), or Equal (`b'E'`).
- **Acceptance Criteria:** Default Vedic charts cast via Sripati.

---

### Finding F-12: Deprecated `.dict()` Call in Narrative Job Handler
- **Description:** `jobs.py:91` calls `result.dict()`, triggering Pydantic v2 deprecation warning on every job completion.
- **Evidence:** [`backend/modules/narrative/jobs.py:91`](file:///c:/Desktop/astro_may_res%20(2)/astro-platform/backend/modules/narrative/jobs.py#L91)
- **Impact:** Log noise; risk of failure upon future Pydantic v3 upgrade.
- **Severity:** **LOW** | **Confidence:** Confirmed
- **Dependencies:** Pydantic
- **Blocks Next Phase:** No
- **Recommended Action:** Change `result.dict()` to `result.model_dump()`.
- **Acceptance Criteria:** Warning eliminated in test execution logs.

---

### Finding F-13: 16 Zero-Byte Stub Files in Legacy App Directory
- **Description:** 16 empty files exist in `backend/app/` from the legacy monolithic codebase.
- **Evidence:** `backend/app/ai/llm_service.py`, `backend/app/astrology/julian.py`, etc.
- **Impact:** Developer confusion during onboarding; code smell.
- **Severity:** **LOW** | **Confidence:** Confirmed
- **Dependencies:** None
- **Blocks Next Phase:** No
- **Recommended Action:** Delete unused legacy directories under `backend/app/` that have been replaced by `backend/modules/` and `backend/shared/`.
- **Acceptance Criteria:** Zero 0-byte source files in repository.

---

### Finding F-14: Absence of Rate Limiting on Heavy AI / Chart Endpoints
- **Description:** No rate limiting middleware exists on `/api/prediction` or `/api/kundali`.
- **Evidence:** [`backend/gateway/main.py`](file:///c:/Desktop/astro_may_res%20(2)/astro-platform/backend/gateway/main.py)
- **Impact:** Potential resource exhaustion (Denial of Service) if malicious clients flood compute-heavy endpoints.
- **Severity:** **MEDIUM** | **Confidence:** Confirmed
- **Dependencies:** Redis
- **Blocks Next Phase:** No
- **Recommended Action:** Introduce `slowapi` or custom Redis sliding-window rate limiter (e.g., 60 req/min for charts, 10 req/min for AI predictions).
- **Acceptance Criteria:** Excessive requests receive HTTP 429 Too Many Requests.

---

### Finding F-15: Absence of Automated CI/CD Workflow Configurations
- **Description:** No GitHub Actions workflow (`.github/workflows/*.yml`) is configured in the repository.
- **Evidence:** Root directory inspection shows no `.github/` folder.
- **Impact:** Risk of regression bugs being committed without automated validation.
- **Severity:** **MEDIUM** | **Confidence:** Confirmed
- **Dependencies:** GitHub repository
- **Blocks Next Phase:** No
- **Recommended Action:** Commit `.github/workflows/test.yml` running `pytest` and linter checks on every pull request and push to `main`.
- **Acceptance Criteria:** Automated CI pipeline turns green on GitHub pull requests.
