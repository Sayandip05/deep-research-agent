# 🎯 GETTING STARTED - Your Complete Guide

## 🎉 Congratulations! Your Project is Set Up

Your Deep Research Agent is ready to build. Here's your complete roadmap.

---

## ⚡ Quick Setup (10 Minutes)

### Step 1: Install Python Dependencies

```bash
# Open terminal in project folder
cd "C:\Users\sayan\AI ML\deep-agent"

# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# Install all dependencies
pip install -r requirements.txt
```

**This installs:**
- Deep Agents (LangGraph-based AI framework)
- FastAPI (backend)
- Streamlit (UI)
- Groq client (FREE LLM)
- All source API clients

---

### Step 2: Get FREE API Keys

#### 🔥 Groq (REQUIRED - 100% FREE)

1. Visit: https://console.groq.com
2. Click "Sign Up" (no credit card!)
3. Verify email
4. Go to "API Keys" section
5. Click "Create API Key"
6. Copy the key (starts with `gsk_...`)

**Why Groq?**
- Completely FREE (no trial, no credit card)
- Llama 3.1 70B model (very smart)
- Fast inference (< 1 second)
- 30 requests/minute (plenty for development)

#### 🐙 GitHub (RECOMMENDED - FREE)

1. Visit: https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Name it: "Deep Research Agent"
4. Select scopes:
   - ✅ `public_repo`
   - ✅ `read:user`
5. Click "Generate token"
6. Copy immediately (shows once!)

**Without GitHub token:**
- App still works
- Can't search GitHub repos
- Limited to 60 requests/hour

**With GitHub token:**
- Full GitHub search
- 5,000 requests/hour
- Access to code, repos, issues

---

### Step 3: Configure Environment

```bash
# Copy the example file
copy .env.example .env

# Open .env in any text editor
notepad .env
```

**Add your keys:**
```ini
# Minimum required:
GROQ_API_KEY=gsk_your_actual_groq_key_here

# Recommended:
GITHUB_TOKEN=ghp_your_actual_github_token_here
```

**Save and close the file.**

---

### Step 4: Verify Setup

```bash
# Test everything is configured correctly
python test_setup.py
```

**You should see:**
```
✅ Configuration loaded successfully
✅ Sources initialized
✅ Research Agent initialized
✅ Search successful
```

**If you see errors:**
- Check your API keys are correct
- Make sure .env file exists
- Verify virtual environment is activated

---

### Step 5: Run the Application!

#### Option A: Streamlit UI (Recommended for first time)

```bash
streamlit run src/ui/app.py
```

Browser opens automatically to: http://localhost:8501

**Try these queries:**
1. "Compare Redux vs Zustand for React"
2. "Is Rust good for web development?"
3. "Best practices for FastAPI"

#### Option B: FastAPI Backend

```bash
python -m uvicorn src.api.main:app --reload
```

Visit: http://localhost:8000/docs for API documentation

**Test with curl:**
```bash
curl -X POST "http://localhost:8000/research" \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"What is FastAPI good for?\"}"
```

---

## 📚 Understanding Your Project

### What You've Built

```
Deep Research Agent
├── 🤖 AI Agent (Deep Agents framework)
│   ├── Plans research strategy
│   ├── Searches multiple sources
│   └── Synthesizes findings
│
├── 🔌 Source Adapters
│   ├── GitHub (repos, code, issues)
│   └── Hacker News (discussions, trends)
│
├── 🌐 FastAPI Backend
│   ├── REST API endpoints
│   └── Async request handling
│
└── 🖥️ Streamlit UI
    ├── Simple web interface
    └── Real-time results
```

### How It Works

1. **User enters query** → "Compare X vs Y"
2. **Agent plans** → Decides to search GitHub + HN
3. **Parallel search** → Both sources searched at once
4. **Synthesis** → LLM combines findings intelligently
5. **Response** → Coherent report with citations

---

## 🎓 Next Steps

### Immediate (Today)

✅ **Test basic functionality:**
- Run `test_setup.py`
- Try the Streamlit UI
- Make a few test queries

✅ **Understand the code:**
- Read `src/agent/research_agent.py`
- Look at source adapters in `src/sources/`
- Check configuration in `src/utils/config.py`

### Short Term (This Week)

