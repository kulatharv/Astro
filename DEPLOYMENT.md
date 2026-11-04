# 🚀 AstroLogic Production Deployment Guide

This guide covers all deployment options for taking the AstroLogic Vedic Astrology platform live in production.

---

## Architecture Overview

* **Frontend**: Next.js 16 (App Router, Turbopack, Tailwind CSS v4, `next-intl` for English, Hindi, and Marathi).
* **Backend**: FastAPI Gateway (Python 3.11, Swiss Ephemeris `pyswisseph`, Uvicorn, SQLite/PostgreSQL).
* **Communication**: Next.js server-side API routes proxy requests to the FastAPI backend via `BACKEND_URL`.

---

## Deployment Option 1: Docker Compose (Recommended for VPS / Cloud Servers)

*Compatible with AWS EC2, DigitalOcean Droplets, Linode, Hetzner, or any Linux VPS.*

### Prerequisites
* Docker & Docker Compose installed on your server:
  ```bash
  curl -fsSL https://get.docker.com | sh
  sudo apt-get install -y docker-compose-plugin
  ```

### Steps

1. **Clone the repository on your server:**
   ```bash
   git clone https://github.com/kulatharv/Astro.git
   cd Astro
   ```

2. **Configure your production environment:**
   ```bash
   cp .env.production.example .env.production
   # Edit .env.production with your domain and secret key:
   nano .env.production
   ```

3. **Build and launch the containers:**
   ```bash
   docker compose up -d --build
   ```

4. **Verify the services are live:**
   ```bash
   # Check container status
   docker compose ps

   # Check backend health
   curl http://localhost:8000/health
   # Expected output: {"status":"healthy"}

   # View live logs
   docker compose logs -f
   ```

Your platform is now running:
* **Frontend**: `http://YOUR_SERVER_IP:3000`
* **Backend**: `http://YOUR_SERVER_IP:8000`

---

## Deployment Option 2: Managed Cloud (Vercel + Render / Railway)

### Step A: Deploy the Backend on Render
1. Create a free account at [render.com](https://render.com).
2. Connect your GitHub repository: `https://github.com/kulatharv/Astro`.
3. Select **Web Service**:
   * **Root Directory**: `backend`
   * **Runtime**: Python 3
   * **Build Command**: `pip install --upgrade pip && pip install -r requirements.txt`
   * **Start Command**: `uvicorn gateway.main:app --host 0.0.0.0 --port $PORT --workers 4`
   * **Health Check Path**: `/health`
4. Add Environment Variables:
   * `ENVIRONMENT`: `production`
   * `SECRET_KEY`: *(Generate a secure random string)*
   * `ALLOWED_ORIGINS`: `https://YOUR_FRONTEND_DOMAIN.vercel.app`
5. Click **Deploy**. Note your backend URL (e.g., `https://astrologic-backend.onrender.com`).

### Step B: Deploy the Frontend on Vercel
1. Create a free account at [vercel.com](https://vercel.com).
2. Click **Add New Project** and import `https://github.com/kulatharv/Astro`.
3. Set **Root Directory** to `frontend`.
4. Framework Preset: **Next.js**.
5. Add Environment Variables:
   * `BACKEND_URL`: `https://astrologic-backend.onrender.com`
   * `BACKEND_API_URL`: `https://astrologic-backend.onrender.com`
6. Click **Deploy**.

---

## Deployment Option 3: VPS with Nginx Reverse Proxy & Free SSL (Let's Encrypt)

If hosting on a single domain (e.g. `astrologic.com`):

### Nginx Configuration (`/etc/nginx/sites-available/astrologic`):
```nginx
server {
    server_name astrologic.com www.astrologic.com;

    # Frontend routes
    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Direct backend API routes (Optional: Next.js proxies these automatically)
    location /api/ {
        proxy_pass http://127.0.0.1:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Enable SSL with Certbot:
```bash
sudo certbot --nginx -d astrologic.com -d www.astrologic.com
```

---

## Security & Sensitive Data Checklist

- [x] **No secrets in repository**: `.gitignore` strictly excludes all `.env*`, `*.db`, `*.pem`, `*.key`, and credentials.
- [x] **Non-Root Containers**: Dockerfiles run as unprivileged users (`nextjs` and `appuser`).
- [x] **Default-Deny Authentication**: FastAPI gateway enforces authorization and ratelimiting on non-public endpoints.
- [x] **Health Checks**: Live Docker and Uvicorn health monitoring via `/health`.
