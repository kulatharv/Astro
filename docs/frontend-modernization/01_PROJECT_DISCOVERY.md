# 01 — Project Discovery & Architecture Assessment

**Project:** AstroLogic AI / Nakshatra Labs — Modern Frontend Migration  
**Document:** `docs/frontend-modernization/01_PROJECT_DISCOVERY.md`  
**Phase:** Phase 1 – Discovery, Architecture Assessment & Implementation Planning  
**Status:** AUDITED & FINALIZED (Verification Standard Enforced)  
**Date:** October 31, 2026  
**Auditor:** Senior Software Architect, Security Engineer & Migration Specialist  

---

## 1. Executive Summary & Verification Methodology

AstroLogic AI (Nakshatra Labs) is an enterprise computational Vedic astrology (Jyotish) and AI-driven life prediction platform. It combines high-precision astronomical algorithms (Swiss Ephemeris), classical Parashari and Jaimini mathematical rule engines, an automated 10-domain prediction engine, an interactive daily Panchang/Muhurat decision engine, and multilingual client accessibility.

This discovery document records the verified physical structure, runtime topology, computational layers, authentication mechanics, localization footprint, and frontend-to-backend boundaries.

### Verification Classification Standard
In accordance with the Phase 1 audit mandate, all statements throughout this documentation set are strictly labeled:
- **`[VERIFIED]`**: Directly confirmed by inspecting backend Python code, templates, or runtime configuration.
- **`[DOCUMENTED]`**: Described in existing repository documentation but not independently executed.
- **`[PROPOSED]`**: Recommended future architecture for the modern Next.js implementation.
- **`[REQUIRES RUNTIME TEST]`**: Architectural interaction that cannot be confirmed solely from static code inspection.
- **`[UNKNOWN]`**: Insufficient evidence in the current repository.

---

## 2. Codebase Topology & Directory Structure `[VERIFIED]`

Inspection of `c:\Desktop\astro_may_res (2)\astro-platform` reveals a dual-layered repository structure resulting from progressive architectural evolution:

```
astro-platform/
│
├── app/                                  # Legacy FastAPI monolithic application package [VERIFIED]
│   ├── api/                              # Route handlers & middleware
│   ├── core/                             # Config & logger
│   ├── db/                               # DB session & models
│   ├── models/                           # User, Profile, Blog, Activity models
│   ├── schemas/                          # Pydantic request/response schemas
│   ├── services/                         # Translation & business logic
│   ├── static/                           # Static assets (css/tokens.css, js/kundali.js, locales, svg)
│   ├── templates/                        # 16 Canonical Jinja2 templates (PROTECTED BASELINE SPECIFICATION)
│   └── main.py                           # Legacy FastAPI entrypoint
│
├── backend/                              # Modern Enterprise Modular Architecture [VERIFIED]
│   ├── gateway/                          # API Gateway & Edge Router
│   │   ├── main.py                       # Active FastAPI entrypoint (app = FastAPI(...))
│   │   ├── pages.py                      # HTML Template router (mounts app/templates)
│   │   ├── deps.py                       # Auth, DB, and Cache dependency injection
│   │   ├── settings.py                   # Pydantic v2 Gateway configuration
│   │   └── middleware/                   # Rate limit, Default-Deny, Language, Sessions
│   ├── modules/                          # 8 Domain-Driven Modular Services
│   │   ├── auth/                         # User & Admin authentication (PBKDF2)
│   │   ├── blog/                         # Astrological CMS & articles
│   │   ├── feedback/                     # User testing & feedback capture
│   │   ├── horoscope/                    # Transit-based daily/weekly horoscopes
│   │   ├── kundali/                      # Kundali D1, D9, Jaimini, Dashas, Saved Charts
│   │   ├── narrative/                    # LLM Astro-Narrative & SSE streaming jobs
│   │   ├── panchang/                     # Panchang, Choghadiya, Horas, Muhurat
│   │   └── prediction/                   # 10-Domain life prediction & Dasha-Transit timing
│   ├── shared/                           # High-precision mathematical libraries
│   │   ├── veda/                         # Parashari Graha Drishti, Yogas, Shadbala, Doshas
│   │   ├── ephemeris/                    # Swiss Ephemeris (`pyswisseph`) C-library wrapper
│   │   ├── cache/                        # Redis client with in-memory fail-open cache
│   │   ├── db/                           # SQLAlchemy engine & session factories
│   │   ├── timezone/                     # Geocoding, IANA timezones, DST calculation
│   │   ├── i18n/                         # 8-language translation dictionary engine
│   │   └── logging/                      # Structured JSON production logging
│   ├── tests/                            # 30+ test suites (810 passing pytest tests)
│   ├── alembic/                          # Database schema migration versions
│   └── scripts/                          # DB seeders & backup/restore utilities
│
├── frontend/                             # Existing static legacy frontend directory [VERIFIED]
│   ├── *.html                            # 16 Static HTML template snapshots
│   ├── js/                               # Static script bundle
│   ├── locales/                          # JSON locale files (en.json, hi.json, mr.json)
│   ├── svg/                              # SVG icons and zodiac glyphs
│   └── vercel.json                       # Static Vercel routing configuration
│
├── docs/                                 # Architectural specifications & audits [VERIFIED]
│   ├── project-audit/                    # Marriage engine & astrology audit reports
│   └── frontend-modernization/           # Phase 1 Planning Documents
│
└── requirements.txt                      # Python dependencies (swisseph, fastapi, sqlalchemy, etc.)
```

