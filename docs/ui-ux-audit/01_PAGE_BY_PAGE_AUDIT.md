# Comprehensive Page-by-Page UI/UX Audit

**Project:** AstroLogic / Nakshatra Labs  
**Version:** 2.0.0  
**Audit Scope:** Deep individual inspection of every discovered page and template  
**Scoring Framework:** 1–10 Scale (1 = Severe Blocker, 10 = Enterprise Best Practice) across 8 dimensions:  
Visual Design (VD), Usability (US), Navigation (NV), Responsive Design (RD), Accessibility (A11Y), Content Hierarchy (CH), Interaction Feedback (IF), Overall Polish (OP).

---

## Page 1: Home / Landing Page (`/` and `/{lang}/`)

### 1. Page Purpose & Target User Journey
- **Purpose:** Serve as the primary front door and conversion engine for AstroLogic. Introduce value propositions, establish Vedic astronomical credibility (Swiss Ephemeris, Lahiri Ayanamsha), provide a daily cosmic snapshot (Live Panchang strip), and route users toward generating a free birth chart or exploring life domains.
- **Target User:** First-time seekers, Vedic astrology enthusiasts, and returning users looking for daily transit or horoscope updates.
- **Primary Call to Action (CTA):** "Generate Free Kundali" (`/kundali`). Secondary CTA: "Complete Profile" (`/profile`).

### 2. Visual Design & Aesthetics
- **Layout & Spacing:** Radial gradient celestial theme (`#0a2540` to `#010812`) with multiple CSS radial-gradient star dots on `body::before`. Max width 1200px centered layout.
- **Typography:** Heavy mix of `Cinzel` for headings, `Crimson Pro` for subheadings, and `Inter` for UI body text. Line heights are readable, but font weight contrast between headings and body creates visual imbalance.
- **Color Contrast:** Deep gold (`#f5c16c`) on dark navy background provides excellent contrast ratio (~9.5:1). However, secondary muted text (`var(--text-dim)`: `rgba(232,232,232,0.52)`) on dark surfaces drops to ~4.1:1, failing WCAG AA for small text under 18px.
- **Visual Clutter & Dead Code:** In `index.html` lines 430–455, an elaborate interactive constellation SVG with animated orbit rings and 9 clickable planet nodes exists in the DOM. However, line 153 explicitly overrides it: `.hero-visual>.vis-hint,.hero-visual>.constellation-wrap{display:none}`. Instead, `.hero-dashboard` is rendered on top, leaving dead SVG animation code executing invisibly in the DOM.

### 3. UX & Interaction Observations
- **Unauthenticated State Falsehood:** Line 378 displays `<div class="hero-note"><span></span>Signed in and ready to calculate your chart</div>` unconditionally. Anonymous first-time visitors see a green active dot and "Signed in", which is confusing and inaccurate.
- **Navigation Inconsistencies:** The header displays `Profile` and `Logout` links to guest users. The Panchang link points to `/panchang.html` (including the `.html` extension), while others point to `/kundali`, `/horoscope`, and `/prediction`.
- **Language Switcher Defect:** Lines 697–715 define a client-side `changeLanguage(lang)` function that writes to `localStorage` and calls `location.reload()`. It does not set the server `lang` cookie or trigger `/change-language/{lang}`. Furthermore, `index.html` contains zero Jinja translation tags `{{ t.get(...) }}`, meaning switching the language dropdown does literally nothing on the homepage.
- **Admin Link Leakage:** Line 665 in the public footer displays a direct link to `<a href="/admin/blogs">Admin</a>`, exposing internal admin routes to standard consumers.

### 4. Responsive Design & Touch Usability
- **Breakpoints:** `@media(max-width: 1024px)`, `(max-width: 900px)`, `(max-width: 768px)`, and `(max-width: 540px)`.
- **Mobile Menu:** Lines 357–366 define `#mn`. When clicked via hamburger (`.ham`), it overlays fixed navigation. However, the mobile menu links to `/panchang.html` and `/blogs.html`.
- **Card Stacking:** At 540px, the 4-column feature grid collapses to 2 columns, but quick dashboard action cards (`.quick-grid`) cram text labels ("Birth Kundali", "Data Profile") with awkward line wraps.

### 5. Accessibility (WCAG 2.2 AA)
- **Heading Hierarchy:** One `<h1>` ("Nothing Happens Without a Pattern"), followed by logical `<h2>` section titles.
- **Form & Interactive Controls:** Hamburger button (`.ham`) is a `<div>` with an inline `onclick` and lacks `role="button"`, `aria-label="Toggle navigation"`, and `aria-expanded="false"`. Keyboard users cannot focus or toggle the mobile menu.
- **Color Contrast:** Muted paragraph text in `.hero-sub` and `.stat-lbl` fails 4.5:1 ratio.

### 6. Technical UX
- **Live Panchang Strip:** Lines 681–696 execute `fetch('/api/panchang', {body: JSON.stringify({city:'Pune'})})`. It hardcodes Pune and lacks geolocation, falling back to a raw text error if the server is unreachable.
- **Asset Overhead:** Loads 13 Google Font variants simultaneously in `<head>`, inducing render blocking.

### 7. Evaluation Scores
| Dimension | Score (1-10) | Evidence & Justification |
| :--- | :---: | :--- |
| **Visual Design** | 7.5 | Atmospheric cosmic theme, rich palette, though marred by hidden dead SVG elements. |
| **Usability** | 6.0 | Misleading "Signed in" badge for guests, dead language toggle, admin link in footer. |
| **Navigation** | 5.5 | Inconsistent `.html` URL extensions, guest state displays Logout button. |
| **Responsive Design** | 7.0 | Solid multi-breakpoint grid transitions, though mobile dashboard cards wrap awkwardly. |
| **Accessibility** | 4.5 | Non-semantic hamburger `div`, missing ARIA attributes, low text-dim contrast. |
| **Content Hierarchy** | 7.5 | Clear flow: Hero → Live Strip → Features → How it Works → Domains → Zodiac → Trust. |
| **Interaction Feedback** | 6.0 | Smooth hover transitions on cards; lack of skeleton state on live panchang strip. |
| **Overall Polish** | 6.5 | Strong first impression visually, but riddled with small functional defects. |

