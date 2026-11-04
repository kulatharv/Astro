# 02 — Comprehensive Template Analysis & Localization Audit

**Project:** AstroLogic AI / Nakshatra Labs — Modern Frontend Migration  
**Document:** `docs/frontend-modernization/02_TEMPLATE_ANALYSIS.md`  
**Phase:** Phase 1 – Discovery, Architecture Assessment & Implementation Planning  
**Status:** AUDITED & FINALIZED (Verification Standard Enforced)  
**Date:** October 31, 2026  
**Auditor:** Senior Software Architect, Security Engineer & Migration Specialist  

---

## 1. Overview & Preservation Mandate `[VERIFIED]`

This document provides a code-verified analysis of all Jinja2 templates located in `app/templates/`, their client scripts (`kundali.js`, `i18n.js`), and their static localization dictionaries. 

**Critical Preservation Rule:** Under no circumstances will any file inside `app/templates/` be modified, renamed, or deleted. These templates serve as the permanent functional specification for workflows, form validation requirements, data contracts, and astrological presentations.

---

## 2. Existing Language & Localization Audit `[VERIFIED]`

### 2.1. Existing Locale Files Inventory `[VERIFIED]`
Inspection of `app/static/locales/` and `frontend/locales/` reveals:
- **`app/static/locales/en.json` (337 bytes):** Baseline 10 keys: `navbar.home`, `navbar.kundali`, `navbar.panchang`, `navbar.blogs`, `navbar.login`, `navbar.signup`, `navbar.logout`, `navbar.profile`, `navbar.prediction`, `navbar.horoscope`.
- **`app/static/locales/hi.json` (491 bytes):** Baseline 10 keys in Hindi (Devanagari script): `होम`, `कुंडली`, `पंचांग`, `ब्लॉग`, `लॉगिन`, `साइन अप`, `लॉगआउट`, `प्रोफ़ाइल`, `भविष्यवाणी`, `राशिफल`.
- **`app/static/locales/mr.json` (4,023 bytes):** Extended 52 keys in Marathi covering brand tagline, navigation, prediction domain titles, planetary labels, and form prompts.
- **`frontend/locales/`:** Replicates the 10-key baseline for `en`, `hi`, and `mr`.

### 2.2. Template Localization Mechanics `[VERIFIED]`
- **Context Injection:** In `backend/gateway/pages.py` lines 10–16:
  ```python
  def _render_page(request: Request, template_name: str, context: dict | None = None) -> HTMLResponse:
      templates = request.app.state.templates
      lang = request.cookies.get("lang", "en")
      page_context = {"request": request, "lang": lang, "t": load_translations(lang)}
      if context:
          page_context.update(context)
      return templates.TemplateResponse(template_name, page_context)
  ```
- **Language Switcher Snippet (`base.html`) `[VERIFIED]`:**
  A dropdown component exposing 8 languages linking to `/change-language/{lang}`:
  - English (`en`), हिन्दी (`hi`), मराठी (`mr`), ગુજરાતી (`gu`), தமிழ் (`ta`), తెలుగు (`te`), ಕನ್ನಡ (`kn`), বাংলা (`bn`).
- **Current Technical Debt `[VERIFIED]`:**
  While the backend infrastructure supports localization, the existing HTML templates heavily hardcode English text throughout page bodies, using `{{ t[...] }}` almost exclusively for navigation labels. The modern Next.js implementation must achieve 100% UI translation coverage using domain-structured messages (`frontend/messages/`).

---

## 3. Shared Layouts & Common UI Patterns `[VERIFIED]`

1. **Global Header & Navigation Bar:**
   - Sticky top bar (`height: 68px` or `74px`, backdrop blur `24px`, background `rgba(1, 8, 18, 0.95)`).
   - Brand logo (`AstroLogic` with superscript star), desktop navigation, language dropdown (`base.html`), authentication action buttons (`Sign In` / `Profile` / `Sign Out`), and mobile hamburger drawer.
   - *Current Debt:* Duplicated verbatim across every HTML template rather than using standard Jinja2 layout inheritance.
2. **Ambient Celestial Starfield Canvas:**
   - Multi-layered CSS radial gradients generating high-performance fixed background starfields (`rgba(155, 220, 255, 0.35)` cyan stars and `rgba(245, 193, 108, 0.28)` gold stars).
