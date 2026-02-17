#!/bin/bash
# Startup script for Render free tier

echo "🚀 Starting MyPocketLawyer..."

# Check if chroma_db exists and has data
if [ -d "/app/chroma_db" ] && [ -n "$(ls -A /app/chroma_db 2>/dev/null)" ]; then
    echo "✅ ChromaDB found with data, skipping ingestion."
else
    echo "⚠️  ChromaDB not found. This will cause issues on free tier due to memory limits."
    echo "📚 Attempting data ingestion (may fail due to 512MB RAM limit)..."
    python backend/ingest.py || echo "❌ Ingestion failed - not enough memory"
fi

# Start the FastAPI application
echo "🌐 Starting FastAPI server..."
uvicorn backend.main:app --host 0.0.0.0 --port 8000
