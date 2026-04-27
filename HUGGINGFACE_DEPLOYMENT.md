# 🤗 Hugging Face Spaces Deployment Guide

Deploy your AI Coding Agent to Hugging Face Spaces in 10 minutes!

---

## 📋 Prerequisites

1. **Hugging Face Account** - Sign up at [huggingface.co](https://huggingface.co/join)
2. **API Keys Ready**:
   - `GEMINI_API_KEY`
   - `GITHUB_TOKEN`

---

## 🚀 Step-by-Step Deployment

### Step 1: Create a New Space

1. Go to [huggingface.co/new-space](https://huggingface.co/new-space)
2. Fill in:
   - **Space name**: `ai-coding-agent` (or your choice)
   - **License**: MIT
   - **Select SDK**: **Docker**
   - **Space hardware**: CPU basic (free)
   - **Visibility**: Public
3. Click **"Create Space"**

### Step 2: Prepare Dockerfile

Create a file named `Dockerfile` in your project root:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p data memory vectorstore

# Expose port
EXPOSE 7860

# Start command
CMD ["gunicorn", "--bind", "0.0.0.0:7860", "--workers", "2", "--timeout", "300", "server:app"]
```

### Step 3: Create README.md for Space

Create `README_SPACE.md`:

```markdown
---
title: AI Coding Agent
emoji: 🤖
colorFrom: purple
colorTo: blue
sdk: docker
pinned: false
---

# 🤖 AI Coding Agent

An intelligent coding assistant that automatically clones GitHub repos, understands codebases, and generates code changes.

## Features

- 🔍 **Smart Code Analysis** - Uses RAG to understand your codebase
- 💻 **Automated Coding** - Generates code based on natural language tasks
- 🚀 **GitHub Integration** - Automatically pushes changes
- 🧠 **Memory System** - Remembers previous tasks and context

## Tech Stack

- **LLM**: Google Gemini 2.5
- **Vector DB**: ChromaDB
- **Embeddings**: Sentence Transformers
- **Framework**: Flask + LangChain

## How to Use

1. Enter your GitHub repo URL
2. Add your GitHub token (optional if set in secrets)
3. Describe what you want to build
4. Watch the AI plan, code, and push changes!

## Built by [Your Name]

[GitHub](https://github.com/vaibhavv-web) | [LinkedIn](your-linkedin-url)
```

### Step 4: Push to Hugging Face

**Option A: Using Git (Recommended)**

```bash
# Add Hugging Face remote
git remote add hf https://huggingface.co/spaces/YOUR_USERNAME/ai-coding-agent

# Push to Hugging Face
git push hf main
```

**Option B: Using Web Interface**

1. Go to your Space's **"Files"** tab
2. Click **"Add file"** → **"Upload files"**
3. Upload all your project files (except `data/`, `vectorstore/`, `.env`)

### Step 5: Add Secrets (Environment Variables)

1. Go to your Space's **"Settings"** tab
2. Scroll to **"Repository secrets"**
3. Click **"New secret"** and add:

```
GEMINI_API_KEY = your_gemini_api_key_here
GITHUB_TOKEN = your_github_personal_access_token_here
```

### Step 6: Wait for Build

- Hugging Face will automatically build your Docker image
- Takes 5-10 minutes for first build
- Watch the build logs in the **"Logs"** tab

### Step 7: Test Your App

Once deployed, your app will be live at:
```
https://huggingface.co/spaces/YOUR_USERNAME/ai-coding-agent
```

---

## 🎯 Post-Deployment

### Update Your Resume

Add this project:

**AI Coding Agent** | [Live Demo](your-hf-space-url) | [GitHub](your-github-url)
- Developed an AI-powered coding assistant using Gemini 2.5, LangChain, and RAG
- Implemented vector-based code search with ChromaDB and sentence transformers
- Automated GitHub integration for code generation and deployment
- Deployed on Hugging Face Spaces with Docker containerization

### LinkedIn Post Template

```
🚀 Excited to share my latest project: AI Coding Agent!

An intelligent assistant that:
✅ Understands entire codebases using RAG
✅ Generates code from natural language
✅ Automatically pushes to GitHub

Built with:
🤖 Google Gemini 2.5
🔗 LangChain
📊 ChromaDB
🐍 Python + Flask

Try it live: [your-space-url]
Code: [your-github-url]

#AI #MachineLearning #GenAI #Python #LLM #OpenSource
```

### Add to LinkedIn Featured Section

1. Go to your LinkedIn profile
2. Click **"Add profile section"** → **"Featured"**
3. Add **"Media"** → Paste your Hugging Face Space URL
4. Add title: "AI Coding Agent - Live Demo"

---

## 🐛 Troubleshooting

### Build Fails

- Check **"Logs"** tab for errors
- Common issues:
  - Missing dependencies → Update `requirements.txt`
  - Port mismatch → Ensure using port 7860
  - Memory issues → Reduce model size or upgrade to paid tier

### App Crashes

- Check **"Logs"** tab for runtime errors
- Verify secrets are set correctly
- Test locally first: `docker build -t test . && docker run -p 7860:7860 test`

### Slow Performance

- Free tier has limited resources
- Consider upgrading to CPU/GPU tier
- Optimize model loading and caching

---

## 📊 Analytics

Track your Space's performance:
- Views and likes on Hugging Face
- GitHub stars and forks
- LinkedIn post engagement

---

## 🎉 You're Done!

Your AI Coding Agent is now live and ready to impress recruiters!

**Next Steps:**
1. Share on LinkedIn
2. Add to resume
3. Submit to AI newsletters/communities
4. Keep improving based on feedback

Good luck! 🚀