3. **Card & Surface System:**
   - Glassmorphic panels with `var(--surface)` background, `1px solid var(--border)`, rounded corners (`12px` to `18px`), and gold hover highlights (`var(--gold-border)`).
4. **Form Controls & City Autocomplete:**
   - Translucent input boxes (`rgba(255, 255, 255, 0.06)`), gold focus borders, date/time pickers, and asynchronous city autocomplete dropdowns connected to `/api/cities`.

---

## 4. Individual Template Specifications `[VERIFIED]`

---

### 4.1. `index.html` — Homepage & Celestial Portal
- **File Size:** 80,508 bytes (2,246 lines)
- **Page Purpose:** Primary marketing landing page, brand portal, educational introduction, feature showcase, and real-time cosmic overview.
- **Key Sections:**
  1. *Hero Banner:* Engaging title ("Ancient Vedic Wisdom Powered by Modern Astronomy"), CTA buttons to Kundali and Panchang, and an interactive 2D Canvas Celestial Sphere preview.
  2. *Live Cosmic Widget:* Today's Tithi, Nakshatra, and Moon sign dynamically loaded via `/api/panchang`.
  3. *Core Feature Showcase:* Kundali Chart Generator, 10-Domain Predictions, Daily Panchang, Transit Horoscopes, and Astrological Knowledge Library.
  4. *How It Works:* 3-step sequence (Birth Details Input $\to$ Swiss Ephemeris Calculation $\to$ AI Interpretation & Remedial Guidance).
  5. *Zodiac Transit Wheel:* Interactive 12-sign quick selector linking to `/horoscope?sign=X`.
  6. *Classical Philosophy & Methodology:* Explanation of Lahiri Ayanamsha, Parashari Graha Drishti, and Jaimini Chara Karakas.
  7. *Footer:* Sitemap, language selector, disclaimer, copyright, privacy policy, and terms of service.
- **Backend Routes & APIs:**
  - Page Route: `GET /` and `GET /{lang}/`
  - Fetches: `GET /api/panchang` (for live cosmic widget).
- **Authentication:** Public (no login required).

---

### 4.2. `kundali.html` & `kundali.js` — Vedic Birth Chart Engine
- **File Size:** `kundali.html` (83,723 bytes) + `kundali.js` (56,235 bytes)
- **Page Purpose:** Core Vedic horoscope generator, interactive chart viewer, planetary analysis table, divisional chart explorer, and AI astrological consultation interface.
- **Key Sections:**
  1. *Birth Data Entry Form:* Name, Gender, Birth Date (DD-MM-YYYY), Birth Time (HH:MM:SS), City Name with dynamic autocomplete dropdown, Latitude, Longitude, and Timezone offset.
  2. *Chart Style Switcher:* Seamless toggle between North Indian (Diamond/House-based) and South Indian (Square/Zodiac-based) SVG layouts.
  3. *Divisional Chart Tabs:* D1 (Rashi Chart), D9 (Navamsha Chart for marriage & inner potential), with data models supporting D4, D7, and D10.
  4. *SVG Interactive Canvas:* Dynamically drawn SVG graphic showing 12 houses, zodiac sign numbers, occupying planets, retrograde markers (`(R)`), and dignity badges (Exalted, Debilitated, Own, Moolatrikona).
  5. *Planetary Coordinates Table:* Name, Sanskrit Rashi, Degrees/Minutes/Seconds, Nakshatra & Pada, Direct/Retrograde status, Combustion status, House placement, and Karaka status.
  6. *Vimshottari Dasha Timeline:* Interactive Mahadasha and Antardasha progression tree showing start dates, end dates, and current active periods.
  7. *Yogas & Doshas Summary:* Detected auspicious Raj/Dhana yogas, Mangal Dosha status, and Kaal Sarp indicators.
  8. *PDF Export Button:* Triggers `/api/download-kundali` to generate an in-memory printable PDF report.
  9. *AstroAI Contextual Chat Assistant:* In-page chat sidebar allowing users to ask questions about their specific chart via `/api/kundali-chat`.
  10. *Saved Charts Drawer:* Allows authenticated users to save, name, reload, and manage birth profiles via `/api/kundali/saved-charts`.
