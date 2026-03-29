FROM python:3.11-slim

RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    curl wget netcat-openbsd openssh-client sudo cron procps \
    vim net-tools iputils-ping nmap sshpass \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir flask requests

RUN useradd -m -s /bin/bash webuser

# ──── PRIVESC: SUID find ────
RUN cp /usr/bin/find /usr/bin/find-suid && chmod u+s /usr/bin/find-suid

# ──── PRIVESC: writable cron ────
RUN mkdir -p /opt/scripts && \
    printf '#!/bin/bash\ndate >> /var/log/health.log\n' > /opt/scripts/healthcheck.sh && \
    chmod 777 /opt/scripts/healthcheck.sh && \
    echo "* * * * * root /opt/scripts/healthcheck.sh" >> /etc/crontab

# ──── HIDDEN FLAG ────
RUN mkdir -p /var/www/maintenance && \
    echo "FLAG{ds_1_wordpress_initial_foothold}" > /var/www/maintenance/.maintenance_log && \
    chmod 644 /var/www/maintenance/.maintenance_log

# ──── DECOY: fake DB creds that don't work ────
RUN printf 'DB_HOST=10.10.30.10\nDB_USER=root\nDB_PASS=W0ntWork_Decoy!\nDB_NAME=production\n' > /var/www/.env

COPY . /app
WORKDIR /app
RUN mkdir -p /app/uploads && chmod 777 /app/uploads
RUN chown -R webuser:webuser /app

COPY setup/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 5000
ENTRYPOINT ["/entrypoint.sh"]
