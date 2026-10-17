from flask import Flask, send_from_directory, jsonify, request
import os
import sqlite3
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.environ.get("SQLITE_PATH", os.path.join(BASE_DIR, "scores.db"))

app = Flask(__name__)

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""CREATE TABLE IF NOT EXISTS scores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        topic TEXT, score INTEGER, total INTEGER,
        created_at TEXT)""")
    return conn

@app.route("/")
def home():
    return send_from_directory(BASE_DIR, "index.html")

@app.route("/privacy")
@app.route("/privacy.html")
def privacy():
    return send_from_directory(BASE_DIR, "privacy.html")

@app.route("/ads.txt")
def ads_txt():
    return send_from_directory(BASE_DIR, "ads.txt", mimetype="text/plain")

@app.route("/robots.txt")
def robots():
    return send_from_directory(BASE_DIR, "robots.txt", mimetype="text/plain")

@app.route("/manifest.json")
@app.route("/manifest.webmanifest")
def manifest():
    return send_from_directory(BASE_DIR, "manifest.json", mimetype="application/manifest+json")

@app.route("/service-worker.js")
@app.route("/sw.js")
def sw():
    return send_from_directory(BASE_DIR, "service-worker.js", mimetype="application/javascript")

@app.route("/icon.svg")
@app.route("/icon.png")
def icon():
    # serve svg icon; png fallback to svg if png missing
    fname = request.path.lstrip("/")
    fpath = os.path.join(BASE_DIR, fname)
    if os.path.exists(fpath):
        return send_from_directory(BASE_DIR, fname)
    return send_from_directory(BASE_DIR, "icon.svg", mimetype="image/svg+xml")

@app.route("/health")
@app.route("/healthz")
def health():
    return jsonify(status="ok", time=datetime.utcnow().isoformat()), 200

# ---- Simple score API (SQLite, works on Render free without extra DB) ----
@app.route("/api/score", methods=["POST"])
def save_score():
    try:
        data = request.get_json(force=True) or {}
        topic = str(data.get("topic", ""))[:50]
        score = int(data.get("score", 0))
        total = int(data.get("total", 0))
        conn = get_db()
        conn.execute("INSERT INTO scores (topic, score, total, created_at) VALUES (?,?,?,?)",
                     (topic, score, total, datetime.utcnow().isoformat()))
        conn.commit()
        conn.close()
        return jsonify(ok=True), 201
    except Exception as e:
        return jsonify(ok=False, error=str(e)), 400

@app.route("/api/scores")
def list_scores():
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT topic, score, total, created_at FROM scores ORDER BY id DESC LIMIT 50")
        rows = [{"topic": r[0], "score": r[1], "total": r[2], "created_at": r[3]} for r in cur.fetchall()]
        conn.close()
        return jsonify(rows)
    except Exception as e:
        return jsonify(error=str(e)), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
