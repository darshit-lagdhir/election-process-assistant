# ELECTION PROCESS ASSISTANT: PRODUCTION DOCKERFILE
# ===============================================
# SECTOR ETA: THE PHYSICS OF CONTAINERIZED PURITY
# "A sovereign deployment is a clean deployment."

# --- STAGE 1: THE BUILD KERNEL ---
# We use a slim Debian base to compile dependencies and prepare the environment.
FROM python:3.12-slim-bookworm AS builder

# Prevent Python from writing .pyc files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system-level build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies into a temporary location
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# --- STAGE 2: THE PRODUCTION RADIANCE ---
# The final image is stripped of build tools, ensuring minimum attack surface.
FROM python:3.12-slim-bookworm

WORKDIR /app

# Copy only the installed packages from the builder stage
COPY --from=builder /install /usr/local

# Copy the application source code
COPY . .

# Set Systemic Environment Variables
ENV METABOLIC_PERIMETER_MB=10.0
ENV PORT=8080
ENV LOG_LEVEL=INFO

# Ensure data directory exists for forensic logs
RUN mkdir -p data

# Expose the API Ingress Port
EXPOSE 8080

# The Final Ignition: Execute the Hadron Core via Uvicorn
# We use 4 workers to maximize the multi-threaded potential of the cloud substrate.
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "4", "--log-level", "info"]
