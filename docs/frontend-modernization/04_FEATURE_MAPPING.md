# 04 — Feature Mapping, Calculation Ownership & Multilingual Coverage

**Project:** AstroLogic AI / Nakshatra Labs — Modern Frontend Migration  
**Document:** `docs/frontend-modernization/04_FEATURE_MAPPING.md`  
**Phase:** Phase 1 – Discovery, Architecture Assessment & Implementation Planning  
**Status:** AUDITED & FINALIZED (Verification Standard Enforced)  
**Date:** October 31, 2026  
**Auditor:** Senior Software Architect, Security Engineer & Migration Specialist  

---

## 1. Architectural Principle: Backend Ownership of Astrology Calculations `[VERIFIED]`

AstroLogic AI enforces a strict architectural boundary: **FastAPI remains the sole authoritative calculation engine.** 

The Next.js frontend is strictly responsible for presentation, user interaction, input capture, and visual rendering. It must never independently calculate, interpolate, or modify astronomical or astrological data.

### 1.1. Calculation Ownership Matrix `[VERIFIED]`

| Astrological Feature | Calculation Owner | Frontend Presentation Responsibility |
| :--- | :--- | :--- |
| **Birth Chart (D1 Lagna)** | **FastAPI** (`kundali/engine.py`) | Declarative SVG rendering of 12 houses and occupying planets |
| **Planetary Coordinates** | **FastAPI** (`pyswisseph` wrapper) | Format degrees, signs, nakshatras, and retrograde/combustion badges |
| **Navamsha (D9 Chart)** | **FastAPI** (`kundali/engine.py`) | Render verified D9 Dhanu Lagna and Gemini 7th house layout |
| **Divisional Charts (D2–D60)**| **FastAPI** (`kundali/varga.py`) | Render divisional charts grid (Hora, Drekkana, Saptamsha, Dashamsha) |
| **Vimshottari Dasha Tree** | **FastAPI** (`kundali/dasha.py`) | Interactive accordion displaying MD $\to$ AD $\to$ PD progression |
| **Shadbala 6-Fold Strength**| **FastAPI** (`shared/veda/shadbala.py`)| ECharts radar visualization comparing scores against minimum Rupas |
| **Ashtakavarga (BAV / SAV)**| **FastAPI** (`shared/veda/ashtakavarga.py`)| 12x8 BAV bindu grid and 12-house Sarvashtakavarga totals |
| **Yogas & Combinations** | **FastAPI** (`shared/veda/yogas.py`) | Cards showing verified Raj/Dhana yogas with textual commentary |
| **Doshas & Cancellations** | **FastAPI** (`shared/veda/doshas.py`) | Multi-frame Mangal Dosha (Lagna, Moon, Venus) and Sade Sati badges |
| **Daily Panchang 5 Limbs** | **FastAPI** (`panchang/engine.py`) | Display Tithi, Nakshatra, Yoga, Karana, Vara with exact end-times |
| **Choghadiya & Horas** | **FastAPI** (`panchang/choghadiya.py`)| Real-time countdown timer to the next transition and Day/Night tables |
| **Muhurat Decision Engine** | **FastAPI** (`panchang/decision.py`) | Feasibility score and traditional Do's & Don'ts advice |
| **10-Domain Predictions** | **FastAPI** (`prediction/domains/`) | Vitality score meters (0–100), evidence lists, and remedial advice |
| **Event Timing Windows** | **FastAPI** (`prediction/timing.py`) | Concrete favorable calendar date ranges and transit activations |
| **AI Astro-Narratives** | **FastAPI** (`narrative/llm_client.py`)| Server-Sent Events (SSE) live typing text stream |

---

## 2. Date, Time & Coordinate Input Contract `[PROPOSED]`

To prevent browser-local timezone mutations corrupting astronomical Julian Day calculations, the frontend will adhere to a strict numeric input contract:

```typescript
// Strict Input DTO sent to FastAPI via Next.js BFF Proxy
export interface BirthInputContract {
  day: number;      // 1-31 (Strict Integer)
  month: number;    // 1-12 (Strict Integer)
  year: number;     // 1900-2100 (Strict Integer)
  hour: number;     // 0-23 (Strict Integer, 24-hour format)
  minute: number;   // 0-59 (Strict Integer)
  second: number;   // 0-59 (Strict Integer, defaults to 0)
  city: string;     // Validated from /api/cities
  latitude?: number;// Optional override (-90.0 to +90.0)
  longitude?: number;// Optional override (-180.0 to +180.0)
  timezone?: string;// IANA timezone string e.g. "Asia/Kolkata"
}
```

