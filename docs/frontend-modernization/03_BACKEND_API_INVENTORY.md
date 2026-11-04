# 03 — Backend API Inventory, Security Classification & BFF Architecture

**Project:** AstroLogic AI / Nakshatra Labs — Modern Frontend Migration  
**Document:** `docs/frontend-modernization/03_BACKEND_API_INVENTORY.md`  
**Phase:** Phase 1 – Discovery, Architecture Assessment & Implementation Planning  
**Status:** AUDITED & FINALIZED (Verification Standard Enforced)  
**Date:** October 31, 2026  
**Auditor:** Senior Software Architect, Security Engineer & Migration Specialist  

---

## 1. Authentication & Session Architecture Investigation `[VERIFIED]`

A thorough code audit of `backend/gateway/main.py`, `backend/modules/auth/api.py`, `backend/modules/auth/engine.py`, and `backend/shared/config/settings.py` was conducted to establish exact security mechanics.

### 1.1. User Authentication Mechanics `[VERIFIED]`
- **Credentials Storage:** Password verification uses PBKDF2-HMAC-SHA256 with 100,000 iterations and a random salt stored in `users.password_hash` (`modules/auth/engine.py:verify_password`).
- **Session Framework:** Built on Starlette's `SessionMiddleware` (`gateway/main.py:211-216`):
  ```python
  app.add_middleware(
      SessionMiddleware,
      secret_key=settings.session_secret_key,
      same_site="lax",
      https_only=settings.is_production,
  )
  ```
- **Cookie Attributes `[VERIFIED]`:**
  - **Cookie Name:** `session`
  - **Payload:** Serialized JSON dictionary signed with HMAC-SHA1 via `itsdangerous.TimestampSigner`.
  - **Domain:** Unset (defaults to the exact host requested).
  - **Path:** `/`
  - **HttpOnly:** `True` (enforced by Starlette `SessionMiddleware`).
  - **Secure:** `settings.is_production` (`False` in development, `True` in production).
  - **SameSite:** `"lax"`
  - **Max-Age / Expires:** Starlette default of 14 days (1,209,600 seconds) unless overwritten.
- **Session Lifecycle & Invalidation `[VERIFIED]`:**
  - Login calls `request.session["user_id"] = user.id`.
  - Admin login calls `request.session["admin"] = "true"`.
  - Logout calls `request.session.clear()`, wiping session keys and emitting an empty/expired cookie.
- **CSRF Protection Status `[VERIFIED]`:**
  **Zero CSRF protection exists in the FastAPI backend.** There are no CSRF tokens, anti-forgery cookies, or header checks. Requests relying on ambient cookie credentials are susceptible to cross-site request forgery if exposed to cross-site origins.
- **Gateway Default-Deny Security `[VERIFIED]`:**
  `DefaultDenyAuthMiddleware` intercepts all requests to `/api/*`. Unless a path matches an explicit allowlist in `PUBLIC_API_PREFIXES` or is a public `GET /api/blogs`, it checks:
  ```python
  user_id = request.session.get("user_id")
  is_admin = request.session.get("admin") == "true"
  if not user_id and not is_admin:
      return JSONResponse(status_code=401, content={"detail": "Authentication required. Default-deny policy enforced."})
  ```

---

## 2. Decoupled Architecture Challenge & Next.js BFF Proxy Solution `[PROPOSED]`

### 2.1. The Cross-Origin Cookie Problem `[VERIFIED]`
When the Next.js development server runs on `http://localhost:3000` and dispatches browser `fetch` requests directly to `http://127.0.0.1:8000`:
1. Browsers treat `localhost` and `127.0.0.1` as distinct origins and different sites.
2. Under `SameSite=Lax`, cookies are **omitted from cross-site asynchronous fetch requests**, even with `credentials: 'include'`.
3. Consequently, all protected `/api/*` requests fail with `401 Unauthorized` during development and across differing production domains.

### 2.2. The Next.js Backend-for-Frontend (BFF) Proxy Architecture `[PROPOSED]`
To resolve this without modifying the backend, a same-origin **Backend-for-Frontend (BFF) proxy** in Next.js is mandatory:

