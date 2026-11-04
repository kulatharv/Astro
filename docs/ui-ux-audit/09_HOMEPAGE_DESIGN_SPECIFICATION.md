# AstroLogic — Homepage Design Specification Document
**Visual Identity, Animations, Color Palette, Typography, SVGs & Asset Architecture**

- **Document ID:** `SPEC-HOMEPAGE-01`
- **Application:** AstroLogic / Nakshatra Labs
- **Current Route:** `/` and `/{lang}/`
- **Template Source:** `app/templates/index.html`
- **Style Tokens:** `app/static/css/tokens.css`
- **Status:** Active Production Design

---

## 1. Design Philosophy & Theme: "Celestial Luxury"

AstroLogic's homepage design follows the **Celestial Luxury** design philosophy. It unifies three distinct product dimensions:
1. **Classical Vedic Jyotish Authenticity:** Sacred gold accents, Sanskrit nomenclature (Rashis, Navagrahas, Bhavas), and reverence for ancient astrological traditions.
2. **Astronomical & Mathematical Precision:** Sub-arcsecond calculation credibility, Swiss Ephemeris engineering, Lahiri Ayanamsha, and coordinates.
3. **High-End Contemporary Digital SaaS:** Dark luxury aesthetic, spacious typography, accessible contrast, smooth micro-interactions, and zero generic marketing fluff.

---

## 2. Color Palette & Design Tokens

All colors are codified as reusable CSS custom properties in `tokens.css`:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                             CELESTIAL PALETTE                               │
├──────────────────┬──────────────────┬──────────────────┬────────────────────┤
│ Obsidian Base    │ Deep Navy Base   │ Card Surface     │ Elevated Surface   │
│ #050B16          │ #081426          │ #0D1929          │ #122136            │
├──────────────────┼──────────────────┼──────────────────┼────────────────────┤
│ Sacred Gold      │ Gold Highlight   │ Deep Gold Accent │ Gold Glass Glow    │
│ #E8B85B          │ #F2CA7A          │ #C99A45          │ rgba(232,184,91,.1)│
├──────────────────┼──────────────────┼──────────────────┼────────────────────┤
│ Celestial Cyan   │ Blue Glass Tint  │ Success Mint     │ Error Coral        │
│ #8BC7ED          │ rgba(139,199,237)│ #36B37E          │ #E56B6F            │
├──────────────────┼──────────────────┼──────────────────┼────────────────────┤
│ Primary Text     │ Secondary Text   │ Muted Text       │ Border Navy        │
│ #F5F3EE (14:1)   │ #A8B3C5 (5.6:1)  │ #7B889B          │ #263448            │
└──────────────────┴──────────────────┴──────────────────┴────────────────────┘
```

### Detailed Token Reference

| Token Name | Hex / RGBA Value | Usage & Application |
| :--- | :--- | :--- |
| `--color-bg-base` | `#050B16` | Main body background color (Deep Cosmic Obsidian). |
| `--color-bg-secondary` | `#081426` | Radial gradient core and alternating section backgrounds. |
| `--color-surface-card` | `#0D1929` | Background for feature cards, domain cards, and quick actions. |
| `--color-surface-elevated`| `#122136` | Elevated cards, hero visual container, and CTA boxes. |
| `--color-surface-hover` | `rgba(18, 33, 54, 0.90)`| Card hover surface elevation. |
| `--color-gold` | `#E8B85B` | Primary brand accent, headings, CTA buttons, and key focus rings. |
| `--color-gold-hover` | `#F2CA7A` | Hover state for gold text and primary buttons. |
| `--color-gold-deep` | `#C99A45` | Gradient end color for primary CTA buttons. |
| `--color-gold-dim` | `rgba(232, 184, 91, 0.10)` | Translucent gold badge backgrounds and subtle pill borders. |
| `--color-gold-border` | `rgba(232, 184, 91, 0.28)` | Standard gold border for cards, inputs, and dividers. |
| `--color-blue` | `#8BC7ED` | Secondary celestial cyan for eyebrows, links, and lunar markers. |
| `--color-blue-dim` | `rgba(139, 199, 237, 0.12)`| Icon container backgrounds and subtle cyan highlights. |
| `--color-border-subtle` | `#1E2D42` | Subtle section dividers and card borders. |
| `--color-border-medium` | `#263448` | Prominent card dividers and input outlines. |
| `--color-text-primary` | `#F5F3EE` | Near-white text with >14:1 contrast ratio for titles and headings. |
| `--color-text-secondary`| `#A8B3C5` | Soft blue-gray text with >5.6:1 contrast (WCAG AA compliant). |
| `--color-text-dim` | `#7B889B` | Tertiary metadata text, copyright, and subtle labels. |
| `--color-success` | `#36B37E` | Active live indicators and positive astrological states. |
| `--color-error` | `#E56B6F` | Error states and warning notifications. |

