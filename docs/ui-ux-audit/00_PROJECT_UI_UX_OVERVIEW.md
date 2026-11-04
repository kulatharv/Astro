# Project UI/UX Overview & Architectural Audit

**Product:** AstroLogic / Nakshatra Labs  
**Version:** 2.0.0 (Vedic Astrology & AI Prediction Platform)  
**Audit Scope:** Complete Page-by-Page UI/UX, Design System, Interaction, Accessibility, and Technical UX Audit  
**Auditor Roles:** Senior UI/UX Designer, UX Researcher, Frontend Architect, Accessibility Specialist, Design Systems Expert  
**Audit Mode:** Audit-Only (Zero code modification, read-only discovery, empirical code and DOM inspection)  
**Date:** October 2026  

---

## 1. Executive Summary

AstroLogic (also designated as Nakshatra Labs) is a high-precision Vedic astrology platform. While the underlying backend calculation engine (powered by Swiss Ephemeris `pyswisseph`, sidereal Lahiri Ayanamsha, 10-domain life prediction fusion, and 5-limb Panchang) is mathematically advanced and backed by an extensive test suite, the **frontend user interface represents an unbundled, legacy multi-page architecture** with severe visual, structural, responsive, and behavioral inconsistencies.

The frontend is implemented as **16 standalone monolithic HTML documents** served via FastAPI with Jinja2 templating, accompanied by client-side Vanilla JavaScript. There is **no reactive component framework** (no Next.js, React, Vue, or Svelte in the active frontend), no CSS build pipeline (no PostCSS, Tailwind CLI, or SCSS), and no centralized design tokens. Each page defines its own embedded `<style>` block and inlines its own navigation, header, footer, modal handlers, and color palette.

### Key Audit Highlights:
- **Discovered Routes:** 29 distinct server routes (17 public/user web pages, 4 auth/profile routes, 6 admin portal routes, 2 utility redirects) plus multiple client-side sub-views.
- **Frontend Architecture:** Multi-Page Application (MPA) with duplicated inline CSS and Vanilla JS.
- **Critical Usability Blockers (P0):**
  1. Broken blog links: All blog cards on `/blogs` link to `/blogs/{id}` (plural), which returns 404 because the server route is `/blog/{id}` (singular).
  2. Silent auth failure: The user login form on `/login` lacks error rendering tags (`{{ error }}` is never emitted into `#errorBox`), causing failed authentication attempts to silently reload without user feedback.
  3. Premature modal interruption: On `/prediction`, submitting birth details causes an unskippable testing feedback modal to instantly pop up over the calculated results before the user can view a single insight.
  4. Relative path resolution defects: The Kundali generator uses relative `fetch('api/kundali')` and `fetch('api/cities')` without leading slashes, causing 404s when trailing slashes or subpaths are visited.
  5. API capability mismatch: `panchang.html` includes rich profile resolution (`/api/panchang/resolve-profile`) and Vedic decision assistant (`/api/panchang/decision`) buttons that fail with 404 under the legacy `app.main` server where those endpoints were never registered.

---

## 2. Technology Stack & Frontend Architecture

| Layer | Implementation | Assessment & Architectural Risk |
| :--- | :--- | :--- |
| **Rendering Architecture** | FastAPI + Jinja2 Server-Side Rendering (SSR) | Hybrid SSR/SPA pattern. Pages are served as full HTML documents, which then execute client-side `fetch()` calls to populate inner HTML. |
| **Component Model** | Monolithic HTML templates (No Web Components or React) | No component reusability. The global navigation bar, mobile drawer, footer, star background, and modal dialogs are duplicated across 16 HTML files. |
| **CSS & Design System** | Vanilla CSS in embedded `<style>` tags per page | No unified design system. Spacing tokens, typography sizes, card radii, and color variables are redefined independently on every page. |
| **Typography** | Google Fonts: `Cinzel` (display serif), `Crimson Pro` (editorial serif), `Inter` (sans-serif) | Heavy font payload (13 distinct font weights loaded from Google Fonts on every page). Flash of unstyled text (FOUT) risk on slower networks. |
| **Icons & Media** | Native Unicode/Emoji (`✦`, `🌅`, `♈`, `♥`, `★`, `₹`, `✈`) and inline SVGs | Unpredictable cross-platform rendering of emojis (iOS vs Android vs Windows). Lack of accessible SVG icon labels. |
| **State Management** | Browser `localStorage` + In-Memory Variables + Cookies | Fragmented state: `panchang.html` stores profiles in `localStorage.getItem('vedic_profiles')`, while the backend stores single profiles in SQLite/PostgreSQL `user_profiles`. User inputs do not persist across navigation tabs. |
| **Internationalization (i18n)** | Cookie-based `lang` header + client-side JSON dictionary | Incomplete coverage: `panchang.html` partially uses `data-i18n` and `{{ t.get() }}`, while `index.html`, `kundali.html`, `prediction.html`, and `daily-horoscope.html` ignore translations completely. |

---

## 3. Complete Discovered Route Inventory