### Critical Rules:
1. **Zero Browser Local Date Math:** The frontend must never convert birth inputs using `new Date(...)` or JavaScript's localized time getters.
2. **Backend Timezone Resolution:** The FastAPI backend (`shared/timezone/tz.py`) is the sole authority for historical daylight saving time (DST) and UTC offset calculations.
3. **Display-Only Formatting:** Frontend date utilities (e.g. `date-fns` or `Intl.DateTimeFormat`) are restricted to formatting returned backend timestamps for display.
4. **Coordinate Precision:** Rounding of degrees is display-only (e.g. `17° 12' 41"`). Original floating-point decimal coordinates (`lagna_degree_decimal`) must be preserved in state stores.

---

## 3. Multilingual Coverage Matrix across Modules `[PROPOSED]`

Every user-facing module will support **English (`en`)**, **Hindi (`hi`)**, and **Marathi (`mr`)**, with traditional **Sanskrit (`sa`)** terminology preserved:

| Application Module | English (`en`) | Hindi (`hi`) | Marathi (`mr`) | Sanskrit Terminology Preservation |
| :--- | :--- | :--- | :--- | :--- |
| **Global Navigation & Layout** | Fully Translated | Fully Translated | Fully Translated | N/A |
| **Authentication & Profile** | Fully Translated | Fully Translated | Fully Translated | N/A |
| **Kundali Input & Forms** | Fully Translated | Fully Translated | Fully Translated | Field prompts localized |
| **Kundali D1/D9 Visualizer** | Translated UI Controls | Translated UI Controls | Translated UI Controls | Rashis (Mesha-Meena), Grahas (Surya-Ketu) |
| **Planetary Position Table** | Translated Headers | Translated Headers | Translated Headers | Nakshatras & Dignities preserved |
| **Vimshottari Dasha Tree** | Translated UI Controls | Translated UI Controls | Translated UI Controls | Mahadasha/Antardasha lords preserved |
| **Daily Panchang 5 Limbs** | Fully Translated | Fully Translated | Fully Translated | Tithi, Nakshatra, Yoga, Karana preserved |
| **Choghadiya & Horas** | Translated Categories | Translated Categories | Translated Categories | Shubh, Labh, Amrit, Rog, Kaal, Udveg |
| **10-Domain Predictions** | Translated Domain UI | Translated Domain UI | Translated Domain UI | House names (Tanu, Sukha, Kalatra, Karma) |
| **Remedial Measures** | Translated Guidelines | Translated Guidelines | Translated Guidelines | Mantras in Devanagari script |
| **Daily Horoscope** | Translated Forecasts | Translated Forecasts | Translated Forecasts | Zodiac glyphs & Rashi names |
| **Knowledge Library** | English Articles | Future Expansion | Future Expansion | Technical glossary linked |
| **Admin Portal** | Fully Translated | Optional | Optional | Operational metadata in English |

---

## 4. Master Feature-to-Route Mapping Table `[VERIFIED / PROPOSED]`

