"""
Collection Manager – Solo Project 3
Backend: Python / Flask
Database: MySQL (Railway)
Features: Full CRUD, search, filter, sort, configurable paging, images, stats
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import pymysql
import os
import time
import random
import string

app = Flask(__name__)
CORS(app)

# ── Database config from environment variables ─────────────────────────────
DB_CONFIG = {
    "host":     os.environ.get("DB_HOST", "localhost"),
    "port":     int(os.environ.get("DB_PORT", 3306)),
    "user":     os.environ.get("DB_USER", "root"),
    "password": os.environ.get("DB_PASSWORD", ""),
    "database": os.environ.get("DB_NAME", "collection_manager"),
    "charset":  "utf8mb4",
    "cursorclass": pymysql.cursors.DictCursor,
    "autocommit": True,
}

VALID_PLATFORMS = {"PC", "PlayStation", "Xbox", "Nintendo Switch", "Mobile", "Other"}
VALID_STATUSES  = {"Wishlist", "Backlog", "Playing", "Completed", "Dropped"}
VALID_SORTS     = {"title", "platform", "status", "hours", "created_at"}
VALID_DIRS      = {"asc", "desc"}
VALID_PAGE_SIZES = {5, 10, 20, 50}

PLACEHOLDER_IMAGE = "https://placehold.co/300x200/1a2240/6aa7ff?text=No+Cover"

# ── Seed data (30 records with Steam cover art) ────────────────────────────
SEED_GAMES = [
    {"title": "Elden Ring",                    "platform": "PlayStation",     "status": "Backlog",   "hours": 0,     "image_url": "https://cdn.cloudflare.steamstatic.com/steam/apps/1245620/header.jpg"},
    {"title": "Baldur's Gate 3",               "platform": "PC",              "status": "Backlog",   "hours": 0,     "image_url": "https://cdn.cloudflare.steamstatic.com/steam/apps/1086940/header.jpg"},
    {"title": "Hades",                         "platform": "Nintendo Switch", "status": "Completed", "hours": 55.5,  "image_url": "https://cdn.cloudflare.steamstatic.com/steam/apps/1145360/header.jpg"},
    {"title": "Cyberpunk 2077",                "platform": "Xbox",            "status": "Playing",   "hours": 18.0,  "image_url": "https://cdn.cloudflare.steamstatic.com/steam/apps/1091500/header.jpg"},
    {"title": "The Witcher 3",                 "platform": "PC",              "status": "Completed", "hours": 120.0, "image_url": "https://cdn.cloudflare.steamstatic.com/steam/apps/292030/header.jpg"},
    {"title": "Red Dead Redemption 2",         "platform": "PlayStation",     "status": "Backlog",   "hours": 0,     "image_url": "https://cdn.cloudflare.steamstatic.com/steam/apps/1174180/header.jpg"},
    {"title": "Hollow Knight",                 "platform": "PC",              "status": "Wishlist",  "hours": 0,     "image_url": "https://cdn.cloudflare.steamstatic.com/steam/apps/367520/header.jpg"},
    {"title": "Stardew Valley",                "platform": "Nintendo Switch", "status": "Completed", "hours": 90.0,  "image_url": "https://cdn.cloudflare.steamstatic.com/steam/apps/413150/header.jpg"},
    {"title": "Sekiro: Shadows Die Twice",     "platform": "PC",              "status": "Wishlist",  "hours": 0,     "image_url": "https://cdn.cloudflare.steamstatic.com/steam/apps/814380/header.jpg"},
    {"title": "God of War (2018)",             "platform": "PlayStation",     "status": "Backlog",   "hours": 0,     "image_url": "https://cdn.cloudflare.steamstatic.com/steam/apps/1593500/header.jpg"},
    {"title": "Ghost of Tsushima",             "platform": "PlayStation",     "status": "Wishlist",  "hours": 0,     "image_url": "https://cdn.cloudflare.steamstatic.com/steam/apps/2215430/header.jpg"},
    {"title": "Persona 5 Royal",               "platform": "PlayStation",     "status": "Backlog",   "hours": 0,     "image_url": "https://cdn.cloudflare.steamstatic.com/steam/apps/1687950/header.jpg"},
    {"title": "Slay the Spire",                "platform": "Mobile",          "status": "Playing",   "hours": 12.5,  "image_url": "https://cdn.cloudflare.steamstatic.com/steam/apps/646570/header.jpg"},
    {"title": "Ori and the Will of the Wisps", "platform": "Xbox",            "status": "Backlog",   "hours": 0,     "image_url": "https://cdn.cloudflare.steamstatic.com/steam/apps/1057090/header.jpg"},
    {"title": "Celeste",                       "platform": "Nintendo Switch", "status": "Completed", "hours": 22.0,  "image_url": "https://cdn.cloudflare.steamstatic.com/steam/apps/504230/header.jpg"},
    {"title": "Disco Elysium",                 "platform": "PC",              "status": "Backlog",   "hours": 0,     "image_url": "https://cdn.cloudflare.steamstatic.com/steam/apps/632470/header.jpg"},
    {"title": "Monster Hunter: World",         "platform": "PC",              "status": "Dropped",   "hours": 9.0,   "image_url": "https://cdn.cloudflare.steamstatic.com/steam/apps/582010/header.jpg"},
    {"title": "Spider-Man Remastered",         "platform": "PlayStation",     "status": "Completed", "hours": 28.5,  "image_url": "https://cdn.cloudflare.steamstatic.com/steam/apps/1817070/header.jpg"},
    {"title": "Control",                       "platform": "PC",              "status": "Backlog",   "hours": 0,     "image_url": "https://cdn.cloudflare.steamstatic.com/steam/apps/870780/header.jpg"},
    {"title": "DOOM Eternal",                  "platform": "Xbox",            "status": "Backlog",   "hours": 0,     "image_url": "https://cdn.cloudflare.steamstatic.com/steam/apps/782330/header.jpg"},
    {"title": "The Last of Us Part I",         "platform": "PlayStation",     "status": "Backlog",   "hours": 0,     "image_url": "https://cdn.cloudflare.steamstatic.com/steam/apps/1888930/header.jpg"},
    {"title": "Resident Evil 4 (Remake)",      "platform": "PlayStation",     "status": "Wishlist",  "hours": 0,     "image_url": "https://cdn.cloudflare.steamstatic.com/steam/apps/2050650/header.jpg"},
    {"title": "Final Fantasy VII Remake",      "platform": "PlayStation",     "status": "Playing",   "hours": 6.0,   "image_url": "https://cdn.cloudflare.steamstatic.com/steam/apps/1462040/header.jpg"},
    {"title": "Final Fantasy XIV",             "platform": "PC",              "status": "Dropped",   "hours": 14.0,  "image_url": "https://cdn.cloudflare.steamstatic.com/steam/apps/39210/header.jpg"},
    {"title": "Overwatch 2",                   "platform": "PC",              "status": "Playing",   "hours": 42.0,  "image_url": "https://cdn.cloudflare.steamstatic.com/steam/apps/2357570/header.jpg"},
    {"title": "Outer Wilds",                   "platform": "PC",              "status": "Wishlist",  "hours": 0,     "image_url": "https://cdn.cloudflare.steamstatic.com/steam/apps/753640/header.jpg"},
    {"title": "Fortnite",                      "platform": "Xbox",            "status": "Playing",   "hours": 110.0, "image_url": "https://cdn2.unrealengine.com/fortnite-chapter-5-season-1-2560x1440-e87f7e0e2e1d.jpg"},
    {"title": "Minecraft",                     "platform": "PC",              "status": "Completed", "hours": 200.0, "image_url": "https://www.minecraft.net/content/dam/games/minecraft/key-art/MC_Anniversary_KeyArt-1170x500.jpg"},
    {"title": "Mario Kart 8 Deluxe",           "platform": "Nintendo Switch", "status": "Playing",   "hours": 35.0,  "image_url": "https://assets.nintendo.com/image/upload/ar_16:9,b_auto:border,c_lpad/b_white/f_auto/q_auto/dpr_auto/c_scale,w_300/v1/ncom/software/switch/70010000000153/e3a47b3f31d41d4da96e0ab1f51c5cc7c8019e5df00a87e7dccbb84e73d49462"},
    {"title": "Animal Crossing: New Horizons", "platform": "Nintendo Switch", "status": "Completed", "hours": 140.0, "image_url": "https://assets.nintendo.com/image/upload/ar_16:9,b_auto:border,c_lpad/b_white/f_auto/q_auto/dpr_auto/c_scale,w_300/v1/ncom/software/switch/70010000025130/4a6d5b5a8e0e98fe0d08a24efa3bc43e48b86a3c"},
]


# ── DB helpers ─────────────────────────────────────────────────────────────
def get_db():
    return pymysql.connect(**DB_CONFIG)


def init_db():
    """Create table if not exists and seed if empty."""
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS games (
                    id          INT AUTO_INCREMENT PRIMARY KEY,
                    title       VARCHAR(80)  NOT NULL,
                    platform    VARCHAR(50)  NOT NULL,
                    status      VARCHAR(20)  NOT NULL,
                    hours       DECIMAL(7,1) NOT NULL DEFAULT 0,
                    image_url   VARCHAR(600) DEFAULT NULL,
                    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
            """)
            cur.execute("SELECT COUNT(*) as cnt FROM games")
            row = cur.fetchone()
            if row["cnt"] == 0:
                for g in SEED_GAMES:
                    cur.execute(
                        "INSERT INTO games (title, platform, status, hours, image_url) VALUES (%s,%s,%s,%s,%s)",
                        (g["title"], g["platform"], g["status"], g["hours"], g.get("image_url"))
                    )
                conn.commit()
    finally:
        conn.close()


