FROM python:3.11-slim

RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    curl procps nmap && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir flask

RUN mkdir -p /opt/monitoring && \
    echo "FLAG{ds_6_monitoring_system_owned}" > /opt/monitoring/.flag_config

COPY . /app
WORKDIR /app
EXPOSE 8080
CMD ["python3", "server.py"]