🔜 **Add more sources:**
- Reddit integration
- Stack Overflow integration
- ArXiv for research papers

🔜 **Improve quality:**
- Better synthesis prompts
- Citation validation
- Result ranking

🔜 **Add features:**
- Semantic caching
- Streaming responses
- Export to PDF/Markdown

### Long Term (3 Weeks)

📈 **Production ready:**
- Deploy to Render.com (FREE)
- Add monitoring (Sentry)
- Write comprehensive tests
- Create demo video

📈 **Portfolio polish:**
- Professional README
- Architecture diagrams
- Technical blog post
- LinkedIn showcase

---

## 💡 Development Tips

### Testing Changes

```bash
# Always activate virtual environment first
venv\Scripts\activate

# Make changes to code
# Then test:
python test_setup.py

# Run app
streamlit run src/ui/app.py
```

### Adding New Sources

1. Create new file in `src/sources/` (e.g., `reddit.py`)
2. Inherit from `BaseSource`
3. Implement `search()` and `is_available()`
4. Register in `src/sources/__init__.py`

Example:
```python
# src/sources/reddit.py
from .base import BaseSource, SearchResult

class RedditSource(BaseSource):
    async def search(self, query, max_results=10):
        # Your Reddit API logic
        pass
    
    async def is_available(self):
        return bool(settings.reddit_client_id)
```

### Debugging

```python
# Add print statements
print(f"🔍 Searching for: {query}")

# Or use logging
import logging
logging.info(f"Results: {len(results)}")

# Check in terminal/console
```

---

## 🚀 Deployment Options (All FREE)

### Option 1: Render.com
- Best for backend API
- 750 hours/month FREE
- Auto-deploy from GitHub

### Option 2: Streamlit Cloud
- Best for UI
- Unlimited public apps
- Direct Streamlit integration

### Option 3: Railway
- Alternative to Render
- $5 FREE credit/month
- Better reliability

**Later:** Check `docs/DEPLOYMENT.md` for full guide

---

## 📖 Documentation

| File | What It Covers |
|------|---------------|
| `README.md` | Project overview, features, quick links |
| `SETUP_COMPLETE.md` | What was built, tech stack, roadmap |
| `docs/QUICKSTART.md` | Step-by-step setup guide |
| `docs/USAGE.md` | How to use the agent, API docs |
| `test_setup.py` | Verify everything works |

---

## 🆘 Troubleshooting

### "Module not found" errors
```bash
# Make sure virtual environment is activated
venv\Scripts\activate

# Reinstall dependencies
pip install -r requirements.txt
```

### "API key not configured"
```bash
# Check .env file exists
dir .env

# Verify it has your keys
type .env

# Make sure no spaces around = sign
GROQ_API_KEY=your_key  # ✅ Good
GROQ_API_KEY = your_key  # ❌ Bad (spaces)
```

### "No results returned"
- Check internet connection
- Verify API keys are valid
- Try different search query
- Check source availability: `GET /sources`

### App won't start
```bash
# Check Python version (need 3.11+)
python --version

# Check if port is in use
# Try different port:
streamlit run src/ui/app.py --server.port 8502
```

---

## 🎯 Your Goals

### This Week
- [ ] Setup complete
- [ ] Test basic searches
- [ ] Understand code structure
- [ ] Make first modification

### This Month
- [ ] Add 2 more sources
- [ ] Implement caching
- [ ] Deploy to production
- [ ] Create demo video

### Portfolio Ready
- [ ] Professional documentation
- [ ] Live demo deployed
- [ ] Technical blog post written
- [ ] Added to LinkedIn/Resume

---

## 💬 Need Help?

1. **Check docs:** All guides in `docs/` folder
2. **Run tests:** `python test_setup.py`
3. **Read code:** Well-commented in `src/`
4. **Debug:** Add print statements
5. **Ask:** Open issue on GitHub

---

## 🎊 You're All Set!

**Start building:**
```bash
cd "C:\Users\sayan\AI ML\deep-agent"
venv\Scripts\activate
streamlit run src/ui/app.py
```

**First query to try:**
```
"What are the trade-offs between microservices and monolithic architecture?"
```

**Watch the magic happen! ✨**

---

*Built with ❤️ using Deep Agents, Groq, FastAPI, and 100% FREE infrastructure*
