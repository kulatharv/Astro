# 06 — Technology Stack Evaluation, Selection & Dependency Audit

**Project:** AstroLogic AI / Nakshatra Labs — Modern Frontend Migration  
**Document:** `docs/frontend-modernization/06_TECH_STACK_DECISION.md`  
**Phase:** Phase 1 – Discovery, Architecture Assessment & Implementation Planning  
**Status:** AUDITED & FINALIZED (Verification Standard Enforced)  
**Date:** October 31, 2026  
**Auditor:** Senior Software Architect, Security Engineer & Migration Specialist  

---

## 1. Executive Summary & Selection Principles

Selecting technologies for an enterprise Vedic computational platform requires balancing mathematical calculation fidelity, high-performance data visualization, rich cultural aesthetic immersion, accessibility, and zero-compromise developer velocity.

Every dependency in this document has been evaluated against three criteria:
1. **Necessity:** Does it solve an architectural requirement that cannot be cleanly achieved natively?
2. **Bundle & Performance Cost:** What is its runtime payload overhead, and can it be tree-shaken or lazy-loaded?
3. **Foundation vs Deferred:** Is it required in the Phase 2 foundation, or should it be deferred to subsequent module milestones?

---

## 2. Core Platform & Framework

### 2.1. Next.js App Router (v15+)
- **Purpose:** Full-stack React application framework, hybrid rendering engine, and BFF proxy.
- **Why Required:**
  - *React Server Components (RSC):* Enables static pre-rendering of educational articles, astrological definitions, and the homepage, achieving sub-second first contentful paint (FCP) and optimal SEO.
  - *App Router Nested Layouts:* Provides persistent layouts for the dashboard, Kundali viewer, and prediction tabs without component remounting.
  - *Same-Origin BFF Proxy:* Routes `/api/*` through Next.js server-side handlers, eliminating cross-origin cookie loss between development (`localhost:3000`) and FastAPI (`127.0.0.1:8000`).
- **Lighter Alternative Evaluated:** Vite + React SPA. *Rejected* because SPAs lack server-side rendering for SEO, require complex manual routing for multi-language paths, and cannot run a server-side BFF cookie proxy natively.
- **Adoption Tier:** **FOUNDATION (Phase 2)**.

### 2.2. React 19 & TypeScript 5+
- **Purpose:** Component runtime and static type checking.
- **Why Required:**
  - Eliminates runtime type errors across complex astrological structures (e.g. 12 houses containing variable numbers of direct/retrograde/combust planets).
  - TypeScript interfaces mirror FastAPI Pydantic v2 schemas 1:1, preventing contract drift.
- **Lighter Alternative Evaluated:** Plain JavaScript. *Rejected* due to high regression risk when handling complex multi-nested astrological payloads.
- **Adoption Tier:** **FOUNDATION (Phase 2)**.

---

## 3. Multilingual (i18n) Framework

### 3.1. `next-intl` (App Router Native)
- **Purpose:** Comprehensive internationalization framework for Next.js App Router.
- **Why Required:**
  - Native integration with Next.js App Router Server Components (`getTranslations`) and Client Components (`useTranslations`).
  - Seamless support for locale-prefixed routing (`/[locale]/...`), language switcher deep-link preservation, and locale-specific metadata.
  - Minimal bundle overhead compared to traditional `react-i18next` or heavy runtime formatters.
- **Lighter Alternative Evaluated:** Custom React Context with raw JSON dictionaries. *Rejected* because custom Context breaks React Server Component static generation and causes hydration mismatches on initial render.
- **Adoption Tier:** **FOUNDATION (Phase 2)**.

---

## 4. Styling & Design System Implementation

### 4.1. Tailwind CSS (v4)
- **Purpose:** Utility-first styling engine implementing the Sacred Almanac design tokens.
- **Why Required:**
  - Zero runtime CSS overhead; purges unused styles to produce a lightweight CSS payload (<15KB).
  - Replaces 12,000+ lines of duplicate inline `<style>` tags across legacy templates.
  - Custom design tokens directly mapped to theme variables: `bg-almanac-ivory`, `text-sacred-kumkum`, `border-temple-gold`.
- **Lighter Alternative Evaluated:** Pure Vanilla CSS. *Rejected* because maintaining custom responsive grids, fluid typography, and dark/light token variations across 40+ components creates immense maintenance debt.
- **Adoption Tier:** **FOUNDATION (Phase 2)**.

### 4.2. shadcn/ui (Radix UI Primitives)
- **Purpose:** Accessible, unstyled component primitives (dialogs, dropdowns, tabs, accordions, tooltips).
- **Why Required:**
  - Code lives directly in the repository (`components/ui/`) with zero third-party package lock-in.
  - Full keyboard accessibility and WCAG 2.2 AA compliance out-of-the-box for complex widgets.
- **Lighter Alternative Evaluated:** Custom hand-coded HTML/CSS dropdowns. *Rejected* due to severe accessibility defects (keyboard focus trapping, screen-reader ARIA states).
- **Adoption Tier:** **FOUNDATION (Phase 2)**.

---

## 5. State Management & Data Fetching

### 5.1. TanStack Query (v5)
- **Purpose:** Asynchronous server-state management, caching, deduplication, and background synchronization.
- **Why Required:**
  - Manages city search autocomplete caching, Panchang daily queries, and saved chart mutations.
  - Handles loading states, retries, and cache invalidation automatically.
