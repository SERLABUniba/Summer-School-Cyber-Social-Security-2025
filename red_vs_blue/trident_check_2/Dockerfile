FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    iputils-ping \
    curl \
    ca-certificates \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
COPY flag.txt .
COPY templates ./templates
COPY static ./static

RUN useradd -r -s /usr/sbin/nologin ctfuser && chown -R ctfuser:ctfuser /app
USER ctfuser

EXPOSE 5000

CMD ["python", "-m", "gunicorn", "--bind", "0.0.0.0:5000", "--workers", "1", "app:app"]