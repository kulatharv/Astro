# 07 — Phased Implementation Roadmap & Quality Gate Criteria

**Project:** AstroLogic AI / Nakshatra Labs — Modern Frontend Migration  
**Document:** `docs/frontend-modernization/07_IMPLEMENTATION_ROADMAP.md`  
**Phase:** Phase 1 – Discovery, Architecture Assessment & Implementation Planning  
**Status:** AUDITED & FINALIZED (Verification Standard Enforced)  
**Date:** October 31, 2026  
**Auditor:** Senior Software Architect, Security Engineer & Migration Specialist  

---

## 1. Roadmap Architecture & Phased Milestones

The AstroLogic frontend modernization is organized into **eight strictly sequential phases**. Each phase specifies concrete objectives, deliverables, dependencies, API interactions, testing gates, and explicit out-of-scope boundaries.

Execution halts at Phase 1. Subsequent phases require explicit user authorization.

```
[Phase 1: Discovery & Documentation Audit] (COMPLETE - CURRENT)
                     │
                     ▼ (Requires Explicit Approval)
[Phase 2: Safe Migration, Next.js Foundation & Multilingual Infrastructure]
                     │
                     ▼
[Phase 3: Homepage & Vedic Kundali Engine (D1, D9, Dasha Tree, SVG Charts)]
                     │
                     ▼
[Phase 4: Daily Panchang, Live Choghadiya & Muhurat Decision Engine]
                     │
                     ▼
[Phase 5: 10-Domain Life Predictions & Dasha-Transit Timing Windows]
                     │
                     ▼
[Phase 6: Daily Horoscope, Knowledge Library & User Dashboard / Saved Charts]
                     │
                     ▼
[Phase 7: Admin Portal, Article CMS & Cache Telemetry]
                     │
                     ▼
[Phase 8: End-to-End Testing, Accessibility Audit & Production Polish]
```

---

## 2. Phase-by-Phase Execution Specifications

---

### Phase 1 — Discovery, Architecture Planning & Documentation Audit
- **Status:** **COMPLETE (Current Phase)**.
- **Objective:** Exhaustive technical discovery, code inspection, defect identification, and preparation of all nine architecture planning documents.
- **Deliverables:** Complete verification of `app/templates/`, `backend/`, and `frontend/`; 9 finalized Markdown documents in `docs/frontend-modernization/`.
- **Completion Criteria:** All 9 planning documents audited, corrected, and verified against actual codebase; Phase 1 readiness report issued.
- **Out of Scope:** Implementation of code, initialization of Next.js, modifying templates, modifying database schemas.

---

### Phase 2 — Safe Migration, Next.js Foundation & Multilingual Infrastructure
- **Objective:** Establish the clean Next.js 15+ App Router application under `frontend/` after securely archiving legacy files, configure the Sacred Almanac design system, implement the same-origin BFF proxy, and deploy the multilingual foundation.
- **Scope:**
  1. *Git & Backup Verification:* Check `git status`, confirm untracked files, and create a clean git checkpoint commit.
  2. *Legacy Archival:* Clone `frontend/` $\to$ `frontend-legacy/` with recursive SHA-256 integrity verification.
  3. *Next.js Scaffolding:* Initialize clean Next.js 15+ App Router in `frontend/` with TypeScript and Tailwind CSS v4.
  4. *Design System Tokens:* Configure Sacred Almanac CSS variables (`--almanac-ivory`, `--sacred-kumkum`, etc.) and typography (Cormorant Garamond, Inter, Noto Serif Devanagari).
  5. *Multilingual Foundation:* Install and configure `next-intl` with locale-prefixed routing (`/[locale]/...`), domain message files (`messages/en.json`, `hi.json`, `mr.json`), and deep-link-preserving language switcher.
  6. *Same-Origin BFF Proxy:* Deploy `app/api/[...proxy]/route.ts` to proxy all client calls to FastAPI (`127.0.0.1:8000`), relaying session cookies seamlessly.
  7. *API Client Foundation:* Centralized typed client (`lib/api-client.ts`) with timeout policy, error normalization, and non-idempotent retry guards.
  8. *Global Layout Shell:* Deploy responsive Navbar, Footer, MobileNav, and Accessibility Skip Link.
