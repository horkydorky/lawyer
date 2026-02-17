# MyPocketLawyer - Deployment Checklist

## ✅ Pre-Deployment Checklist

### 1. GitHub Setup
- [ ] Create new GitHub repository at https://github.com/new
- [ ] Note your GitHub username: `_______________`
- [ ] Note your repository name: `_______________`

### 2. Update Configuration Files

#### Update render.yaml
Replace this line in `render.yaml`:
```yaml
repo: https://github.com/YOUR_USERNAME/YOUR_REPO_NAME
```
With your actual GitHub URL:
```yaml
repo: https://github.com/YOUR_ACTUAL_USERNAME/YOUR_ACTUAL_REPO
```

### 3. Environment Variables to Set in Render
- `GEMINI_API_KEY` - Your Google Gemini API key (from .env file)

---

## 🚀 Deployment Steps

### Step 1: Push to GitHub
```bash
# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit - MyPocketLawyer RAG application"

# Set main branch
git branch -M main

# Add remote (replace with your actual URL)
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git

# Push to GitHub
git push -u origin main
```

### Step 2: Deploy on Render

#### Option A: Using render.yaml (Recommended)
1. Go to https://dashboard.render.com/
2. Click "New +" → "Blueprint"
3. Connect your GitHub repository
4. Render will detect `render.yaml` automatically
5. Add environment variable:
   - Key: `GEMINI_API_KEY`
   - Value: (paste your API key from .env file)
6. Click "Apply"

#### Option B: Manual Setup
1. Go to https://dashboard.render.com/
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Name**: `mypocketlawyer`
   - **Runtime**: Docker
   - **Branch**: main
   - **Instance Type**: Free (or Starter for better performance)
5. Add environment variable:
   - Key: `GEMINI_API_KEY`
   - Value: (paste your API key)
6. Add Disk (IMPORTANT for ChromaDB persistence):
   - Click "Add Disk"
   - **Name**: `chroma_data`
   - **Mount Path**: `/app/chroma_db`
   - **Size**: 1 GB
7. Click "Create Web Service"

### Step 3: Ingest Data (One-time setup)
After deployment completes:
1. Go to your service in Render Dashboard
2. Click "Shell" tab
3. Run:
   ```bash
   python backend/ingest.py
   ```
4. Wait for ingestion to complete (may take several minutes)

### Step 4: Test Your Deployment
1. Open your Render URL (e.g., `https://mypocketlawyer.onrender.com`)
2. Test with a query like: "What are the three organs of the Government under the Constitution of Nepal?"

---

## 🔧 Troubleshooting

### Build Fails
- Check that all dependencies are in `requirements.txt`
- Verify `Dockerfile` is correct
- Check Render build logs for specific errors

### Frontend Not Loading
- Ensure frontend build completed successfully
- Check that `frontend/dist` exists in the Docker image
- Verify static file mounting in `backend/main.py`

### Database Empty
- Make sure you ran `python backend/ingest.py` in the Render shell
- Verify the disk is mounted at `/app/chroma_db`
- Check that `processeddata/` folder has JSON files

### API Errors
- Verify `GEMINI_API_KEY` is set correctly in Render environment variables
- Check API key has proper permissions in Google AI Studio
- Review application logs in Render dashboard

---

## 📝 Important Notes

1. **Free Tier Limitations**: Render free tier spins down after 15 minutes of inactivity. First request after spin-down will be slow.

2. **Persistent Storage**: The disk mount at `/app/chroma_db` ensures your vector database persists across deployments.

3. **Environment Variables**: Never commit `.env` file to GitHub. Always set sensitive values in Render dashboard.

4. **Build Time**: Initial build may take 5-10 minutes as it builds both frontend and backend.

5. **Data Ingestion**: Only needs to be run once after initial deployment, or when you update legal documents.

---

## 🎯 Quick Reference

### Your Configuration
- GitHub Repo: `https://github.com/_______________/_______________`
- Render Service: `https://_______________.onrender.com`
- API Endpoint: `https://_______________.onrender.com/chat`

### Useful Commands
```bash
# Check deployment status
curl https://YOUR_APP.onrender.com/api/health

# Test chat endpoint
curl -X POST https://YOUR_APP.onrender.com/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the Constitution of Nepal?", "k": 8}'
```