# ── Validation ─────────────────────────────────────────────────────────────
def validate_game(body):
    errors = {}
    title     = (body.get("title") or "").strip()
    platform  = (body.get("platform") or "").strip()
    status    = (body.get("status") or "").strip()
    hours_raw = body.get("hours")
    image_url = (body.get("image_url") or "").strip()

    if len(title) < 2 or len(title) > 80:
        errors["title"] = "Title must be 2–80 characters."
    if platform not in VALID_PLATFORMS:
        errors["platform"] = f"Platform must be one of: {', '.join(sorted(VALID_PLATFORMS))}."
    if status not in VALID_STATUSES:
        errors["status"] = f"Status must be one of: {', '.join(sorted(VALID_STATUSES))}."
    try:
        h = float(hours_raw)
        if h < 0 or h > 9999:
            raise ValueError
    except (TypeError, ValueError):
        errors["hours"] = "Hours must be a number between 0 and 9999."
    if image_url and len(image_url) > 600:
        errors["image_url"] = "Image URL must be under 600 characters."

    return errors


# ── Routes ─────────────────────────────────────────────────────────────────

@app.route("/api/games", methods=["GET"])
def get_games():
    # Query params
    try:
        page = max(1, int(request.args.get("page", 1)))
    except:
        page = 1
    try:
        page_size = int(request.args.get("page_size", 10))
        if page_size not in VALID_PAGE_SIZES:
            page_size = 10
    except:
        page_size = 10

    search   = (request.args.get("search") or "").strip()
    status_f = (request.args.get("status") or "").strip()
    platform_f = (request.args.get("platform") or "").strip()
    sort     = request.args.get("sort", "title")
    direction = request.args.get("dir", "asc").lower()

    if sort not in VALID_SORTS:
        sort = "title"
    if direction not in VALID_DIRS:
        direction = "asc"

    # Build WHERE
    conditions = []
    params = []
    if search:
        conditions.append("title LIKE %s")
        params.append(f"%{search}%")
    if status_f and status_f in VALID_STATUSES:
        conditions.append("status = %s")
        params.append(status_f)
    if platform_f and platform_f in VALID_PLATFORMS:
        conditions.append("platform = %s")
        params.append(platform_f)

    where = ("WHERE " + " AND ".join(conditions)) if conditions else ""

    conn = get_db()
    try:
        with conn.cursor() as cur:
            # Total count
            cur.execute(f"SELECT COUNT(*) as cnt FROM games {where}", params)
            total = cur.fetchone()["cnt"]

            total_pages = max(1, -(-total // page_size))
            page = min(page, total_pages)
            offset = (page - 1) * page_size

            # Fetch page
            cur.execute(
                f"SELECT * FROM games {where} ORDER BY {sort} {direction} LIMIT %s OFFSET %s",
                params + [page_size, offset]
            )
            games = cur.fetchall()

            # Replace null image_url with placeholder
            for g in games:
                if not g.get("image_url"):
                    g["image_url"] = PLACEHOLDER_IMAGE
                # Convert decimals to float for JSON
                g["hours"] = float(g["hours"])
                if g.get("created_at"):
                    g["created_at"] = g["created_at"].isoformat()
                if g.get("updated_at"):
                    g["updated_at"] = g["updated_at"].isoformat()

        return jsonify({
            "games": games,
            "page": page,
            "total_pages": total_pages,
            "total": total,
            "page_size": page_size,
        })
    finally:
        conn.close()


@app.route("/api/games", methods=["POST"])
def create_game():
    body = request.get_json(silent=True) or {}
    errors = validate_game(body)
    if errors:
        return jsonify({"errors": errors}), 422

    image_url = (body.get("image_url") or "").strip() or None
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO games (title, platform, status, hours, image_url) VALUES (%s,%s,%s,%s,%s)",
                (body["title"].strip(), body["platform"].strip(), body["status"].strip(),
                 float(body["hours"]), image_url)
            )
            conn.commit()
            new_id = cur.lastrowid
            cur.execute("SELECT * FROM games WHERE id = %s", (new_id,))
            game = cur.fetchone()
            game["hours"] = float(game["hours"])
            if not game.get("image_url"):
                game["image_url"] = PLACEHOLDER_IMAGE
            if game.get("created_at"):
                game["created_at"] = game["created_at"].isoformat()
            if game.get("updated_at"):
                game["updated_at"] = game["updated_at"].isoformat()
        return jsonify(game), 201
    finally:
        conn.close()


@app.route("/api/games/<int:game_id>", methods=["GET"])
def get_game(game_id):
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM games WHERE id = %s", (game_id,))
            game = cur.fetchone()
        if not game:
            return jsonify({"error": "Not found"}), 404
        game["hours"] = float(game["hours"])
        if not game.get("image_url"):
            game["image_url"] = PLACEHOLDER_IMAGE
        if game.get("created_at"):
            game["created_at"] = game["created_at"].isoformat()
        if game.get("updated_at"):
            game["updated_at"] = game["updated_at"].isoformat()
        return jsonify(game)
    finally:
        conn.close()


@app.route("/api/games/<int:game_id>", methods=["PUT"])
def update_game(game_id):
    body = request.get_json(silent=True) or {}
    errors = validate_game(body)
    if errors:
        return jsonify({"errors": errors}), 422

    image_url = (body.get("image_url") or "").strip() or None
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM games WHERE id = %s", (game_id,))
            if not cur.fetchone():
                return jsonify({"error": "Not found"}), 404
            cur.execute(
                "UPDATE games SET title=%s, platform=%s, status=%s, hours=%s, image_url=%s WHERE id=%s",
                (body["title"].strip(), body["platform"].strip(), body["status"].strip(),
                 float(body["hours"]), image_url, game_id)
            )
            conn.commit()
            cur.execute("SELECT * FROM games WHERE id = %s", (game_id,))
            game = cur.fetchone()
            game["hours"] = float(game["hours"])
            if not game.get("image_url"):
                game["image_url"] = PLACEHOLDER_IMAGE
            if game.get("created_at"):
                game["created_at"] = game["created_at"].isoformat()
            if game.get("updated_at"):
                game["updated_at"] = game["updated_at"].isoformat()
        return jsonify(game)
    finally:
        conn.close()


@app.route("/api/games/<int:game_id>", methods=["DELETE"])
def delete_game(game_id):
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM games WHERE id = %s", (game_id,))
            if not cur.fetchone():
                return jsonify({"error": "Not found"}), 404
            cur.execute("DELETE FROM games WHERE id = %s", (game_id,))
            conn.commit()
        return jsonify({"deleted": game_id})
    finally:
        conn.close()


@app.route("/api/stats", methods=["GET"])
def get_stats():
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) as total FROM games")
            total = cur.fetchone()["total"]

            cur.execute("SELECT status, COUNT(*) as cnt FROM games GROUP BY status ORDER BY cnt DESC")
            by_status = {r["status"]: r["cnt"] for r in cur.fetchall()}

            cur.execute("SELECT platform, COUNT(*) as cnt FROM games GROUP BY platform ORDER BY cnt DESC")
            by_platform = {r["platform"]: r["cnt"] for r in cur.fetchall()}

            cur.execute("SELECT SUM(hours) as total_hours FROM games")
            total_hours = float(cur.fetchone()["total_hours"] or 0)

            completed = by_status.get("Completed", 0)
            cur.execute("SELECT AVG(hours) as avg_h FROM games WHERE status='Completed'")
            avg_completed = float(cur.fetchone()["avg_h"] or 0)

            completion_rate = round(completed / total * 100, 1) if total else 0

            cur.execute("SELECT title, hours FROM games ORDER BY hours DESC LIMIT 1")
            most_played = cur.fetchone()
            if most_played:
                most_played["hours"] = float(most_played["hours"])

        return jsonify({
            "total": total,
            "by_status": by_status,
            "by_platform": by_platform,
            "completion_rate": completion_rate,
            "total_hours": round(total_hours, 1),
            "avg_hours_completed": round(avg_completed, 1),
            "most_played": most_played,
        })
    finally:
        conn.close()


@app.route("/", methods=["GET"])
def health():
    return jsonify({"status": "ok", "service": "Collection Manager SP3 API"})


# ── Boot ───────────────────────────────────────────────────────────────────
with app.app_context():
    try:
        init_db()
    except Exception as e:
        print(f"DB init warning: {e}")

if __name__ == "__main__":
    app.run(debug=True, port=5000)