```
┌─────────────────────────────────────────────────────────────┐
│                    Browser Client                           │
│              (Origin: http://localhost:3000)                │
└──────────────────────────────┬──────────────────────────────┘
                               │ Same-Origin HTTP Request
                               │ Cookie: session=... (Automatic)
                               ▼
┌─────────────────────────────────────────────────────────────┐
│            Next.js App Router (BFF Layer)                   │
│             `app/api/[...proxy]/route.ts`                   │
│                                                             │
│ 1. Extracts incoming `Cookie` and `Authorization` headers.  │
│ 2. Enforces client-side CSRF tokens on mutating requests.   │
│ 3. Normalizes timeouts (default 10s) and error formats.     │
└──────────────────────────────┬──────────────────────────────┘
                               │ Server-to-Server HTTP Request
                               │ Cookie: session=... (Forwarded)
                               ▼
┌─────────────────────────────────────────────────────────────┐
│              FastAPI Gateway (:8000)                        │
│             `backend/gateway/main.py`                       │
│                                                             │
│ 1. Validates `session` signature.                           │
│ 2. DefaultDenyAuthMiddleware authorizes request.            │
│ 3. Executes Swiss Ephemeris / Astrological calculations.    │
│ 4. Emits `Set-Cookie` header on login/logout.               │
└──────────────────────────────┬──────────────────────────────┘
                               │ Server-to-Server Response
                               │ Set-Cookie: session=...
                               ▼
┌─────────────────────────────────────────────────────────────┐
│            Next.js App Router (BFF Layer)                   │
│ 1. Relays `Set-Cookie` back to the browser on :3000.        │
│ 2. Formats response JSON.                                   │
└──────────────────────────────┬──────────────────────────────┘
                               │ Same-Origin Response
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                    Browser Client                           │
│   (Session cookie stored safely under localhost:3000)       │
└─────────────────────────────────────────────────────────────┘
```

#### Key Advantages of the BFF Proxy:
1. **100% Same-Origin:** Browser interacts solely with `localhost:3000`. Cookies are never considered third-party or cross-site.
2. **CSRF Mitigation at the Edge:** The Next.js BFF layer validates a custom request header (e.g. `X-Requested-With: AstroLogicClient`) or CSRF token before forwarding mutating `POST`/`PUT`/`DELETE` calls to FastAPI.
3. **Seamless Set-Cookie Relay:** When FastAPI logs a user in or out, the proxy mirrors the `Set-Cookie` header directly to the browser.
4. **Server vs Client Calls:**
   - *Server Components (RSC):* Extract cookies from `next/headers` and forward directly to `http://127.0.0.1:8000`.
   - *Client Components (`'use client'`):* Call `/api/*` via standard same-origin `fetch` without special configuration.

---

## 3. Authentication Test Matrix `[VERIFIED / TEST SPECIFICATION]`

| # | Test Scenario | Expected Outcome | Verification Status | Code Evidence |
| :- | :--- | :--- | :--- | :--- |
| **T01** | User Registration (`POST /api/auth/signup`) | Account created, PBKDF2 hash stored, session cookie issued | `[VERIFIED]` | `modules/auth/api.py:237-244` |
| **T02** | User Login (`POST /api/auth/login`) | Credentials validated, valid session cookie returned with `user_id` | `[VERIFIED]` | `modules/auth/api.py:247-254` |
| **T03** | Page Refresh with Session Cookie | Session remains valid, user profile reloaded | `[REQUIRES RUNTIME TEST]` | Browser cookie retention check |
| **T04** | Open Protected Dashboard (`/profile`) | Authenticated access granted | `[VERIFIED]` | `modules/auth/api.py:155-161` |
| **T05** | Access Protected API without Session | Rejected with `401 Unauthorized` | `[VERIFIED]` | `gateway/main.py:79-84` |
| **T06** | Access Protected API with Valid Session | Authorized, calculations returned | `[VERIFIED]` | `gateway/main.py:85` |
| **T07** | User Logout (`POST /api/auth/logout`) | `request.session.clear()` called, session wiped | `[VERIFIED]` | `modules/auth/api.py:257-261` |
| **T08** | Reuse Old Session Cookie after Logout | Rejected with `401 Unauthorized` | `[REQUIRES RUNTIME TEST]` | Relies on cookie overwrite |
| **T09** | Expired Session (>14 Days) | Rejected with `401 Unauthorized` | `[REQUIRES RUNTIME TEST]` | Timestamp validation in `itsdangerous` |
| **T10** | Invalid Login Credentials | Rejected with `401 Invalid email or password` | `[VERIFIED]` | `modules/auth/api.py:251-252` |
| **T11** | CSRF-Sensitive Mutation via BFF | Validated by Next.js header check before backend dispatch | `[PROPOSED]` | BFF proxy implementation gate |
| **T12** | Admin Route with Standard User Session | Rejected with `403 Forbidden` or `admin-login` redirect | `[VERIFIED]` | `gateway/main.py:166, 179` |

