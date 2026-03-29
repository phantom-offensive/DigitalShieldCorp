#!/bin/bash
# Start Redis WITHOUT authentication (intentional misconfiguration)
redis-server --daemonize yes --bind 0.0.0.0 --protected-mode no

# Seed Redis with session data
python3 /app/setup/seed_redis.py

# Start the web app
python3 /app/server.py
