# 08 — Legacy Frontend Assessment, Verification & Safe Migration Strategy

**Project:** AstroLogic AI / Nakshatra Labs — Modern Frontend Migration  
**Document:** `docs/frontend-modernization/08_MIGRATION_AND_PRESERVATION.md`  
**Phase:** Phase 1 – Discovery, Architecture Assessment & Implementation Planning  
**Status:** AUDITED & FINALIZED (Verification Standard Enforced)  
**Date:** October 31, 2026  
**Auditor:** Senior Software Architect, Security Engineer & Migration Specialist  

---

## 1. Assessment of Existing Legacy Frontend Directory `[VERIFIED]`

### 1.1. Physical Inventory of Files
Inspection of `c:\Desktop\astro_may_res (2)\astro-platform\frontend\` reveals the following file inventory:

```
frontend/
├── about.html                   # 27,602 bytes (Static snapshot of about page)
├── admin-activity.html          # 5,437 bytes (Admin activity log)
├── admin-blog.html              # 8,635 bytes (Admin blog management)
├── admin-feedback.html          # 4,713 bytes (Admin feedback viewer)
├── admin-login.html             # 4,165 bytes (Admin login form)
├── admin-users.html             # 5,653 bytes (Admin user directory)
├── auth.html                    # 11,119 bytes (Login / signup form)
├── base.html                    # 746 bytes (Language dropdown snippet)
├── blog-detail.html             # 6,993 bytes (Article reader view)
├── blogs.html                   # 21,593 bytes (Blog article catalog)
├── daily-horoscope.html         # 27,164 bytes (12-sign daily horoscope)
├── index.html                   # 41,472 bytes (Static homepage snapshot)
├── kundali.html                 # 82,809 bytes (Static Kundali chart viewer)
├── kundali.js                   # 56,235 bytes (SVG chart drawing & event script)
├── panchang.html                # 36,748 bytes (Static Panchang & Choghadiya)
├── prediction.html              # 47,221 bytes (Static 10-domain life predictions)
├── profile.html                 # 13,922 bytes (Static profile form)
├── Untitled-1.md                # 5,131 bytes (Developer notes)
├── vercel.json                  # 598 bytes (Static hosting rewrite rules)
├── js/                          # Directory containing client scripts
├── locales/                     # Directory containing en.json, hi.json, mr.json
└── svg/                         # Directory containing zodiac and navagraha SVG icons
```

### 1.2. Verification of Active Server References `[VERIFIED]`
- **FastAPI Mount Configuration:** `backend/gateway/main.py` lines 37, 198, 201–204 mounts `app/static/` and `app/templates/`.
- **Finding:** The running FastAPI server **does not mount or read from `frontend/`**.
- **Role of `frontend/`:** The `frontend/` directory was originally created as an exported static snapshot configured with `vercel.json` for frontend preview.
- **Current Active Usage:** It is **not actively used** by the backend API process. However, because it contains historical assets, scripts, and static templates, **no files will be deleted or modified in Phase 1**.

---

## 2. Safe Migration & Archival Procedure (To be executed in Phase 2) `[PROPOSED]`

The following 6-step procedure must be executed in Phase 2 only after explicit user authorization.

### Step 1 — Inspect Repository State & Create Checkpoint Commit
Before any filesystem modifications:
```powershell
# 1. Inspect repository state
git status
# 2. Verify current branch
git branch --show-current
# 3. Create a clean migration checkpoint commit ensuring zero uncommitted work is lost
git add .
git commit -m "chore(migration): pre-migration checkpoint commit before frontend modernization"
```

### Step 2 — Create Complete Legacy Archive
Clone the entire `frontend/` directory into a dedicated archive directory:
```powershell
# Clone the complete directory recursively into frontend-legacy/
Copy-Item -Path "c:\Desktop\astro_may_res (2)\astro-platform\frontend" -Destination "c:\Desktop\astro_may_res (2)\astro-platform\frontend-legacy" -Recurse -Force
```

### Step 3 — Verify Backup Integrity (SHA-256 Hash Audit)
A backup is deemed valid **only** when all files, directories, hidden files, and configurations match 100%. The following automated PowerShell verification script must execute:
```powershell
$source = "c:\Desktop\astro_may_res (2)\astro-platform\frontend"
$backup = "c:\Desktop\astro_may_res (2)\astro-platform\frontend-legacy"

$srcFiles = Get-ChildItem -Path $source -Recurse -File
$bakFiles = Get-ChildItem -Path $backup -Recurse -File

