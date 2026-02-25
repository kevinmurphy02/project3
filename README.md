# GameLog — Collection Manager

A video game backlog and wishlist manager. Solo Project 3 for CPSC 3750.

Live site: https://kevinmurphy02.github.io/project3/

---

## Domain & Hosting

- **Domain:** [kevinmurphyproject3.com](https://kevinmurphy02.github.io/project3/)
- **Frontend hosting:** GitHub Pages (served from the `/docs` folder)
- **Backend hosting:** Railway
- **Database hosting:** Railway (MySQL)

---

## Tech Stack

- **Frontend:** HTML, CSS, JavaScript
- **Backend:** Python 3 / Flask / Gunicorn
- **Database:** MySQL 8

---

## Database

MySQL database hosted on Railway. The table is created automatically on first startup. 30 seed records are inserted if the table is empty. No manual database setup is required.

---

## How to Deploy

**Frontend:**
1. Push changes to the `docs/` folder on GitHub
2. GitHub Pages automatically serves the updated files within a few minutes

**Backend:**
1. Push changes to the `backend/` folder on GitHub
2. Railway automatically redeploys the Flask app on every push

---

## How to Update the App

Edit files locally or directly on GitHub, commit and push — both GitHub Pages and Railway redeploy automatically.

---

## Configuration & Secrets

No passwords or credentials are stored in the code or repository.

The Flask backend connects to MySQL using environment variables set in the Railway dashboard:

| Variable | Description |
|----------|-------------|
| `DB_HOST` | MySQL host |
| `DB_PORT` | MySQL port |
| `DB_USER` | MySQL username |
| `DB_PASSWORD` | MySQL password |
| `DB_NAME` | Database name |

These are set once in Railway and never committed to Git.
