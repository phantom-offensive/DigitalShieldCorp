FROM python:3.11-slim

RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    openssh-server sudo curl procps vim net-tools postgresql postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# DB admin user
RUN useradd -m -s /bin/bash dbadmin && \
    echo "dbadmin:Vault_Adm1n!" | chpasswd

# Sudo: pg_dump as root
RUN echo "dbadmin ALL=(root) NOPASSWD: /usr/bin/pg_dump, /usr/bin/psql" >> /etc/sudoers

# Flag (root only)
RUN echo "FLAG{ds_8_database_root_compromise}" > /root/.pgpass && \
    chmod 600 /root/.pgpass

RUN mkdir -p /run/sshd /run/postgresql && chown postgres:postgres /run/postgresql
COPY setup/sshd_config /etc/ssh/sshd_config
COPY setup/init.sql /docker-entrypoint-initdb.d/init.sql
COPY setup/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 22 5432
ENTRYPOINT ["/entrypoint.sh"]
