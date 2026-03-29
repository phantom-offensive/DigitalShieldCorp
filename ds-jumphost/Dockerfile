FROM ubuntu:22.04

RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    openssh-server sudo curl wget netcat-openbsd procps python3 \
    vim net-tools iputils-ping nmap cron sshpass tcpdump rsync \
    && rm -rf /var/lib/apt/lists/*

# User 1: j.reynolds (email password reuse)
RUN useradd -m -s /bin/bash j.reynolds && \
    echo "j.reynolds:Summer2026!" | chpasswd

# User 2: svc_deploy (from devportal)
RUN useradd -m -s /bin/bash svc_deploy && \
    echo "svc_deploy:D3pl0y_2026!" | chpasswd

# ──── PRIVESC: sudo tcpdump (GTFOBins) ────
RUN echo "j.reynolds ALL=(root) NOPASSWD: /usr/bin/tcpdump" >> /etc/sudoers

# ──── PRIVESC: sudo rsync (GTFOBins) ────
RUN echo "svc_deploy ALL=(root) NOPASSWD: /usr/bin/rsync" >> /etc/sudoers

# ──── HIDDEN CONFIG: filestore creds ────
RUN mkdir -p /opt/.deploy && \
    printf 'deploy:\n  filestore:\n    host: 10.10.20.20\n    user: backup_agent\n    pass: Bk@gent_2026!\n    protocol: ftp\n  monitoring:\n    host: 10.10.20.30\n    port: 8080\n' > /opt/.deploy/config.yml && \
    chmod 644 /opt/.deploy/config.yml

# Flag (readable only by root)
RUN echo "FLAG{ds_4_jumphost_privesc_complete}" > /opt/.deploy/.flag && \
    chmod 600 /opt/.deploy/.flag

# Monitoring creds hint in crontab
RUN echo "# monitoring health check - nagios:Monitor2026! at 10.10.20.30:8080" >> /etc/crontab

# Decoy: maintenance contacts (no passwords)
RUN printf 'Maintenance Contacts:\n  Network: John Smith - ext 4521\n  Database: Sarah Lee - ext 4533\n  Security: Mike Torres - ext 4540\n' > /home/j.reynolds/maintenance_contacts.txt && \
    chown j.reynolds:j.reynolds /home/j.reynolds/maintenance_contacts.txt

# known_hosts hints
RUN mkdir -p /home/svc_deploy/.ssh && \
    printf '10.10.20.10 ssh-ed25519 AAAAC3NzaC1...\n10.10.20.20 ssh-ed25519 AAAAC3NzaC1...\n10.10.20.30 ssh-ed25519 AAAAC3NzaC1...\n' > /home/svc_deploy/.ssh/known_hosts && \
    chown -R svc_deploy:svc_deploy /home/svc_deploy/.ssh

# bash_history
RUN printf 'ssh backup_agent@10.10.20.20\ncurl http://10.10.20.30:8080/status\nnmap -sT -Pn 10.10.20.0/24 -p 22,80,8080,21\n' > /home/svc_deploy/.bash_history && \
    chown svc_deploy:svc_deploy /home/svc_deploy/.bash_history

RUN mkdir -p /run/sshd
COPY setup/sshd_config /etc/ssh/sshd_config

EXPOSE 22
CMD ["/usr/sbin/sshd", "-D"]
