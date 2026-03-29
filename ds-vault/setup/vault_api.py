from flask import Flask, request, jsonify
import json
import os
import ssl

app = Flask(__name__)
API_TOKEN = "dsc-vault-tk-8f3a2b9c7d1e4056"

with open("/opt/vault/secrets.json") as f:
    vault = json.load(f)

@app.route("/")
def index():
    return "<h2>DS Vault API</h2><p>Authenticate with Authorization: Bearer &lt;token&gt;</p>"

@app.route("/api/v1/health")
def health():
    return jsonify({"status": "ok", "version": "2.1.0", "secrets_count": len(vault["secrets"])})

@app.route("/api/v1/secrets")
def get_secrets():
    auth = request.headers.get("Authorization", "")
    if auth != f"Bearer {API_TOKEN}":
        return jsonify({"error": "unauthorized — valid bearer token required"}), 401
    return jsonify(vault)

# ──── VULN: Path traversal in backup endpoint ────
@app.route("/api/v1/backup")
def backup():
    auth = request.headers.get("Authorization", "")
    if auth != f"Bearer {API_TOKEN}":
        return jsonify({"error": "unauthorized"}), 401
    path = request.args.get("path", "/opt/vault/secrets.json")
    # VULNERABLE: no sanitization
    try:
        with open(path, "r") as f:
            return f.read(), 200, {"Content-Type": "text/plain"}
    except:
        return jsonify({"error": "file not found"}), 404

# Decoy endpoint
@app.route("/api/v1/admin")
def admin():
    return jsonify({"message": "Admin API — Coming Soon", "version": "2.1.0"})

if __name__ == "__main__":
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ctx.load_cert_chain("/opt/vault.crt", "/opt/vault.key")
    app.run(host="0.0.0.0", port=8443, ssl_context=ctx)
