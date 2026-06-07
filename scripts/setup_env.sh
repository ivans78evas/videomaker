#!/bin/bash

# TranslationTurbo: Codespace Environment Setup

echo "📦 Installing minimal test dependencies..."
pip install groq httpx loguru pydantic-settings redis

echo "🔗 Setting up PYTHONPATH..."
export PYTHONPATH=$PYTHONPATH:$(pwd)/backend

echo "✅ Environment ready."
echo "💡 Usage: export GROQ_API_KEY='your_key' && python scripts/test_quality_bench.py"
