# Global Design System Audit

**Product:** AstroLogic / Nakshatra Labs  
**Version:** 2.0.0  
**Scope:** Design tokens, CSS architecture, shared UI components, typography, color harmony, and visual consistency across all 16 application templates.

---

## 1. Current Design Token Analysis

Across the application's 16 templates, design tokens are implemented as CSS Custom Properties declared inside localized `:root` blocks within embedded `<style>` tags. Because there is **no centralized CSS file** (no global `variables.css` or design token package), tokens have drifted significantly across pages.

### A. Color Palette Inventory & Drift

| Token Name | Intended Role | Observed Values Across Codebase | Inconsistency & WCAG Compliance Notes |
| :--- | :--- | :--- | :--- |
| `--gold` | Primary Brand & Headings | `#f5c16c` (all templates) | High contrast (~9.5:1) against `#010812`. Vibrant, elegant, well-received. |
| `--gold2` | Gradient Transition Tone | `#d89b3c` (most templates) | Secondary gradient anchor for buttons and card borders. |
| `--gold-dim` | Card/Hover Background Fill | `rgba(245,193,108,.12)` on home/panchang;<br>`rgba(245,193,108,0.1)` on kundali | Drift in alpha opacity (10% vs 12%), causing subtle brightness variance across routes. |
| `--gold-border`| Accent Border | `rgba(245,193,108,.28)` | Consistent across most templates. |
| `--blue` | Secondary Cosmic / Accents | `#9bdcff` | Pastel sky blue. Used for eyebrow tags, links, and astrological karakas. Contrast against dark bg is ~8.2:1 (Pass). |
| `--green` | Auspicious / Direct Status | `#4ade80` | Mint green. Used for yogas, direct planets, and recommended actions. |
| `--red` | Inauspicious / Retrograde | `#f87171` (most); `#ef4444` (print) | Coral red. Used for doshas, Rahu Kaal, and warnings. |
| `--surface` | Primary Card Background | `rgba(255,255,255,.04)` on home;<br>`rgba(255,255,255,.05)` on auth/admin | Slight opacity drift (4% vs 5%). Both deliver a pleasant glassmorphic backdrop. |
| `--border` | Subtle Container Outline | `rgba(255,255,255,.08)` (home);<br>`rgba(255,255,255,.1)` (auth/admin) | Border opacity drifts between 0.08 and 0.10. |
| `--text` | Primary Body Text | `#e8e8e8` | Off-white text providing crisp 12:1 contrast against deep navy. |
| `--text-dim` | Secondary / Metadata Text | `rgba(232,232,232,.52)` (home);<br>`rgba(232,232,232,.55)` (panchang);<br>`rgba(232,232,232,.58)` (admin) | **WCAG Failure:** `rgba(232,232,232,.52)` on dark backgrounds produces a contrast ratio of only **4.1:1**, which fails WCAG AA minimum 4.5:1 for normal body text (< 18px). Must be increased to at least `rgba(232,232,232, 0.70)`. |
| `--hh` | Global Header Height | `68px` (all standard pages);<br>`72px` (`blog-detail.html`) | Header height shifts by 4px when visiting single blog articles, causing jarring layout shifts. |

---

## 2. Typography System & Hierarchy

The application incorporates three distinct Google Font families:

1. **`Cinzel` (Weights: 400, 500, 600, 700):** Classical Roman serif used exclusively for branding, page titles (`<h1>`), section titles (`<h2>`), and zodiac glyph names.
2. **`Crimson Pro` (Weights: 300, 400, 500, Italic):** Humanist editorial serif used for hero subheadings, philosophy prose, and blog article reading bodies.
3. **`Inter` (Weights: 300, 400, 500, 600, 700):** Clean geometric sans-serif used for navigation, forms, buttons, data tables, and telemetry streams.

```
┌────────────────────────────────────────────────────────┐
│  Typography Scale (Observed Across Templates)          │
├───────────────────┬─────────────┬───────────┬──────────┤
│ Level             │ Font Family │ Size      │ Weight   │
├───────────────────┼─────────────┼───────────┼──────────┤
│ Hero Display      │ Cinzel      │ 38px–56px │ 600–700  │
│ Page Title (H1)   │ Cinzel      │ 24px–38px │ 600      │
│ Section Title (H2)│ Cinzel      │ 20px–30px │ 600      │
│ Eyebrow Tag       │ Inter       │ 10.5–11px │ 700–800  │
│ Editorial Body    │ Crimson Pro │ 17px–19px │ 300–400  │
│ Standard Body     │ Inter       │ 13px–14px │ 400–500  │
│ Micro Metadata    │ Inter       │ 10px–11px │ 500–600  │
└───────────────────┴─────────────┴───────────┴──────────┘
```

### Typography Issues:
- **Excessive Weight Requests:** Pages request 13 individual font weights in a single Google Fonts `<link>`, increasing Initial Server Response time and First Contentful Paint (FCP).
- **Line Lengths:** Editorial text on `/about` and `/blog/*` is properly constrained (`max-width: 740px`), but prediction analysis text on `/prediction` stretches across 1100px on wide viewports, exceeding the recommended 75-character ergonomic reading line length.
- **Header Font Pairing:** Headings that combine `Cinzel` with italic `Crimson Pro` in the same line (`<h1>Nothing Happens Without a <em>Pattern.</em></h1>`) occasionally suffer from mismatched baseline alignment due to different font metric descenders.

