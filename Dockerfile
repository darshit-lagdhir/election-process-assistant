# Phase 1: Build the Hadronic Core
FROM python:3.11-slim as backend

WORKDIR /app
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .
COPY data/ ../data/

# Phase 2: Radiant Frontend
# Since we use vanilla HTML/JS, we can serve it via the backend or a lean nginx image.
# For simplicity and speed, we serve it via FastAPI.

EXPOSE 8000

CMD ["python", "main.py"]