| Feature Category | Existing Template / Route | Proposed Next.js Route | Security Classification | Calculation Owner |
| :--- | :--- | :--- | :--- | :--- |
| **Homepage** | `index.html`<br>`GET /` | `app/[locale]/page.tsx` | `PUBLIC` | Static / Client |
| **User Sign In** | `auth.html`<br>`GET/POST /login` | `app/[locale]/(auth)/login/page.tsx` | `PUBLIC` | FastAPI Auth |
| **User Registration** | `auth.html`<br>`GET/POST /signup` | `app/[locale]/(auth)/signup/page.tsx` | `PUBLIC` | FastAPI Auth |
| **User Profile** | `profile.html`<br>`GET/POST /profile` | `app/[locale]/(dashboard)/profile/page.tsx` | `AUTHENTICATED` | FastAPI DB |
| **Saved Charts** | Inferred in `kundali.js`<br>`profile.html` | `app/[locale]/(dashboard)/saved-charts/page.tsx` | `AUTHENTICATED` | FastAPI DB |
| **User Activity** | `admin-activity.html`<br>`profile.html` | `app/[locale]/(dashboard)/activity/page.tsx` | `AUTHENTICATED` | FastAPI DB |
| **Kundali Generator** | `kundali.html`<br>`GET /kundali` | `app/[locale]/kundali/page.tsx` | `PUBLIC / SESSION`| **FastAPI** |
| **Persistent Chart View** | Inferred from session | `app/[locale]/kundali/[id]/page.tsx` | `AUTHENTICATED` | **FastAPI** |
| **Divisional Charts (D-Charts)**| Missing in Jinja2 UI | `app/[locale]/kundali/[id]/divisional/page.tsx` | `AUTHENTICATED` | **FastAPI** |
| **Vimshottari Dasha Tree** | `kundali.html` (timeline) | `components/kundali/DashaTimeline.tsx` | `PUBLIC / SESSION`| **FastAPI** |
| **PDF Report Download** | `kundali.html` button | Action: `/api/download-kundali` | `AUTHENTICATED` | **FastAPI** |
| **Panchang & Choghadiya** | `panchang.html`<br>`GET /panchang` | `app/[locale]/panchang/page.tsx` | `PUBLIC` | **FastAPI** |
| **Muhurat Decision Engine** | `panchang.html` (decision) | `components/panchang/DecisionEngine.tsx` | `AUTHENTICATED` | **FastAPI** |
| **Personalized Panchang** | `panchang.html` (profile) | `app/[locale]/panchang/personalized/page.tsx` | `AUTHENTICATED` | **FastAPI** |
| **Panchang iCal Export** | `panchang.html` button | Action: `/api/panchang/calendar.ics` | `PUBLIC` | **FastAPI** |
| **Panchang Social Share** | `panchang.html` button | Action: `/api/panchang/share-image` | `PUBLIC` | **FastAPI** |
| **Upcoming Festivals** | `panchang.html` (drawer) | `components/panchang/FestivalFeed.tsx` | `PUBLIC` | **FastAPI** |
| **10-Domain Predictions** | `prediction.html`<br>`GET /prediction` | `app/[locale]/predictions/page.tsx` | `AUTHENTICATED` | **FastAPI** |
| **Domain Detail (Marriage)**| `prediction.html` tab | `app/[locale]/predictions/marriage/page.tsx` | `AUTHENTICATED` | **FastAPI** |
| **Domain Detail (Career)** | `prediction.html` tab | `app/[locale]/predictions/career/page.tsx` | `AUTHENTICATED` | **FastAPI** |
| **Dasha-Transit Timing** | `prediction.html` (timing) | `components/predictions/TimingWindows.tsx`| `AUTHENTICATED` | **FastAPI** |
| **Remedial Measures** | `prediction.html` (remedies)| `components/predictions/RemediesCard.tsx` | `AUTHENTICATED` | **FastAPI** |
| **AI Narrative Stream** | `backend/modules/narrative` | `components/ai/AstroNarrativeStream.tsx` | `AUTHENTICATED` | **FastAPI** |
| **Daily Horoscope** | `daily-horoscope.html` | `app/[locale]/horoscope/page.tsx` | `PUBLIC` | **FastAPI** |
| **Sign Forecast** | `daily-horoscope.html` tab | `app/[locale]/horoscope/[sign]/page.tsx` | `PUBLIC` | **FastAPI** |
| **Knowledge Library** | `blogs.html`<br>`GET /blogs` | `app/[locale]/library/page.tsx` | `PUBLIC` | **FastAPI** |
| **Article Reader** | `blog-detail.html` | `app/[locale]/library/[slug]/page.tsx` | `PUBLIC` | **FastAPI** |
| **About & Methodology** | `about.html`<br>`GET /about` | `app/[locale]/about/page.tsx` | `PUBLIC` | Static / FastAPI |
| **Admin Login** | `admin-login.html` | `app/[locale]/admin/login/page.tsx` | `PUBLIC` | FastAPI Auth |
| **Admin Blog CMS** | `admin-blog.html` | `app/[locale]/admin/blogs/page.tsx` | `ADMIN_ONLY` | FastAPI DB |
| **Admin User Directory** | `admin-users.html` | `app/[locale]/admin/users/page.tsx` | `ADMIN_ONLY` | FastAPI DB |
| **Admin Activity Log** | `admin-activity.html` | `app/[locale]/admin/activity/page.tsx` | `ADMIN_ONLY` | FastAPI DB |
| **Admin Cache Flush** | Embedded in Admin API | `app/[locale]/admin/cache/page.tsx` | `ADMIN_ONLY` | FastAPI Admin |