### 8. Recommended Improvements & Acceptance Criteria
- **Fix 1 (P1):** Replace hardcoded "Signed in" message with dynamic conditional rendering. If user is guest, show "Calculate your personal birth chart in 60 seconds" and display "Sign In / Register" in header.
  - *Acceptance Criteria:* Guest sees "Sign In" and "Generate Kundali"; authenticated user sees their name and "Profile".
- **Fix 2 (P1):** Connect `#languageSelector` to `/change-language/{lang}` and internationalize homepage content with `{{ t.get() }}`.
  - *Acceptance Criteria:* Selecting "Hindi" switches UI headers, hero text, and meta description into Hindi.
- **Fix 3 (P2):** Clean up dead constellation CSS/SVG markup or re-enable it as an interactive hero graphic.
  - *Acceptance Criteria:* No hidden 400x400 SVG running CSS keyframe animations in the background.

---

## Page 2: Daily Panchang (`/panchang` and `/panchang.html`)

### 1. Page Purpose & Target User Journey
- **Purpose:** Serve as the real-time daily Vedic decision engine. Displays the 5 classical limbs (Tithi, Nakshatra, Yoga, Karana, Vara), active Choghadiya countdowns, planetary Horas, prohibited travel direction (Disha Shool with Vedic remedies), auspicious windows (Abhijit/Brahma Muhurat), and personalized Tara Bala/Chandra Bala calculations.
- **Target User:** Daily practitioners, astrologers, and individuals timing important activities (travel, signing contracts, investments).
- **Primary CTA:** City selection & "Resolve Profile" for personalized score.

### 2. Visual Design & Aesthetics
- **Layout & Components:** Dense, highly functional layout. Features live hero with large cosmic score badge (`8.5`), live status indicator pills, 16-period horizontal Choghadiya timeline, dual-card Do's & Don'ts grid, and a full planetary transit table.
- **Visual Clutter:** High cognitive load. Screen presents over 25 individual astrological parameters simultaneously without progressive disclosure.
- **Footer Inconsistency:** Line 590 renders a minimalist one-line footer: `<footer>© 2026 AstroLogic · Enterprise Vedic Decision Engine</footer>`, completely ignoring the rich 4-column footer established on the homepage.

### 3. UX & Interaction Observations
- **API Disconnect on Profile Resolution (P0 Blocker):** Lines 780–823 implement an elaborate `resolveProfile()` function triggering `fetch('/api/panchang/resolve-profile')`. This endpoint exists in `backend/modules/panchang/api.py`, but **is completely absent from `app/api/routes/panchang.py`**. Under the legacy backend, entering birth details and clicking "Resolve Profile" throws an unhandled HTTP 404 error and alert.
- **Decision Engine Disconnect (P0 Blocker):** Lines 418–428 feature a "Vedic Decision Assistant" with quick buttons for Travel, Investment, Meeting, Spiritual, and Purchase. Clicking any button calls `/api/panchang/decision`, which also fails with HTTP 404 on the legacy router.
- **City Select Hardcoding:** Lines 344–363 hardcode 17 cities in a static `<select>` instead of loading all 150+ supported cities from `/api/cities`.
- **Live Choghadiya Countdown:** Line 598 sets a 1-second `setInterval()`. However, line 603 accesses `chog.time_remaining_str` without updating the underlying countdown seconds, causing the timer text to remain static until a full page refresh.

### 4. Responsive Design & Touch Usability
- **Horizontal Scroll Trap:** The 16-period Choghadiya timeline (`.chog-strip`) is configured with `grid-template-columns: repeat(8, 1fr); overflow-x: auto;`. On mobile viewports (375px/390px), each cell is squished to ~40px wide, clipping Sanskrit period names ("Shubh", "Labh", "Amrit").
- **Table Overflow:** The Gochara transits table (`.glass-table`) scrolls horizontally on mobile devices, but lacks a visible swipe affordance or sticky first column.

### 5. Accessibility (WCAG 2.2 AA)
- **Form Controls:** City selector has no associated `<label>` (only an implicit container).
- **Dynamic Content Announcements:** When live countdowns or Choghadiya periods change, screen readers receive no `aria-live="polite"` notification.
- **Color-Coded Meaning:** Recommended actions (`.advice-card.rec`) use green borders, while Avoid actions (`.advice-card.avd`) use red borders. Users with deuteranopia / red-green color blindness cannot distinguish these without relying on the small emoji icons (`✅` and `🚫`).

### 6. Technical UX
- **ICS Calendar Export:** The "Add to Calendar (.ics)" button calls `downloadCalendarICS()`, which requests `/api/panchang/calendar.ics`—another endpoint missing from the legacy server.

### 7. Evaluation Scores
| Dimension | Score (1-10) | Evidence & Justification |
| :--- | :---: | :--- |
| **Visual Design** | 7.8 | High-density dashboard with informative visual cards and cosmic badge. |
| **Usability** | 4.0 | Multiple critical features (Resolve Profile, Decision Assistant, ICS) return 404. |
| **Navigation** | 6.5 | Standard header, but minimalist single-line footer breaks site consistency. |
| **Responsive Design** | 5.5 | Choghadiya 8-column grid severely clips text on mobile screens. |
| **Accessibility** | 5.0 | Missing form labels, no `aria-live` for countdown timers, color-dependent alerts. |
| **Content Hierarchy** | 8.0 | Superb logical order: Status → Timeline → Do's/Don'ts → Limbs → Transits. |
| **Interaction Feedback** | 4.5 | Alert popups on error instead of inline form validation states. |
| **Overall Polish** | 5.0 | Feature-rich concept crippled by backend endpoint mismatch and mobile layout clipping. |

