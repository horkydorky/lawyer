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

# Install Python packages with optimizations for limited resources
# Install torch CPU-only version first (smaller, faster)
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

# Install remaining requirements
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ ./backend/
COPY config/ ./config/
# Copy processed data for ingestion
COPY processeddata/ ./processeddata/
# Copy ingestion script
COPY backend/ingest.py ./backend/ingest.py

# Copy startup script
COPY start.sh ./start.sh
RUN chmod +x ./start.sh

# Copy built frontend assets from Stage 1
# backend/main.py expects frontend/dist to be at ../frontend/dist relative to backend/main.py
# So we copy to /app/frontend/dist
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Expose port
EXPOSE 8000

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

# Run the application using startup script
CMD ["./start.sh"]
