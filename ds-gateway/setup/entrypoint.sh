#!/bin/bash
service cron start
su - webuser -c "cd /app && python3 server.py"
