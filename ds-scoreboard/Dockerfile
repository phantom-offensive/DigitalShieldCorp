FROM python:3.11-slim
RUN pip install --no-cache-dir flask
COPY . /app
WORKDIR /app
EXPOSE 5000
CMD ["python3", "server.py"]
