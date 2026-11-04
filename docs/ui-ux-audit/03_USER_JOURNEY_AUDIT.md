# User Journey Audit & Experience Maps

**Product:** AstroLogic / Nakshatra Labs  
**Version:** 2.0.0  
**Scope:** End-to-end evaluation of core user journeys, steps, friction points, drop-off triggers, and conversion opportunities.

---

## Journey 1: First-Time Visitor Discovery to Kundali Generation & PDF Export

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│ 1. Home Land │ ──> │ 2. CTA Click │ ──> │ 3. Form Fill │ ──> │ 4. View Chart│ ──> │ 5. Download  │
│  Explore Hero│     │  To /kundali │     │ Name/DOB/City│     │ D1/D9 + Yogas│     │  PDF Report  │
└──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
       │                                         │                                         │
       ▼                                         ▼                                         ▼
[Friction 1]                              [Friction 2]                              [Friction 3]
"Signed In" green dot                     No auto-detect of                         Forced feedback
shown to anonymous                        timezone; relative                        modal blocks PDF;
guests causes confusion                   fetch path risk                           opens unstyled tab
```

### Step-by-Step Breakdown & Friction Analysis

1. **Step 1: Visitor arrives on `/`**
   - *Intended Experience:* Understand platform value (Swiss Ephemeris precision, AI explanations), see live cosmic data, and proceed to free chart.
   - *Friction Points:* The hero section falsely displays "Signed in and ready to calculate your chart" with a pulsing green indicator for anonymous users. The header displays "Profile" and "Logout", confusing new visitors who wonder if they are somehow logged into someone else's account.
2. **Step 2: Clicks "Generate Free Kundali"**
   - *Intended Experience:* Instant navigation to `/kundali`.
   - *Friction Points:* Smooth navigation, but header action buttons change unpredictably (Language switcher disappears; CTA button disappears).
3. **Step 3: Enters Birth Data (Name, Date, Time, City)**
   - *Intended Experience:* Effortless input with autocomplete.
   - *Friction Points:* City autocomplete requires typing at least 2 characters, but does not display a loading spinner while `/api/cities` loads. If the user was born outside India, the field label "Time of Birth (IST)" forces them to manually convert their local birth time to Indian Standard Time.
4. **Step 4: Clicks "Generate Kundali"**
   - *Intended Experience:* Smooth calculation and display of D1/D9 charts, yogas, doshas, and dasha.
   - *Friction Points:* Line 767 calls `fetch('api/kundali')` without a leading slash. If the user visited `/kundali/` with a trailing slash, the request fails with a 404 error. When successful, the results section auto-scrolls down abruptly after a 100ms timeout.
5. **Step 5: Clicks "⬇ PDF"**
   - *Intended Experience:* Immediate download of a high-resolution, branded PDF report.
   - *Friction Points:* **Critical drop-off trigger.** The download button is hijacked by `openFeedbackModal()`, forcing the user to complete a 4-question testing feedback form with required dropdowns before downloading. Once submitted, it opens a raw, unstyled `window.open` browser window instead of streaming a real PDF, frequently blocked by mobile popup blockers.

### Opportunities to Improve Completion Rates:
- Implement progressive disclosure: show a streamlined 3-field birth form directly on the homepage hero.
- Auto-detect user timezone and location via browser Geolocation API.
- Remove feedback roadblock from the PDF download action. Stream real PDF via `GET /api/download-kundali`.

---

## Journey 2: Daily Panchang Routine & Vedic Decision Lookup

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│ 1. Navigate  │ ──> │ 2. Select    │ ──> │ 3. 'My       │ ──> │ 4. Decision  │
│  To /panchang│     │    City/GPS  │     │   Panchang'  │     │   Assistant  │
└──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
       │                                         │                    │
       ▼                                         ▼                    ▼
[Friction 1]                              [Friction 2]         [Friction 3]
Link in nav was                           Clicking 'Resolve    Decision buttons
"/panchang.html"                          Profile' throws 404  fail with 404 on
with .html suffix                         under legacy server  legacy backend
```

### Step-by-Step Breakdown & Friction Analysis

1. **Step 1: User navigates to Panchang**
   - *Intended Experience:* Quick check of today's Tithi, Nakshatra, Rahu Kaal, and active Choghadiya.
   - *Friction Points:* Link in the header of multiple pages is written as `/panchang.html` rather than semantic `/panchang`. The page loads with a very high density of information (over 25 numbers/timings visible at once).
2. **Step 2: Selects City or Clicks "📍 Use GPS"**
   - *Intended Experience:* Instant recalculation for their exact location.
   - *Friction Points:* The city dropdown only lists 17 hardcoded cities. If the user lives in a tier-2 city (e.g., Surat, Indore, Nagpur), they cannot select it from the dropdown, even though the backend supports it.
3. **Step 3: Toggles "✨ My Panchang" (Personalization)**
   - *Intended Experience:* Enter natal Moon sign or birth details to calculate personal Tara Bala and Chandra Bala.
   - *Friction Points:* The profile form prompts for Name, Birth Date, Time, and City. Clicking "🔮 Resolve Profile" triggers `fetch('/api/panchang/resolve-profile')`. In the standard `app.main` deployment, **this endpoint does not exist and throws an uncaught 404 error alert**, completely breaking the personalization feature.
4. **Step 4: Uses Vedic Decision Assistant**
   - *Intended Experience:* Click "✈️ Travel" or "💰 Investment" to see if the current Muhurat is favorable.
   - *Friction Points:* Also calls an unregistered endpoint (`/api/panchang/decision`), failing with 404.

