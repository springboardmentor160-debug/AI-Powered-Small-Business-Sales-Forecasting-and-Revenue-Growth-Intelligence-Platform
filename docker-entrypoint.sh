#!/bin/sh
set -e

echo "Creating database tables (if needed)..."
python -m backend.init_db

echo "Seeding admin account (if configured)..."
python -m backend.seed_admin

echo "Starting MarketMind AI API on port ${PORT:-8000}..."
exec uvicorn backend.main:app --host 0.0.0.0 --port "${PORT:-8000}"
