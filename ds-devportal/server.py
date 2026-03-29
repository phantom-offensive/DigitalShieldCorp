from flask import Flask, request, render_template, session, redirect, jsonify
import redis
import json
import os
import hashlib

app = Flask(__name__)
app.secret_key = "ds-devportal-k3y"
r = redis.Redis(host="127.0.0.1", port=6379, decode_responses=True)

USERS = {
    "guest": hashlib.sha256(b"guest").hexdigest(),
}

@app.route("/", methods=["GET", "POST"])
def login():
    if "user" in session:
        return redirect("/dashboard")
    error = ""
    if request.method == "POST":
        action = request.form.get("action", "login")
        user = request.form.get("username", "")
        pwd = request.form.get("password", "")
        if action == "register" and user and pwd:
            USERS[user] = hashlib.sha256(pwd.encode()).hexdigest()
            session["user"] = user
            session["role"] = "contractor"
            return redirect("/dashboard")
        elif user in USERS and USERS[user] == hashlib.sha256(pwd.encode()).hexdigest():
            session["user"] = user
            session["role"] = "contractor"
            return redirect("/dashboard")
        else:
            error = "Invalid credentials"
    return render_template("login.html", error=error)

# ──── VULN: Session hijack via stolen admin token from Redis ────
@app.route("/dashboard")
def dashboard():
    # Check for admin token in cookie
    admin_token = request.cookies.get("ds_session")
    if admin_token:
        data = r.get(f"session:{admin_token}")
        if data:
            info = json.loads(data)
            if info.get("role") == "admin":
                session["user"] = info["user"]
                session["role"] = "admin"

    if "user" not in session:
        return redirect("/")
    is_admin = session.get("role") == "admin"
    return render_template("dashboard.html", user=session["user"], is_admin=is_admin)

# ──── Admin deployment page (shows SSH creds) ────
@app.route("/deploy")
def deploy():
    if session.get("role") != "admin":
        return "Access denied — admin only", 403
    config = r.get("deploy:config")
    return render_template("deploy.html", config=json.loads(config) if config else {})

# ──── VULN: Path traversal in repo file viewer ────
@app.route("/repo/view")
def repo_view():
    if "user" not in session:
        return redirect("/")
    filepath = request.args.get("file", "README.md")
    # VULNERABLE: no path sanitization
    try:
        full_path = os.path.join("/app/repos", filepath)
        with open(full_path, "r") as f:
            content = f.read()
        return jsonify({"file": filepath, "content": content})
    except:
        return jsonify({"error": "File not found"}), 404

# ──── Git log page (shows deleted commits from Redis) ────
@app.route("/repo/log")
def repo_log():
    if "user" not in session:
        return redirect("/")
    commits = []
    for key in r.keys("repo:deploy-scripts:*"):
        data = r.get(key)
        if data:
            commits.append(json.loads(data))
    return render_template("repo_log.html", commits=commits)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    os.makedirs("/app/repos", exist_ok=True)
    with open("/app/repos/README.md", "w") as f:
        f.write("# Deploy Scripts\n\nAutomated deployment scripts for Digital Shield infrastructure.\n")
    app.run(host="0.0.0.0", port=3000)
