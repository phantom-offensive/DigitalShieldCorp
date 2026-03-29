from flask import Flask, request, render_template, session, redirect, jsonify
import hashlib
import requests as req

app = Flask(__name__)
app.secret_key = "ds-webmail-s3ss10n-k3y"

USERS = {
    "j.reynolds": hashlib.sha256(b"Summer2026!").hexdigest(),
    "m.chen": hashlib.sha256(b"DevOps2026!").hexdigest(),
    "a.kowalski": hashlib.sha256(b"SysAdmin2026!").hexdigest(),
}

EMAILS = {
    "j.reynolds": [
        {
            "id": 1, "from": "it-support@digitalshield.local", "subject": "VPN & Jumphost Access",
            "date": "Mar 25, 2026",
            "body": """Hi James,

Your VPN and SSH access has been provisioned.

SSH Access:
  Host: ds-jumphost (10.10.10.40 from DMZ)
  Username: j.reynolds
  Password: Same as your email password

Please change your jumphost password at your earliest convenience.

Best,
IT Support Team"""
        },
        {
            "id": 2, "from": "a.kowalski@digitalshield.local", "subject": "RE: Redis Cache Issue",
            "date": "Mar 22, 2026",
            "body": """James,

I looked into the Redis issue you reported. The developer portal (ds-devportal, 10.10.10.30) is running Redis on port 6379 WITHOUT authentication. I've flagged this to Michelle but she says it's "by design for performance."

The Redis instance caches session tokens and some repo data. Anyone on the DMZ can connect to it directly with redis-cli. This is a serious misconfiguration.

I've added it to the risk register but no ETA on a fix.

Adrian Kowalski
Systems Administrator"""
        },
        {
            "id": 3, "from": "d.okafor@digitalshield.local", "subject": "Q1 Security Review Action Items",
            "date": "Mar 18, 2026",
            "body": """Team,

Action items from the Q1 review:

1. Rotate all service account credentials (OVERDUE)
2. Patch the monitoring dashboard — default creds still active
3. Move backup credentials out of config files on the jumphost
4. The file server backup creds are stored in the IT shared drive on the filestore
5. Review database access — the read-only monitor account shouldn't exist

Also attaching the latest incident report for reference.

FLAG{ds_2_corporate_email_intelligence}

Dayo Okafor, CTO"""
        },
        {
            "id": 4, "from": "noreply@digitalshield.local", "subject": "Meeting: Infrastructure Migration",
            "date": "Mar 15, 2026",
            "body": """Reminder: Infrastructure migration meeting tomorrow at 2 PM.

Agenda:
- Database migration to restricted network (COMPLETED)
- Vault API deployment status (COMPLETED - running on 10.10.30.20:8443)
- Monitoring system upgrade (PENDING)

Note: The test server at 10.10.20.99 has been decommissioned. Please do not attempt to connect to it.

-- Automated Notification"""
        },
    ],
}

# ──── VULN: SSRF via link checker ────
@app.route("/check-link", methods=["POST"])
def check_link():
    if "user" not in session:
        return jsonify({"error": "unauthorized"}), 401
    url = request.form.get("url", "")
    try:
        r = req.get(url, timeout=5, verify=False)
        return jsonify({"status": r.status_code, "length": len(r.text), "preview": r.text[:500]})
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route("/", methods=["GET", "POST"])
def login():
    if "user" in session:
        return redirect("/inbox")
    error = ""
    if request.method == "POST":
        user = request.form.get("username", "")
        pwd = request.form.get("password", "")
        if user in USERS and USERS[user] == hashlib.sha256(pwd.encode()).hexdigest():
            session["user"] = user
            return redirect("/inbox")
        error = "Invalid username or password"
    return render_template("login.html", error=error)

@app.route("/inbox")
def inbox():
    if "user" not in session:
        return redirect("/")
    emails = EMAILS.get(session["user"], [])
    return render_template("inbox.html", user=session["user"], emails=emails)

@app.route("/email/<int:eid>")
def view_email(eid):
    if "user" not in session:
        return redirect("/")
    emails = EMAILS.get(session["user"], [])
    email = next((e for e in emails if e["id"] == eid), None)
    if not email:
        return "Email not found", 404
    return render_template("email.html", user=session["user"], email=email)

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
