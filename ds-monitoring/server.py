from flask import Flask, request, render_template, jsonify
import subprocess
import base64
import os

app = Flask(__name__)

VALID_USER = "nagios"
VALID_PASS = "Monitor2026!"

def check_auth():
    auth = request.authorization
    if not auth or auth.username != VALID_USER or auth.password != VALID_PASS:
        return False
    return True

def require_auth():
    return ("Unauthorized", 401, {"WWW-Authenticate": 'Basic realm="DS Monitoring"'})

@app.route("/")
def index():
    if not check_auth():
        return require_auth()
    return render_template("dashboard.html")

# ──── VULN: Command injection via "Run Check" ────
@app.route("/check", methods=["POST"])
def run_check():
    if not check_auth():
        return require_auth()
    host = request.form.get("host", "")
    port = request.form.get("port", "22")
    try:
        # VULNERABLE: unsanitized input
        result = subprocess.run(
            f"nmap -Pn -p {port} {host}",
            shell=True, capture_output=True, text=True, timeout=15
        )
        output = result.stdout + result.stderr
    except:
        output = "Check timed out"
    return render_template("dashboard.html", check_output=output)

# ──── VULN: Config endpoint leaks DB credentials ────
@app.route("/config")
def config():
    if not check_auth():
        return require_auth()
    config_data = {
        "monitoring": {"version": "3.2.1", "check_interval": 60},
        "postgres": {"host": "10.10.30.10", "port": 5432, "user": "monitor_ro", "password": "M0n_R34d!", "database": "shieldcorp"},
        "alerts": {"email": "soc@digitalshield.local", "slack_webhook": "https://hooks.slack.com/services/REDACTED"},
        "note": "Read-only database access for monitoring queries"
    }
    return render_template("config.html", config=config_data)

# ──── VULN: LFI via log viewer ────
@app.route("/logs")
def logs():
    if not check_auth():
        return require_auth()
    logfile = request.args.get("file", "/var/log/syslog")
    try:
        with open(logfile, "r") as f:
            content = f.read()[:5000]
    except:
        content = f"Cannot read: {logfile}"
    return render_template("logs.html", logfile=logfile, content=content)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
