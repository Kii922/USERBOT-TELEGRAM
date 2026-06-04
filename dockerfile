FROM python:3.12-slim

WORKDIR /app

# Install build tools (untuk tgcrypto)
RUN apt-get update && apt-get install -y --no-install-recommends gcc libc6-dev && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Volume untuk data persistent (session, database)
VOLUME /app/data

# Environment variables default
ENV DB_PATH=/app/data/promo_bot.db

CMD ["python", "bot.py"]
