# 🚀 Quick Deploy Guide - MyPocketLawyer

## Prerequisites
- Git installed
- GitHub account
- Render account (sign up at https://render.com)
- Your GEMINI_API_KEY (from your .env file)

---

## 🎯 3-Step Deployment

### Step 1: Configure and Push to GitHub

```bash
# Run the setup script to update render.yaml
python setup_deployment.py

# Initialize git and commit
git init
git add .
git commit -m "Initial commit - MyPocketLawyer"
git branch -M main

# Add your GitHub remote (use the URL from setup script)
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git

# Push to GitHub
git push -u origin main
```

### Step 2: Deploy on Render

1. Go to https://dashboard.render.com/
2. Click **"New +"** → **"Blueprint"**
3. Connect your GitHub repository
4. Render will detect `render.yaml` automatically
5. Add environment variable:
   - **Key**: `GEMINI_API_KEY`
   - **Value**: (paste from your .env file)
6. Click **"Apply"**
7. Wait for build to complete (5-10 minutes)

### Step 3: Ingest Legal Documents

1. Once deployed, go to your service in Render Dashboard
2. Click the **"Shell"** tab
3. Run this command:
   ```bash
   python backend/ingest.py
   ```
4. Wait for completion (may take several minutes)

---

## ✅ Verify Deployment

Visit your app URL: `https://YOUR_APP_NAME.onrender.com`

Test the API:
```bash
curl https://YOUR_APP_NAME.onrender.com/api/health
```

---

## 📋 What Gets Deployed

- ✅ React frontend (built with Vite)
- ✅ FastAPI backend
- ✅ ChromaDB vector database (persistent disk)
- ✅ All legal documents ready for ingestion

---

## ⚠️ Important Notes

1. **Free Tier**: App spins down after 15 min of inactivity
2. **First Load**: May take 30-60 seconds after spin-down
3. **Data Persistence**: Disk mount ensures database survives restarts
4. **Security**: Never commit .env file to GitHub

---

## 🆘 Need Help?

Check `DEPLOYMENT_CHECKLIST.md` for detailed troubleshooting steps.
