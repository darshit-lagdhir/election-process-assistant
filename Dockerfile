# Hardened Production Dockerfile for Hadron Core
FROM python:3.12-slim as builder

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
FROM python:3.12-slim

WORKDIR /app

# Environmental Hardening
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/root/.local/bin:$PATH"

# Copy dependencies from builder
COPY --from=builder /root/.local /root/.local
COPY . .

# Metadata labels
LABEL project="Hadron Core Election Assistant"
LABEL version="9.0.0-AGNOSTIC"
LABEL type="sovereign-intelligence"

EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:8000/kernel/health || exit 1

# Start application via Master Ignition
CMD ["python", "start.py"]
