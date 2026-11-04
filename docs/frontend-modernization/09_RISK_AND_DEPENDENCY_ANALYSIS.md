# 09 — Comprehensive Risk Register, Security Audit & Mitigation Framework

**Project:** AstroLogic AI / Nakshatra Labs — Modern Frontend Migration  
**Document:** `docs/frontend-modernization/09_RISK_AND_DEPENDENCY_ANALYSIS.md`  
**Phase:** Phase 1 – Discovery, Architecture Assessment & Implementation Planning  
**Status:** AUDITED & FINALIZED (Verification Standard Enforced)  
**Date:** October 31, 2026  
**Auditor:** Senior Software Architect, Security Engineer & Migration Specialist  

---

## 1. Executive Summary

Transitioning an enterprise Vedic computational platform to a decoupled Next.js architecture introduces specific technical, security, architectural, and mathematical risks. 

This document identifies each potential risk vector, evaluates its likelihood and impact, and details concrete, proven mitigation strategies to guarantee zero regression, complete security, and high computational fidelity.

---

## 2. Comprehensive Risk Register & Mitigation Matrix

---

### Risk 1: Cross-Origin Session Cookie Block (CORS & SameSite=Lax) `[VERIFIED RISK]`
- **Category:** Application Security & Architecture
- **Description:**
  FastAPI relies on Starlette's `SessionMiddleware` setting signed cookies with `SameSite=Lax`. When the Next.js development server runs on `http://localhost:3000` and dispatches browser `fetch` requests directly to `http://127.0.0.1:8000`, browsers treat them as different sites. Under `SameSite=Lax`, cookies are **omitted from cross-site asynchronous fetch requests**, causing all protected `/api/*` endpoints to fail with `401 Unauthorized`.
- **Likelihood:** High | **Impact:** Critical (Completely blocks authenticated user journeys).
- **Mitigation Strategy `[PROPOSED]`:**
  Deploy a same-origin **Next.js Backend-for-Frontend (BFF) proxy** (`app/api/[...proxy]/route.ts`). All browser requests target `http://localhost:3000/api/*` (same-origin). Next.js forwards session cookies server-to-server to FastAPI (`127.0.0.1:8000`), capturing and relaying `Set-Cookie` headers back to the browser.

---

### Risk 2: Absence of CSRF Protection in Backend API `[VERIFIED RISK]`
- **Category:** Application Security
- **Description:**
  Code audit confirms that FastAPI currently contains zero CSRF middleware or anti-forgery tokens. If ambient cookie credentials are used directly by browser clients, mutating requests (`POST /api/kundali/saved-charts`, `POST /api/feedback`, `POST /profile`) could be vulnerable to cross-site request forgery.
- **Likelihood:** Medium | **Impact:** High.
- **Mitigation Strategy `[PROPOSED]`:**
  Implement CSRF defense-in-depth at the Next.js BFF proxy layer. The BFF proxy validates a custom request header (e.g. `X-Requested-With: AstroLogicClient`) or double-submit CSRF cookie before forwarding mutating requests to FastAPI. Requests lacking this header are rejected at the edge with `403 Forbidden`.

---

### Risk 3: Date, Timezone & Geocoding Discrepancies `[VERIFIED RISK]`
- **Category:** Astrological Calculation Fidelity
- **Description:**
  JavaScript's native `Date` object evaluates dates in the browser's local timezone. If a user in New York enters a birth date for someone born in India (IST, UTC+5:30), naive `Date` parsing can shift the day or hour, corrupting Julian Day and Ascendant degree calculations.
- **Likelihood:** High | **Impact:** Critical (Produces completely incorrect astrological charts).
- **Mitigation Strategy `[VERIFIED]`:**
  1. *Zero Browser Local Date Math:* Prohibit `new Date(year, month, day)` in calculation contexts.
  2. *Pure Integer Component Transmission:* The form transmits strict integers (`{year: 2004, month: 11, day: 2, hour: 16, minute: 15, second: 0, city: "Aurangabad"}`).
  3. *Authoritative Server-Side Geocoding:* The FastAPI backend (`shared/timezone/tz.py`) handles all IANA timezone resolution, historical DST offsets, and Julian Day conversions via Swiss Ephemeris (`pyswisseph`), ensuring absolute astronomical precision.

---

### Risk 4: Planetary Overcrowding & Visual Collision in SVG Kundali Charts `[PROPOSED RISK]`
- **Category:** UI / Data Visualization
- **Description:**
  In Vedic astrology, planetary conjunctions often place 3, 4, or 5 planets in a single house (Stelliums). In fixed SVG polygonal slots, text labels can overlap and become unreadable, especially on mobile viewports (<360px).