---

## 3. Runtime & Execution Architecture `[VERIFIED]`

### 3.1. Gateway & Server Bootstrap `[VERIFIED]`
- **Active Server Command:** `python -m uvicorn gateway.main:app --host 127.0.0.1 --port 8000` executed from `backend/`.
- **Mount Points:**
  - `BASE_DIR = Path(__file__).resolve().parent.parent / "app"`
  - Static files: `BASE_DIR / "static"` (resolves to `app/static/`).
  - Jinja2 templates: `BASE_DIR / "templates"` (resolves to `app/templates/`).
- **Middleware Pipeline Execution Order:**
  `DefaultDenyAuthMiddleware` $\to$ `LanguageDetectionMiddleware` $\to$ `RateLimitMiddleware` $\to$ `SessionMiddleware` $\to$ `CORSMiddleware`.

### 3.2. Authentication & Session Architecture `[VERIFIED]`
- **Session Engine:** Starlette's `SessionMiddleware` configured in `backend/gateway/main.py` lines 211–216:
  - Secret key: `settings.session_secret_key` (`"astrologic-session-secret-key-2026"`).
  - Cookie name: `session` (signed base64 string using `itsdangerous`).
  - Attributes: `SameSite="lax"`, `https_only=settings.is_production` (`False` in development, `True` in production), `Path="/"`, default expiration 14 days.
- **Session Keys:** `request.session["user_id"]` (integer), `request.session["admin"]` (`"true"`), `request.session["kundali_chart"]` (dict).
- **Default-Deny Policy (`DefaultDenyAuthMiddleware`):**
  - All `/api/*` endpoints strictly require `user_id` or `admin == "true"` in session, EXCEPT an explicit public prefix allowlist (`/health`, `/ready`, `/api/locales`, `/api/panchang`, `/api/festivals`, `/api/horoscope`, `/api/daily-horoscope`, `/api/cities`, `/api/system/ephemeris`, `/api/auth/login`, `/api/auth/signup`, `/api/auth/logout`, and public `GET /api/blogs`).
- **CSRF Protection Status `[VERIFIED]`:** No CSRF tokens or CSRF validation middleware currently exist in the FastAPI backend.
- **Decoupled Cross-Origin Problem `[VERIFIED]`:**
  When a Next.js development server runs on `http://localhost:3000` and requests `http://127.0.0.1:8000`, the browser treats them as different sites. Under `SameSite=Lax`, cookies are not forwarded on cross-site fetch calls, causing all protected `/api/*` calls to fail with `401 Unauthorized`.
- **BFF / Reverse-Proxy Solution `[PROPOSED]`:**
  A Next.js server-side API proxy (Backend-for-Frontend / BFF) is mandatory. The browser communicates solely with `http://localhost:3000/api/*` (same-origin). Next.js forwards session cookies server-to-server to FastAPI at `http://127.0.0.1:8000/api/*`, capturing and relaying `Set-Cookie` headers seamlessly.

---

## 4. Astrological Calculation Pipeline & Backend Ownership `[VERIFIED]`

### 4.1. Core Architectural Principle
**FastAPI is the sole authoritative computational astrology engine.** The Next.js frontend is strictly a presentation and interaction layer. The frontend must never calculate, estimate, or alter astronomical or astrological coordinates.

```
[User Input: Date, Time, City, Lat/Lon, Timezone]
                       │
                       ▼ (Transmitted via Next.js BFF Proxy)
    [FastAPI: modules/kundali/engine.py & shared/ephemeris]
                       │  Swiss Ephemeris (SE_SIDM_LAHIRI)
                       │  High-precision Julian Day calculation
                       ▼
    [D1 Rashi Chart & Exact Planetary Coordinates]
                       │
        ┌──────────────┼──────────────┬──────────────┐
        ▼              ▼              ▼              ▼
   [D9 Navamsha] [Chara Karakas] [Bhavabala &] [Vimshottari]
  (Dhanu Lagna)  (Jaimini Atma-   (Shadbala 6-   (Chronological
  (Gemini 7th)    karaka, UL)     fold potency)   MD-AD-PD tree)
        │              │              │              │
        └──────────────┼──────────────┴──────────────┘
                       │
                       ▼
  [shared/veda: 100+ Raj/Dhana Yogas, Graha Drishti, Dosha Detection]
                       │
                       ▼
  [modules/prediction: 10 Life Domains Evaluation & Dasha Timing]
                       │
                       ▼ (JSON Response with strict precision)
[Next.js Frontend: Declarative D3/SVG Rendering & Sacred Almanac Presentation]
```

