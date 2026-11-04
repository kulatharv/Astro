# 05 — Target Frontend Architecture, BFF Proxy & Multilingual Specification

**Project:** AstroLogic AI / Nakshatra Labs — Modern Frontend Migration  
**Document:** `docs/frontend-modernization/05_FRONTEND_ARCHITECTURE.md`  
**Phase:** Phase 1 – Discovery, Architecture Assessment & Implementation Planning  
**Status:** AUDITED & FINALIZED (Verification Standard Enforced)  
**Date:** October 31, 2026  
**Auditor:** Senior Software Architect, Security Engineer & Migration Specialist  

---

## 1. Architectural Foundations & Principles `[PROPOSED]`

The target frontend for AstroLogic AI will be built using **Next.js 15+ (App Router)** with **TypeScript**, **React 19**, and **Tailwind CSS**. The architecture is structured around five core principles:

1. **Strict Calculation Ownership `[VERIFIED]`:**
   FastAPI remains the sole calculation engine. The frontend captures input, dispatches requests, and presents returned coordinates without independent astronomical math.
2. **Same-Origin Backend-for-Frontend (BFF) Proxy `[PROPOSED]`:**
   Eliminates cross-origin cookie omission by terminating client requests at `http://localhost:3000` and proxying them server-to-server to `http://127.0.0.1:8000`, relaying `Set-Cookie` headers directly.
3. **Foundational Multilingual Architecture (`next-intl`) `[PROPOSED]`:**
   Locale-prefixed routing (`/[locale]/...`) supporting English (`en`), Hindi (`hi`), and Marathi (`mr`) from day one, with Sanskrit (`sa`) terminology preservation and future expansion readiness.
4. **Sacred Almanac Design System (Ivory & Kumkum) `[PROPOSED]`:**
   Authentic Vedic temple manuscript aesthetic with high-contrast typography, WCAG 2.2 AAA readability, and zero text clipping in Devanagari scripts.
5. **Hybrid Server/Client Rendering (RSC Strategy) `[PROPOSED]`:**
   Server Components for SEO and fast initial paint; Client Components strictly for interactive SVG charts, 3D globes, and real-time timers.

---

## 2. Next.js BFF Proxy & Session Integration Architecture `[PROPOSED]`

### 2.1. Request Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    Browser Client                           │
│               Origin: http://localhost:3000                 │
└──────────────────────────────┬──────────────────────────────┘
                               │ 1. Same-Origin HTTP Request
                               │    Cookie: session=... (Ambient)
                               ▼
┌─────────────────────────────────────────────────────────────┐
│           Next.js App Router (BFF Layer)                    │
│             `app/api/[...proxy]/route.ts`                   │
│                                                             │
│ - Validates `X-Requested-With` or CSRF header.              │
│ - Forwards incoming `Cookie` header server-to-server.       │
│ - Imposes a strict 10s timeout on calculation endpoints.    │
└──────────────────────────────┬──────────────────────────────┘
                               │ 2. Server-to-Server Request
                               │    Cookie: session=...
                               ▼
┌─────────────────────────────────────────────────────────────┐
│              FastAPI Gateway (:8000)                        │
│ 1. Validates signed session signature (itsdangerous).       │
│ 2. DefaultDenyAuthMiddleware authorizes request.            │
│ 3. Executes Swiss Ephemeris calculation.                    │
│ 4. Emits `Set-Cookie: session=...` on login/logout.         │
└──────────────────────────────┬──────────────────────────────┘
                               │ 3. Server-to-Server Response
                               │    Set-Cookie: session=...
                               ▼
