# Deploying MyPocketLawyer to Render

This guide will help you deploy your application to Render using Docker.

## Prerequisites
1.  **GitHub Account**: You must push this code to a GitHub repository.
2.  **Render Account**: Sign up at [render.com](https://render.com).

## Step 1: Push to GitHub
If you haven't already:
1.  Create a new repository on GitHub.
2.  Push your code:
    ```bash
    git init
    git add .
    git commit -m "Initial commit"
    git branch -M main
    git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
    git push -u origin main
    ```

## Step 2: Create New Web Service on Render
1.  Log in to the [Render Dashboard](https://dashboard.render.com/).
2.  Click **New +** -> **Web Service**.
3.  Connect your GitHub repository.
4.  Give it a name (e.g., `mypocketlawyer`).
5.  **Runtime**: Select **Docker**.
6.  **Instance Type**: Free (or Starter if you need more RAM).

## Step 3: Environment Variables
Scroll down to "Environment Variables" and add:
-   **Key**: `GEMINI_API_KEY`
-   **Value**: `AIzaSy...` (Paste your actual key here)

## Step 4: Persistent Disk (Crucial!)
Since we use a local database (`chroma_db`), we need a persistent disk so data isn't lost when the app restarts.
1.  Go to the **Disks** tab (or "Advanced" settings during creation).
2.  Click **Add Disk**.
3.  **Name**: `chroma_data`
4.  **Mount Path**: `/app/chroma_db`
5.  **Size**: 1 GB is enough for now.

## Step 5: Deploy
Click **Create Web Service**. Render will:
1.  Clone your repo.
2.  Build the Docker image (takes a few minutes).
3.  Start the app.

## Step 6: Ingest Data (One-time)
Once deployed, your cloud database starts empty. You need to run the ingestion script **inside** the cloud server.
1.  Go to the **Shell** tab in your Render dashboard for this service.
2.  Run this command in the cloud shell:
    ```bash
    python backend/ingest.py
    ```
3.  Wait for it to finish.

**Done!** Your app is live.
