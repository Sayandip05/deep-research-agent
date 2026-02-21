# 🚀 Quick Start Guide

Get your Deep Research Agent up and running in 5 minutes!

## Prerequisites

- Python 3.11 or higher
- pip (Python package manager)
- Docker (for Qdrant)

## Step 1: Setup Environment

```bash
# Navigate to the project
cd "C:\Users\sayan\AI ML\deep-research-agent"

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
# source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Step 2: Get FREE API Keys

### Required: Groq (LLM)
1. Go to [console.groq.com](https://console.groq.com)
2. Sign up (no credit card needed)
3. Create an API key
4. Copy the key

### Recommended: GitHub
1. Go to [github.com/settings/tokens](https://github.com/settings/tokens)
2. Click "Generate new token (classic)"
3. Select scopes: `public_repo`, `read:user`
4. Generate and copy token

## Step 3: Configure Environment

```bash
# Copy example environment file
copy .env.example .env  # Windows
# cp .env.example .env  # Mac/Linux

# Edit .env file and add your keys
```

**Minimum required in `.env`:**
```ini
GROQ_API_KEY=your_groq_key_here
GITHUB_TOKEN=your_github_token_here
```

## Step 4: Start Services & Test

```bash
# Start Qdrant (vector cache)
docker-compose up -d

# Verify the system
python test_system.py
```

You should see: `🎉 ALL CORE SYSTEMS OPERATIONAL`

## Step 5: Run the Application

### Option A: Streamlit UI (Easiest)
```bash
streamlit run frontend/app.py
```
Open browser to: http://localhost:8501

### Option B: FastAPI Backend
```bash
python -m uvicorn backend.api.main:app --reload
```
API available at: http://localhost:8000
Docs at: http://localhost:8000/docs

## Quick Test Query

Try this query in the UI:
```
Compare Redux vs Zustand for React state management
```

## Troubleshooting

### "groq_api_key not configured"
- Make sure you copied `.env.example` to `.env`
- Add your Groq API key to `.env`
- Restart the application

### "GitHub token not configured"
- This is a warning, not an error
- App will work but skip GitHub searches
- Add GitHub token to `.env` for full functionality

### Import errors
```bash
pip install -r requirements.txt
```

---

**🎉 You're all set! Start researching!**