- **Dependencies:** Approved Phase 1 documentation; Node.js 18+; running FastAPI gateway on `127.0.0.1:8000`.
- **Files Likely Created:**
  - `frontend/app/[locale]/layout.tsx`, `page.tsx`
  - `frontend/app/api/[...proxy]/route.ts`
  - `frontend/components/layout/Navbar.tsx`, `Footer.tsx`, `LanguagePicker.tsx`
  - `frontend/lib/api-client.ts`, `utils.ts`
  - `frontend/messages/en.json`, `hi.json`, `mr.json`
  - `frontend/i18n.ts`, `middleware.ts`
- **API Dependencies:** `GET /health`, `GET /api/system/ephemeris`, `GET /api/locales/{lang}`.
- **Risks:** Cookie relay failure between BFF and FastAPI; font rendering defects in Devanagari.
- **Testing Requirements:**
  - Unit tests verifying BFF proxy header forwarding and cookie capture.
  - Language switcher test verifying route preservation across `/en`, `/hi`, `/mr`.
  - Clean production build test (`npm run build`).
- **Completion Criteria:**
  - Next.js boots on `http://localhost:3000` with Sacred Almanac styling.
  - BFF proxy successfully connects to FastAPI `GET /health` and forwards session cookies.
  - Language picker switches between English, Hindi, and Marathi with zero layout shifts.
- **Explicit Out of Scope:** Building complete astrological modules (Kundali, Panchang, Predictions) is strictly deferred to subsequent phases.

---

### Phase 3 — Homepage & Vedic Kundali Experience
- **Objective:** Deliver the interactive homepage and the full Vedic Horoscope calculation interface with declarative D1 and D9 SVG chart renderers.
- **Scope:**
  - Homepage hero section, live cosmic ticker (`GET /api/panchang`), and feature showcase.
  - Accessible birth input form with React Hook Form + Zod schema validation.
  - Debounced city search autocomplete connected to `GET /api/cities`.
  - Declarative SVG Kundali component (`KundaliChart.tsx`) supporting North Indian (Diamond) and South Indian (Square) styles with house zoom and hover states.
  - Authoritative D9 Navamsha renderer verified for benchmark chart (Dhanu Lagna, Gemini 7th).
  - Comprehensive Planetary Coordinate Table with dignity badges (Exalted, Debilitated, Vargottama, Combust, Retrograde).
  - Interactive Vimshottari Dasha tree accordion (Mahadasha $\to$ Antardasha $\to$ Pratyantardasha).
  - PDF report download button triggering `GET /api/download-kundali`.
  - Contextual AstroAI Chat drawer (`POST /api/kundali-chat`).
- **Dependencies:** Phase 2 foundation.
- **API Dependencies:** `GET /api/cities`, `POST /api/kundali`, `GET /api/download-kundali`, `POST /api/kundali-chat`.
- **Testing Requirements:**
  - Benchmark chart calculation test verifying exact parity with backend outputs.
  - SVG node alignment test across viewport widths (320px, 768px, 1440px).
- **Completion Criteria:**
  - User can enter birth data, generate chart, switch North/South styles, view D1/D9, inspect dasha tree, and download PDF.
- **Explicit Out of Scope:** 10-domain life predictions and daily panchang decision engine.

---

### Phase 4 — Daily Panchang, Live Choghadiya & Muhurat Engine
- **Objective:** Implement the real-time Hindu astronomical almanac, live Choghadiya countdowns, planetary Horas, and the Vedic Decision Engine.
- **Scope:**
  - 5 Limbs display: Tithi, Nakshatra, Yoga, Karana, Vara with exact end-times.
  - Live Choghadiya component with real-time countdown timer to the next transition and Day/Night mode toggles.
  - Auspicious/Inauspicious Kaal indicator cards (Rahu Kaal, Yamaghanta, Abhijit Muhurat).
  - Interactive Vedic Decision Advisor form submitting to `POST /api/panchang/decision`.
  - Upcoming Festivals feed drawer (`GET /api/festivals/upcoming`).
  - iCal `.ics` download and social share image modal (`GET /api/panchang/share-image`).
- **Dependencies:** Phase 2 foundation.
- **API Dependencies:** `POST /api/panchang`, `POST /api/panchang/decision`, `GET /api/festivals/upcoming`, `GET /api/panchang/calendar.ics`, `GET /api/panchang/share-image`.
- **Testing Requirements:**
  - Real-time timer accuracy test across system sleep/wake events.
  - City/date switcher query cache invalidation test.