### 8. Recommended Improvements & Acceptance Criteria
- **Fix 1 (P0):** Ensure all advanced Panchang endpoints (`/api/panchang/resolve-profile`, `/api/panchang/decision`, `/api/panchang/calendar.ics`) are registered across all server boot paths.
  - *Acceptance Criteria:* Submitting birth details in "My Panchang" mode resolves Tara Bala and Chandra Bala without 404 errors.
- **Fix 2 (P1):** Redesign `.chog-strip` on viewports < 768px into a scrollable vertical timeline or a 2-column card stack.
  - *Acceptance Criteria:* All 8 daytime and 8 nighttime Choghadiya segments display full period names, timings, and planets without text clipping on 375px screens.

---

## Page 3: Kundali / Birth Chart (`/kundali` and `/{lang}/kundali`)

### 1. Page Purpose & Target User Journey
- **Purpose:** Primary flagship tool. Allows users to enter exact birth details (Name, Date, Time, City) to generate complete Vedic natal charts: D1 Rashi (Natal), D9 Navamsa (Spouse/Dharma), planetary positions with dignity/combustion, chart strength scores, 50+ yogas, doshas with remedies, all 12 house lords, Vimshottari Dasha timeline, contextual AI chat, and a downloadable PDF report.
- **Target User:** Anyone seeking a comprehensive, traditional Vedic astrology birth chart.
- **Primary CTA:** "Generate Kundali" button (`#generateBtn`). Secondary CTA: "⬇ PDF" download button (`#downloadBtn`).

### 2. Visual Design & Aesthetics
- **North Indian Diamond Chart SVG:** Custom inline SVG chart renderer (`renderChart()` in lines 503–532). Accurately positions house numbers and planets in classical diamond/triangle geometry.
- **Visual Palette:** Clean deep blues with gold accents. Dignity badges (Exalted in green, Debilitated in red, Own Sign in gold) provide immediate visual clarity.
- **Inlined Script Bloat:** The entire 1,100-line `kundali.js` file is duplicated directly inside `kundali.html` (lines 371–1541), creating an 82 KB HTML file with redundant inline logic.

### 3. UX & Interaction Observations
- **Relative Path Resolution Defect (P0):** Line 767 executes `fetch('api/kundali', ...)`, and line 468 executes `fetch('api/cities', ...)`. Without a leading slash `/`, accessing `/kundali/` (with trailing slash) attempts to fetch `/kundali/api/kundali`, returning 404.
- **Hardcoded Remote URL Fallback:** Lines 376–379 contain:
  ```javascript
  const API_URL = window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1"
    ? "http://127.0.0.1:8000"
    : "https://astrologic-vedic-1.onrender.com";
  ```
  This hardcodes an external third-party Render URL. If deployed to any other domain, client requests risk pointing to a stale or dormant server.
- **PDF Download Hijack & Fake PDF (P1):** Clicking the "⬇ PDF" button does not download a generated PDF from `/api/download-kundali`. Instead, line 901 forces the user to complete an intrusive testing feedback modal (`openFeedbackModal`). Once submitted, line 973 opens a new browser window and writes raw unstyled HTML via `window.open("", "_blank").document.write(...)`. This is not a real PDF document and causes popup blockers to trigger on mobile browsers.
- **Birth Time Input (Timezone Risk):** The birth time label specifies `Time of Birth (IST)`. It does not support time zone offsets for international births (e.g., London, New York), even though the calculation engine supports coordinate lookups.

### 4. Responsive Design & Touch Usability
- **Chart Layout Stacking:** On desktop, D1 and D9 charts sit side-by-side (`grid-template-columns: 1fr 1fr`). On screens below 900px, they stack vertically. However, the SVGs use a fixed `viewBox="0 0 600 420"` with small 10px text that becomes difficult to read on 375px mobile screens.
- **Table Touch Targets:** The Navagraha table has 9 columns (`Planet`, `Sign`, `Degree`, `House`, `Nakshatra`, `Pada`, `Navamsa`, `Strength`, `Status`). On mobile, it scrolls horizontally across 700px, which causes touch-scroll conflicts with page scrolling.

### 5. Accessibility (WCAG 2.2 AA)
- **SVG Chart Inaccessibility:** The generated North Indian SVG chart lacks `<title>`, `<desc>`, and ARIA roles. Screen readers perceive the entire chart as an invisible block.
- **Input Labels:** Date and time inputs lack explicit `id`/`for` association in `<label>`.

### 6. Technical UX
- **Performance:** Rendering all 12 house cards, full dasha timeline, yoga lists, and SVG charts creates significant DOM reflows upon form submission.
- **State Loss on Refresh:** If a user refreshes the page, their entered birth details and generated chart vanish completely because data is held only in JavaScript memory (`_data`).

### 7. Evaluation Scores
| Dimension | Score (1-10) | Evidence & Justification |
| :--- | :---: | :--- |
| **Visual Design** | 8.0 | Crisp SVG North Indian charts, professional badge hierarchy, cohesive palette. |
| **Usability** | 5.5 | Relative fetch paths risk 404s, intrusive feedback modal intercepts PDF download. |
| **Navigation** | 6.5 | Standard header, missing language toggle, profile button redirects guest to login. |
| **Responsive Design** | 6.5 | SVG charts stack cleanly on tablet, but text scaling degrades on mobile viewports. |
| **Accessibility** | 4.0 | SVG charts are completely inaccessible to screen readers, missing ARIA table headers. |
| **Content Hierarchy** | 8.5 | Logical breakdown: Input → Details → Charts → Planets → Strengths → Yogas → Dasha. |
| **Interaction Feedback** | 6.0 | Toast notifications function well; feedback modal feels coercive before download. |
| **Overall Polish** | 6.5 | Outstanding calculation presentation hampered by script duplication and download hijacking. |

### 8. Recommended Improvements & Acceptance Criteria
- **Fix 1 (P0):** Fix all fetch URLs to absolute paths (`/api/kundali`, `/api/cities`) and remove the hardcoded Render URL fallback.
  - *Acceptance Criteria:* Generating a Kundali succeeds at `/kundali`, `/kundali/`, and custom domain deployments.