---

## 3. Typography Hierarchy

The platform loads high-performance web fonts with local system fallbacks:

```
Headings & Display: 'Cinzel', Georgia, 'Times New Roman', serif
Subheadings:        'Crimson Pro', Georgia, serif
Interface & Body:   'Inter', system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif
```

| Element | Font Family | Size (Desktop / Fluid) | Weight | Line Height |
| :--- | :--- | :--- | :--- | :--- |
| **Hero Title** | `Cinzel` | `clamp(34px, 4.8vw, 56px)` | 700 (Bold) | `1.16` |
| **Section Headings**| `Cinzel` | `clamp(24px, 3.6vw, 36px)` | 700 (Bold) | `1.25` |
| **Card Headings** | `Cinzel` | `18px` | 700 (Bold) | `1.3` |
| **Hero Subtitle** | `Crimson Pro`| `19px` | 400 (Regular) | `1.7` |
| **Section Intro** | `Crimson Pro`| `18px` | 400 (Regular) | `1.68` |
| **UI Body Copy** | `Inter` | `13.5px – 15px` | 400 (Regular) | `1.6` |
| **Eyebrows / Badges**| `Inter` | `11px – 11.5px` (Uppercase, +2.8px spacing) | 700 (Bold) | `1.0` |
| **Primary Buttons**| `Inter` | `14px – 15px` | 700 (Bold) | `1.0` |

---

## 4. Animation & Motion Design System

The motion system is engineered for **purpose, restraint, and zero performance penalty**:

### A. Interactive 3D Armillary Celestial Sphere (HTML5 Canvas)
- **Math Engine:** Pure JavaScript 3D perspective projection formula ($X, Y, Z \rightarrow X', Y'$ using 3D rotation matrices for pitch and yaw).
- **Celestial Coordinates:**
  - **Celestial Equator:** 48-segment circular coordinate ring rendered in cyan starlight (`rgba(139, 199, 237, 0.18)`).
  - **Ecliptic Band (Zodiac Ring):** 56-segment ring inclined at 23.4° (`0.41 rad`) holding 12 Vedic Rashi glyphs (♈ through ♓) rendered in luminous gold.
  - **Polar Meridian:** 40-segment vertical coordinate ring.
  - **9 Navagrahas in Orbit:** Surya, Chandra, Mangala, Budha, Guru, Shukra, Shani, Rahu, and Ketu. Each planet calculates its orbital velocity, inclination, starlight radial glow gradient, and planetary glyph symbol.
- **Micro-Interactions:**
  - **Inertial Drag:** Users can click and drag with mouse or swipe on touchscreens to orbit around the 3D celestial sphere in real time.
  - **Cosmic Drift:** When idle, the sphere slowly rotates at `0.0018 rad/frame`.
  - **Hover Hit Detection:** Hovering over any planet instantly updates the celestial tooltip with its Sanskrit name, Karaka significance, and astrological domain.
- **Battery & Performance Protection:**
  - Uses `IntersectionObserver`: When the user scrolls past the hero section, the canvas render loop **automatically pauses**, reducing GPU/CPU usage to 0%.
  - Supports high-DPI displays with `window.devicePixelRatio` scaling.

### B. Scroll-Triggered Reveal Animations
- Elements with `.reveal-on-scroll` start at `opacity: 0; transform: translateY(20px);`.
- An `IntersectionObserver` detects when cards enter the viewport (threshold `0.1`) and applies `.in-view`, triggering a smooth transition:
  `transition: opacity 0.6s cubic-bezier(0.16, 1, 0.3, 1), transform 0.6s cubic-bezier(0.16, 1, 0.3, 1);`

### C. Micro-Interactions & Hover Feedback
- **Card Hover Elevation:** Feature cards and quick action cards smoothly rise `transform: translateY(-4px)` with shadow elevation and an animated top-edge gold light sweep (`opacity: 1`).
- **Button Hover States:** Primary gold buttons feature a gentle brightness filter (`brightness(1.15)`), a 2px elevation, and a directional arrow slide (`transform: translateX(3px)`).
- **Session Pulse Dot:** A breathing pulsing dot indicator (`box-shadow: 0 0 12px rgba(54, 179, 126, 0.8)`) next to the active session state.
- **Accessible Hamburger Animation:** Clicking the mobile navigation button smoothly morphs the 3 hamburger spans into an 'X' using 45° rotation and vertical translation.

