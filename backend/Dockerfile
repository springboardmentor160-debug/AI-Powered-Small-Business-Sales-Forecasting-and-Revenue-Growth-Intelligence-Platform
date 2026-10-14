# Build context = repo ROOT (main.py reads ../ml/outputs and ../datasets/processed)
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
WORKDIR /app

COPY requirements-api.txt .
RUN pip install --no-cache-dir -r requirements-api.txt

COPY backend ./backend
COPY ml/outputs ./ml/outputs
COPY datasets/processed ./datasets/processed

WORKDIR /app/backend
EXPOSE 8000

# Render/Railway inject $PORT; locally it falls back to 8000
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]