- **Backend Routes & APIs:**
  - Page Route: `GET /kundali`
  - APIs Called:
    - `GET /api/cities`: Fetches city coordinates database.
    - `POST /api/kundali`: Calculates complete chart, D9, yogas, doshas, and dasha.
    - `GET /api/download-kundali`: Downloads generated PDF report.
    - `POST /api/kundali-chat`: Interactive AI chat based on chart session.
    - `POST /api/user-activity`: Logs chart generation for profile audit.
    - `GET /api/kundali/saved-charts`: Lists user's saved charts.
    - `POST /api/kundali/saved-charts`: Saves active chart to database.
- **Authentication:** Public generation allowed; saving charts and persistent profile operations require session authentication.

---

### 4.3. `prediction.html` — 10-Domain Comprehensive Life Predictions
- **File Size:** 49,751 bytes (773 lines)
- **Page Purpose:** In-depth multi-domain life analysis engine synthesizing natal planetary strength (Shadbala), house lords, divisional charts, dasha periods, and transits.
- **Ten Life Domains Evaluated:**
  1. *Career & Profession:* 10th house, D10 Dashamsha, Sun/Saturn/Mercury, Raj Yogas.
  2. *Marriage & Relationships:* 7th house, 7th lord, D9 Navamsha Lagna/7th, Venus/Jupiter karakas, Upapada Lagna (UL), Mangal Dosha.
  3. *Wealth & Finance:* 2nd (accumulated) & 11th (gains) houses, Dhana Yogas, Jupiter/Venus.
  4. *Health & Longevity:* 1st house (vitality), 6th house (disease), 8th house (longevity), Shadbala scores.
  5. *Children & Progeny:* 5th house, 5th lord, D7 Saptamsha, Jupiter (Putrakaraka).
  6. *Education & Intellect:* 4th & 5th houses, Mercury (Budha), Jupiter.
  7. *Property & Vehicles:* 4th house (Sukha bhava), Mars (Bhumi karaka), Venus (Vahana karaka), D4.
  8. *Challenges & Obstacles:* 6th, 8th, 12th Trik houses, Saturn Sade Sati, Rahu/Ketu afflictions.
  9. *Travel & Foreign Relocation:* 9th (pilgrimage/long travel) & 12th (foreign settlement) houses.
  10. *Spirituality & Dharma:* 9th (Dharma) & 12th (Moksha) houses, Jupiter, Ketu.
- **Backend Routes & APIs:**
  - Route: `GET /prediction`
  - APIs Called:
    - `GET /api/cities`: City autocomplete.
    - `POST /api/domains`: Evaluates all 10 life domains simultaneously.
    - `POST /api/prediction/timing/{domain}`: Retrieves granular transit timing windows.
- **Authentication:** Protected by default-deny middleware (requires login or active session).

---

### 4.4. `panchang.html` — Daily Panchang & Vedic Decision Engine
- **File Size:** 57,989 bytes (1,058 lines)
- **Page Purpose:** Comprehensive astronomical Hindu almanac, real-time Choghadiya countdown, planetary Hora schedule, auspicious Muhurats, and daily Vedic decision advisor.
- **Key Sections:**
  1. *Live Cosmic Status Hero:* Auspiciousness score badge, live countdown to next Choghadiya transition, active Tithi and Moon nakshatra.
  2. *Five Limbs of Panchang (Panch-Anga):*
     - Tithi (Lunar day, Shukla/Krishna Paksha, exact end time).
     - Nakshatra (Lunar mansion 1–27, active Pada 1–4, deity, ruling planet).
     - Yoga (Solilunar combination 1–27, auspicious/inauspicious flag).
     - Karana (Half-tithi 1–60, movable/fixed classification).
     - Vara (Solar day of the week, ruling planet).
  3. *Solar & Lunar Timings:* Sunrise, Sunset, Moonrise, Moonset, Sun sign, Moon sign.
  4. *Auspicious & Inauspicious Kaal Windows:*
     - Rahu Kaal, Yamaghanta, Gulika Kaal (inauspicious—to be avoided).
     - Abhijit Muhurat, Brahma Muhurat, Amrit Kaal (auspicious—ideal for new beginnings).
  5. *Real-Time Choghadiya Tables:* Day and Night Choghadiya schedules classified as Shubh (Auspicious), Labh (Prosperity), Amrit (Best), Chal (Neutral), Rog (Disease), Kaal (Loss), and Udveg (Anxiety).
  6. *Planetary Horas Table:* 24 hourly planetary rulers based on sunrise and weekday lord.
  7. *Vedic Decision Engine (Do's & Don'ts):* Algorithmic advice on travel, financial contracts, property purchase, and health treatments.
  8. *Disha Shool & Remedies:* Directional travel obstacles and traditional counter-remedies.
  9. *Upcoming Festivals Drawer:* 14-day chronological festival feed (`/api/festivals/upcoming?limit=14`).
  10. *Social Share Image & Calendar Export:* Triggers `/api/panchang/share-image` and `/api/panchang/calendar.ics`.