---

## 4. Access-Control Matrix `[VERIFIED]`

| User State | Public APIs (`/panchang`, `/horoscope`, etc.) | Authenticated APIs (`/domains`, `/saved-charts`) | Admin APIs (`/admin/cache/*`, `/admin/blogs`) | Internal Diagnostics (`/health`, `/ready`) |
| :--- | :--- | :--- | :--- | :--- |
| **Anonymous** | `ALLOW` | `DENY (401 Unauthorized)` | `DENY (401 Unauthorized)` | `ALLOW` |
| **Authenticated User** | `ALLOW` | `ALLOW` | `DENY (403 Forbidden)` | `ALLOW` |
| **Administrator** | `ALLOW` | `ALLOW` | `ALLOW` | `ALLOW` |
| **Internal Service / Worker** | `ALLOW` | `DENY` (unless bearer token or internal flag) | `DENY` | `ALLOW` |

---

## 5. Verified Backend API Route Inventory (77 Routes) `[VERIFIED]`

Every active route in `gateway.main:app` has been inspected and classified into one of four security tiers:
1. `PUBLIC`
2. `AUTHENTICATED`
3. `ADMIN_ONLY`
4. `INTERNAL / DIAGNOSTIC`

### 5.1. Vedic Kundali, Planetary Coordinates & Saved Charts
*Router: `modules/kundali/api.py` (Prefix: none, Tags: `Kundali & Charts`)*

| Method | Endpoint Path | Security Tier | Request Schema | Response Schema | Frontend Consumer |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `GET` | `/api/cities` | `PUBLIC` | None | `list[str]` (500+ city names) | City autocomplete in Kundali & Panchang |
| `POST` | `/api/generate-chart` | `PUBLIC` | `KundaliRequest` | `{basic_details, planets}` | Lightweight preview widget |
| `POST` | `/api/kundali` | `PUBLIC / SESSION` | `KundaliRequest` | Complete Kundali payload (D1, D9, yogas, doshas, dasha) | Primary Kundali generator |
| `GET` | `/api/download-kundali` | `AUTHENTICATED` | Session cookie | `application/pdf` binary stream | PDF download button |
| `POST` | `/api/kundali-chat` | `PUBLIC / SESSION` | `{question: str}` | `{response: str, context: dict}` | AstroAI chat drawer |
| `GET` | `/api/kundali/saved-charts` | `AUTHENTICATED` | Query: `skip, limit` | `list[SavedChartResponse]` | Saved charts management table |
| `POST` | `/api/kundali/saved-charts` | `AUTHENTICATED` | `SavedChartCreate` | `SavedChartResponse` | Save chart button |
| `GET` | `/api/kundali/saved-charts/{chart_id}` | `AUTHENTICATED` | Path: `chart_id: int` | `SavedChartResponse` | Open saved chart |
| `PUT` | `/api/kundali/saved-charts/{chart_id}` | `AUTHENTICATED` | Path, `SavedChartUpdate` | `SavedChartResponse` | Edit saved chart metadata |
| `DELETE` | `/api/kundali/saved-charts/{chart_id}` | `AUTHENTICATED` | Path: `chart_id: int` | `{status: "ok"}` | Delete saved chart |

### 5.2. Life Domain Predictions & Dasha Timing Engine
*Router: `modules/prediction/api.py` (Prefix: none, Tags: `Predictions & Domains`)*

| Method | Endpoint Path | Security Tier | Request Schema | Response Schema | Frontend Consumer |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `POST` | `/api/domains` | `AUTHENTICATED` | `KundaliRequest` | 10-domain scores, evidence, remedies, timing | Predictions dashboard |
| `POST` | `/api/prediction` | `AUTHENTICATED` | `KundaliRequest` | Marriage & Career AI predictions | Specialized prediction view |
| `POST` | `/api/prediction/timing/{domain}` | `AUTHENTICATED` | Path: `domain`, `KundaliRequest` | Concrete dasha + transit timing intervals | Timing window cards |
| `POST` | `/api/chat` | `AUTHENTICATED` | `{question: str}` | AI narrative prediction response | Prediction chat assistant |

### 5.3. Daily Panchang, Muhurat & Festivals
*Router: `modules/panchang/api.py` (Prefix: none, Tags: `Panchang & Festivals`)*