- **Fix 2 (P1):** Connect the PDF download button directly to the backend endpoint `GET /api/download-kundali` to stream a clean, branded PDF report.
  - *Acceptance Criteria:* Clicking "⬇ PDF" immediately prompts a file download of `AstroLogic_Kundali_Report.pdf`.
- **Fix 3 (P1):** Persist the generated chart into `sessionStorage` or user profile so a page refresh does not erase the user's reading.

---

## Page 4: Daily Horoscope (`/horoscope` and `/{lang}/horoscope`)

### 1. Page Purpose & Target User Journey
- **Purpose:** Deliver dynamic transit-based daily horoscope insights for all 12 zodiac signs. Presents transit overview, Love/Career/Health domain summaries, 5-star ratings, planetary influence bars, and lucky attributes (number, color, gem, ruling planet, auspicious direction).
- **Target User:** Casual readers checking daily transit guidance.
- **Primary CTA:** Zodiac sign pill selector (`.zodiac-strip`).

### 2. Visual Design & Aesthetics
- **Zodiac Strip:** Smooth horizontal carousel of 12 zodiac signs with custom glyphs (`♈`, `♉`, etc.), Latin names, and element tags (Fire, Earth, Air, Water). Active sign features a vibrant gold gradient.
- **Influence Bars:** Custom horizontal visualizer showing planetary influence (positive vs negative net impact) with retrograde badges (`⟲R`).
- **Sidebar Card:** Lucky numbers, colors, mantras, and compatible signs styled in a neat high-contrast card.

### 3. UX & Interaction Observations
- **URL Parameter Ignored Bug (P1):** The homepage and navigation links route to `/horoscope?sign=4` (Leo). However, `daily-horoscope.html` **never inspects `window.location.search`**. Line 495 hardcodes `loadHoroscope(0)` (Aries). Clicking any sign on the homepage or external link always defaults to Aries.
- **Developer Error Leakage (P1):** Lines 427–432 contain the following error message rendered when the API fails:
  ```html
  <div>Could not load horoscope data.<br>
  Ensure <code>festival_engine.py</code> is installed in <code>app/astrology/</code> and the API route is registered.</div>
  ```
  Exposing internal file names and folder structures to end consumers is an egregious UX and information-disclosure defect.
- **Swipe Gesture Conflict:** Lines 486–492 add a `touchstart`/`touchend` listener to swipe between signs. Because it lacks a vertical-delta check, scrolling vertically on mobile can inadvertently trigger a horizontal sign change.

### 4. Responsive Design & Touch Usability
- **Sidebar Stacking:** The 2-column layout (`1fr 360px`) collapses smoothly on screens under 900px.
- **Zodiac Carousel:** Touch scrolling on `.zodiac-scroll` is smooth with a customized webkit scrollbar.

### 5. Accessibility (WCAG 2.2 AA)
- **Star Ratings:** Star indicators (`sOverall`, `sLove`, etc.) render raw Unicode characters (`★★★★☆`) without accessible text labels like `aria-label="4 out of 5 stars"`. Screen readers announce "black star black star black star black star white star".
- **Element Pills:** Color pills for Fire, Earth, Air, and Water have good contrast, but rely strictly on color tags.

### 6. Technical UX
- **Client-Side Caching:** Lines 416–425 implement an efficient client-side date-keyed cache (`_cache[`${signIdx}-${today}`]`), preventing duplicate network requests when switching between signs.

### 7. Evaluation Scores
| Dimension | Score (1-10) | Evidence & Justification |
| :--- | :---: | :--- |
| **Visual Design** | 8.5 | Excellent layout, planetary influence bars, and cohesive element styling. |
| **Usability** | 5.5 | Query parameters are ignored (always resets to Aries); touch swipe hijacks scroll. |
| **Navigation** | 7.0 | Clean header, though profile link exhibits the universal guest state bug. |
| **Responsive Design** | 7.5 | Clean grid collapse on mobile, easy-to-tap zodiac selection pills. |
| **Accessibility** | 5.0 | Star ratings read out awkwardly on screen readers; no keyboard arrow navigation on carousel. |
| **Content Hierarchy** | 8.5 | Great hierarchy: Sign Strip → Overview → Ratings → Domains → Lucky Sidebar. |
| **Interaction Feedback** | 7.5 | Skeleton loading placeholders provide pleasant perceived performance. |
| **Overall Polish** | 6.5 | Visually gorgeous, but ruined by the query parameter bug and internal developer error leak. |

### 8. Recommended Improvements & Acceptance Criteria
- **Fix 1 (P1):** Parse `URLSearchParams` on page load: `const initialSign = parseInt(new URLSearchParams(location.search).get('sign')) || 0; loadHoroscope(initialSign);`.
  - *Acceptance Criteria:* Navigating to `/horoscope?sign=7` loads Scorpio immediately.
- **Fix 2 (P1):** Replace internal developer error message with user-friendly fallback ("Horoscope data currently unavailable. Please try again later.").
- **Fix 3 (P2):** Add `aria-label` to star ratings and keyboard arrow-key navigation to sign selector.

---

## Page 5: Predictions & 10 Life Domains (`/prediction` and `/{lang}/prediction`)

### 1. Page Purpose & Target User Journey
- **Purpose:** The core AI prediction engine. Synthesizes natal charts across 10 distinct life domains: Marriage, Career, Wealth, Health, Children, Education, Property, Challenges, Travel, and Spirituality. Displays timing windows, dasha activation status, and planetary remedies.
- **Target User:** Users seeking actionable life guidance and calendar timing for critical decisions.
- **Primary CTA:** "Analyse All 10 Domains ✦" (`#analyseBtn`).

### 2. Visual Design & Aesthetics
- **Domain Cards & Overview:** Clean 5-column overview grid showing domain icons, scores (0–100%), and progress bars with color thresholds (Green > 70%, Gold 50–70%, Red < 50%).
- **Deep Insight Panels:** Specialized indicator rows for each domain (e.g., Marriage Type, Mangal Dosh, Partner Traits for Marriage; Sector, Business vs Job for Career; Vulnerable Organs, Prakriti for Health).

