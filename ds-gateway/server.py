from flask import Flask, request, render_template, send_from_directory, session, redirect, url_for
import subprocess
import os
import hashlib

app = Flask(__name__)
app.secret_key = "ds-gateway-s3cr3t-k3y-2026"

UPLOAD_DIR = "/app/uploads"
ADMIN_USERS = {
    "admin": hashlib.sha256(b"Shield2026!").hexdigest(),
}

# ──── PUBLIC PAGES ────

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/services")
def services():
    return render_template("services.html")

@app.route("/careers")
def careers():
    return render_template("careers.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

# ──── ADMIN LOGIN (brute-forceable) ────

@app.route("/admin", methods=["GET", "POST"])
def admin_login():
    error = ""
    if request.method == "POST":
        user = request.form.get("username", "")
        pwd = request.form.get("password", "")
        pwd_hash = hashlib.sha256(pwd.encode()).hexdigest()
        if user in ADMIN_USERS and ADMIN_USERS[user] == pwd_hash:
            session["admin"] = user
            return redirect("/admin/dashboard")
        error = "Invalid credentials"
    return render_template("admin_login.html", error=error)

@app.route("/admin/dashboard")
def admin_dashboard():
    if "admin" not in session:
        return redirect("/admin")
    return render_template("admin_dashboard.html")

# ──── VULN: Command injection via health check (requires admin auth) ────
@app.route("/admin/healthcheck", methods=["POST"])
def healthcheck():
    if "admin" not in session:
        return redirect("/admin")
    target = request.form.get("target", "")
    try:
        result = subprocess.run(f"ping -c 2 {target}", shell=True, capture_output=True, text=True, timeout=30)
        output = result.stdout + result.stderr
    except:
        output = "Error running check"
    return render_template("admin_dashboard.html", check_output=output)

# ──── VULN: Local File Inclusion via "page" parameter ────
@app.route("/page")
def page_view():
    p = request.args.get("name", "about")
    # Vulnerable: allows path traversal
    try:
        filepath = os.path.join("/var/www", p)
        # VULN: If path is a directory, list its contents (misconfigured directory listing)
        if os.path.isdir(filepath):
            files = os.listdir(filepath)
            listing = "\n".join(files) if files else "(empty directory)"
            return f"<html><head><title>Digital Shield</title><link rel='stylesheet' href='/static/style.css'></head><body style='background:#0a1628;color:#c8d6e5;font-family:monospace;padding:40px'><h3>Index of /page?name={p}</h3><pre>{listing}</pre><p><a href='/' style='color:#00b4d8'>Home</a></p></body></html>"
        with open(filepath, "r") as f:
            content = f.read()
        return f"<html><head><title>Digital Shield</title><link rel='stylesheet' href='/static/style.css'></head><body style='background:#0a1628;color:#c8d6e5;font-family:monospace;padding:40px'><pre>{content}</pre><p><a href='/' style='color:#00b4d8'>Home</a></p></body></html>"
    except:
        return "Page not found", 404

# ──── File Upload (requires admin) ────
@app.route("/admin/upload", methods=["POST"])
def upload():
    if "admin" not in session:
        return redirect("/admin")
    f = request.files.get("file")
    if f and f.filename:
        save_path = os.path.join(UPLOAD_DIR, f.filename)
        f.save(save_path)
        os.chmod(save_path, 0o755)
        return redirect("/admin/dashboard")
    return redirect("/admin/dashboard")

@app.route("/uploads/<path:filename>")
def serve_upload(filename):
    return send_from_directory(UPLOAD_DIR, filename)

# ──── API: User enumeration (exposed by design) ────
@app.route("/api/v1/team")
def api_team():
    return {"employees": [
        {"name": "James Reynolds", "role": "Senior Security Analyst", "username": "j.reynolds"},
        {"name": "Michelle Chen", "role": "DevOps Lead", "username": "m.chen"},
        {"name": "Adrian Kowalski", "role": "Systems Administrator", "username": "a.kowalski"},
        {"name": "Dayo Okafor", "role": "Chief Technology Officer", "username": "d.okafor"},
    ]}

@app.route("/robots.txt")
def robots():
    return "User-agent: *\nDisallow: /admin\nDisallow: /page?name=maintenance\nDisallow: /api/v1/\n", 200, {"Content-Type": "text/plain"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
