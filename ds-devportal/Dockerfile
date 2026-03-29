FROM python:3.11-slim

RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    redis-server curl procps && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir flask redis

COPY . /app
WORKDIR /app

COPY setup/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 3000 6379
ENTRYPOINT ["/entrypoint.sh"]