### Opportunities to Improve Completion Rates:
- Populate city selector dynamically from `/api/cities`.
- Unify server route registration so all modular endpoints are accessible.
- Group the dense 25+ parameters into 3 tabbed views: "Now (Live Status)", "Full 5 Limbs", and "Auspicious Timings".

---

## Journey 3: Daily Horoscope Discovery by Zodiac Sign

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│ 1. Home Land │ ──> │ 2. Click Sign│ ──> │ 3. Land on   │ ──> │ 4. Switch    │
│  Scroll Grid │     │   eg: Scorpio│     │   Horoscope  │     │   Signs      │
└──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
                            │                    │                    │
                            ▼                    ▼                    ▼
                     [Friction 1]         [Friction 2]         [Friction 3]
                     Navigates to         Query param ignored! Vertical swipe
                     /horoscope?sign=7    Page ALWAYS resets   inadvertently
                                          to Aries (Sign 0)    changes signs
```

### Step-by-Step Breakdown & Friction Analysis

1. **Step 1: Visitor scrolls homepage to "Today's Horoscope by Sign"**
   - *Intended Experience:* See their sign's glyph and click to read their horoscope.
2. **Step 2: Clicks "Scorpio" (`/horoscope?sign=7`)**
   - *Intended Experience:* Arrive on `/horoscope` with Scorpio preselected and loaded.
3. **Step 3: Lands on `/horoscope`**
   - *Friction Points (Critical Bug):* `daily-horoscope.html` completely ignores `window.location.search`. It unconditionally calls `loadHoroscope(0)`, resetting the active sign to **Aries**. The user clicked Scorpio, but is shown Aries predictions. Most users will not realize the page did not honor their selection and will read the wrong horoscope.
4. **Step 4: User attempts to switch signs on mobile**
   - *Friction Points:* The page binds a touch listener without tracking vertical travel delta. When users attempt to scroll down to read the career prediction, slight diagonal thumb movements trigger horizontal sign switching.

### Opportunities to Improve Completion Rates:
- Add 2 lines of JavaScript to read `new URLSearchParams(window.location.search).get('sign')` on load.
- Constrain touch swipe handler to require `Math.abs(deltaX) > Math.abs(deltaY) * 2`.

---

## Journey 4: Deep Life Predictions (10 Domains)

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│ 1. Navigate  │ ──> │ 2. Re-enter  │ ──> │ 3. Click     │ ──> │ 4. Interrupted│
│  /prediction │     │    Birth Data│     │   'Analyse'  │     │   by Feedback│
└──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
                            │                                         │
                            ▼                                         ▼
                     [Friction 1]                              [Friction 2]
                     User already entered                      Full screen modal
                     birth details on Kundali;                 pops up BEFORE user
                     forced to re-type all                     can read results
```

### Step-by-Step Breakdown & Friction Analysis

1. **Step 1: User navigates to `/prediction`**
   - *Intended Experience:* Get in-depth predictions across Career, Marriage, Wealth, Health, etc.
2. **Step 2: Enters Birth Details**
   - *Friction Points:* If the user just generated their Kundali on `/kundali`, they expect their birth details to carry over. Instead, they must re-enter their Name, Date, Time, and City from scratch.
3. **Step 3: Clicks "Analyse All 10 Domains ✦"**
   - *Intended Experience:* System calculates Vedic house lords, Dasha triggers, and transits, presenting the domain scorecards.
4. **Step 4: Immediate Feedback Interruption (Critical Usability Blocker)**
   - *Friction Points:* As soon as the API response arrives, the app immediately executes `openFeedbackModal("prediction", person, ...)`. A dark backdrop covers the screen with a form demanding: "How accurate was the reading? Select: Very Accurate / Mostly Accurate...".
   - *User Emotional State:* Frustration and confusion. The user hasn't even looked at the predictions yet, but is being asked to rate their accuracy! Most users will abandon or submit random garbage feedback just to dismiss the modal.

### Opportunities to Improve Completion Rates:
- Share birth details seamlessly across all modules using `sessionStorage` or cookies.
- Move feedback collection to a subtle bottom-of-page thumbs-up/thumbs-down widget ("Was this prediction helpful?").

---

## Journey 5: Account Registration & Profile Persistence

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│ 1. Click     │ ──> │ 2. Submit    │ ──> │ 3. Redirected│ ──> │ 4. Edit &    │
│  'Create Acc'│     │    Form      │     │   to /profile│     │    Save Data │
└──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
                            │                                         │
                            ▼                                         ▼
                     [Friction 1]                              [Friction 2]
                     Required phone                            Clicking 'Save'
                     number with strict                        boots user back to
                     regex pattern                             homepage without alert
```

### Step-by-Step Breakdown & Friction Analysis

1. **Step 1: User clicks "Create Account"**
   - *Intended Experience:* Quick signup to save charts and reading histories.
2. **Step 2: Submits Registration Form**
   - *Friction Points:* Phone number is strictly mandatory (`required = true`), blocking users who prefer not to share their mobile number. If password is shorter than 6 characters, error feedback is nonexistent if the form fails on the backend.
3. **Step 3: Arrives on `/profile`**
   - *Intended Experience:* Fill out birth details (DOB, Time, City, Zodiac) to enable 1-click readings across the site.
4. **Step 4: Clicks "Save Profile"**
   - *Friction Points:* Upon submission, `auth.py:200` executes `return RedirectResponse("/", status_code=303)`. The user is instantly kicked back to the homepage (`/`) with no success message!
   - *Impact:* The user assumes the submission failed or experienced an error, returns to `/profile`, and is left wondering if their changes were persisted.

### Opportunities to Improve Completion Rates:
- Make phone number optional at signup.
- Keep user on `/profile` after saving, displaying a clear green success notification: "Profile updated successfully".
- Automatically populate birth details into Kundali and Prediction pages when an authenticated user visits them.