### 3. UX & Interaction Observations
- **Immediate Feedback Modal Interruption (P0 Usability Blocker):** Lines 479–484 trigger `openFeedbackModal("prediction", person, ...)` **immediately** inside the `analyse()` success callback. As soon as the user clicks "Analyse" and the calculation completes, a full-screen blocking modal appears asking "How accurate was the reading? Select: Very Accurate / Mostly Accurate / Average / Not Accurate". The user has not had a single second to read their prediction! This is a critical usability failure.
- **No Data Pre-population from Profile or Kundali:** Despite requiring identical birth inputs (Name, DOB, TOB, City), the page never checks `localStorage`, cookies, or user profile to pre-fill the form.
- **Chat Interface Absence:** While `prediction.py` contains an endpoint `POST /api/chat`, `prediction.html` has no chat input or message stream. Users expecting to chat with AstroAI find no interface.

### 4. Responsive Design & Touch Usability
- **Domain Tabs Wrapping:** On mobile screens (375px), 10 domain tab buttons wrap across 4 rows, consuming half the viewport height before content begins.
- **Panel Layout Stacking:** The 2-column detail layout (`1fr 340px`) collapses vertically below 900px, placing remedies and timing windows below the long analysis text.

### 5. Accessibility (WCAG 2.2 AA)
- **Tab Semantics:** Domain tabs (`.d-tab`) are implemented as `<div>` elements without `role="tab"`, `role="tablist"`, or `aria-selected` attributes. Screen readers cannot navigate them as a tabbed interface.
- **Color Threshold Contrast:** Light green text (`#4ade80`) on light gray card backgrounds fails WCAG contrast requirements.

### 6. Technical UX
- **Payload & Endpoint:** Calls `POST /api/domains` with JSON payload. Endpoint performs heavy multi-domain calculations synchronously, taking 800ms–1500ms without an animated progress indicator.

### 7. Evaluation Scores
| Dimension | Score (1-10) | Evidence & Justification |
| :--- | :---: | :--- |
| **Visual Design** | 8.0 | Rich domain cards, structured badge hierarchy, clean timing window cards. |
| **Usability** | 4.0 | Aggressive immediate feedback modal blocks reading results; no auto-fill. |
| **Navigation** | 6.5 | Standard header, missing language switcher, no cross-linking to Kundali. |
| **Responsive Design** | 6.0 | Domain tabs consume excessive vertical space on mobile screens. |
| **Accessibility** | 4.5 | `div`-based tabs without ARIA roles; low-contrast score text. |
| **Content Hierarchy** | 8.0 | Strong hierarchy: Input → Overview Scoreboard → Domain Tabs → Detailed Insights. |
| **Interaction Feedback** | 4.0 | Disastrous premature modal popup ruins an otherwise smooth calculation flow. |
| **Overall Polish** | 5.5 | High-value prediction content severely degraded by intrusive feedback mechanics. |

### 8. Recommended Improvements & Acceptance Criteria
- **Fix 1 (P0):** Remove the automated feedback modal popup from the calculation callback. Move feedback capture to a subtle inline prompt at the bottom of the page.
  - *Acceptance Criteria:* Submitting birth details immediately displays the domain overview and analysis text without modal interruptions.
- **Fix 2 (P1):** Automatically pre-fill the birth details form if the user has an active session, a saved profile, or generated a chart on `/kundali`.
- **Fix 3 (P2):** Convert `.d-tab` into semantic `<button role="tab">` elements inside a scrollable horizontal tab bar on mobile.

---

## Page 6: Blogs & Articles (`/blogs` and `/{lang}/blogs`)

### 1. Page Purpose & Target User Journey
- **Purpose:** Content marketing, educational repository, and SEO traffic driver. Allows users to browse, search, and filter astrology articles across categories (Vedic, Transits, Nakshatras, Remedies, Philosophy).
- **Target User:** Seekers learning about astrological concepts and principles.
- **Primary CTA:** Article cards leading to individual blog posts.

### 2. Visual Design & Aesthetics
- **Hero & Featured Card:** Featured post card with gold gradient border and prominent metadata (date, read time).
- **2-Column Article Grid:** Clean cards with category pill, title, excerpt, and "Read →" link.

### 3. UX & Interaction Observations
- **Broken Article Links (P0 Blocker):** Lines 328, 341, and 356 generate anchor tags pointing to `/blogs/${b.id}`:
  ```javascript
  feat.innerHTML = `<a href="/blogs/${first.id}" class="featured-post">...</a>`;
  grid.innerHTML = rest.map(b => `<a href="/blogs/${b.id}" class="blog-card">...</a>`);
  ```
  However, the FastAPI route in `app/api/routes/pages.py:83` is registered as:
  ```python
  @router.get("/blog/{blog_id}", response_class=HTMLResponse)
  ```
  Notice the singular `/blog/` vs plural `/blogs/`! **Every single blog link in the application leads to a 404 Not Found error!**
- **Client-Side Search & Filter:** Search input (`#searchInput`) and category pills filter articles in real time. Works smoothly on preloaded data.
- **Static Fallback Data:** Lines 280–289 fetch `/api/blogs`. If empty or offline, falls back to hardcoded `STATIC_BLOGS`.

### 4. Responsive Design & Touch Usability
- **Sidebar Stacking:** The 2-column layout (`1fr 300px`) collapses cleanly below 900px.
- **Category Pills:** Horizontal flex-wrap works well across viewport sizes.

### 5. Accessibility (WCAG 2.2 AA)
- **Search Input:** Search box has an icon but lacks an explicit `<label for="searchInput">` or `aria-label="Search articles"`.
- **Read More Links:** Multiple identical "Read →" links violate WCAG 2.4.4 (Link Purpose in Context) without aria-labels referencing the article title.

