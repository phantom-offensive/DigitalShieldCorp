FROM python:3.11-slim

RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    openssh-server sudo curl procps vim openssl \
    && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir flask

# Vault admin user
RUN useradd -m -s /bin/bash vaultadmin && \
    echo "vaultadmin:V@ultAdm1n_2026!" | chpasswd

# ──── PRIVESC: sudo openssl (GTFOBins — can read files) ────
RUN echo "vaultadmin ALL=(root) NOPASSWD: /usr/bin/openssl" >> /etc/sudoers

# Generate self-signed cert for HTTPS
RUN openssl req -x509 -newkey rsa:2048 -keyout /opt/vault.key -out /opt/vault.crt \
    -days 365 -nodes -subj '/CN=ds-vault.digitalshield.local' 2>/dev/null

# Final flag (root only)
COPY setup/flag.txt /root/flag_final.txt
RUN chmod 600 /root/flag_final.txt

# Vault data
COPY setup/vault_data.json /opt/vault/secrets.json
COPY setup/vault_api.py /opt/vault/api.py

RUN mkdir -p /run/sshd
COPY setup/sshd_config /etc/ssh/sshd_config
COPY setup/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 22 8443
ENTRYPOINT ["/entrypoint.sh"]