The application defines 29 accessible server routes, categorized into Public, User Authenticated, Admin Authenticated, and API Gateway endpoints:

### A. Public Web Pages (Accessible without Authentication)
1. `GET /` — Landing / Home Page (`index.html`)
2. `GET /{lang}/` — Localized Landing Page (`index.html`)
3. `GET /panchang` & `GET /panchang.html` — Daily Panchang & Decision Engine (`panchang.html`)
4. `GET /{lang}/panchang` — Localized Panchang Page (`panchang.html`)
5. `GET /kundali` — Birth Kundali & Navamsa Chart Visualizer (`kundali.html`)
6. `GET /{lang}/kundali` — Localized Kundali Page (`kundali.html`)
7. `GET /horoscope` — Daily Horoscope & Transit Engine (`daily-horoscope.html`)
8. `GET /{lang}/horoscope` — Localized Horoscope Page (`daily-horoscope.html`)
9. `GET /prediction` — 10 Life Domain Predictions & AI Insights (`prediction.html`)
10. `GET /{lang}/prediction` — Localized Prediction Page (`prediction.html`)
11. `GET /chat` & `GET /{lang}/chat` — Legacy redirect to `/prediction` (or broken `chat.html` in gateway)
12. `GET /blogs` — Blog Article Index & Category Filter (`blogs.html`)
13. `GET /{lang}/blogs` — Localized Blog Index (`blogs.html`)
14. `GET /blog/{blog_id}` — Single Blog Article Post (`blog-detail.html`)
15. `GET /{lang}/blog/{blog_id}` — Localized Blog Article Post (`blog-detail.html`)
16. `GET /about` — About Vedic Astrology & Platform Science (`about.html`)
17. `GET /{lang}/about` — Localized About Page (`about.html`)

### B. User Authentication & Profile Routes
18. `GET /login` — User Login Page (`auth.html`, mode="login")
19. `POST /login` — Authenticates session against SQLite/PostgreSQL `users` table
20. `GET /signup` — User Registration Page (`auth.html`, mode="signup")
21. `POST /signup` — Account creation endpoint
22. `GET /logout` — Clears user session and redirects to `/`
23. `GET /change-language/{lang}` — Sets 1-year language cookie and redirects to `/`
24. `GET /profile` — User Profile Dashboard & Activity Feed (`profile.html` — requires login)
25. `POST /profile` — Updates user profile birth details and notes

### C. Administrator Portal Routes (Requires `admin="true"` Session)
26. `GET /admin` — Redirects to `/admin/login` or `/admin/blogs`
27. `GET /admin/login` — Administrator Credential Form (`admin-login.html`)
28. `POST /admin/login` — Authenticates against `admin_users` table
29. `GET /admin/logout` — Terminates admin session
30. `GET /admin/blogs` — Admin Blog Management & CRUD Table (`admin-blog.html`)
31. `GET /admin/users` — Registered User Portfolio & Profile Monitor (`admin-users.html`)
32. `GET /admin/activity` — System User Activity Telemetry Stream (`admin-activity.html`)
33. `GET /admin/feedback` — Testing Feedback & User Ratings Dashboard (`admin-feedback.html`)

---

## 4. Global Navigation Structure & Visual Consistency

### Navigation Inconsistencies Across Pages
The global navigation bar demonstrates significant drift across routes:

| Route / Template | Brand Logo Link | Nav Links Present | Action Buttons in Header | Header Position & Height |
| :--- | :--- | :--- | :--- | :--- |
| **Home (`index.html`)** | `Astro✦Logic` | Home, Panchang (`/panchang.html`), Kundali, Horoscope, Predictions, Blogs, About, Profile | Language Selector (`<select>`), Profile, Logout, Generate Kundali | Sticky, 68px |
| **Panchang (`panchang.html`)** | `Astro✦Logic` | Home, Panchang (`/panchang`), Kundali, Horoscope, Predictions, Blogs, About, Profile | Profile, Logout, Kundali (No Language dropdown) | Sticky, 68px |
| **Kundali (`kundali.html`)** | `Astro✦Logic` | Home, Panchang (`/panchang.html`), Kundali, Horoscope, Predictions, Blogs, About, Profile | Profile, Logout (No CTA, No Language dropdown) | Sticky, 68px |
| **Horoscope (`daily-horoscope.html`)** | `Astro✦Logic` | Home, Panchang (`/panchang.html`), Kundali, Horoscope, Predictions, Blogs, About, Profile | Profile, Logout, Today's Panchang | Sticky, 68px |
| **Prediction (`prediction.html`)** | `Astro✦Logic` | Home, Panchang (`/panchang.html`), Kundali, Horoscope, Predictions, Blogs, About, Profile | Profile, Logout, Kundali | Sticky, 68px |
| **Blogs (`blogs.html`)** | `Astro✦Logic` | Home, Panchang (`/panchang.html`), Kundali, Horoscope, Predictions, Blogs, About, Profile | Profile, Logout, Today's Panchang | Sticky, 68px |
| **Blog Detail (`blog-detail.html`)** | `Astro✦Logic` | Home, Panchang (`/panchang.html`), Horoscope, Predictions, Blogs, About, Profile (**Kundali is MISSING!**) | Profile, Logout, Today's Panchang | **Fixed, 72px (causes layout shift)** |
| **About (`about.html`)** | `Astro✦Logic` | Home, Panchang (`/panchang.html`), Kundali, Horoscope, Predictions, Blogs, About, Profile | Profile, Logout, Generate Kundali | Sticky, 68px |
| **Profile (`profile.html`)** | `Astro✦Logic` | Home, Panchang (`/panchang.html`), Kundali, Horoscope, Predictions, Blogs, Profile (**About is MISSING!**) | Profile, Kundali, Logout | Sticky, 68px |
| **Admin Portal Pages** | `Astro*Logic` | Sidebar: Blog Management, Users, User Activity, Testing Feedback, View Website, Logout | Top Action Buttons: Users, Activity, Feedback, Blogs | Fixed Sidebar 248px |