### 6. Technical UX
- **Performance:** Lightweight client-side rendering. Excerpt generation safely strips HTML tags.

### 7. Evaluation Scores
| Dimension | Score (1-10) | Evidence & Justification |
| :--- | :---: | :--- |
| **Visual Design** | 8.0 | Elegant editorial card grid, balanced typography, clear category badges. |
| **Usability** | 2.5 | 100% of article links are broken due to route path mismatch (`/blogs/` vs `/blog/`). |
| **Navigation** | 6.0 | Standard header; footer contains public link to `/admin/blogs`. |
| **Responsive Design** | 8.0 | Clean grid collapse, responsive search bar and category filters. |
| **Accessibility** | 5.5 | Missing search label, non-descriptive "Read →" link text. |
| **Content Hierarchy** | 8.5 | Search & Filters → Featured Post → Article Grid → Recent Sidebar. |
| **Interaction Feedback** | 7.5 | Instant filter responsiveness with pleasant empty state icon. |
| **Overall Polish** | 4.0 | Beautiful interface rendered completely unusable by broken routing. |

### 8. Recommended Improvements & Acceptance Criteria
- **Fix 1 (P0):** Update all blog card link templates in `blogs.html` to point to `/blog/${b.id}` instead of `/blogs/${b.id}` (or add a redirect route in `pages.py`).
  - *Acceptance Criteria:* Clicking any article card opens `blog-detail.html` with full article content.
- **Fix 2 (P2):** Add `aria-label="Read full article: ${b.title}"` to all card links.

---

## Page 7: Blog Article Detail (`/blog/{blog_id}`)

### 1. Page Purpose & Target User Journey
- **Purpose:** Focused reading experience for an individual astrological article.
- **Target User:** Readers consuming long-form content.
- **Primary CTA:** "← Back to Articles" link (`/blogs`).

### 2. Visual Design & Aesthetics
- **Typography:** `Crimson Pro` body text with 19px font size and 1.85 line-height provides an excellent editorial reading experience. Max reading width constrained to 740px.
- **Layout Shift Bug (P1):** Line 18 defines:
  ```css
  header{position:fixed;top:0;height:var(--hh); ... --hh:72px;}
  .page-wrap{padding-top:calc(var(--hh)+60px);}
  ```
  Every other page in the application uses `position: sticky; height: 68px;`. When navigating from `/blogs` to `/blog/1`, the header jumps 4px in height and switches from sticky to fixed, causing an abrupt layout shift.

### 3. UX & Interaction Observations
- **Missing Kundali Link in Navigation (P1):** Lines 75–83 define the header navbar:
  ```html
  <nav><ul>
    <li><a href="/">Home</a></li>
    <li><a href="/panchang.html">Panchang</a></li>
    <li><a href="/horoscope">Horoscope</a></li>
    <li><a href="/prediction">Predictions</a></li>
    <li><a href="/blogs" class="active">Blogs</a></li>
    <li><a href="/about">About</a></li>
    <li><a href="/profile">Profile</a></li>
  </ul></nav>
  ```
  **Kundali is completely absent from the navbar!** On the flagship product where Kundali is the primary value proposition, users reading an article have no way to access the Kundali generator without going back to Home.
- **Raw Newline Rendering:** Line 60 uses `white-space: pre-line;` on `.article-body`. If an article contains HTML formatting, tags are rendered as plain escaped text.

### 4. Responsive Design & Touch Usability
- Reading column scales down to 17px body font at 768px. Clean margins and readable line lengths.

### 5. Accessibility (WCAG 2.2 AA)
- Good contrast, semantic `<h1>` article title. Lacks breadcrumb navigation (`Home > Blogs > Article`).

### 6. Technical UX
- Line 113 reads `const blogId = "{{ blog_id }}";` injected via Jinja2 context, and fetches `/api/blogs/${blogId}`. If the blog ID does not exist, it displays "Article not found" gracefully.

### 7. Evaluation Scores
| Dimension | Score (1-10) | Evidence & Justification |
| :--- | :---: | :--- |
| **Visual Design** | 8.0 | Clean editorial typography, distraction-free reading column. |
| **Usability** | 6.5 | Navigating here causes header layout shift; Kundali missing from nav. |
| **Navigation** | 5.0 | Core feature (Kundali) missing from navbar; fixed header jumps 4px. |
| **Responsive Design** | 8.5 | Clean typography scaling and fluid margins across mobile devices. |
| **Accessibility** | 7.0 | Clean heading hierarchy, though missing breadcrumb trail. |
| **Content Hierarchy** | 8.5 | Back Link → Title → Date/Author → Article Body → Footer. |
| **Interaction Feedback** | 7.0 | Clean error state if blog ID is invalid. |
| **Overall Polish** | 6.5 | Great reading typography ruined by inconsistent header dimensions and missing nav link. |

### 8. Recommended Improvements & Acceptance Criteria
- **Fix 1 (P1):** Restore `<a href="/kundali">Kundali</a>` to the navigation menu.
- **Fix 2 (P1):** Align header to global standard (`position: sticky; height: 68px;`).

---

## Page 8: About Platform & Vedic Science (`/about` and `/{lang}/about`)

### 1. Page Purpose & Target User Journey
- **Purpose:** Establish brand authority, educate visitors on Vedic astrology vs Western astrology, explain the 9 Grahas (Navagrahas), 27 Nakshatras, 12 Bhavas, Vimshottari Dasha, and Swiss Ephemeris mathematical precision.
- **Target User:** Skeptics, students, and new users seeking to understand the scientific foundation of the platform.

### 2. Visual Design & Aesthetics
- **Pillars & Tables:** High quality. Features 3 core philosophy pillars, a complete 9-planet reference table (Graha, Sanskrit name, Nature, Ruling Sign, Exaltation, Signification), and an interactive 27-nakshatra 9-column grid.
- **Visual Harmony:** Uses `Cinzel` and `Crimson Pro` harmoniously with gold gradient dividers.

