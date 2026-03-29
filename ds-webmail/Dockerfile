FROM python:3.11-slim

RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    curl wget procps && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir flask requests

COPY . /app
WORKDIR /app
EXPOSE 8080
CMD ["python3", "server.py"]