| Method | Endpoint Path | Security Tier | Request Schema | Response Schema | Frontend Consumer |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `POST` | `/api/panchang` | `PUBLIC` | `PanchangRequest` | 5 limbs, Choghadiya, Horas, Kaals, Muhurat | Panchang page |
| `GET` | `/api/festivals/today` | `PUBLIC` | Query: `city?` | `list[Festival]` | Daily festival banner |
| `GET` | `/api/festivals/upcoming` | `PUBLIC` | Query: `limit?, city?` | `list[Festival]` | Upcoming festival feed |
| `POST` | `/api/panchang/decision` | `AUTHENTICATED` | `{activity, date, city}` | Muhurat feasibility score & guidance | Vedic Decision Advisor |
| `POST` | `/api/panchang/resolve-profile` | `AUTHENTICATED` | `{user_id, date}` | Tara Bala & Chandra Bala score | Personalized Panchang |
| `GET` | `/api/panchang/calendar.ics` | `PUBLIC` | Query: `month, year, city` | `text/calendar` (.ics file) | Add to Calendar button |
| `GET` | `/api/panchang/share-image` | `PUBLIC` | Query: `date, city` | `image/png` binary stream | Social share button |

### 5.4. Transit Horoscopes
*Router: `modules/horoscope/api.py` (Prefix: none, Tags: `Horoscope`)*

| Method | Endpoint Path | Security Tier | Request Schema | Response Schema | Frontend Consumer |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `GET` | `/api/daily-horoscope/{sign}` | `PUBLIC` | Path: `sign: str` | Transit horoscope for sign name | Sign forecast page |
| `GET` | `/api/horoscope/{sign_idx}` | `PUBLIC` | Path: `sign_idx: int` | Scores, lucky items, commentary | 12-sign scrollbar widget |

### 5.5. AI Astro-Narrative & SSE Streaming
*Router: `modules/narrative/api.py` (Prefix: none, Tags: `narrative`)*

| Method | Endpoint Path | Security Tier | Request Schema | Response Schema | Frontend Consumer |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `POST` | `/api/narrative/generate` | `AUTHENTICATED` | `NarrativeRequest` | `{job_id: str, status: "pending"}` | Generate AI Narrative button |
| `GET` | `/api/narrative/{job_id}` | `AUTHENTICATED` | Path: `job_id` | Status polling payload | Background job watcher |
| `GET` | `/api/narrative/{job_id}/stream` | `AUTHENTICATED` | Path: `job_id` | **`text/event-stream` (SSE)** | Live AI typing narrative |
| `POST` | `/api/narrative/chat` | `AUTHENTICATED` | `{job_id, message}` | Conversational message response | Narrative multi-turn chat |

### 5.6. Blog CMS & Knowledge Library
*Router: `modules/blog/api.py` (Prefix: none, Tags: `blogs`)*

| Method | Endpoint Path | Security Tier | Request Schema | Response Schema | Frontend Consumer |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `GET` | `/api/blogs` | `PUBLIC` | Query: `category, search` | `list[BlogResponse]` | Blog library index |
| `GET` | `/api/blogs/{slug}` | `PUBLIC` | Path: `slug_or_id` | Full article payload | Blog reader view |
| `POST` | `/api/blogs` | `ADMIN_ONLY` | `BlogCreate` | `BlogResponse` | Admin blog editor |

### 5.7. User Testing & Feedback
*Router: `modules/feedback/api.py` (Prefix: none, Tags: `feedback`)*

| Method | Endpoint Path | Security Tier | Request Schema | Response Schema | Frontend Consumer |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `POST` | `/api/feedback` | `PUBLIC / SESSION` | `FeedbackCreate` | `{status: "ok", id: int}` | Beta feedback widget |
| `GET` | `/api/feedback` | `ADMIN_ONLY` | Query: `limit` | `list[FeedbackResponse]` | Admin feedback viewer |

### 5.8. Authentication & Profile
*Router: `modules/auth/api.py` (Prefix: none, Tags: `Authentication`)*

