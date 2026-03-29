from flask import Flask, request, jsonify, render_template, make_response
import hashlib
import json
import sqlite3
import time
import os

app = Flask(__name__)
DB_PATH = "/tmp/scoreboard.db"

FLAGS = {
    hashlib.sha256(b"FLAG{ds_1_wordpress_initial_foothold}").hexdigest(): {"id": 1, "name": "Initial Foothold", "category": "Web Exploitation", "points": 100, "difficulty": "Easy", "hint": "The company website has a health check feature. What happens if you're authenticated?"},
    hashlib.sha256(b"FLAG{ds_2_corporate_email_intelligence}").hexdigest(): {"id": 2, "name": "Email Intelligence", "category": "OSINT", "points": 100, "difficulty": "Easy", "hint": "Staff names from the careers page might have email accounts. Try common corporate passwords."},
    hashlib.sha256(b"FLAG{ds_3_redis_session_hijack}").hexdigest(): {"id": 3, "name": "Session Hijack", "category": "Misconfiguration", "points": 150, "difficulty": "Medium", "hint": "Developer tools often use caching services. Is authentication required?"},
    hashlib.sha256(b"FLAG{ds_4_jumphost_privesc_complete}").hexdigest(): {"id": 4, "name": "Bastion Breach", "category": "Privilege Escalation", "points": 200, "difficulty": "Medium", "hint": "Check what commands you can run with elevated privileges. GTFOBins is your friend."},
    hashlib.sha256(b"FLAG{ds_5_filestore_data_breach}").hexdigest(): {"id": 5, "name": "Data Breach", "category": "Data Exfiltration", "points": 150, "difficulty": "Medium", "hint": "The file server has confidential documents. You'll need the right credentials to access them."},
    hashlib.sha256(b"FLAG{ds_6_monitoring_system_owned}").hexdigest(): {"id": 6, "name": "Eyes Everywhere", "category": "Web Exploitation", "points": 100, "difficulty": "Easy", "hint": "Monitoring systems often use default credentials. Check common ones."},
    hashlib.sha256(b"FLAG{ds_7_database_secrets_decrypted}").hexdigest(): {"id": 7, "name": "Crypto Breach", "category": "Cryptography", "points": 250, "difficulty": "Hard", "hint": "The secrets table has encrypted data. The key might be closer than you think."},
    hashlib.sha256(b"FLAG{ds_8_database_root_compromise}").hexdigest(): {"id": 8, "name": "DB Takeover", "category": "Privilege Escalation", "points": 200, "difficulty": "Medium", "hint": "PostgreSQL has powerful features that can execute system commands."},
    hashlib.sha256(b"FLAG{ds_9_vault_secrets_exfiltrated}").hexdigest(): {"id": 9, "name": "Vault Raider", "category": "API Exploitation", "points": 200, "difficulty": "Medium", "hint": "The vault API requires a bearer token. Where might one be stored?"},
    hashlib.sha256(b"FLAG{ds_10_full_kill_chain_complete}").hexdigest(): {"id": 10, "name": "Full Compromise", "category": "Privilege Escalation", "points": 300, "difficulty": "Hard", "hint": "The final flag requires root on the vault. Check your sudo privileges carefully."},
}

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    db = get_db()
    db.execute("""CREATE TABLE IF NOT EXISTS players (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE,
        created_at REAL
    )""")
    db.execute("""CREATE TABLE IF NOT EXISTS captures (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        player_id INTEGER,
        flag_id INTEGER,
        flag_name TEXT,
        points INTEGER,
        captured_at REAL,
        UNIQUE(player_id, flag_id)
    )""")
    db.commit()
    db.close()

init_db()

@app.route("/")
def index():
    player = request.cookies.get("ds_player", "")
    return render_template("scoreboard.html", player=player)