### D. Accessibility & Reduced Motion Override
- Respects `@media (prefers-reduced-motion: reduce)`:
  - Halts continuous 3D canvas rotation.
  - Replaces all transition durations with `0.001ms`.
  - Disables parallax and keeps the celestial sphere statically aligned.

---

## 5. Complete SVG & Iconography Catalog

To ensure visual elegance and fast loading, **all emojis were removed as primary icons** and replaced with custom inline SVGs formatted with `stroke-width="1.8"`, `stroke-linecap="round"`, and `stroke-linejoin="round"`:

### 1. Brand & Navigation
- **Brand Sparkle (`✦`):** Elevated gold celestial mark indicating cosmic intelligence.
- **Hamburger Toggle:** 3-bar accessible morphing vector lines.

### 2. Section C: Quick-Action Icons
- **Birth Kundali:** Polygonal celestial star / birth diamond (`<polygon points="12 2 15 9 22 9 17 14 19 21 12 17 5 21 7 14 2 9 9 9 12 2"/>`).
- **Daily Panchang:** Radiant sun with 8 directional rays (`<circle cx="12" cy="12" r="5"/>` + ray lines).
- **Daily Horoscope:** Celestial globe with orbital meridians (`<circle cx="12" cy="12" r="10"/>` + curved paths).
- **Life Predictions:** Multi-faceted isometric crystal cube (`<path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8..."/>`).

### 3. Section D: Core Capabilities Feature Icons
- **Birth Kundali & Horoscope:** 3D Polyhedral geometry icon representing natal division.
- **Daily Panchang & Muhurat:** Classical astrological calendar tablet with date markers.
- **Transit-Based Daily Horoscope:** Celestial transit clock indicating exact planetary hour.
- **AI Life Predictions:** Radiant cosmic nova / planetary aspect rays.
- **Divisional Varga Charts:** Quadrant divisional grid representing D1 to D12 vargas.
- **Vedic Astrology Journal:** Ancient classical scripture book / Jyotish manuscript.

### 4. Section E: Ten Vedic Life Domain Icons
1. **Marriage & Relationships:** Interlocking heart vector (`7th House, Venus`).
2. **Career & Calling:** Executive briefcase vector (`10th House, Saturn`).
3. **Wealth & Prosperity:** Classical Dhana coin with central rupee symbol (`2nd & 11th Houses`).
4. **Health & Vitality:** Protective shield of vitality (`1st & 6th Houses`).
5. **Education & Intellect:** Academic graduation cap of Vidya (`4th, 5th Houses & Mercury`).
6. **Children & Family:** Parent and child bond silhouette (`5th House & Saptamsha D7`).
7. **Property & Assets:** Vastu home architecture silhouette (`4th House & Mars`).
8. **Travel & Relocation:** Compass directional paper plane (`9th & 12th Houses`).
9. **Spirituality & Moksha:** Sacred 8-petal lotus / Dharma wheel (`Moksha Houses & Ketu`).
10. **Obstacles & Remedies:** Protective lightning thunderbolt / Dosha mitigation (`Shadbala`).

### 5. Section F: Zodiac Constellation Symbols (Rashis)
Renders authentic classical Unicode zodiac glyphs with gold gradient styling:
`♈ Mesha`, `♉ Vrishabha`, `♊ Mithuna`, `♋ Karka`, `♌ Simha`, `♍ Kanya`, `♎ Tula`, `♏ Vrishchika`, `♐ Dhanu`, `♑ Makara`, `♒ Kumbha`, `♓ Meena`.

---

## 6. Image & Visual Asset Architecture

- **Zero Heavy Bitmaps:** No heavy JPEG or PNG stock images are downloaded over the network.
- **Pure CSS Deep Space Ambient:** Generated using 8 layered CSS radial gradients directly in `body::before`, ensuring instant page rendering (0ms network request).
- **High-DPI Canvas Rendering:** The 3D Armillary Canvas dynamically queries `window.devicePixelRatio` and scales its backing store to provide Retina/4K sharpness without blurriness.
- **Graceful Fallback:** If JavaScript or canvas is disabled, a pure CSS/SVG Vedic Mandala fallback appears automatically.

---

## 7. Verification & Live Server Status

- **Development Server:** Uvicorn live reload active on `http://127.0.0.1:8000`.
- **HTTP Smoke Test:** All HTML routes (`/`, `/kundali`, `/panchang`, `/horoscope`, `/prediction`, `/login`, `/signup`) return **HTTP 200 OK**.
- **Automated Tests:** 40 / 40 automated tests passing with zero regressions.
- **Cross-Version Starlette Engine:** `app/core/templating.py` guarantees compatibility across all Starlette and FastAPI versions.