- **Completion Criteria:**
  - Real-time Choghadiya countdown updates second-by-second on client.
  - Decision engine returns personalized feasibility score and traditional guidance.

---

### Phase 5 — 10-Domain Predictions & Dasha-Transit Timing Engine
- **Objective:** Modernize the multi-domain life prediction interface, vitality score meters, astrological evidence drawers, and Dasha-Transit event windows.
- **Scope:**
  - 10-Domain Overview Grid displaying vitality scores (0–100) with animated radial gauges.
  - Detailed domain panels for Career, Marriage, Wealth, Health, Children, Education, Property, Challenges, Travel, and Spirituality.
  - Astrological Evidence inspector: Influencing houses, lord placements, and Shadbala potency.
  - Dasha-Transit Timing Windows component highlighting concrete favorable calendar intervals.
  - Vedic Remedial Measures card: Prescribed gemstones, Beej mantras with Devanagari script, charitable acts, and fasting rituals.
  - AI Astro-Narrative streaming integration using Server-Sent Events (`/api/narrative/{job_id}/stream`).
- **Dependencies:** Phase 2 foundation and Phase 3 birth chart state.
- **API Dependencies:** `POST /api/domains`, `POST /api/prediction/timing/{domain}`, `GET /api/narrative/{job_id}/stream`.
- **Testing Requirements:**
  - SSE stream buffer and reconnection resilience test.
  - 10-domain layout rendering test across all supported screen sizes.
- **Completion Criteria:**
  - All 10 domains render returned vitality scores, evidence arrays, and timing windows.
  - SSE streaming displays live token-by-token typing animation.

---

### Phase 6 — Daily Horoscope, Knowledge Library & User Dashboard
- **Objective:** Implement 12-sign transit horoscopes, the astrology blog library, user account management, and saved chart persistence.
- **Scope:**
  - 12-zodiac scrollbar and daily transit forecasts (`GET /api/horoscope/{sign_idx}`).
  - Article directory with category filtering, search, and reading view (`/library/[slug]`).
  - User profile editor (`/profile`) and security settings.
  - Saved Charts Manager (`/saved-charts`): Full CRUD table with ownership check, loading charts directly into the Kundali viewer with one click.
  - User activity audit trail feed (`/activity`).
- **Dependencies:** Phase 2 auth foundation.
- **API Dependencies:** `GET /api/horoscope/{sign_idx}`, `GET /api/blogs`, `GET/POST /api/kundali/saved-charts`.
- **Testing Requirements:**
  - CRUD lifecycle testing for saved charts (create, list, update, delete).
  - Unauthenticated access redirect test.
- **Completion Criteria:**
  - Authenticated user can save, edit, and delete birth charts with immediate optimistic UI updates.

---

### Phase 7 — Administration & CMS Authoring
- **Objective:** Implement protected administration screens for article authoring, user directories, system telemetry, and cache flushing.
- **Scope:**
  - Admin login screen (`/admin/login`) with role validation.
  - Article Markdown CMS editor with live preview (`/admin/blogs`).
  - Registered users directory table with role inspection (`/admin/users`).
  - Cache telemetry dashboard displaying hit/miss ratios and one-click flush controller (`/admin/cache`).
- **Dependencies:** Phase 2 auth foundation.
- **API Dependencies:** `POST /admin/login`, `GET/POST /api/blogs`, `GET /api/admin/cache/stats`, `POST /api/admin/cache/flush`.
- **Testing Requirements:**
  - Strict role-based authorization test (`403 Forbidden` for standard users).
  - Cache flush roundtrip verification test.
- **Completion Criteria:**
  - Admin users can manage blogs, review user counts, and monitor/flush caches.

---

### Phase 8 — Testing, Accessibility Audit & Production Polish
- **Objective:** Comprehensive automated end-to-end testing, accessibility audit, Lighthouse performance optimization, and production build readiness.
- **Scope:**
  - Playwright E2E test suite covering: Birth input $\to$ Kundali generation $\to$ D1/D9 chart inspection $\to$ PDF download $\to$ Panchang viewing.
  - Lighthouse audit achieving 95+ scores across Performance, Accessibility (WCAG 2.2 AA), Best Practices, and SEO.
  - Bundle size optimization (lazy loading Three.js, tree-shaking ECharts, optimizing web fonts).
  - Production build verification (`npm run build`).
- **Completion Criteria:**
  - 100% of automated Playwright test scenarios pass.
  - Zero console warnings or hydration errors in production build.