- **Likelihood:** High | **Impact:** Medium (Degrades usability and visual prestige).
- **Mitigation Strategy `[PROPOSED]`:**
  1. *Dynamic Sub-Layout Algorithm:* Implement an automatic sub-layout algorithm within each house polygon that calculates rows/columns dynamically based on occupying planet count.
  2. *Interactive House Zoom:* Clicking or tapping any house expands it into a focused modal sheet displaying high-resolution planetary degrees, nakshatras, padas, and karakas.
  3. *Standardized Short Glyphs:* Use compact notation (`Su`, `Mo`, `Ma`, `Me`, `Ju`, `Ve`, `Sa`, `Ra`, `Ke`, `La`) with color-coded dignity dots (gold for exalted, red for debilitated) and rich popover tooltips on hover.

---

### Risk 5: Multilingual Font Rendering & Devanagari Matra Clipping `[VERIFIED RISK]`
- **Category:** Internationalization & Typography
- **Description:**
  Hindi and Marathi Devanagari scripts contain ascending and descending diacritics (matras) and complex conjunct characters (samyuktaksharas). Standard line heights (1.4–1.5) often cause upper and lower matras to be clipped by container boundaries.
- **Likelihood:** High | **Impact:** Medium (Aesthetic degradation and unreadable Sanskrit terms).
- **Mitigation Strategy `[PROPOSED]`:**
  1. *Typography Standard:* Deploy Google Font `Noto Serif Devanagari` paired with `Cormorant Garamond`.
  2. *Line-Height Standard:* Enforce relaxed `line-height: 1.7` across all Devanagari text blocks.
  3. *Text Wrapping:* Apply `word-break: keep-all; overflow-wrap: break-word;` to preserve compound Sanskrit terms.

---

### Risk 6: Backend Language Capability Gaps `[VERIFIED RISK]`
- **Category:** Multilingual Integration
- **Description:**
  FastAPI calculation endpoints (`/api/kundali`, `/api/domains`, `/api/panchang`) do not currently accept a `lang` parameter; they return standardized Sanskrit/English terms. Assuming that the backend returns translated text in Hindi/Marathi will cause missing translation bugs.
- **Likelihood:** High | **Impact:** Medium.
- **Mitigation Strategy `[PROPOSED]`:**
  Establish a clear boundary: the Next.js frontend handles UI label and technical term translation using the centralized glossary (`frontend/messages/`). AI narrative translation to Hindi/Marathi is labeled as a future backend enhancement.

---

### Risk 7: WebGL & Three.js Performance on Mobile Devices `[PROPOSED RISK]`
- **Category:** Client Performance & Battery Life
- **Description:**
  Rendering an interactive 3D celestial sphere with continuous animation loops (`requestAnimationFrame`) can cause high GPU/battery consumption and frame drops on budget mobile devices.
- **Likelihood:** Medium | **Impact:** Medium.
- **Mitigation Strategy `[PROPOSED]`:**
  1. *Dynamic Lazy Loading:* The `CelestialGlobe.tsx` component is dynamically imported with `ssr: false` only when the user scrolls to the interactive viewport.
  2. *Visibility Throttling:* The 3D render loop pauses automatically when the tab is inactive or the canvas is out of the viewport (Intersection Observer).
  3. *Graceful 2D Fallback:* If WebGL is unsupported or the device is identified as low-power, a responsive, lightweight 2D SVG celestial diagram is rendered instead.

---

### Risk 8: Accidental Overwrite of Legacy Frontend during Migration `[CRITICAL RISK]`
- **Category:** File Integrity & Migration Safety
- **Description:**
  Initializing Next.js directly inside `frontend/` without prior archival would destroy legacy HTML templates, SVGs, and scripts.
- **Likelihood:** High | **Impact:** Critical (Irreversible asset loss).
- **Mitigation Strategy `[VERIFIED]`:**
  Enforce the 6-step safe migration protocol in Phase 2:
  1. Inspect `git status` and commit all untracked work.
  2. Recursively clone `frontend/` $\to$ `frontend-legacy/`.
  3. Execute automated SHA-256 hash comparison across 100% of files.
  4. Only upon hash verification, clear `frontend/` and initialize Next.js.
  5. Selectively copy required SVGs and locales from `frontend-legacy/`.
  6. Documented zero-data-loss rollback procedure to restore original state if build fails.

---

### Risk 9: Calculation Leakage into Frontend Architecture `[ARCHITECTURAL RISK]`
- **Category:** System Integrity
- **Description:**
  Frontend developers might be tempted to implement client-side dasha date calculators, Ayanamsha approximations, or yoga detectors, duplicating backend logic and creating diverging calculation outputs.
- **Likelihood:** Medium | **Impact:** Critical (Astrological inaccuracy).
- **Mitigation Strategy `[VERIFIED]`:**
  FastAPI remains the sole calculation engine. The frontend captures input, dispatches requests, and presents returned coordinates without independent astronomical math.