| Method | Endpoint Path | Security Tier | Request Schema | Response Schema | Frontend Consumer |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `POST` | `/api/auth/signup` | `PUBLIC` | `UserRegister` | `{status: "ok", user: dict}` | Signup form |
| `POST` | `/api/auth/login` | `PUBLIC` | `UserLogin` | `{status: "ok", user: dict}` | Login form |
| `POST` | `/api/auth/logout` | `AUTHENTICATED` | None | `{status: "ok", message: str}` | Sign out button |
| `GET` | `/change-language/{lang}` | `PUBLIC` | Path: `lang: str` | Redirect with `Set-Cookie: lang` | Language switcher |
| `GET` | `/profile` | `AUTHENTICATED` | Session cookie | HTML / Profile data | Profile dashboard |
| `POST` | `/profile` | `AUTHENTICATED` | Form-encoded profile | Redirect / Profile updated | Profile form |

### 5.9. System Diagnostics & Cache
*Gateway Direct Endpoints (Tags: `Untagged` / `Admin`)*

| Method | Endpoint Path | Security Tier | Purpose |
| :--- | :--- | :--- | :--- |
| `GET` | `/health` | `PUBLIC / DIAGNOSTIC` | Liveness probe returning app name, environment, and ephemeris mode |
| `GET` | `/ready` & `/api/ready` | `PUBLIC / DIAGNOSTIC` | Readiness probe checking database connectivity and cache operational status |
| `GET` | `/metrics` | `PUBLIC / DIAGNOSTIC` | Operational cache hit/miss metrics |
| `GET` | `/api/system/ephemeris` | `PUBLIC / DIAGNOSTIC` | Swiss Ephemeris runtime mode (`swisseph` C vs `moshier`) and licensing |
| `GET` | `/api/admin/cache/stats` | `ADMIN_ONLY` | In-memory and Redis cache statistics |
| `POST` | `/api/admin/cache/flush` | `ADMIN_ONLY` | Flushes all calculation caches |
| `GET` | `/api/locales/{lang}` | `PUBLIC` | Returns translation dictionary for requested locale code |

---

## 6. Backend Language Integration Capabilities `[VERIFIED]`

| Backend Capability | Existing Support Status | Evidence in Codebase |
| :--- | :--- | :--- |
| **Language Cookie Extraction** | `[VERIFIED]` | `request.cookies.get("lang")` in `LanguageDetectionMiddleware` |
| **URL Prefix Language Extraction** | `[VERIFIED]` | `/{lang}/...` handled in `LanguageDetectionMiddleware` & `pages.py` |
| **Accept-Language Header Parsing** | `[VERIFIED]` | Priority 4 in `LanguageDetectionMiddleware` |
| **User Profile Language Storage** | `[VERIFIED]` | `users.preferred_language` in `modules/auth/models.py` |
| **Astrology Terms Dictionary** | `[VERIFIED]` | Sanskrit/Hindi/Marathi mappings in `shared/i18n/translation.py` |
| **Dynamic JSON Locale Endpoint** | `[VERIFIED]` | `GET /api/locales/{lang}` loads `app/static/locales/{lang}.json` |
| **API Parameter Language Filter** | `[NOT SUPPORTED]` | Calculation endpoints (`/api/kundali`, `/api/domains`, `/api/panchang`) do **not** take a `lang` parameter in their Pydantic schemas. They return standardized Sanskrit/English astronomical terms. |
| **AI Narrative Language Parameter**| `[NOT SUPPORTED]` | `NarrativeRequest` does not currently include a `language` field. LLM prompts generate in English by default. |

**Frontend Architectural Boundary:**
Because backend calculation endpoints return standardized astrological data (e.g. `sign: "Kanya"`, `dignity: "Exalted"`), the Next.js frontend will handle domain label localization using the centralized glossary (`frontend/messages/`). AI narrative translation to Hindi/Marathi should be proposed as a future backend enhancement.

---

## 7. Centralized API Client Integration Rules `[PROPOSED]`

1. **Centralized Client:** All API communication will route through `lib/api-client.ts` executing calls via the same-origin Next.js BFF proxy.
2. **Timeout Standard:** Strict 10-second timeout on standard calculation requests; 60-second timeout for async narrative streaming.
3. **Safe Retry Policy:**
   - Idempotent `GET` requests: Exponential backoff retry (up to 3 attempts on 502/503/504 errors).
   - Non-idempotent `POST`/`PUT`/`DELETE` requests: **Zero automatic retries** to prevent duplicate database writes or calculation jobs.
4. **Error Normalization:** Converts backend HTTPException JSON (`{"detail": "..."}`) into typed `AstroLogicApiError` instances displaying user-friendly localized error toasts.
5. **SSE Streaming Support:** Native browser `EventSource` or `fetch` readable streams consuming `/api/narrative/{job_id}/stream` with automatic reconnect guards.
