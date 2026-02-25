# GameLog – Deployment Documentation
## Solo Project 3 · CPSC 3750

---

## Live URL
**`https://YOUR-CUSTOM-DOMAIN.com`** ← update after DNS setup

---

## Architecture Overview

```
Browser (Netlify + Custom Domain)
  ↕ fetch() over HTTPS
Flask Backend (Render)
  ↕ PyMySQL
MySQL Database (Railway)
```

| Layer    | Service  | URL |
|----------|----------|-----|
| Frontend | Netlify  | `https://your-domain.com` |
| Backend  | Render   | `https://your-app.onrender.com` |
| Database | Railway  | Internal MySQL connection |

---

## Tech Stack
- **Frontend**: HTML, CSS, JavaScript (no framework)
- **Backend**: Python 3.11 / Flask 3.x / Gunicorn
- **Database**: MySQL 8 hosted on Railway
- **ORM/Driver**: PyMySQL (raw SQL, no ORM)

---

## Database Schema

```sql
CREATE TABLE games (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    title       VARCHAR(80)  NOT NULL,
    platform    VARCHAR(50)  NOT NULL,
    status      VARCHAR(20)  NOT NULL,
    hours       DECIMAL(7,1) NOT NULL DEFAULT 0,
    image_url   VARCHAR(600) DEFAULT NULL,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

The table is created automatically on first startup if it does not exist.
30 seed records are inserted automatically if the table is empty.

---

## Secrets & Environment Variables

**No passwords or credentials are committed to Git.**

All secrets are set as environment variables in the Render dashboard:

| Variable      | Description |
|---------------|-------------|
| `DB_HOST`     | Railway MySQL host |
| `DB_PORT`     | Railway MySQL port (usually 3306) |
| `DB_USER`     | Railway MySQL username |
| `DB_PASSWORD` | Railway MySQL password |
| `DB_NAME`     | Database name (e.g. `railway`) |

---

## Deployment Guide

### Step 1 – Create Railway MySQL Database
1. Go to [railway.app](https://railway.app) and sign up (free)
2. New Project → **MySQL**
3. Click the MySQL service → **Variables** tab
4. Copy: `MYSQL_HOST`, `MYSQL_PORT`, `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_DATABASE`

### Step 2 – Deploy Backend to Render
1. Push the `backend/` folder to a GitHub repo
2. Go to [render.com](https://render.com) → **New Web Service**
3. Connect your GitHub repo
4. Settings:
   - **Language**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
5. Under **Environment Variables**, add all 5 DB_ variables from Railway
6. Deploy — wait ~2 minutes for the first build
7. Test: visit `https://your-app.onrender.com/api/games` — should return 30 games

### Step 3 – Configure Frontend
Edit `frontend/config.js`:
```js
const API_BASE = "https://your-app.onrender.com";
```

### Step 4 – Deploy Frontend to Netlify
1. Push `frontend/` to GitHub (can be same or separate repo)
2. Netlify → **Add new site → Import from Git**
3. Set **Publish directory** to the frontend folder
4. Deploy

### Step 5 – Connect Custom Domain
1. In Netlify: **Site Settings → Domain Management → Add custom domain**
2. Enter your domain (e.g. `gamelog.yourdomain.com`)
3. At your registrar (Namecheap, GoDaddy, etc.), set DNS:
   - For apex domain: **A record** → Netlify's load balancer IP (`75.2.60.5`)
   - For subdomain: **CNAME record** → `your-site.netlify.app`
4. Netlify auto-provisions an SSL certificate via Let's Encrypt (HTTPS)
5. DNS propagation takes 5–30 minutes

---

## Updating the App

**Backend changes:**
1. Push to GitHub → Render auto-redeploys

**Frontend changes:**
1. Push to GitHub → Netlify auto-redeploys

**Database migrations:**
- Connect to Railway MySQL with a client (TablePlus, DBeaver, or Railway's built-in shell)
- Run SQL manually for schema changes

---

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET    | `/api/games?page=1&page_size=10&search=&status=&platform=&sort=title&dir=asc` | Paginated, filtered, sorted list |
| GET    | `/api/games/{id}` | Single record |
| POST   | `/api/games` | Create record |
| PUT    | `/api/games/{id}` | Update record |
| DELETE | `/api/games/{id}` | Delete record |
| GET    | `/api/stats` | Aggregated statistics |

Validation errors return HTTP 422 with `{"errors": {"field": "message"}}`.
