FROM python:3.14-slim AS deps

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libc6-dev && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir --prefix=/install aio-pika==9.5.8 asyncpg==0.30.0

FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY --from=deps /install /usr/local

COPY main.py .

CMD ["python", "-u", "main.py"]
