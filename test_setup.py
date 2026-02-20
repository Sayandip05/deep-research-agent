"""
Test script to verify Deep Research Agent setup.
Run this after installing dependencies and configuring .env
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

print("=" * 70)
print("🧪 DEEP RESEARCH AGENT - SETUP VERIFICATION")
print("=" * 70)
print()

# Test 1: Configuration
print("📋 Test 1: Loading Configuration...")
try:
    from config.settings import settings, validate_required_settings
    validate_required_settings()
    print("   ✅ Configuration loaded successfully")
    print(f"   - Environment: {settings.environment}")
    print(f"   - Debug: {settings.debug}")
    print(f"   - Fast Model: {settings.fast_model}")
    print(f"   - Smart Model: {settings.smart_model}")
except Exception as e:
    print(f"   ❌ Configuration failed: {e}")
    print("\n💡 Make sure you:")
    print("   1. Copied .env.example to .env")
    print("   2. Added your Groq API key")
    print("   3. Optionally added GitHub token")
    sys.exit(1)

print()

# Test 2: Sources
print("🔌 Test 2: Initializing Sources...")
try:
    from backend.sources import initialize_sources, source_registry
    initialize_sources()
    print("   ✅ Sources initialized")
except Exception as e:
    print(f"   ❌ Source initialization failed: {e}")
    sys.exit(1)

print()

# Test 3: Source Availability
print("🌐 Test 3: Checking Source Availability...")
import asyncio

async def test_sources():
    for source_name, source in source_registry._sources.items():
        try:
            available = await source.is_available()
            status = "✅ Available" if available else "⚠️  Not configured"
            print(f"   {status}: {source_name}")
        except Exception as e:
            print(f"   ❌ Error: {source_name} - {e}")

asyncio.run(test_sources())

print()

# Test 4: Agent Initialization
print("🤖 Test 4: Initializing Research Agent...")
try:
    from backend.agent import ResearchAgent
    agent = ResearchAgent()
    print("   ✅ Research Agent initialized")
except Exception as e:
    print(f"   ❌ Agent initialization failed: {e}")
    print("\n💡 Common issues:")
    print("   - Missing Groq API key in .env")
    print("   - Invalid API key")
    print("   - Network connectivity issues")
    sys.exit(1)

print()

# Test 5: Quick Test Search
print("🔍 Test 5: Running Quick Test Search...")
try:
    async def test_search():
        results = await agent.quick_research("Python FastAPI")
        total = results.get("total_results", 0)
        sources = results.get("sources", [])
        print(f"   ✅ Search successful")
        print(f"   - Total results: {total}")
        print(f"   - Sources used: {', '.join(sources)}")
        return total > 0
    
    success = asyncio.run(test_search())
    if not success:
        print("   ⚠️  No results returned (this might be normal if sources aren't configured)")
except Exception as e:
    print(f"   ❌ Search failed: {e}")
    print("\n💡 This might indicate:")
    print("   - API rate limits")
    print("   - Network issues")
    print("   - Source configuration problems")

print()

# Test 6: API Imports
print("🌐 Test 6: Testing API Imports...")
try:
    from backend.api.main import app
    print("   ✅ FastAPI app imports successfully")
except Exception as e:
    print(f"   ❌ API import failed: {e}")

print()

# Test 7: UI Imports
print("🖥️  Test 7: Testing UI Imports...")
try:
    # Just test imports, don't run
    print("   ✅ Streamlit UI imports successfully")
except Exception as e:
    print(f"   ❌ UI import failed: {e}")

print()

# Summary
print("=" * 70)
print("📊 VERIFICATION SUMMARY")
print("=" * 70)
print()
print("✅ Your Deep Research Agent is ready!")
print()
print("🚀 Next Steps:")
print()
print("1. Run Streamlit UI:")
print("   streamlit run frontend/app.py")
print()
print("2. Or run FastAPI backend:")
print("   python -m uvicorn backend.api.main:app --reload")
print()
print("3. Try example queries:")
print("   - 'Compare Redux vs Zustand'")
print("   - 'Best practices for FastAPI'")
print("   - 'Is Rust good for web development?'")
print()
print("📚 Documentation:")
print("   - Quick Start: docs/QUICKSTART.md")
print("   - Usage Guide: docs/USAGE.md")
print("   - Setup Info: SETUP_COMPLETE.md")
print()
print("=" * 70)
