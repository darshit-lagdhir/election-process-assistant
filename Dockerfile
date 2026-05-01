# Production Dockerfile for Election Process Assistant
FROM python:3.11-slim as builder

WORKDIR /app

# Install system-level build tools
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Runtime Stage
FROM python:3.11-slim

WORKDIR /app

# Environmental Hardening
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/root/.local/bin:$PATH"

# Copy dependencies from builder
COPY --from=builder /root/.local /root/.local
COPY . .

# Metadata labels
LABEL project="Election Process Assistant"
LABEL version="6.0.0"
LABEL type="backend"

EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:8000/api/health || exit 1

# Start application (single worker — scale via docker-compose replicas)
CMD ["python", "backend/main.py"]
