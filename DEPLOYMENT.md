# 🚀 Deployment Guide — CodeAgent AI

This guide walks you through deploying your AI coding agent to **Render** (free tier).

---

## 📋 Prerequisites

Before deploying, make sure you have:

1. **GitHub Account** — to push your code
2. **Render Account** — sign up at [render.com](https://render.com) (free)
3. **API Keys Ready**:
   - `GEMINI_API_KEY` — your Google Gemini API key
   - `GITHUB_TOKEN` — your GitHub personal access token

---

## 🔧 Step 1: Push Your Code to GitHub

If you haven't already, initialize a git repo and push to GitHub:

```bash
git init
git add .
git commit -m "Initial commit - CodeAgent AI"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

Replace `YOUR_USERNAME` and `YOUR_REPO` with your actual GitHub username and repository name.

---

## 🌐 Step 2: Deploy on Render

### 2.1 Create a New Web Service

1. Go to [render.com](https://render.com) and log in
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub account if you haven't already
4. Select your repository from the list

### 2.2 Configure the Service

Render will auto-detect the `render.yaml` file. If not, use these settings:

- **Name**: `codeagent-ai` (or any name you prefer)
- **Environment**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 300 server:app`
- **Plan**: `Free`

### 2.3 Add Environment Variables

In the Render dashboard, go to **Environment** tab and add:

| Key | Value |
|-----|-------|
| `GEMINI_API_KEY` | Your Gemini API key |
| `GITHUB_TOKEN` | Your GitHub personal access token |
| `PYTHON_VERSION` | `3.11.0` |

Click **"Save Changes"**

### 2.4 Deploy

Click **"Create Web Service"** — Render will:
- Clone your repo
- Install dependencies
- Start the server

This takes 3-5 minutes. Watch the logs for any errors.

---

## ✅ Step 3: Test Your Deployment

Once deployed, Render gives you a URL like:

```
https://codeagent-ai.onrender.com
```

Open it in your browser — you should see the CodeAgent AI interface.

Test it:
1. Enter a GitHub repo URL
2. Add a task (e.g., "Add a README file")
3. Click **Run Agent**

---

## 🛠️ Troubleshooting

### Build Fails

- Check the **Logs** tab in Render dashboard
- Common issues:
  - Missing dependencies → verify `requirements.txt`
  - Python version mismatch → ensure `runtime.txt` has `python-3.11.0`

### App Crashes on Startup

- Check environment variables are set correctly
- Look for errors in the **Logs** tab

### Memory/Vectorstore Not Persisting

Render's free tier uses **ephemeral storage** — files reset on each deploy. For persistent storage:
- Upgrade to a paid plan with disk storage
- Or use external storage (AWS S3, Google Cloud Storage)

### Timeout Errors

If tasks take too long:
- Increase `--timeout` in `Procfile` (currently 300 seconds)
- Or upgrade to a paid plan with more resources

---

## 🔄 Updating Your Deployment

After making code changes:

```bash
git add .
git commit -m "Your update message"
git push origin main
```

Render auto-deploys on every push to `main` branch.

---

## 💡 Tips

- **Free Tier Limitations**: 
  - App sleeps after 15 min of inactivity (first request takes ~30s to wake)
  - 750 hours/month free
  - Ephemeral storage (resets on deploy)

- **Logs**: Always check Render logs if something breaks

- **Custom Domain**: You can add a custom domain in Render settings (paid plans)

---

## 🎉 You're Live!

Your AI coding agent is now deployed and accessible worldwide. Share the URL and let others use it!

For questions or issues, check the Render docs: https://render.com/docs