### 4.2. Reference Benchmark Verification `[VERIFIED]`
- **Input Data:** November 2, 2004, 16:15 IST, Aurangabad, Maharashtra ($19.8762^\circ\text{N}, 75.3433^\circ\text{E}$).
- **Ascendant (Lagna):** Pisces (Meena) at $17^\circ 12' 41"$.
- **D9 Navamsha Lagna:** Sagittarius (Dhanu); D9 7th House: Gemini (Mithuna) with Rahu.
- **Upapada Lagna (UL):** Sagittarius (Dhanu) in House 10 from Lagna.
- **Debilitation/Cancellation:** Venus debilitated in Virgo; Neecha Bhanga confirmed via Jupiter Kendra (House 7); NBRY not established.
- **Active Dasha (Late 2026):** Saturn Mahadasha – Saturn Antardasha – Mercury Pratyantardasha.

---

## 5. Multilingual (i18n) Architecture & Audit `[VERIFIED]`

Multilingual support is a foundational requirement, not a post-launch add-on.

### 5.1. Existing Codebase Audit `[VERIFIED]`
1. **Configured Languages:** `SUPPORTED_LANGUAGES` in `backend/shared/i18n/translation.py`:
   - `en` (English), `hi` (Hindi), `mr` (Marathi), `bn` (Bengali), `gu` (Gujarati), `kn` (Kannada), `ta` (Tamil), `te` (Telugu).
2. **Existing Locale Dictionaries:**
   - `app/static/locales/en.json`: 10 keys (navbar labels).
   - `app/static/locales/hi.json`: 10 keys (navbar labels).
   - `app/static/locales/mr.json`: 52 keys (extended navbar, brand, prediction labels).
   - `frontend/locales/`: identical 10-key baseline for `en`, `hi`, `mr`.
3. **Backend Middleware:** `LanguageDetectionMiddleware` evaluates 5 priority levels:
   URL path prefix (`/{lang}/...`) $\to$ Query param (`?lang=...`) $\to$ Cookie (`lang=...`) $\to$ `Accept-Language` header $\to$ Fallback (`en`).
4. **User Model Integration:** `User.preferred_language = Column(String(10), default="en")` in `modules/auth/models.py`.

### 5.2. Proposed Initial Launch Language Strategy `[PROPOSED]`
- **Primary:** English (`en`).
- **High Priority Tier-1:** Hindi (`hi`) and Marathi (`mr`).
- **Specialized Astrological Vocabulary:** Sanskrit (`sa`) terminology preserved across all languages for technical authenticity.
- **Future Expansion:** Gujarati (`gu`), Bengali (`bn`), Tamil (`ta`), Telugu (`te`), Kannada (`kn`).
- **Framework Adoption:** **`next-intl`** with locale-prefixed App Router paths (`/[locale]/kundali`, `/[locale]/panchang`, etc.).

---

## 6. Legacy Frontend Directory Assessment `[VERIFIED]`

- **Location:** `astro-platform/frontend/`
- **Contents:** 16 HTML files, `js/`, `locales/`, `svg/`, and `vercel.json`.
- **Usage Status:** Standalone static export snapshot. **Not mounted or executed by FastAPI.**
- **Safe Preservation Requirement:** Under no circumstances will `frontend/` be deleted or overwritten in Phase 1. When Phase 2 begins, it will be safely cloned into `frontend-legacy/` with full SHA-256 hash verification.

---

## 7. Phase 1 Verification Summary

| Discovery Area | Status | Evidence / Source |
| :--- | :--- | :--- |
| Gateway & Server Bootstrap | `[VERIFIED]` | `backend/gateway/main.py:app` |
| Jinja2 Templates Baseline | `[VERIFIED]` | `app/templates/` (16 HTML files, 0 modified) |
| Session Authentication & Default-Deny | `[VERIFIED]` | `backend/gateway/main.py:40-86` & `modules/auth/api.py` |
| Lack of Backend CSRF Protection | `[VERIFIED]` | Codebase grep confirms zero CSRF middleware |
| Cross-Origin Session Block Risk | `[VERIFIED]` | `SameSite=Lax` cookie across localhost:3000 and 127.0.0.1:8000 |
| Swiss Ephemeris Lahiri Engine | `[VERIFIED]` | `backend/shared/ephemeris/wrapper.py` |
| Authoritative D9 / UL Coordinates | `[VERIFIED]` | `backend/tests/test_marriage_engine_regression.py` |
| Existing i18n Locales (en, hi, mr) | `[VERIFIED]` | `app/static/locales/` & `backend/shared/i18n/` |
| Backend Astrological Ownership | `[VERIFIED]` | All math localized in `backend/shared/veda/` |
| Legacy Frontend Non-Active Status | `[VERIFIED]` | FastAPI loads from `app/`, not `frontend/` |
