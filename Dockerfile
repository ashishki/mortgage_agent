# Dockerfile
# Multi-stage build for a slim, production-ready image

# Stage 1: build dependencies
FROM python:3.12-slim AS builder
WORKDIR /app

# Install build essentials (including Tesseract OCR)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    tesseract-ocr \
 && rm -rf /var/lib/apt/lists/*

# Copy Python dependency manifest
COPY requirements.txt .

# Install Python deps into a dedicated directory
RUN pip install --upgrade pip \
    && pip install --no-cache-dir --prefix=/install -r requirements.txt

# Stage 2: runtime
FROM python:3.12-slim
WORKDIR /app

# Copy installed Python packages from builder
COPY --from=builder /install /usr/local

# Copy application code
COPY . .

# Ensure Python can find the installed packages
ENV PYTHONPATH=/usr/local/lib/python3.12/site-packages:$PYTHONPATH

# Default entrypoint
ENTRYPOINT ["python", "main.py"]
