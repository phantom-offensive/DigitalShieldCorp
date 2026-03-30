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
        result = subprocess.run(f"ping -c 2 {target}", shell=True, capture_output=True, text=True, timeout=120)
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
        return redirect("/uploads/")
    return redirect("/admin/dashboard")

# ──── VULN: Directory listing of uploads — shows all uploaded files ────
@app.route("/uploads/")
def list_uploads():
    files = []
    if os.path.isdir(UPLOAD_DIR):
        for fname in sorted(os.listdir(UPLOAD_DIR)):
            fpath = os.path.join(UPLOAD_DIR, fname)
            size = os.path.getsize(fpath)
            files.append({"name": fname, "size": size})
    rows = ""
    for f in files:
        is_script = f["name"].endswith((".sh", ".py", ".php", ".pl", ".rb"))
        run_link = f' &nbsp; <a href="/uploads/{f["name"]}/run" style="color:#10b981;font-size:12px">[Execute]</a>' if is_script else ""
        rows += f'<tr><td><a href="/uploads/{f["name"]}" style="color:#00b4d8">{f["name"]}</a>{run_link}</td><td style="color:#6b7280">{f["size"]} bytes</td></tr>\n'
    if not rows:
        rows = '<tr><td colspan="2" style="color:#6b7280;padding:20px;text-align:center">No files uploaded yet</td></tr>'
    return f'''<html><head><title>Uploads — Digital Shield</title><link rel="stylesheet" href="/static/style.css"></head>
<body style="background:#0a1628;color:#c8d6e5;font-family:monospace;padding:40px">
<h2>Uploaded Files</h2>
<p style="color:#5a6f8a;font-size:12px;margin-bottom:16px">Click [Execute] to run scripts on the server</p>
<table style="width:100%;border-collapse:collapse;">
<thead><tr style="border-bottom:1px solid #1a2d4a"><th style="text-align:left;padding:8px;color:#8b9dc3">File</th><th style="text-align:left;padding:8px;color:#8b9dc3">Size</th></tr></thead>
<tbody>{rows}</tbody></table>
<p style="margin-top:20px"><a href="/admin/dashboard" style="color:#00b4d8">Back to Dashboard</a></p>
</body></html>'''

# ──── VULN: Execute uploaded scripts (RCE via file upload) ────
@app.route("/uploads/<path:filename>/run")
def run_upload(filename):
    fpath = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(fpath):
        return "File not found", 404
    try:
        if filename.endswith(".sh"):
            result = subprocess.Popen(["bash", fpath], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        elif filename.endswith(".py"):
            result = subprocess.Popen(["python3", fpath], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        elif filename.endswith(".php"):
            result = subprocess.Popen(["php", fpath], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        elif filename.endswith((".pl", ".rb")):
            result = subprocess.Popen([fpath], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        else:
            return "Not an executable script", 400
        # Wait up to 5 seconds for immediate output, but don't block on long-running processes
        try:
            stdout, stderr = result.communicate(timeout=5)
            output = stdout.decode(errors="replace") + stderr.decode(errors="replace")
        except subprocess.TimeoutExpired:
            output = f"Script started in background (PID: {result.pid})"
        return f'''<html><head><title>Execute — Digital Shield</title><link rel="stylesheet" href="/static/style.css"></head>
<body style="background:#0a1628;color:#c8d6e5;font-family:monospace;padding:40px">
<h3 style="color:#10b981">Executed: {filename}</h3>
<pre style="background:#0d1f3c;padding:16px;border-radius:8px;border:1px solid #1a2d4a;overflow-x:auto">{output if output.strip() else "(no output)"}</pre>
<p style="margin-top:16px"><a href="/uploads/" style="color:#00b4d8">Back to Uploads</a></p>
</body></html>'''
    except Exception as e:
        return f"Execution error: {e}", 500

# ──── Download uploaded files ────
@app.route("/uploads/<path:filename>")
def download_upload(filename):
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
    return "User-agent: *\nDisallow: /admin\nDisallow: /page?name=maintenance\nDisallow: /page?name=.\nDisallow: /api/v1/\n", 200, {"Content-Type": "text/plain"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
