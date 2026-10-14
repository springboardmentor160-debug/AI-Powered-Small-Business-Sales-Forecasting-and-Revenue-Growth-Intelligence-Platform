# MarketMind AI — Backend Dockerfile
FROM python:3.13-slim

# Prevent Python from writing .pyc files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

WORKDIR /app

# Install system dependencies needed for compiling numerical/C extensions (e.g. cmdstanpy, gcc, g++)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements and install dependencies
COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /app/backend/requirements.txt

# Copy backend code, data, reports, and db initialization directories
COPY backend/ /app/backend/
COPY data/ /app/data/
COPY db/ /app/db/
COPY reports/ /app/reports/

# Create necessary persistent directories if not present
RUN mkdir -p /app/db /app/reports /app/data/processed /app/data/test_fixtures

# Health check endpoint
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000

# Start FastAPI application with production Uvicorn server
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