Write-Host "Source file count: $($srcFiles.Count)"
Write-Host "Backup file count: $($bakFiles.Count)"

if ($srcFiles.Count -ne $bakFiles.Count) {
    Throw "CRITICAL ERROR: File count mismatch between source and backup!"
}

# Verify SHA-256 hash for every file
foreach ($file in $srcFiles) {
    $relPath = $file.FullName.Substring($source.Length)
    $bakFilePath = Join-Path $backup $relPath
    
    if (-not (Test-Path $bakFilePath)) {
        Throw "CRITICAL ERROR: Missing backup file: $relPath"
    }
    
    $srcHash = (Get-FileHash -Path $file.FullName -Algorithm SHA256).Hash
    $bakHash = (Get-FileHash -Path $bakFilePath -Algorithm SHA256).Hash
    
    if ($srcHash -ne $bakHash) {
        Throw "CRITICAL ERROR: Hash mismatch for file: $relPath"
    }
}
Write-Host "BACKUP INTEGRITY VERIFIED: 100% SHA-256 MATCH ACROSS ALL FILES."
```

### Step 4 — Initialize Next.js in `frontend/`
Only after Step 3 passes:
```powershell
# Remove old contents from frontend/ (frontend-legacy is safely preserved)
Remove-Item -Path "c:\Desktop\astro_may_res (2)\astro-platform\frontend\*" -Recurse -Force

# Initialize Next.js 15+ App Router application in non-interactive mode
npx -y create-next-app@latest "c:\Desktop\astro_may_res (2)\astro-platform\frontend" --typescript --tailwind --eslint --app --src-dir=false --import-alias="@/*" --use-npm
```

### Step 5 — Selectively Migrate & Organize Assets
Copy required static assets from `frontend-legacy/` into the new Next.js structure:
```powershell
# Copy SVG glyphs and icons
New-Item -ItemType Directory -Path "c:\Desktop\astro_may_res (2)\astro-platform\frontend\public\svg" -Force
Copy-Item -Path "c:\Desktop\astro_may_res (2)\astro-platform\frontend-legacy\svg\*" -Destination "c:\Desktop\astro_may_res (2)\astro-platform\frontend\public\svg" -Recurse -Force

# Copy and organize locale files for next-intl
New-Item -ItemType Directory -Path "c:\Desktop\astro_may_res (2)\astro-platform\frontend\messages" -Force
Copy-Item -Path "c:\Desktop\astro_may_res (2)\astro-platform\frontend-legacy\locales\*" -Destination "c:\Desktop\astro_may_res (2)\astro-platform\frontend\messages" -Force
```

### Step 6 — Rollback Procedure
If Next.js scaffolding fails, dependency installation aborts, or the build is broken:
```powershell
# Complete, zero-data-loss rollback to original state:
Remove-Item -Path "c:\Desktop\astro_may_res (2)\astro-platform\frontend" -Recurse -Force
Copy-Item -Path "c:\Desktop\astro_may_res (2)\astro-platform\frontend-legacy" -Destination "c:\Desktop\astro_may_res (2)\astro-platform\frontend" -Recurse -Force
Write-Host "ROLLBACK COMPLETE: frontend/ restored to exact pre-migration state."
```
*Guaranteed Safety:* Rollback affects **only** `frontend/`. The canonical Jinja2 templates (`app/templates/`) and FastAPI backend (`backend/`) remain completely untouched throughout the entire process.

---

## 3. Preservation Guarantees for Existing Systems `[VERIFIED]`

1. **Jinja2 Templates (`app/templates/`):**
   - Must remain **100% untouched and operational** throughout the entire migration process.
   - FastAPI's server-rendered routes (`/`, `/kundali`, `/panchang`, `/prediction`) will continue serving HTML as fallback endpoints until the Next.js frontend is fully vetted and approved for production cutover.
2. **FastAPI Backend Core (`backend/`):**
   - Zero modifications to calculation formulas, route signatures, or database schemas.
   - The backend will operate simultaneously in dual mode: as an SSR server (legacy) and as a headless JSON API server (for Next.js).
3. **Database & Alembic (`astrologic.db`, `backend/alembic/`):**
   - Database tables (`users`, `profiles`, `user_saved_charts`, `blogs`, `feedback`, `user_activities`) remain unchanged. Next.js will interface with these models strictly through existing authenticated REST APIs.
4. **Test Suite Integrity (`backend/tests/`):**
   - All 810 automated pytest tests must continue passing without regression during and after frontend modernization.
