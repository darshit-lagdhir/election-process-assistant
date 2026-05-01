# --- MULTI-STAGE DOCKER BUILD ---

# Stage 1: Build Stage
FROM python:3.11-slim as builder

WORKDIR /app

# Security: Install only essential build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: Production Image
FROM python:3.11-slim

WORKDIR /app

# Security: Non-root execution context
RUN groupadd -r civi && useradd -r -g civi civi
USER civi

# Copy installed packages from builder
COPY --from=builder /root/.local /home/civi/.local
ENV PATH=/home/civi/.local/bin:$PATH

# Copy Assets
COPY backend/ ./backend/
COPY data/ ./data/
COPY frontend/ ./frontend/

# Environment Configuration
ENV GOOGLE_API_KEY=""
ENV PORT=8000

# Network Configuration
EXPOSE 8000

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
