# ==========================================
# Stage 1: Frontend Build
# ==========================================
FROM node:18-alpine AS frontend-builder
WORKDIR /app/frontend

# Copy frontend source
COPY frontend/package*.json ./
RUN npm install

COPY frontend/ .
# Build the React app (Vite)
RUN npm run build

# ==========================================
# Stage 2: Backend Runtime
# ==========================================
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for potential build tools or specific libs
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ ./backend/
COPY config/ ./config/
# Copy ingestion script if needed at runtime
COPY backend/ingest.py ./backend/ingest.py

# Copy built frontend assets from Stage 1
# backend/main.py expects frontend/dist to be at ../frontend/dist relative to backend/main.py
# So we copy to /app/frontend/dist
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Expose port
EXPOSE 8000

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

# Run the application
# We need to run from /app so that backend.main is importable
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
