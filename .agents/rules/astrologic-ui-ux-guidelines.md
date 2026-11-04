---
description: Project-specific design, 3D, motion, and UI verification rules for AstroLogic / Nakshatra Labs
globs: ["app/templates/**/*.html", "app/static/**/*", "frontend/**/*", "docs/ui-ux-audit/**/*"]
alwaysApply: true
---

# AstroLogic / Nakshatra Labs — UI/UX, 3D & Animation Guidelines

This rule applies to all UI/UX design, motion graphics, 3D web features, and browser verification tasks within AstroLogic. It governs the execution of `ui-ux-pro-max`, `ai-ui-ux-motion-engine`, `3d-website-architect`, and `ui-verification`.

---

## 1. Existing Architecture & Technology Stack
- **Core Stack:** Preserve FastAPI, Jinja2, Semantic HTML5, Vanilla CSS, and Vanilla JavaScript (ES6+).
- **No Unapproved Framework Migration:** Do NOT introduce React, Next.js, Vue, Svelte, or a node-based bundling pipeline without explicit user instruction.
- **Backend & Routing Integrity:** Respect all existing FastAPI endpoints, template routes (`app/api/routes/pages.py`), static mount (`/static`), and session cookies.
- **Rendering Technology Selection:**
  - Use Vanilla CSS for layouts, transitions, states, and responsive grids.
  - Use SVG and Canvas for 2D charts, North Indian Kundali wheels, and planetary aspects.
  - Use Three.js (via CDN/isolated module) **only where 3D materially enhances user comprehension or immersion** (e.g., interactive celestial sphere, 3D zodiac band, planetary orbital viewer). Never add gratuitous 3D widgets that slow down page loads.

---

## 2. Astrology Domain Integrity
- **Untouchable Engine Settings:** Never modify Swiss Ephemeris settings (`swe.set_sid_mode`), Lahiri Ayanamsha (`SIDM_LAHIRI`), planetary calculation logic, Panchang limb calculations, Kundali chart rendering math, or prediction rules during UI work.
- **Contract Preservation:** Retain all API request/response schemas, authentication guards (`DefaultDenyAuthMiddleware`), session parameters, and saved profile persistence.
- **Clear Demarcation:** Distinctly separate deterministic calculation results (planetary degrees, Nakshatra, Dasha timelines, Ashtakavarga points) from AI-generated narrative interpretations in visual cards.

---

## 3. Visual Quality & Celestial Aesthetic Standards
- **Brand Personality:** Deliver a cohesive, mystical yet scientific, high-trust Vedic astrology experience (Dark Cosmic / Luxury Mystical).
- **Curated Celestial Palette:**
  - Deep Celestial Navy/Obsidian base: `#010812`, `#071426`, `#0c2a4a`
  - Sacred Gold accents: `#f5c16c`, `#d89b3c`, `rgba(245,193,108,0.28)`
  - Cosmic Blue secondary: `#9bdcff`, `rgba(155,220,255,0.38)`
  - Surface Glass: `rgba(255, 255, 255, 0.04)` to `rgba(255, 255, 255, 0.07)` with `backdrop-filter: blur(16px)`
- **Typography:**
  - Display / Headlines: `Cinzel`, serif (hierarchical, celestial, dignified)
  - Body & Long-form Narrative: `Crimson Pro`, serif or `Inter`, sans-serif (high readability, comfortable line heights 1.6–1.8)
  - Data / Astrological Glyphs: `Inter`, sans-serif with tabular figures
- **Restraint & Anti-Slop:**
  - Avoid generic AI templates, muddy purple gradients, and clashing neon glows.
  - Avoid heavy, distracting particle fields that reduce text legibility.
  - Keep 3D focused and purposeful: one flagship visual experience per page.

---

## 4. Performance & Accessibility
- **Performance Budget:**
  - Initial content render under 1.5s.
  - Lazy-load all nonessential 3D scenes until user scrolls or activates them (`IntersectionObserver`).
  - Provide a graceful 2D/static fallback when WebGL is unavailable or errors out.
- **Accessibility (WCAG 2.1 AA):**
  - Respect `prefers-reduced-motion`: disable or reduce smooth camera sweeps, particle drifting, and scroll-jacking.
  - Full keyboard accessibility: interactive elements must have visible focus rings (`:focus-visible`) and logical Tab order.
  - Minimum touch target size: 44×44px on mobile devices.
  - High text contrast: maintain minimum 4.5:1 contrast for all informational text.

---

## 5. Implementation Safety & Visual Verification
- **Verification First:** Validate findings and inspect existing code before modifying files.
- **Scoped Edits:** Make targeted, incremental changes. Never perform sweeping unrequested refactors.
- **Regression Testing:** Ensure existing tests (`pytest tests/`) continue to pass after any UI change.
- **Visual Browser Verification:** Use `ui-verification` probes (target-size, focus-walk, viewport-stress, console-network) to measure real computed styles and layout behavior in the browser.