┌─────────────────────────────────────────────────────────────┐
│           Next.js App Router (BFF Layer)                    │
│ - Captures backend `Set-Cookie` header.                     │
│ - Relays `Set-Cookie` back to the browser on :3000.         │
└──────────────────────────────┬──────────────────────────────┘
                               │ 4. Same-Origin Response
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                    Browser Client                           │
│ (Session cookie persists seamlessly on localhost:3000)      │
└─────────────────────────────────────────────────────────────┘
```

### 2.2. Server vs Client API Consumption
- **Server Components (RSC):**
  Read cookies via `next/headers`:
  ```typescript
  import { cookies } from 'next/headers';
  const cookieStore = await cookies();
  const res = await fetch('http://127.0.0.1:8000/api/kundali/saved-charts', {
    headers: { Cookie: cookieStore.toString() }
  });
  ```
- **Client Components (`'use client'`):**
  Dispatch calls via standard same-origin `fetch('/api/kundali/saved-charts')`. The Next.js BFF route handler intercepts the call, attaches credentials, and forwards to FastAPI.

---

## 3. Multilingual (i18n) Architecture `[PROPOSED]`

### 3.1. Routing & Internationalization Framework
- **Selected Engine:** **`next-intl`** for Next.js App Router.
- **Routing Pattern:** Locale-prefixed paths with fallback detection:
  - English: `/en/kundali`, `/en/panchang`, `/en/predictions`
  - Hindi: `/hi/kundali`, `/hi/panchang`, `/hi/predictions`
  - Marathi: `/mr/kundali`, `/mr/panchang`, `/mr/predictions`
- **Supported Languages Configuration (`i18n.ts`):**
  ```typescript
  export const locales = ['en', 'hi', 'mr'] as const;
  export const defaultLocale = 'en' as const;
  ```
- **Language Detection Priority:**
  1. URL path prefix (`/[locale]/...`).
  2. Persistent cookie (`lang=hi`).
  3. Authenticated user profile preference (`User.preferred_language`).
  4. Browser `Accept-Language` header.
  5. Default fallback (`en`).
- **Deep-Link Preservation:**
  Switching languages on `/hi/predictions/marriage` will navigate directly to `/en/predictions/marriage` or `/mr/predictions/marriage`, maintaining exact active tab, chart ID, and query parameters.

### 3.2. Translation Key Structure (`frontend/messages/`)
Translation files are organized by functional domain to prevent file bloat:
```
frontend/messages/
├── en.json
├── hi.json
└── mr.json
```
Example domain structure within `en.json`:
```json
{
  "common": {
    "loading": "Calculating celestial coordinates...",
    "save": "Save Chart",
    "error": "An error occurred while computing the chart."
  },
  "navigation": {
    "home": "Home",
    "kundali": "Kundali",
    "panchang": "Panchang",
    "predictions": "Predictions",
    "horoscope": "Horoscope",
    "library": "Knowledge Library"
  },
  "kundali": {
    "birth_details": "Birth Details",
    "generate_chart": "Generate Kundali",
    "rashi_chart": "Lagna (D1) Chart",
    "navamsha_chart": "Navamsha (D9) Chart",
    "dasha_timeline": "Vimshottari Dasha Timeline"
  },
  "panchang": {
    "tithi": "Tithi",
    "nakshatra": "Nakshatra",
    "yoga": "Yoga",
    "karana": "Karana",
    "vara": "Vara",
    "choghadiya": "Live Choghadiya"
  }
}
```

### 3.3. Devanagari & Indian Language Typography Standards
To prevent clipped matras, overlapping conjuncts, and broken glyphs in Hindi and Marathi:
- **Font Stack:** `'Noto Serif Devanagari', 'Cormorant Garamond', Georgia, serif`.
- **Line-Height Standard:** Relaxed `line-height: 1.7` applied across all Devanagari text containers (compared to `1.5` for English).
- **Word Wrapping:** `word-break: keep-all; overflow-wrap: break-word;` to respect Sanskrit compound terms.

---

## 4. Sacred Almanac Design System (Ivory & Kumkum) `[PROPOSED]`

### 4.1. Master Color Tokens (WCAG 2.2 AAA Compliant)

```css
:root {
  /* ── Background & Parchment Surfaces ── */
  --almanac-ivory: #FAF3E7;         /* Primary Background: Sacred reflective parchment */
  --almanac-parchment: #F7EBD7;     /* Secondary Surface: Elevated cards, sidebars */
  --almanac-surface-dim: #F0DFC4;   /* Recessed Surface: Form input fields, inactive tabs */
  --almanac-surface-hover: #FDF9F2; /* Card Hover State */

  /* ── Sacred Kumkum & Terracotta Accents ── */
  --sacred-kumkum: #791412;         /* Primary Brand: Vermilion CTAs, major headers */
  --kumkum-hover: #630F0D;          /* Button Hover State */
  --terracotta-brick: #943F28;      /* Secondary Accent: Sub-headers, badges */
  --terracotta-dim: rgba(148, 63, 40, 0.12); /* Subtle pill backdrops */

  /* ── Temple Gold & Auspicious Ochre ── */
  --temple-gold-light: #EFC792;     /* Subtle Borders: Card outlines, divider lines */
  --temple-gold-border: rgba(220, 153, 85, 0.45); /* Card borders */
  --ochre-gold: #DC9955;            /* Auspicious Accents: Active tabs, stars */

  /* ── Typography & Contrast Standards ── */
  --text-primary-maharani: #58170C; /* Deep Maroon / Maharan: Main headers (>8:1 ratio) */
  --text-charcoal-bhasma: #30221A;  /* Charcoal Bhasma: Body text, tables (>10:1 ratio) */
  --text-muted: #6E5B51;            /* Subtitles, secondary metadata */
  --text-on-kumkum: #FAF3E7;        /* White-ivory text on primary red CTA buttons */

  /* ── Astrological Indicators ── */
  --shubh-green: #2D6A4F;           /* Auspicious Choghadiya, Benefic Planets */
  --shubh-bg: rgba(45, 106, 79, 0.10);
  --ashubh-red: #A4161A;            /* Inauspicious Kaal, Malefic Afflictions */
  --ashubh-bg: rgba(164, 22, 26, 0.10);
  --neutral-blue: #1D4E89;          /* Neutral Chal Choghadiya */
}
```

---

## 5. Component Tree & Directory Structure `[PROPOSED]`

```
frontend/
├── app/                                  # Next.js App Router root
│   ├── [locale]/                         # Locale-prefixed dynamic route segment
│   │   ├── layout.tsx                    # Locale layout (next-intl provider, fonts, navbar)
│   │   ├── page.tsx                      # Homepage & Celestial Portal
│   │   ├── (auth)/                       # Route Group: Authentication
│   │   │   ├── login/page.tsx            # Login screen
│   │   │   └── signup/page.tsx           # Signup screen
│   │   ├── (dashboard)/                  # Route Group: Authenticated Portal
│   │   │   ├── profile/page.tsx          # User Profile & Preferences
│   │   │   ├── saved-charts/page.tsx     # Saved Charts CRUD Manager
│   │   │   └── activity/page.tsx         # User Activity Audit Trail
│   │   ├── kundali/                      # Kundali Generator & Explorer
│   │   │   ├── page.tsx                  # Birth Input & Chart View
│   │   │   └── [id]/divisional/page.tsx  # D2 to D60 Divisional Charts
│   │   ├── predictions/                  # 10-Domain Predictions
│   │   │   ├── page.tsx                  # 10-Domain Overview & Vitality Grid
│   │   │   └── [domain]/page.tsx         # Specific Domain Deep Dive
│   │   ├── panchang/                     # Daily Panchang
│   │   │   ├── page.tsx                  # 5 Limbs, Choghadiya, Horas
│   │   │   └── personalized/page.tsx     # Tara Bala / Chandra Bala Advisor
│   │   ├── horoscope/                    # Transit Horoscopes
│   │   │   ├── page.tsx                  # 12-Zodiac Transit Hub
│   │   │   └── [sign]/page.tsx           # Sign-Specific Forecast
│   │   ├── library/                      # Astrology Knowledge Library
│   │   │   ├── page.tsx                  # Article Catalog
│   │   │   └── [slug]/page.tsx           # Article Reader
│   │   ├── about/page.tsx                # Ephemeris Accuracy & Ethics
│   │   └── admin/                        # Admin Portal
│   │       ├── login/page.tsx            # Admin Sign-in
│   │       ├── blogs/page.tsx            # Blog CMS
│   │       ├── users/page.tsx            # User Directory
│   │       └── cache/page.tsx            # Cache Telemetry & Flush
│   └── api/                              # Next.js BFF Proxy Route Handlers
│       └── [...proxy]/route.ts           # Server-side proxy forwarding to FastAPI
│
├── components/                           # Feature-organized component tree
│   ├── ui/                               # Atomic primitives (shadcn/ui tailored to Sacred Almanac)
│   ├── layout/                           # Navbar, Footer, MobileNav, LanguagePicker
│   ├── kundali/                          # KundaliChart (SVG), PlanetaryTable, DashaTimeline
│   ├── panchang/                         # ChoghadiyaTable, HoraTable, DecisionAdvisor
│   ├── predictions/                      # VitalityMeter, TimingWindows, RemediesCard
│   ├── celestials/                       # CelestialGlobe (Three.js / R3F)
│   └── ai/                               # AstroAIChatDrawer, AstroNarrativeStream
│
├── hooks/                                # Custom React hooks
│   ├── useKundali.ts, usePanchang.ts, useSavedCharts.ts, useCitySearch.ts
│
├── stores/                               # Lightweight client UI state (Zustand)
│   ├── useChartStore.ts, usePreferencesStore.ts
│
├── lib/                                  # Utilities & API client
│   ├── api-client.ts                     # Centralized typed fetch client
│   ├── astrological-constants.ts         # Signs, Nakshatras, Planets, Glyphs
│   └── utils.ts                          # Classnames helper (clsx + tailwind-merge)
│
├── messages/                             # next-intl translation dictionaries
│   ├── en.json, hi.json, mr.json
│
└── types/                                # Strict TypeScript contracts mirroring Pydantic schemas
    ├── kundali.ts, prediction.ts, panchang.ts, auth.ts
```

---

## 6. State Management Boundaries `[PROPOSED]`

To avoid state duplication, strict boundaries are enforced:
1. **Server / API State (TanStack Query v5):**
   - Owns all data retrieved from FastAPI (`kundali`, `panchang`, `predictions`, `saved-charts`, `cities`).
   - Handles background refetching, retry logic, and memory caching (`staleTime: 30 minutes`).
2. **Client UI State (Zustand v5):**
   - Restricted to transient UI states: active chart style (`north` vs `south`), active prediction tab (1 to 10), and modal drawer visibility.
   - **Never duplicates server calculation payloads.**
3. **Form State (React Hook Form + Zod):**
   - Manages birth data input fields and validates numeric ranges before dispatching requests.
4. **Local State (`useState` / `useReducer`):**
   - Component-level interactions (hover states, dropdown menus, tab selections).
