# Deploying MyPocketLawyer to Railway

Railway offers a more generous free tier ($5 free credit/month) with better resource limits than Render.

## Prerequisites
1. GitHub account with your code pushed
2. Railway account (sign up at https://railway.app)

## Deployment Steps

### Step 1: Sign Up for Railway
1. Go to https://railway.app
2. Click "Login" and sign in with GitHub
3. Authorize Railway to access your repositories

### Step 2: Create New Project
1. Click "New Project"
2. Select "Deploy from GitHub repo"
3. Choose your repository: `horkydorky/lawyer`
4. Railway will automatically detect the Dockerfile

### Step 3: Configure Environment Variables
1. Go to your project dashboard
2. Click on your service
3. Go to "Variables" tab
4. Add environment variable:
   - **Variable**: `GEMINI_API_KEY`
   - **Value**: (paste your Gemini API key)
5. Click "Add"

### Step 4: Configure Settings (Optional but Recommended)
1. Go to "Settings" tab
2. Under "Deploy":
   - **Start Command**: `./start.sh` (should be auto-detected)
   - **Dockerfile Path**: `Dockerfile` (should be auto-detected)
3. Under "Networking":
   - Railway will auto-generate a public URL
   - You can add a custom domain later if you want

### Step 5: Deploy
1. Railway will automatically start building and deploying
2. Watch the build logs in the "Deployments" tab
3. First deployment takes 5-10 minutes (building frontend + backend)
4. Once deployed, you'll see a green "Active" status

### Step 6: Access Your App
1. Go to "Settings" tab
2. Under "Networking", click "Generate Domain"
3. Your app will be available at: `https://your-app-name.up.railway.app`

### Step 7: Monitor Usage
1. Railway free tier includes $5 credit/month
2. Monitor usage in the "Usage" tab
3. Typical usage for this app: ~$3-4/month (well within free tier)

## Important Notes

### Free Tier Limits
- $5 free credit per month
- No execution time limits
- Better memory limits than Render (up to 8GB)
- 1GB disk storage included
- No forced sleep/spin-down

### Data Persistence
- Railway provides persistent volumes automatically
- Your ChromaDB data will persist across deployments
- No need to re-ingest data after restarts

### Cold Starts
- Railway keeps your app running (no cold starts on free tier)
- Much better performance than Render free tier

## Troubleshooting

### Build Fails
- Check build logs in "Deployments" tab
- Ensure all dependencies are in `requirements.txt`
- Verify Dockerfile is correct

### Out of Memory
- Railway free tier has generous memory limits
- If you still hit limits, check the "Metrics" tab
- Consider optimizing the embedding model loading

### App Not Responding
- Check "Logs" tab for runtime errors
- Verify `GEMINI_API_KEY` is set correctly
- Ensure port 8000 is exposed (Railway auto-detects this)

### Database Empty
- Check if `chroma_db/` folder was included in git
- If not, the app will auto-ingest on first startup
- Monitor logs to see ingestion progress

## Advantages Over Render Free Tier

✅ More memory (no 512MB limit)
✅ No forced sleep after inactivity
✅ Persistent storage included
✅ Better build performance
✅ Simpler configuration
✅ Better logging and monitoring
✅ $5/month free credit (enough for this app)

## Cost Estimate

Based on typical usage:
- **Compute**: ~$2-3/month
- **Storage**: Included in free tier
- **Network**: Minimal
- **Total**: ~$3-4/month (within $5 free credit)

## Next Steps After Deployment

1. Test your app at the Railway URL
2. Try sample queries to verify it works
3. Monitor usage in Railway dashboard
4. (Optional) Add custom domain in Settings
5. (Optional) Set up GitHub auto-deploy for continuous deployment

---

## Quick Command Reference

```bash
# Push changes to trigger new deployment
git add .
git commit -m "Update app"
git push origin main

# Railway will auto-deploy on push
```

## Support

- Railway Docs: https://docs.railway.app
- Railway Discord: https://discord.gg/railway
- Railway Status: https://status.railway.app