@app.route("/api/register", methods=["POST"])
def register():
    data = request.get_json()
    name = data.get("name", "").strip()
    if not name:
        return jsonify({"error": "Name required"}), 400
    db = get_db()
    try:
        db.execute("INSERT INTO players (name, created_at) VALUES (?, ?)", (name, time.time()))
        db.commit()
    except sqlite3.IntegrityError:
        pass
    db.close()
    resp = make_response(jsonify({"status": "registered", "name": name}))
    resp.set_cookie("ds_player", name, max_age=86400*30)
    return resp

@app.route("/api/submit", methods=["POST"])
def submit_flag():
    data = request.get_json()
    flag = data.get("flag", "").strip()
    player_name = request.cookies.get("ds_player", "")
    if not player_name:
        return jsonify({"error": "Register first"}), 400

    flag_hash = hashlib.sha256(flag.encode()).hexdigest()
    flag_info = FLAGS.get(flag_hash)
    if not flag_info:
        return jsonify({"correct": False, "message": "Invalid flag"}), 200

    db = get_db()
    player = db.execute("SELECT id FROM players WHERE name = ?", (player_name,)).fetchone()
    if not player:
        return jsonify({"error": "Player not found"}), 400

    existing = db.execute("SELECT id FROM captures WHERE player_id = ? AND flag_id = ?", (player["id"], flag_info["id"])).fetchone()
    if existing:
        db.close()
        return jsonify({"correct": True, "already": True, "message": f"Already captured: {flag_info['name']} ({flag_info['points']} pts)"})

    db.execute("INSERT INTO captures (player_id, flag_id, flag_name, points, captured_at) VALUES (?, ?, ?, ?, ?)",
               (player["id"], flag_info["id"], flag_info["name"], flag_info["points"], time.time()))
    db.commit()
    db.close()
    return jsonify({"correct": True, "message": f"Correct! {flag_info['name']} — {flag_info['points']} points", "name": flag_info["name"], "points": flag_info["points"]})

@app.route("/api/progress")
def progress():
    player_name = request.cookies.get("ds_player", "")
    db = get_db()
    captures = []
    total_points = 0
    if player_name:
        player = db.execute("SELECT id FROM players WHERE name = ?", (player_name,)).fetchone()
        if player:
            rows = db.execute("SELECT flag_id, flag_name, points, captured_at FROM captures WHERE player_id = ? ORDER BY captured_at", (player["id"],)).fetchall()
            captures = [{"id": r["flag_id"], "name": r["flag_name"], "points": r["points"]} for r in rows]
            total_points = sum(r["points"] for r in rows)
    db.close()

    flags_info = []
    for fhash, info in sorted(FLAGS.items(), key=lambda x: x[1]["id"]):
        captured = any(c["id"] == info["id"] for c in captures)
        flags_info.append({"id": info["id"], "name": info["name"], "category": info["category"], "points": info["points"], "difficulty": info["difficulty"], "captured": captured})

    return jsonify({"player": player_name, "captures": captures, "total_points": total_points, "max_points": 1750, "flags": flags_info})

@app.route("/api/leaderboard")
def leaderboard():
    db = get_db()
    rows = db.execute("""
        SELECT p.name, COUNT(c.id) as flags, SUM(c.points) as points, MAX(c.captured_at) as last_capture
        FROM players p LEFT JOIN captures c ON p.id = c.player_id
        GROUP BY p.id ORDER BY points DESC, last_capture ASC
    """).fetchall()
    db.close()
    return jsonify([{"name": r["name"], "flags": r["flags"] or 0, "points": r["points"] or 0} for r in rows])

@app.route("/api/hint", methods=["POST"])
def get_hint():
    data = request.get_json()
    flag_id = data.get("flag_id", 0)
    for info in FLAGS.values():
        if info["id"] == flag_id:
            return jsonify({"hint": info["hint"], "cost": f"-{info['points']//4} points"})
    return jsonify({"error": "Flag not found"}), 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
