import redis
import json

r = redis.Redis(host="127.0.0.1", port=6379)

# Admin session token (can be stolen to hijack admin session)
r.set("session:admin_token_a8f3b2c1", json.dumps({
    "user": "m.chen", "role": "admin", "login_time": "2026-03-28T08:00:00"
}))

# Cached deployment config (contains SSH creds for jumphost)
r.set("deploy:config", json.dumps({
    "jumphost": {"host": "10.10.10.40", "user": "svc_deploy", "password": "D3pl0y_2026!"},
    "deploy_key": "/opt/deploy/.ssh/id_rsa",
    "targets": ["10.10.20.10", "10.10.20.20", "10.10.20.30"]
}))

# Cached git repo data
r.set("repo:deploy-scripts:latest_commit", json.dumps({
    "hash": "a7f3b2c1", "author": "m.chen", "message": "Update deploy targets",
    "files": ["deploy.sh", "rollback.sh", "config.yml"]
}))

r.set("repo:deploy-scripts:deleted_commit", json.dumps({
    "hash": "e4d2f1a0", "author": "m.chen", "message": "FLAG{ds_3_redis_session_hijack} — Remove hardcoded credentials",
    "files": ["config.yml.bak"]
}))

# Decoy: fake expired credentials
r.set("cache:old_passwords", json.dumps({
    "note": "EXPIRED — rotated 2025-12-01",
    "db_admin": "OldP@ss_2025!", "vault": "V@ult_Old!"
}))

print("Redis seeded successfully")
