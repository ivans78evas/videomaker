import sys
import os
from pathlib import Path
import json
import httpx
from loguru import logger

# Add backend to path if running from repo root
sys.path.append(str(Path(__file__).parent.parent / "backend"))

def check_env():
    """Diagnostic check for keys and connectivity."""
    keys = {
        "GROQ_API_KEY": os.getenv("GROQ_API_KEY"),
        "OPENROUTER_API_KEY": os.getenv("OPENROUTER_API_KEY")
    }

    missing = [k for k, v in keys.items() if not v]
    if missing:
        logger.warning(f"⚠️ Missing keys: {', '.join(missing)}. Running in STUB mode.")
        return False
    return True

def test_api_connectivity():
    """Verifies that the server can reach API endpoints."""
    endpoints = ["https://api.groq.com", "https://openrouter.ai"]
    for url in endpoints:
        try:
            httpx.get(url, timeout=5.0)
            logger.success(f"🌐 Connected to {url}")
        except Exception as e:
            logger.error(f"❌ Failed to reach {url}: {e}")

def run_benchmark():
    # Load backend services only if env is ready
    try:
        from app.services.llm_router import unified_llm
        from app.services.openrouter_guard import openrouter_guard
    except ImportError:
        logger.error("Could not import backend services. Ensure PYTHONPATH=./backend")
        return

    logger.info("🚀 Starting Quality Benchmark on GitHub Codespaces...")

    test_api_connectivity()
    is_ready = check_env()

    # 1. Check OpenRouter Free Status
    free_models = openrouter_guard.fetch_free_models()
    logger.info(f"OpenRouter Free Inventory: {len(free_models)} models found.")

    samples = [
        {"text": "Artificial Intelligence is transforming video localization.", "lang": "German"},
        {"text": "Zero-cost infrastructure is the key to scalable agencies.", "lang": "Russian"}
    ]

    for sample in samples:
        logger.info(f"--- Testing: '{sample['text']}' -> {sample['lang']} ---")

        # Test 1: Groq (Llama 3.3 70b)
        try:
            res = unified_llm.route_request(
                f"Translate to {sample['lang']}. Return JSON {{'translated_text': '...'}}",
                sample['text'],
                tier="high_precision"
            )
            logger.success(f"Groq [70b]: {res.get('translated_text')}")
        except Exception as e:
            logger.error(f"Groq Error: {e}")

        # Test 2: Gemini (OpenRouter Free)
        try:
            res = unified_llm.call_openrouter_free(
                f"Translate to {sample['lang']}. Return JSON {{'translated_text': '...'}}",
                sample['text'],
                model="google/gemini-flash-1.5:free"
            )
            logger.success(f"Gemini [Free]: {res.get('translated_text')}")
        except Exception as e:
            logger.error(f"Gemini Error: {e}")

    logger.info("Benchmark complete.")

if __name__ == "__main__":
    # Instruction for execution
    if len(sys.argv) > 1 and sys.argv[1] == "--diagnostic":
        test_api_connectivity()
    else:
        run_benchmark()