### 3. UX & Interaction Observations
- **Missing In-Page Anchors:** The footer on the homepage links to `/about#nakshatras` and `/about#dashas`. However, `about.html` lacks `id="nakshatras"` and `id="dashas"` attributes on its section headers, so clicking those footer links fails to scroll to the target sections.
- **Header State:** Still displays `Profile` and `Logout` for unauthenticated visitors.

### 4. Responsive Design & Touch Usability
- **Nakshatra Grid Collapse:** The 9-column nakshatra grid collapses cleanly to 3 columns on tablet and 2 columns on mobile.
- **Table Horizontal Scroll:** Planet table scrolls cleanly within `.planet-table-wrap`.

### 5. Accessibility (WCAG 2.2 AA)
- Good table markup with `<thead>` and `<th>` tags. Lacks caption or summary on the table.

### 6. Evaluation Scores
| Dimension | Score (1-10) | Evidence & Justification |
| :--- | :---: | :--- |
| **Visual Design** | 8.5 | High-quality educational layout, rich astronomical reference tables. |
| **Usability** | 7.5 | Informative and engaging, though anchor links from footer fail. |
| **Navigation** | 7.0 | Standard header, missing language dropdown. |
| **Responsive Design** | 8.0 | Nakshatra grid and planet table adapt smoothly across breakpoints. |
| **Accessibility** | 7.0 | Proper table headers, readable contrast, logical heading hierarchy. |
| **Content Hierarchy** | 9.0 | Hero → Philosophy → Navagrahas → Nakshatras → Houses → Dasha → CTA. |
| **Interaction Feedback** | 7.5 | Subtle hover effects on nakshatra cards. |
| **Overall Polish** | 8.0 | One of the most polished and complete content pages on the platform. |

### 7. Recommended Improvements & Acceptance Criteria
- **Fix 1 (P2):** Add `id="nakshatras"` and `id="dashas"` to the respective section headings.

---

## Page 9: User Login & Registration (`/login` and `/signup`)

### 1. Page Purpose & Target User Journey
- **Purpose:** User authentication and registration. Allows users to create an account or sign in to access their saved profile, birth details, and activity telemetry.
- **Target User:** Returning users logging in or new users creating an account.
- **Primary CTA:** "Login" (`#submitBtn`) on `/login`; "Create Account" on `/signup`.

### 2. Visual Design & Aesthetics
- **Split-Screen Layout:** 2-column shell (`1fr 430px`) on desktop. Left column features branded display typography ("Return To Your Astro Space."); right column holds the frosted glass card.
- **Aesthetic Quality:** Very clean, modern, dark glassmorphism card with gold gradient button.

### 3. UX & Interaction Observations
- **Silent Authentication Failure Bug (P0 Blocker):** Lines 341 in `auth.html` defines `<div class="alert error" id="errorBox"></div>`. However, the template contains **zero Jinja2 tags** to print the server-provided error message! In `auth.py`, when credentials fail:
  ```python
  return _render_auth_page(request, mode="login", error="Invalid email or password", title="User Login")
  ```
  Because `auth.html` does not include `{% if error %}{{ error }}{% endif %}` or populate `#errorBox`, **the user receives zero feedback when their password is incorrect!** The page silently reloads with empty password inputs.
- **Recursive Back Link Bug (P2):** On `/login`, line 399 renders `<a class="back-link" href="/login">Back to Login</a>`. Clicking "Back to Login" while already on `/login` is redundant and confusing.
- **Strict Phone Requirement for Signup:** On `/signup`, lines 432–433 set `phoneInput.required = true` with a strict regex. For international users or users who only want to sign up with email, forcing a mobile number creates high signup drop-off.
- **No Password Visibility Toggle:** The password input has no "show/hide password" eye icon, increasing input errors on mobile touch keyboards.

### 4. Responsive Design & Touch Usability
- Below 860px, the 2-column layout stacks vertically. Mobile inputs are comfortably sized (padding 12px 14px, font size 14px preventing iOS auto-zoom).

### 5. Accessibility (WCAG 2.2 AA)
- Inputs have associated `<label>` tags. Error alert lacks `role="alert"` and `aria-live="assertive"`.

### 6. Evaluation Scores
| Dimension | Score (1-10) | Evidence & Justification |
| :--- | :---: | :--- |
| **Visual Design** | 8.5 | Sleek split-screen layout, beautiful glassmorphism card, gold CTA. |
| **Usability** | 3.5 | Failed logins fail silently without displaying error messages to the user. |
| **Navigation** | 7.0 | Clean switch between login and signup, though "Back to Login" on login page is redundant. |
| **Responsive Design** | 8.0 | Stacks cleanly on mobile viewports; input fields meet touch guidelines. |
| **Accessibility** | 6.0 | Missing `aria-live` on error container, no password visibility toggle. |
| **Content Hierarchy** | 8.5 | Clean copy hierarchy: Brand → Eyebrow → Title → Form → Switch Link. |
| **Interaction Feedback** | 2.5 | Zero error display upon authentication failure. |
| **Overall Polish** | 4.5 | Visually stunning, but functionally crippled by the missing error tag. |

### 7. Recommended Improvements & Acceptance Criteria
- **Fix 1 (P0):** Add `{% if error %}<div class="alert error" id="errorBox" style="display:block;">{{ error }}</div>{% endif %}` to `auth.html`.
  - *Acceptance Criteria:* Submitting invalid credentials displays "Invalid email or password" in a red alert box above the form.
- **Fix 2 (P2):** Add a toggle eye icon to inspect entered passwords.
- **Fix 3 (P2):** Make phone number optional during registration.

---

## Page 10: User Profile & Saved Details (`/profile`)

### 1. Page Purpose & Target User Journey
- **Purpose:** User account dashboard. Allows authenticated users to view and update their personal details (Name, Phone, Birth Date, Birth Time, Birth City, Zodiac Sign, Personal Notes) and review their recent activity telemetry stream.
- **Target User:** Registered users maintaining their birth profile.
- **Primary CTA:** "Save Profile" (`.btn-save`).