### Key Navigation Flaws:
1. **Broken Static Extension Links:** Five separate pages link to `/panchang.html` rather than the semantic route `/panchang`. Mobile drawers frequently link to `/blogs.html`.
2. **Missing Nav Items:** `blog-detail.html` completely omits the core `Kundali` feature from the navbar. `profile.html` omits the `About` page.
3. **Unconditional Signed-In State in Nav:** Every public page displays `Profile` and `Logout` in the header even when visited by anonymous/guest users. Clicking `Profile` triggers a redirect to `/login`, and clicking `Logout` resets an empty session.
4. **Header Height & Position Shift:** Nine pages use `position: sticky; height: 68px;`, while `blog-detail.html` uses `position: fixed; height: 72px;` with manual body padding compensation, causing abrupt visual jumps during page-to-page navigation.

---

## 5. Available User Journeys & Disconnects

```mermaid
graph TD
    A[Visitor Lands on /] --> B{Action}
    B -->|Click Generate Kundali| C[/kundali]
    B -->|Click Daily Panchang| D[/panchang]
    B -->|Click Horoscope| E[/horoscope]
    B -->|Click 10 Domains| F[/prediction]
    
    C --> G[Enter Birth Details & Submit]
    G --> H[View D1/D9 SVG Charts & Dasha]
    H --> I[Click PDF Download]
    I --> J[Unskippable Testing Feedback Modal]
    J --> K[Window.open Raw HTML Print View]
    
    F --> L[Enter Birth Details & Submit]
    L --> M[Fetch /api/domains]
    M --> N[IMMEDIATE Feedback Modal Pops Up Over Results]
    N --> O[User Reads Domain Scores & Remedies]
    
    D --> P[Select City or GPS]
    P --> Q[Toggle 'My Panchang' Mode]
    Q --> R[Click 'Resolve Profile']
    R -->|Legacy Backend| S[HTTP 404 Endpoint Not Found]
```

### Major Journey Friction Points:
1. **Kundali → Prediction Journey Disconnect:** When a user enters their date, time, and city of birth on `/kundali`, that data is not shared with `/prediction` or `/panchang`. The user is forced to re-type their exact birth date, time, and city on every single page.
2. **Unsaved Profile Trap:** The landing page encourages users to "Signed in and ready to calculate your chart" and provides an "Update profile" link. However, saving a profile on `/profile` abruptly redirects to the homepage (`/`) without feedback, and the saved birth data is not auto-filled when navigating to `/kundali` or `/prediction`.
3. **Disruptive Feedback Capture:** Instead of capturing feedback post-reading, both `/kundali` and `/prediction` trigger high-friction rating modals before the user has had time to evaluate the accuracy of the reading.

---

## 6. Testing Methodology & Audit Limitations

### Testing Methodology
- **Source Code Inspection:** Complete static line-by-line inspection of all 16 HTML templates, 3 client-side JavaScript scripts, 10 FastAPI route modules, and SQLAlchemy data models.
- **Cross-Component Static Analysis:** Verified consistency of DOM identifiers, class names, CSS variable definitions, media queries, and font declarations across the entire repository.
- **Route & Link Verification:** Cross-referenced every anchor tag (`<a href>`), form action (`<form action>`), and client-side `fetch()` call against server-side FastAPI route definitions.

### Audit Limitations
- **Server Startup Constraint:** The local development server could not be started in the active test environment due to an existing codebase defect in `app/services/__init__.py:4` (where `generate_kundali_pdf` is imported instead of `generate_kundali_pdf_buffer`). Per strict user instructions ("This is an audit-only task. Do not modify source code..."), source code was not modified to bypass this defect.
- **Dynamic Viewport Inspection Limitation:** Exact pixel-level layout shifts and computed browser rendering across physical mobile hardware were evaluated through rigorous static responsive breakpoint inspection (`@media` rules and CSS grid/flexbox constraints) rather than live headless browser screenshots. All reported findings are directly verifiable in source code.
