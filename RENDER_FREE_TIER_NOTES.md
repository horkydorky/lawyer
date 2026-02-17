# Render Free Tier Deployment Notes

## Important Limitations

Since you're using Render's free tier, be aware of these limitations:

### 1. No Persistent Storage
- The ChromaDB vector database is stored in memory/temporary storage
- **Data is lost when the service restarts** (after 15 minutes of inactivity)
- Solution: The app automatically re-ingests data on every startup

### 2. Cold Starts
- Free tier services spin down after 15 minutes of inactivity
- First request after spin-down will be slow (30-60 seconds) as it:
  - Spins up the container
  - Runs data ingestion (processes all JSON files)
  - Starts the FastAPI server

### 3. Build Time
- Initial deployment takes 5-10 minutes
- Includes building frontend and backend
- Downloads embedding model (BAAI/bge-large-en-v1.5)

## What Happens on Startup

The `start.sh` script automatically:
1. Checks if ChromaDB exists
2. If not, runs `python backend/ingest.py`
3. Processes all files in `processeddata/` folder
4. Creates embeddings using HuggingFace model (CPU)
5. Starts the FastAPI server

## Performance Expectations

- **First request after restart**: 30-60 seconds (includes ingestion)
- **Subsequent requests**: 2-5 seconds (normal response time)
- **Inactivity timeout**: 15 minutes (then spins down)

## Upgrade Path

If you need better performance:
- Upgrade to Starter plan ($7/month)
- Adds persistent disk storage
- No spin-down on inactivity
- Faster cold starts (no re-ingestion needed)

## Current Setup

✅ Auto-ingestion on startup
✅ All legal documents included in Docker image
✅ Local embedding model (no external API needed for embeddings)
✅ Gemini API only used for generation (not embeddings)
