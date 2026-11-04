# AstroLogic AI — Application Execution & Development Guide

This guide details how to run the AstroLogic AI platform with the latest modernized Next.js frontend UI and FastAPI backend services.

---

## 🏗️ Architecture & Service Topology

| Layer | Service / Technology | Default Host / Port | Description |
| :--- | :--- | :--- | :--- |
| **Frontend** | Next.js 16 (App Router + Turbopack) | `http://localhost:3000` | Modernized UI, 3D Celestial Orrery, Panchang engine, Vimshottari Dasha tree, Multilingual (`/en`, `/hi`, `/mr`). |
| **Backend Gateway** | FastAPI Modular Monolith | `http://127.0.0.1:8000` | Swiss Ephemeris calculations, Kundali, Panchang, Horoscopes, Rate limiting, and Auth. |
| **API Documentation** | OpenAPI Swagger UI | `http://127.0.0.1:8000/docs` | Interactive API explorer and route tester. |
| **Readiness Probe** | System Ephemeris Diagnostics | `http://127.0.0.1:8000/ready` | Health check verifying DB, cache, and ephemeris accuracy tier. |

---

## ⚡ 1. One-Click Execution (Automated Scripts)

Convenient launcher scripts are located in the project root:

### Option A: PowerShell Script (`start-dev.ps1`)
Open PowerShell in the project root and run:
```powershell
.\start-dev.ps1
```
* **What it does:**
  1. Checks if ports `8000` or `3000` are already running.
  2. Launches the FastAPI backend in a dedicated terminal window on port `8000`.
  3. Waits for the backend `/health` endpoint to report ready.
  4. Launches the Next.js frontend in a dedicated terminal window on port `3000`.
  5. Automatically opens your default web browser to `http://localhost:3000`.

### Option B: Windows Batch Launcher (`start-dev.bat`)
Double-click `start-dev.bat` in Windows File Explorer or execute from Command Prompt:
```cmd
start-dev.bat
```

---

## 🛠️ 2. Step-by-Step Manual Run (Two Terminals)

If you prefer running services manually in separate terminals:

### Terminal 1: Backend Gateway (FastAPI)
```powershell
# 1. Navigate to the backend directory
cd "backend"

# 2. Activate Python Virtual Environment
.\venv\Scripts\Activate.ps1

# 3. Start the FastAPI Uvicorn Server with hot-reload
python -m uvicorn gateway.main:app --host 127.0.0.1 --port 8000 --reload
```
* **Confirmation:** You will see `INFO: Uvicorn running on http://127.0.0.1:8000`.

---

### Terminal 2: Modern Frontend (Next.js)
```powershell
# 1. Navigate to the frontend directory
cd "frontend"

# 2. Start Next.js with Turbopack
npm run dev
```
* **Confirmation:** You will see `▲ Next.js 16.4.3 (Turbopack) - Ready in ... - Local: http://localhost:3000`.

---

## 🌐 3. Key Pages & Routes to Explore

Once both services are running:

* **Modern Homepage (3D Orrery & Live Cosmic Ticker):**  
  👉 [http://localhost:3000/en](http://localhost:3000/en)
* **Vedic Kundali & Birth Chart Engine (D1, D9, Dasha Tree, Yogas, AI Chat):**  
  👉 [http://localhost:3000/en/kundali](http://localhost:3000/en/kundali)
* **Daily Panchang & Real-Time Choghadiya Decision Engine:**  
  👉 [http://localhost:3000/en/panchang](http://localhost:3000/en/panchang)
* **Multilingual Switching:**  
  - Hindi: [http://localhost:3000/hi](http://localhost:3000/hi)  
  - Marathi: [http://localhost:3000/mr](http://localhost:3000/mr)
* **FastAPI Swagger API Documentation:**  
  👉 [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* **System Readiness & Ephemeris Diagnostic Endpoint:**  
  👉 [http://127.0.0.1:8000/ready](http://127.0.0.1:8000/ready)

---

## ⚙️ 4. Environment Variables

### Backend (`backend/.env`)
- `SECRET_KEY`: Security signing key for sessions and tokens.
- `DATABASE_URL`: SQLite or PostgreSQL database connection string (defaults to `sqlite:///./astrologic.db`).
- `EPHEMERIS_PATH`: Path to high-precision Swiss Ephemeris `.se1` ephemeris files (falls back to Moshier analytical model if empty).
- `CORS_ORIGINS`: Allowed client origins (e.g., `http://localhost:3000,http://127.0.0.1:3000`).

### Frontend (`frontend/.env.local` - Optional)
- `BACKEND_API_URL`: Points to FastAPI backend (defaults automatically to `http://127.0.0.1:8000`).

---

## 🔍 5. Troubleshooting & FAQ

### Port 8000 or 3000 Already in Use
If a previous process was left running, you can find and free the port using PowerShell:
```powershell
# Check which process is occupying port 8000 or 3000
Get-NetTCPConnection -LocalPort 8000, 3000 -ErrorAction SilentlyContinue | Select-Object LocalPort, OwningProcess

# Terminate process by PID (replace <PID> with the OwningProcess number)
Stop-Process -Id <PID> -Force
```

### PDF Report Download "Cookie Header Too Large" Fix
PDF generation utilizes server-side memory caching (`_CHART_CACHE`) indexed by a deterministic chart ID. This guarantees cookie sizes remain minimal (<1KB), preventing HTTP 400 cookie overflow errors on long Kundali reports.

### Swiss Ephemeris Diagnostics
To check whether Swiss Ephemeris is in Moshier analytical mode or precision ephemeris file mode:
```powershell
curl http://127.0.0.1:8000/api/system/ephemeris
```

