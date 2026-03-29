#!/bin/bash
# Start SSH
/usr/sbin/sshd

# Find PostgreSQL version
PG_VER=$(ls /usr/lib/postgresql/ | head -1)

# Configure for remote access before starting
PG_HBA="/etc/postgresql/$PG_VER/main/pg_hba.conf"
PG_CONF="/etc/postgresql/$PG_VER/main/postgresql.conf"

if [ -f "$PG_HBA" ]; then
    echo "host all all 0.0.0.0/0 md5" >> "$PG_HBA"
    echo "host all all ::/0 md5" >> "$PG_HBA"
fi

if [ -f "$PG_CONF" ]; then
    sed -i "s/#listen_addresses.*/listen_addresses = '*'/" "$PG_CONF"
fi

# Start PostgreSQL
su - postgres -c "pg_ctlcluster $PG_VER main start"

# Wait for it to be ready
for i in $(seq 1 10); do
    su - postgres -c "pg_isready" && break
    sleep 1
done

# Run init SQL
su - postgres -c "psql -f /docker-entrypoint-initdb.d/init.sql" 2>/dev/null

# Keep running
tail -f /dev/null