### 2. Visual Design & Aesthetics
- **Layout:** 2-column grid (`1fr 340px`) holding the Profile Details form on the left and Account Summary / Recent Activity on the right.
- **Uncommented Legacy Code Artifact:** Lines 1–26 contain raw, unstyled commented-out HTML from early development (`<!-- <h2>User Profile</h2> ... <a href="/logout">Logout</a> -->`).

### 3. UX & Interaction Observations
- **Save Profile Redirect Trap (P1):** When a user updates their birth details and clicks "Save Profile", `auth.py:200` executes:
  ```python
  return RedirectResponse("/", status_code=303)
  ```
  It redirects the user away from their profile to the HOMEPAGE (`/`)! The user receives no success banner, no confirmation toast, and must manually navigate back to `/profile` to verify if their changes were saved.
- **Missing Nav Item:** In `profile.html:514-522`, the navbar includes Home, Panchang, Kundali, Horoscope, Predictions, Blogs, Profile—**About is completely missing!**
- **Zodiac Sign Input Type:** Zodiac sign is an unvalidated plain text input (`<input name="zodiac_sign" placeholder="Aries">`) instead of a constrained `<select>` dropdown of the 12 valid zodiac signs.

### 4. Responsive Design & Touch Usability
- The 2-column layout collapses cleanly to 1 column on screens below 840px. Form inputs use 2-column grids that collapse to 1 column on mobile.

### 5. Accessibility (WCAG 2.2 AA)
- Form inputs have associated `<label>` tags. Recent activity stream items lack semantic list markup (`<div class="activity-list">` instead of `<ul>`/`<li>`).

### 6. Evaluation Scores
| Dimension | Score (1-10) | Evidence & Justification |
| :--- | :---: | :--- |
| **Visual Design** | 7.8 | Clean form layout, pleasant summary sidebar, cohesive gold/navy palette. |
| **Usability** | 4.5 | Submitting form kicks user back to homepage without confirmation; plain text zodiac input. |
| **Navigation** | 6.0 | About link missing from navbar; profile button in header links to current page. |
| **Responsive Design** | 8.0 | Fluid collapse from 2-column to 1-column layout on mobile. |
| **Accessibility** | 6.5 | Labels present, but activity items lack semantic list structure. |
| **Content Hierarchy** | 8.0 | Hero Banner → Form Grid → Account Cards → Recent Activity. |
| **Interaction Feedback** | 4.0 | No success alert or toast on profile update. |
| **Overall Polish** | 5.5 | Functional dashboard damaged by confusing redirect behavior and leftover commented code. |

### 7. Recommended Improvements & Acceptance Criteria
- **Fix 1 (P1):** Change `auth.py:200` to redirect back to `/profile?saved=true` and display a green success banner: "Profile updated successfully".
  - *Acceptance Criteria:* Clicking "Save Profile" keeps user on `/profile` with updated values and a clear success indicator.
- **Fix 2 (P2):** Convert `zodiac_sign` input to a `<select>` dropdown containing the 12 signs.
- **Fix 3 (P3):** Remove commented-out HTML snippet (lines 1–26).

---

## Pages 11–15: Administrator Portal (`/admin/*`)

### 1. Route Inventory & Roles
- `GET /admin/login` (`admin-login.html`) — Admin Authentication Form
- `GET /admin/blogs` (`admin-blog.html`) — Blog Post Management & Editor (CRUD)
- `GET /admin/users` (`admin-users.html`) — Registered Users & Saved Profiles Registry
- `GET /admin/activity` (`admin-activity.html`) — System-wide Activity Telemetry Feed
- `GET /admin/feedback` (`admin-feedback.html`) — Testing Feedback Ratings & Comments

### 2. Visual Design & Layout Structure
- **Persistent Admin Sidebar:** 248px fixed dark sidebar (`background: rgba(1,8,18,0.95); border-right: 1px solid var(--border)`).
- **Branding Drift:** The sidebar logo displays `Astro*Logic` (with an asterisk `*`), whereas public pages use `Astro✦Logic` (with a diamond star `✦`) or `AstroLogic`.
- **Consistency Across Admin Pages:** High visual cohesion between the 4 dashboard views: 3-column top stat cards, top action pill buttons, and responsive data tables with rounded badges.

### 3. UX & Interaction Observations
- **CSRF Token Absence (Security/UX Risk):** Admin blog creation, update, and deletion forms (`admin-blog.html`) submit plain `POST` requests without CSRF protection tokens.
- **No Confirmation Dialog on Deletion:** Deleting a blog post executes immediately without a confirmation modal or prompt.
- **Table Paging & Truncation:** User activity (`admin-activity.html`) and feedback (`admin-feedback.html`) limit query results to 100/200 rows with no pagination controls. On a production system with thousands of events, historical data cannot be accessed.

### 4. Responsive Design & Touch Usability
- At `@media(max-width: 900px)`, the sidebar converts from `position: fixed` to `position: static`, and the data tables allow horizontal scrolling.

### 5. Evaluation Scores (Admin Portal Average)
| Dimension | Score (1-10) | Evidence & Justification |
| :--- | :---: | :--- |
| **Visual Design** | 8.0 | Clean professional admin dashboard, consistent stats cards, neat badge styling. |
| **Usability** | 7.0 | Straightforward CRUD, though lacks deletion confirmations and search/pagination. |
| **Navigation** | 8.5 | Highly coherent sidebar with active state indicators across all admin routes. |
| **Responsive Design** | 7.5 | Sidebar unsticks smoothly on mobile viewports; tables scroll horizontally. |
| **Accessibility** | 6.5 | Good contrast, standard table markup; lacks pagination ARIA controls. |
| **Content Hierarchy** | 8.5 | Sidebar → Header & Actions → Top Metrics → Data Table. |
| **Interaction Feedback** | 6.5 | Error banner displays properly on login; lacks inline validation on blog form. |
| **Overall Polish** | 7.5 | Functional, reliable back-office portal. |
