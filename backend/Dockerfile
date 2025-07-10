FROM python:3.11-slim AS builder

WORKDIR /app

# Install build dependencies terlebih dahulu
RUN apt-get update && \
    apt-get install -y gcc g++ make && \
    rm -rf /var/lib/apt/lists/*

# Salin requirements.txt lebih awal agar cache pip install tetap optimal
COPY requirements.txt .

# Install dependencies
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Tahap akhir, image lebih kecil
FROM python:3.11-slim

WORKDIR /app

# Copy hasil instalasi dependencies dari builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy source code (hanya file yang perlu, agar cache tetap optimal)
COPY *.py ./
COPY utils/ ./utils/
COPY prompts/ ./prompts/
# COPY modules/ ./modules/

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]