- **Lighter Alternative Evaluated:** Raw `useEffect` + `fetch`. *Rejected* due to race conditions, lack of caching, and boilerplate bloat.
- **Adoption Tier:** **FOUNDATION (Phase 2)**.

### 5.2. Zustand (v5)
- **Purpose:** Minimal client-side UI state store (<1KB bundle).
- **Why Required:**
  - Manages transient user interface preferences: active chart style (North vs South Indian), active prediction tab (1 to 10), and modal drawer visibility.
  - Does **not** duplicate server data.
- **Lighter Alternative Evaluated:** React Context. *Context causes unnecessary whole-tree re-renders* during frequent UI toggles; Zustand isolates re-renders to selecting components.
- **Adoption Tier:** **FOUNDATION (Phase 2)**.

### 5.3. React Hook Form & Zod
- **Purpose:** High-performance form state management and schema validation.
- **Why Required:**
  - Isolates re-renders to individual form fields during birth date/time typing.
  - Zod schemas validate birth coordinates, hours (0–23), minutes (0–59), and valid calendar dates before dispatching network requests to FastAPI.
- **Lighter Alternative Evaluated:** Uncontrolled form inputs. *Rejected* due to complex multi-field birth validation requirements.
- **Adoption Tier:** **FOUNDATION (Phase 2)**.

---

## 6. Astrological Visualization & Graphics

### 6.1. Declarative React SVG + D3.js
- **Purpose:** North Indian (Diamond) and South Indian (Square) Kundali chart visualization.
- **Why Required:**
  - Pure vector graphics scale flawlessly across mobile screens (320px) to high-density desktop displays (4K).
  - D3.js geometric math calculates precise polygonal house nodes, planetary collision avoidance within congested houses, and aspect connection lines (Drishti).
- **Lighter Alternative Evaluated:** HTML Canvas or PNG images. *Rejected* because canvas graphics cannot be easily styled with CSS, lack DOM accessibility, and become blurry on high-DPI displays.
- **Adoption Tier:** **PHASE 3 (Kundali Module)**.

### 6.2. Apache ECharts (via `echarts-for-react`)
- **Purpose:** Multi-dimensional numerical analytics: Shadbala 6-fold potency radar, Ashtakavarga 12x8 matrix, and 10-domain vitality scores.
- **Why Required:**
  - Outstanding Canvas/SVG rendering performance for dense numerical grids.
  - Responsive radar and bar visualizations require minimal custom math compared to manual D3 implementations.
- **Optimization Strategy:** Dynamically imported with `ssr: false` to ensure zero impact on initial bundle size.
- **Adoption Tier:** **PHASE 3 / PHASE 5 (Deferred to Analytics Modules)**.

### 6.3. Three.js & React Three Fiber (R3F)
- **Purpose:** Interactive 3D Celestial Sphere / Sky Globe on the homepage and transit explorer.
- **Why Required:**
  - Renders an immersive 3D celestial sphere displaying the tilted ecliptic band and real-time planetary transits.
- **Optimization Strategy:** Strictly lazy-loaded (`next/dynamic` with `ssr: false`) and omitted from the initial Phase 2 bundle. Includes a lightweight 2D SVG fallback for low-power mobile devices.
- **Adoption Tier:** **PHASE 3 / PHASE 4 (Deferred Enhancement)**.

---

## 7. Animation & Icons

### 7.1. Motion (formerly Framer Motion)
- **Purpose:** Declarative page transitions, tab sliding indicators, accordion expansion, and modal dialog animations.
- **Why Required:**
  - First-class React integration with declarative `AnimatePresence` and spring physics.
  - Respects system `prefers-reduced-motion` settings automatically for accessibility.
- **Adoption Tier:** **FOUNDATION (Phase 2)**.

### 7.2. Lucide React
- **Purpose:** Lightweight, tree-shakeable SVG icon set.
- **Why Required:**
  - Replaces heavy font-icon bundles with individual SVG symbols.
- **Adoption Tier:** **FOUNDATION (Phase 2)**.

---

## 8. Master Dependency Rollout Schedule

| Package Name | Purpose | Rollout Phase | Bundle Impact | Initial Foundation? |
| :--- | :--- | :--- | :--- | :--- |
| `next` | Core App Router Framework | Phase 2 | Framework | **YES** |
| `react` / `react-dom` | UI Runtime | Phase 2 | Framework | **YES** |
| `typescript` | Static Type System | Phase 2 | Dev-only (0KB) | **YES** |
| `tailwindcss` (v4) | Utility Styling Engine | Phase 2 | <15KB purged | **YES** |
| `next-intl` | Multilingual (i18n) Engine | Phase 2 | ~8KB | **YES** |
| `shadcn/ui` (Radix) | Accessible Primitives | Phase 2 | Code-owned | **YES** |
| `@tanstack/react-query`| Server State & Caching | Phase 2 | ~12KB | **YES** |
| `zustand` | Client UI State | Phase 2 | <1KB | **YES** |
| `react-hook-form` + `zod`| Form Validation | Phase 2 | ~15KB | **YES** |
| `motion` | Micro-Animations | Phase 2 | ~30KB | **YES** |
| `lucide-react` | Icons | Phase 2 | Tree-shaken | **YES** |
| `d3` (selected modules)| Kundali SVG Math | Phase 3 | ~20KB | DEFERRED |
| `echarts` / `echarts-for-react`| Shadbala & Radars | Phase 3/5 | Dynamic (~300KB) | DEFERRED |
| `three` / `@react-three/fiber`| 3D Celestial Globe | Phase 3/4 | Dynamic (~500KB) | DEFERRED |