---

## 3. Shared Components & Duplication Audit

Because there is no component templating or reactive library, shared components are manually copy-pasted across templates with varying degrees of divergence.

### A. The Global Header
- **Duplicated in 10 Public Pages:** Defined separately in `index.html`, `panchang.html`, `kundali.html`, `daily-horoscope.html`, `prediction.html`, `blogs.html`, `blog-detail.html`, `about.html`, `auth.html`, and `profile.html`.
- **Divergence:**
  - `index.html` includes a `<select id="languageSelector">` in the header; none of the other 9 pages include it.
  - Action buttons drift: some pages show `Profile + Logout + Generate Kundali`; others show `Profile + Logout + Today's Panchang`; `kundali.html` shows only `Profile + Logout`.
  - `blog-detail.html` omits `Kundali` from the navbar entirely.
  - `profile.html` omits `About` from the navbar entirely.
  - `blog-detail.html` uses `position: fixed; height: 72px;`, while all other pages use `position: sticky; height: 68px;`.

### B. Mobile Navigation Drawer (`.mob-nav`)
- **Duplicated in 9 Pages:** Each page maintains an inline `<div class="mob-nav" id="mn">` with separate toggle script `document.getElementById('mn').classList.toggle('open')`.
- **Divergence:** Several mobile drawers link to `/panchang.html` and `/blogs.html` (with static `.html` suffixes), while others link to semantic `/panchang` and `/blogs`.

### C. The Global Footer
- **Divergence:**
  - `index.html` renders a 4-column rich footer with brand description, feature links, educational links, company links, copyright, and technology badges (Swiss Ephemeris, Lahiri Ayanamsa, AI-Powered).
  - `panchang.html` renders a single centered text string: `<footer>© 2026 AstroLogic · Enterprise Vedic Decision Engine</footer>`.
  - `kundali.html` renders another single centered string: `<footer><p>© 2026 AstroLogic · Vedic Astrology Platform · Calculations via Lahiri Ayanamsa & Swiss Ephemeris</p></footer>`.
  - `daily-horoscope.html` and `profile.html` **have no footer at all**.

### D. Buttons & Action Links
Multiple button naming conventions exist side-by-side:
- `.btn-g` (Gold gradient primary button)
- `.btn-o` (Gold outline secondary button)
- `.btn-hero-p` (Home hero primary button)
- `.btn-hero-s` (Home hero secondary button)
- `.btn-auth` (Authentication submit button)
- `.btn-login` (Admin login submit button)
- `.btn-gold`, `.btn-outline`, `.btn-danger` (Admin portal buttons)

---

## 4. Design System Gaps

1. **No Centralized CSS File:** Changes to brand color, header navigation, or typography currently require manual editing of 16 separate HTML files.
2. **Missing Form Design System:** Input styles are declared ad-hoc in every page's `<style>` tag. Some pages use `!important` flags on input backgrounds to override browser defaults.
3. **No Elevation / Shadow Tokens:** Shadows range from `box-shadow: 0 8px 24px rgba(0,0,0,.4)` to `0 24px 70px rgba(0,0,0,.28)`, creating inconsistent depth layers.
4. **No Standard Modal / Dialog Pattern:** Both Kundali and Prediction pages inject ad-hoc `document.createElement("div")` modal overlays into `document.body` with inline styles instead of using a reusable accessible `<dialog>` element.
5. **No Standard Iconography:** Interface mixes Unicode symbols (`✦`, `🌅`, `♈`, `♥`, `★`, `₹`, `✈`), SVG paths, and platform-specific emojis. On different operating systems (Windows 11 vs macOS vs Android), emojis render with drastically different styles and visual weights.

---

## 5. Architectural Recommendations for Unification

To transition AstroLogic into a unified, enterprise-grade design system without requiring an immediate framework rewrite:

1. **Extract Global Tokens to `app/static/css/tokens.css`:**
   - Define canonical CSS Custom Properties for colors, typography scale, spacing (4px, 8px, 12px, 16px, 24px, 32px, 48px), border-radii (`sm: 6px`, `md: 10px`, `lg: 16px`, `pill: 999px`), and z-index layers.
2. **Unify Layout Templates via Jinja2 Inheritance:**
   - Create a true `base.html` master template containing the canonical `<head>`, Google Fonts links, sticky 68px header, mobile drawer, and 4-column footer.
   - All 16 pages should extend `base.html` via `{% extends "base.html" %}`, eliminating 1,500+ lines of duplicated navigation and footer code.
3. **Consolidate Button Hierarchy:**
   - Establish three standard classes: `.btn-primary` (gold gradient), `.btn-secondary` (gold outline), and `.btn-ghost` (transparent).
4. **Replace Emoji Icons with Accessible SVG System:**
   - Create an SVG sprite or component directory for Vedic planetary symbols, zodiac signs, and action icons with consistent stroke weight (1.5px) and gold/blue palette harmony.