- **Backend Routes & APIs:**
  - Route: `GET /panchang`
  - APIs Called:
    - `POST /api/panchang`: Full Panchang calculation for given date/city.
    - `POST /api/panchang/decision`: Personalized decision engine queries.
    - `GET /api/festivals/upcoming`: Upcoming festival calendar.
    - `GET /api/panchang/calendar.ics`: iCal export.
    - `GET /api/panchang/share-image`: Shareable branded PNG image.
- **Authentication:** Public.

---

### 4.5. `daily-horoscope.html` — 12-Zodiac Transit Horoscope
- **File Size:** 27,164 bytes (499 lines)
- **Page Purpose:** Daily astrological transit forecasts tailored to each of the 12 Vedic/Western zodiac signs.
- **Key Sections:**
  1. *Horizontal Zodiac Scrollbar:* 12 interactive sign pills with Sanskrit & Western names, elemental symbols, and active indicators.
  2. *Daily Transit Scorecard:* Career, Love, Wealth, and Health vitality bars.
  3. *Predictive Text Commentary:* General overview, opportunities, and cautionary advice.
  4. *Cosmic Lucky Metrics:* Lucky Number, Lucky Color, Auspicious Time Window, and Favorable Direction.
- **Backend Routes & APIs:**
  - Route: `GET /horoscope`
  - APIs Called: `GET /api/horoscope/{sign_idx}` (0 = Aries to 11 = Pisces).
- **Authentication:** Public.

---

### 4.6. `blogs.html` & `blog-detail.html` — Knowledge Library & CMS
- **File Sizes:** `blogs.html` (21,590 bytes), `blog-detail.html` (7,543 bytes)
- **Page Purpose:** Public educational articles, classical Jyotish tutorials, planetary transit commentaries, and SEO hub.
- **Backend Routes & APIs:**
  - Routes: `GET /blogs`, `GET /blog/{blog_id}`
  - APIs Called: `GET /api/blogs`, `GET /api/blogs/{slug_or_id}`
- **Authentication:** Public for reading; Admin for authoring.

---

### 4.7. `auth.html` — Dual Authentication Portal
- **File Size:** 11,470 bytes (475 lines)
- **Page Purpose:** Unified user login and registration portal.
- **Backend Routes & APIs:**
  - Routes: `GET /login`, `GET /signup`, `POST /login`, `POST /signup`
  - REST APIs: `POST /api/auth/login`, `POST /api/auth/signup`
- **Authentication:** Public.

---

### 4.8. `profile.html` — User Profile & Activity Hub
- **File Size:** 13,922 bytes (654 lines)
- **Page Purpose:** User account settings, saved birth details, default astrological preferences, and security audit log.
- **Backend Routes & APIs:**
  - Route: `GET /profile`, `POST /profile`
- **Authentication:** Protected (requires user login).

---

### 4.9. Admin Suite (`admin-*.html`)
- **Templates:**
  - `admin-login.html` (4,165 bytes): Dedicated admin sign-in with PBKDF2 hash verification.
  - `admin-blog.html` (8,635 bytes): Article authoring editor, markdown support, publishing status toggle, and deletion controls.
  - `admin-users.html` (5,653 bytes): Paginated directory of registered users with role badges and signup dates.
  - `admin-activity.html` (5,437 bytes): Real-time system-wide user action audit trail.
  - `admin-feedback.html` (4,713 bytes): Beta-testing feedback submissions and user bug reports.
- **Authentication:** Strictly protected; requires `request.session["admin"] == "true"`.
