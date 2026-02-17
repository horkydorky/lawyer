#!/bin/bash
# Startup script for Render free tier
# This will ingest data on every startup since we don't have persistent storage

echo "🚀 Starting MyPocketLawyer..."

# Check if chroma_db exists and has data
if [ ! -d "/app/chroma_db" ] || [ -z "$(ls -A /app/chroma_db)" ]; then
    echo "📚 ChromaDB not found or empty. Running data ingestion..."
    python backend/ingest.py
    echo "✅ Data ingestion complete!"
else
    echo "✅ ChromaDB found, skipping ingestion."
fi

# Start the FastAPI application
echo "🌐 Starting FastAPI server..."
uvicorn backend.main:app --host 0.0.0.0 --port 8000
