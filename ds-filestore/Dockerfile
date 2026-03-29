FROM ubuntu:22.04

RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    openssh-server sudo curl wget netcat-openbsd procps python3 \
    vim net-tools iputils-ping cron sshpass vsftpd \
    && rm -rf /var/lib/apt/lists/*

# Backup agent user
RUN useradd -m -s /bin/bash backup_agent && \
    echo "backup_agent:Bk@gent_2026!" | chpasswd

# ──── PRIVESC: SUID python3 ────
RUN cp /usr/bin/python3 /usr/bin/python3-suid && chmod u+s /usr/bin/python3-suid

# ──── PRIVESC: writable cron ────
RUN mkdir -p /opt/scripts && \
    printf '#!/bin/bash\nfind /tmp -name "*.tmp" -delete 2>/dev/null\n' > /opt/scripts/cleanup.sh && \
    chmod 777 /opt/scripts/cleanup.sh && \
    echo "* * * * * root /opt/scripts/cleanup.sh" >> /etc/crontab

# ──── FTP SETUP ────
RUN mkdir -p /srv/ftp/shared /srv/ftp/confidential /srv/ftp/backups
COPY shares/ /srv/ftp/shared/
COPY shares/confidential/ /srv/ftp/confidential/

# .htpasswd with crackable bcrypt hash (dbadmin:Vault_Adm1n!)
RUN printf 'dbadmin:$2y$05$kQ6J8Z1pK5mW3vN4xR7qFuLjY2hT9sA0bC5dE8fG1iK3mO6pR9tV\n' > /srv/ftp/.htpasswd && \
    chmod 644 /srv/ftp/.htpasswd

# Decoy: old passwords
RUN printf '# EXPIRED CREDENTIALS — rotated 2025-12-01\ndb_admin: OldDBP@ss_2025 (CHANGED)\nvault_api: old-token-expired-123 (REVOKED)\n' > /srv/ftp/shared/passwords_OLD.txt

# FLAG
RUN printf 'DIGITAL SHIELD CORPORATION — CONFIDENTIAL\nIncident Report: Unauthorized Access Detected\nDate: 2026-03-15\n\nDuring routine log review, anomalous access patterns were detected\non the corporate network. Investigation is ongoing.\n\nFLAG{ds_5_filestore_data_breach}\n\nClassification: CONFIDENTIAL\n' > /srv/ftp/confidential/incident_report_2026.txt

# Vault access hints in bash_history
RUN printf 'psql -h 10.10.30.10 -U app_user -d shieldcorp\ncurl -k https://10.10.30.20:8443/api/v1/health\ncat /srv/ftp/.htpasswd\n' > /home/backup_agent/.bash_history && \
    chown backup_agent:backup_agent /home/backup_agent/.bash_history

# FTP config
RUN printf 'listen=YES\nlocal_enable=YES\nwrite_enable=YES\nlocal_umask=022\nchroot_local_user=NO\nallow_writeable_chroot=YES\nlocal_root=/srv/ftp\npasv_enable=YES\npasv_min_port=30000\npasv_max_port=30100\n' > /etc/vsftpd.conf

RUN mkdir -p /run/sshd
COPY setup/sshd_config /etc/ssh/sshd_config
COPY setup/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 22 21
ENTRYPOINT ["/entrypoint.sh"]
